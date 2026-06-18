# subset-b-005676 research

Grouped research for the subset-b-005676 source files. Each section preserves the source path in its title and is wrapped with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/journal.c -->
# sources/distributed-fs/ceph-client/fs/jbd2/journal.c

## Purpose
`journal.c` is the central JBD2 journal lifecycle and log-space manager. It owns journal initialization over an external block device or journal inode, superblock validation and updates, the `kjournald2` commit thread, log head/tail accounting, descriptor-buffer allocation, fast-commit buffer allocation, journal flushing/wiping, abort/error persistence, `journal_head` lifetime, module-level caches, proc statistics, and shrinker integration. Physical placement policy is intentionally delegated through `journal->j_bmap` or inode `bmap()`, while this file manages the in-memory `journal_t` state and the persistent journal superblock.

## Important APIs, types, and functions
The exported API includes `jbd2_journal_init_dev()`, `jbd2_journal_init_inode()`, `jbd2_journal_load()`, `jbd2_journal_destroy()`, `jbd2_journal_flush()`, `jbd2_journal_wipe()`, `jbd2_journal_abort()`, `jbd2_journal_errno()`, `jbd2_journal_ack_err()`, `jbd2_journal_clear_err()`, `jbd2_journal_start_commit()`, `jbd2_log_wait_commit()`, `jbd2_journal_force_commit()`, `jbd2_complete_transaction()`, fast-commit helpers, and `journal_head` helpers. Core persistent data is `journal_superblock_t`, with `s_start`, `s_sequence`, `s_head`, feature flags, checksum fields, and error state. Core volatile state lives in `journal_t`: sequence counters, log head/tail/free counts, transaction pointers, wait queues, locks, revoke tables, commit thread pointer, write buffers, fast-commit area fields, shrinker state, and proc stats.

Key internal functions are `journal_load_superblock()`, `journal_check_superblock()`, `journal_reset()`, `jbd2_write_superblock()`, `jbd2_journal_update_sb_log_tail()`, `jbd2_mark_journal_empty()`, `__jbd2_journal_erase()`, `jbd2_journal_write_metadata_buffer()`, `jbd2_journal_get_descriptor_buffer()`, and `jbd2_descriptor_block_csum_set()`. Cache and lifetime helpers include `jbd2_alloc()`, `jbd2_free()`, `jbd2_journal_add_journal_head()`, `jbd2_journal_grab_journal_head()`, and `jbd2_journal_put_journal_head()`.

## Control flow
Initialization enters through `jbd2_journal_init_dev()` or `jbd2_journal_init_inode()`, both of which call `journal_init_common()`. That common path allocates `journal_t`, loads and checks the on-disk superblock, initializes waits/locks/counters/revoke tables/write buffers/shrinker state, and leaves the journal in `JBD2_ABORT` until recovery succeeds. `jbd2_journal_load()` creates the block-size slab, calls `jbd2_journal_recover()`, verifies no failed commit was recorded, clears the initial abort flag, calls `journal_reset()`, and starts `kjournald2`.

`kjournald2()` sleeps on commit requests or transaction expiry. When `j_commit_request` differs from `j_commit_sequence`, it deletes the commit timer and calls `jbd2_journal_commit_transaction()`. Otherwise it handles freezer transitions and wakes when a running transaction expires. The commit thread is shut down through `journal_kill_thread()` by setting `JBD2_UNMOUNT` and waiting for `j_task` to clear.

Commit scheduling flows through `__jbd2_log_start_commit()`, `jbd2_log_start_commit()`, `jbd2_journal_start_commit()`, `jbd2_complete_transaction()`, and `jbd2_log_wait_commit()`. These coordinate `j_commit_request`, `j_commit_sequence`, `j_running_transaction`, `j_committing_transaction`, and wait queues. Force-commit paths refuse to force the running transaction if the caller already has an active handle, avoiding self-deadlock.

Log allocation uses `jbd2_journal_next_log_block()` to consume `j_head` and `j_free`, wrapping at `j_last`. Descriptor buffers are acquired with `jbd2_journal_get_descriptor_buffer()`, initialized with a JBD2 header, and charged to transaction credits. `jbd2_journal_write_metadata_buffer()` creates an alias buffer for journal I/O, uses frozen data when the buffer has been modified by a later transaction, applies magic-number escaping, fires frozen triggers, files the original buffer on `BJ_Shadow`, and marks the original buffer shadowed until writeout completes.

