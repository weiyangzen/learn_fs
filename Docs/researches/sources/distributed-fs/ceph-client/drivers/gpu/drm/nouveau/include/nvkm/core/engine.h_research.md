# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/engine.h

## Purpose
Declares the NVKM engine base class used by graphics, copy, video, display-related engines, and FIFO channel object class hooks.

## Important APIs, Types, And Functions
Defines `struct nvkm_engine`, `nvkm_engine_func`, constructors, ref/unref, reset, tile update, channel-switch-load query, base/fifo class hooks, and `sclass` arrays.

## Control Flow
Engine lifecycle calls dtor/preinit/oneinit/init/fini/reset/intr callbacks. FIFO hooks expose engine channel classes. Tile and chsw callbacks update memory tile state and channel-switch state.

## State And Persistence
Engine state includes function table, embedded subdevice, and lock. Subclass-specific state persists in containing engine implementations.

## Dependencies And Integration Points
Depends on `core/subdev.h`, `core/oclass.h`, channel and framebuffer tile types; used by engine implementations and FIFO object construction.

## Risks
Callback ordering and ref/unref correctness are critical. Missing nonstall/intr/reset hooks can leave engines wedged after faults.

## Test Signals
Engine init/fini/reset, interrupt handling, channel class creation, tile update tests, and suspend/resume validate behavior.
