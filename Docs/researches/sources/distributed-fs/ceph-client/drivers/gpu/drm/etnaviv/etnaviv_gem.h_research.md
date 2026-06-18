# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem.h

## Purpose
Defines etnaviv GEM object, VRAM mapping, userptr, submit, and GEM operation structures shared by memory management and submission code.

## Important APIs, Types, and Functions
Defines `struct etnaviv_gem_userptr`, `struct etnaviv_vram_mapping`, `struct etnaviv_gem_object`, `struct etnaviv_gem_ops`, `struct etnaviv_gem_submit_bo`, and `struct etnaviv_gem_submit`. Inline helpers are `to_etnaviv_bo()` and `is_active()`. Declares submit put, GEM wait/private allocation/object list/pages/mapping APIs.

## Control Flow
No main control flow; the structures are populated by GEM creation, submit ioctl parsing, IOMMU mapping, scheduler jobs, and hang dump paths.

## State and Persistence
The header defines persistent per-object state, per-mapping state, per-submit variable-length BO arrays, scheduler job embedding, MMU contexts, fences, pid, exec state, perfmon requests, and command buffer.

## Dependencies and Integration Points
Included by driver, GEM, PRIME, submit, GPU, MMU, dump, and command parser code. Depends on DRM GEM, dma-resv, DRM scheduler, etnaviv cmdbuf and UAPI headers.

## Risks
`struct etnaviv_gem_submit` ends with a flexible array and must not gain fields after `bos[]`. Mapping `use` counts and object refs must stay balanced. `gpu_active` must reflect scheduler/hardware ownership to avoid freeing active objects.

## Test Signals
Build coverage, submit allocation sizing, BO mapping lifetime tests, hang recovery dumps, and lockdep/refcount checks exercise this header’s contracts.
