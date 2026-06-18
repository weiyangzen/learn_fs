# subset-b-009085 Research

Grouped research for WiredTiger prepare transaction regression tests `test_prepare08.py` through `test_prepare49.py` except `test_prepare45.py`. Each section preserves the original source path for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare08.py

## Purpose

Tests that prepared tombstones and update-then-delete chains are correctly committed or rolled back after eviction has pushed prepared content toward the data store. It covers column-store and string-row tables with byte-array values.

## Important APIs, Control Flow, and State

`test_prepare08` uses `wttest.WiredTigerTestCase`, `SimpleDataSet`, `make_scenarios`, `session.begin_transaction`, `prepare_transaction`, `commit_transaction`, `rollback_transaction`, `checkpoint`, and debug cursors with `release_evict`. Helpers bulk update, remove, and timestamp-read rows with `ignore_prepare=true`. The three tests build two tables, pin oldest/stable timestamps, load large values at timestamps 20 and 30, checkpoint, create an unresolved prepared delete or update-delete sequence, then mutate the second table to force eviction of the first. They verify older values remain visible while the prepare is unresolved, then check rollback preserves prior history and commit produces deletion visibility at the commit timestamp. One variant starts from a committed tombstone instead of a base update.

## Dependencies, Risks, and Test Signals

Dependencies are WiredTiger Python APIs, timestamp helpers, datasets, scenarios, and eviction debug config. The risk is subtle reconciliation of prepared tombstones written to disk, especially when no base update exists or multiple updates share one prepared transaction. Signals are timestamped reads, `WT_NOTFOUND`, large value pressure, checkpoints, and explicit eviction before resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare09.py

## Purpose

Validates rollback of prepared updates that were reconciled to disk does not leave incorrect tombstones or stale visibility metadata. It targets column and integer-row tables with large string values.

## Important APIs, Control Flow, and State

`test_prepare09` creates timestamped tables, pins oldest/stable to 1, and uses direct cursor assignment plus `prepare_transaction` and `rollback_transaction`. `test_prepared_update_is_aborted_correctly_with_on_disk_value` commits key 1 at timestamp 2, fills many other keys to force the value onto disk, prepares a replacement at timestamp 3, rolls it back, drives more page pressure, and asserts key 1 still returns the original value. `test_prepared_update_is_aborted_correctly` prepares inserts for keys 1 to 3 without a prior committed value, forces the prepare to disk through many additional writes, rolls it back, and asserts key 1 is not found.

## Dependencies, Risks, and Test Signals

Dependencies are WiredTiger errors/constants, `wttest`, and scenario generation. The main risk is rollback accidentally inserting a tombstone where an older committed value should remain visible, or failing to hide an aborted insert. Strong signals are large values, low cache, post-rollback point searches, and `WT_NOTFOUND` checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare10.py

## Purpose

Checks that rollback of a prepared insert after committed deletes preserves correct time windows for concurrent readers and history-store retrieval.

## Important APIs, Control Flow, and State

The class uses `SimpleDataSet`, timestamped bulk `insert`/`remove` helpers, and read helpers using `ignore_prepare=true`. The test loads 1000 records with value A at timestamp 20 and value B at 30, checkpoints, opens long-lived reader transactions, removes all keys at 40, then prepares reinserts with value C at 50. It verifies snapshot readers at timestamps 20 and 35 see A/B while later reads see not found. After rolling back the prepared insert, the same visibility expectations remain, and the long-running sessions still observe their original snapshots.

## Dependencies, Risks, and Test Signals

Dependencies include WiredTiger constants, datasets, scenarios, checkpoints, and timestamp reads. The risk is that rollback of a prepared insert corrupts restored time windows or invalidates active snapshots. Test signals include two preserved reader sessions, `WT_NOTFOUND` at later timestamps, and repeated checks before and after prepare rollback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare11.py

## Purpose

Exercises prepare resolution when a reserved update sits between two updates to the same key. It ensures repeated-key tracking does not skip either prepared operation during commit or rollback.

## Important APIs, Control Flow, and State

`test_prepare11` parameterizes column and string-row keys and whether the prepared transaction commits or rolls back. The test creates one table, begins a transaction, writes `value_x`, calls cursor `reserve()` on the same key, writes `value_y`, and prepares at timestamp 10. The commit path assigns commit timestamp 20 and durable timestamp 30 before commit; the rollback path calls `rollback_transaction`. No final read is needed: the test is a regression/crash assertion around prepare resolution over update/reserve/update chains.

## Dependencies, Risks, and Test Signals

Dependencies are `wttest`, `make_scenarios`, cursor reserve semantics, and transaction timestamp APIs. The risk is resolving only one prepared update because a reservation changes key-repeat metadata. The test signal is successful prepare resolution under both commit and rollback scenarios without assertion or write-chain corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare12.py

## Purpose

Tests update restore of a page containing a prepared update while another uncommitted update and eviction pressure are present.

