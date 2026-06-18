# sources/distributed-fs/openafs/src/libadmin/vos/Makefile.in

## Purpose

`Makefile.in` builds and installs the OpenAFS VOS admin static library, `libvosadmin.a`, and installs its public header `afs_vosAdmin.h`.

## Important APIs, Types, and Functions

The makefile defines object groups for local admin code (`afs_vosAdmin.o`, `vosutils.o`, `vsprocs.o`, `lockprocs.o`) and generated/cross-directory RPC stubs from `vlserver`, `volser`, and `fsint` (`vldbint.*`, `volint.*`, `afsint.xdr.o`, `afscbint.xdr.o`). `LIBOBJS` combines those into `libvosadmin.a`. The `all`, `install`, `dest`, and `clean` targets are the primary entry points.

## Control Flow

Build flow installs the public header into `${TOP_INCDIR}/afs`, archives all library objects with `$(AR)`, and runs `$(RANLIB)`. Cross-directory `.c` files are compiled with `$(AFS_CCRULE)`. `install` and `dest` create include/library directories and copy the header and archive into packaging or destination trees.

## State and Persistence Behavior

The makefile creates build artifacts: object files, `libvosadmin.a`, and installed copies of the library/header. It does not manage runtime state.

## Dependencies and Integration Points

It includes OpenAFS config and pthread make fragments. The library depends on generated VLDB, volserver, and fsint RPC code and on the local `vsprocs`/`lockprocs` helpers. `afs_vosAdmin.o` explicitly depends on `afs_vosAdmin.h`.

## Risks and Test Signals

The archive directly includes generated RPC client/XDR objects, so stale generated sources or cross-directory path changes can break the build. `clean` removes `*.o` and `libvosadmin*` but not installed artifacts. Test signals are successful `make`, header installation, archive symbol availability for all declared VOS admin APIs, and clean rebuild after generated RPC files change.
