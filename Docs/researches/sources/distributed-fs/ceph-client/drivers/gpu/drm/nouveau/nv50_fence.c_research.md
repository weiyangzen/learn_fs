# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv50_fence.c

## Purpose
This file provides the NV50 fence backend, mostly reusing NV17 semaphore logic with the NV50 DMA object class variant.

## Important APIs, Types, and Functions
Main entry point is `nv50_fence_create`. Internal context creation constructs the semaphore DMA object and installs NV10 emit/read plus NV17 sync callbacks.

## Control Flow
Creation allocates `nv10_fence_priv`, sets destructor/resume/context callbacks, initializes the lock, creates a one-page VRAM semaphore BO, and clears it. Context creation allocates a channel fence context, initializes generic fence state, points emit/read/sync to NV10/NV17 helpers, and constructs `NvSema` with `NV_DMA_IN_MEMORY` targeting the semaphore BO.

## State and Persistence Behavior
Global state is the semaphore BO and sequence lock in `drm->fence`. Per-channel state is `nv10_fence_chan` plus an NVIF semaphore object.

## Dependencies and Integration Points
It depends on NVIF class and DMA object APIs, Nouveau BO mapping, NV10/NV17 fence helpers, and generic fence infrastructure.

## Risks
Semaphore BO allocation failure must destroy partially initialized state. The DMA object range is based on the BO resource start and size, so incorrect placement would break sync. Error handling delegates to shared NV10 cleanup.

## Test Signals
Signals include NV50 fence emit/read, cross-channel sync, context construction failure, suspend/resume through NV17 resume helper, and driver unload cleanup.
