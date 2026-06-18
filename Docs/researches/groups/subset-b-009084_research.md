# subset-b-009084 Research

Grouped research for WiredTiger Python suite files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema11.py

## Purpose
Tests disaggregated layered schema checkpoint pickup when a follower has locally dropped a table that still exists in shared metadata from an older leader checkpoint.

## APIs, Types, And Functions
Defines `test_layered_schema11`, decorated with `@disagg_test_class`, using `gen_disagg_storages(..., disagg_only=True)`. Helper APIs cover `Connection.set_timestamp` for `stable_disaggregated_schema_epoch`, `Session.checkpoint`, `Session.publish` with `schema_epoch`, `disagg_advance_checkpoint`, metadata cursors on `file:WiredTigerShared.wt_stable`, and local cursor-open probes on stable-file URIs.

## Control Flow, State, And Persistence
The tests create layered tables, publish CREATE or REMOVE entries at schema epochs, checkpoint with stable epochs before or after drops, and then advance a follower checkpoint. State is split across leader shared metadata, follower local metadata, and the follower's schema operation queue. The key persistence behavior is that deferred REMOVE entries suppress recreation from shared metadata until the leader epoch advances enough to remove the table globally.

## Dependencies, Integration, Risks, And Test Signals
Integrates disaggregated helper storage, layered table metadata naming, publish epochs, and checkpoint metadata pickup. Risks are stale shared metadata, per-table isolation bugs, and incorrect handling of REMOVE followed by CREATE for the same URI. Assertions check presence or absence in local and shared metadata after each checkpoint advance.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup01.py

## Purpose
Exercises a basic disaggregated role swap where a follower becomes leader and writes new layered-table content that must be visible on both old and new leaders.

## APIs, Types, And Functions
Defines `test_layered_stepup01` under `@disagg_test_class`. It uses `wiredtiger_open` to open a follower home, `Session.create`, cursor inserts, `Session.checkpoint`, `disagg_switch_follower_and_leader`, and `disagg_advance_checkpoint`.

## Control Flow, State, And Persistence
The original leader creates a layered table and inserts three key families per item, checkpoints, then the helper switches leader/follower roles. The old follower inserts another three key families, checkpoints, and advances the old leader to the new checkpoint. Persistence is validated by scanning both connections and expecting six entries per logical item.

## Dependencies, Integration, Risks, And Test Signals
Depends on the disaggregated test hook and statistics logging; the test returns early on Darwin. The risk covered is role-switch state loss or partial checkpoint propagation. The main signal is full row-count equality on both connections after role inversion and checkpoint advancement.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup02.py

## Purpose
Verifies that layered tables can accept inserts under both initial leader and follower roles, and that a leader can reopen as follower in the same home while preserving data.

## APIs, Types, And Functions
Defines `test_layered_stepup02` with `conn_config()` returning `disaggregated=(role="<initial_role>")`. It uses `SimpleDataSet.populate`, `SimpleDataSet.check`, `Session.checkpoint`, `reopen_conn`, and `disagg_get_complete_checkpoint_meta`.

## Control Flow, State, And Persistence
Each scenario starts as either leader or follower, populates 1000 rows, and checks them. In the leader scenario, it checkpoints, reopens the same directory as follower with captured checkpoint metadata, appends another 1000 rows, and checks the expanded dataset. The persisted state is the disaggregated checkpoint metadata plus local table content across connection reopen.

## Dependencies, Integration, Risks, And Test Signals
Integrates `wtdataset.SimpleDataSet`, role scenarios, and disaggregated storage scenarios. It mainly protects against role-specific insert restrictions and incorrect checkpoint metadata reuse during same-home role changes. Test signals are `SimpleDataSet.check()` before and after reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup03.py

## Purpose
Regression test for leader-to-follower transition while eviction may encounter pages with pending split state produced by a checkpoint.

## APIs, Types, And Functions
Defines `test_layered_stepup03`, mixing in `eviction_util`. It uses `populate`, `Connection.set_timestamp`, `Session.checkpoint`, `Connection.reconfigure` for aggressive eviction and role transition, `disagg_get_complete_checkpoint_meta`, `close_conn`, and `open_conn`.

## Control Flow, State, And Persistence
The test writes 10,000 1KB rows into a 10MB cache, sets stable timestamp, checkpoints to create clean pages that may carry split metadata, makes eviction aggressive, captures checkpoint metadata, reconfigures the active connection from leader to follower, waits briefly, then reopens as follower with the checkpoint. The persisted checkpoint must remain readable after concurrent eviction/role-change pressure.

## Dependencies, Integration, Risks, And Test Signals
Depends on layered block manager `block_manager=disagg`, eviction utilities, and disaggregated checkpoint metadata. Risks include assertion failures or corrupt page state when eviction sees split pages during role transition. The final signal is a full cursor scan count equal to the inserted row count.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup04.py

## Purpose
Verifies that prepared transactions active on a follower at step-up time survive promotion and can be committed or rolled back correctly.

## APIs, Types, And Functions
Defines `test_layered_stepup04` with scenarios over commit versus rollback, prepare-in-checkpoint versus not, and single versus multi-table. Helpers open followers with `checkpoint_meta`, checkpoint arbitrary connections, and resolve prepared transactions through `timestamp_transaction`, `commit_transaction`, or `rollback_transaction`.

## Control Flow, State, And Persistence
Each test builds base committed data, optionally checkpoints a prepared transaction on the leader, closes the leader without a final checkpoint, opens a follower from exact checkpoint metadata, creates a matching live prepared transaction, promotes the follower via `reconfigure('disaggregated=(role="leader")')`, resolves it, checkpoints, and validates historical and post-resolution reads. Insert, update, and delete variants cover new keys, changed existing keys, and tombstones.

## Dependencies, Integration, Risks, And Test Signals
Depends on `preserve_prepared=true`, `precise_checkpoint=true`, prepared IDs, read timestamps, and layered tables. Risks are unresolved prepare state, conflict during step-up, incorrect timestamp visibility, or partial multi-table resolution. Assertions check read visibility at `ts=60` and `ts=200` for both commit and rollback outcomes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup05.py