## Important APIs, Control Flow, and State

The test parameterizes column and integer-row key formats. It creates a table, prepares key 1 with value `a` at timestamp 1, opens a second session with an uncommitted insert to key 2, then a third session inserts many larger records in independent transactions to fill the small cache and trigger eviction/update restore. The original prepared update is then committed with commit timestamp 1 and durable timestamp 2. A read transaction at timestamp 2 asserts key 1 returns `a`.

## Dependencies, Risks, and Test Signals

Dependencies are `wttest`, `make_scenarios`, small-cache eviction, multiple sessions, and timestamp commit/read APIs. The risk is update restore losing or misordering a prepared update when another uncommitted update exists on the page. The signal is a successful timestamp read after cache pressure and prepare commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare13.py

## Purpose

Verifies fast truncate fails with a conflict when the truncation range contains a prepared update.

## Important APIs, Control Flow, and State

`test_prepare13` builds a large timestamp-capable table with small page sizes, loads many records, prepares a replacement at key 1000, advances stable/oldest to the prepare timestamp, then updates many later records from a separate session to encourage eviction of the prepared page. A separate transaction attempts `session.truncate` from key 100 through the table end and expects `WiredTigerError` matching `/conflict between concurrent operations/`. The prepared transaction is resolved in a `finally` block with commit and durable timestamps 50.

## Dependencies, Risks, and Test Signals

Dependencies include `simple_key`, `simple_value`, `make_scenarios`, explicit truncate cursors, and WiredTiger error assertions. The risk is fast-truncate bypassing page-level prepared-update checks. The test signal is the expected conflict rather than silent range deletion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare14.py

## Purpose

Tests visibility for an on-disk update whose start and stop time points come from the same uncommitted prepared transaction.

## Important APIs, Control Flow, and State

The test runs for in-memory and non-in-memory configurations and column/integer-row keys. It creates a timestamp-capable table, optionally disables logging for in-memory, pins timestamps to 10, and in a separate session inserts then removes the same key before preparing at timestamp 20. A debug `release_evict` cursor reads with `ignore_prepare=true`, expects `WT_NOTFOUND`, resets to force eviction, and a second read again expects not found.

## Dependencies, Risks, and Test Signals

Dependencies are cursor remove, prepared transactions, debug eviction, and `WT_NOTFOUND`. The risk is an insert/remove pair in a prepared transaction becoming visible or being restored incorrectly after eviction. Signals are successful eviction of a prepared start-stop chain and repeated not-found reads under `ignore_prepare`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare15.py

## Purpose

Validates commit and rollback of prepared transactions containing update/tombstone combinations, including history-store interactions and in-memory variants.

## Important APIs, Control Flow, and State

The file parameterizes in-memory mode, key format, and transaction end. `test_prepare_hs_update_and_tombstone` commits value A, commits a tombstone, prepares value B plus remove, evicts with `ignore_prepare`, resolves commit or rollback, evicts again, and verifies the historical read at timestamp 20 returns A. `test_prepare_hs_update` commits A, prepares update+remove, evicts, resolves, verifies timestamp 20 still sees A, advances timestamps, writes C, evicts, and checks timestamp 70 sees not found only if the prepare committed. `test_prepare_no_hs` handles a prepared insert/remove with no historical base and expects not found regardless of resolution.

## Dependencies, Risks, and Test Signals

Dependencies include `WT_NOTFOUND`, scenarios, in-memory logging options, history-store visibility, and release eviction. Risks center on replacing on-disk keys with history-store content or tombstones when prepared operations resolve. Signals are timestamped reads across commit/rollback and eviction before and after resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare16.py

## Purpose

Tests prepared commit and rollback across many keys when each key can occupy its own leaf page, for both in-memory and disk-backed trees.

## Important APIs, Control Flow, and State

The test configures large cache, small leaf pages, and large values, parameterizing in-memory mode, key format, and commit/rollback. It prepares 1000 inserted keys at timestamp 11, then uses a second session with `ignore_prepare=true` and `release_evict` to search every key and force page eviction while prepared. The transaction commits at timestamps 20/30 or rolls back. Stable advances to 30, disk-backed runs checkpoint, and a read at timestamp 20 expects all values on commit or `WT_NOTFOUND` on rollback.

## Dependencies, Risks, and Test Signals

Dependencies are timestamped transactions, release eviction, page sizing, and `WT_NOTFOUND`. The risk is page-by-page prepared resolution differing across many leaf pages or in-memory mode. Signals are full-range eviction and full-range timestamp verification after resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare17.py

## Purpose

Regression test for cache-stuck behavior when committing a large prepared update that itself exceeds eviction trigger thresholds.

## Important APIs, Control Flow, and State

The connection is configured with 1 MB cache and low eviction dirty/update triggers. The test inserts a 400 KB value inside a transaction, prepares at timestamp 5, assigns commit and durable timestamps, closes the cursor, sleeps to give eviction time to write prepared content, and then commits. The important state is that commit may need to read the prepared page and history-store page back into cache while the cache already appears over target.

