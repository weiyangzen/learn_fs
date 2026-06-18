# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/nhm_idle.c

## Purpose
Implements an Intel Nehalem/Westmere-style MSR residency monitor for core C3/C6 and package PC3/PC6.

## Important APIs, Types, and Functions
Key functions are `nhm_get_count`, `nhm_get_count_percent`, `nhm_start`, `nhm_stop`, `intel_nhm_register`, and `intel_nhm_unregister`. The monitor descriptor is `intel_nhm_monitor` with four states.

## Control Flow, State, and Persistence
Registration requires Intel vendor, invariant TSC, and APERF capability. It allocates per-CPU arrays, snapshots residency MSRs and a base-CPU TSC at start/stop, and reports each state as delta residency divided by TSC delta. State is in process heap arrays and hardware MSRs only.

## Dependencies and Integration Points
Depends on x86 MSR access, CPU capability discovery, root access, and monitor table integration.

## Risks and Test Signals
The model check is broad, so registration may occur on Intel CPUs where these exact MSRs are not meaningful, with failures masked by validity flags. Validity uses OR at stop. Test on known Nehalem/Westmere systems, newer Intel systems, no MSR access, multi-socket systems, and output bounds below 100 percent.
