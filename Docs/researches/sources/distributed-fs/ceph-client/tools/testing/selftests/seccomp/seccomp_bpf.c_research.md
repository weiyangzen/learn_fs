# sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/seccomp_bpf.c

## Purpose
Large kselftest harness for Linux seccomp classic-BPF behavior. It validates strict mode, filter mode, BPF return action semantics, filter stacking precedence, ptrace/seccomp interactions, thread synchronization, seccomp user notifications, notification fd operations, and uprobe/uretprobe interaction on supported architectures. It is intentionally broad because seccomp behavior is ABI-facing and must stay compatible across libc and kernel header versions.

## Important APIs, types, and functions
The file wraps raw `seccomp()` when libc lacks it and supplies compatibility definitions for `SECCOMP_RET_*`, `SECCOMP_FILTER_FLAG_*`, `struct seccomp_notif`, `struct seccomp_notif_resp`, `struct seccomp_notif_addfd`, `struct seccomp_metadata`, and arch syscall numbers. BPF programs are represented with `struct sock_filter` and `struct sock_fprog`. Important helpers include `filecmp()` over `kcmp()`, `kill_thread_or_group()`, ptrace fixture helpers `start_tracer()`, `setup_trace_fixture()`, `teardown_trace_fixture()`, arch register helpers `get_syscall()`, `change_syscall_nr()`, `change_syscall_ret()`, `user_notif_syscall()`, proc parsers `get_nth()`, `get_proc_stat()`, and `get_proc_syscall()`.

## Control flow
The file is organized as kselftest harness `TEST`, `TEST_SIGNAL`, `FIXTURE`, and `TEST_F` cases. Early tests validate basic mode entry, `NO_NEW_PRIVS`, empty/oversized filters, and kill/errno/trap actions. The precedence fixture installs multiple filters in different orders and confirms action priority is independent of installation order except for action data. Trace tests fork a tracer, attach with `PTRACE_O_TRACESECCOMP` or `PTRACE_SYSCALL`, modify syscall numbers/returns, and verify redirected, faked, skipped, or killed syscalls. TSYNC tests start sibling threads with optional diverged filter trees and validate synchronized installation, failure TID reporting, `TSYNC_ESRCH`, and dead thread-leader behavior. User notification tests install `SECCOMP_RET_USER_NOTIF` filters, receive and send notification ioctls, inject fds with `SECCOMP_IOCTL_NOTIF_ADDFD`, validate pid namespace reporting, signal interruption, listener shutdown, FIFO ordering, and wait-killable behavior. Final uprobe tests optionally attach perf uprobes to local functions and verify seccomp filters around the internal uprobe syscalls.

## State and persistence
Most state is per-process test state: installed seccomp filters are irreversible for the task, so tests isolate destructive cases in harness signal tests, forks, or fixtures. Shared state includes pipes, socketpairs, pthread condition variables, semaphores, listener fds, forked children, and global variables such as `tracer_running` and `handled`. No persistent files are written by the test, but it reads `/proc/<pid>/stat`, `/proc/<pid>/syscall`, `/proc/self/maps`, `/sys/bus/event_source/devices/uprobe/*`, and may depend on open fd identity.

## Dependencies and integration points
Integrates with `kselftest_harness.h`, clone3 selftest helpers, Linux seccomp, ptrace, BPF, perf event, capability, pthread, signal, namespace, and procfs APIs. Some tests require root or capabilities (`CAP_SYS_ADMIN`, checkpoint/restore ptrace metadata), kernel options such as `CONFIG_SECCOMP_FILTER`, `CONFIG_KCMP`, `CONFIG_PID_NS`, `CONFIG_CHECKPOINT_RESTORE`, and arch support for ptrace register access and uprobe syscall numbers.

## Risks
The file intentionally kills threads/processes and installs irreversible filters, so incorrect isolation can terminate a test process early. Several checks are timing-sensitive around signals, process states, notification wakeups, and poll timeouts. Architecture register abstractions are fragile when syscall ABI details change. User notification tests depend on exact errno semantics and kernel cleanup timing. Some loops spin until process state changes and can be flaky on overloaded systems.

## Test signals
Pass signals come from harness assertions, expected `SIGSYS`/`SIGKILL` terminations, exact errno values such as `EACCES`, `EINVAL`, `EFAULT`, `EOPNOTSUPP`, `ENOENT`, `EMFILE`, and child exit status checks. Skip signals cover missing kernel features, missing clone3, missing namespaces, missing root/capabilities, missing uprobe support, and unsupported ptrace metadata.
