# sources/distributed-fs/openafs/src/tbozo/Makefile.in

## Purpose
`src/tbozo/Makefile.in` builds pthread/libtool variants of bosserver, `bos`, `bos_util`, and the BOS RPC support by reusing sources from `src/bozo`.

## Important APIs, types, and functions
Key targets are `all`, `generated`, `liboafs_bos.la`, `bosserver`, `bos`, `bos_util`, `install`, `dest`, and `clean`. Generated files include `bosint.cs.c`, `bosint.ss.c`, `bosint.xdr.c`, `bosint.h`, `bnode.h`, and `boserr.c`.

## Control flow
The makefile includes pthread and libtool config, runs `RXGEN` and `COMPILE_ET`, compiles selected `../bozo` C sources with `AFS_CCRULE`, links command/server binaries against auth, kauth, volser, rx, rxkad, rxstat, cmd, util, opr, LWP compatibility, sys, and process-management libraries, and installs only when `ENABLE_PTHREADED_BOS` is yes.

## State and persistence behavior
It writes generated RPC/error headers and C files, libtool objects, binaries, libraries, and install-tree files. `clean` removes generated BOS interface files and built products.

## Dependencies and integration points
It depends on the canonical bozo sources and `.xg`/`.et` files, top include/lib directories, pthread config, libtool, RXGEN, and compile_et. Outputs are part of the BOS administration/server toolchain.

## Risks
This shadow makefile must stay synchronized with `src/bozo` source lists and headers. Conditional install means builds can succeed without packaging pthreaded BOS if the configure flag is off. Library ordering is nontrivial.

## Test signals
Run `make generated`, build `bosserver`, `bos`, and `bos_util`, verify generated headers match `src/bozo`, and test install/dest with `ENABLE_PTHREADED_BOS` enabled and disabled.
