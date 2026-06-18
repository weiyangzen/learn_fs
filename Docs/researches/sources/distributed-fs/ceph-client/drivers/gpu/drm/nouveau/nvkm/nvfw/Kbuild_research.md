# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/Kbuild

## Purpose
Builds Nouveau firmware-format parser/debug helpers for NVIDIA binary firmware structures.

## Important APIs, types, and functions
Compiles `fw.o`, `hs.o`, `ls.o`, `acr.o`, and `flcn.o`.

## Control flow, state, and persistence
No runtime logic in the Kbuild file. It controls availability of parsers and dump helpers used by falcon and ACR code.

## Dependencies and integration points
Included by nvkm build logic. Parser users include `falcon/fw.c`, `subdev/acr/*`, and `engine/sec2/*`.

## Risks and test signals
Missing parser objects break firmware construction and ACR WPR handling. Build and firmware-load paths validate inclusion.
