# sources/distributed-fs/ceph-client/lib/sys_info.c

## Purpose
Implements a configurable diagnostic dump facility selected by `SYS_INFO_*` bits. It can dump task state, memory, timers, locks, ftrace buffers, all-CPU backtraces, and blocked tasks, with an optional sysctl default mask for callers that pass zero.

## APIs, Control Flow, and State
Exports `sys_info_parse_param()` and `sys_info()`, and under `CONFIG_SYSCTL` provides `sysctl_sys_info_handler()`. `sys_info_parse_param()` splits a comma-separated string and maps names through `match_string()` into bit positions derived from `ilog2(SYS_INFO_*)`. Sysctl writes parse the supplied string into `kernel_si_mask` with `WRITE_ONCE`; reads rebuild a comma-separated string from the current mask and pass it through `proc_dostring()`. The `kernel/kernel_sys_info` sysctl is registered at `subsys_initcall`. `sys_info()` invokes `__sys_info()` with the supplied mask or the global default, then calls each selected dump routine.

Persistent state is the unsynchronized global `kernel_si_mask`. The sysctl handler allocates a temporary names buffer per operation.

## Dependencies, Integration, Risks, and Tests
Depends on bitops/log2, console and scheduler debug dumping, sysrq timer listing, lockdep debug, ftrace dump, NMI all-CPU backtrace, string matching, and sysctl. Integration points are panic/oops/driver diagnostics and module parameters that want standardized debug dumps. Risks include very noisy or expensive dumps, unsynchronized global mask updates, empty name for `SYS_INFO_PANIC_CONSOLE_REPLAY` not round-tripping through sysctl text, sysctl buffer sizing mistakes, and use in contexts where dump helpers are unsafe or reentrant. Test signals include sysctl read/write tests, parser tests for comma-separated masks, panic/debug dump smoke tests, lockdep/ftrace enabled and disabled builds, and concurrency tests around updating `kernel_si_mask`.
