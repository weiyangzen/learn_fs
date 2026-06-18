# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/Kbuild

## Purpose
Adds the MXM subdevice objects to the NVKM build: `base.o`, `mxms.o`, and `nv50.o`.

## Important APIs, Types, And Functions
The build file is declarative. It ensures the core MXM constructor, MXM-SIS parser, and NV50 DCB sanitization logic are linked into the nouveau NVKM object set.

## Control Flow
There is no runtime control flow in this file. Build-time control is a straight `nvkm-y +=` object list.

## State And Persistence
No state is stored. Its persistence effect is build graph membership.

## Dependencies And Integration Points
Integrates with the kernel Kbuild system and the surrounding nouveau `nvkm-y` aggregation. Removing an object here would break MXM symbol availability.

## Risks And Test Signals
Risk is missing object linkage or stale source list after adding/removing MXM files. Test by building nouveau with MXM enabled paths and checking unresolved symbols for `nvkm_mxm_new_`, `mxms_*`, and `nv50_mxm_new`.