Shutdown through `jbd2_journal_destroy()` kills the thread, commits a final running transaction, checkpoints all checkpoint transactions, checks filesystem-device writeback errors, marks the journal empty if not aborted, releases proc/shrinker/revoke/write-buffer resources, and frees the journal object.

## State and persistence behavior
The journal superblock is the durable cursor. `jbd2_journal_update_sb_log_tail()` writes `s_sequence` and `s_start` with caller-selected flags and clears `JBD2_FLUSHED` after success. `jbd2_mark_journal_empty()` writes `s_start = 0`, records `s_head`, and sets `JBD2_FLUSHED`. Tail advancement in `__jbd2_update_log_tail()` uses `REQ_FUA` because freed log space can be reused immediately after the update; losing that superblock update could replay stale overwritten log contents after power loss. `jbd2_write_superblock()` respects `JBD2_BARRIER` by dropping `REQ_FUA`/`REQ_PREFLUSH` when barriers are disabled, updates v2/v3 checksums, retries after prior superblock write errors, and aborts on new write failure.

Feature flags are validated and mutated in `journal_check_superblock()`, `jbd2_journal_check_used_features()`, `jbd2_journal_check_available_features()`, `jbd2_journal_set_features()`, and `jbd2_journal_clear_features()`. Fast commit reserves a tail portion of the journal by reducing `j_last`, setting `j_fc_first`, `j_fc_last`, `j_fc_wbufsize`, and initializing `j_fc_wbuf`. During reset, fast commit is cleared in memory so the client filesystem must explicitly re-enable it if still supported.

Abort state is both in-memory and persistent. `jbd2_journal_abort()` serializes with `j_abort_mutex`, sets `JBD2_ABORT`, records `j_errno`, starts the running transaction so buffers are released, and writes the error to the journal superblock. `-ESHUTDOWN` takes precedence over prior errors. `jbd2_journal_errno()` returns `-EROFS` for currently aborted journals, while ack/clear helpers control whether old errors block future handles.

`journal_head` lifetime persists as references against `buffer_head` objects while JBD2 owns transaction or checkpoint state. The code uses `BH_JBD`, elevated `b_count`, RCU-safe slab allocation, and `b_jcount`; `jbd2_journal_put_journal_head()` detaches only after no transaction, next transaction, checkpoint, or list state remains. Frozen and committed copies are freed defensively with warnings if still present.

## Dependencies and integration points
This file integrates with `transaction.c` for exported transaction/handle and buffer APIs, with commit/checkpoint code via `jbd2_journal_commit_transaction()`, `jbd2_log_do_checkpoint()`, `jbd2_cleanup_journal_tail()`, and checkpoint shrinkers, with `recovery.c` through `jbd2_journal_recover()` and `jbd2_journal_skip_recovery()`, and with `revoke.c` through revoke table cache initialization and journal revoke table setup. It depends heavily on block-layer `buffer_head` I/O, `blkdev_issue_flush()`, discard/zeroout operations, page/folio helpers, wait queues, kthreads, freezer support, procfs, slab caches, percpu counters, and tracepoints.

Filesystem clients such as ext4 provide the journal block mapping policy and call the exported init/load/start/stop/flush/feature APIs. Fast commit is delegated through callbacks such as `j_fc_cleanup_callback`; replay-side callbacks live in recovery.

## Risks and edge cases
The highest-risk areas are ordering of superblock updates versus log reuse, abort/error handling during writeback failure, interaction between fast-commit feature state and the partitioned log area, and `journal_head` lifetime under concurrent buffer release. Metadata escaping and frozen-data copying must be correct or recovery can misinterpret user metadata as descriptor headers. `jbd2_journal_bmap()` aborts on missing inode-backed journal blocks; a bad mapping can convert to a journal abort and read-only behavior. Feature changes must preserve checksum compatibility; the code intentionally upgrades checksum v2 requests to v3 and avoids incompatible v1/v3 combinations.

Locking risks concentrate around `j_state_lock`, `j_list_lock`, `j_checkpoint_mutex`, `j_barrier`, `j_abort_mutex`, and buffer journal-head locks. Force-commit paths protect against deadlock by rejecting active-handle self-waits. Destroy and flush paths must not mark the journal empty while transactions or checkpoint records remain.

