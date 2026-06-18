<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/Kbuild

## Purpose
Builds the generic GSP-RM bridge objects and GPU class tables.

## Important APIs, Types, And Functions
Includes `client.o`, `engine.o`, `gr.o`, `nvdec.o`, `nvenc.o`, generation GPU table files, and the `r535/` subdirectory.

## Control Flow
Kbuild compiles common RM object wrappers, engine constructors, and per-generation class constants.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects RM client/object machinery with R535/R570 APIs and generation GSP function tables.

## Risks And Edge Cases
Omitted object files can produce missing RM class mappings or engine constructors.

## Test Signals
Build success and availability of RM-backed engines for supported GSP-RM GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/Kbuild -->
