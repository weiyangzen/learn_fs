# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/priv.h

## Purpose
Defines the private MXM subdevice structure and constructor declaration.

## Important APIs, Types, And Functions
Defines `nvkm_mxm(p)` container macro, `MXM_SANITISE_DCB`, `struct nvkm_mxm`, and `nvkm_mxm_new_`.

## Control Flow
No executable control flow exists.

## State And Persistence
`struct nvkm_mxm` persists the subdev base, action flags, and owned MXMS blob pointer.

## Dependencies And Integration Points
Includes public `<subdev/mxm.h>` and is included by all MXM implementation files. The action bit is consumed by `nv50.c`.

## Risks And Test Signals
Risk is memory ownership or flag mismatch across files. Build tests catch layout/name drift; runtime unload tests should catch MXMS blob lifetime leaks.