## Purpose
Tests reuse of a reset layered cursor across follower-to-leader step-up with different checkpoint views and optional read timestamps.

## APIs, Types, And Functions
Defines `test_layered_stepup05`, scenarios over cursor operations (`next`, `prev`, `search`, `search_near`) and transaction modes. Helpers write timestamped checkpoints, dispatch the selected operation, and decide whether the run should see checkpoint 1 based on `read_ts`.

## Control Flow, State, And Persistence
The leader writes checkpoint 1, a follower advances to it and opens then resets a cursor, the leader writes checkpoint 2 with new keys and an updated value, the follower advances again, the leader closes, and the follower is promoted. The existing cursor is then used inside or outside a transaction. Persistence expectations are tied to stable checkpoint visibility and read timestamp selection.

## Dependencies, Integration, Risks, And Test Signals
Depends on disaggregated checkpoint pickup, cursor reset semantics, read timestamps, and layered cursor stable/ingest coordination. Risks include stale stable cursor state after step-up and incorrect checkpoint selection for reset cursors. Assertions validate exact keys and values for each operation under each transaction scenario.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup06.py

## Purpose
Regression test for step-up when two prepared sessions share one `prepared_id`, including a write-free prepared session and a writing prepared session.

## APIs, Types, And Functions
Defines `test_layered_stepup06`, skipped for the tiered hook and decorated for disaggregated storage. It uses `preserve_prepared=true`, `prepare_transaction(prepared_id=42)`, role reconfiguration, timestamped commit or rollback, and read-timestamp verification.

## Control Flow, State, And Persistence
The leader commits base keys and checkpoints, then closes without a final checkpoint. A follower opens from checkpoint metadata, starts `top_session` with no writes and `work_session` with keys 4 through 6, both prepared under the same ID. The follower steps up to leader, resolves both sessions, checkpoints, and checks base plus prepared-key visibility.

## Dependencies, Integration, Risks, And Test Signals
Exercises prepared transaction tracking across sessions during disaggregated promotion. The failure class is resolving only the first prepared session for an ID, leaving writes conflicted or uncommitted. Test signals are successful step-up, successful resolution of both sessions, and read timestamp checks for commit versus rollback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup08.py

## Purpose
Tests draining of the layered ingest table during follower-to-leader promotion for inserts, updates, removes, and remove/insert ordering.

## APIs, Types, And Functions
Defines `test_layered_stepup08` with small and large scenarios. It uses `helper_disagg.Oplog` to generate and apply logical operations, `disagg_advance_checkpoint`, connection role reconfiguration, stable timestamps, checkpoints, and direct transactions for a tombstone-chain edge case.

## Control Flow, State, And Persistence
Most tests create leader and follower copies of one layered table, apply oplog ranges, advance checkpoints, promote the follower, make the last oplog timestamp stable, and checkpoint to drain ingest state. Three tests intentionally call `skipTest` after the drain checkpoint because step-down is not supported. `test_drain_insert_remove_within_same_transaction` directly creates insert/delete/update chains on a follower and verifies the promotion checkpoint completes without consecutive tombstone failure.

## Dependencies, Integration, Risks, And Test Signals
Integrates Oplog replay, layered ingest, stable timestamps, and role transitions. Risks are duplicate tombstones, incorrect operation ordering, inability to abandon leader-side post-checkpoint changes, and unverified post-step-down reopen paths. Signals are Oplog checks before and after checkpoint advance plus successful drain checkpoint; some later validation remains skipped pending WT-15763.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup09.py

## Purpose
Verifies stable cursor lifecycle when a layered cursor opened on a follower is reused after that connection becomes leader.

## APIs, Types, And Functions
Defines module-level operation functions for insert, update, search, search_near, next, prev, remove, reserve, modify, and largest_key. The test class uses overwrite and no-overwrite cursor scenarios, connection statistics `layered_curs_open_stable` and `layered_curs_reopen_stable`, and role reconfiguration.

## Control Flow, State, And Persistence
One test advances the follower to a checkpoint, opens the stable cursor through a read, resets it, closes the old leader, promotes the follower, then uses the same cursor in a rollback transaction and expects a stable-cursor reopen. The second test never opens stable before step-up and expects first post-step-up use to open it once without a reopen. Inserted ingest data keeps the cursor active while stable state changes.

## Dependencies, Integration, Risks, And Test Signals
Depends on layered cursor statistics, disaggregated checkpoint advancement, and cursor operation semantics. Risks are leaving a read-only stable cursor active after promotion, reopening when unnecessary, or operation-specific cursor breakage. Signals are exact statistic counters after the selected operation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup10.py

## Purpose
Regression test for disaggregated btree handle state across two step-down and step-up cycles on the same connection.

## APIs, Types, And Functions
Defines `test_layered_stepup10` with small and large oplog sizes. It uses `Oplog`, layered table creation, role `Connection.reconfigure`, stable timestamps, and checkpoints with `precise_checkpoint=true` and `preserve_prepared=true`.

## Control Flow, State, And Persistence
The test writes and checkpoints a stable baseline, reconfigures to follower, applies batch 2 into ingest, promotes to leader and checkpoints to drain, then repeats follower write and leader drain for batch 3. It then verifies all three batches on the current leader. Persistence focus is clearing ingest and refreshing btree handles so stale readonly state does not corrupt checkpoint block-size accounting on the second cycle.

## Dependencies, Integration, Risks, And Test Signals
Integrates disaggregated btree handle lifecycle, oplog replay, and checkpoint size accounting. The risk is a handle left readonly or outdated across promotion, causing skipped checkpoints or block-size assertion failure. The signal is successful second cycle checkpoint and complete Oplog verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_stepup10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_leaf_delta_disagg01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_leaf_delta_disagg01.py

## Purpose
Validates that disaggregated leaf page deltas merge correctly with a base image across overlapping updates, inserted keys, empty values, prefix compression, and deletes.

