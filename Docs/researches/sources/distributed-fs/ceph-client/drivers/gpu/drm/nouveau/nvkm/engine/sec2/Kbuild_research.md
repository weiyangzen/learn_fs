# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/Kbuild

## Purpose
Adds SEC2 engine objects to the Nouveau nvkm build. It selects the common SEC2 core and per-generation implementations for Pascal, Turing, Ampere, and R535/GSP-backed operation.

## Important APIs, types, and functions
The build entries compile `base.o`, `gp102.o`, `gp108.o`, `tu102.o`, `ga102.o`, and `r535.o` into `nvkm-y`.

## Control flow, state, and persistence
There is no runtime logic. Build inclusion controls which constructors and firmware-interface tables are available to chipset dispatch code.

## Dependencies and integration points
Included by the higher-level Nouveau engine Kbuild. These objects depend on the falcon, ACR, firmware, interrupt, GSP, and SEC2 public headers.

## Risks and test signals
Missing entries cause unresolved constructors or absent SEC2 support on affected GPUs. Build logs and module symbol resolution are the main tests; runtime probe logs confirm the correct generation file was linked.
