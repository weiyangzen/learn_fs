# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/priv.h

## Purpose
Defines the private software-engine function table and constructor shared by all Nouveau SW engine implementations.

## Important APIs, types, and functions
`struct nvkm_sw_func` contains a per-channel constructor and an array of software object classes. `struct nvkm_sw_chan_sclass` pairs a channel object constructor with an `nvkm_sclass`. `nvkm_sw_new_()` constructs a software engine from a function table.

## Control flow, state, and persistence
No code runs here. The structures drive class enumeration, per-FIFO channel creation, and SW object construction in `base.c`.

## Dependencies and integration points
Includes public `engine/sw.h` and forward declares `nvkm_sw_chan`. Used by all files in `engine/sw`.

## Risks and test signals
Incorrect class arrays or constructors surface as missing NVIF software classes. Build coverage catches structural signature drift.
