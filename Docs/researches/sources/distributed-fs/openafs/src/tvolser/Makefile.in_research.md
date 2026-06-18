# sources/distributed-fs/openafs/src/tvolser/Makefile.in

## Purpose
Builds the threaded volume server (`volserver`) and volume administration client (`vos`) from canonical volser, vol, dir, and vlserver sources.

## Important APIs, Types, And Functions
Object groups include volserver RPC/procedure objects, VLDB client RPC objects, directory objects, volume package objects, and common libraries. Generated files include `vl_errors.c`, `volerr.c`, and `volser.h`; volserver uses `volint.cs/ss/xdr` sources from `../volser`. Targets are `volserver`, `vos`, install/dest, and clean.

## Control Flow
The makefile compiles volser server/client sources with `-I../volser`, compiles shared volume and directory package files, generates error tables, links `vos` with ubik/volser client libraries, and links `volserver` with server-side ACL/common libraries. Install always installs `volserver`; `vos` installation is conditional on pthreaded ubik.

## State And Persistence
Build artifacts are objects, generated error headers/sources, `volserver`, and `vos`. Installed binaries affect persistent OpenAFS server/admin tooling, but the makefile itself does not touch volume data.

## Dependencies And Integration Points
This wrapper ties together volser RPC, VLDB interfaces, ubik client libraries, FSSYNC/SALVSYNC client support, volume package, directory package, rx/rxkad/rxstat, cmd, util, usd, and lwpcompat libraries. It has an AIX-specific link export flag for `volserver`.

## Risks And Test Signals
Risks include many shared sources compiled with different include paths/defines, generated header ordering, conditional `vos` install, and platform-specific linker flags. Signals include full threaded build, generated `volser.h` rebuilds, `vos` and `volserver` link success, AIX link testing, and install path validation.
