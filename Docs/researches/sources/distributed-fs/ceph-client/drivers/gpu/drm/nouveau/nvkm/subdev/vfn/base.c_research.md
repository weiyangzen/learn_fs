# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/base.c

## Purpose
Implements common VFN subdevice construction for usermode register aperture exposure and optional interrupt fanout.

## Important APIs, Types, And Functions
`nvkm_vfn_new_()` allocates `struct nvkm_vfn`, sets private/user address bases, registers optional interrupt leaves through `nvkm_intr_add()`, and installs the user object constructor `nvkm_uvfn_new`.

## Control Flow
Construction computes `addr.user = addr.priv + func->user.addr`; if an interrupt function is provided it creates an interrupt controller with up to eight leaves; then it advertises a user class and aperture size.

## State, Persistence, And Dependencies
State includes `nvkm_vfn`, address fields, interrupt object, and user class metadata.

## Integration Points
Depends on nvkm subdev construction, interrupt infrastructure, and `uvfn.c` for mapping usermode registers to clients.

## Risks
If interrupt registration fails, construction returns an error after allocation. Address arithmetic must match chip BAR0 layouts.

## Test Signals
Signals include successful VFN subdev creation, valid usermode object class exposure, and interrupt leaves dispatching to configured subdevices.
