<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/ol_verify.c -->
# sources/distributed-fs/openafs/src/budb/ol_verify.c

## Purpose
Performs online consistency verification of the budb database. It walks blocks, hash tables, free lists, text chains, and record relationships to detect corruption while the server is running.

## Important APIs, Types, And Functions
`DbVerify` is the RPC entry, wrapping `verifyDatabase`. `checkDiskAddress` and `ConvertDiskAddress` validate disk addresses and map them to block/entry indexes. Specific validators include `verifyDumpEntry`, `verifyTapeEntry`, `verifyVolFragEntry`, `verifyVolInfoEntry`, `verifyBlocks`, `verifyHashTable`, `verifyEntryChains`, `verifyFreeLists`, `verifyMapBits`, `verifyText`, and `verifyTextChain`. `blockMap` records per-block/per-entry flags such as hash membership, free state, tape/dump linkage, text usage, and appended-dump linkage.

## Control Flow
`verifyDatabase` computes block count from `eofPtr`, allocates a block map, reads all block headers, verifies each current and old hash table, validates record chains, checks text chains, checks free lists, and finally ensures each entry has a compatible combination of map bits.

## State And Persistence
It does not repair data. It builds transient verification state in `miscData` and `blockMap`, reads persistent Ubik blocks, and reports status/error counts. `DbVerify` returns host address and status to the caller.

## Dependencies And Integration Points
Used by admin verification RPCs and by `cdbread` address validation. It depends on `database.h` schema, hash helpers, Ubik read transactions, audit, and logging.

## Risks And Test Signals
Risks include verifier assumptions matching schema exactly, a noted `checkEntry` table comment saying it may not match `typeName[]`, and limited tolerance after 50 errors in normal builds. Signals are clean verification after create/add/delete, deliberate corruption fixtures for bad links/free counts/hash buckets, text chain checks, and old-hash-table migration cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/ol_verify.c -->
