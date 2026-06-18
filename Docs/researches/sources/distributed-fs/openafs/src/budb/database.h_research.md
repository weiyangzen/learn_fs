<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/database.h -->
# sources/distributed-fs/openafs/src/budb/database.h

## Purpose
Defines the on-disk and in-memory schema for the OpenAFS backup database. This is the core contract for database layout, block allocation, hash tables, text storage, locks, and persistent dump/tape/volume records.

## Important APIs, Types, And Functions
Key types include `dbadr`, `hashTable`, `textBlock`, `db_lockS`, `dbHeader`, fixed-size `block`/`blockHeader`, `htBlock`, `volFragment`, `volInfo`, `tape`, `dump`, `memoryHTBlock`, `memoryHashTable`, and `memoryDB`. Constants define `BUDB_VERSION`, `BLOCKSIZE`, block types, hash function IDs, entry counts, and address helpers such as `BlockBase`. Macros `set_header_word`, `set_word_offset`, and `set_word_addr` update memory and persist a single word through `dbwrite`.

## Control Flow
The header encodes how higher layers work: allocate fixed-size blocks, store homogeneous records per block, index records through hash buckets, and link records through embedded `dbadr` chain fields.

## State And Persistence
The persistent root is `dbHeader` at database offset zero. It stores free lists, EOF, hash-table descriptors, text locks, text block descriptors, last IDs, update time, and check version. All multi-byte fields stored in the database are generally network ordered.

## Dependencies And Integration Points
It depends on OpenAFS backup constants, auth principal types, and Ubik transaction helpers declared elsewhere. Every budb storage module includes it.

## Risks And Test Signals
This is a high-risk layout header: changing structure sizes, padding, counts, byte order, or block constants can break existing databases. Signals include build-time size assumptions, database create/upgrade tests, online verification, dump/restore across architectures, and hash allocation traversal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/database.h -->