## Dependencies, Risks, and Test Signals

Dependencies are timing/sleep, eviction thresholds, and prepare commit. The risk is eviction checks during prepared transaction resolution causing a stuck cache or deadlock. The test signal is successful commit under pressure; it is primarily a no-hang/no-crash regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare18.py

## Purpose

Ensures prepared transactions reject operations on logged tables.

## Important APIs, Control Flow, and State

With connection logging enabled, the test populates a logged table through `SimpleDataSet`, commits one ordinary update, begins another transaction on the same key, and calls `prepare_transaction('prepare_timestamp=1')`. It expects `WiredTigerError` with the message that a prepared transaction cannot include a logged table.

## Dependencies, Risks, and Test Signals

Dependencies are logging configuration, `SimpleDataSet`, and `assertRaisesWithMessage`. The risk is allowing prepared semantics on logged objects, which conflicts with timestamped prepared transaction guarantees. The test signal is the exact error path rather than any persisted state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare19.py

## Purpose

Tests in-memory rollback of a reconciled prepared update when the resulting update chain would otherwise become empty.

## Important APIs, Control Flow, and State

The connection is `in_memory=true`. The test creates many aborted updates on key 1, then calls `prepare_evict_rollback`, which prepares another update, opens a conflicting writer to force eviction on the page with more than 1000 updates, catches the expected write conflict, and rolls back the prepared transaction. It then starts a new transaction and writes key 1. If rollback did not append the needed tombstone into the btree/update chain, this final write would observe an active transaction and fail.

## Dependencies, Risks, and Test Signals

Dependencies are in-memory tables, write-conflict behavior, and prepared rollback. The risk is metadata mismatch between aborted update chains and btree state after reconciliation. The signal is absence of a write conflict after rollback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare20.py

## Purpose

Demonstrates an application-level log replay strategy for unstable prepared transactions across crash recovery.

## Important APIs, Control Flow, and State

`test_prepare20` uses a logged connection but a data file with `log=(enabled=false)` and a separate logged application log table. Helpers record logical operations: begin, write, prepare timestamp, prepare, commit timestamp, durable timestamp, and commit. The test commits baseline A at timestamp 10, logs and commits B at 22/25, optionally checkpoints at varied stable timestamps, logs C prepared at 30 and optionally commits it at 32/35, optionally checkpoints again, then simulates crash restart. `log_replay` scans the log, ignores transactions without prepare/commit evidence, starts replay transactions with `roundup_timestamps=(prepared=true)`, repairs durable timestamps if they are not beyond stable, and commits any prepared-but-uncommitted transaction with recorded times.

## Dependencies, Risks, and Test Signals

Dependencies are `simulate_crash_restart`, scenarios over key format, checkpoint timing, and commit-before-crash state. Risks include replaying unprepared partial work, double-writing stable data, or using durable timestamps below stable. Signals are reads at timestamps 15/25/35 and expected replay counts based on checkpoint timing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare21.py

## Purpose

Regression test for prepared rollback interacting with rollback-to-stable, eviction, and a concurrent checkpoint.

## Important APIs, Control Flow, and State

The class inherits rollback-to-stable helpers, enables all statistics and `history_store_checkpoint_delay`, and uses `checkpoint_thread`. It writes value A at 20, B at 30, removes at 40, prepares value C at 50, verifies older reads, evicts pages with `ignore_prepare=true`, advances stable to 40, rolls back the prepared update, and writes value D at 60. A checkpoint thread starts; the test waits for checkpoint state via statistics, then evicts again while checkpoint is active. Final reads verify A, B, and D remain visible at their timestamps.

## Dependencies, Risks, and Test Signals

Dependencies include `test_rollback_to_stable_base`, `SimpleDataSet`, `checkpoint_thread`, and `stat.conn.checkpoint_state`. The risk is out-of-order timestamp/history fixup crashing during checkpoint. Signals are concurrent checkpoint synchronization, forced eviction, and post-operation timestamp reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare22.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare22.py

## Purpose

Tests prepare rollback followed by rollback-to-stable in a normal eviction path without forced eviction failure.

## Important APIs, Control Flow, and State

The test parameterizes key format and whether a committed delete exists. It inserts value A at timestamp 10, value B at 20, optionally removes at 30, prepares value C at 40, evicts the page with `ignore_prepare=true` at timestamp 20, checkpoints to persist history-store state, rolls back the prepare, sets stable to 30, and calls `rollback_to_stable`. It then evicts again and verifies reads at timestamps 10 and 20 still return A and B, with timestamp 30 returning not found for delete scenarios.

## Dependencies, Risks, and Test Signals

Dependencies are WiredTiger rollback-to-stable, release eviction, checkpoints, and `WT_NOTFOUND`. The risk is rollback-to-stable losing history after an aborted prepared update was evicted. Signals are pre/post RTS eviction and timestamp readback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare22.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare23.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare23.py

