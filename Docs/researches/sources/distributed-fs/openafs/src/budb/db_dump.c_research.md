<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_dump.c -->
# sources/distributed-fs/openafs/src/budb/db_dump.c

## Purpose
Serializes the budb database into a portable stream for dump/restore clients. It writes network-order headers and records for database metadata, dumps, tapes, volume entries, and text blocks while coordinating a producer thread with an RPC reader through a pipe.

## Important APIs, Types, And Functions
`canWrite`, `haveWritten`, and `doneWriting` synchronize writer/reader state in `dumpSyncPtr`. `writeStructHeader`, `writeTextHeader`, `writeDbHeader`, `writeDump`, `writeTape`, `writeVolume`, `writeText`, and `writeDatabase` generate the dump stream. `checkLock` and `checkText` guard text export.

## Control Flow
`writeDatabase` writes a database header, walks both current and old dump-id hash tables, skips appended dumps as roots, then follows each initial dump's appended chain in restore order. For each dump it writes tapes and volume fragments by following `firstTape` and `firstVol` chains, reading corresponding `volInfo` records. It then writes dump schedule, volume set, and tape host text blocks, followed by an `SD_END` marker.

## State And Persistence
The stream reflects persistent Ubik records but is not itself stored by this file. It preserves IDs, dump/tape/volume metadata, text contents, and header high-water marks. `MAXAPPENDS` and loop-count guards prevent unbounded appended-dump traversal.

## Dependencies And Integration Points
Called by `dbs_dump.c` dump worker. It depends on hash lookup, checked database reads, struct conversion helpers, text locks, `globals.h` dump synchronization, and Ubik read transactions.

## Risks And Test Signals
Risks include stale or held text locks blocking export, partial output on inconsistent chains, circular appended-dump chains, and pipe synchronization deadlocks. Signals are savedb/restoredb round trips, database dumps with appended dumps, text-block export, timeout handling, and online verifier agreement before dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_dump.c -->
