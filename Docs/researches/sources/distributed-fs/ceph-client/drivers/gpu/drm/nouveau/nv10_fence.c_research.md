# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv10_fence.c

## Purpose
This file implements the NV10 fence backend using the user channel reference register and shared helpers later reused by NV17/NV50 fence implementations.

## Important APIs, Types, and Functions
Public helpers are `nv10_fence_emit`, `nv10_fence_read`, `nv10_fence_context_del`, `nv10_fence_destroy`, and `nv10_fence_create`. The private context creation function installs generic fence callbacks.

## Control Flow
Fence creation allocates `nv10_fence_priv`, sets destructor and context callbacks, and initializes the sequence lock. Per-channel context allocation creates `nv10_fence_chan`, initializes generic fence state, and sets emit/read/sync. Emit writes `SET_REFERENCE` with the sequence number and kicks. Read returns the `REFERENCE` register. Sync is unsupported on bare NV10 and returns `-ENODEV`.

## State and Persistence Behavior
`drm->fence` owns global fence private state, optional semaphore BO pointer used by later variants, a lock, and sequence counter. Per-channel contexts hold a semaphore object slot even if NV10 itself does not construct one.

## Dependencies and Integration Points
It depends on NVIF push006c, NV06E class methods, Nouveau fence context helpers, BO unpin/delete during destroy, and the shared `nv10_fence.h` structures.

## Risks
Destroy unconditionally calls `nouveau_bo_unpin_del(&priv->bo)`, so the helper must tolerate a NULL BO for base NV10. Cross-channel sync is unavailable. Register class assumptions must match channel user object class.

## Test Signals
Signals include NV10 fence sequence emission/readback, context allocation/free, module unload with NULL semaphore BO, and unsupported sync fallbacks.