## Purpose

Stresses prepare rollback with rollback-to-stable under a failed eviction split timing stress.

## Important APIs, Control Flow, and State

With `timing_stress_for_test=[failpoint_eviction_split]`, the test loops 1000 keys, each with value A, value B, optional delete, and a prepared value C. For each key it evicts using `ignore_prepare=true` at the B timestamp, rolls back the prepare, advances stable to the last committed timestamp, calls `rollback_to_stable`, and verifies A/B plus optional deletion remain readable. The timestamp base increments per key to avoid cross-key timestamp reuse.

## Dependencies, Risks, and Test Signals

Dependencies are failpoint eviction split, timestamped updates/removes, rollback-to-stable, and scenarios. The risk is failed eviction paths leaving prepared rollback state that RTS misinterprets. Signals are repeated per-key verification over 1000 iterations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare23.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare24.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare24.py

## Purpose

Tests commit of a prepared update after an eviction failure path.

## Important APIs, Control Flow, and State

Using the eviction split failpoint, the test iterates 1000 keys. Each key gets value A at timestamp +10, optional delete at +20, a prepared value B at +30, eviction at the A timestamp with `ignore_prepare=true`, then commit with commit timestamp +30 and durable timestamp +40. It evicts again and verifies timestamp +10 sees A, optional timestamp +20 sees not found, and timestamp +30 sees B.

## Dependencies, Risks, and Test Signals

Dependencies are failpoint eviction, prepared commit, release eviction, and `WT_NOTFOUND`. The risk is failed eviction causing committed prepared updates or prior deletes to lose correct time windows. Signals are repeated read verification after both eviction and commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare24.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare25.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare25.py

## Purpose

Covers a rollback of one prepared update followed by a committed prepared update on the same key under eviction failure stress.

## Important APIs, Control Flow, and State

Each of 1000 keys receives value A, optional delete, a prepared value B that is evicted and rolled back, then a second prepared value C that commits with durable timestamp after the commit timestamp. A second eviction occurs after commit. Reads verify A at the first timestamp, optional deletion at the delete timestamp, and C at the second prepare/commit timestamp. The connection uses `timing_stress_for_test=[failpoint_eviction_split]`.

## Dependencies, Risks, and Test Signals

Dependencies are prepared rollback/commit sequencing, eviction failpoint, scenario key formats, and timestamp visibility. The risk is stale rollback state from the first prepared update interfering with the later committed prepared update. Signals are long repeated key coverage and post-resolution reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare25.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare26.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare26.py

## Purpose

Tests rollback of a prepared update, deletion of the same key, timestamp advancement, and later updates after eviction.

## Important APIs, Control Flow, and State

The test inserts value A at timestamp 10, prepares value C at 20, evicts at timestamp 10 with `ignore_prepare=true`, rolls back the prepare, deletes the key at timestamp 30, advances oldest to 30, evicts and expects not found, writes value B at 40 and C at 50, evicts again at timestamp 50, and finally verifies timestamp 30 reads not found. It runs for column and integer-row keys.

## Dependencies, Risks, and Test Signals

Dependencies are release eviction, timestamped removes/updates, oldest timestamp advancement, and `WT_NOTFOUND`. The risk is an aborted prepared update being selected as a base value after the key is deleted and rewritten. Signals are staged evictions and a final timestamped not-found assertion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare26.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare27.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare27.py

## Purpose

Ensures an aborted prepared update is not chosen as the base value during rollback-to-stable reconstruction.

## Important APIs, Control Flow, and State

The test parameterizes column, integer-row, and string-row keys. It writes five timestamped values for one key, sets stable to 2, prepares a sixth value, evicts with `ignore_prepare=true` so the prepared update reaches the data store and older versions reach history store, rolls back the prepare, and calls `rollback_to_stable`. Comments document the expected chain as stable update 2 followed by aborted updates 6 and 5. It then opens a read transaction at timestamp 1 and searches the key, exercising retrieval of the earliest committed value rather than the aborted prepared base.

## Dependencies, Risks, and Test Signals

Dependencies are the transaction context manager, release eviction, `rollback_to_stable`, and scenario key conversion helpers. The risk is selecting an aborted prepared update as the restore base. The signal is successful post-RTS historical search without visibility corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare27.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare28.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare28.py

## Purpose

Regression test for reading a partial prepared transaction with `ignore_prepare=true` during prepare resolution.

## Important APIs, Control Flow, and State

The test is skipped for tiered storage and enables `timing_stress_for_test=[prepare_resolution_2]`, which sleeps during prepare resolution. One session prepares three updates to key 1 at timestamp 4. A second thread waits briefly, opens a transaction with `ignore_prepare=true`, hits `session.breakpoint()`, and searches key 1 while the main thread commits at timestamp 6. The expected search return is `-31803`, and connection statistic `txn_read_race_prepare_commit` must be greater than zero.

