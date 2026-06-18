# sources/distributed-fs/ceph-client/include/uapi/drm/vgem_drm.h

## Purpose
This small header defines the vgem DRM UAPI for attaching and signaling fences on virtual GEM BOs. It is primarily a testing and synchronization helper ABI rather than a rendering command interface.

## Important APIs and types
The ABI has two ioctls: `DRM_IOCTL_VGEM_FENCE_ATTACH` and `DRM_IOCTL_VGEM_FENCE_SIGNAL`. `drm_vgem_fence_attach` takes a GEM `handle`, `flags`, and returns an `out_fence` file descriptor or handle depending on kernel semantics; `VGEM_FENCE_WRITE` marks the fence as a write dependency. `drm_vgem_fence_signal` takes a fence and flags and signals it.

## Control flow and state
Userspace creates or imports a vgem BO through generic GEM paths, attaches a fence with read or write semantics, passes that fence to other DRM or dma-buf users, and later signals it. There are no command queues, BO mappings, or device-specific memory layouts in this file.

## State and persistence behavior
The fence object persists until signaled and released by the fd/handle lifecycle. The attachment records synchronization state against a BO handle. Flags must remain compatible because this simple ABI is often used by tests that assert exact synchronization behavior.

## Dependencies and integration points
The header depends on `drm.h` and integrates with GEM BO handles, DMA fence semantics, dma-buf style synchronization tests, and cross-driver explicit fencing.

## Risks and test signals
Risks are concentrated in fence lifetime and signaling: double signal, stale BO handle, incorrect write/read dependency semantics, and invalid flags. Tests should attach read and write fences, signal them, verify poll/wait behavior, validate error paths for invalid handles and fences, and ensure unknown flags are rejected.
