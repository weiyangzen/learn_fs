# Grouped Research: subset-b-009074

This grouped research report covers the requested WiredTiger Python suite files. Each section is delimited for deterministic splitting into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint17.py

Purpose: validates that a checkpoint can still read needed history-store content when the history store is clean at the time a later checkpoint is taken. It covers named and unnamed checkpoints, row-store and column-store tables, and `precise_checkpoint` on/off.

Important APIs and types: `wttest.WiredTigerTestCase`, `SimpleDataSet`, `make_scenarios`, `session.checkpoint`, checkpoint cursors with `checkpoint=` and `debug=(checkpoint_read_timestamp=...)`, and timestamp helpers from the test base.

Control flow: create an empty dataset, pin oldest/stable timestamps, write three timestamped full-table value generations, checkpoint at stable 30, write a disjoint key range at timestamp 40, checkpoint again, then open the later checkpoint at historical read timestamps 10, 20, and 30.

State and persistence behavior: the test intentionally makes the second checkpoint have no new history for the original key range, so history-store checkpoint retention is the persistence concern. It verifies old values remain reconstructable from the checkpoint even after the live tree has advanced.

Dependencies and integration points: depends on WiredTiger checkpoint cursor timestamp debug configuration and on history-store checkpoint matching. Skipped for disaggregated and tiered hooks because named checkpoint support or tiered behavior differs.

Risks: false failures can come from changes to checkpoint read timestamp semantics, history-store cleanup, or named checkpoint rules. The `zeros` argument is currently unused, so count-only absence checks rely on cursor iteration.

Test signals: success is all checkpoint cursor scans returning exactly `nrows` rows with the expected historical value for each timestamp and checkpoint precision scenario.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint18.py

Purpose: tests that an open checkpoint cursor pins the matching history-store checkpoint in a non-timestamped scenario while a later checkpoint advances the database and can remove the older history-store footprint.

Important APIs and types: `checkpoint_thread`, `stat.conn.checkpoint_state`, `SimpleDataSet`, `session.open_cursor(..., "checkpoint=WiredTigerCheckpoint")`, and `timing_stress_for_test=[checkpoint_slow]`.

Control flow: populate baseline data and checkpoint; start a second session with odd-key updates held open; run a background checkpoint and wait until it starts; commit the transaction during the checkpoint; update the remaining even keys; open a checkpoint cursor; take another checkpoint; then scan the first checkpoint cursor.

State and persistence behavior: the first checkpoint is potentially inconsistent with a transaction committed mid-checkpoint. The open cursor must hold the correct checkpoint and matching history-store state even after the second checkpoint writes more pages and performs cleanup.

Dependencies and integration points: integrates with checkpoint thread synchronization through connection statistics. `precise_checkpoint=true` requires a stable timestamp seed. Skipped for disaggregated and tiered hooks.

Risks: timing is sensitive because it waits on checkpoint state polling. The expected result depends on checkpoint cursor snapshot pinning rather than named checkpoint behavior.

Test signals: the final checkpoint cursor must see only `value_a` for all rows, proving neither odd-key nor even-key later writes leaked into the pinned checkpoint view.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint19.py

Purpose: timestamped companion to checkpoint cursor pinning tests. It verifies that checkpoint cursors opened at different checkpoint read timestamps keep access to the correct history-store checkpoint after a later checkpoint and history cleanup.

Important APIs and types: `WiredTigerTestCase`, `SimpleDataSet`, timestamped transactions, `session.open_cursor` with `checkpoint=WiredTigerCheckpoint,debug=(checkpoint_read_timestamp=...)`, and `make_scenarios`.

Control flow: create baseline data at timestamp 10, update odd keys at timestamps 20 and 30, checkpoint at stable 30, update even keys at timestamp 40, open three checkpoint cursors for read timestamps 10/20/30, advance stable to 40 and oldest to 35, checkpoint again, then scan all pinned cursors.

State and persistence behavior: advancing oldest past 30 makes older history eligible for cleanup. The test checks that already-open checkpoint cursors retain the historical version chain and matching history-store checkpoint despite later cleanup.

Dependencies and integration points: exercises timestamp visibility, history-store reconciliation, checkpoint cursor debug options, and precise/fuzzy checkpoint modes. Skipped for tiered and disaggregated hooks.

Risks: key parity is inferred from cursor scan count rather than parsing keys; changes in iteration order would break assumptions. History cleanup must actually rewrite involved history-store pages for the test to catch regressions.

Test signals: timestamp 10 sees all `value_a`; timestamp 20 sees odd `value_b` and even `value_a`; timestamp 30 sees odd `value_c` and even `value_a`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint20.py

Purpose: verifies reading checkpoint data when the checkpoint contains prepared updates. The intended behavior is that checkpoint cursors use ignore-prepare semantics and expose stable prior values rather than failing on prepared conflicts.

Important APIs and types: prepared transactions (`prepare_transaction`, `timestamp_transaction`, durable commit), `SimpleDataSet`, debug eviction cursors `debug=(release_evict)`, named/unnamed checkpoints, and checkpoint read timestamps.

Control flow: write stable data at timestamp 10; prepare updates over half the table at prepare timestamp 20; evict pages while reading at timestamp 10 so prepared content is written; checkpoint with stable timestamp either 15 or 25; commit prepared data later; then read checkpoint at timestamps 10, 20, and default.

State and persistence behavior: the checkpoint can contain pages with prepared data, but the checkpoint cursor should reconstruct the visible stable state. Eviction forces prepared updates to disk before checkpoint to exercise on-disk prepare handling.

Dependencies and integration points: depends on transaction prepare/durable timestamp semantics, eviction debug cursors, checkpoint cursor visibility, and scenario coverage over row/column stores plus named/unnamed checkpoints.

Risks: the disabled `checkfail` path documents older conflict expectations but is not active. The test is sensitive to eviction effectiveness because without writing prepared pages the main edge case may not be reached.

Test signals: all checkpoint reads return exactly `value_a` for every row, including reads at timestamp 20 and default checkpoint read timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint21.py

Purpose: tests checkpoint visibility for a committed prepared transaction whose commit timestamp is before stable but durable timestamp is after stable. It documents the chosen behavior that checkpoint cursors may show committed-but-not-yet-durable data in no-read-timestamp mode while timestamped reads follow timestamp visibility.

Important APIs and types: prepared transaction APIs, durable timestamp commit configuration, `debug=(release_evict)`, named/unnamed checkpoint helpers, and checkpoint cursor timestamp debug configuration.

Control flow: write initial data at timestamp 10; prepare full-table update at timestamp 20; advance stable to 30; commit at timestamp 25 with durable timestamp 35; evict half the pages; checkpoint while stable remains 30; then read the checkpoint at 15, 25, default, and no timestamp.

State and persistence behavior: half the transaction is forced to disk before checkpoint, and the remaining pages are checkpointed later. The core persistence question is whether checkpoint reconstructs a torn transaction consistently.

Dependencies and integration points: integrates timestamped visibility with prepared transaction persistence and checkpoint cursor read-time handling. Skipped for tiered and disaggregated hooks.

