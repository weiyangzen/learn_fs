# sources/distributed-fs/openafs/src/libadmin/pts/Makefile.in

## Purpose
This makefile builds and installs the PTS admin static library and public header.

## Important APIs, Types, and Functions
`ADMINOBJS` contains `afs_ptsAdmin.o`. `PTSERVEROBJS` adds generated protection-server RPC/XDR client objects `ptint.xdr.o` and `ptint.cs.o`. `libptsadmin.a` archives all three object groups. `all`, `install`, and `dest` install `afs_ptsAdmin.h` and the static archive. `clean` removes local objects and archives.

## Control Flow and State
The build compiles the local PTS admin implementation and generated ptserver sources from `../../ptserver`, archives them, indexes the archive, and copies artifacts to build or installation destinations.

## Persistence and Side Effects
Generated artifacts include local object files and `libptsadmin.a`; install/dest targets create include/lib directories and copy outputs. Clean deletes local generated files.

## Dependencies and Integration Points
The PTS admin archive depends on ptserver RPC/XDR sources. It is linked by cfg tests and other admin tooling that needs protection database operations. Client admin cell handles provide authenticated PTS ubik clients to the PTS implementation.

## Risks
Generated RPC source paths must remain valid relative to this directory. The object dependency `afs_ptsAdmin.o: afs_ptsAdmin.h` does not mention internal headers. Static library consumers need correct archive ordering with auth/rpc and ubik dependencies.

## Test Signals
Build signals include successful compilation of generated ptserver objects, creation/indexing of `libptsadmin.a`, correct install/dest placement, and downstream link success for cfg or PTS admin tests.