## APIs, Types, And Functions
Defines `test_leaf_delta_disagg01` with prefix-compression scenarios. Helpers build table config with `block_manager=disagg`, read data-source statistics, insert/update byte values, delete keys, verify present and deleted keys, and reopen disaggregated connections to force base-plus-delta reconstruction.

## Control Flow, State, And Persistence
`verify_leaf_delta` writes a base page, checkpoints, then reopens three times and writes three update batches, expecting one leaf delta per batch. It reopens again and verifies that latest deltas override earlier deltas and base entries. Individual tests vary duplicate key sets, new keys, empty values, and deletion. Delete testing adds one more checkpoint and verifies tombstone persistence after reopen.

## Dependencies, Integration, Risks, And Test Signals
Depends on `page_delta`, reconciliation statistics, prefix compression statistics, byte value format, and disaggregated block manager. Risks are wrong merge precedence, empty-value unpacking bugs, delta/delete tombstone mishandling, or prefix compression divergence. Signals include exact delta counts, prefix compression stat checks, and value/WT_NOTFOUND assertions after reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_leaf_delta_disagg01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_leaf_delta_disagg02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_leaf_delta_disagg02.py

## Purpose
Tests the `page_delta.delete_pct` threshold that forces reconciliation to write a full leaf page instead of a delta when too many disk-image keys are removed.

## APIs, Types, And Functions
Defines `test_leaf_delta_disagg02` under disaggregated storage scenarios. It uses `page_delta=(delta_pct=1000,delete_pct=50)`, data-source stats `rec_page_delta_leaf` and `rec_page_delta_rejected_delete_threshold`, timestamped per-key transactions, and read timestamp verification.

## Control Flow, State, And Persistence
`populate` creates ten deterministic keys on one leaf page and checkpoints at a base timestamp. One test deletes seven keys, advances oldest/stable timestamps, checkpoints, and expects full-page output with delete-threshold rejection. The other deletes three keys and updates four, then expects a delta. Both verify present/absent keys before and after reopening the disaggregated connection.

## Dependencies, Integration, Risks, And Test Signals
Depends on small page layout, deterministic key widths, disaggregated leaf-page delta support, and timestamp visibility. Risks are off-by-one threshold behavior, writing tombstone-heavy deltas when full pages are required, or losing data across restart. Signals are stats counters plus read-timestamp searches after restart.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_leaf_delta_disagg02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_live_restore01.py

## Purpose
Validates live restore connection compatibility rules and configuration error handling.

## APIs, Types, And Functions
Defines `test_live_restore01` extending `backup_base`. Helpers `expect_success`, `expect_failure`, and `expect_failure_rounds` open `DEST` with supplied configs, close or assert `WiredTigerError`, and reset the destination directory. The test uses `take_full_backup` to produce `SOURCE`.

## Control Flow, State, And Persistence
After taking a full backup, the test removes all home files except `SOURCE` and output logs, creates `DEST`, and runs valid and invalid live restore opens. It covers Windows unsupported behavior, in-memory compatibility, empty and missing paths, thread bounds, readonly, salvage, statistics disabled, disaggregated incompatibility, non-live reopen while restore is in progress, and statistics reconfigure rejection.

## Dependencies, Integration, Risks, And Test Signals
Depends on backup infrastructure, filesystem cleanup, live restore config parsing, and exact error-message patterns. Risks include accepting incompatible modes or allowing stats to be disabled during active restore. Signals are successful opens for valid configs and regex-matched errors for invalid configs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_live_restore02.py

## Purpose
Exercises live restore background migration until completion while source collections are compared with the destination.

## APIs, Types, And Functions
Defines `test_live_restore02` extending `backup_base`, with scenarios over key format and `read_size`. It uses `SimpleDataSet`, `take_full_backup`, `open_conn` with `live_restore`, `statistics:` cursor for `live_restore_state`, and `WT_LIVE_RESTORE_COMPLETE`.

## Control Flow, State, And Persistence
The test populates three files, checkpoints, backs up to `SOURCE`, deletes local home files, opens `DEST` with one live restore thread, and loops for up to 120 seconds. During the loop it creates extra files to stress file creation while migration runs. After completion, it opens `SOURCE` separately and compares every key/value in the restored URIs. It also asserts no `.stop` files remain.

## Dependencies, Integration, Risks, And Test Signals
Depends on Unix live restore support, verbose progress logs, statistics, and backup correctness. Risks are migration stalls, file-create assertions during restore, partial data copy, and leaked stop markers. Signals are completion state, row-by-row equality against `SOURCE`, and absence of stop files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_live_restore03.py

## Purpose
Checks that data-source file size statistics work for objects that still exist only in the live restore source directory.

## APIs, Types, And Functions
Defines `test_live_restore03` extending `backup_base`. It uses `SimpleDataSet`, backup creation, live restore with `threads_max=0`, and `statistics:<uri>` cursors with `statistics=(size)` to read `stat.dsrc.block_size`.

## Control Flow, State, And Persistence
The test creates one `file:` and one `table:` object, checkpoints, backs up to `SOURCE`, removes the original home files, opens `DEST` in live restore mode with no background threads, and queries block-size statistics for both URIs. Because no background migration is running, the statistics path must fetch size information through live restore's source-file view.

## Dependencies, Integration, Risks, And Test Signals
Depends on Unix live restore and statistics size mode. Risks include returning zero or failing when metadata exists locally but the file has not migrated. Test signal is `block_size > 0` for both file and table URI statistics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_live_restore04.py

## Purpose
Tests `wt` utility behavior against an unfinished live restore home, including dump, verify, printlog, and error handling without a live restore source path.

## APIs, Types, And Functions
Defines `test_live_restore04` extending `backup_base`, with column and row-integer scenarios. It uses `runWt`, `SimpleDataSet`, `take_full_backup`, `filecmp.cmp`, and the utility `-l SOURCE` live restore option.

