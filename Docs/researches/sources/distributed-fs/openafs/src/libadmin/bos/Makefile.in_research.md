# sources/distributed-fs/openafs/src/libadmin/bos/Makefile.in

## Purpose
Builds and installs the BOS admin static library and public header. It compiles the local BOS admin wrapper plus generated bozo RPC client/XDR objects, archives them into `libbosadmin.a`, and installs the library and `afs_bosAdmin.h` into the configured include/lib trees.

## Important APIs, Types, And Functions
Important variables are `BOZO=../../bozo`, `ADMINOBJS=afs_bosAdmin.o`, `BOZOOBJS=bosint.xdr.o bosint.cs.o`, and `LIBOBJS=${ADMINOBJS} ${BOZOOBJS}`. Targets include `all`, header/library staging into `${TOP_INCDIR}` and `${TOP_LIBDIR}`, `install`, `dest`, `libbosadmin.a`, generated-RPC object builds from `${BOZO}/bosint.xdr.c` and `${BOZO}/bosint.cs.c`, and `clean`.

## Control Flow
`all` first ensures the public header is installed in the top include directory and then builds/stages `libbosadmin.a`. The archive target removes any old archive, runs `$(AR) $(ARFLAGS)`, then `$(RANLIB)`. The generated bozo RPC source files are compiled with `$(AFS_CCRULE)`. `install` and `dest` create destination include/lib directories and copy the source header plus archive.

## State And Persistence
The makefile creates object files and `libbosadmin.a` in the build tree and installs copies under `${TOP_INCDIR}`, `${TOP_LIBDIR}`, `${DESTDIR}${includedir}/afs`, `${DESTDIR}${libdir}/afs`, or `${DEST}` depending on target. `clean` removes local objects and `libbosadmin*`.

## Dependencies And Integration Points
It includes OpenAFS build configuration and pthread make fragments. It integrates the libadmin BOS wrapper with generated bozo RPC stubs from `src/bozo`, making the BOS admin library depend on the bozo RPC contract.

## Risks And Test Signals
Risks are ordinary build-system drift: missing regenerated `bosint` sources, stale header installation, and archive contents diverging from implementation. Test signals are `make` in this directory, install/dest dry-runs, and verifying `libbosadmin.a` contains `afs_bosAdmin.o`, `bosint.xdr.o`, and `bosint.cs.o`.
