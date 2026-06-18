
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_ai.h

## Purpose
Defines AI/GFX9-era MES PM4 packet layouts used by `kfd_packet_manager_v9.c`, including set-resources, runlist, map-process, map-queues, query-status, unmap-queues, release-mem, and write-data MMIO packets.

## Important APIs, types, and functions
- `union PM4_MES_TYPE_3_HEADER` with `u32All` storage.
- Packet structs: `pm4_mes_set_resources`, `pm4_mes_runlist`, `pm4_mes_map_process`, `PM4_MES_MAP_PROCESS_VM`, `pm4_mes_map_queues`, `pm4_mes_query_status`, `pm4_mes_unmap_queues`, `pm4_mec_release_mem`, and `pm4_mec_write_data_mmio`.
- Enum groups define queue types, engine selectors, extended SDMA selectors, unmap actions, query commands, release-mem modes, and write-data MMIO controls.

## Control flow
No executable control flow. Packet-manager code zeroes one of these structs, writes header and bitfields, then submits the resulting dwords.

## State and persistence behavior
No local runtime state. These definitions are a hardware/firmware ABI and therefore persistent across command submissions and checkpoint compatibility expectations.

## Dependencies and integration points
Consumed primarily by v9 and Aldebaran packet builders. Includes extended engine selectors for SDMA0-7 and SDMA8-15 and a `WRITE_DATA` packet shape used to tune dequeue wait counts.

## Risks
Generated-style bitfields are sensitive to compiler and architecture assumptions used by the kernel. Small field-width differences from VI, especially doorbell offset width, GDS size high bits, XNACK retry disable check, and extended engine selector fields, can cause silent scheduler failure. Packet `sizeof` values are used directly for PM4 header counts and runlist sizing.

## Test signals
Compile-time checks through users of every packet struct; runtime packet dump comparison for set-resources, map-process, map-queues with high SDMA engines, unmap, query-status, release-mem, and dequeue wait-count write-data.
