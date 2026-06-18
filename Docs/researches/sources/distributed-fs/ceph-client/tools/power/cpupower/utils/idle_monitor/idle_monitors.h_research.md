# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/idle_monitors.h

## Purpose
Declares all monitor plugin symbols through the shared `idle_monitors.def` list.

## Important APIs, Types, and Functions
It temporarily defines `DEF(x)` to emit `extern struct cpuidle_monitor x_monitor;`, includes `idle_monitors.def`, undefines the macro, and declares `all_monitors[]`.

## Control Flow, State, and Persistence
There is no runtime state. The file ensures the plugin list used for extern declarations stays synchronized with the framework array construction in `cpupower-monitor.c`.

## Dependencies and Integration Points
Integrated by `cpupower-monitor.h` and `cpupower-monitor.c`; requires every monitor named in `idle_monitors.def` to provide a matching `struct cpuidle_monitor` object.

## Risks and Test Signals
Build failures surface if the def list and compiled plugin objects diverge. Test all configured architecture builds and monitor list output to verify each expected plugin registers or cleanly declines.
