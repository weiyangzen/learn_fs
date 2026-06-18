# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/Kbuild

## Purpose
Aggregates Nouveau nvkm subdevice build fragments.

## Important APIs, types, and functions
Includes Kbuild files for ACR, BAR, BIOS, bus, clock, devinit, fault, FB, fuse, GPIO, FSP, GSP, I2C, instance memory, LTC, MC, MMU, MXM, PCI, PMU, privring, therm, timer, TOP, VFN, and volt.

## Control flow, state, and persistence
There is no runtime logic. Build ordering and inclusion determine available subdevice constructors.

## Dependencies and integration points
This file is the integration point from top-level nvkm build logic into individual subdev directories, including the ACR and BAR subdirectories researched in this group.

## Risks and test signals
Missing includes remove entire subdevice families. Build logs and module link success are the primary signals.