## Test signals
Useful tests include clean mount/unmount verifying `s_start` becomes zero, crash/recovery tests verifying tail/head/sequence replay, fault injection for superblock write errors and filesystem-device writeback errors, external journal and inode-backed journal mapping failures, barrier-on/off persistence checks, fast-commit enable/disable and fallback paths, descriptor checksum corruption, magic-number escaping recovery, journal flush with discard/zeroout, proc stats visibility, shrinker pressure over checkpointed `journal_head` objects, and module unload leak checks under `CONFIG_JBD2_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/journal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/recovery.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/recovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/revoke.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/revoke.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/transaction.c -->
# sources/distributed-fs/ceph-client/fs/jbd2/transaction.c

## Purpose
`transaction.c` manages JBD2 transaction and handle semantics. Filesystem operations acquire handles, reserve credits, attach metadata buffers to transactions, dirty metadata, forget deleted buffers, restart long operations across transactions, quiesce updates, free buffers during truncation/reclaim, and file ordered-data inode ranges. This file enforces the state-machine and locking rules that make journal commit atomic with respect to metadata buffer mutation.

## Important APIs, types, and functions
Important exported APIs include `jbd2__journal_start()`, `jbd2_journal_start()`, `jbd2_journal_start_reserved()`, `jbd2_journal_free_reserved()`, `jbd2_journal_extend()`, `jbd2__journal_restart()`, `jbd2_journal_restart()`, `jbd2_journal_lock_updates()`, `jbd2_journal_unlock_updates()`, `jbd2_journal_get_write_access()`, `jbd2_journal_get_create_access()`, `jbd2_journal_get_undo_access()`, `jbd2_journal_set_triggers()`, `jbd2_journal_dirty_metadata()`, `jbd2_journal_forget()`, `jbd2_journal_stop()`, `jbd2_journal_try_to_free_buffers()`, `jbd2_journal_invalidate_folio()`, `jbd2_journal_refile_buffer()`, `jbd2_journal_inode_ranged_write()`, `jbd2_journal_inode_ranged_wait()`, and `jbd2_journal_begin_ordered_truncate()`.

Key internal helpers are `jbd2_get_transaction()`, `add_transaction_credits()`, `start_this_handle()`, `stop_this_handle()`, `do_get_write_access()`, `jbd2_write_access_granted()`, `jbd2_freeze_jh_data()`, `__jbd2_journal_file_buffer()`, `__jbd2_journal_temp_unlink_buffer()`, `__jbd2_journal_refile_buffer()`, and `journal_unmap_buffer()`. Core data is `transaction_t`, `handle_t`, `journal_head`, transaction buffer lists (`BJ_Metadata`, `BJ_Reserved`, `BJ_Forget`, `BJ_Shadow`), and `struct jbd2_inode` ordered-data state.

## Control flow
Handle start begins in `jbd2__journal_start()`. Nested calls reuse the current handle if it belongs to the same journal. Otherwise the function creates a handle, optionally creates a reserved handle, accounts revoke descriptor credits, and calls `start_this_handle()`. `start_this_handle()` validates credit limits, optionally preallocates a new transaction, checks abort/error state, waits for update barriers unless reserved, creates a running transaction when needed, waits when the current transaction is locked or too large, ensures sufficient log/checkpoint space, accounts reserved credits, increments `t_updates` and `t_handle_count`, stores the handle in `current->journal_info`, and enters a NOFS allocation context.

Credit extension is best-effort through `jbd2_journal_extend()`. If extension fails, callers can use `jbd2__journal_restart()`, which detaches the handle, starts commit of the old transaction if needed, resets credits, and attaches to a new transaction. `jbd2_journal_stop()` decrements nested references, optionally batches synchronous handles based on observed commit time, starts a commit for sync or expired transactions, drops outstanding credits through `stop_this_handle()`, optionally waits for commit, frees reserved handles, and returns `-EIO` if abort occurred.

Write access flows through `jbd2_journal_get_write_access()` and `do_get_write_access()`. If a lockless fast path confirms the buffer already belongs to the handle transaction, no heavy work is needed. Otherwise a `journal_head` is attached, dirty external state is sanitized, the buffer is filed as reserved if unowned, or copy-out is performed when the buffer belongs to the committing transaction. Copy-out uses `b_frozen_data` to preserve the committing image if the new running transaction must modify the primary buffer. `jbd2_journal_get_create_access()` handles newly allocated locked buffers and allows the special case where a committing transaction holds the block on `BJ_Forget`. `jbd2_journal_get_undo_access()` additionally preserves `b_committed_data` for non-rewindable operations such as bitmap changes.

After modification, `jbd2_journal_dirty_metadata()` marks the buffer modified, consumes a credit once per transaction, sets `buffer_jbddirty`, and files it on `BJ_Metadata` unless it still belongs to the committing transaction and will be refiled later. `jbd2_journal_forget()` removes or pins buffers being deleted, using `BJ_Forget`, checkpoint removal, `buffer_freed`, and `b_next_transaction` depending on whether the buffer belongs to the running transaction, committing transaction, checkpoint list, or no transaction.

Buffer list management is centralized in `__jbd2_journal_file_buffer()`, temporary unlink, unfile, and refile helpers. Refile moves a buffer from a committing transaction to `b_next_transaction` after commit, choosing `BJ_Forget`, `BJ_Metadata`, or `BJ_Reserved` based on freed/modified state.

## State and persistence behavior
Transaction state starts as `T_RUNNING` with a TID, expiry, outstanding credits, revoke counts, update counters, and inode list. Handles pin transactions by incrementing `t_updates`. Credit accounting reserves enough space for metadata descriptors and revoke descriptors before metadata is dirtied, because commit cannot safely force checkpointing for buffers that it is also committing. `j_reserved_credits` prevents reserved handles from overcommitting future transactions.

Persistence is implemented by preserving correct buffer images until commit. `b_frozen_data` preserves the old committing image when the live buffer is modified by a later transaction. `b_committed_data` preserves undo-protected bitmap state until it is safe to reuse freed blocks. `buffer_jbddirty` separates JBD2-owned metadata dirtiness from ordinary VM dirty state. `BJ_Forget` records deletion semantics so checkpoints are not removed before the deleting transaction commits. Ordered-data inode filing records dirty byte ranges and sets `t_need_data_flush` so commit can flush file data before metadata commit.

Truncation and reclaim paths maintain persistence invariants. `jbd2_journal_invalidate_folio()` and `journal_unmap_buffer()` decide whether buffers can be dropped, must wait for a committing transaction, must be pinned on a forget list, or can have checkpoint state removed. `jbd2_journal_begin_ordered_truncate()` starts writeout of truncated ranges if their inode data is in the committing transaction.

## Dependencies and integration points
This file is the main client-facing transaction layer for filesystems such as ext4. It depends on `journal.c` for commit scheduling, abort state, log space, `journal_head` allocation, and buffer-copy allocators; on `revoke.c` for canceling revokes before journaling a block; on checkpoint code for removing checkpointed buffers; and on commit code for transaction state transitions and buffer list processing. It uses buffer-head, folio, page-cache, writeback, hrtimer, wait queue, rwlock/spinlock, tracepoint, and NOFS allocation APIs.

## Risks and edge cases
This file is race-sensitive. Important risks include credit under-accounting, modifying a buffer while commit is writing the old image, dirty metadata outside JBD2 control, use-after-free of transactions while waiting, deadlocks between commit and checkpointing, barrier deadlocks with reserved handles, buffer aliasing during truncate, and wrong `b_next_transaction` refiling. The code has many `WARN_ON_ONCE()` and abort paths for impossible state, including buffers on the wrong transaction, illegal create-access reuse, unexpected frozen data, and bad list states.

Reserved handles are intentionally allowed to join locked transactions to avoid writeback deadlocks, but not `T_SWITCH` transactions. `jbd2_journal_lock_updates()` must wait for reserved credits and open updates before establishing a barrier. Sync batching improves throughput but changes timing and must still force commit for synchronous handles. Aborted handles return `-EROFS` or `-EIO` depending on phase.

## Test signals
Test handle nesting, credit exhaustion, reserved-handle start/free/start-reserved paths, transaction-too-large waits, checkpoint-space waits, lock-update barriers, sync handle batching, restart after failed extend, write access to buffers in running and committing transactions, frozen-data copy-out, undo access and committed-data preservation, dirty metadata credit consumption, forget of running/committing/checkpointed buffers, refile after commit, invalidate/truncate of full and partial folios, ordered truncate writeout, abort during active handles, and fault injection for allocation and writeback errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/transaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/Kconfig -->
# sources/distributed-fs/ceph-client/fs/jffs2/Kconfig

## Purpose
This Kconfig file defines the build-time feature surface for JFFS2. It exposes the base `JFFS2_FS` filesystem option, debug verbosity, write-buffer support, summary nodes, extended attributes, POSIX ACLs, security labels, selectable compression backends, and default compression mode.

## Important options
`JFFS2_FS` is a tristate that depends on `MTD` and selects `CRC32`; it states that JFFS2 is for MTD flash devices rather than normal block devices. `JFFS2_FS_DEBUG` is an integer verbosity level. `JFFS2_FS_WRITEBUFFER` defaults to yes and supports NAND, NOR with transparent ECC, and DataFlash. `JFFS2_FS_WBUF_VERIFY` optionally reads back write-buffer writes. `JFFS2_SUMMARY` enables summary information for faster mounts.

`JFFS2_FS_XATTR` gates extended attributes. `JFFS2_FS_POSIX_ACL` depends on xattrs, defaults to yes when xattrs are enabled, and selects `FS_POSIX_ACL`. `JFFS2_FS_SECURITY` also depends on xattrs and defaults to yes for security labels. Compression options are hidden behind `JFFS2_COMPRESSION_OPTIONS`, with zlib and rtime defaulting to yes, LZO and Rubin defaulting to no, and a choice among none, priority, size, and favour-LZO compression modes.

## Control flow and integration
Kconfig selections are consumed by the JFFS2 Makefile and preprocessor conditionals. For example, enabling POSIX ACLs compiles `acl.o` and turns the `acl.h` declarations into real operations; disabling them makes the header macros return no ACL support. Enabling xattrs pulls in xattr handlers, while security labels and ACLs layer on top of xattrs. Compression selections control which compressor object files are linked and which runtime default mode is built in.

## State and persistence behavior
This file does not persist runtime state, but its options affect on-flash compatibility. Compression backend choices can determine whether an image written by one kernel can be read by another. Summary support affects whether images can include mount-acceleration summary records. Xattrs, ACLs, and security labels persist extra metadata as JFFS2 xattr nodes.

## Dependencies and risks
The primary dependency is `MTD`. ACL and security options depend on xattr support. Zlib and LZO select their kernel compression libraries. The help text warns that removing compressors can make existing filesystems unreadable and enabling experimental compressors can reduce compatibility with standard kernels or bootloaders. `JFFS2_FS_DEBUG` level 1 is useful for bug reports but higher verbosity can be noisy.

## Test signals
Build matrix coverage should include base JFFS2 as built-in and module, write-buffer on/off, summary on/off, xattr with ACL/security combinations, each compressor backend, and each compression mode choice. Runtime smoke tests should mount MTD-backed images using selected features and verify expected object files are present in the linked module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/Makefile -->
# sources/distributed-fs/ceph-client/fs/jffs2/Makefile

## Purpose
The Makefile maps JFFS2 Kconfig selections to the `jffs2.o` composite object. It defines the always-built core object list for `CONFIG_JFFS2_FS` and appends optional feature objects for write buffering, xattrs, security labels, ACLs, compressors, and summary support.

## Important build rules
`obj-$(CONFIG_JFFS2_FS) += jffs2.o` builds JFFS2 only when the main Kconfig option is enabled. The base `jffs2-y` list includes compression framework code, directory/file/ioctl operations, node management, allocation helpers, read/write/scan/GC paths, symlink/build/erase/background/fs/writev/super/debug code. Conditional additions include `wbuf.o`, `xattr.o xattr_trusted.o xattr_user.o`, `security.o`, `acl.o`, `compr_rubin.o`, `compr_rtime.o`, `compr_zlib.o`, `compr_lzo.o`, and `summary.o`.

## Control flow and integration
This file is the build-system bridge from `Kconfig` to source inclusion. It ensures `build.o` and `background.o` are part of the core filesystem, while `acl.c` is present only with `CONFIG_JFFS2_FS_POSIX_ACL`. Xattr support is required before ACL/security objects are meaningful because those features persist metadata through xattr nodes. Compression objects correspond to the Kconfig backend options.

## State and persistence behavior
The Makefile has no runtime state, but the linked object set controls supported on-flash formats and metadata. Omitting a compressor may prevent reading nodes compressed by that algorithm. Omitting summary support disables summary-node consumption/production. Omitting ACL/security removes support for persisted xattr classes.

## Dependencies, risks, and test signals
Risks are mostly configuration drift: adding a new source file or Kconfig option without updating this Makefile would silently exclude functionality. Build tests should cover `CONFIG_JFFS2_FS=m/y`, optional xattr/ACL/security combinations, all compressor toggles, summary support, and link verification that each enabled object is included in `jffs2.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/acl.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/acl.c