Risks: comments explain the semantics are pragmatic rather than obviously final. Any future change to default checkpoint read timestamp or durable timestamp visibility would need this test revisited.

Test signals: timestamped/default checkpoint reads see `value_a`, while no-read-timestamp checkpoint read sees all `value_b`, proving no torn transaction is observed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint22.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint22.py

Purpose: verifies that skipped trees during checkpoint retain and use the correct checkpoint write generation after restart, so transaction IDs on disk are unpacked with the checkpoint generation rather than the current one.

Important APIs and types: `SimpleDataSet`, checkpoint helper for named/unnamed checkpoints, `reopen_conn`, open read transactions, and transaction ID generation through many small commits.

Control flow: create two tables; churn many commits to raise transaction IDs; hold a reader transaction so later txnids are written to disk; update the main table to `value_b`; checkpoint; rollback reader and restart; update a second table so a subsequent checkpoint is non-vacuous while the first table is skipped; checkpoint again; read the first table from the second checkpoint.

State and persistence behavior: the first table is unchanged across restart and second checkpoint, so the checkpoint may skip it. The test protects persistence metadata that records the correct write generation for unpacking transaction visibility.

Dependencies and integration points: relies on restart behavior, transaction ID visibility without timestamps, checkpoint skip logic, and named/unnamed checkpoint combinations. Skipped for disaggregated and tiered hooks.

Risks: the comment notes more advanced torn-transaction variants are not practical in Python. The test assumes transaction IDs after restart are sufficiently lower than pre-restart IDs.

Test signals: reading the second checkpoint for the skipped table returns all `value_b` rows, showing checkpoint-generation visibility did not hide valid data.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint22.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint24.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint24.py

Purpose: non-timestamped fast-delete checkpoint test. It verifies checkpoint cursors can read a checkpoint containing pages deleted through fast truncate, including after optional reopen for named checkpoints.

Important APIs and types: `session.truncate`, `stat.conn.rec_page_delete_fast`, `SimpleDataSet`, named/unnamed checkpoint helper, and `session.open_cursor(..., checkpoint=...)`.

Control flow: populate a table, reopen to force data on disk, truncate the middle half, assert fast-delete stats increased, checkpoint, optionally reopen, then scan the checkpoint cursor.

State and persistence behavior: the checkpoint stores fast-deleted page state, and the cursor must enumerate only surviving records. Reopen coverage verifies named checkpoint metadata remains usable after restart.

Dependencies and integration points: uses row and column store scenarios, statistics cursor, and checkpoint cursor reads. Unnamed checkpoint plus reopen is intentionally avoided because reopen creates a new unnamed checkpoint.

Risks: depends on truncate choosing fast-delete for at least one page; page size or dataset changes may reduce coverage. Skipped on tiered/disaggregated hooks.

Test signals: `rec_page_delete_fast` is greater than zero and the checkpoint scan returns exactly half the original rows with the original value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint24.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint25.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint25.py

Purpose: timestamped counterpart to fast-delete checkpoint reading. It verifies that checkpoint cursors handle fast-deleted pages correctly across historical, default, and no-read-timestamp reads after optional timestamp advancement and reopen.

Important APIs and types: timestamped `session.truncate`, `stat.conn.rec_page_delete_fast`, checkpoint cursor `debug=(checkpoint_read_timestamp=...)`, `set_timestamp`, and `make_scenarios` over oldest/stable advancement.

Control flow: write data at timestamp 10, make it stable and reopen, fast-truncate the middle half at timestamp 20, set stable 20, verify fast-delete stats, checkpoint, optionally advance oldest/stable and reopen, then read the checkpoint at timestamps 15, 25, default, and 0.

State and persistence behavior: the checkpoint must preserve both pre-truncate and post-truncate views. Historical reads at 15 see all rows; newer/default/no-read-timestamp views see only surviving rows.

Dependencies and integration points: covers row/column stores, named/unnamed checkpoints, timestamp advancement, history-store visibility, and fast-delete reconciliation. Skipped for tiered/disaggregated hooks.

Risks: broad scenario matrix can be expensive. The zero-count argument is not directly checked against cursor holes for column-store beyond count/value assertions.

Test signals: fast-delete statistic is positive; read timestamp 15 returns all rows; read timestamp 25/default/0 return half the rows.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint25.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint26.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint26.py

Purpose: validates the `timing_stress_for_test=[checkpoint_evict_page]` mode, which makes checkpoint evict reconciled pages, and confirms checkpoint-driven eviction is observable in statistics.

Important APIs and types: `WiredTigerTestCase`, `stat.conn.eviction_pages_in_parallel_with_checkpoint`, `session.checkpoint`, and `make_scenarios` for precise versus fuzzy checkpoint.

Control flow: create a table with integer keys and large string values, insert 10,000 records in separate transactions, assert the checkpoint-eviction statistic is initially zero, run checkpoint, and assert the statistic is now positive.

State and persistence behavior: the table is large enough to produce dirty pages but uses a large cache and high dirty targets so ordinary eviction should not run before checkpoint. Persistence is validated indirectly by checkpoint eviction statistics.

Dependencies and integration points: uses WiredTiger connection configuration for cache, dirty eviction targets, all statistics, and timing stress. Precise checkpoint mode needs a stable timestamp set first.

Risks: statistic isolation is important; unexpected eviction before checkpoint would invalidate the initial assertion. The test does not scan data after checkpoint.

Test signals: zero `eviction_pages_in_parallel_with_checkpoint` before checkpoint, greater than zero after checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint26.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint27.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint27.py

Purpose: checks that evicting metadata pages while reading checkpoint cursors does not corrupt checkpoint metadata access or history-store lookup.

Important APIs and types: `debug=(release_evict)` cursor on `file:WiredTiger.wt`, named/unnamed checkpoints, checkpoint cursor read timestamps, and `SimpleDataSet`.

Control flow: write two timestamped value generations, checkpoint, then repeatedly call `evict_metadata` before opening checkpoint cursors, after opening, and during first scan iteration. Reads are performed at historical timestamp 15, newer timestamp 25, default, no timestamp, and again at 15.

State and persistence behavior: the test forces metadata pages out of cache around checkpoint cursor reads so checkpoint handle/metadata reconstruction must be robust to eviction and reload.

Dependencies and integration points: directly touches the WiredTiger metadata file via an eviction debug cursor. Skipped for tiered and disaggregated hooks because checkpoint/metadata behavior differs.

Risks: metadata eviction is intentionally awkward and may be sensitive to metadata table size. Comments note preliminary scans may be required before metadata eviction reproduces the targeted path.

Test signals: all checkpoint scans return exactly expected values and counts, including historical reads that require history-store content.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint27.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint28.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint28.py

Purpose: verifies checkpoint visibility for a prepared transaction committed during a checkpoint where commit and durable timestamps straddle the checkpoint's stable timestamp, across two tables.

Important APIs and types: `checkpoint_thread`, `stat.conn.checkpoint_state`, prepared transaction calls, `timing_stress_for_test=[checkpoint_handle]`, and checkpoint cursors.

