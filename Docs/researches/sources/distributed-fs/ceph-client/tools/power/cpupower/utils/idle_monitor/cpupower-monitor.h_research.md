# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpupower-monitor.h

## Purpose
Defines the monitor plugin ABI shared by `cpupower monitor` and all idle/power monitor implementations.

## Important APIs, Types, and Functions
Important definitions are `MONITORS_MAX`, `MONITOR_NAME_LEN`, architecture-dependent `CSTATE_NAME_LEN`, `CSTATE_DESC_LEN`, `enum power_range_e`, `cstate_t`, `struct cpuidle_monitor`, `timespec_diff_us`, `print_overflow_err`, and inline `bind_cpu`.

## Control Flow, State, and Persistence
The ABI represents each monitor as start/stop/register/unregister callbacks plus an array of states. Each state reports either a percentage or raw count through callback pointers. The header also defines affinity binding used by monitors needing per-CPU synchronized reads.

## Dependencies and Integration Points
Included by monitor framework and plugin files. It pulls in `idle_monitors.h`, scheduler affinity APIs, gettext through users, and global `cpu_count`.

## Risks and Test Signals
Fixed monitor/name/state widths drive UI layout and can truncate longer labels. Callback contracts are implicit, especially around allocation lifetime and CPU indexing. Test compilation of every monitor, non-x86 builds, and table formatting for maximum name lengths.
