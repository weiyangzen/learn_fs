<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys_info.h -->
# sources/distributed-fs/ceph-client/include/linux/sys_info.h

## Purpose

`sys_info.h` declares a kernel diagnostic interface for dumping selected system information, with bitmask flags for tasks, memory, timers, locks, ftrace, panic console replay, all backtraces, and blocked tasks.

## Important APIs, types, and functions

Flags are `SYS_INFO_TASKS`, `SYS_INFO_MEM`, `SYS_INFO_TIMERS`, `SYS_INFO_LOCKS`, `SYS_INFO_FTRACE`, `SYS_INFO_PANIC_CONSOLE_REPLAY`, `SYS_INFO_ALL_BT`, and `SYS_INFO_BLOCKED_TASKS`. APIs are `sys_info()`, `sys_info_parse_param()`, and, with sysctl enabled, `sysctl_sys_info_handler()`.

## Control flow

Callers pass a mask to `sys_info()` to emit selected diagnostic sections. Boot/sysctl parsing can convert string parameters into masks, and sysctl handling can trigger or configure dumps through `/proc/sys` plumbing.

## State and persistence behavior

The header owns no state. State is diagnostic output and any sysctl-side configuration stored elsewhere. Panic console replay is explicitly panic-only because it requires special handling.

## Dependencies and integration points

It depends on `sysctl.h` and integrates with kernel diagnostics, panic paths, sysctl, task/memory/timer/lock/ftrace subsystems, and blocked-task reporting.

## Risks and test signals

Risks include excessive output in panic contexts, unsafe diagnostics while locks are compromised, parsing invalid masks, and triggering console replay outside panic. Tests should validate mask parsing, individual section output, sysctl handler read/write behavior, panic-only constraints, and builds without CONFIG_SYSCTL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys_info.h -->
