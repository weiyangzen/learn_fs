# sources/distributed-fs/openafs/src/butc/test_budb.c

Purpose: live integration stress test for BUDB database operations used by backup tape workflows. It connects to the backup database server, creates dump/tape/volume hierarchies, finishes them, verifies database consistency, and deletes selected dumps across repeated passes.

Important APIs: `connect_buserver` initializes RX, calls `udbClientInit`, and checks `BUDB_T_GetVersion`. `verifyDb` wraps `BUDB_DbVerify`. `deleteDump` calls `bcdb_deleteDump`. `main` constructs `budb_dumpEntry`, `budb_tapeEntry`, and `budb_volumeEntry` records and exercises `bcdb_CreateDump`, `bcdb_UseTape`, `bcdb_AddVolume`, `bcdb_FinishTape`, and `bcdb_FinishDump`.

Control flow and state: `NPASS` loops create `NDUMPS` dumps, each with `NTAPES` tapes and `NVOLUMES` volumes, varying volume names and sizes. Dump 1 can reference dump 0 as its initial dump. After each pass it deletes one non-appended dump and verifies the DB. Persistence is entirely in the live BUDB service.

Dependencies and integration: depends on RX, UBik BUDB client globals, and backup database client wrappers. It is not hermetic and requires a running backup database service for the selected cell.

Risks and tests: the test mutates real BUDB state and uses old-style C declarations. One bug checks `code` after `bcdb_UseTape` without assigning its return value, so a tape-use failure may be missed. It is valuable as an integration signal for BUDB metadata paths, but risky to run outside a disposable test cell.