## Control Flow, State, And Persistence
The test creates three logged files, dumps original utility output, backs up to `SOURCE`, removes home files except `SOURCE` and utility output, opens and closes a `threads_max=0` live restore connection to leave migration incomplete, then runs `wt dump` without `-l` expecting an error. It runs `wt -l SOURCE printlog`, then dumps and verifies each file through live restore and compares dumps to originals.

## Dependencies, Integration, Risks, And Test Signals
Depends on Unix live restore, the external `wt` utility, logged homes, and backup layout. Risks are utility commands bypassing live restore rules, failing to read source-backed files, or mismatched dump output. Signals are non-empty error/printlog files, successful dump/verify, and byte-identical dump comparisons.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_live_restore05.py

## Purpose
Reproduces and guards against duplicate `live_restore=` metadata entries in a live restore home.

## APIs, Types, And Functions
Defines `test_live_restore05` extending `backup_base`, with row-integer and column-store scenarios. It uses `SimpleDataSet`, `take_full_backup`, `open_conn` with `live_restore`, and `runWt` to dump `file:WiredTiger.wt`.

## Control Flow, State, And Persistence
The test creates one collection, checkpoints, backs up to `SOURCE`, removes home files, opens `DEST` with live restore and no background migration threads, dumps the metadata file through `wt -l SOURCE`, and scans the dump text. For each metadata line containing `live_restore=`, it asserts there is not another occurrence later in the same line.

## Dependencies, Integration, Risks, And Test Signals
Depends on metadata rewrite behavior during live restore and utility dump output. The risk is repeated config insertion causing malformed or ambiguous metadata. The signal is textual absence of duplicate `live_restore=` substrings in dumped `WiredTiger.wt` metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_live_restore06.py

## Purpose
Ensures backups taken from live restore destinations clean `nbits=-1` metadata and produce reusable backup metadata with `nbits=0`.

## APIs, Types, And Functions
Defines `test_live_restore06` extending `backup_base`. It uses `SimpleDataSet`, live restore statistics, file manager close settings, timing stress `live_restore_clean_up`, backup cursors, and metadata cursors.

## Control Flow, State, And Persistence
The test creates three source files, backs up to `SOURCE`, opens `DEST` with one live restore thread and aggressive sweep settings, loops until `WT_LIVE_RESTORE_COMPLETE`, then verifies destination metadata includes `nbits=-1` for files. It then runs `do_backup_test` twice, once from complete live restore mode and once from non-live restore mode, checking `WiredTiger.backup` omits `nbits=-1` and reopened backup metadata contains `nbits=0`.

## Dependencies, Integration, Risks, And Test Signals
Depends on live restore cleanup, sweep timing, backup metadata export, and restart. Risks are leaking placeholder allocation metadata into backups or reopening backups with live restore-only metadata. Signals are completion state, metadata string assertions, and successful backup reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_live_restore07.py

## Purpose
Checks that live restore from an empty source directory is rejected.

## APIs, Types, And Functions
Defines `test_live_restore07` with unused key-format scenarios. It uses `close_conn`, `os.mkdir`, `open_conn`, and `assertRaisesWithMessage` for `wiredtiger.WiredTigerError`.

## Control Flow, State, And Persistence
On non-Windows platforms, the test closes the default connection, creates empty `SOURCE` and `DEST` directories, then tries to open `DEST` with `live_restore=(enabled=true,path="SOURCE")`. No database state should be created through a successful restore because an empty source has no valid WiredTiger metadata to restore.

## Dependencies, Integration, Risks, And Test Signals
Depends on live restore startup validation and filesystem directory state. The risk is accepting an empty restore source and later failing with less clear metadata errors. The signal is the specific error message `Source directory is empty. Nothing to restore!`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_live_restore08.py

## Purpose
Tests that bulk cursor usage is disallowed on files migrated by live restore after restore completion.

## APIs, Types, And Functions
Defines `test_live_restore08` extending `backup_base`. Helpers read `live_restore_state`, wait for completion, and populate a backup containing a normal file and an empty `file:bulk`. It uses `open_cursor(..., "bulk")` for the final error assertion.

## Control Flow, State, And Persistence
The test creates `SOURCE` with one populated file and one newly created bulk target, opens `DEST` with one live restore thread and small read size, waits until `WT_LIVE_RESTORE_COMPLETE`, then attempts to open a bulk cursor on the migrated `file:bulk`. Since the object is no longer newly created in the destination, bulk load must be rejected.

## Dependencies, Integration, Risks, And Test Signals
Depends on live restore migration state and bulk cursor eligibility rules. Risks include allowing bulk load to overwrite restored objects or classifying migrated empty files as new objects. Test signal is the expected `bulk-load is only supported on newly created objects` error.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_live_restore08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_load01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_load01.py

## Purpose
Smoke-tests dynamic `load_control` reconfiguration and validation bounds.

## APIs, Types, And Functions
Defines `test_load01` using `conn_config="cache_size=50MB,statistics=(all)"`. The test calls `Connection.reconfigure` with `load_control=[enable=...,control_threshold=...]`, table cursors, and `assertRaisesException` for invalid configs.

## Control Flow, State, And Persistence
The test creates a table, writes baseline rows, loops over valid disabled/enabled thresholds from 10 through 100, reconfigures the connection, writes more rows, and confirms the connection remains usable by scanning row count. It then tries threshold 0, negative, and too-large values and expects `Invalid argument`. Table state is only a liveness signal for reconfiguration.

## Dependencies, Integration, Risks, And Test Signals
Depends on runtime config parsing and connection reconfiguration. Risks are accepting invalid thresholds or requiring restart for load control changes. Signals are successful post-reconfigure reads/writes and failures for invalid thresholds with stderr ignored afterward.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_load01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_log03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_log03.py

## Purpose
Tests `log.os_cache_dirty_pct` by measuring increased fsync activity as the dirty limit becomes more aggressive.

## APIs, Types, And Functions
Defines `test_log03` with custom `setUpConnectionOpen` and `setUpSessionOpen` returning `None` so each subtest opens its own home. Helpers populate 20,000 large string rows, read `stat.conn.fsync_io`, and open connections with variable `log=(file_max=...,os_cache_dirty_pct=...)`.

