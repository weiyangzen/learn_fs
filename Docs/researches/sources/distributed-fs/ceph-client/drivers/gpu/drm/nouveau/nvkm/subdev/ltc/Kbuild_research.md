# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/Kbuild

## Purpose
Adds the LTC subdevice objects to the Nouveau NVKM build for Fermi through Ampere/Tegra variants.

## Important APIs, Types, and Functions
The build list includes `base.o`, `gf100.o`, `gk104.o`, `gm107.o`, `gm200.o`, `gp100.o`, `gp102.o`, `gp10b.o`, and `ga102.o`.

## Control Flow, State, and Persistence
There is no runtime control flow. Build order makes the shared base and exported generation helpers available before chip-specific constructors are linked.

## Dependencies and Integration Points
This Kbuild fragment is included by the Nouveau NVKM kernel build. It must stay aligned with chip constructors referenced by device tables.

## Risks and Test Signals
Omitting an object causes unresolved constructor or helper symbols for that GPU family. Signals are kernel build coverage for all enabled Nouveau configurations and module load on supported chips.
