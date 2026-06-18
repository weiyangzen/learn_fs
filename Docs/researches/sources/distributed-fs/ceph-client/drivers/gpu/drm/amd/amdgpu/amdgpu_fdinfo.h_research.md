# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fdinfo.h

## Purpose
`amdgpu_fdinfo.h` declares AMDGPU fdinfo support and related helper prototypes.

## Important APIs, types, and functions
It declares `amdgpu_show_fdinfo()` and `amdgpu_get_ip_count()`. The includes pull in DRM file, scheduler, sync, ring, ID, IDR, kfifo, rbtree, and task memory types used by fdinfo-adjacent accounting code.

## Control flow
The header has no executable control flow. Its declarations allow the DRM driver table to point at `amdgpu_show_fdinfo()` and allow related code to query IP counts.

## State and persistence behavior
No state is defined here. Runtime state is owned by file private data, VM, context managers, and device IP metadata.

## Dependencies and integration points
It is included by `amdgpu_drv.c` and `amdgpu_fdinfo.c`, connecting DRM core fdinfo callbacks to AMDGPU accounting implementation.

## Risks and edge cases
The include guard name still says `__AMDGPU_SMI_H__`, which is harmless for builds but confusing for maintenance. Prototype drift would break fdinfo registration or IP-count callers.

## Test signals
Build coverage and successful `/proc/<pid>/fdinfo` reporting validate the declarations.
