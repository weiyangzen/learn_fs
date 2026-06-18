<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/Kbuild

## Purpose
Builds Nouveau GPIO subdevice support for multiple GPU generations.

## Important APIs, Types, And Functions
Adds common `base.o` and generation objects `nv10.o`, `nv50.o`, `g94.o`, `gf119.o`, `gk104.o`, and `ga102.o`.

## Control Flow
Kbuild includes these objects in the NVKM build.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects shared GPIO APIs with chipset register-map implementations.

## Risks And Edge Cases
Missing an object removes constructor support for a generation. Adding new GPIO generations requires corresponding build inclusion.

## Test Signals
Build success and constructor availability for all listed generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/Kbuild -->
