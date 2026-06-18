# sources/distributed-fs/ceph-client/fs/jbd2/revoke.c

## Purpose
`revoke.c` implements JBD2 revoke records. Revokes prevent old log entries for freed metadata blocks from being replayed after those physical blocks have been reused for newer data. The file serves both normal commit-time operation, where the current transaction records blocks that must not be replayed, and recovery-time operation, where revoke records are collected and consulted before applying logged blocks.

## Important APIs, types, and functions
The main APIs are `jbd2_journal_revoke()`, `jbd2_journal_cancel_revoke()`, `jbd2_clear_buffer_revoked_flags()`, `jbd2_journal_switch_revoke_table()`, `jbd2_journal_write_revoke_records()`, `jbd2_journal_set_revoke()`, `jbd2_journal_test_revoke()`, and `jbd2_journal_clear_revoke()`. Initialization/destruction APIs manage slab caches and per-journal tables: `jbd2_journal_init_revoke_record_cache()`, `jbd2_journal_init_revoke_table_cache()`, `jbd2_journal_init_revoke_table()`, `jbd2_journal_init_revoke()`, and matching destroy helpers.

The key structures are `struct jbd2_revoke_record_s`, which stores a revoked `blocknr` and recovery `sequence`, and `struct jbd2_revoke_table_s`, a power-of-two hash table of record lists. Runtime uses two tables in `journal->j_revoke_table[]`: one for the running transaction and one for the committing transaction.

## Control flow
During normal operation, a filesystem calls `jbd2_journal_revoke()` under a transaction handle before freeing metadata. The function enables the journal revoke incompat feature, finds or uses the supplied buffer, checks revoke credits, sets buffer `Revoked`/`RevokeValid` bits when a buffer exists, calls `jbd2_journal_forget()` for supplied buffers, decrements revoke credits, and inserts a revoke record into the running transaction hash table.

When the same transaction later journals the block as metadata, `jbd2_journal_cancel_revoke()` is called from write-access paths. It uses cached buffer revoke bits when valid; otherwise it searches the hash table. If a record exists, it removes and frees it. For unhashed aliases, it also clears revoke state on the hashed alias to keep buffer state consistent.

At commit time, `jbd2_journal_switch_revoke_table()` switches `journal->j_revoke` so new revokes go into the next running table while the previous table belongs to the committing transaction. `jbd2_journal_write_revoke_records()` drains the committing table. It builds revoke descriptor blocks with `jbd2_journal_get_descriptor_buffer()`, writes 32-bit or 64-bit block numbers depending on journal features, finalizes `r_count`, sets descriptor checksums, marks buffers for journal write, and frees records as it goes. If the journal is aborted, descriptor I/O becomes a no-op but records are still drained.

During recovery, `scan_revoke_records()` in `recovery.c` calls `jbd2_journal_set_revoke()` to record the newest revoke sequence for each block. `jbd2_journal_test_revoke()` suppresses replay when the replayed transaction sequence is less than or equal to the recorded revoke sequence. `jbd2_journal_clear_revoke()` empties the table once recovery completes.

## State and persistence behavior
Commit-time revoke state is both in memory and persisted as journal revoke descriptor blocks. In-memory buffer bits provide a cache for the current transaction: invalid, valid-not-revoked, or valid-revoked. The durable revoke descriptor stores only block numbers plus descriptor metadata; transaction sequence comes from the descriptor header. At recovery, only the latest sequence for a block matters.

Two-table switching prevents the commit thread from blocking normal updates while it writes revoke records. The committing table is single-threaded under `kjournald2`, while the running table is protected by `j_revoke_lock` for list operations. Normal transaction handles pin the running table against switching.

## Dependencies and integration points
This file integrates with `transaction.c` through `jbd2_journal_forget()` and `jbd2_journal_cancel_revoke()` calls from buffer write-access paths. It integrates with `journal.c` through descriptor buffer allocation, descriptor checksums, feature enabling, journal abort checks, and revoke table initialization/destruction. It is consumed by `recovery.c` for replay suppression. It depends on buffer-head lookup, buffer state bits, block-device identity via `journal->j_fs_dev`, slab caches, `kvmalloc` hash tables, and list/spinlock primitives.

## Risks and edge cases
Double revoke without an intervening allocation is treated as inconsistent and can return `-EIO`. Running out of revoke credits is a serious error path. Losing a cancel can suppress a legitimate later metadata write during recovery; cancel logic therefore handles invalid buffer cache state and aliases carefully. Failing to preserve revoke records after a block is written as file data could let old metadata overwrite data after crash; the comments explicitly distinguish metadata journaling from data writes. Hash table chains can grow during recovery, so `recovery.c` may allocate a larger temporary table with a cap.

## Test signals
Test revoke before block free, revoke cancellation by later metadata write in the same transaction, metadata-write-then-revoke precedence, revoked block reused as data, double-free/double-revoke detection, 32-bit and 64-bit revoke descriptor formats, checksum-protected revoke descriptors, aborted-journal record draining, hash-table switching under concurrent transactions, recovery with multiple revoke records for the same block, and buffer alias revoke-bit clearing.