Control flow: create two tables, prepare full-table updates at timestamp 20, advance stable to 30, start a background checkpoint and wait for it to start, commit at timestamp 25 with durable timestamp 35, open checkpoint cursors on both tables, and scan them.

State and persistence behavior: the checkpoint should not expose the prepared transaction because its durable timestamp is after stable. The two-table setup checks consistent handling across handles in the checkpoint.

Dependencies and integration points: depends on checkpoint stress timing, prepared transaction visibility, stable/durable timestamp rules, and checkpoint cursor reads. Skipped for tiered and disaggregated hooks.

Risks: checkpoint timing is synchronization-sensitive. The test asserts both tables have identical zero-row visibility in the checkpoint for the inserted rows.

Test signals: checkpoint cursors for both tables scan zero rows, proving prepared updates did not become visible in the checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint28.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint29.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint29.py

Purpose: tests checkpoint cursor behavior after bulk cursor activity creates a single-file checkpoint that is not valid as the system checkpoint.

Important APIs and types: `session.open_cursor(..., "bulk")`, `session.checkpoint`, internal checkpoint name `WiredTigerCheckpoint`, `expectedStdoutPattern`, and `wiredtiger.WiredTigerError`.

Control flow: create an empty table, take a system checkpoint, open and close a bulk cursor, attempt to open `checkpoint=WiredTigerCheckpoint` and expect failure plus warning, take another system-wide checkpoint, then open the checkpoint cursor successfully.

State and persistence behavior: bulk cursor close creates per-file checkpoint metadata that can be inconsistent with the system checkpoint. A subsequent database-wide checkpoint repairs the metadata state.

Dependencies and integration points: exercises bulk-load metadata interaction with checkpoint cursor opening. Skipped for tiered and disaggregated hooks.

Risks: warning text is part of the test contract. Precise checkpoint mode requires a stable timestamp seed.

Test signals: first checkpoint cursor open raises with stdout containing `could not open the checkpoint`; second open after full checkpoint succeeds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint29.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint30.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint30.py

Purpose: tests snapshot cursor visibility when aggregate time-window information says a page is visible but individual deleted on-disk versions are not all visible to an active reader.

Important APIs and types: timestamped transactions, long-lived reader transaction, `debug=(release_evict)` eviction cursor, `large_removes`, and `session.checkpoint`.

Control flow: write 100 rows at timestamp 10; hold open an uncommitted remove for key 1; remove the remaining keys at timestamp 20; start a reader transaction; commit key 1 remove at timestamp 25; verify the reader still sees key 1 before eviction, after eviction, and after checkpoint.

State and persistence behavior: the reader snapshot should not be invalidated by evicting or checkpointing pages whose aggregate deletion state may appear visible. The test protects per-key visibility when deletion state is persisted.

Dependencies and integration points: uses checkpoint, eviction, transaction snapshot isolation, and timestamped removes. Tiered storage is skipped.

Risks: the `check` helper ignores its `ts` parameter and relies on the session's existing transaction state for long-lived visibility. Data size is small but targets a subtle visibility edge.

Test signals: the reader sees exactly one row with `value_a` after each state transition.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint30.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint31.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint31.py

Purpose: verifies named checkpoint cursors can be opened and read from a read-only connection, particularly when prepared transaction durable timestamps mean later values should not be visible in the named checkpoint.

Important APIs and types: prepared transactions, named `session.checkpoint("name=ckpt1")`, `reopen_conn(config="readonly=true")`, and checkpoint cursor lookup.

Control flow: create two prepared updates to key `2`; checkpoint `ckpt1` with stable timestamp between commit and durable timestamp of the second update; take a later unnamed checkpoint at stable 40; reopen normally and read `ckpt1`; reopen read-only and read `ckpt1` again.

State and persistence behavior: the named checkpoint must persist its visibility state after restart and be readable without write access. Expected value for key `2` is the first transaction's value.

Dependencies and integration points: checkpoint cursor opening in read-only mode, prepared transaction timestamp handling, and named checkpoint metadata. Skipped for disaggregated hooks.

Risks: no tiered skip is present; behavior may be environment-sensitive if named checkpoint support changes. Error paths are not exercised here.

Test signals: both normal and read-only reopened connections find key `2` in `ckpt1` and return value `20`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint31.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint32.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint32.py

Purpose: tests cursor tree-walk optimization that skips in-memory reconciled deleted pages after checkpoint.

Important APIs and types: `SimpleDataSet`, `stat.conn.cursor_tree_walk_inmem_del_page_skip`, transaction-per-key inserts/removes, and checkpoint.

Control flow: populate a table, insert 1,000 rows, hold a read transaction open, remove all data in individual transactions, checkpoint, read the statistic baseline, scan the table expecting no rows, read the statistic again, and assert it increased.

State and persistence behavior: deleted pages remain represented in memory while an old reader is open. After checkpoint, cursor traversal should skip the in-memory deleted pages rather than walking them normally.

Dependencies and integration points: relies on cursor traversal statistics and the presence of an active reader to keep deleted page state relevant. Covers row-store and column-store formats plus precise/fuzzy checkpoint.

Risks: precise checkpoint requires stable timestamp initialization. Statistic changes may vary if cursor traversal implementation changes.

Test signals: table scan returns zero rows and `cursor_tree_walk_inmem_del_page_skip` increases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint32.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint33.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint33.py

Purpose: verifies checkpoint does not skip tables whose end-of-file free space can be reclaimed after checkpoint cleanup, and that repeated checkpointing can shrink a fully deleted table to minimum size.

Important APIs and types: `test_cc_base` checkpoint-cleanup helper, `suite_subprocess`, `stat.dsrc.block_size`, timestamped populate/delete loops, eviction cursor `debug=(release_evict)`, and `wait_for_cc_to_run`.

Control flow: create and populate a large table at timestamp 2, checkpoint at stable 3, delete all keys at timestamp 4, checkpoint at stable 5, evict all pages, advance oldest to 5, then loop waiting for checkpoint cleanup and checkpointing until file size drops below 12KB or max attempts.

State and persistence behavior: deletion becomes globally visible, checkpoint cleanup removes obsolete pages, and checkpoint should rewrite/truncate to reclaim file-end space.

Dependencies and integration points: integrates checkpoint cleanup with block manager truncation and statistics. Skips under TSan due to known compression-size failure.

Risks: high data volume and per-key transactions make it expensive. File size expectations depend on allocation/page layout and checkpoint cleanup timing.

Test signals: final `block_size` is less than or equal to `min_file_size`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint33.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint34.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint34.py

Purpose: tests precise checkpoint behavior with an unstable fast truncate followed by crash restart. The unstable truncate should not require rollback-to-stable update aborts and original data must remain after recovery.

Important APIs and types: `conn_config = "precise_checkpoint=true"`, `SimpleDataSet`, `session.truncate`, `stat.conn.rec_page_delete_fast`, `simulate_crash_restart`, and `stat.conn.txn_rts_upd_aborted`.

Control flow: write 200,000 timestamped rows while advancing stable, reopen, perform an unstable truncate from midpoint to end at a later timestamp without advancing stable, confirm fast-truncate statistic, checkpoint, crash/restart, inspect RTS stats, then read all rows.

