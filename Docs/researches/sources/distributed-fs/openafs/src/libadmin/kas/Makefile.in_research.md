# sources/distributed-fs/openafs/src/libadmin/kas/Makefile.in

## Purpose
This makefile builds and installs the KAS admin static library and public header.

## Important APIs, Types, and Functions
`ADMINOBJS` is `afs_kasAdmin.o`. `KAUTHOBJS` imports generated/client KAuth support objects `kauth.cs.o`, `kauth.xdr.o`, and `kaaux.o`. `libkasadmin.a` archives both admin and KAuth support objects. `all`, `install`, and `dest` copy `afs_kasAdmin.h` and the archive into build/install destinations.

## Control Flow and State
The build compiles the local admin object and KAuth support sources from `../../kauth`, archives them, runs `ranlib`, and installs the public header/library. The KAuth objects are compiled through `$(AFS_CCRULE)` from source paths outside this directory.

## Persistence and Side Effects
Generated outputs include object files and `libkasadmin.a`; install/dest targets create include/lib directories and copy artifacts. Clean removes local objects and KAS admin archives.

## Dependencies and Integration Points
The KAS admin library depends on KAuth RPC/XDR generated code and `kaaux.c`. Client admin cell handles provide KAS ubik clients consumed by `afs_kasAdmin.c`. Other admin components link this archive for authentication database management.

## Risks
The archive bundles generated KAuth RPC objects, so it must stay in sync with the kauth interface. Relative paths to `../../kauth` are sensitive to build layout. As with other static OpenAFS makefiles, library order matters for downstream link lines.

## Test Signals
Signals include successful rebuild after KAuth RPC source changes, install/dest header and archive placement, and downstream link success for code calling KAS admin APIs.
