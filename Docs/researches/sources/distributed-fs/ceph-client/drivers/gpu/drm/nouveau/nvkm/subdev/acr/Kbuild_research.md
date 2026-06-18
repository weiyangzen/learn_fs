# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/Kbuild

## Purpose
Builds the Nouveau ACR subdevice core, low-secure firmware loader, and generation-specific ACR implementations.

## Important APIs, types, and functions
Compiles `base.o`, `lsfw.o`, `gm200.o`, `gm20b.o`, `gp102.o`, `gp108.o`, `gv100.o`, `gp10b.o`, `tu102.o`, `ga100.o`, and `ga102.o`.

## Control flow, state, and persistence
No runtime logic. It determines which WPR builders, HS firmware loaders, and chipset constructors are linked.

## Dependencies and integration points
Included by `nvkm/subdev/Kbuild`. Objects depend on falcon firmware support, SEC2/PMU/GSP, memory/VMM, and firmware parsers.

## Risks and test signals
Omitting generation files breaks secure boot on those chips. Build success and ACR subdev probe/firmware boot validate inclusion.
