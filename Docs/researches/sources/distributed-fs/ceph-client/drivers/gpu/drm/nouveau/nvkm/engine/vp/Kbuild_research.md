# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vp/Kbuild

## Purpose
Builds the Nouveau VP engine implementation for G84-era video processing hardware.

## Important APIs, types, and functions
Adds `nvkm/engine/vp/g84.o` to `nvkm-y`.

## Control flow, state, and persistence
No runtime logic. Build inclusion makes the G84 VP constructor and Xtensa configuration available.

## Dependencies and integration points
Included by engine-level Kbuild. The object depends on the generic Xtensa engine and VP public header.

## Risks and test signals
Omitting the entry removes VP engine support. Build logs and class exposure for `NV74_VP2` validate inclusion.
