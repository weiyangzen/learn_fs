# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/Kbuild

## Purpose
Builds Nouveau BAR subdevice implementations for NV50 through GM20B-era hardware.

## Important APIs, types, and functions
Compiles `base.o`, `nv50.o`, `g84.o`, `gf100.o`, `gk20a.o`, `gm107.o`, `gm20b.o`, and `tu102.o`.

## Control flow, state, and persistence
No runtime logic. It selects the BAR management implementations available to chipset constructors.

## Dependencies and integration points
Included by `nvkm/subdev/Kbuild`. BAR objects depend on memory, VMM, FB, MMU, timer, and device resource-size hooks.

## Risks and test signals
Missing BAR objects break BAR1/BAR2 mapping setup. Build output and BAR subdev init logs validate inclusion.