State and persistence behavior: precise checkpoint should avoid persisting unstable fast-truncate changes in a way that recovery must abort. All original stable values should be available after restart.

Dependencies and integration points: precise checkpoint, fast truncate, rollback-to-stable recovery, and crash simulation. Tiered hook is skipped.

Risks: large row count makes this a heavy test. It assumes `txn_rts_upd_aborted` stays zero because precise checkpoint prevented unstable update persistence.

Test signals: fast truncate pages are observed, RTS aborted update count is zero, and every key returns `value_a` after crash restart.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint34.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint35.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint35.py

Purpose: tests precise checkpoint with stable full-table data and later unstable updates. After crash restart, rollback-to-stable should not report aborted updates and stable data should remain intact.

Important APIs and types: `conn_config = "precise_checkpoint=true"`, `SimpleDataSet`, per-row timestamped writes, `simulate_crash_restart`, and `stat.conn.txn_rts_upd_aborted`.

Control flow: create one million rows at increasing timestamps while advancing stable, write unstable `value_b` updates to the first 99 keys at a future timestamp, checkpoint, crash/restart, assert RTS aborted count is zero, then scan all keys for the stable value.

State and persistence behavior: precise checkpoint is expected to avoid writing unstable updates that would need RTS cleanup. The checkpoint plus recovery should present only stable `value_a` data.

Dependencies and integration points: tests precise checkpoint, timestamp stability, crash recovery, and RTS statistics. It covers row and column store formats.

Risks: very large data volume may be expensive. It does not assert that unstable updates are absent before crash, only after recovery.

Test signals: `txn_rts_upd_aborted == 0` and every row reads `value_a`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint35.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint36.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint36.py

Purpose: verifies API constraints for precise checkpoint when no checkpoint timestamp is available and when attempting `use_timestamp=false`.

Important APIs and types: `WiredTigerTestCase`, `wiredtiger.WiredTigerError`, `assertRaisesWithMessage`, `session.checkpoint`, and `conn.set_timestamp`.

Control flow: open with `precise_checkpoint=true`, call checkpoint before setting stable timestamp and expect an error mentioning stable timestamp; set stable timestamp 5 and checkpoint successfully; then call checkpoint with `use_timestamp=false` and expect an error.

State and persistence behavior: this is an API validation test rather than a data persistence test. It ensures precise checkpoint always has timestamp context and cannot be bypassed with `use_timestamp=false`.

Dependencies and integration points: direct checkpoint API behavior under precise checkpoint mode. Tiered hook is skipped.

Risks: the second expected error message is empty, so only the exception type is effectively checked. Comments refer to `test_checkpoint35.py`, likely a stale file-name comment.

Test signals: first and third checkpoint calls raise `WiredTigerError`; checkpoint after setting stable timestamp succeeds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint36.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint37.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint37.py

Purpose: verifies reconciliation during checkpoint removes obsolete updates from pages and keeps cache memory growth bounded.

Important APIs and types: `eviction=[skip_update_obsolete_check=true]`, timestamped `large_updates`, `stat.conn.cache_bytes_inuse`, `stat.conn.cache_obsolete_updates_removed`, and checkpoint.

Control flow: write initial data at timestamp 5, set oldest/stable, checkpoint and reopen, perform repeated full-table updates at timestamps 10, 20, 30, and 40; after advancing oldest/stable to each new timestamp, checkpoint and compare cache bytes with an earlier baseline; finally assert obsolete-update removal statistic is positive.

State and persistence behavior: as oldest advances, older update chains become obsolete. Checkpoint reconciliation should discard obsolete updates and avoid unbounded cache growth.

Dependencies and integration points: interacts with eviction configuration, cache statistics, timestamp advancement, and checkpoint reconciliation. Covers row/column stores.

Risks: contains `self.session.breakpoint()`, which may be test-harness specific and surprising. Cache byte thresholds are heuristic (`< prev * 2`).

Test signals: cache bytes after each checkpoint stay below twice baseline and `cache_obsolete_updates_removed` is greater than zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint37.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint38.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint38.py

Purpose: validates parallel checkpoint worker threads reconcile pages during a large checkpoint and that related statistics are populated.

Important APIs and types: `checkpoint_threads` connection configuration, `stat.conn.checkpoint_pages_reconciled`, `checkpoint_parallel_pages_reconciled`, `checkpoint_sync_rec_pct`, and statistics logging.

Control flow: run scenarios with 4 and 8 checkpoint threads, create a table with 55,000 large records and small leaf pages, sample checkpoint stats, run checkpoint, compute deltas, print metrics, and assert reconciliation happened in both total and parallel-worker counters.

State and persistence behavior: a large cache and disabled pre-checkpoint scrubbing keep dirty pages in cache until the checkpoint walk. The test is about checkpoint execution distribution, not data scan validation.

Dependencies and integration points: uses connection-level checkpoint threading, eviction tuning, statistics cursors, and statistics log configuration. It can run under tiered hook because cache is enlarged for that overhead.

Risks: data volume is about hundreds of MB and can be resource-heavy. If eviction writes dirty pages before checkpoint, parallel counters may be low.

Test signals: total pages reconciled, parallel pages reconciled, and checkpoint sync reconciliation percentage are all greater than zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint38.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot01.py

Purpose: verifies checkpoint metadata can be saved while multiple sessions hold active snapshots with uncommitted inserts.

Important APIs and types: `copy_wiredtiger_home`, `SimpleDataSet`, multiple sessions/cursors, `begin_transaction`, and `session.checkpoint`.

Control flow: create a table, open five sessions, each begins a transaction and inserts a disjoint range beyond the initial rows without committing, run checkpoint in another session, copy the home directory to simulate crash material, then open the copied home.

State and persistence behavior: checkpoint must persist consistent snapshot metadata despite active uncommitted transactions. The copied home must be openable after the checkpoint.

Dependencies and integration points: tests metadata checkpointing and connection setup helpers. Tagged as `checkpoint:metadata`.

Risks: it does not assert table contents after reopening, so the main signal is absence of crash/open failure. The value format uses raw bytes (`u`) in both column and row-string scenarios.

Test signals: the copied checkpointed home opens successfully after uncommitted transactional activity.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot02.py

Purpose: exercises inconsistent checkpoint recovery when a checkpoint takes its snapshot before a concurrent transaction commits, for both crash restart and backup restore paths, with and without timestamps.

Important APIs and types: `backup_base`, `checkpoint_thread`, `simulate_crash_restart`, `take_full_backup`, `stat.conn.checkpoint_snapshot_acquired`, RTS stats `txn_rts_inconsistent_ckpt` and `txn_rts_keys_removed`.

Control flow: helpers populate and verify data, start a checkpoint thread, wait until checkpoint snapshot is acquired, then commit a transaction. Test variants cover non-timestamped inserts, timestamped inserts beyond stable, and a mixed txnid/timestamp case with an extra rollback and second restart.

State and persistence behavior: checkpoint and eviction timing can leave inconsistent checkpoint state. Recovery or backup restore should roll back uncheckpointed effects and preserve only the last checkpointed stable contents.

