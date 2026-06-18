# sources/distributed-fs/openafs/src/venus/test/Makefile.in

## Purpose
This makefile builds the small Venus test utilities in `src/venus/test`: `fulltest`, `owntest`, `idtest`, and `getinitparams`. It wires them into the OpenAFS build system with the required command, pioctl/syscall, auth, ubik, VLDB, RX, utility, roken, and crypto libraries.

## Important APIs, Types, And Functions
The important targets are `all`, `test`, `fulltest`, `owntest`, `idtest`, `getinitparams`, and `clean`. `LT_deps` lists OpenAFS libtool archive dependencies, including `liboafs_sys`, `liboafs_ubik`, `liboafs_vldb`, `liboafs_auth`, `liboafs_rxkad`, `liboafs_comerr`, `liboafs_cmd`, `liboafs_rx`, `liboafs_util`, and `liboafs_opr`. `LT_libs` appends roken, hcrypto, and platform libraries.

## Control Flow
The default `all` and `test` targets build all four programs. Each executable links the corresponding object with `$(LT_LDRULE_static)`, the dependency archives, and external libraries. `install` and `dest` are intentionally empty, so these diagnostics are build/test artifacts rather than installed user commands. `clean` invokes `$(LT_CLEAN)` and removes objects and binaries.

## State And Persistence
The makefile creates object files and four local test executables in the build directory, and removes them during clean. It does not install persistent artifacts or modify source files.

## Dependencies And Integration Points
It includes `Makefile.config` and `Makefile.pthread`, so it inherits compiler, libtool, threading, and platform settings from the top-level OpenAFS build. It integrates test binaries with the same libraries used by Venus command tools, especially pioctl/syscall and command parsing support for `getinitparams`.

## Risks And Test Signals
Risks include dependency drift if test programs stop needing or newly need libraries, static link portability, and the empty install targets meaning packaging will not naturally exercise these tests. Test signals are successful `make test` or `make all` in this directory, clean rebuilds, and running the resulting binaries against an AFS mount/cache manager.