## Dependencies, Risks, and Test Signals

Dependencies are `wtthread.Thread`, timing stress, WiredTiger statistics, and thread interleaving. The risk is exposing a subset of updates from one prepared transaction while resolution is in progress. Signals are the special return code and race statistic increment.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare28.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare29.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare29.py

## Purpose

Ensures updates preceding an unstable prepared tombstone are restored with valid transaction IDs after crash recovery.

## Important APIs, Control Flow, and State

The test is skipped for disaggregated storage because it relies on rollback-to-stable. It inserts a value at timestamp 100, sets stable to 200, checkpoints, removes the key in a prepared transaction at timestamp 300, evicts the key with `ignore_prepare=true`, checkpoints from another session, and simulates an unclean crash restart. After recovery, it removes the same key in a new transaction and commits at timestamp 201. Without correct transaction ID reset for restored updates, this operation would see a write conflict or rollback error.

## Dependencies, Risks, and Test Signals

Dependencies are `simulate_crash_restart`, release eviction page debug, timestamps, and scenario key formats. The risk is recovery leaving restored pre-tombstone updates with transaction IDs that conflict with future writers. The signal is successful post-recovery remove/commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare29.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare30.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare30.py

## Purpose

Validates prepare API error handling when `preserve_prepared=true` is enabled.

## Important APIs, Control Flow, and State

The scenario enables `precise_checkpoint=true,preserve_prepared=true`. The test sets stable timestamp 50, creates a simple table, begins a transaction, and calls `prepare_transaction` at timestamp 100 without a `prepared_id`. It expects `WiredTigerError` with the message requiring `prepared_id` when preserve prepared is enabled.

## Dependencies, Risks, and Test Signals

Dependencies are `make_scenarios`, preserve-prepared connection config, and `assertRaisesWithMessage`. The risk is accepting prepared transactions without durable identity metadata needed by preserve-prepared checkpoint/recovery. The test signal is the precise API validation failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare30.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare31.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare31.py

## Purpose

Tests checkpoint selection for rolled-back prepared updates under preserve-prepared, based on stable timestamp relative to prepare and rollback timestamps.

## Important APIs, Control Flow, and State

The class inherits `test_prepare_preserve_prepare_base`, which enables precise checkpoint, preserve prepared, and statistics. Helpers set up committed initial data, create a prepared transaction over many keys with `prepared_id=1`, roll it back at a supplied rollback timestamp, and inspect `rec_time_window_prepared`. Three tests assert checkpoint skips aborted prepared updates when rollback timestamp is stable, skips when prepare timestamp is not stable, and writes the prepared update when prepare is stable but rollback is not.

## Dependencies, Risks, and Test Signals

Dependencies are `wiredtiger.stat.dsrc.rec_time_window_prepared`, `checkpoint_and_verify_stats`, timestamp helpers, and prepared IDs. The risk is checkpoint writing or skipping aborted prepared updates at the wrong stability boundary. Signals are targeted reconciliation statistics for each timestamp regime.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare31.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare32.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare32.py

## Purpose

Tests checkpoint behavior for committed prepared updates as stable timestamp advances across prepare, commit, and durable timestamps.

## Important APIs, Control Flow, and State

After initial data and a clean checkpoint, the test prepares updates for keys 1 to 99 at timestamp 70 with a prepared ID and commits at timestamp 80 with durable timestamp 90. With stable still 40, checkpoint should not write prepared content. Stable 85 should write the update as prepared. Stable 95 should write it as committed with durable start timestamp metadata and no prepared time window. Stable 100 should not rewrite because the page is clean.

## Dependencies, Risks, and Test Signals

Dependencies include preserve-prepared base behavior, `checkpoint_and_verify_stats`, and `wiredtiger.stat.dsrc` counters for prepared and durable start timestamps. Risks are premature prepared writes, failure to convert prepared cells to committed cells, or dirty-page churn. Signals are staged stat checks across stable timestamp movement.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare32.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare33.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare33.py

## Purpose

Tests checkpoint handling for rolled-back prepared transactions that include tombstones.

## Important APIs, Control Flow, and State

The test creates initial data, checkpoints, then a prepared transaction updates many keys and repeatedly removes key 1, prepares at timestamp 70 with a prepared ID, and rolls back at timestamp 80. With stable 40, checkpoint should not write the prepare. With stable 75, checkpoint should write prepared start and stop transaction metadata. With stable 85, rollback is stable, so checkpoint should skip the aborted prepared stop information while writing committed start metadata.

## Dependencies, Risks, and Test Signals

Dependencies are preserve-prepared base config, prepared IDs, and detailed reconciliation stats such as start/stop txn and durable start/stop timestamps. The risk is mishandling tombstone time-window fields after rollback. Signals are granular stat expectations at pre-prepare, between prepare/rollback, and post-rollback stable timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare33.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare34.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare34.py

## Purpose