## Control Flow, State, And Persistence
`test_dirty_max` first establishes a baseline with 12MB log files and dirty pct 0. It recreates `HOME` for each run, writes enough data to produce log traffic, closes the connection, and compares fsync stats for dirty percentages 50, 33, 25, and 20. Lower percentages should trigger increasingly more fsyncs.

## Dependencies, Integration, Risks, And Test Signals
Depends on statistics fast mode, logging, OS-cache dirty threshold behavior, and large data writes. Risks include flaky fsync counts from environment variance, so expected increases are conservative. Signals are `assertGreater(result, baseline + increase)` for each threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_log03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_log04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_log04.py

## Purpose
Smoke-tests interactions among logging, timestamps, non-logged objects, checkpoints, and rollback to stable.

## APIs, Types, And Functions
Defines `test_log04` with logged connection config, row/column scenarios, and checkpoint/no-checkpoint scenarios. It uses `SimpleDataSet`, `Connection.set_timestamp`, transaction commit timestamps, read timestamp checks, optional `Session.checkpoint`, and `Connection.rollback_to_stable`.

## Control Flow, State, And Persistence
The test creates one logged table, one non-logged timestamped table, and one non-logged table updated without timestamps. It verifies initial data, rolls back an uncommitted update, commits at timestamps 20 and 30, advances stable to 25, optionally checkpoints, and runs rollback to stable. Logged and non-timestamped tables ignore timestamp rollback, while non-logged timestamped data rolls back the timestamp-30 update.

## Dependencies, Integration, Risks, And Test Signals
Depends on timestamp hook prevention, logging enabled at connection level, per-object `log=(enabled=false)`, and RTS. Risks are applying timestamps to logged data or failing to roll back non-logged timestamped data. Signals are read-timestamp value assertions before and after rollback to stable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_log04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_log05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_log05.py

## Purpose
Regression test for recovery from oversized corrupted log record lengths without generating duplicate log files.

## APIs, Types, And Functions
Defines `test_log05` with logging enabled. Helpers parse `checkpoint_lsn` from `WiredTiger.turtle`, seek into `WiredTigerLog.0000000%03d`, and overwrite the record length with `UINT32_MAX` using `struct.pack`. It uses `WiredTigerCursor` and expected stdout matching.

## Control Flow, State, And Persistence
The test creates data in one transaction, then repeats 20 cycles: close the connection, corrupt the next log file at the checkpoint LSN, and reopen expecting a corrupted-length recovery message. After the cycles, it counts existing log files and asserts no more than two remain. Recovery should salvage and continue rather than proliferating log files.

## Dependencies, Integration, Risks, And Test Signals
Depends on turtle file format, log naming, little-endian record length, and recovery salvage. Risks are brittle offsets if metadata format changes, failed recovery, or disk growth from duplicate logs. Signals are expected stdout pattern and final log count bound.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_log05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_log06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_log06.py

## Purpose
Reproduces partial log record recovery where a 128-byte aligned zero-length block contains non-zero bytes and must be truncated safely.

## APIs, Types, And Functions
Defines `test_log06` with scenarios for non-zero record length bytes and flag bytes. It uses `copy_wiredtiger_home`, appends raw blocks to all copied log files, opens the copied home through `setUpConnectionOpen`, and matches recovery notice text.

## Control Flow, State, And Persistence
Phase 1 writes `value_a` and checkpoints. Phase 2 writes `value_b` to the WAL without checkpointing. Phase 3 copies the home while open, appends the corrupt block to copied logs, and closes the original. Phase 4 opens the copy expecting recovery notices and truncation. Phase 5 verifies every key has `value_b`, proving WAL replay before the partial block succeeded.

## Dependencies, Integration, Risks, And Test Signals
Depends on log alignment, transaction sync method `none`, crash-copy semantics, and recovery validation. Risks are over-truncating valid log content or failing to detect holes. Signals are expected NOTICE patterns and all rows preserving the post-checkpoint value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_log06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor01.py

## Purpose
Basic smoke test for metadata cursor iteration and search over `metadata:` and `metadata:create`.

## APIs, Types, And Functions
Defines `test_metadata_cursor01` with scenarios for plain and create metadata cursors. Helpers generate keys/values, assert cursor key/value are unset, and wrap `Session.create` for better diagnostics.

## Control Flow, State, And Persistence
Each test creates a simple table, opens the selected metadata cursor, and verifies cursor state before iteration. Forward and backward tests iterate until `WT_NOTFOUND` and ensure keys and values are available while positioned. The search test fetches `metadata:` itself and the created table entry, checking for `key_format` in metadata strings. Metadata state is persisted in the WiredTiger metadata table.

## Dependencies, Integration, Risks, And Test Signals
Depends on metadata cursor URI variants and standard cursor reset semantics. Risks are invalid positioned/unpositioned cursor state, incomplete create metadata expansion, or missing table metadata. Signals are key/value availability checks, final `WT_NOTFOUND`, and substring checks in metadata values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor02.py

## Purpose
Tests metadata cursor behavior when table metadata is incomplete because a column group or backing file has been dropped independently.

## APIs, Types, And Functions
Defines `test_metadata_cursor02`, skipped for disaggregated and tiered hooks. It uses scenarios for `metadata:` versus `metadata:create` and invalidation by `colgroup` versus `file` drops. Helpers reopen, force-drop existing tables, and recreate three tables.

## Control Flow, State, And Persistence
For each table, the test recreates all three, then drops either the table's column group or file URI to make one table incomplete. It opens the metadata cursor, counts entries starting with `table:`, and for create cursors checks captured error output for missing metadata information. Plain metadata still lists all table entries; create metadata omits the invalid one.

## Dependencies, Integration, Risks, And Test Signals
Depends on attached storage internals, metadata cleanup messages, and `metadata:create` expansion. Risks are crashing on incomplete metadata or returning invalid expanded entries. Signals are count differences between cursor modes and expected diagnostic patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor03.py

## Purpose
Exercises atomic schema create/drop logging paths for files, simple tables, column groups, and indexes.