## Purpose
`acl.c` implements JFFS2 POSIX ACL support on top of JFFS2 xattrs. It converts between Linux `struct posix_acl` objects and the compact on-flash JFFS2 ACL format, retrieves and stores ACL xattrs, updates inode mode bits for access ACL changes, and stages inherited ACLs during inode creation.

## Important APIs, types, and functions
External functions are `jffs2_get_acl()`, `jffs2_set_acl()`, `jffs2_init_acl_pre()`, and `jffs2_init_acl_post()`. Internal conversion helpers are `jffs2_acl_size()`, `jffs2_acl_count()`, `jffs2_acl_from_medium()`, `jffs2_acl_to_medium()`, and `__jffs2_set_acl()`. Persistent payload types are declared in `acl.h`: `jffs2_acl_header`, `jffs2_acl_entry_short`, and `jffs2_acl_entry`. Xattr prefixes are `JFFS2_XPREFIX_ACL_ACCESS` and `JFFS2_XPREFIX_ACL_DEFAULT`.

## Control flow
`jffs2_get_acl()` rejects RCU lookup with `-ECHILD`, maps ACL type to the JFFS2 xattr prefix, queries the xattr size with `do_jffs2_getxattr()`, allocates a buffer if present, reads the value, and converts it with `jffs2_acl_from_medium()`. `-ENODATA` and `-ENOSYS` map to no ACL.

