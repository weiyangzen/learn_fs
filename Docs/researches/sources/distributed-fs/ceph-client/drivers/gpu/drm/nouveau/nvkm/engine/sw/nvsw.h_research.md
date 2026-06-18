# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nvsw.h

## Purpose
Declares the private NVSW object used by software-channel classes.

## Important APIs, types, and functions
`struct nvkm_nvsw` embeds `struct nvkm_object`, a function table, and the owning software channel. `struct nvkm_nvsw_func` provides an optional object-method callback. The header declares generic and custom constructors.

## Control flow, state, and persistence
No runtime logic exists in the header. The object persists as a child of a software channel and uses the channel for events and generation state.

## Dependencies and integration points
Includes core object support and is used by SW generation files plus `nvsw.c`.

## Risks and test signals
Any signature change affects all software class constructors. Build coverage and userspace SW object creation are the main validation points.
