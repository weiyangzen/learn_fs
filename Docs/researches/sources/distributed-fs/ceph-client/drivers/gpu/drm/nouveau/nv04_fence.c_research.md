# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv04_fence.c

## Purpose
This file implements the earliest Nouveau fence backend using the NV_SW object reference register on NV04-era hardware.

## Important APIs, Types, and Functions
It defines private/channel fence wrappers and the public `nv04_fence_create`. Internal operations are `nv04_fence_emit`, `nv04_fence_read`, `nv04_fence_sync`, context new/delete, and destroy.

## Control Flow
Creation allocates `drm->fence` and installs context callbacks. Each channel context allocates a `nouveau_fence_chan`, sets emit/read/sync methods, and stores it on the channel. Emit waits for push space, writes the sequence through NV_SW method `0x0150`, and kicks. Read issues `NV04_NVSW_GET_REF` on the channel software object. Cross-channel sync is unsupported and returns `-ENODEV`.

## State and Persistence Behavior
Global state is only the allocated fence private object. Per-channel state is the generic fence context. Fence progress persists in the hardware/software reference value read from `chan->nvsw`.

## Dependencies and Integration Points
It depends on Nouveau push macros, `nouveau_fence_context_*`, NVIF object method calls, and the NV_SW class interface.

## Risks
No cross-channel sync means callers need fallback waits. Push space failures propagate from emit. Read uses `WARN_ON` on method failure and returns possibly stale `args.ref`.

## Test Signals
Signals include fence emit/read on NV04-class hardware, channel context teardown, unsupported sync handling, and push-buffer exhaustion.
