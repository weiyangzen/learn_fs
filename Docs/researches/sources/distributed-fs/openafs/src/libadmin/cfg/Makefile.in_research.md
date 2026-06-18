# sources/distributed-fs/openafs/src/libadmin/cfg/Makefile.in

## Purpose
Builds and installs the configuration-admin static library and public header. The library combines local configuration modules with generated Ubik RPC client/XDR support.

## Important APIs, Types, And Functions
`UBIKOBJS` contains `ubik_int.cs.o` and `ubik_int.xdr.o`. `CFGOBJS` contains `cfgclient.o`, `cfgdb.o`, `cfghost.o`, `cfgservers.o`, and `cfginternal.o`. `LIBOBJS` archives both groups into `libcfgadmin.a`. Targets stage/install `afs_cfgAdmin.h` and `libcfgadmin.a`, build generated Ubik objects from `../../ubik`, and clean local build outputs.

## Control Flow
`all` installs the header into `${TOP_INCDIR}/afs` and the archive into `${TOP_LIBDIR}`. `libcfgadmin.a` removes any old archive, archives all objects, and runs `ranlib`. All configuration objects depend on `afs_cfgAdmin.h`, while Ubik generated objects are compiled through `$(AFS_CCRULE)`.

## State And Persistence
The makefile writes object files and `libcfgadmin.a` in the build tree and installs copies into top-level or destination include/lib directories. `clean` removes objects and `libcfgadmin*`.

## Dependencies And Integration Points
It includes the OpenAFS standard and pthread build fragments. It integrates configuration APIs with Ubik RPC stubs and with sibling implementation files that call BOS, client, KAS, PTS, and utility-admin libraries.

## Risks And Test Signals
Risks are stale object dependencies and missing generated Ubik sources. Useful signals are directory-level builds, archive-content inspection, and install/dest target checks that confirm `afs_cfgAdmin.h` and `libcfgadmin.a` land under the expected `afs` subdirectories.
