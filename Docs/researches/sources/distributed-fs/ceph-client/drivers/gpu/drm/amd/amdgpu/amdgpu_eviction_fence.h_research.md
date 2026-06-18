# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eviction_fence.h

## Purpose
`amdgpu_eviction_fence.h` defines the data structures and API for AMDGPU per-file eviction fence management.

## Important APIs, types, and functions
The key types are `struct amdgpu_eviction_fence`, embedding `struct dma_fence`, and `struct amdgpu_eviction_fence_mgr`, holding the current RCU-protected eviction fence, fence context/sequence, suspend work, and shutdown flag. The inline `amdgpu_evf_mgr_get_fence()` safely references the current fence under RCU. Prototypes cover attach, rearm, detach, init, shutdown, suspend flush, and fini.

## Control flow
The header encodes the lifecycle: initialize a manager for a file, rearm fences while VM BOs are locked, attach/detach BO reservation fences during GEM open/close, flush or shut down work during release, and drop the final fence reference at fini.

## State and persistence behavior
All state is runtime synchronization state scoped to a DRM file private object. The comments document the lock contract: current fence updates happen under the VM reservation lock, and signaling happens under the user queue mutex.

## Dependencies and integration points
It depends on Linux dma-fence, RCU-safe fence reference helpers, AMDGPU BO types, and DRM exec through the C implementation. It connects GEM/VM code with user-queue eviction.

## Risks and edge cases
Misusing the inline without checking for `NULL` would be unsafe, though the manager initializes with a stub fence. Lock-order violations between VM reservation locks and `userq_mutex` can create races or deadlocks. The RCU pointer must not be replaced or signaled outside the documented locking model.

## Test signals
Build coverage, lockdep under VM/user-queue stress, BO reservation fence replacement, file close/release ordering, and user queue eviction/resume tests validate this header contract.
