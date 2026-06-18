# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool_types.h

## Purpose
`xe_mem_pool_types.h` defines the public node type and initialization flag for Xe memory pools.

## Important APIs, Types, And Functions
- `XE_MEM_POOL_BO_FLAG_INIT_SHADOW_COPY` requests shadow BO setup.
- `struct xe_mem_pool_node` wraps a `struct drm_mm_node` used for suballocation.

## Control Flow
Clients allocate nodes through the implementation and pass the flag at pool initialization when they need shadow-copy behavior.

## State And Persistence
Each node persists while inserted in a pool and is freed by `xe_mem_pool_free_node()`. The header owns no storage.

## Dependencies And Integration Points
Depends on DRM MM. Used by pool clients and `xe_mem_pool.c`.

## Risks
A node must not be freed before removal from `drm_mm`, and the type does not track insertion state itself.

## Test Signals
Node allocation/free tests and misuse detection around double free or freeing uninserted nodes where debug config can catch it.