Tests preserve-prepared checkpoint behavior for transactions containing `wiredtiger.Modify` operations, for both rollback and commit.

## Important APIs, Control Flow, and State

The rollback test inserts baseline `aaaaa` values, prepares two rounds of large modifies, checkpoints before and after rollback timestamp movement, and verifies reads at timestamp 75 still return the original value. The commit test performs ordered modifies inserting long B and D strings, commits with durable timestamp 90, verifies checkpoints write prepared content when prepare is stable and committed content when durable is stable, handles disaggregated storage page-delta expectations, and checks timestamp 81 reconstructs `D + B + aaaaa`.

## Dependencies, Risks, and Test Signals

Dependencies are `wiredtiger.Modify`, preserve-prepared stats, read timestamps, and hook-specific disagg behavior. Risks include reconstructing modifies incorrectly from preserved prepared cells or writing wrong time-window metadata. Signals are reconciliation stats plus value reconstruction before and after commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare34.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare35.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare35.py

## Purpose

Tests repeated prepared inserts to the same key, including a rolled-back prepared update that leaves a globally visible tombstone before a second prepared update.

## Important APIs, Control Flow, and State

The test creates committed baseline keys 1 to 20, prepares key 21 with `prepared_id=1`, advances stable to the prepare timestamp, and verifies checkpoint writes prepared time-window metadata. It forces eviction through a debug page eviction session, rolls back the prepared insert at timestamp 35, verifies key 21 is not visible, then creates a second prepared insert to key 21 with a different prepared ID and advances stable beyond its prepare timestamp. A final checkpoint must again write prepared content.

## Dependencies, Risks, and Test Signals

Dependencies are preserve-prepared helper stats, page eviction debug, prepared IDs, and `WT_NOTFOUND`. The risk is retaining or losing tombstone/prepared state when a second prepared operation reuses a key. Signals are two `rec_time_window_prepared` checkpoints and readback after first rollback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare35.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare36.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare36.py

## Purpose

Verifies history-store contents for a committed prepared transaction under precise checkpoint and preserve-prepared.

## Important APIs, Control Flow, and State

The test writes baseline value A for keys 1 to 21 at timestamp 25, prepares value B for key 21 at timestamp 30, advances stable to 30, verifies checkpoint writes prepared metadata, evicts pages, and commits at 35/40. It reads key 21 at timestamp 40 as B and at timestamp 30 as A. When stable is 35, `check_ckpt_hs` opens `file:WiredTigerHS.wt` from the checkpoint and expects value A with start timestamp 25 and max stop timestamp. After stable 40 and reopen, it expects A in the history store with stop timestamp 40.

## Dependencies, Risks, and Test Signals

Dependencies are direct history-store cursor reads, `WT_TS_MAX`, preserve-prepared stats, eviction, and reopen. It skips disagg until cell packing/unpacking support exists. Risks are wrong HS stop timestamp adjustment around committed prepared updates. Signals are value/timestamp checks inside HS checkpoint and reopened HS files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare36.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare37.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare37.py

## Purpose

Tests eviction and visibility for committed and rolled-back prepared updates and deletes after checkpoint writes preserve-prepared cells.

## Important APIs, Control Flow, and State

Four tests share a pattern: create base values at timestamp 25, update to second values at 30, prepare an update or delete for key 20 at 35 with a prepared ID, advance stable to 35, verify checkpoint writes prepared metadata, resolve commit at 40/45 or rollback at 40, force debug page eviction, and verify timestamp reads. Commit-update reads see prepared value at 45 and old values at 30/25. Rollback-update reads see the second committed value. Commit-delete sees `WT_NOTFOUND` at 45 while older timestamps see committed values. Rollback-delete restores the second committed value.

## Dependencies, Risks, and Test Signals

Dependencies include preserve-prepared stats, debug eviction, timestamped reads, and `WT_NOTFOUND`. Risks are eviction freeing updates that are still needed as rollback fallback or historical versions. Signals are repeated eviction before and after stable advances to resolution timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare37.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare38.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare38.py

## Purpose

Checks compatibility: a database containing on-disk prepared updates produced with preserve-prepared can be opened with `preserve_prepared=false`.

## Important APIs, Control Flow, and State

The test creates a table, commits key 1, then in a prepared transaction removes key 1, inserts key 2, and inserts/removes key 3. It prepares at timestamp 10 with a prepared ID, advances stable to 20, checkpoints from another session to write prepared updates to disk, copies the WiredTiger home to `RESTART`, and opens that copy with `preserve_prepared=false`. Back in the original connection it rolls back the prepared transaction at timestamp 30 and advances stable.

## Dependencies, Risks, and Test Signals

Dependencies are `copy_wiredtiger_home`, alternate `wiredtiger_open`, preserve-prepared base config, and prepared IDs. The risk is an on-disk format compatibility break between preserve-prepared and normal opens. The signal is successful open of the copied home without preserving prepared state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare38.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare39.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare39.py

