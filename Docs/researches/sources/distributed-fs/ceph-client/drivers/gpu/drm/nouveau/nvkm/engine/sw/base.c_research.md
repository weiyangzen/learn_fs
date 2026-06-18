# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/base.c

## Purpose
Implements the common Nouveau software engine. It tracks per-FIFO software channels and dispatches software methods to channel-specific handlers.

## Important APIs, types, and functions
`nvkm_sw_new_()` allocates and constructs `struct nvkm_sw`. `nvkm_sw_mthd()` finds a channel by FIFO id and dispatches a method. `nvkm_sw_oclass_get()` exposes software object classes. `nvkm_sw_cclass_get()` creates per-channel software contexts through generation functions.

## Control flow, state, and persistence
The engine owns `sw->chan`, a list of active `nvkm_sw_chan` objects protected by `engine.lock`. Method dispatch scans for the matching channel id, calls `nvkm_sw_chan_mthd()`, and moves the channel to the list head as a locality optimization. State persists for the engine lifetime and per-channel object lifetime.

## Dependencies and integration points
Depends on FIFO channels, the nvkm object/class model, and generation-provided `nvkm_sw_func`. Integrated by FIFO when users create software channel classes.

## Risks and test signals
Wrong locking or stale list entries can misroute methods. Signals include successful software class creation, page-flip event delivery, and handled return values for SW methods.
