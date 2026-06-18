<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_alloc.c -->
# sources/distributed-fs/openafs/src/budb/db_alloc.c

## Purpose
Implements fixed-size block and record allocation for the budb on-disk database. It manages generic free blocks and per-record-type free lists for volume fragments, volume info, tapes, and dumps.

## Important APIs, Types, And Functions
`InitDBalloc` fills `nEntries` and `sizeEntries` from schema constants. `AllocBlock` extends the database at `eofPtr` or removes a block from the generic free list. `FreeBlock` clears a block header and chains the block onto `freePtrs[free_BLOCK]`. `AllocStructure` finds or creates a block for a specific structure type, uses the first word of each record as the allocated/free marker, decrements `nFree`, and returns the record address. `FreeStructure` validates block type, marks the first word zero, increments `nFree`, and adds the block to its type free list if it was previously full.

## Control Flow
Structure allocation first reclaims fully empty typed blocks back to the generic list when possible, then scans the block for the first zero first-word slot. The caller must later write the full structure contents.

## State And Persistence
Persistent state is `db.h.freePtrs[]`, block headers, `eofPtr`, and first-word allocation markers inside records. All updates are written through `set_header_word`, `set_word_offset`, and `dbwrite` in a Ubik transaction.

## Dependencies And Integration Points
Used by `procs.c`, `db_hash.c`, and `db_text.c` to create/free dumps, tapes, volume records, hash blocks, and text blocks.

## Risks And Test Signals
Risks include free-count corruption, mismatched block type, and relying on the first record word as free marker. Signals are allocator stress tests, delete/recreate cycles, verifier free-list checks, and crash-recovery tests around partial transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_alloc.c -->