Dependencies and integration points: logging is disabled for some datasets, timing stress slows checkpoint, and backup/crash paths share validation. Disaggregated is skipped; one variant skips tiered.

Risks: thread timing and polling of statistics are central. The `check` helper prints ordering diagnostics and accepts only exact target counts.

Test signals: table contains the expected checkpointed value after restore/restart; inconsistent checkpoint stat is positive; removed-key stat is non-negative and zero on the second restart path.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot03.py

Purpose: verifies rollback-to-stable can skip unnecessary pages when a table contains more than the checkpoint snapshot, avoiding needless update aborts or restores.

Important APIs and types: `simulate_crash_restart`, `SimpleDataSet`, RTS statistics (`txn_rts_inconsistent_ckpt`, `txn_rts_keys_removed`, `txn_rts_keys_restored`, `txn_rts_tree_walk_skip_pages`, `txn_rts_upd_aborted`), and `make_scenarios`.

Control flow: hold an uncommitted insert beyond the main range, bulk-update 500,000 rows, checkpoint, rollback and reopen; repeat with a new uncommitted insert plus one committed update, checkpoint, rollback, crash/restart, then inspect RTS stats.

State and persistence behavior: restart recovery should identify inconsistent checkpoint state but skip pages that do not require rollback. No updates should be aborted or restored for the stable main content.

Dependencies and integration points: row-string and column scenarios, cache/statistics configuration, and crash simulation. Disaggregated is skipped because RTS behavior is not expected there.

Risks: large dataset and cache size make it heavier. Assertions around inconsistent checkpoint and skipped pages are bypassed for disaggregated hook even though class is skipped for that hook.

Test signals: `txn_rts_upd_aborted == 0`, `txn_rts_keys_restored == 0`, inconsistent checkpoint and page-skip stats are positive in normal runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot04.py

Purpose: tests backup dump/comparison behavior when transaction IDs are written to disk and checkpoint snapshot state exists.

Important APIs and types: `backup_base`, backup cursor `open_cursor("backup:")`, optional backup `target=`, `compare_backups`, `SimpleDataSet`, and transaction-per-row updates.

Control flow: start an uncommitted insert beyond the main range, write committed data in many transactions, checkpoint, create a full or targeted backup by copying backup cursor files, rollback the uncommitted transaction, then compare backup contents against the original twice.

State and persistence behavior: backup must represent the checkpointed state consistently even with transaction IDs on disk and an active transaction. Targeted backup lacks history store, so the second compare checks that RTS does not change backup contents on repeat.

Dependencies and integration points: integrates backup cursor file lists, dataset verification, and backup comparison utilities. Scenarios cover row-string and column stores plus full/targeted backup.

Risks: relies on filesystem copy of backup cursor entries. It does not explicitly inspect RTS stats, using compare output as the persistence signal.

Test signals: `compare_backups` succeeds for the backup versus the live home on repeated attempts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot05.py

Purpose: tests backup recovery after an inconsistent checkpoint created following a bulk load and concurrent checkpoint/transaction/eviction sequence.

Important APIs and types: `backup_base`, bulk cursor, `checkpoint_thread`, `wttest.open_cursor`, `stat.conn.checkpoint_snapshot_acquired`, `take_full_backup`, and RTS stats.

Control flow: bulk-load rows with `valuea`, hold a transaction updating all rows to `valueb`, start a single checkpoint thread and wait for snapshot acquisition, commit the update, evict all pages to force inconsistent checkpoint content, take a full backup, reopen the backup, and verify contents.

State and persistence behavior: recovery of the backup is expected to fix inconsistent checkpoint state and retain checkpointed bulk-loaded values, not the concurrent updated values.

Dependencies and integration points: logging enabled at connection level but table config disables logging for bulk data; timing stress slows checkpoint. Disaggregated is skipped for bulk-load support.

Risks: uses an `assert` for checkpoint count/skipped stats rather than `self.assert*`, making it dependent on Python assertion settings. Timing loop is deliberately aggressive.

Test signals: backup restore reads all `valuea` rows, `txn_rts_inconsistent_ckpt` is positive, and `txn_rts_keys_removed` equals zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot06.py

Purpose: tests recovery/backup correctness when checkpoint runs concurrently with truncates, reinserts, and eviction across two tables.

Important APIs and types: `backup_base`, `checkpoint_thread`, `copy_wiredtiger_home`, `simulate_crash_restart`, `take_full_backup`, truncate APIs, and `debug=(release_evict)` eviction cursors.

Control flow: create two logged tables, populate and verify both, remove key 50, start a truncate transaction deleting range 1-100, start another transaction reinserting key 50 with `valueb`, run checkpoint and wait for snapshot acquisition, commit insert then truncate, evict table 1 changes, checkpoint again, then backup or crash restart and verify both tables.

State and persistence behavior: out-of-order commit between insert and truncate plus eviction can create inconsistent checkpoint state. Recovery/backup should preserve the final reinserted key in both tables.

Dependencies and integration points: logging, checkpoint timing stress, backup/crash paths, and duplicate copy of pre-restart home for diagnostics.

Risks: no direct RTS stat assertions; correctness is key-based. Concurrent timing is central and uses polling on checkpoint snapshot acquisition.

Test signals: after restart/restore, key 50 is found in both tables with `valueb`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_chunkcache_cleanup.py -->
# sources/storage-engines/wiredtiger/test/suite/test_chunkcache_cleanup.py

Purpose: verifies startup cleanup removes stale chunk cache metadata on connection reopen.

Important APIs and types: `WiredTigerTestCase`, metadata cursor `open_cursor("metadata:")`, `wiredtiger.WT_NOTFOUND`, and `reopen_conn`.

Control flow: create the historical chunk cache metadata file URI `file:WiredTigerCC.wt`, confirm it exists in metadata, reopen the connection, then search metadata again.

State and persistence behavior: the created metadata entry survives until close/reopen, at which point startup cleanup should delete it. This tests migration/deprecation cleanup rather than cache functionality.

Dependencies and integration points: integrates with connection startup metadata cleanup code and WiredTiger metadata cursor semantics.

Risks: only metadata removal is asserted; physical file cleanup is not separately checked. URI is hard-coded to the chunk cache file name.

Test signals: metadata search returns success before reopen and `WT_NOTFOUND` after reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_chunkcache_cleanup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_chunkcache_deprecate.py -->
# sources/storage-engines/wiredtiger/test/suite/test_chunkcache_deprecate.py

Purpose: verifies deprecated chunk cache configuration is rejected or warned according to whether it attempts to enable or disable the removed feature.

Important APIs and types: `wiredtiger_open`, `open_conn`, `close_conn`, `assertRaisesWithMessage`, `expectedStdoutPattern`, and `wiredtiger.WiredTigerError`.

Control flow: close the default connection; attempt to open with `chunk_cache=(enabled=true)` and expect a deprecation error; reopen normally for teardown. A second test closes the connection and opens with `enabled=false`, expecting a deprecation warning on stdout.

State and persistence behavior: no data is created. The state under test is connection configuration acceptance and messaging for deprecated options.

