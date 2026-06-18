# sources/distributed-fs/ceph-client/kernel/entry/syscall_user_dispatch.c

## Purpose

`syscall_user_dispatch.c` implements Syscall User Dispatch, a per-task mechanism that lets user space redirect syscalls made outside an allowed dispatcher region into `SIGSYS`. It supports `prctl()` configuration, ptrace get/set of dispatch config, selector-byte filtering, inclusive/exclusive address ranges, syscall rollback, and precise `SIGSYS` metadata.

## Important APIs, Types, And Functions

- `trigger_sigsys()` builds `kernel_siginfo` with `SIGSYS`, `SYS_USER_DISPATCH`, call address, architecture, and syscall number, then forces the signal.
- `syscall_user_dispatch()` is the syscall-entry filter. It checks instruction pointer range, vDSO sigreturn exemption, optional selector state, and dispatches blocked syscalls.
- `task_set_syscall_user_dispatch()` validates and installs configuration for a target task.
- `set_syscall_user_dispatch()` applies configuration to `current`.
- `syscall_user_dispatch_get_config()` and `syscall_user_dispatch_set_config()` expose ptrace configuration using `struct ptrace_sud_config`.

## Control Flow

On syscall entry, `syscall_user_dispatch()` first allows syscalls whose instruction pointer lies in the configured direct-dispatch region. It also allows architecture-recognized vDSO sigreturn. If a selector pointer exists, it reads one byte from user memory. `SYSCALL_DISPATCH_FILTER_ALLOW` permits the syscall, `SYSCALL_DISPATCH_FILTER_BLOCK` continues to dispatch, a failed user read exits with `SIGSEGV`, and any invalid selector value exits with `SIGSYS`.

For a blocked syscall, the code sets `sd->on_dispatch`, rolls back the syscall register state with `syscall_rollback()`, and sends `SIGSYS` with syscall metadata. Configuration accepts `PR_SYS_DISPATCH_OFF`, `PR_SYS_DISPATCH_EXCLUSIVE_ON`, and `PR_SYS_DISPATCH_INCLUSIVE_ON`. Inclusive mode inverts the range by moving `offset` to the end and making `len` negative, relying on the unsigned wraparound-aware range check in the dispatch fast path. Enabling sets `SYSCALL_USER_DISPATCH` syscall work; disabling clears it.

Ptrace get copies mode, offset, len, and selector to user space. Ptrace set copies config from user space and uses the same validation path as prctl.

## State And Persistence Behavior

State lives in `task_struct.syscall_dispatch`: selector pointer, offset, length, and `on_dispatch`. The enabled bit is task syscall-work state. It persists for the task until changed by prctl/ptrace or task lifetime end. There is no disk persistence.

## Dependencies And Integration Points

The implementation depends on generic syscall entry work flags, `prctl` constants, ptrace ABI, signal delivery, user access helpers, scheduler/task stack helpers, architecture syscall helpers, vDSO sigreturn detection, and memory-tag untagging through `untagged_addr()`.

## Risks And Edge Cases

- Range validation must catch overflow and zero-length invalid regions. Inclusive mode intentionally stores a negative length, so maintenance must preserve the wraparound semantics in the fast-path comparison.
- The selector address is checked with `access_ok()` at configuration time, but each dispatch still uses `__get_user()` and handles faults.
- Tracers configuring tagged tracees need the selector address untagged for access checks.
- Failing to call `syscall_rollback()` before `SIGSYS` would expose partially committed syscall-entry state to the signal handler.
- Invalid selector byte values deliberately kill with `SIGSYS`.

## Test Signals

Exercise prctl off/exclusive/inclusive modes, overflow and zero-length validation, selector allow/block/fault/invalid-byte behavior, ptrace get/set ABI, vDSO sigreturn exemption, syscall rollback visible in signal handlers, tagged-address selector setup, and interactions with seccomp/audit/syscall tracing.