`jffs2_set_acl()` maps the ACL type. For access ACLs, it calls `posix_acl_update_mode()` to compute the inode mode implied by the ACL; if the mode changes it updates mode and ctime through `jffs2_do_setattr()`. For default ACLs, it rejects setting an ACL on non-directories with `-EACCES`. It then serializes or removes the xattr via `__jffs2_set_acl()` and updates the inode ACL cache on success.

`jffs2_init_acl_pre()` is called during inode creation before the inode has been fully persisted. It calls `posix_acl_create()` using the parent directory and proposed mode, caches inherited default/access ACLs on the new inode, and adjusts the mode through the `i_mode` pointer. `jffs2_init_acl_post()` later writes cached default/access ACLs to xattrs after the inode exists.

## State and persistence behavior
On-flash ACL data starts with `JFFS2_ACL_VERSION`, then stores the first four canonical ACL entry classes in short form and user/group named entries in long form with IDs. Conversion uses JFFS2 endian helpers (`je16`, `je32`) and maps IDs through `init_user_ns`. A null ACL removes the xattr; `-ENODATA` from deletion is normalized to success. ACL caches (`i_acl`, `i_default_acl`) are populated during creation and after successful set operations.

## Dependencies and integration points
This file depends on POSIX ACL helpers, JFFS2 xattr get/set, JFFS2 setattr, MTD/JFFS2 endian types, inode ACL caching, and the VFS ACL operation hooks declared in `acl.h`. It only builds when `CONFIG_JFFS2_FS_POSIX_ACL` is enabled, which itself depends on JFFS2 xattrs.

