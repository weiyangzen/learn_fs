# sources/distributed-fs/ceph-client/include/linux/binfmts.h

## Purpose
Defines kernel binary-format loading interfaces, the `linux_binprm` execution context, binfmt handler registration, and exec/coredump helper declarations.

## Important APIs, types, and functions
- `struct linux_binprm` carries argument memory, target mm, file/interpreter/executable, new credentials, exec flags, unsafe mask, personality clearing, argument/environment counts, names, fd path, stack rlimit, and initial binary buffer.
- `struct linux_binfmt` registers `load_binary()` and optional `core_dump()` handlers with module ownership and coredump minimum size.
- Optional `struct binfmt_misc` tracks misc handler entries and enabled state.
- Registration helpers: `register_binfmt()`, `insert_binfmt()`, and `unregister_binfmt()`.
- Exec helpers include `remove_arg_zero()`, `begin_new_exec()`, `setup_new_exec()`, `finalize_exec()`, `would_dump()`, `setup_arg_pages()`, `transfer_args_to_stack()`, `bprm_change_interp()`, `copy_string_kernel()`, `set_binfmt()`, `read_code()`, and `kernel_execve()`.

## Control flow and state
Exec builds a `linux_binprm`, reads the initial bytes into `buf`, walks registered binfmt handlers, and calls a handler's `load_binary()`. Handlers may change interpreter, credentials, stack layout, and point-of-no-return state. Registration order matters: `insert_binfmt()` places a handler before existing handlers.

## State and persistence behavior
State is per-exec transient until `finalize_exec()` commits the new program. Credentials and mm changes become the task's persistent runtime state after successful exec. `point_of_no_return` marks the transition where errors can no longer be reported to the original userspace image.

## Dependencies and integration points
Depends on scheduler, unistd, architecture exec definitions, and UAPI binfmt constants. Integrated by ELF, script, misc, flat, and other binary loaders, LSM hooks, coredump code, and kernel users of `kernel_execve()`.

## Risks
Credential transitions, `secureexec`, nondump flags, and inaccessible path flags are security-sensitive. Binfmt handlers must honor point-of-no-return and avoid leaking file/credential references. Stack setup differs for MMU and NOMMU builds.

## Test signals
Run exec tests for ELF, script interpreters, binfmt_misc, `execveat`, setuid/secureexec, nondump behavior, coredumps, argument limits, NOMMU builds, and handler registration order.
