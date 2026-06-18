# sources/distributed-fs/openafs/src/volser/Makefile.in

## Purpose
Builds and installs the OpenAFS volume server tools, generated RX interfaces, and volser libraries.

## Important Targets And Variables
Major outputs are `volserver`, `vos`, `restorevol`, `voldump`, `libvolser.a`, `liboafs_volser.la`, `libvolser_pic.la`, installed headers `volser.h`, `volint.h`, `volser_prototypes.h`, and `vsutils_prototypes.h`. `SOBJS` define volserver server-side objects, `LT_objs` define client/library objects, `LIBS` collects volserver dependencies, and `VOLDUMP_LIBS` supplies the standalone dump utility.

## Control Flow And Build Integration
Generated files come from `volerr.et` via `COMPILE_ET_*` and `volint.xg` via `RXGEN`. Build rules link LWP and libtool variants, then install binaries and headers into server/client locations. Platform conditionals skip or alter volserver installation on Linux, AIX, SGI, Solaris, and Darwin families.

## State And Persistence
The makefile itself does not persist runtime state, but it controls generated source files and installed artifacts. Clean removes generated C/header files, objects, libraries, and binaries.

## Risks And Test Signals
Risks include stale dependency lists after source/header changes, duplicated or order-sensitive libraries, generated-interface mismatch, platform install typos, and divergence between `install` and `dest`. Test signals include full `make all`, `make generated`, clean rebuild, libtool library symbol checks, `check-splint`, and install/dest dry-runs on supported platform families.
