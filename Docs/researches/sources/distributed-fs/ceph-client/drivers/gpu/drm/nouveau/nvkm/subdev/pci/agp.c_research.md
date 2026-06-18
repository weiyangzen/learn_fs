# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/agp.c

## Purpose
Implements optional AGP bridge setup, teardown, mode quirks, preinit reset, and write-combining aperture setup for AGP NVIDIA devices.

## Important APIs, Types, And Functions
Exports `nvkm_agp_ctor`, `nvkm_agp_dtor`, `nvkm_agp_preinit`, `nvkm_agp_init`, and `nvkm_agp_fini` when AGP is enabled. Defines quirk table `nvkm_device_agp_quirks`.

## Control Flow
Constructor temporarily acquires the AGP bridge, copies mode/base/size info, applies `NvAGP`, platform defaults, and hostbridge/chip quirks, disables fast writes on NV18, and registers write-combining. Preinit disables fast writes if needed, disables bus mastering/AGP, resets PGRAPH/PFIFO/PTIMER, and restores bus mastering. Init acquires and enables the backend; fini releases it.

## State And Persistence
Stores bridge pointer, AGP mode/base/size/CMA, MTRR handle, and acquired flag inside `pci->agp`. Hardware AGP mode and CPU WC mapping persist until fini/dtor.

## Dependencies And Integration Points
Depends on Linux AGP backend, PCI IDs, architecture WC APIs, and `NvAGP` options. Called from PCI base constructor/preinit/init/fini/dtor.

## Risks And Test Signals
Risks include bridge acquisition failure, bad quirks, fast-write lockups, PowerPC GATT issues, WC mapping leaks, and mode mismatches. Test AGP mode 0/1/2/4/8, quirked VIA/SiS platforms, NV18, module unload, and VBIOS init requiring stable AGP reset.
