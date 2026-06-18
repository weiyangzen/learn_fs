# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv17_fence.c

## Purpose
This file extends NV10 fences with VRAM-backed semaphore synchronization for NV17-class channels.

## Important APIs, Types, and Functions
Public functions are `nv17_fence_sync`, `nv17_fence_resume`, and `nv17_fence_create`. It reuses `nv10_fence_emit`, `nv10_fence_read`, and `nv10_fence_context_del`.

## Control Flow
Creation allocates `nv10_fence_priv`, creates a one-page VRAM semaphore BO, installs resume and context callbacks, and clears the BO. Context creation constructs a DMA object covering the semaphore BO and sets sync to `nv17_fence_sync`. Sync tries to lock the client mutex, reserves two sequence increments under the spinlock, programs acquire/release semaphore operations into the previous channel and the target channel, kicks both, and unlocks.

## State and Persistence Behavior
The global sequence counter is persisted in the semaphore BO on resume via `nouveau_bo_wr32`. Per-channel semaphore DMA objects are destroyed with the channel context.

## Dependencies and Integration Points
It depends on NV176E semaphore methods, NVIF DMA object construction, Nouveau BO allocation/mapping, client mutex serialization, and generic fence context helpers.

## Risks
`mutex_trylock` can return `-EBUSY`, so callers must tolerate retry. The function returns 0 even after push programming errors are stored in `ret`, which looks suspicious and can hide sync failures. Semaphore BO placement must be valid VRAM.

## Test Signals
Signals include cross-channel fence sync, suspend/resume sequence restoration, push failure injection, client mutex contention, and semaphore BO allocation failure.