## APIs, Types, And Functions
Defines `test_metadata03` with logging enabled and scenarios for file, table with column group, table with index, and simple table. Helpers count whole log records through a `log:` cursor and provide `verify_logrecs`.

## Control Flow, State, And Persistence
The test counts existing log records, creates the main URI with optional column definitions, optionally creates a column group or index, then drops the main URI. Intended behavior is that schema operations log as atomic records rather than many individual records. The current `verify_logrecs` assertion is commented out pending WT-3965, so the test walks the log and performs the operations but does not enforce the expected count.

## Dependencies, Integration, Risks, And Test Signals
Depends on the log cursor, schema metadata logging, and table/index/column-group creation. The major risk is reduced regression strength because the count assertion is disabled. Existing signals are operation success and log cursor traversal, not strict atomicity validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor04.py

## Purpose
Checks that `metadata:create` exposes expected logging configuration for simple and complex tables.

## APIs, Types, And Functions
Defines `test_metadata04` with logged connection config. Helper `check_meta` opens `metadata:create`, searches a URI, prints metadata, and optionally asserts `log=(enabled=false)` is present.

## Control Flow, State, And Persistence
The complex-table test creates a table with `log=(enabled=false)`, column definitions, a column group, and an index, then checks the column group and index expanded metadata include logging disabled while the top-level table is printed but not checked. The simple-table test creates one non-logged table and asserts its create metadata includes `log=(enabled=false)`.

## Dependencies, Integration, Risks, And Test Signals
Depends on metadata create cursor expansion and schema configuration propagation to indexes and column groups. Risks include losing per-object log settings in generated metadata. Signals are direct metadata substring assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_modify01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_modify01.py

## Purpose
Stress-tests the modify API by applying generated modify vectors and verifying they transform old values into expected new values.

## APIs, Types, And Functions
Defines `test_modify01` with value format scenarios `u` and `S`. It uses deterministic `random.Random(42)`, `modify_utils.create_mods`, `Cursor.modify`, transaction timestamps, and cursor reads.

## Control Flow, State, And Persistence
For 1000 keys, the test randomly chooses value size, repeated pattern count, number of modifications, and max difference. `create_mods` returns an old value, modify list, and expected new value. The test inserts the old value, begins a transaction, applies `modify`, commits with a timestamp, and verifies reading the key returns the expected new value.

## Dependencies, Integration, Risks, And Test Signals
Depends on modify vector generation and WiredTiger's ability to apply add/remove/replace edits for both byte-array and string values. Risks are incorrect diff application, timestamp incompatibility under disaggregated hooks, or generator assumptions. Signals are non-null modify lists and exact post-commit value equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_modify01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_modify02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_modify02.py

## Purpose
Verifies that `Cursor.modify` fails when no base value exists for the target key.

## APIs, Types, And Functions
Defines `test_modify02` with value format scenarios `u` and `S`. It uses deterministic `random.Random(43)`, `modify_utils.create_mods`, `Cursor.modify`, and `wiredtiger.WT_NOTFOUND`.

## Control Flow, State, And Persistence
For 1000 generated cases, the test creates modify vectors but intentionally does not insert the old/base value into the table. Inside a transaction it sets only the key, calls `modify`, expects `WT_NOTFOUND`, and commits. No successful data modification should be persisted for those keys.

## Dependencies, Integration, Risks, And Test Signals
Depends on the modify API's requirement for an existing base value and on consistent generated modify vectors. Risks include accidentally creating values from deltas without a base or returning success for missing keys. The signal is exact `WT_NOTFOUND` for each attempted modify.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_modify02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_overwrite.py -->
# sources/storage-engines/wiredtiger/test/suite/test_overwrite.py

## Purpose
Tests cursor `overwrite=false` semantics for insert, remove, and update across files, simple tables, complex tables, indexes, and key formats.

## APIs, Types, And Functions
Defines `test_overwrite` with scenarios over dataset type, key format, and several syntactically different cursor configs that all disable overwrite. It uses `SimpleDataSet`, `ComplexDataSet`, `SimpleIndexDataSet`, duplicate cursors, and `wiredtiger.WT_NOTFOUND`.

## Control Flow, State, And Persistence
Each method populates 100 rows and opens cursors with and without overwrite. Insert tests fail on existing keys with overwrite off, allow duplicate cursor override when supported, and allow inserts on new keys. Remove tests show overwrite no longer changes missing-key behavior: missing removes fail in both modes. Update tests fail on missing keys with overwrite off but upsert with overwrite on.

## Dependencies, Integration, Risks, And Test Signals
Depends on dataset helpers and cursor config parsing, including fast-path and normal parser cases. Risks are regressions in overwrite config parsing, remove semantics, or layered duplicate cursor support. Signals are exceptions, zero returns, and `WT_NOTFOUND` for each operation class.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_overwrite.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_ovfl01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_ovfl01.py

## Purpose
Regression test that bulk insert with overflow keys does not leave orphaned overflow items when reconciliation page split writes fail.

## APIs, Types, And Functions
Defines `test_ovfl01` with small leaf key/value limits, `timing_stress_for_test=(failpoint_rec_split_write)`, bulk cursor insertion, `Connection.reconfigure`, `Session.checkpoint`, and `Session.verify`.

## Control Flow, State, And Persistence
The test creates a string-key table where 1KB keys and values exceed overflow thresholds, bulk inserts 10,000 sorted records, tolerates `EBUSY` insert failures from the failpoint, disables the failpoint before closing the cursor, checkpoints, and verifies on-disk contents. Overflow pages and split state are persisted through reconciliation.

## Dependencies, Integration, Risks, And Test Signals
Depends on overflow key/value handling, bulk load, reconciliation split failpoint, and verify. Risks are orphaned overflow keys after partial split failures or unexpected errors other than `EBUSY`. Signals are successful checkpoint and `session.verify`, with expected stdout pattern ignored if the failpoint fires.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_ovfl01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_pack.py -->
# sources/storage-engines/wiredtiger/test/suite/test_pack.py

