<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/Kbuild

## Purpose
Lists all Nouveau nvkm I2C subdev objects built into nvkm-y: base constructors, generation frontends, pad implementations, bus implementations, bit-bang logic, AUX implementations, and ANX9805 external encoder support.

## Important APIs, Types, And Functions
Important entries include base.o, nv04/nv4e/nv50/g94/gf117/gf119/gk104/gk110/gm200.o, pad*.o, bus*.o, bit.o, aux*.o, and anx9805.o.

## Control Flow
Kbuild has no runtime control flow; it controls link inclusion so chip constructors can reference shared helpers and generation-specific ops.

## State, Persistence, Dependencies, And Integration
State is build-system configuration. Dependencies are the surrounding DRM/Nouveau make hierarchy. Integration points are kernel build/link and module symbol availability.

## Risks And Test Signals
Risks: omitting one object breaks constructor references or feature support for a GPU generation. Test signals are successful kernel/module build and probe of each generation-specific I2C constructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/Kbuild -->
