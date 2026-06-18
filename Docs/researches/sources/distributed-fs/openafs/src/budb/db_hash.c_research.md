<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_hash.c -->
# sources/distributed-fs/openafs/src/budb/db_hash.c

## Purpose
Implements the persistent hash tables used to locate dumps by id/name, tapes by name, and volume info by name. It also performs incremental hash-table growth and provides generic chain scanning.

## Important APIs, Types, And Functions
Initialization is via `InitDBhash` and `ht_DBInit`. Core operations are `ht_HashEntry`, `ht_GetType`, `ht_LookupEntry`, `ht_HashIn`, `ht_HashOut`, `RemoveFromList`, `scanHashTable`, and `ht_LookupBucket`. Internal helpers allocate/free table blocks, cache table blocks in memory, move entries from old to new tables, and compute string/id hashes.

## Control Flow
Insertions call `ht_MaybeAdjust`; if a table is too dense and small enough to grow, the current table is moved to `oldTable` and a new table is allocated. Each operation moves up to a small quota of buckets from the old table into the current table through `ht_MoveEntries`, so resizing is incremental. Lookups search current then old tables. Deletions remove from old first when present, then current.

## State And Persistence
Persistent hash descriptors live in `db.h` and point to chains of `hashTable_BLOCK` blocks. Record linkage uses embedded chain fields whose offsets are stored in the descriptor. Memory caches in `memoryHashTable` are invalidated on header refresh.

## Dependencies And Integration Points
All high-level RPCs in `procs.c` rely on these indexes. The verifier and dump code traverse the same tables.

## Risks And Test Signals
Risks include bucket-cache invalidation mistakes, incorrect old-table progress, hash entry count drift, and chain corruption from bad offsets. Signals are insert/delete/lookup stress, forced hash growth, verifier hash-table checks, and cross-checks between name/id indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_hash.c -->
