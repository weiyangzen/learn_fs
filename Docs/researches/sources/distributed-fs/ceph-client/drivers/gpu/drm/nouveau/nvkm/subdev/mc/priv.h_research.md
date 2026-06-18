# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/priv.h

## Purpose
Defines the private MC backend contract and shared declarations for reset maps, interrupt data, and device enable methods.

## Important APIs, Types, and Functions
`struct nvkm_mc_map` maps PMC bits to subdevice type/instance and optional `noauto`. `struct nvkm_mc_func` contains init, interrupt, device control, reset map, and `unk260` hooks. Shared exports cover NV04, NV17, GT215, GF100, GK104, and GP100 helpers.

## Control Flow, State, and Persistence
No executable flow. The function tables drive base.c reset, enable, interrupt registration, and special register programming.

## Dependencies and Integration Points
Includes public `subdev/mc.h` and is consumed by all MC backends. It links MC to the generic `nvkm_intr` framework.

## Risks and Test Signals
Risks are signature drift, incorrectly marked `noauto`, and function tables missing mandatory device callbacks. Build every chip backend and test reset/interrupt paths.
