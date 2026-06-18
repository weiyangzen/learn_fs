# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/Kbuild

## Purpose
Builds the Nouveau fault subdevice objects for generic fault handling, user exposure, and GP100/GP10B/GV100/TU102 implementations.

## Important APIs, types, and functions
The Kbuild file adds `base.o`, `user.o`, `gp100.o`, `gp10b.o`, `gv100.o`, and `tu102.o` to `nvkm-y`.

## Control flow
No runtime flow; it controls link composition.

## State and persistence
No runtime state.

## Dependencies and integration points
Integrated by the parent NVKM build. Constructors referenced by chipset tables must be present in this list.

## Risks
Omitting `user.o` or a generation object would break user event exposure or chipset-specific fault support.

## Test signals
Kernel build/link coverage and modpost symbol resolution for fault constructors and user object helpers.
