# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/rapl_monitor.c

## Purpose
Implements a `cpupower monitor` plugin named `RAPL` that reports energy deltas for powercap zones exposing `energy_uj`.

## Important APIs, Types, and Functions
Important functions are `rapl_get_count_uj`, `powercap_count_zones`, `rapl_start`, `rapl_stop`, and `rapl_register`. It uses arrays `rapl_zones`, `rapl_zones_pt`, previous/current counts, and a maximum of 10 zones.

## Control Flow, State, and Persistence
Registration verifies intel-rapl driver availability and enabled state, initializes the powercap zone tree, walks it, and adds each energy-capable zone as a monitor state. Start and stop snapshot `energy_uj`; callbacks report the delta in microjoules. No persistent state is written, but it retains pointers to the allocated powercap tree for process lifetime.

## Dependencies and Integration Points
Depends on `powercap.c`, Linux powercap sysfs, monitor framework, and x86 build gating. Unlike MSR monitors it does not require root by descriptor flag.

## Risks and Test Signals
`powercap_count_zones` prints debug-looking `sys_name` and return values to stdout, which can corrupt monitor table output. Energy counter wrap handling is not implemented. `rapl_max_count` assignment appears wrong because it compares absolute current value before storing delta. Test with nested RAPL zones, more than 10 zones, counter wrap, disabled powercap, and normal `cpupower monitor -m RAPL` output cleanliness.
