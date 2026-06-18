# sources/distributed-fs/openafs/src/rx/bulktest/Makefile.in

Purpose: legacy bulk-test makefile for building Rx bulk client/server examples.

Important APIs/types/functions: targets `bulk_client`, `bulk_server`, generated `bulk.cs.c`, `bulk.ss.c`, `bulk.er.c`, and `bulk.h`.

Control flow: includes config/LWP make fragments, uses hard-coded `SRCDIR=/usr/andy/` library paths for Rx/LWP, invokes `rxgen bulk.xg`, and links with `AFS_LDRULE`.

State/persistence: generated rxgen files and example binaries.

Dependencies/integration: legacy local installation layout, Rx, LWP, rxgen, and bulk sources.

Risks: hard-coded paths are non-portable and differ from modern build-tree conventions; lacks a clean target in the shown file. Test signals are mostly historical: build only in a matching developer layout or after Makefile modernization.
