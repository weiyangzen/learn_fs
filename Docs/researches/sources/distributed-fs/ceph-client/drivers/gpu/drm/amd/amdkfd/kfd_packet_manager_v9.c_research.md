
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c

## Purpose
Builds PM4 MES packets for GFX9+ HWS scheduling, including generic v9 packets and the Aldebaran/GFX9.4.x per-debug-VMID map-process variant.

## Important APIs, types, and functions
- `kfd_v9_pm_funcs` and `kfd_aldebaran_pm_funcs` export packet-builder vtables.
- `pm_map_process_v9` and `pm_map_process_aldebaran` fill process context packets.
- `pm_runlist_v9`, `pm_set_resources_v9`, `pm_map_queues_v9`, `pm_unmap_queues_v9`, and `pm_query_status_v9` build scheduler control packets.
- `pm_config_dequeue_wait_counts_v9` emits a `WRITE_DATA` MMIO packet for dequeue wait-count tuning.

## Control flow
The generic packet manager passes pre-reserved packet buffers to these builders. Map-process packets encode PASID, DIQ/debug flags, process quantum, GDS/GWS/OAC, SDMA enable, queue count, trap handler addresses, GDS context, and page-table base. Aldebaran additionally writes SPI debug control, watch points, and single-mem-op debug mode. Map-queues selects compute or SDMA engines, including extended SDMA engine selectors for engines 8-15. Unmap-queues chooses preempt or reset and one of PASID/all/non-static filters. Query-status writes a fence-only-after-write-ack packet.

## State and persistence behavior
The file has no owned persistent state. It serializes data from `qcm_process_device`, `kfd_process_device`, `queue`, `device_queue_manager`, and device capabilities into binary PM4 packet buffers.

## Dependencies and integration points
Depends on `kfd_pm4_headers_ai.h`, `kfd_pm4_headers_aldebaran.h`, opcode definitions, DQM wait-time state, KFD debug flags, process runtime debug state, watch-point storage, isolation settings, XNACK chain flags, and `kfd2kgd->build_dequeue_wait_counts_packet_info`.

## Risks
This is a binary firmware contract: field widths, packet sizes, and enum values must match MES firmware expectations. SDMA engine selection differs across SDMA IP versions and high engine IDs. Debug and isolation fields can alter scheduling semantics. Dequeue-wait tuning is allowed only for specific GC ranges; returning `-EPERM` in the builder can roll back packet submission.

## Test signals
Validate packet dword dumps for GFX9, GFX9.4.3, GFX9.5, and Aldebaran paths. Cover debug trap enabled/disabled, watch points, SR-IOV XNACK support, isolation mode, SDMA engine IDs below and above 8, unmap filters, reset/preempt actions, and dequeue wait-count init/reset/set commands.
