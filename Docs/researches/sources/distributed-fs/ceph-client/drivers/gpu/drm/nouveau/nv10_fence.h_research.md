# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv10_fence.h

## Purpose
This header shares NV10-family fence private structures across NV10, NV17, and NV50 fence implementations.

## Important APIs, Types, and Functions
`struct nv10_fence_chan` embeds the generic fence channel and an NVIF semaphore object. `struct nv10_fence_priv` embeds the generic fence private object, semaphore BO pointer, spinlock, and sequence counter.

## Control Flow
No executable control flow exists. The structure layout lets later implementations reuse NV10 emit/read and generic context deletion while adding semaphore objects.

## State and Persistence Behavior
State covers per-channel semaphore object lifetime and global semaphore BO/sequence allocation for cross-channel synchronization on NV17/NV50.

## Dependencies and Integration Points
It includes `nouveau_fence.h` and `nouveau_bo.h` and is included by NV10, NV17, and NV50 fence code.

## Risks
Shared layout changes can break multiple chipset backends. The semaphore object is optional by variant, so cleanup must stay NULL-safe.

## Test Signals
Build all three backends and run fence context creation/destruction on NV10, NV17, and NV50-class devices.
