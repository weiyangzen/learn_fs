# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vic/Kbuild

## Purpose
Documents the disabled build hook for the Nouveau VIC engine.

## Important APIs, types, and functions
The only object entry, `nvkm/engine/vic/base.o`, is commented out.

## Control flow, state, and persistence
No runtime code is compiled from this directory in the current configuration.

## Dependencies and integration points
Included by the engine Kbuild, but it contributes no objects. It indicates an intended or historical VIC engine slot.

## Risks and test signals
Because the entry is disabled, no VIC nvkm engine support is built here. Build output should not include `engine/vic/base.o`.