## Purpose
Tests public packing/unpacking behavior for multiple value formats through table storage and index lookup.

## APIs, Types, And Functions
Defines `test_pack` with helper `check(fmt, *v)`. It creates a table with value format `fmt`, creates an inverse index on all value columns, inserts one key/value tuple, reads the table value, and searches the index by value.

## Control Flow, State, And Persistence
`test_packing` calls `check` for integer groups, fixed and variable strings, strings containing nul padding, byte-array formats, empty byte arrays, and signed string formats. Each generated table and index persists one record, then the test validates both direct table unpacking and index key packing.

## Dependencies, Integration, Risks, And Test Signals
Depends on WiredTiger format strings, column definitions, index packing, and Python API return conventions for single versus multiple values. Risks are mismatched fixed-size packing, null/empty byte handling, or secondary index encoding divergence. Signals are equality of unpacked values and successful inverse index lookup returning key 1234.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_pack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prefetch01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prefetch01.py

## Purpose
Validates basic prefetch configuration compatibility between connection-level availability/default settings and session-level enablement.

## APIs, Types, And Functions
Defines `test_prefetch01` with scenarios over `prefetch.available`, `prefetch.default`, and optional session config `prefetch=(enabled=...)`. It uses `helper.copy_wiredtiger_home`, `wiredtiger_open`, `Connection.open_session`, and error pattern matching.

## Control Flow, State, And Persistence
The test copies the current home to a new directory, constructs connection and session configs, and then checks three cases: unavailable plus default-on must fail at connection open, unavailable plus session-enabled must fail at session open, and all other combinations open a session and close cleanly. State is limited to copied home metadata and configuration runtime state.

## Dependencies, Integration, Risks, And Test Signals
Depends on prefetch config parsing and copied-home open semantics. Risks are enabling prefetch when globally unavailable or rejecting valid disabled/default combinations. Signals are expected `pre-fetching cannot be enabled` errors or successful session close.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prefetch01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prefetch02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prefetch02.py

## Purpose
Runs traversal and verify scenarios expected to trigger prefetch, and confirms statistics move only when prefetch is enabled.

## APIs, Types, And Functions
Defines `PrefetchStats` and `test_prefetch02`, mixing in `suite_subprocess`. It uses connection/session prefetch configs, statistics `prefetch_pages_queued`, `prefetch_attempts`, `prefetch_attempts_succeeded`, `prefetch_pages_read`, `verifyUntilSuccess`, and large fixed-page datasets.

## Control Flow, State, And Persistence
The test copies the home, opens a setup connection with selected config, populates 100,000 rows in a small-page file, checkpoints, closes to clear cache, and reopens. Traversal scenarios walk half the keyspace, snapshot stats, finish forward or backward traversal, then assert stats increased or remained zero. Verify scenarios run verification and assert the same prefetch/stat behavior.

## Dependencies, Integration, Risks, And Test Signals
Depends on disk reads rather than cache hits, small page layout, prefetch worker activity, and statistics. Risks are flaky nondecreasing stats, unavailable prefetch incorrectly doing work, or verify not using prefetch. Signals are stat snapshots and zero-stat assertions; some checks use `GreaterEqual` pending stronger WT-12193 assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prefetch02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prefetch03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prefetch03.py

## Purpose
Verifies prefetch is incompatible with in-memory databases and logs a compatibility message instead of enabling it.

## APIs, Types, And Functions
Defines `test_prefetch03` with default and in-memory connection config scenarios. It uses `reopen_conn` and `expectedStdoutPattern` for the in-memory warning.

## Control Flow, State, And Persistence
The default scenario reopens the current home with prefetch available/default-on and verbose prefetch logging. The in-memory scenario reopens with `in_memory=true` plus the same prefetch settings and expects a stdout message saying the configuration is incompatible. No table state is created; the test is purely connection configuration behavior.

## Dependencies, Integration, Risks, And Test Signals
Depends on connection config handling and verbose prefetch messaging. Risks are enabling prefetch in in-memory mode or failing the open instead of disabling/logging. Signal is successful reopen plus expected warning for the in-memory path.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prefetch03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare01.py

## Purpose
Tests basic prepared transaction visibility across isolation levels, checkpoints, and a read-timestamp-after-prepare warning.

## APIs, Types, And Functions
Defines `test_prepare01` with row/column and file/table scenarios, plus `test_prepare01_read_ts`. Helpers count cursor-visible records, create named checkpoints, check transactions under read-uncommitted, snapshot, and read-committed isolation, and compare committed versus total rows.

## Control Flow, State, And Persistence
`test_visibility` inserts 1000 rows in transactions, periodically checks visibility before preparing and committing, and confirms prepared but uncommitted rows are visible only to the owning cursor/read-uncommitted while checkpoints include committed rows. Final prepare/commit makes all rows visible. The second class prepares a transaction then attempts to set a read timestamp, expecting a silently ignored warning.

## Dependencies, Integration, Risks, And Test Signals
Depends on prepare timestamps, durable/commit timestamps, checkpoint cursors, isolation semantics, and column-store phantom filtering. Risks are leaking prepared updates to snapshot/read-committed readers or checkpointing uncommitted prepared data. Signals are record counts per isolation/checkpoint and expected stderr for ignored read timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare02.py

## Purpose
Ensures forbidden `WT_SESSION` APIs return the expected errors while a transaction is prepared, and permitted operations still work.

## APIs, Types, And Functions
Defines `test_prepare02`, skipped for tiered storage and mixed with `suite_subprocess`. It uses session APIs including `reconfigure`, `open_cursor`, `alter`, `create`, `compact`, `drop`, `log_flush`, `reset`, `salvage`, `truncate`, `verify`, `begin_transaction`, `prepare_transaction`, `checkpoint`, `breakpoint`, commit, rollback, and close.

## Control Flow, State, And Persistence
The test creates a table, writes one key in a transaction, prepares it, then calls many session methods and asserts `not permitted in a prepared transaction` or `not permitted in a running transaction` where applicable. It verifies these errors do not poison the transaction by committing successfully. It then separately checks commit after prepare, timestamp-setting after prepare, rollback after prepare, and close after prepare.