Dependencies and integration points: directly exercises WiredTiger connection config parsing and compatibility/deprecation path.

Risks: stdout warning text is part of the contract and may be brittle. The disabled-warning test does not explicitly reopen normally afterward, relying on test lifecycle cleanup.

Test signals: enabling chunk cache raises; disabling chunk cache prints the expected deprecation warning while opening succeeds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_chunkcache_deprecate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_colgap.py -->
# sources/storage-engines/wiredtiger/test/suite/test_colgap.py

Purpose: covers variable-length column-store gaps and very large record numbers near the unsigned 64-bit maximum. It ensures traversal, search, update, and removal remain efficient and correct.

Important APIs and types: `SimpleDataSet`, `simple_key`, `simple_value`, cursor `next`/`prev`/`search`/`remove`, `wiredtiger.WT_NOTFOUND`, and `make_scenarios`.

Control flow: `test_column_store_gap` inserts sparse recnos with huge gaps, scans forward/backward before and after reopen. `test_column_store_gap_traverse` adds middle in-memory records after reopening and verifies merged traversal order. `test_colmax` creates file/table column stores, optionally bulk-loads, inserts a record at a huge or maximum recno, reopens optionally, then searches, updates, and removes it.

State and persistence behavior: tests both in-memory update lists and persisted disk pages, including traversal that merges on-disk records with new in-memory records. Large recnos test maximum key encoding and column-store namespace gaps.

Dependencies and integration points: variable-length column-store implementation, bulk cursor mode, file/table URI handling, and scenario matrix across value formats and reopen modes.

Risks: performance is implicit; a regression may hang rather than fail quickly. The `nentries` class field is mutated per test.

Test signals: exact forward/backward key sequences, successful lookup/update of huge recno, and `WT_NOTFOUND` after removal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_colgap.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact01.py

Purpose: validates session-level and utility compaction reduce page count after deleting most of a file or complex table.

Important APIs and types: `compact_util`, `suite_subprocess`, `SimpleDataSet`, `ComplexDataSet`, `runWt(["compact", ...])`, `session.compact`, `stat.dsrc.btree_row_leaf`, and compact progress stats.

Control flow: populate a dataset with many entries, reopen to force disk state, assert enough leaf pages exist, truncate most keys, compact via session method or `wt compact`, optionally after reopen, then reopen and check page count decreased below scenario threshold.

State and persistence behavior: compaction should rewrite/reclaim on-disk pages after deletion. Utility-mode compaction requires closing the connection and running the external tool.

Dependencies and integration points: uses compact progress stats for method mode, skip for timestamp hook because timestamped removals do not free space, and avoids progress stat checks for tiered/utility cases.

Risks: compaction behavior depends on page sizing, overflow avoidance, and storage hook behavior. Utility invocation depends on `suite_subprocess`.

Test signals: initial page count is above `maxpages`; after compaction and reopen, row leaf page count is below `maxpages`; method mode reports reviewed/rewritten progress.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact02.py

Purpose: tests that compact reduces file size after deleting large records, and that dry-run mode records expected rewrite estimates without actual shrinkage expectations.

Important APIs and types: `compact_util`, manual `wiredtiger_open`, `session.compact`, `get_size`, `raisesBusy`, compact progress stats, and `make_scenarios`.

Control flow: open a connection with scenario cache size, create a table avoiding overflow values, insert alternating large/small records, checkpoint and measure size, delete all large records, checkpoint, compact with `free_space_target=1MB` and optional `dryrun=true` retrying `EBUSY`, then measure size and stats.

State and persistence behavior: after deletion, file free space should be reclaimable by foreground compaction unless dry-run is selected. Dry-run only estimates rewrite work.

Dependencies and integration points: directly controls connection setup to vary cache size, uses compact utility helper stats, and skips size assertions under tiered hook.

Risks: file-size thresholds depend on storage layout and avoiding overflow pages. Retry loop can take time under eviction conflicts.

Test signals: non-dry-run non-tiered size falls below half full size and progress stats reconcile reviewed/rewritten/skipped pages; dry-run with enough pages reports expected bytes/pages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact03.py

Purpose: verifies compaction does not significantly reduce file size when overflow values remain at the end of the file, and that new normal values reuse freed middle extents without increasing file size.

Important APIs and types: `compact_util`, `make_scenarios`, `session.compact`, helper `truncate`, `populate`, `get_size`, and compact progress stats.

Control flow: create small-page table with many normal values, checkpoint and measure size, append overflow values, checkpoint and measure growth, delete or truncate the middle 90 percent of normal values, checkpoint, compact and verify size mostly unchanged, then reinsert normal values into the freed middle range and compact again.

State and persistence behavior: overflow pages at file end prevent effective file truncation despite rewritten middle pages. Freed middle extents should be reused by later inserts.

Dependencies and integration points: tests block manager compaction around overflow items and free extent reuse. Tiered hook is skipped due to occasional rollback errors.

Risks: sensitive to overflow thresholds and page allocation sizes. Assertions allow 10 percent leeway on size.

Test signals: size with overflow is greater than without; after compaction size remains at least 90 percent of overflow size; later inserts do not increase file size.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact04.py

Purpose: checks accuracy of compact work estimation by comparing expected rewritten pages with actual rewritten pages over repeated table instances.

Important APIs and types: `compact_util`, `stat.dsrc.btree_compact_pages_rewritten`, `btree_compact_pages_rewritten_expected`, `btree_compact_pages_selected_inmem`, `stat.conn.session_table_compact_bytes_rewrite_inmem`, and verbose compact output suppression.

Control flow: for up to 10 iterations, create and populate a table, checkpoint, delete several ranges to create reclaimable space, compact, read data-source and connection stats, compute prediction error, and terminate early if prediction is good with no failures.

State and persistence behavior: compaction estimation and actual rewriting are both tracked in statistics. The test tolerates rare inaccurate predictions but caps failures.

Dependencies and integration points: compact progress verbose/stat infrastructure, in-memory page selection, and `compact_util.populate`.

Risks: prediction accuracy is intentionally probabilistic; up to two failures are tolerated. Tiered storage returns early after gathering stats because compact stats are not meaningful there.

Test signals: non-tiered runs require positive rewritten/expected/selected stats and prediction error under 15 percent for at least one iteration before too many failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact05.py

Purpose: verifies foreground compaction honors `free_space_target`: it proceeds when available bytes exceed the threshold and skips with a warning when they do not.

Important APIs and types: `compact_util`, `make_scenarios`, `session.compact`, `expectedStdoutPattern`, `stat.dsrc.btree_compact_pages_rewritten`, and `btree_compact_pages_rewritten_expected`.

Control flow: create and populate a table, checkpoint, delete four large ranges, then compact with either `free_space_target=1MB` or `45MB`. For expected skip, capture stdout warning; otherwise compact normally and suppress verbose output. Finally inspect compact stats.

State and persistence behavior: compaction eligibility is based on tracked reusable bytes. Progress stats should remain zero when compaction is skipped before rewrite work.

Dependencies and integration points: foreground compaction threshold logic, compact verbose messages, and data-source statistics. Tiered hook is skipped.

