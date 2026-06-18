# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/Kbuild

## Purpose
Declares the object files that build the Nouveau privring subdevice implementation into `nvkm-y`.

## Important APIs, Types, And Functions
The file contributes these object targets: `gf100.o`, `gf117.o`, `gk104.o`, `gk20a.o`, `gm200.o`, `gp10b.o`. There are no runtime C APIs.

## Control Flow
Kbuild conditionlessly appends the listed objects when the Nouveau nvkm subtree is built; chip selection happens later through device tables and constructor calls.

## State, Persistence, And Dependencies
No runtime state is persisted. The only dependency is the kernel build system variable expansion for `nvkm-y`.

## Integration Points
Integrated by the parent Nouveau nvkm Kbuild so the privring constructors and helpers are linkable.

## Risks
Missing an object silently removes a chip implementation at link time; adding an object here without matching declarations can create unresolved symbols.

## Test Signals
Build coverage is the primary signal: enabled Nouveau configurations should compile and link all listed objects.
