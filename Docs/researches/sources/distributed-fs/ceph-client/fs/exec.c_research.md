# sources/distributed-fs/ceph-client/fs/exec.c

## Purpose
`exec.c` is the Linux execve implementation. It owns opening an executable for execution, building a temporary `linux_binprm`, counting and copying argv/envp into a new stack, selecting a registered binary-format loader, committing credentials, replacing the task's `mm_struct`, collapsing a multithreaded task into one thread, installing the new executable identity, and exposing `execve`, `execveat`, compat exec syscalls, and `kernel_execve`. It is both VFS-facing and scheduler/security-facing: successful binfmt handlers call back into `begin_new_exec()`, after which failures are fatal to the current task.

## Important APIs, types, and functions
The binary-format registry is `formats` protected by `binfmt_lock`, with exported `__register_binfmt()`, `unregister_binfmt()`, `set_binfmt()`, and internal `put_binfmt()`. `path_noexec()` enforces `MNT_NOEXEC` and `SB_I_NOEXEC`.

Argument setup is handled by `bprm_mm_init()`, `count()`, `count_strings_kernel()`, `bprm_stack_limits()`, `copy_strings()`, `copy_string_kernel()`, `copy_strings_kernel()`, `setup_arg_pages()` on MMU builds, and `transfer_args_to_stack()` on NOMMU builds. `struct user_arg_ptr` abstracts native and compat user pointers.

Executable opening and read helpers include `do_open_execat()`, exported `open_exec()`, optional `read_code()`, and matching `do_close_execat()`. `alloc_bprm()`, `free_bprm()`, and the cleanup class around `struct linux_binprm` own lifetime.

The irreversible exec transition is split across `bprm_execve()`, `exec_binprm()`, `search_binary_handler()`, and exported `begin_new_exec()`, `setup_new_exec()`, and `finalize_exec()`. Security and credential helpers include `prepare_bprm_creds()`, `check_unsafe_exec()`, `bprm_fill_uid()`, `bprm_creds_from_file()`, `would_dump()`, and `set_dumpable()`.

Thread/task replacement helpers are `exec_mmap()`, `de_thread()`, `unshare_sighand()`, and `__set_task_comm()`. User entry points are `SYSCALL_DEFINE3(execve)`, `SYSCALL_DEFINE5(execveat)`, compat syscall wrappers, and `kernel_execve()`.

## Control flow
User syscalls enter `do_execveat_common()`. It rechecks deferred `RLIMIT_NPROC` failure, opens the target with `do_open_execat()`, allocates a new `linux_binprm` and temporary `mm`, counts argv/envp, computes stack limits that include pointer-array space, copies the executable path, environment strings, and arguments backward into the new stack, and inserts an empty `argv[0]` if userspace passed no arguments.

`bprm_execve()` then locks and prepares credentials, records unsafe ptrace/no-new-privs/shared-fs state, sets `current->in_execve`, lets LSMs fill invariant credential state via `security_bprm_creds_for_exec()`, and either returns for `AT_EXECVE_CHECK` or calls `exec_binprm()`. `exec_binprm()` repeatedly calls `search_binary_handler()` to read the initial buffer, run `security_bprm_check()`, and invoke registered `fmt->load_binary()` methods. Interpreter rewrites replace `bprm->file` with `bprm->interpreter`, retain an execfd executable when needed, and are bounded by a small recursion depth.

Binfmt success calls `begin_new_exec()`. That function computes final file-derived credentials, marks `point_of_no_return`, kills sibling threads with `de_thread()`, cancels io_uring, unshares the files table, installs `mm->exe_file`, computes nondumpability, swaps the new `mm` into the task through `exec_mmap()`, resets namespaces/timers/sighand/thread state, applies `CLOEXEC`, adjusts secureexec stack limits, sets dumpability, updates `comm`, flushes signal handlers, commits credentials under LSM hooks, and optionally passes the opened executable as an fd to an interpreter. Afterward, binfmt code calls `setup_new_exec()` and `finalize_exec()` around arch-specific loader setup and `start_thread()`.

On failure before the point of no return, cleanup unwinds the binprm, credentials, executable write denial, temporary `mm`, pages, and interpreter strings. On failure after the point of no return, `bprm_execve()` forces a fatal signal if one is not already pending.

## State and persistence behavior
Most state is transient in the current task and its new `linux_binprm`: copied argv/env pages, temporary stack VMA, new `mm`, executable file, interpreter file, final credentials, flags such as `secureexec`, `interp_flags`, `per_clear`, `point_of_no_return`, and the `execfd` handoff. Persistent user-visible state changes include the task's `mm`, `comm`, credentials, dumpability, signal disposition, fd table after close-on-exec, namespace execution hooks, process event notifications, rseq/user-events state, and `/proc` executable identity.

The global `suid_dumpable` sysctl is persistent kernel configuration under `fs.suid_dumpable`. `formats` is global runtime state owned by binfmt modules. The code updates accounting and notification surfaces through audit, ptrace, proc connector, sched tracepoints, perf events, taskstats, NUMA cleanup, and coredump safety validation.

## Dependencies and integration points
This file integrates VFS pathname opening, mount noexec policy, mmap and stack VMA setup, GUP, signal/thread-group management, pid transfer, file-descriptor tables, LSM hooks, credentials/user namespaces/idmapped mounts, binfmt modules, scheduler and cgroup threadgroup transitions, io_uring cancellation, perf, audit, ptrace, proc connector, rseq, user events, sysctl, coredump, and architecture `start_thread` preparation.

## Risks and test signals
Key risks are point-of-no-return error paths, multithreaded exec races, credential and dumpability mistakes around setuid/setgid/no-new-privs/ptrace/shared-fs states, stale executable fd/path handling for interpreters, stack-limit overflows, user pointer faults while copying arguments, module lifetime races while traversing binfmt handlers, `CLOEXEC` ordering versus dumpability, and NOMMU/MMU divergence.

Useful tests include `execve`/`execveat` with `AT_EMPTY_PATH`, `AT_SYMLINK_NOFOLLOW`, `AT_EXECVE_CHECK`, inaccessible `/dev/fd` interpreter paths, null argv, huge argv/envp near `ARG_MAX`, fatal signals during copy, setuid/setgid under idmapped mounts and user namespaces, ptrace/no-new-privs/LSM combinations, multithreaded exec from non-leader threads, close-on-exec races, binfmt interpreter chains, compat exec syscalls, noexec mounts, unreadable executable coredump policy, and fault injection after `begin_new_exec()`.