## Risks and edge cases
Conversion is format-sensitive. Malformed sizes, unknown versions, invalid tags, trailing bytes, and UID/GID entries that overrun the buffer all return `-EINVAL`. The count calculation assumes the fixed ordering/short-entry convention for the first four entries. `jffs2_acl_to_medium()` allocates based on `acl->a_count`; unexpected tags fail and free the buffer. Access ACL updates must keep mode bits and ACL xattr synchronized, or permission checks can diverge. RCU get is unsupported and must return `-ECHILD` for VFS retry.

## Test signals
Test get/set/remove access and default ACLs, inherited ACLs at inode creation, non-directory default ACL rejection, ACL mode-bit updates and ctime changes, malformed ACL blobs with bad version/size/tag/trailing data, named user/group ID round trips, no-xattr cases returning null ACL, xattr set/delete failures, cache updates, and builds with POSIX ACL disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/acl.h -->
# sources/distributed-fs/ceph-client/fs/jffs2/acl.h

## Purpose
`acl.h` defines the JFFS2 on-flash ACL structures and conditionally exposes POSIX ACL operation prototypes or no-op macros depending on `CONFIG_JFFS2_FS_POSIX_ACL`.

## Important APIs and types
`struct jffs2_acl_entry` stores tag, permission, and ID for named user/group entries. `struct jffs2_acl_entry_short` stores tag and permission for ACL entries that do not need an ID. `struct jffs2_acl_header` stores the ACL version followed by a flexible entry array. When ACL support is enabled, the header declares `jffs2_get_acl()`, `jffs2_set_acl()`, `jffs2_init_acl_pre()`, and `jffs2_init_acl_post()`.

When ACL support is disabled, `jffs2_get_acl` and `jffs2_set_acl` are defined as `NULL`, and init hooks return zero. This lets the rest of JFFS2 compile without POSIX ACL code while VFS operation tables can omit ACL handlers.

