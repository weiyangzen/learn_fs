# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/powercap.h

## Purpose
Defines the public cpupower powercap/RAPL interface and the in-memory zone tree representation consumed by powercap reporting and monitoring code.

## Important APIs, Types, and Functions
Important constants are `PATH_TO_POWERCAP`, `PATH_TO_RAPL`, `POWERCAP_MAX_CHILD_ZONES`, `POWERCAP_MAX_TREE_DEPTH`, `MAX_LINE_LEN`, and `SYSFS_PATH_MAX`. `struct powercap_zone` stores printable `name`, sysfs-relative `sys_name`, tree depth, parent pointer, up to 10 children, and bitfields advertising available `power_uw` and `energy_uj` counters. Function declarations cover discovery, walking, enabled-state reads/writes, driver lookup, and 64-bit counter reads.

## Control Flow, State, and Persistence
This header has no runtime control flow. It defines the heap object layout filled by `powercap.c`; callers retain raw pointers into that tree and there is no ownership helper for freeing it. State is bounded by static constants, which influence recursive discovery and report indentation.

## Dependencies and Integration Points
Included directly by `powercap.c`, `powercap-info.c`, and `rapl_monitor.c`. The interface maps Linux powercap sysfs files into a generic-looking API, but the paths and comments reflect an intel-rapl-only implementation.

## Risks and Test Signals
The fixed child and path limits can truncate future hardware topologies. The write APIs are declared even though current implementations are no-ops, which can mislead callers. Tests should compile all users against this header, verify struct field assumptions in RAPL monitor/reporting, and exercise a zone tree at the maximum child/depth boundaries.