Risks: exact available bytes must fall between 1MB and 45MB for the scenarios. Warning text is regex-matched and thus part of the contract.

Test signals: expected compaction yields positive rewritten and expected pages; expected skip yields zero for both.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact06.py

Purpose: tests background compaction API validation, running state errors, run-once behavior, and history-store skip accounting.

Important APIs and types: `session.compact(None, "background=true")`, `turn_on_bg_compact`, `turn_off_bg_compact`, `get_bg_compaction_files_skipped`, `get_bg_compaction_running`, `session.get_last_error`, `errno.EINVAL`, and `wiredtiger.WT_BACKGROUND_COMPACT_ALREADY_RUNNING`.

Control flow: assert background compaction cannot be started on a specific URI, cannot disable with extra configuration, and cannot exclude non-table URIs. Enable background compaction, verify reconfiguration attempts fail with specific sub-error, wait for HS skip, disable, run once, wait for self-stop, then enable/disable again.

State and persistence behavior: no user data is compacted; state is the background compaction server lifecycle and cumulative skip counters.

Dependencies and integration points: compact server configuration parser, error reporting, helper methods in `compact_util`, and background compaction statistics. Tiered hook is skipped.

Risks: waits depend on background thread scheduling. Uses `assert` for some checks rather than `self.assert*`.

Test signals: expected API errors occur, last-error subcode matches already-running, skip counter advances as expected, and run-once server stops.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact07.py

Purpose: validates background compaction selects only files whose free space exceeds the configured threshold, and that foreground compaction can later compact a smaller-free-space file.

Important APIs and types: `compact_util`, `stat.conn.background_compact_files_tracked`, `stat.dsrc.block_reuse_bytes`, `get_files_compacted`, `get_pages_rewritten`, `turn_on_bg_compact`, and `dropUntilSuccess`.

Control flow: create one table with 20 percent deleted and two tables with 90 percent deleted; compare free-space MB; run background compaction once with threshold above the small table's free space; verify only large-free-space tables compacted; run foreground compaction on the small table; then restart background tracking and drop tables until tracking list shrinks.

State and persistence behavior: background compaction tracks metadata files, skips those below threshold, rewrites eligible files, and drops removed tables from tracking after idle expiration.

Dependencies and integration points: background compact debug mode, block reuse statistics, foreground compact helper, and table drop handling. Tiered hook is skipped.

Risks: loops wait on asynchronous background stats. A small bug in the free-space comparison loop references the last `uri` value but scenario intent is clear.

Test signals: small table has zero pages rewritten by background then positive pages after foreground; skipped and success stats are positive; tracking count eventually drops.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact08.py

Purpose: verifies compaction is not allowed for in-memory or read-only databases.

Important APIs and types: `session.compact`, `reopen_conn(config="in_memory=true")`, `reopen_conn(config="readonly=true")`, `expectedStdoutPattern`, and `wiredtiger.WiredTigerError`.

Control flow: create a file, reopen as in-memory and check foreground compaction prints unsupported message while background compaction raises with a specific warning; reopen read-only and verify compaction attempts raise operation-not-supported errors.

State and persistence behavior: this is API guard behavior, not data mutation. It ensures compaction does not run against configurations where rewriting files is impossible or invalid.

Dependencies and integration points: connection mode flags, foreground/background compaction API paths, and stdout/error message contracts.

Risks: final background read-only check calls `start_foreground_compaction` again, likely a copy/paste mistake, so the background path in read-only mode is not actually exercised.

Test signals: in-memory foreground warning observed, in-memory background raises, and read-only compact raises operation-not-supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact09.py

Purpose: tests background compaction exclude-list behavior.

Important APIs and types: `compact_util`, `stat.conn.background_compact_skipped_exclude`, `session.compact(None, background=true, exclude=...)`, `get_files_compacted`, and `get_pages_rewritten`.

Control flow: create two tables, populate and checkpoint, delete 90 percent from both, checkpoint, run background compaction once excluding both files and assert no files compacted; then run again excluding only the first file and verify only the second is compacted.

State and persistence behavior: background compaction should respect metadata/file-name exclude list and leave excluded table file pages unreclaimed.

Dependencies and integration points: background compaction, metadata file naming (`table:test_compact09_0.wt`), exclusion skip statistic, and helper stats. Tiered hook is skipped.

Risks: exclude strings use `.wt` file names derived from table URIs, so naming changes could break it. Asynchronous waits depend on background thread progress.

Test signals: exclude skip count equals expected cumulative values; first table has zero pages rewritten; second has positive pages rewritten.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact10.py

Purpose: verifies background compaction does not alter logical table contents by comparing full backups taken before and after compaction.

Important APIs and types: `backup_base`, `compact_util`, `take_full_backup`, `compare_backups`, `turn_on_bg_compact`, `get_bg_compaction_success`, and `get_bytes_recovered`.

Control flow: generate five tables, populate, checkpoint, delete half the rows, checkpoint, take full backup 1, run background compaction once with `free_space_target=1MB`, wait until all tables are processed and bytes recovered is positive, take full backup 2, then compare all table backups.

State and persistence behavior: compaction rewrites/reclaims blocks but must preserve table content. Backup comparison acts as a logical consistency check across compacted and uncompacted file layouts.

Dependencies and integration points: full backup support, background compaction, compact utility data population/deletion, and backup comparison. Tiered hook is skipped because both compaction and backup are unsupported/unsuitable.

Risks: waits on asynchronous background success count. Backup comparison must normalize physical differences or compare logical dumps as implemented by `backup_base`.

Test signals: bytes recovered is positive and every URI compares equal between pre- and post-compaction backups.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact11.py

Purpose: verifies background compaction does not incorrectly clear incremental backup block modification bits while compacting tables.

Important APIs and types: `backup_base`, `compact_util`, metadata cursor parsing of `blocks=...`, `take_full_backup`, `take_incr_backup`, `compare_backups`, and `turn_on_bg_compact`.

Control flow: create five tables, populate first half, checkpoint, take initial full backup for incremental chain, populate second half, checkpoint, delete half, checkpoint, take a reference full backup, parse block modification bitmaps, run background compaction once, and whenever recovered bytes changes take an incremental backup. Then compare each incremental backup against the reference full backup.

State and persistence behavior: compaction modifies blocks physically but must preserve incremental backup metadata so incremental backups remain logically complete.

Dependencies and integration points: backup ID management from `backup_base`, metadata block bitmap format, background compaction, and filesystem copy of backup homes.

Risks: `parse_blkmods` records bitmaps but the stored values are not asserted later. The test depends on bytes-recovered changes to trigger incremental backups.

Test signals: bytes recovered becomes positive and every incremental backup generated during compaction compares equal to the full reference for each URI.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact12.py

Purpose: intended to verify compaction rewrites pages in `WT_REF_DELETED` state that still have disk blocks, especially after a mix of obsolete deletes and non-obsolete fast truncate.

Important APIs and types: `compact_util`, `test_cc_base`, timestamped populate/remove/truncate, `wait_for_cc_to_run`, `stat.conn.rec_page_delete_fast`, `session.compact`, and `get_size`.

