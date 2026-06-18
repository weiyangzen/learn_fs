
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_vi.h

## Purpose
Defines VI-generation MES PM4 packet layouts consumed by `kfd_packet_manager_vi.c`.

## Important APIs, types, and functions
- `union PM4_MES_TYPE_3_HEADER`.
- Packet structs: `pm4_mes_set_resources`, `pm4_mes_runlist`, `pm4_mes_map_process`, `pm4_mes_map_queues`, `pm4_mes_query_status`, `pm4_mes_unmap_queues`, and `pm4_mec_release_mem`.
- Enums define VI queue selectors, queue types, engine selectors, unmap actions, query commands, release-mem event/cache/destination/interrupt/data selections.

## Control flow
No executable code. The VI packet manager writes these structs into command buffers.

## State and persistence behavior
No local state. Struct layouts form the VI firmware command ABI and are reflected in runlist IBs and HIQ packets.

## Dependencies and integration points
Consumed by VI and CIK-compatible packet manager paths. Field widths match older hardware limits such as 21-bit doorbell offsets and 16-bit high runlist address field.

## Risks
Do not interchange with AI/v9 packet headers: fields such as `gds_heap_base`, `gds_heap_size`, doorbell offsets, and runlist high address differ. `sizeof` drives PM4 header counts, so padding changes would be hazardous.

## Test signals
Compile packet-manager VI path and compare emitted dwords for all packet structs. Include queue map/unmap for compute and SDMA, set-resources masks, runlist chaining, and release-mem cache flush events.
