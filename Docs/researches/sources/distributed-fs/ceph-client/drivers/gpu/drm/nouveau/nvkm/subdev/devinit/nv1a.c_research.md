# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv1a.c

## Purpose
Defines NV1A devinit as a small NV04-compatible variant without custom memory initialization.

## Important APIs, types, and functions
Exports `nv1a_devinit_new()` and a static `nv1a_devinit` function table.

## Control flow
All runtime behavior is inherited from NV04 dtor/preinit/post/pll_set. No meminit hook is installed.

## State and persistence
State is the inherited NV04 saved VGA owner and common devinit post flags.

## Dependencies and integration points
Depends on `nv04.h` and NV04 helper functions.

## Risks
If an NV1A board needs memory probing, this function table will not perform it; support relies on firmware/BIOS initialization.

## Test signals
Boot/post and PLL programming on NV1A hardware without custom meminit.
