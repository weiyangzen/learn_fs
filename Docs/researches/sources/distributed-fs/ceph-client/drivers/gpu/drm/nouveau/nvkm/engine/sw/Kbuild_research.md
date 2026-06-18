# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/Kbuild

## Purpose
Builds the Nouveau software engine implementation and generation-specific software classes.

## Important APIs, types, and functions
Compiles `base.o`, generation files `nv04.o`, `nv10.o`, `nv50.o`, `gf100.o`, plus shared `chan.o` and `nvsw.o`.

## Control flow, state, and persistence
No runtime logic. It determines which software FIFO class constructors and method handlers are present in the module.

## Dependencies and integration points
Included by the engine-level Kbuild. These objects integrate with FIFO, display vblank events, BAR flushes, and NVIF software class APIs.

## Risks and test signals
Omitting a generation file removes software class support for that GPU family. Build success and class enumeration through NVIF are the primary signals.