## Purpose

Verifies history-store contents for a rolled-back prepared transaction under precise checkpoint and preserve-prepared.

## Important APIs, Control Flow, and State

The test commits value A at timestamp 21 and value B at 25 for keys 1 to 21, prepares key 21 at timestamp 30, advances stable to 30, verifies checkpoint writes prepared metadata, then rolls back at timestamp 35. A checkpoint with stable still 30 should place value B in the history store with max stop timestamp. After stable 40 and checkpoint/eviction, timestamp reads for key 21 at 21, 25, 30, and 35 return A/B/B/B as expected. After reopening, direct history-store reads expect value A with start 21 and stop 25.

## Dependencies, Risks, and Test Signals

Dependencies are direct history-store file cursors, with a disagg-specific shared history-store filename, preserve-prepared stats, and reopen. Risks are wrong HS stop timestamp when a prepared update is rolled back. Signals are direct HS tuple checks and timestamped user-data reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare39.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare40.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare40.py

## Purpose

Regression test that checkpoint after opening a backup with prepared updates does not crash when a prepared transaction is later rolled back with rollback timestamp greater than stable.

## Important APIs, Control Flow, and State

With precise checkpoint and preserve-prepared enabled, the test commits keys 1 and 2 at timestamp 60, prepares keys 3 to 5 at timestamp 100 with prepared ID 123, advances stable to 150, and checkpoints to write prepared cells. It force-evicts committed keys to hit on-disk prepare resolution, rolls back at timestamp 200, and checkpoints from a new session. Non-disagg expects `rec_time_window_prepared`; disagg expects no page delta write.

## Dependencies, Risks, and Test Signals

Dependencies are preserve-prepared checkpoint stats, debug page eviction, hook detection, and rollback timestamp handling. Risks are crashes or wrong reconciliation after prepared cells were written then rolled back while rollback remains unstable. Signals are successful post-rollback checkpoint with expected stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare40.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare41.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare41.py

## Purpose

Tests that update restore for rolled-back prepared operations retains full updates needed to reconstruct modifies.

## Important APIs, Control Flow, and State

Both tests insert a 100-character value, apply a committed modify at timestamp 25 changing the first byte to `b`, then create a prepared operation at timestamp 30: either another modify changing the first byte to `d` or a delete. The prepared operation is rolled back at timestamp 35, pages are force-evicted with `ignore_prepare=true`, stable advances to 40, and checkpoint reinserts updates into the history store. A timestamp-25 read must reconstruct `b` plus 99 `a` characters in both cases.

## Dependencies, Risks, and Test Signals

Dependencies are `wiredtiger.Modify`, preserve-prepared configuration, release eviction page debug, checkpoint, and timestamped reads. The risk is update restore retaining a delta without the full base update after prepared rollback. Signals are exact reconstructed value comparisons.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare41.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare42.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare42.py

## Purpose

Tests rolled-back prepared inserts becoming deletes through rollback tombstones, including a case where the prior stop point is globally visible.

## Important APIs, Control Flow, and State

`test_prepare_insert_rollback` inserts committed keys 1 to 19, prepares insert of key 20, rolls it back at timestamp 45, verifies early checkpoint writes no prepared content, advances stable to prepare timestamp 35 and expects prepared time-window write, evicts, advances stable to rollback timestamp, checkpoints no prepared content, evicts again, and verifies key 20 is not found. The second test first deletes key 19 at timestamp 25, makes the delete stable and globally visible by moving oldest, prepares a new insert for key 19, rolls it back, and follows the same stable/eviction progression.

## Dependencies, Risks, and Test Signals

Dependencies are preserve-prepared stats, debug page eviction, oldest/stable timestamp movement, and `WT_NOTFOUND`. Risks are failure to materialize or clean rollback tombstones when no live base update remains. Signals are staged checkpoint stat transitions and final not-found reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare42.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare43.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare43.py

## Purpose

Ensures checkpoint cursors still walk pages containing prepared tombstones and do not skip keys after eviction.

## Important APIs, Control Flow, and State

The test runs under fuzzy checkpoint and precise/preserve-prepared configurations. It inserts keys 1 to 99 at timestamp 21, prepares removal of all keys at timestamp 25 with a prepared ID, advances stable beyond the prepare timestamp, checkpoints, then force-evicts the page with `ignore_prepare=true`. A checkpoint cursor on `checkpoint=WiredTigerCheckpoint` iterates from key 1 to 99 and expects every key to return the original committed value.

## Dependencies, Risks, and Test Signals

Dependencies are `make_scenarios`, checkpoint cursors, debug page eviction, and preserve-prepared base behavior. The risk is page walks incorrectly skipping pages or keys because prepared tombstones are present. The test signal is complete ordered checkpoint-cursor iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare43.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare44.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare44.py

## Purpose

Regression test for an in-memory page eviction assertion involving an aborted prepared update at the tail of an update chain.

