# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/module.mk.in

## Purpose
Build-system fragment that adds DBPF backend source files to the OrangeFS server build and selects the database backend implementation.

## Important APIs, Types, And Functions
Sets `DIR := src/io/trove/trove-dbpf`, appends DBPF bstream, collection, AIO, keyval, attr-cache, open-cache, dspace, context, op, queue, thread, management, keyval pcache, sync, alternate/null/direct bstream sources to `SERVERSRC`, conditionally adds `dbpf-db-bdb.c` or `dbpf-db-lmdb.c` based on `DATABASE_BACKEND`, and sets module CFLAGS.

## Control Flow
The make include is consumed by the broader build system. Backend selection is a make-time branch; all common DBPF sources are compiled, then the configured DB wrapper implementation is added.

## State And Persistence
No runtime state. It controls which source files participate in the binary and adds include/feature flags that affect compilation.

## Dependencies And Integration Points
Depends on the build variables `SERVERSRC`, `DATABASE_BACKEND`, `srcdir`, and `MODCFLAGS_$(DIR)`. It adds the handle-management include path so `trove-ledger.h` is visible and defines `_GNU_SOURCE` for Linux pread/pwrite access while avoiding `_XOPEN_SOURCE` conflicts with Berkeley DB.

## Risks And Test Signals
Risks include missing new DBPF files from `SERVERSRC`, wrong DB backend selected, and feature macro conflicts with system/db headers. Test signals are successful builds with both BDB and LMDB settings and compile coverage of direct/null/alt AIO files.