Control flow: the active test immediately skips due to FIXME-SLS-1890. The intended flow creates and populates timestamped data, deletes the first quarter and makes it obsolete, fast-truncates the last tenth, waits for checkpoint cleanup, verifies fast truncate pages, compacts, and checks that at least one quarter of file size is recovered.

State and persistence behavior: the intended persistence target is reclaiming disk blocks for deleted references after checkpoint cleanup and compaction.

Dependencies and integration points: checkpoint cleanup, fast truncate, foreground compaction, timestamps, and size accounting. Tiered hook would be skipped before the explicit skip.

Risks: currently disabled because it is not robust to eviction behavior. As a result it provides no active regression coverage until re-enabled.

Test signals: currently the only runtime signal is a skip. If enabled, it would require positive fast-truncate pages and size recovery above one quarter of pre-compact size.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact13.py

Purpose: checks that background compaction statistics/state reset after the server is disabled, so later eligible files can be compacted rather than treated as already processed/skipped.

Important APIs and types: `compact_util`, `turn_on_bg_compact`, `turn_off_bg_compact`, `get_bg_compaction_files_skipped`, `get_files_compacted`, and background compact free-space target.

Control flow: create two tables and populate them without deleting data, checkpoint, enable background compaction and wait until tables plus history store are skipped, disable it, delete 90 percent of both tables, checkpoint, re-enable background compaction, and wait until both files are compacted.

State and persistence behavior: background compaction server lifecycle should clear relevant per-run state so subsequent runs can process changed files.

Dependencies and integration points: background compaction asynchronous state, skip counters, compact utility deletion/population, and table stats. Tiered hook is skipped.

Risks: no explicit final assert beyond waiting for compaction count; timeout behavior depends on test harness. Imports `stat` but does not use it directly.

Test signals: the waits complete: initial skip count reaches `n_tables + 1`, and after deletion `get_files_compacted(uris)` reaches 2.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact14.py

Purpose: verifies background compaction skips small files that do not meet compaction thresholds.

Important APIs and types: `compact_util`, `turn_on_bg_compact`, `get_bg_compaction_files_skipped`, `session.checkpoint`, and table creation/population helpers.

Control flow: create a small table with one key, checkpoint it to disk, enable background compaction with `free_space_target=1MB`, then wait until at least one file is counted as skipped.

State and persistence behavior: no meaningful reclaimable space exists; the background server should inspect and skip rather than rewrite.

Dependencies and integration points: background compaction threshold logic and skip statistics. Tiered hook is skipped.

Risks: the test is wait-only with no explicit assert after the loop; a hang is the failure mode. The skipped file could be the tiny table or another small internal file depending on metadata traversal.

Test signals: `get_bg_compaction_files_skipped()` becomes nonzero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact15.py

Purpose: validates foreground compaction API requires a URI while allowing a valid URI.

Important APIs and types: `WiredTigerTestCase`, `session.compact`, `wiredtiger.WiredTigerError`, `assertRaisesWithMessage`, and `make_scenarios`.

Control flow: create a table, then either call `session.compact(self.uri, None)` for the valid scenario or call `session.compact(None, None)` and expect an error for the invalid scenario.

State and persistence behavior: this is API validation rather than data persistence. It protects the distinction between foreground compaction, which requires a target URI, and background compaction, which uses `None` with `background=true`.

Dependencies and integration points: compaction configuration parser and tiered hook behavior. Tiered hook is skipped.

Risks: valid URI scenario does not verify compaction work occurred; it only checks the call is accepted.

Test signals: valid URI compaction returns successfully; missing URI raises with `Compaction requires a URI`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compact16.py

Purpose: tests foreground compaction can reclaim space while checkpoints are running concurrently, without exhausting compact pass limits and leaving excessive reusable space.

Important APIs and types: `compact_util`, `checkpoint_thread`, `stat.conn.checkpoint_state`, `session.compact`, `get_bytes_avail_for_reuse`, and `get_size`.

Control flow: create and populate a million-key table, checkpoint, delete one quarter, reopen to force disk state, start a background checkpoint thread and wait for it to enter checkpoint state, run compact concurrently, stop the checkpoint thread, then calculate percentage available for reuse.

State and persistence behavior: compaction and checkpoint can contend over block movement and checkpoint writes. The expected result is successful space reclamation despite concurrent checkpoint activity.

Dependencies and integration points: foreground compaction, checkpoint threading, block reuse statistics, verbose compact output suppression, and compact helper population/deletion. Tiered hook is skipped.

Risks: high data volume and concurrent timing are expensive and potentially flaky. It uses a percentage threshold rather than exact file size.

Test signals: reusable bytes divided by file size is less than 20 percent after compact.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compact16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compat01.py

Purpose: tests compatibility release configuration effects on log versions, log removal, reconfiguration, restart, and active-transaction restrictions.

Important APIs and types: `WiredTigerTestCase`, `suite_subprocess.runWt(["printlog"])`, `conn.reconfigure`, `wiredtiger_open`, `SimpleDataSet`, `make_scenarios`, and filesystem log enumeration.

Control flow: scenario matrix creates a database with an initial compatibility release, writes enough records to generate logs, then either reconfigures compatibility in-place or restarts with a new release. `check_prev_lsn` runs `wt printlog` and searches for `prev_lsn` records to infer log version. It also checks whether old log files remain or are removed on downgrade. `test_reconfig_fail` verifies compatibility upgrade/downgrade is blocked by an active transaction while unrelated reconfigure is allowed.

State and persistence behavior: compatibility release controls log format version and whether newer logs can remain when downgrading. Restart path forces recovery and log cleanup.

Dependencies and integration points: command-line `wt printlog`, connection compatibility parser, logging subsystem, file retention, and scenario pruning.

Risks: large compatibility matrix is pruned but still broad. Log file naming and `printlog` output strings are part of the test contract.

Test signals: `prev_lsn` presence matches expected log version, log removal behavior matches downgrade rules, and active transaction blocks compatibility reconfigure with a quiescence error.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compat02.py

Purpose: tests compatibility `release`, `require_min`, and `require_max` configuration interactions, including future-version rejection and base config handling.

Important APIs and types: `WiredTigerTestCase`, `suite_subprocess`, `make_scenarios`, `wiredtiger_open`, `assertRaisesWithMessage`, and compatibility connection config fields.

Control flow: create a database at a scenario release level with logging enabled, write enough records to produce logs, close with checkpoint verbose enabled, build a restart config from `require_min`, `require_max`, and `release`, compute whether the combination should fail based on associated log-version numbers, and then assert either version incompatibility or successful reopen.

State and persistence behavior: existing database log version and configured compatibility constraints determine whether restart is allowed. The test protects compatibility gating before opening an incompatible home.

Dependencies and integration points: logging, compatibility version-to-log-version mapping, future version handling, config base true/false, and scenario pruning.

Risks: error cases are intentionally checked by generic version-incompatibility message because exact error ordering depends on library code. Future version constants must stay beyond current supported versions.

Test signals: restart raises `Version incompatibility detected` when computed invalid; otherwise `wiredtiger_open` succeeds and closes cleanly.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat02.py -->
