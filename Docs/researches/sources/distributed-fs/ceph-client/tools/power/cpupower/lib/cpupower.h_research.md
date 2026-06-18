<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower.h

## Purpose
Public common libcpupower header. It defines `struct cpupower_topology`, `struct cpuid_core_info`, `CPULIST_BUFFER`, and declares topology retrieval/release plus CPU online checking.

## Important APIs, Types, And Functions
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.

## Control Flow
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.

## State And Persistence
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.

## Dependencies And Integration Points
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.

## Risks And Edge Cases
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.

## Test Signals
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower.h -->
