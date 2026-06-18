<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/Kbuild

## Purpose
Builds the FSP subdevice objects into the Nouveau NVKM module.

## Important APIs, Types, And Functions
Lists `base.o`, `gh100.o`, `gb100.o`, and `gb202.o` in `nvkm-y`.

## Control Flow
Kbuild includes these objects unconditionally in the NVKM build when this source tree is built.

## State And Persistence
No runtime state. It controls build composition.

## Dependencies And Integration Points
Connects FSP base logic with GH100 and Blackwell generation implementations.

## Risks And Edge Cases
Omitting a generation object would leave its constructor unresolved or unsupported. Adding an object without matching declarations can create link errors.

## Test Signals
Kernel module build success and availability of FSP constructors for supported GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/Kbuild -->
