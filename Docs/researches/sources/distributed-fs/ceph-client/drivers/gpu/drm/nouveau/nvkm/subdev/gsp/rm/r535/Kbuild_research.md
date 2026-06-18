<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/Kbuild

## Purpose
Builds the R535/R570-style RM API implementation objects used by GSP-RM.

## Important APIs, Types, And Functions
Includes RM core, GSP, RPC, control/allocation/client/device, BAR, FBSR, VMM, display, FIFO, CE, GR, and video/OFA object files.

## Control Flow
Kbuild compiles all R535 API modules into NVKM so firmware-interface records can point at R535/R570 RM API tables.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects lower-level RM RPC/control wrappers to display, FIFO, memory, and engine implementations.

## Risks And Edge Cases
Omitted modules can leave function pointers unresolved or null in RM API tables.

## Test Signals
Build success and full GSP-RM feature availability at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/Kbuild -->
