# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/chan.h

## Purpose
Declares the private software-channel type and method/event hooks shared by SW engine implementations.

## Important APIs, types, and functions
`struct nvkm_sw_chan` contains the nvkm object, parent software engine, FIFO channel, list node, and event object. `struct nvkm_sw_chan_func` provides optional destructor and method callbacks. The header declares `nvkm_sw_chan_ctor()` and `nvkm_sw_chan_mthd()`, and defines `NVKM_SW_CHAN_EVENT_PAGE_FLIP`.

## Control flow, state, and persistence
No code runs here. The declarations define per-channel state persisted while a software channel object is live.

## Dependencies and integration points
Includes core object/event headers and `priv.h`. Used by `chan.c`, generation SW files, and `nvsw.c`.

## Risks and test signals
ABI changes affect all generation files. Build coverage catches most signature drift; runtime page-flip event delivery validates event bit wiring.
