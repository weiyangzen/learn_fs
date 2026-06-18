# sources/distributed-fs/openafs/src/libadmin/client/Makefile.in

## Purpose
This makefile builds and installs the OpenAFS client admin static library and public header.

## Important APIs, Types, and Functions
`ADMINOBJS` contains `afs_clientAdmin.o`; `LIBOBJS` mirrors it. The `all` target installs `afs_clientAdmin.h` into `$(TOP_INCDIR)/afs` and `libclientadmin.a` into `$(TOP_LIBDIR)`. `install` and `dest` copy the header and archive to configured or destination include/lib trees. `libclientadmin.a` is built with `$(AR)` and indexed with `$(RANLIB)`.

## Control Flow and State
The build compiles `afs_clientAdmin.c` into one object, archives it, and copies the archive/header into build or install destinations. The explicit dependency `afs_clientAdmin.o: afs_clientAdmin.h` ensures public API changes rebuild the object.

## Persistence and Side Effects
Generated artifacts are `afs_clientAdmin.o` and `libclientadmin.a`; install/dest targets create include and library directories and copy outputs. `clean` removes local objects and library archives.

## Dependencies and Integration Points
The file relies on OpenAFS global make configuration and pthread settings. Downstream admin libraries and tests link `libclientadmin.a` for token, cell, mountpoint, ACL, server enumeration, stats, and rxdebug helpers.

## Risks
The library is a single-object archive, so any change in `afs_clientAdmin.c` rebuilds the full archive. Install and dest paths differ (`DESTDIR`/configured prefix versus `DEST` staging), and packaging must invoke the correct target. Missing dependency declarations on internal headers can cause stale builds if those internals change.

## Test Signals
Build tests should confirm the header and archive appear in top-level and install destinations, `ranlib` succeeds, and `make clean` removes local generated outputs without touching installed artifacts.
