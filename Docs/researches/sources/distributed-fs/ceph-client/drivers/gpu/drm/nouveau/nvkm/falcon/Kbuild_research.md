# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/Kbuild

## Purpose
Builds the shared Nouveau falcon support library and generation-specific falcon operations.

## Important APIs, types, and functions
Compiles common objects `base.o`, `cmdq.o`, `fw.o`, `msgq.o`, `qmgr.o`, `v1.o` and generation files `gm200.o`, `gp102.o`, `tu102.o`, `ga100.o`, `ga102.o`.

## Control flow, state, and persistence
No runtime logic. Build inclusion makes generic falcon access, firmware boot, queues, and generation-specific register helpers available to SEC2, ACR, PMU, GSP, and other falcon users.

## Dependencies and integration points
Included by nvkm Kbuild. These files depend on core falcon structures, firmware parsers, memory/VMM, MC, timer, and subdev owners.

## Risks and test signals
Missing objects cause broad link or runtime failures. Build success plus SEC2/ACR/PMU firmware boot validate coverage.