## Control flow and integration
`acl.c` consumes these structures for serialization/deserialization. Other JFFS2 files include this header to wire inode operation ACL hooks and inode creation hooks. The conditional macros mirror the Makefile/Kconfig relationship: `acl.o` is only linked when `CONFIG_JFFS2_FS_POSIX_ACL` is enabled.

## State and persistence behavior
The header defines the layout of persisted ACL xattr payloads. Any change to these structs would be an on-flash format change. The distinction between short and long entries is part of the encoder/decoder contract in `acl.c`.

## Risks and test signals
Risks include ABI drift between the struct layout and `acl.c` size/count calculations, missing ACL operation hooks when the config is enabled, and accidental non-NULL hooks when disabled. Test with ACL enabled and disabled builds, validate serialized ACL byte sizes for short and long entries, and run create/get/set ACL tests against mounted JFFS2 images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/background.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/background.c

## Purpose
`background.c` owns the JFFS2 garbage-collection daemon thread. It starts and stops the per-MTD GC kthread, wakes it when eraseblock state requires work, handles freezer and signal interactions, and repeatedly invokes `jffs2_garbage_collect_pass()` while throttling itself to reduce boot-time/user-space starvation.

## Important APIs and functions
The external functions are `jffs2_garbage_collect_trigger()`, `jffs2_start_garbage_collect_thread()`, and `jffs2_stop_garbage_collect_thread()`. The internal thread body is `jffs2_garbage_collect_thread()`. State is stored in `struct jffs2_sb_info`: `gc_task`, `gc_thread_start`, `gc_thread_exit`, `erase_completion_lock`, and the MTD index used in the thread name.

## Control flow
`jffs2_start_garbage_collect_thread()` asserts no existing GC task, initializes start/exit completions, starts `jffs2_garbage_collect_thread()` with `kthread_run()`, waits until the thread publishes `c->gc_task`, and returns the PID or an error. `jffs2_stop_garbage_collect_thread()` takes `erase_completion_lock`, sends `SIGKILL` to the GC task if present, drops the lock, and waits for `gc_thread_exit`.

`jffs2_garbage_collect_trigger()` must be called with `erase_completion_lock` held. If a GC task exists and `jffs2_thread_should_wake(c)` is true, it sends `SIGHUP` to wake the thread.

The thread allows `SIGKILL`, `SIGSTOP`, and `SIGHUP`, publishes `gc_task`, lowers priority with nice value 10, and marks itself freezable. In its loop it unblocks SIGHUP, sleeps when `jffs2_thread_should_wake()` is false, delays 50 ms to avoid starving user-space after boot, handles freezer and pending signals, blocks SIGHUP while doing work, and calls `jffs2_garbage_collect_pass()`. `-ENOSPC` from a GC pass logs a notice and terminates the thread. On exit it clears `gc_task` under the erase lock and completes the exit completion.

## State and persistence behavior
This file does not directly persist flash data; persistence happens inside `jffs2_garbage_collect_pass()` and erase/write paths. Its state controls whether background GC runs and whether mount/unmount can safely wait for the daemon. Signal handling is used as an in-kernel wake/stop mechanism rather than user-visible process control.

## Dependencies and integration points
It depends on `nodelist.h` for JFFS2 internal state and `jffs2_thread_should_wake()`/`jffs2_garbage_collect_pass()`, on MTD for device naming, on kthreads, completions, freezer support, and kernel signal helpers. Mount/superblock code starts and stops this thread; erase completion paths trigger it when dirty/free-space thresholds require collection.

## Risks and edge cases
The start function must only be called when no GC thread exists; it uses `BUG_ON(c->gc_task)`. Stop relies on the thread processing `SIGKILL`; if the thread blocks in lower layers, unmount waits. The trigger requires the erase-completion spinlock and can race with exit unless `gc_task` is protected consistently. The deliberate 50 ms throttle improves interactivity but can delay reclaim under tight free-space pressure. `-ENOSPC` terminates background GC, which can leave the filesystem relying on foreground operations or remount/error handling.

## Test signals
Test thread start/stop on mount/unmount, trigger wakeups under the erase lock, freezer suspend/resume, SIGSTOP/SIGKILL/SIGHUP handling, no-work sleep and wake behavior, GC pass `-ENOSPC` termination, repeated start/stop cycles, and races between trigger and stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/background.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/build.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/build.c

