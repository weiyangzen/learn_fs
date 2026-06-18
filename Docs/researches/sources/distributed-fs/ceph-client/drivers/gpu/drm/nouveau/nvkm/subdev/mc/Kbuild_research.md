# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/Kbuild

## Purpose
Builds the Nouveau NVKM master-control subdevice and chip-specific MC backends.

## Important APIs, Types, and Functions
The fragment links `base.o` plus MC variants from NV04 through GA100, including G84/G98/GT215, Fermi/Kepler, Tegra, Pascal, and Ampere.

## Control Flow, State, and Persistence
No runtime flow exists. Object inclusion determines which constructors and shared reset/interrupt maps are available to device tables.

## Dependencies and Integration Points
Integrated by the parent NVKM Kbuild. It must match all MC constructors referenced by chipset discovery.

## Risks and Test Signals
Missing object entries cause unresolved symbols or absent hardware support. Kernel build matrices and module-load smoke tests on each generation are the main signals.
