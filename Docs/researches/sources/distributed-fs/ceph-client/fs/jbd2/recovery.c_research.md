# sources/distributed-fs/ceph-client/fs/jbd2/recovery.c

## Purpose
`recovery.c` replays an unclean JBD2 journal at mount time or intentionally skips that recovery when told to wipe/ignore old log contents. Its central contract is to discover the valid transaction range, collect revoke records, replay unrevoked metadata/data blocks to the filesystem device, restart transaction sequencing after the last valid transaction, and force replayed writes to stable storage.

## Important APIs, types, and functions
The public entry points are `jbd2_journal_recover()` and `jbd2_journal_skip_recovery()`. Internal state is carried by `struct recovery_info`, which tracks `start_transaction`, `end_transaction`, `head_block`, replay count, revoke count, and revoke-hit count. The pass engine is `do_one_pass()`, using `PASS_SCAN`, `PASS_REVOKE`, and `PASS_REPLAY`. Supporting functions include `jread()`, `do_readahead()`, `count_tags()`, `read_tag_block()`, `calc_chksums()`, `jbd2_do_replay()`, `scan_revoke_records()`, descriptor/commit/tag checksum verifiers, and `fc_do_one_pass()` for fast-commit callback replay.

## Control flow
`jbd2_journal_recover()` first checks whether `journal->j_tail` is zero. A zero tail means the on-disk journal is clean, so it initializes `j_transaction_sequence` from `s_sequence + 1`, restores `j_head` from `s_head`, and exits without replay. Otherwise it performs three ordered passes. `PASS_SCAN` walks transactions from `s_start` and `s_sequence`, finding the first invalid or missing commit boundary and recording the valid end transaction and next head block. `PASS_REVOKE` re-walks the valid range, optionally enlarges the replay revoke hash table if many revokes were counted, and records revoke block numbers with their transaction sequence. `PASS_REPLAY` walks the same range and writes descriptor-described blocks back to `j_fs_dev` unless `jbd2_journal_test_revoke()` says the block was revoked by the same or a later transaction.

`do_one_pass()` reads each journal block via `jread()`, checks magic, block type, and sequence, then handles descriptor, commit, and revoke blocks. Descriptor blocks are checksum-verified for v2/v3; scan mode may tolerate stale checksum failures from lazy journal initialization and later decide using commit timestamps. Replay mode calls `jbd2_do_replay()`, which reads each logged data block, validates per-tag checksums when enabled, reconstructs escaped magic values, marks destination buffers uptodate and dirty, and counts replayed blocks. Commit blocks advance the expected transaction sequence if checksum rules pass. Revoke blocks are counted in scan mode and inserted in revoke mode. Fast-commit replay runs after scan and replay passes, not during revoke, through the filesystem callback stored in `journal->j_fc_replay_callback`.

After replay, `jbd2_journal_recover()` advances `j_transaction_sequence` to one past the recovered range, sets `j_head`, clears replay revoke records, restores the normal revoke table if a larger temporary table was used, syncs the filesystem block device, checks writeback errors, and issues a flush when barriers are enabled.

## State and persistence behavior
Recovery treats `s_start`/`j_tail` as the dirty-clean indicator and `s_sequence` as the first transaction to scan. It does not mark the journal empty here; that is done later by `journal_reset()` in `journal.c`. Replay writes destination buffers through the filesystem block device, marks them dirty, and relies on `sync_blockdev()`, write-error checks, and optional `blkdev_issue_flush()` to ensure data reaches permanent storage before the journal is reset for new transactions.

Checksum behavior is layered. Old checksum-v1 mode accumulates CRCs over descriptor and data blocks and compares against commit headers. V2/v3 mode verifies descriptor-block tails, commit-block checksums, and per-tag data block checksums seeded from the journal UUID. Partial commit-block checksum verification allows detection of incomplete commit blocks. Commit timestamps help distinguish interrupted commits from stale journal blocks after checksum failures.

Revoke persistence is interpreted by sequence number: a revoke record at sequence N suppresses replay of records from transactions <= N, but later transactions still replay. The replay revoke table is temporary; it is cleared before normal mounted operation resumes.

## Dependencies and integration points
This file depends on `journal.c` for log block mapping via `jbd2_journal_bmap()`, tag size via `journal_tag_bytes()`, journal state fields, barriers, and block-device synchronization. It depends on `revoke.c` for `jbd2_journal_set_revoke()`, `jbd2_journal_test_revoke()`, `jbd2_journal_clear_revoke()`, and temporary revoke table allocation. It integrates with filesystem-specific fast-commit replay through `j_fc_replay_callback`. It uses buffer-head block I/O directly and implements its own 128 KiB readahead because recovery bypasses the normal page-cache readahead path.

## Risks and edge cases
Recovery correctness depends on stopping at exactly the last complete transaction. False acceptance can replay stale/corrupt metadata; false rejection can lose committed metadata. The code has special handling for async commits, checksum mismatches, incomplete commit blocks, stale blocks from lazy journal initialization, wraparound at `j_last`, and journals with 64-bit block tags. Memory pressure can fail revoke-table enlargement or destination buffer allocation; only `-ENOMEM` aborts replay immediately in `jbd2_do_replay()`. Bad journal mappings or unreadable log blocks surface as `-EIO`/corruption errors.

Revoke table sizing is deliberately capped to avoid malicious filesystem memory blowups. Fast-commit replay is callback-driven, so a filesystem callback error can fail recovery even if the normal log scan succeeds.

## Test signals
Strong tests include unclean shutdown replay of multiple transactions, revoked block replay suppression, revoke-then-later-write replay, corrupted descriptor/commit/tag checksums, stale journal blocks after lazy initialization, async commit checksum mismatch handling, 32-bit and 64-bit tag formats, log wraparound, injected journal read failures, allocation failures in replay, fast-commit replay success/failure/stop callback paths, and post-replay flush/write-error injection on `j_fs_dev`.
