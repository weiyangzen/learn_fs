# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/Kbuild

## Purpose
Declares the object files that build the Nouveau thermal subdevice implementation into `nvkm-y`.

## Important APIs, Types, And Functions
The file contributes these object targets: `base.o`, `fan.o`, `fannil.o`, `fanpwm.o`, `fantog.o`, `ic.o`, `temp.o`, `nv40.o`, `nv50.o`, `g84.o`, `gt215.o`, `gf100.o`, `gf119.o`, `gk104.o`, `gm107.o`, `gm200.o`, `gp100.o`. There are no runtime C APIs.

## Control Flow
Kbuild conditionlessly appends the listed objects when the Nouveau nvkm subtree is built; chip selection happens later through device tables and constructor calls.

## State, Persistence, And Dependencies
No runtime state is persisted. The only dependency is the kernel build system variable expansion for `nvkm-y`.

## Integration Points
Integrated by the parent Nouveau nvkm Kbuild so the thermal constructors and helpers are linkable.

## Risks
Missing an object silently removes a chip implementation at link time; adding an object here without matching declarations can create unresolved symbols.

## Test Signals
Build coverage is the primary signal: enabled Nouveau configurations should compile and link all listed objects.
