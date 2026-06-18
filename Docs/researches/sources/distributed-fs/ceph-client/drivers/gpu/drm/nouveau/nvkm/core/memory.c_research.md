# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/memory.c

## Purpose
This file implements common NVKM memory reference counting, instance-memory allocation, and framebuffer compression tag allocation tracking.

## Important APIs, Types, and Functions
Public functions include `nvkm_memory_ctor`, `nvkm_memory_ref`, `nvkm_memory_unref`, `nvkm_memory_new`, `nvkm_memory_tags_get`, and `nvkm_memory_tags_put`.

## Control Flow
Memory construction installs a function table and initializes a kref. Unref drops the kref and calls the backend destructor before freeing. `nvkm_memory_new` supports instance-memory targets, selecting whether contents must be preserved across suspend/resume, and delegates to `nvkm_instobj_new`. Compression tag get locks framebuffer tag state, reuses compatible existing tags or allocates a new tag object and MM node, optionally clears hardware tags, and records empty tags when allocation fails. Put decrements and frees MM nodes/tags on last ref.

## State and Persistence Behavior
State includes memory function table, kref, optional compression tags pointer, tag MM node, tag refcount, and backend-specific memory allocations. Tag state persists on the memory object and framebuffer tag allocator.

## Dependencies and Integration Points
It depends on NVKM framebuffer tag allocator, instance memory subdev, NVKM MM allocator, and memory backend destructors. GPU object and firmware memory code use this interface.

## Risks
Compression tag compatibility is enforced by requested tag count; mismatches return `-EINVAL`. Empty tags intentionally represent failed hardware tag allocation and force uncompressed mappings later. Missing instmem returns `-ENOSYS`.

## Test Signals
Signals include memory ref/unref destructor calls, instance allocation for preserve and non-preserve targets, compression tag reuse/free, incompatible tag requests, allocation failure fallback, and concurrent tag access.
