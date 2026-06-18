# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_mmap.c

## Purpose
This file provides helper functions for selftests that need to mmap a GEM VMA offset through a DRM file.

## Important APIs, Types, And Functions
- `igt_mmap_offset_with_file()` maps a specific DRM VMA offset using a supplied `struct file`.
- `igt_mmap_offset()` obtains a mock DRM file for the primary node, calls the file-specific helper, then releases the file.

## Control Flow
The helper looks up the exact `drm_vma_offset_node` under the manager lock, temporarily grants the file access with `drm_vma_node_allow()`, calls `vm_mmap()` with node offset/size, revokes access, and returns the userspace address or errno.

## State And Persistence
It temporarily mutates VMA-node access permissions for the file’s private data. The mapping may persist to the caller if `vm_mmap()` succeeds; permission is revoked immediately after mmap setup.

## Dependencies And Integration Points
It depends on DRM VMA offset management, mock DRM file creation, and kernel `vm_mmap`. It is a utility for GEM mmap selftests.

## Risks
The helper assumes the selftest owns the object and skips extra refcounting on the node. Exact offset/size lookup must match a registered mmap node. Error values are returned as unsigned long addresses following mmap conventions.

## Test Signals
Failure signals include `-ENOENT` for missing nodes, permission errors from `drm_vma_node_allow()`, or mmap error values. Success is a mapped address.
