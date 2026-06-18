# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool.h

## Purpose
`xe_mem_pool.h` declares the memory-pool API for BO-backed suballocation and optional shadow synchronization.

## Important APIs, Types, And Functions
- Declares pool initialization, full sync, shadow swap, per-node shadow sync, GPU/CPU address accessors, swap guard accessor, flush/readback helpers, node allocation/insertion/free, node CPU address, and dump.
- Includes `xe_mem_pool_types.h` for node and flag definitions.

## Control Flow
Clients create a pool, allocate/insert nodes, access node memory by CPU pointer or GPU address offset, optionally flush/sync for iomem, and free nodes.

## State And Persistence
The header owns no state but exposes functions over `struct xe_mem_pool` and `struct xe_mem_pool_node` state allocated by the implementation.

## Dependencies And Integration Points
Depends on Linux sizes/types, DRM MM, DRM printer, and Xe tile forward declarations. It is used by subsystems needing compact GPU-visible allocation arenas.

## Risks
The API does not expose internal locking for `drm_mm`; callers must establish allocation serialization. Shadow operations require respecting the returned mutex.

## Test Signals
Compile users and verify allocation, address, shadow, and dump APIs across regular and iomem-backed BOs.