## Purpose
`build.c` builds the in-memory JFFS2 filesystem model during mount. It allocates eraseblock structures, initializes block lists, scans the flash medium into inode caches and raw node references, reconstructs directory link counts and parent relationships, removes unlinked/dead inode trees, initializes xattr and summary subsystems, rotates block lists for wear leveling, and computes free-space/GC trigger thresholds.

## Important APIs, types, and functions
The external mount entry is `jffs2_do_mount_fs()`. Internal traversal helpers are `first_inode_chain()`, `next_inode()`, and `for_each_inode`. Build phases are implemented by `jffs2_build_filesystem()`, `jffs2_build_inode_pass1()`, `jffs2_build_remove_unlinked_inode()`, and `jffs2_calc_trigger_levels()`. Key types are `struct jffs2_sb_info`, `struct jffs2_eraseblock`, `struct jffs2_inode_cache`, `struct jffs2_full_dirent`, and `struct jffs2_raw_node_ref`.

## Control flow
`jffs2_do_mount_fs()` initializes `free_size`, computes `nr_blocks`, allocates `c->blocks` with `vzalloc()` or `kzalloc()`, initializes each eraseblock offset/free size, sets up all block-state lists, initializes `highest_ino` and summary state, calls `jffs2_sum_init()`, then calls `jffs2_build_filesystem()`. On success it computes trigger levels and returns. On failure it exits the summary subsystem and frees block storage.

`jffs2_build_filesystem()` sets `JFFS2_SB_FLAG_SCANNING`, calls `jffs2_scan_medium()`, clears scanning, dumps block lists for debug, then sets `JFFS2_SB_FLAG_BUILDING`. Pass 1 iterates all inode caches with `scan_dents`, resolves child inode caches for dirents, marks missing-child raw nodes obsolete, stores `fd->ic`, increments child `pino_nlink`, marks directory children, and flags possible hard-linked directories.

Pass 2 scans for inode caches with zero `pino_nlink` and calls `jffs2_build_remove_unlinked_inode()`. That function marks all raw nodes for the inode obsolete, walks child dirents if the inode was a directory, decrements child link counts, and pushes newly unlinked children onto a `dead_fds` list for iterative cleanup instead of recursion. Pass 2a drains `dead_fds` and repeats removal for children that reached zero links.

The final pass frees temporary `scan_dents`. For directories, it converts `pino_nlink` from a link count to the parent inode number and logs errors if hard-linked directories remain. Then it builds the xattr subsystem, clears the building flag, rotates lists for wear leveling, and returns success.

## State and persistence behavior
This file primarily reconstructs volatile mount state from persistent flash nodes. It marks obsolete raw nodes for missing children and dead inodes, but actual deletion/freeing of inode caches is deferred to erase code after nodes are completely gone. `scan_dents` are temporary mount-build structures; final directory parent information is stored in `pino_nlink` for directories after build. The block lists initialized here (`clean`, `dirty`, `very_dirty`, `erasable`, `erasing`, `free`, `bad`, and others) become the runtime allocation/erase/GC state.

Trigger levels persist only in memory but govern future writes and GC: deletion reserve, write reserve, background GC threshold, GC merge threshold, bad-block GC threshold, very-dirty trigger, and dirty-space no-space cutoff. Calculations scale with flash size, sector size, eraseblock count, and whether obsolete nodes can be marked on medium.

## Dependencies and integration points
`build.c` depends on scan code (`jffs2_scan_medium()`), node obsolescence (`jffs2_mark_node_obsolete()`), inode-cache lookup/freeing, raw-node reference freeing, full-dirent allocation/freeing, xattr subsystem build/clear, summary init/exit, list rotation, and MTD geometry in `jffs2_sb_info`. It is called from mount/superblock setup before background GC and normal operations rely on the reconstructed lists and inode caches.

## Risks and edge cases
Mount build must tolerate stale dirents, deletion dirents (`ino == 0`), missing child inode caches, dead directories with children, and old hard-linked directory artifacts. Incorrect link counting can retain deleted trees or delete live nodes. The overloaded `pino_nlink` field changes meaning from link count to parent inode for directories, so phase ordering matters. Error cleanup must free all `scan_dents` and clear xattrs without double-freeing raw node structures. Large flash devices can require vmalloc for eraseblock arrays, and all passes use `cond_resched()` to avoid long mount-time stalls.

## Test signals
Test mounting clean images, images with stale dirents to missing inodes, deleted directories with nested children, hard-linked directory artifacts, large directories, large flash requiring vmalloc, xattr subsystem build failure, summary init failure, scan failure cleanup, block-list initialization correctness, trigger-level calculations for small/large media, and wear-level list rotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/build.c -->