## Dependencies, Integration, Risks, And Test Signals
Depends on prepared transaction state-machine enforcement and Python API exception messages. Risks are allowing schema/maintenance operations while prepared or setting transaction error flags for rejected operations. Signals are exact error regexes and successful permitted resolution paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare03.py

## Purpose
Checks that cursor APIs are rejected in prepared transaction state and still work normally outside that state.

## APIs, Types, And Functions
Defines `test_prepare03` with file/table and row/column scenarios. Helpers generate row or record-number keys, generate values, and assert unpositioned cursor key/value errors. Tested cursor APIs include `insert`, `next`, `get_key`, `get_value`, `prev`, `search`, `update`, `remove`, `reserve`, `reconfigure`, and `search_near`.

## Control Flow, State, And Persistence
The test creates a table, opens a cursor, then for inserts and cursor traversal repeatedly begins a transaction, prepares it, asserts the selected cursor operation fails with prepared-state error, resolves the transaction, and performs the corresponding operation outside prepared state. It verifies forward and backward iteration order and exercises update/remove after a prepared-state rejection.

## Dependencies, Integration, Risks, And Test Signals
Depends on cursor-state enforcement during prepared transactions and normal cursor behavior afterward. It skips a URI equality assertion under the disagg hook because URIs may be rewritten to layered. Risks are allowing cursor reads/writes in prepared state or leaving the cursor corrupted after rejected calls. Signals are expected exceptions plus successful normal operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare04.py

## Purpose
Tests prepared update conflict behavior for readers and writers with different read timestamps and `ignore_prepare` settings.

## APIs, Types, And Functions
Defines `test_prepare04` with row/column scenarios, read-before/read-after/no timestamp scenarios, and `ignore_prepare` true/false scenarios. It uses `prepare_transaction`, alternate sessions, cursor search/update, conflict regexes, and timestamped commit.

## Control Flow, State, And Persistence
The test creates a table, commits a base value at timestamp 100, advances oldest to 100, then prepares an update at timestamp 200. A second session begins with the scenario transaction config. If the reader is after the prepare timestamp and `ignore_prepare=false`, search must raise a prepared conflict; otherwise it sees the old value. A write attempt from the second session must always detect a concurrent operation conflict. The prepared update is then committed.

## Dependencies, Integration, Risks, And Test Signals
Depends on timestamp visibility, prepared conflict detection, and `ignore_prepare`. Risks are hiding prepared conflicts from readers that should block or allowing conflicting writers. Signals are expected prepared-conflict and concurrent-conflict errors plus old-value visibility in allowed cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare05.py

## Purpose
Validates timestamp ordering rules for prepare, commit, and durable timestamps.

## APIs, Types, And Functions
Defines `test_prepare05` with column and row-integer scenarios. It uses `Connection.set_timestamp`, `Session.prepare_transaction`, `Session.timestamp_transaction`, cursor writes, and error-message assertions.

## Control Flow, State, And Persistence
The test creates a table, sets stable timestamp 2, then verifies prepare timestamp 1 and 2 are rejected because they are not newer than stable. It confirms prepare timestamp 3 can be committed with matching commit/durable timestamps. It then verifies setting commit timestamp before prepare is illegal, including when prepare timestamp is already set through `timestamp_transaction`. Finally it confirms a transaction with write data can commit with commit and durable timestamps equal to the prepare timestamp.

## Dependencies, Integration, Risks, And Test Signals
Depends on prepared timestamp validation and timestamp API state ordering. Risks are accepting prepare timestamps at or before stable, or allowing commit timestamp before prepare. Signals are exact error messages and successful legal commit cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare06.py

## Purpose
Tests `roundup_timestamps=(prepared=true)` behavior for prepared transactions whose supplied timestamps are older than stable or oldest timestamps.

## APIs, Types, And Functions
Defines `test_prepare06` with column and row-integer scenarios. It uses `Connection.set_timestamp`, `Session.begin_transaction` with roundup config, `prepare_transaction`, `timestamp_transaction`, and commit.

## Control Flow, State, And Persistence
The test sets oldest timestamp 20 and stable timestamp 30, first confirms a prepare timestamp 10 is rejected without roundup. It then begins transactions with prepared timestamp rounding enabled and supplies prepare/commit timestamps earlier than stable and even earlier than oldest, while durable timestamp is 35. Both rounded prepared transactions must commit successfully.

## Dependencies, Integration, Risks, And Test Signals
Depends on timestamp rounding rules for prepared transactions. Risks are rejecting legal rounded transactions or failing to round prepare/commit timestamps consistently. Signals are the initial expected rejection and successful commits for both roundup cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare07.py

## Purpose
Ensures an active prepared transaction older than oldest timestamp does not make its update visible in backups after oldest/stable advance.

## APIs, Types, And Functions
Defines `test_prepare07` with column and string-row scenarios. It uses `SimpleDataSet`, timestamped transactions, a separate prepared session, `Connection.set_timestamp`, `Session.checkpoint`, `backup`, `wiredtiger_open` on the backup, and cursor reads.

## Control Flow, State, And Persistence
The test populates base rows, inserts many large values, checkpoints, then commits updates at timestamps 110 and 120, prepares an update at 130 and leaves it open, commits more updates at 140 and 150, advances stable and oldest to 155, commits another update at 160, and checkpoints before resolving the prepared transaction with commit timestamp 140 and durable timestamp 160. A backup is taken and opened. The backup must include stable non-prepared updates, exclude the prepared update because it was not durable at checkpoint, and exclude the timestamp-160 update newer than stable.

## Dependencies, Integration, Risks, And Test Signals
Depends on backup, checkpoint visibility, prepared durable timestamp handling, and `txn_visible_all` behavior when oldest advances past a prepared transaction. Risks are visibility gaps that expose prepared updates or newer-than-stable data. Signals are exact value checks in the backup for keys nrows+1 through nrows+6.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare07.py -->