## Important APIs, Control Flow, and State

The test is skipped for tiered storage and uses `precise_checkpoint=true,preserve_prepared=true` with an in-memory, non-logged table. It prepares key 1, rolls it back at timestamp 15, then commits a new value for key 1 at timestamp 20 and adds many more keys to fill the page. Oldest is not advanced past committed updates so they are not globally visible. A release-evict cursor with `ignore_prepare=true` searches key 1, expects the committed value, and resets to evict. A timestamp-20 read verifies the committed value remains.

## Dependencies, Risks, and Test Signals

Dependencies are in-memory storage, prepared IDs, debug eviction, and timestamp reads. The risk is aborted prepared tail state setting `has_newer_updates` and tripping in-memory split assertions. Signals are no crash during eviction and correct post-eviction readback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare44.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare46.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare46.py

## Purpose

Regression test for preserving a prepared cell after eviction happens while the prepare timestamp is still unstable.

## Important APIs, Control Flow, and State

The test commits key 1 at timestamp 20, sets stable to 25 below the upcoming prepare timestamp, opens a concurrent writer transaction to pin transaction state, then prepares a fresh insert for key 2 at timestamp 30 and rolls it back at timestamp 50. Eviction at stable 25 should defer the rollback tombstone instead of marking it written. After the blocker closes and stable advances to 35, checkpoint must write `rec_time_window_prepared=True`. When stable advances to 55, checkpoint should no longer write prepared content. Reads at timestamp 20 still find key 1 throughout.

## Dependencies, Risks, and Test Signals

Dependencies are preserve-prepared config, prepared IDs, concurrent sessions, release eviction, and checkpoint stats. The risk is poisoning later reconciliation by selecting the tombstone before prepare timestamp is stable. Signals are prepared stat true at stable 35 and false at stable 55.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare46.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare47.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare47.py

## Purpose

Tests aborted prepared inserts on top of committed tombstones, ensuring reconciliation keeps a rollback fallback across multiple evictions.

## Important APIs, Control Flow, and State

The class parameterizes row and column keys under precise checkpoint/preserve-prepared. `test_aborted_prepared_with_committed_tombstone` inserts and checkpoints values, deletes them in memory, prepares replacement values, rolls back with rollback timestamp ahead of stable, advances oldest past the tombstone, evicts once below prepare timestamp and again after stable passes prepare timestamp, then asserts representative keys are not found. `test_aborted_prepared_with_lost_disk_fallback` creates an on-disk cell with start and stop timestamps, prepares insert after the cell is deleted, rolls back without appending a tombstone because the disk cell is the fallback, then performs the same two eviction rounds.

## Dependencies, Risks, and Test Signals

Dependencies are scenario key formats, release eviction, timestamped helper reads, and preserve-prepared semantics. Risks are dropping the committed tombstone or on-disk fallback, causing leaked-prepared-update assertions. Signals are no assertion during second eviction and not-found reads after rollback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare47.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare48.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare48.py

## Purpose

Regression test for an aborted prepared insert with a pinned concurrent writer and persisted delete fallback.

## Important APIs, Control Flow, and State

The test commits key 1 as an eviction anchor, commits key 2 then removes it, advances stable to 31, checkpoints, and force-evicts so the delete reaches disk. Oldest advances past the remove, a blocker session keeps an active writer transaction open, and an eviction session begins before the prepared transaction. Another session prepares an insert for key 2 at timestamp 40 and rolls it back at 50. Eviction below prepare timestamp must preserve the persisted delete. After stable 42, a second eviction and read assert key 2 remains not found. Stable 55 and checkpoint clean up while preserving not-found semantics.

## Dependencies, Risks, and Test Signals

Dependencies are multiple concurrent sessions, release eviction, `assert_not_found`, preserve-prepared config, and `WT_NOTFOUND`. The risk is discarding the persisted delete when an aborted prepared marker remains. Signals are not-found reads before and after rollback timestamp becomes stable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare48.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare49.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare49.py

## Purpose

Tests eviction after rolling back a prepared transaction that updates, reserves, and deletes the same key.

## Important APIs, Control Flow, and State

With precise checkpoint and preserve-prepared enabled, the test commits a stable base value for key 1 at timestamp 5. It then begins a prepared transaction that updates key 1, calls `cursor.reserve()` on the key, and removes it, all under the same prepared transaction at timestamp 10 with prepared ID 1. Stable advances past the prepare timestamp to 15, then the transaction rolls back at timestamp 20. `_force_evict` opens a fresh session, reads key 1 at timestamp 5 with `ignore_prepare=true`, and resets a release-evict cursor to force eviction.

## Dependencies, Risks, and Test Signals

Dependencies are cursor reservation, prepared rollback, preserve-prepared config, timestamped read, and release eviction. The risk is reserve-in-the-middle chains confusing rollback/eviction resolution for update/delete prepared operations. The signal is eviction completing without crash while the base timestamp read succeeds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare49.py -->
