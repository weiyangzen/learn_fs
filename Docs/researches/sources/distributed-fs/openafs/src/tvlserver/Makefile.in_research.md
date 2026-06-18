# sources/distributed-fs/openafs/src/tvlserver/Makefile.in

## Purpose
Builds pthreaded versions of Volume Location Server tools from `src/vlserver`: `vlserver`, `vlclient`, `cnvldb`, and `vldb_check`, plus generated VL RPC and error headers.

## Important APIs, Types, And Functions
Targets include `vlserver`, `vlclient`, `cnvldb`, `vldb_check`, generated `vldbint.ss.c`, `vldbint.xdr.c`, `vldbint.h`, `vl_errors.c`, and `vlserver.h`. Library groups combine pthreaded ubik, sys, Rx, rxstat, rxkad, lwpcompat, cmd, util, opr, audit, and vldb client libraries.

## Control Flow
The makefile compiles source files from `$(VLSERVER)`, runs `RXGEN` on `vldbint.xg`, runs compile_et on `vl_errors.et`, links tools with static libtool rules, and conditionally installs server/checker/converter when `ENABLE_PTHREADED_UBIK` is `yes`. `vlclient` is built but not installed by the install target.

## State And Persistence
Generated files, objects, and binaries are build artifacts. Installed outputs persist server-side VLDB tools in configured directories. Runtime VLDB state is unaffected by the build.

## Dependencies And Integration Points
This is a pthreaded wrapper around the canonical VL server source tree and ubik library. It depends on rxgen, compile_et, version generation, OpenAFS library targets, and pthread configuration.

## Risks And Test Signals
Risks include missing dependency edges for generated headers, conditional installation surprises, and link-order differences from non-threaded builds. Test signals are a full `make all`, regenerated interface/error files, `vlserver` and `vldb_check` link success, and install gating with `ENABLE_PTHREADED_UBIK`.
