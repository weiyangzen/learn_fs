# subset-b-009087 WiredTiger rollback-to-stable test research

This grouped report covers the requested WiredTiger Python rollback-to-stable tests. Each section preserves the source path in the title and is bounded by the required file research markers for downstream reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable05.py

Purpose: exercises rollback-to-stable (RTS) when two tables have unstable updates while another session holds a long-running transaction open. It varies column-store versus integer row-store keys, in-memory versus disk-backed connections, prepared versus non-prepared updates, and RTS worker thread counts 0/4/8.

Important APIs/types/functions: class `test_rollback_to_stable05` extends `test_rollback_to_stable_base`, reusing `large_updates`, `check`, `timestamp_str`, and RTS log verification. `conn_config` enables `statistics=(all)` and `verbose=(rts:5)`, plus `in_memory=true` for that scenario. The test uses `SimpleDataSet`, explicit `session.checkpoint`, an auxiliary session transaction, `conn.rollback_to_stable('threads=N')`, and `stat.conn.txn_rts*` counters.

Control flow: creates two tables, pins oldest/stable at timestamp 10, writes table 1 at 20/30/40/50, opens a second session transaction, writes table 2 at 20/30/40/50, optionally checkpoints for disk cases, commits the long transaction, then runs RTS. Visibility checks before RTS prove each timestamped value is readable; checks after RTS expect both tables to remain at their stable view rather than being incorrectly affected by the formerly open transaction.

State and persistence behavior: disk cases force dirty pages through checkpoint before RTS; in-memory cases skip checkpoint and therefore have different aborted-update expectations. Prepared scenarios offset read timestamps and use durable timestamps through the shared helper. Persistence-sensitive state is the combination of data-store pages, history-store records, active transaction visibility, and RTS statistics.

Dependencies and integration points: integrates with WiredTiger Python test harness, `wtdataset.SimpleDataSet`, `wtscenario.make_scenarios`, `wiredtiger.stat`, and helper-level RTS log verification. It is a direct regression for transaction ID visibility crossing multiple dhandles during RTS.

Risks: sensitive to transaction lifetime cleanup and checkpoint timing. If RTS starts with a live transaction or stats are interpreted identically for in-memory and disk modes, false failures can occur. Worker-thread variants increase coverage for parallel tree traversal races.

Test signals: asserts one RTS call, no key removal/restoration, nonnegative pages visited, and mode-dependent `txn_rts_upd_aborted` behavior. Data checks around timestamps are the primary correctness signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable06.py

Purpose: validates that RTS removes all updates newer than a stable timestamp when a table only has unstable content. Scenarios cover column and integer row stores, prepared/non-prepared updates, in-memory/disk configurations, optional eviction pressure, and worker thread counts.

Important APIs/types/functions: `test_rollback_to_stable06` derives from `test_rollback_to_stable_base`. It uses `SimpleDataSet`, `conn.set_timestamp`, helper `large_updates` and `check`, optional eviction behavior from the scenario, explicit checkpointing, `conn.rollback_to_stable`, and `stat.conn` counters such as `txn_rts`, `txn_rts_keys_removed`, `txn_rts_upd_aborted`, and `txn_rts_hs_removed`.

Control flow: populates `table:rollback_to_stable06`, pins oldest/stable to 10, writes four full-table values at 20/30/40/50, checks each historical view, checkpoints for disk-backed runs, runs RTS with the selected thread count, and rechecks that reads at those timestamps return zero rows. It then checkpoints again and inspects RTS counters.

State and persistence behavior: the test specifically forces a state where there is no stable version of any key, so RTS should delete or abort all unstable updates. In-memory runs disable logging for the table and do not rely on on-disk checkpoint content. Prepared runs shift visible read timestamps by one because prepare/commit/durable timestamps are staged by the shared helper.

Dependencies and integration points: depends on the common RTS base helper for timestamped transactions and read validation, `wiredtiger.stat` for statistics, and the scenario generator. It integrates with history-store accounting because disk-backed updates may have history-store entries while in-memory updates do not.

Risks: the optional eviction scenario can change whether work is counted as keys removed versus updates aborted. The test mitigates this by checking combined counts where appropriate and by separately asserting no history-store removals.

Test signals: expects one RTS invocation, no key restoration, positive pages visited, nonnegative keys removed, no history-store removal, and `upd_aborted + keys_removed == nrows * 4` after final checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable07.py

Purpose: tests recovery-time RTS after a simulated crash where stable data exists and later updates were checkpointed. It validates that restart recovery rolls pages back to the configured stable timestamp without requiring an explicit runtime RTS call.

Important APIs/types/functions: `test_rollback_to_stable07` extends `test_rollback_to_stable_base`; uses `simulate_crash_restart`, `SimpleDataSet`, `conn.set_timestamp`, `session.checkpoint`, helper `large_updates`/`check`, and `stat.conn.txn_rts*` counters.

Control flow: creates one table, pins timestamps at 10, writes values at 20/30/40/50, moves stable to 50 for prepared or 40 for non-prepared, writes additional values at 60/70/80, checkpoints, then simulates crash/restart. After restart, reads verify that timestamps at and beyond stable resolve to the last stable value, while older timestamps still resolve to their historical values.

State and persistence behavior: the checkpoint deliberately persists updates newer than stable so recovery must rollback persisted unstable content. Prepared variants require stable timestamp 50 because the prepared update at commit 50 has a durable timestamp after its prepare timestamp. No explicit `rollback_to_stable` is invoked after restart.

Dependencies and integration points: integrates recovery helper `simulate_crash_restart` and WiredTiger recovery RTS. Statistics are read after restart, where recovery-time RTS should already have run.

Risks: crash simulation and checkpoint content are timing-sensitive. If checkpoint does not include expected unstable updates, stats may show less work. Prepared timestamp choices must remain aligned with helper behavior.

Test signals: post-restart data visibility is the main signal. Statistics assert zero explicit RTS calls, no keys removed/restored, no updates aborted, and nonnegative history-store removal, proving recovery handled the persisted state consistently.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable08.py

Purpose: validates that RTS is a no-op when the stable timestamp is advanced to include all updates. It covers large tables across row/column formats, in-memory/disk modes, prepared/non-prepared updates, and RTS worker counts.

Important APIs/types/functions: uses the shared RTS base class, `SimpleDataSet`, `conn.set_timestamp`, `large_updates`, `check`, optional `session.checkpoint`, `conn.rollback_to_stable`, and RTS statistics including calls, history-store removal, update aborts, key removal/restoration, and pages visited.

Control flow: creates `table:rollback_to_stable08` with 10,000 rows, pins oldest/stable to 10, writes four full-table versions at 20/30/40/50, verifies all versions, advances stable to include the last write (60 for prepared, 50 for non-prepared), checkpoints disk-backed content, runs RTS, then verifies all historical versions remain readable.

State and persistence behavior: checkpointing persists the newest value, but because stable includes it, RTS should not discard data or history. In-memory cases avoid checkpointing and should report zero pages visited for some counters while still exercising the API path.

Dependencies and integration points: uses WiredTiger statistics and shared helper timestamp rules. It complements tests that delete unstable data by proving RTS does not over-prune stable histories.

Risks: off-by-one timestamp errors in prepared mode would make the stable update appear unstable. Large row count makes the test useful for traversal but can be slow in stressed environments.

Test signals: one RTS call, zero `hs_removed`, zero `upd_aborted`, zero key removal/restoration, and mode-dependent pages-visited expectations. Visibility checks confirm all values survive.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable09.py

Purpose: tests timestamped schema operations under RTS: creating a table, creating an index, rolling back to stable, then dropping the table and validating object visibility. It runs both column-style and row-style table definitions, in-memory/disk modes, prepared/non-prepared schema transactions, and worker counts.

Important APIs/types/functions: defines `create_table`, `create_index`, and `drop_table` helper methods using explicit transactions and optional prepare/commit/durable timestamps. It uses `session.create`, `session.drop`, `session.open_cursor`, `conn.rollback_to_stable`, `os.path.exists`, and `wiredtiger.WiredTigerError`.

Control flow: pins oldest/stable at 10, creates the table at timestamp 20, creates the index at 30, runs RTS, then verifies the table and index still exist and can be opened. It then drops the table at timestamp 40 and asserts that both table and index cursors fail to open.

State and persistence behavior: table and index metadata must survive RTS even though created after the initial stable timestamp, reflecting special handling for durable schema operations. Disk mode additionally checks `.wt` and `.wti` file existence.

Dependencies and integration points: uses WiredTiger metadata/schema APIs, secondary index naming, Python filesystem checks, and the RTS helper base. The test integrates with the broader metadata rollback path rather than only data-page rollback.

Risks: schema timestamp semantics differ from row updates, so incorrectly treating metadata like unstable data can remove objects. In-memory mode lacks file existence checks and relies on cursor open behavior.

Test signals: successful cursor opens after RTS, `WT_NOTFOUND` on empty cursors, file existence in disk mode, and expected `WiredTigerError` after timestamped drop.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable10.py

Purpose: stresses recovery-time RTS, history-store cleanup, checkpoint races, and prepared transactions across two tables. It has one general crash/restart test and a dedicated prepared transaction variant that copies the home before committing prepared updates.

Important APIs/types/functions: `test_rollback_to_stable10` extends the RTS base, uses `checkpoint_thread`, `simulate_crash_restart`, `copy_wiredtiger_home`, `threading.Event`, `time.sleep`, `SimpleDataSet`, `large_updates`, `check`, and `check_hs_stats`. Connection config enables history-store checkpoint delay timing stress, statistics logging, and RTS verbosity.

Control flow: both tests create two tables, write values at 20/30/40/50, advance stable to include 50/60 depending on prepare, start a checkpoint thread, perform more updates while checkpointing, then restart. The prepared variant performs an initial checkpoint, starts prepared transactions on both tables, copies the home while history-store content is present, commits prepared transactions in the original home, and opens the copied home to force recovery.

State and persistence behavior: the tests depend on persisted history-store pages and partial checkpoints. `check_hs_stats` expects recovery RTS to visit pages and remove or sweep history-store entries while not removing keys or restoring keys. The prepared variant checks history-store file size before and after restart.

Dependencies and integration points: integrates threaded checkpoint machinery, recovery simulation, history-store statistics, and prepare timestamp semantics. It is a concurrency regression for interactions among checkpoint, history store, prepared updates, and RTS.

Risks: inherently timing-sensitive; checkpoint timing determines whether work is counted in `txn_rts_hs_removed` or `txn_rts_sweep_hs_keys`. The test accounts for this by asserting the sum is positive rather than exact.

Test signals: data visibility after restart, positive history-store processing, zero explicit RTS calls, no key removals/restorations, positive pages visited, and positive on-disk history-store size in the prepared path.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable11.py

Purpose: validates recovery-time RTS when history-store content must restore a stable update after newer values are checkpointed. It covers row/column key formats and prepared/non-prepared updates.

Important APIs/types/functions: uses `simulate_crash_restart`, `SimpleDataSet`, shared `large_updates`/`check`, `conn.set_timestamp`, `session.checkpoint`, and RTS statistics for calls, key removal/restoration, history-store restore, update abort, and pages visited.

Control flow: writes a sequence of values at increasing timestamps, sets stable to the middle of the sequence, checkpoints unstable content, simulates crash/restart, and verifies reads at and after stable see the correct stable value while earlier timestamps still see their own history.

State and persistence behavior: because later updates are on disk, recovery must use the history store or in-page history to restore a stable value. Prepared mode shifts stable and read timestamps according to commit/durable timestamp rules.

Dependencies and integration points: integrates the recovery helper and `wiredtiger.stat`; inherits RTS log verification through the base class.

Risks: if reconciliation or history-store insertion changes, the exact counter mix can change. The data checks are more stable than individual statistics and protect against visible corruption.

Test signals: post-restart visibility checks plus stats expecting no explicit runtime RTS call, no key deletion/restoration surprises, and recovery work reflected in visited/aborted/history counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable12.py

Purpose: covers recovery RTS when stable content is a remove/tombstone and newer updates must be discarded. It runs row/column formats and prepared/non-prepared updates.

Important APIs/types/functions: class extends `test_rollback_to_stable_base` and uses `large_updates`, `large_removes`, `check`, `simulate_crash_restart`, `session.checkpoint`, `conn.set_timestamp`, and `stat.conn` counters.

Control flow: creates a table, writes an initial value, removes all rows at a timestamp that becomes stable, writes newer values, checkpoints, simulates crash/restart, and verifies that reads at and after stable observe an empty table while older reads still see the original value.

State and persistence behavior: the stable state is a globally meaningful tombstone. Recovery RTS must preserve that tombstone and remove newer updates, including any history-store entries produced by the checkpoint.

Dependencies and integration points: relies on the common helper for prepared remove transactions and on recovery RTS for cleanup. It integrates with history-store and tombstone accounting.

Risks: stable deletes are easy to mishandle because restoring an older value would be incorrect once the remove is stable. Prepared timestamp offsets must match the helper's prepare/commit/durable timestamps.

Test signals: post-restart empty-table checks at stable/newer timestamps, original-value checks at older timestamps, and statistics that show recovery RTS did work without an explicit runtime RTS call.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable13.py

Purpose: validates stable tombstone restoration across multiple variants: simple update/remove/update chains, aborted updates before stable remove, history tombstones, and stable remove combined with dry-run RTS. It covers row/column formats, prepared updates, dry-run mode, and worker counts.

Important APIs/types/functions: extends the RTS base; uses `large_updates`, `large_removes`, explicit cursor writes followed by rollback, `session.checkpoint`, `simulate_crash_restart`, runtime `conn.rollback_to_stable("dryrun=...")`, and `stat.conn.txn_rts_hs_restore_tombstones`.

Control flow: each test pins timestamps at 10, creates a stable value at 20, creates removals or mixed update/remove transactions around 30/40, adds newer unstable updates around 60, checkpoints, and restarts. The stable-remove variant performs a runtime RTS dry-run or real RTS before another checkpoint and restart.

State and persistence behavior: focuses on tombstones restored from the history store. The expected stable state after restart is no rows at stable/newer read timestamps while older reads see the original value.

Dependencies and integration points: depends on history-store tombstone support, recovery RTS, dry-run accounting, prepared timestamp behavior, and RTS log verification via the base class.

Risks: tombstone history is nuanced; aborted updates should not interfere with the stable remove, and dry-run must not mutate state. Counter expectations are exact (`restored_tombstones == nrows`) and may expose implementation accounting changes.

Test signals: visibility checks before and after restart plus exact `txn_rts_hs_restore_tombstones` counts. The dry-run branch verifies that a dry-run does not change final recovery behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable14.py

Purpose: stresses RTS recovery of chains containing full updates plus `wiredtiger.Modify` deltas. It includes three variants: normal modify rollback, repeated modifies at the same timestamp, and append-style modify chains. Formats are column and integer row store, with prepared/non-prepared scenarios.

Important APIs/types/functions: uses helper `large_updates`, `large_modifies`, `check`, local `mod_val`-derived expected strings, `checkpoint_thread`, `simulate_crash_restart`, `stat.conn.txn_rts_hs_restore_updates`, `txn_rts_hs_removed`, `txn_rts_sweep_hs_keys`, and pages-visited counters.

Control flow: creates a base value at timestamp 20, applies multiple byte modifications at 30/40/50/60, advances stable to include part of the chain, checkpoints while applying newer modifications, restarts, and verifies every historical read reconstructs the correct string. Same-timestamp and append variants alter modify ordering and stable point.

State and persistence behavior: requires RTS to reconstruct stable full values from history-store update/modify chains rather than only full updates. Checkpoint races are used to persist history before recovery. Prepared mode skips some runtime combinations where uncommitted prepared transactions would make RTS illegal.

Dependencies and integration points: depends on `wiredtiger.Modify` behavior exposed by the shared helper, threaded checkpoint support, recovery helper, and detailed RTS history-store statistics.

Risks: modify chains are vulnerable to base-value selection, order errors, and same-timestamp edge cases. Background checkpoint timing can change exact `hs_removed` versus sweep counts, so the test uses combined lower bounds.

Test signals: exact reconstructed values at timestamps 20/30/40/50/60, zero explicit RTS calls on recovery, `hs_restore_updates == nrows`, no key restoration/removal, and positive history-store cleanup/visited pages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable15.py

Purpose: tests runtime RTS on fixed-size or integer-style values, ensuring unstable updates are aborted and older stable integer values remain visible. Scenarios include column/integer-row keys, in-memory/disk, and worker counts.

Important APIs/types/functions: class derives directly from `wttest.WiredTigerTestCase`, adds `verify_rts_logs` teardown, and defines a local `check` method. It uses `session.create`, cursor item assignment, timestamped commits, `conn.set_timestamp`, `conn.rollback_to_stable`, and `stat.conn.txn_rts_upd_aborted`/`txn_rts`.

Control flow: creates a table with the scenario key/value format, pins timestamps at 1, inserts value `0x20` at timestamp 2, updates to `0x30` at 5, rolls back to stable 2, checks only the first value remains, then writes further updates at 7 and 9, rolls back to stable 7, and checks the timestamp-7 value remains.

State and persistence behavior: intentionally performs two RTS passes on one table to verify state can be rolled back, updated again, and rolled back again. In-memory mode adds `in_memory=true`; disk mode uses normal persisted tables.

Dependencies and integration points: uses low-level cursor writes rather than the common base helpers, but still integrates with RTS log verification and statistics.

Risks: the source reassigns `value30` before defining `value40`, which is intentional-looking but confusing; report consumers should verify this if changing the test. Fixed-size column behavior can differ from string-value tests.

Test signals: local `check` verifies row counts and values at read timestamps. Stats expect two RTS calls and `(nrows * 2) - 2` aborted updates after the second pass.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable16.py

Purpose: verifies RTS removes whole key ranges that only have unstable updates while preserving earlier ranges. It covers column/integer-row formats, string values, in-memory/disk modes, and worker counts.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`. It defines `insert_update_data` for timestamped range inserts and a local `check` that can expect either a value or missing keys. Uses `conn.rollback_to_stable`, `simulate_crash_restart` import, and stats for updates aborted plus keys removed.

Control flow: creates a table, pins timestamps at 1, writes four disjoint 200-key ranges at increasing timestamps, sets stable to 5, optionally checkpoints, runs RTS, then verifies ranges at timestamps 2 and 5 survive while ranges at 7 and 9 are absent.

State and persistence behavior: the test's core state is key-range existence, not just value replacement. RTS may account for cleanup as update aborts or key removals depending on whether content was reconciled.

Dependencies and integration points: depends on WiredTiger cursor search semantics and `WT_NOTFOUND` behavior through `wiredtiger` imports. It uses scenario-generated formats and RTS logs.

Risks: count expectations combine two counters because eviction/checkpoint state can alter whether deletions are represented as aborted updates or removed keys. In-memory mode changes persistence pressure.

Test signals: range-specific checks and `upd_aborted + keys_removed >= (nrows * 2) - 2`, proving the two unstable ranges were eliminated.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable17.py

Purpose: tests repeated updates of the same key range where RTS should restore the stable value rather than delete keys. It runs row/column formats, in-memory/disk, and worker thread counts.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass using `verify_rts_logs`, local `insert_update_data`, local `check`, `conn.set_timestamp`, optional checkpoint, `conn.rollback_to_stable`, and stats including `txn_rts_upd_aborted` and `txn_rts_hs_removed`.

Control flow: creates a table, writes the same key range with values `aaaa`, `bbbb`, `cccc`, and `dddd` at increasing timestamps, sets stable to 5, checkpoints disk cases, runs RTS, then checks reads at timestamps 2 and 5 return the correct original/stable values while later timestamps return the stable value.

State and persistence behavior: stable keys must remain present and read as the timestamp-5 value after newer updates are discarded. If data is on disk, history-store cleanup may contribute to the stat total.

Dependencies and integration points: uses the WiredTiger test harness and `wiredtiger.stat`; does not use the shared base helper but mirrors its transaction patterns.

Risks: read timestamp selection must align with commits. In-memory and disk modes can produce different accounting, so the test combines update-aborted and history-store removed counts.

Test signals: value checks at 2/5/7/9 and `upd_aborted + hs_removed >= (nrows * 2) - 2`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable18.py

Purpose: tests RTS over an evicted page containing a stable update followed by an unstable remove. It covers row/column key formats, prepared/non-prepared updates, and worker counts.

Important APIs/types/functions: extends the shared RTS base; uses `SimpleDataSet`, `large_updates`, `large_removes`, `check`, an eviction cursor opened with `debug=(release_evict)`, `conn.rollback_to_stable`, and stats for calls and aborted updates.

Control flow: creates a logged-disabled table, pins oldest/stable to 10, writes value at 20, removes all rows at 30, verifies both states, opens a debug eviction cursor and resets it to force reconciliation, sets stable to include only the update (30 for prepared or 20 for non-prepared), runs RTS, then checks the value is visible again.

State and persistence behavior: eviction forces the update/remove chain to disk or reconciled state before RTS. The stable state is the pre-remove value, so RTS must abort the remove and restore visibility.

Dependencies and integration points: depends on WiredTiger debug eviction cursor support and the shared helper's prepared transaction handling.

Risks: eviction may be fragile if page layout changes or if the cursor does not actually trigger reconciliation. The test uses 10,000 rows to improve eviction/reconciliation likelihood.

Test signals: after RTS all rows read as the original value at timestamp 30, one RTS call, and `upd_aborted == nrows`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable19.py

Purpose: validates RTS behavior for no-history and with-history delete/update chains across clean shutdown and crash restart paths. Scenarios include in-memory/disk, row/column keys, and restart mode.

Important APIs/types/functions: extends `test_rollback_to_stable_base`; imports `WT_NOTFOUND`; uses explicit cursor loops, `large_updates`, `large_removes`, debug eviction cursors, `session.checkpoint`, `simulate_crash_restart`, normal reopen/close behavior, and `stat.conn` counters.

Control flow: `test_rollback_to_stable_no_history` creates timestamped updates/removes without a stable history version, evicts deleted pages, sets stable to 20, then restarts or crashes and verifies no data is visible. `test_rollback_to_stable_with_history` first writes stable value at 20, removes at 30, mixes later updates/removes, evicts, sets stable to 40, restarts/crashes, and checks the expected stable/deleted views.

State and persistence behavior: distinguishes cleanup done during orderly shutdown from recovery-time RTS after crash. In-memory and clean-restart paths can have zero startup counters because work already happened during shutdown.

Dependencies and integration points: integrates eviction, checkpoint, recovery simulation, `WT_NOTFOUND` cursor search, and detailed RTS statistics.

Risks: stats are branch-dependent; interpreting clean shutdown like crash would be incorrect. Eviction and checkpoint order determines whether history exists and how counters are charged.

Test signals: visibility checks plus branch-specific assertions for aborted updates, history-store removals, key removal, and zero/positive behavior depending on `in_memory` and `crash`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable20.py

Purpose: regression test for dhandle cleanup during recovery-time RTS. It creates many tables so recovery must open and close many data handles without leaking them.

Important APIs/types/functions: extends the RTS base; uses `SimpleDataSet`, timestamped updates, `conn.set_timestamp`, `session.checkpoint`, `simulate_crash_restart`, and `stat.conn.dh_conn_handle_count`.

Control flow: creates many tables with identical data and timestamped updates, pins oldest/stable around the update time, checkpoints, simulates crash/restart, then reads the connection handle count statistic.

State and persistence behavior: the core state is metadata/dhandle lifecycle rather than row visibility. Recovery RTS scans many objects and should not leave all handles open after restart.

Dependencies and integration points: integrates with WiredTiger dhandle manager, metadata scan during RTS, and recovery simulation. It also uses the common dataset and scenario machinery.

Risks: handle-count thresholds can be sensitive to unrelated open metadata objects. The test uses a low expected count to catch leaks but not exact equality.

Test signals: asserts `open_dhandle_count < 5` after restart, showing RTS did not pin one handle per tested table.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable22.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable22.py

Purpose: stress test for RTS transaction checks while many dhandles and eviction/history-store activity exist. It is designed to make eviction active without letting history-store work interfere with RTS's active transaction validation.

Important APIs/types/functions: extends the RTS base, uses `SimpleDataSet`, repeated large updates across several datasets, `conn.rollback_to_stable('threads=N')`, and scenario worker thread counts. The class sets `conn_config` directly to `cache_size=100MB,verbose=(rts:5)` and disables prepare.

Control flow: creates several tables, populates each, then runs many iterations of 100-byte updates across 1,000 rows to generate around 100MB of activity and trigger eviction. RTS is then invoked under different worker counts.

State and persistence behavior: focuses on concurrent internal state: multiple open dhandles, eviction, history-store activity, and RTS transaction validation. The tables are not primarily used for detailed timestamp visibility checks.

Dependencies and integration points: depends on the shared RTS base, WiredTiger eviction behavior, and the scenario framework. It complements functional rollback tests by exercising resource/transaction coordination.

Risks: workload size and cache behavior make it timing-sensitive. If eviction thresholds or cache behavior change, the intended pressure may weaken.

Test signals: absence of illegal active-transaction failures or data corruption during RTS is the primary signal; scenario completion under all thread counts is meaningful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable22.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable23.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable23.py

Purpose: validates recovery RTS over modify chains and verifies values using explicit `set_key` cursor access. It covers column and integer-row keys plus prepared/non-prepared updates.

Important APIs/types/functions: extends the RTS base; defines `check_with_set_key` to read each key by direct lookup instead of cursor iteration. Uses `large_updates`, `large_modifies`, `session.checkpoint`, `simulate_crash_restart`, and stats including `txn_rts_hs_restore_updates` and `txn_rts_hs_removed`.

Control flow: writes a full base value at 20, applies byte modifications at 30/40/50/60, advances stable to 60 for prepared or 50 otherwise, checkpoints, restarts, then checks direct lookups for expected values at each timestamp up to stable.

State and persistence behavior: recovery RTS must reconstruct stable values from update/modify chains after checkpointed unstable content. Direct lookup checks ensure point-search behavior matches iteration behavior tested elsewhere.

Dependencies and integration points: depends on `wiredtiger.Modify` through shared helper logic, recovery simulation, and history-store restore stats.

Risks: byte-offset modify expectations are brittle if value construction changes. Prepared timestamp shifts must preserve the correct stable boundary.

Test signals: point-lookup checks for every key at historical timestamps, `hs_restore_updates == nrows`, and history-store removal lower bounds, with prepared branches allowing different cleanup counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable23.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable24.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable24.py

Purpose: targets RTS correctness for reconciliation where one key has a newer unstable update and another key is updated after forced eviction. It covers column and integer-row formats and worker counts.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`. Uses manual `session.create`, explicit cursor writes and timestamped commits, debug eviction cursor `debug=(release_evict)`, `conn.set_timestamp`, `conn.rollback_to_stable`, and direct cursor indexing for assertions.

Control flow: writes keys at timestamp 10, updates key 4 at 50, evicts the page, updates key 1 at 30, sets stable to 40, runs RTS, and reads at 40. Expected results are key 1's stable update, unchanged baseline values for keys 2/3, and key 4's value as of the reconciled state.

State and persistence behavior: forced eviction creates on-disk page state before the later update and RTS. The test checks that RTS handles per-key time windows correctly after reconciliation.

Dependencies and integration points: integrates low-level debug eviction with timestamped cursor operations, independent of the common base helpers.

Risks: direct key assumptions are small and precise; if column-store key allocation or eviction behavior changes, the scenario may need adjustment.

Test signals: exact cursor values for keys 1-4 at read timestamp 40 after RTS.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable24.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable25.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable25.py

Purpose: exhaustive scenario test for RTS interactions with RLE cells, uniform versus heterogeneous writes, updates versus deletes, eviction at different times, and rollback stable times. It filters meaningless scenario combinations before running.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`. Defines `is_meaningful`, `writes`, `evict`, and `check`. Uses `filter_scenarios`, `make_scenarios`, cursor removes/updates, debug eviction, timestamped transactions, `WT_NOTFOUND`, and `conn.rollback_to_stable`.

Control flow: creates a row-store table, pins timestamps at 2, writes endpoint rows at 5, applies scenario-selected writes at 10/20/30, optionally evicts after each phase, rolls back to stable 15 or 25, then checks expected visibility at read timestamps 10/20/30.

State and persistence behavior: endpoints bookend an RLE-sized range so reconciliation can generate or preserve RLE cells. RTS must correctly instantiate or prune data depending on whether stable time falls before or after updates/deletes.

Dependencies and integration points: integrates scenario filtering with WiredTiger reconciliation details and cursor search semantics. It is tightly coupled to RLE/time-window behavior.

Risks: scenario explosion is controlled by `is_meaningful`; modifying write-type semantics without updating the filter can create invalid or redundant cases. RLE formation is an implementation detail and may change with reconciliation.

Test signals: `check` verifies endpoints, expected values for every interior key, and `WT_NOTFOUND` for expected deletions at each timestamp after RTS.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable25.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable26.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable26.py

Purpose: tests recovery RTS when a checkpoint races with prepared or unprepared updates, optional history-store removes, and an optional prepared remove. It validates history-store restoration and cleanup after crash.

Important APIs/types/functions: extends the RTS base; imports `checkpoint_thread` and `simulate_crash_restart`; defines `evict_cursor`; uses `large_updates`, `large_removes`, prepared transactions, `stat.conn.checkpoint_state`, and stats including `txn_rts_hs_removed`, `txn_rts_hs_restore_updates`, and key removal counters.

Control flow: writes values at 20 and 30, optionally removes at 40, opens a prepared transaction at 50 that updates or removes one key, sets stable to 40, starts a checkpoint thread and waits for checkpoint state, writes value D at 60, restarts, verifies stable values, and writes value E after recovery to ensure the table remains usable.

State and persistence behavior: combines stable history-store records, prepared state, and concurrent checkpoint persistence. Recovery should restore exactly `nrows` updates from the history store and remove obsolete history-store entries.

Dependencies and integration points: integrates checkpoint threading, prepare handling, eviction/reconciliation, recovery RTS, and statistics.

Risks: checkpoint waiting is timing-sensitive. Prepared remove branches are subtle because unresolved prepared operations can block runtime RTS but recovery must resolve persisted state safely.

Test signals: post-restart data checks, `keys_removed == 0`, `hs_restore_updates == nrows`, `hs_removed == nrows`, then successful post-recovery writes and reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable26.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable27.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable27.py

Purpose: validates RTS with a no-timestamp update over timestamped RLE-like content. Only the non-timestamped key should remain visible after rollback.

Important APIs/types/functions: extends the RTS base; defines local `evict` using `debug=(release_evict)`. Uses `large_updates`, explicit no-timestamp transaction, `conn.rollback_to_stable`, and direct cursor iteration.

Control flow: writes all rows at timestamp 20, evicts to force reconciliation, performs a no-timestamp update for key 7, sets stable to 15, runs RTS, then scans at multiple read timestamps and expects only key 7 with the no-timestamp value.

State and persistence behavior: no-timestamp updates are globally visible and must survive even when all timestamped updates are newer than stable. In-memory/disk and worker thread scenarios cover both storage modes.

Dependencies and integration points: depends on the shared base, debug eviction, and WiredTiger's semantics for no-timestamp updates mixed with timestamped content.

Risks: RLE assumptions are noted in source comments as not directly asserted. If reconciliation does not form the expected shape, coverage weakens but the visible behavior remains checked.

Test signals: cursor scan after RTS asserts the only visible key is 7 and its value is the no-timestamp value, across all checked timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable27.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable28.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable28.py

Purpose: tests recovery RTS with `debug_mode=(update_restore_evict=true)` and verifies write-generation metadata after update-restore eviction. It currently runs the integer row-store scenario.

Important APIs/types/functions: extends the RTS base; `conn_config` enables statistics/RTS verbosity and `conn_recon` adds low cache and update-restore eviction debug mode. Defines `parse_write_gen` using metadata cursor regexes for `write_gen` and `run_write_gen`. Uses `large_updates`, `session.checkpoint`, `simulate_crash_restart`, and `stat.conn.cache_eviction_force_retune`-style update-restore counters.

Control flow: writes stable values through timestamp 40, sets stable to 40, writes newer values at 50/60/70, checkpoints, parses checkpoint metadata write generations, restarts with update-restore eviction enabled, parses metadata again, reads update-restored page stats, and validates all post-stable reads return the timestamp-40 value.

State and persistence behavior: recovery must rollback checkpointed unstable updates and assign newer run write generations to pages it update-restores. The metadata checks prove recovery generated a new write generation above the prior checkpoint base.

Dependencies and integration points: integrates metadata cursor parsing, debug reconciliation configuration, recovery RTS, and stats for update-restored pages.

Risks: regex strings use `\d` in normal string literals, which triggers Python warnings on newer interpreters. Metadata format changes can break `parse_write_gen`.

Test signals: checkpoint `run_write_gen == 1`, checkpoint write gen greater than run write gen, recovery run write gen greater than old checkpoint write gen, recovery write gen greater than recovery run write gen, positive update-restored pages, and stable-value reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable28.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable29.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable29.py

Purpose: validates recovery RTS behavior when a no-timestamp update is written after timestamped history and removals. The no-timestamp value should remain globally visible after crash/restart.

Important APIs/types/functions: extends the RTS base; connection config enables small cache, statistics log, logging, and RTS verbosity. Uses `large_updates`, `large_removes`, an old reader transaction, `session.checkpoint`, `simulate_crash_restart`, and `stat.conn.txn_rts_hs_removed`.

Control flow: writes value A at 10, pins oldest/stable to 10, opens an old reader at read timestamp 10, removes at 30, writes value B at 40, checkpoints, writes value C at 50, then writes value D with no timestamp. It verifies value D at multiple timestamps, checkpoints, restarts, and rechecks value D.

State and persistence behavior: no-timestamp update supersedes timestamped history for visibility and must not be discarded by recovery RTS. The old reader helps preserve history-store content before later operations.

Dependencies and integration points: integrates logging, statistics logging, old-reader history retention, recovery helper, and RTS history-store cleanup.

Risks: no-timestamp semantics can mask older timestamped history; this is intentional. History-store removal counts are non-exact and only asserted nonnegative.

Test signals: value D visible at timestamps 10/20/40/50 and after restart; `hs_removed >= 0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable29.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable30.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable30.py

Purpose: validates that runtime RTS refuses to run while there are active file cursors or active transactions, including prepared transactions, and succeeds after resources are closed/resolved.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`. Uses `SimpleDataSet` and `ComplexDataSet`, row/string key formats, `prepare_resolve`, `assertRaisesWithMessage`, `conn.rollback_to_stable`, `prepare_transaction`, and commit/rollback callbacks.

Control flow: pins oldest/stable to 1, populates a dataset, opens a cursor and asserts RTS fails with an active-cursor message. Then it writes and prepares a transaction at timestamp 10, asserts RTS fails with an active-transaction message, resolves the prepared transaction by commit or rollback depending on test method, closes active resources, and verifies RTS succeeds.

State and persistence behavior: focuses on connection/session state rather than persisted data contents. Prepared transactions hold state that must block RTS until resolved.

Dependencies and integration points: integrates dataset variations, prepared transaction API, and error-message contracts for illegal RTS calls.

Risks: assertions depend on exact diagnostic regexes. ComplexDataSet adds coverage for multi-column schemas but can make setup heavier.

Test signals: expected `WiredTigerError` messages for active cursor/transaction and successful final `rollback_to_stable` for both commit and rollback resolution paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable30.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable31.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable31.py

Purpose: documents and tests RTS behavior when no stable timestamp has ever been set. It compares runtime RTS with recovery-time RTS after crash, with and without checkpoint.

Important APIs/types/functions: extends the RTS base; uses `SimpleDataSet`, `large_updates`, `check`, optional `session.checkpoint`, `simulate_crash_restart`, and `conn.rollback_to_stable`. Scenarios vary row/column format, checkpoint mode, recovery/runtime mode, and worker counts.

Control flow: creates a table without setting oldest/stable, writes values at timestamps 10/20/30, optionally checkpoints, then either simulates crash/recovery or runs explicit RTS. It checks visibility at timestamps 5/15/25/35 based on mode.

State and persistence behavior: runtime RTS should do nothing when no stable timestamp exists. Recovery without checkpoint can lose all uncheckpointed content after crash; recovery with checkpoint preserves checkpointed timestamped data because there is no stable bound for RTS to enforce.

Dependencies and integration points: integrates crash simulation and checkpoint persistence semantics, not just RTS cleanup.

Risks: the expected result differs sharply between crash and runtime paths; future changes to recovery handling of absent stable timestamps must update the documented expectations.

Test signals: explicit value/row-count checks for each mode and checkpoint combination.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable31.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable32.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable32.py

Purpose: tests runtime RTS in a case that triggers update-restore eviction and then validates subsequent writes/checkpoints remain correct. It covers row/column formats, prepared/non-prepared updates, and worker counts.

Important APIs/types/functions: extends RTS base; connection config uses 100MB cache, all statistics, and RTS verbosity. Uses `large_updates`, `large_removes`, `session.checkpoint`, `conn.rollback_to_stable`, explicit cursor no-timestamp or timestamped operations, and `check`.

Control flow: writes value A at 20, value B at 30, removes at 40, sets stable around 40/50 depending on prepare, writes value C at 60, checkpoints, verifies all states, runs RTS, then performs more writes/checkpoints and validates the stable value remains correct.

State and persistence behavior: RTS must handle a stable remove plus newer update and update-restore eviction side effects without corrupting later updates. Prepared scenarios use shifted stable timestamps.

Dependencies and integration points: relies on shared base helpers and WiredTiger reconciliation/update restore behavior.

Risks: exact behavior depends on whether pages are evicted and restored during checkpoint. Test comments indicate it is focused on update-restore eviction, so cache or eviction behavior changes can affect coverage.

Test signals: data checks before and after RTS, especially empty reads at stable remove timestamps and restored values after new updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable32.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable33.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable33.py

Purpose: tests RTS behavior for logged versus non-logged tables in an in-memory connection. Logged objects should not be rolled back the same way as non-logged objects.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `conn_config = 'in_memory=true,verbose=(rts:5)'`, `verify_rts_logs`, `SimpleDataSet`, timestamped cursor writes, `conn.set_timestamp`, and `conn.rollback_to_stable`.

Control flow: creates a table with scenario-selected logging, writes changes at timestamp 30, sets stable to 20, runs RTS, opens a cursor, and checks whether values are the updated values or original dataset values depending on the logging flag.

State and persistence behavior: in-memory plus logging creates a special persistence/rollback boundary. Non-logged updates should be rolled back; logged updates should remain.

Dependencies and integration points: integrates dataset setup, logging configuration, and in-memory connection RTS behavior.

Risks: semantics are table-config dependent; incorrect scenario config can invert expectations. The test is small but covers a behavior not exercised by ordinary disk-backed tables.

Test signals: direct cursor value assertions for keys 10-12, choosing either updated values or original values based on `logged`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable33.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable34.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable34.py

Purpose: validates RTS rollback of fast-delete/truncate operations, including recovery and runtime modes, optional second checkpoint, prepared/non-prepared variants, and column/integer/string row formats.

Important APIs/types/functions: extends RTS base; sets snapshot isolation and logging disabled. Defines `mkdata`, `evict`, and `checkx`. Uses cursor `truncate`, prepared transaction support, `simulate_crash_restart`, `conn.rollback_to_stable`, `stat.dsrc.rec_page_delete_fast`, and worker thread scenarios.

Control flow: writes baseline data at 20 and updated data at 30, evicts pages, sets stable to 25, checkpoints, truncates most of the table at 35 (optionally prepared), verifies fast-delete stats, optionally checkpoints again, then either crashes/restarts or calls runtime RTS. It verifies reads at 20/30 after rollback.

State and persistence behavior: the unstable fast-delete must be undone so all original keys remain visible. Recovery may need to instantiate fast-deleted pages and apply history to restore them.

Dependencies and integration points: integrates fast truncate, eviction, checkpoint, prepare, recovery, and RTS. It covers both fixed column keys and string row keys.

Risks: runtime RTS with uncommitted prepared truncates is skipped because RTS rejects unresolved prepared transactions. Fast-delete stats depend on page layout and may fail if the table does not produce fast-deleted pages.

Test signals: positive fast-delete stats, successful rollback/recovery, and `checkx` validating all `nrows` keys at historical timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable34.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable35.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable35.py

Purpose: reproduces a checkpoint/logging race by copying the WiredTiger home while a checkpoint is stopped under timing stress, then opening the copied home and checking that RTS/recovery does not do unexpected work.

Important APIs/types/functions: extends RTS base; defines local two-table `large_updates` and `check`. Uses `checkpoint_thread`, `copy_wiredtiger_home`, `threading.Event`, checkpoint stop timing-stress statistics, logging with `force_write_wait`, and RTS statistics.

Control flow: creates two tables, writes baseline data, opens a long-running transaction, writes more data, starts a checkpoint thread and waits for checkpoint activity, writes additional data, evicts, waits for checkpoint stop timing stress, copies the home to `RESTART`, completes checkpoint/transaction cleanup, opens the copied home, and verifies latest data.

State and persistence behavior: the copied home represents a checkpoint race snapshot. The test expects recovery to preserve the latest copied state without invoking meaningful RTS work, reflected by zero calls/pages/aborts and nonnegative history-store removal.

Dependencies and integration points: integrates logging, checkpoint timing stress, home copying, two-table consistency, and recovery open path.

Risks: highly timing-sensitive; relies on timing-stress hooks and checkpoint state stats. It can be slow or flaky if checkpoint stop is not reached.

Test signals: two-table value checks after opening the copied home and stats asserting `calls == 0`, `keys_removed == 0`, `keys_restored == 0`, `pages_visited == 0`, `upd_aborted == 0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable35.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable36.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable36.py

Purpose: tests rollback of a checkpointed fast truncate where stable data must be restored. It runs runtime and recovery modes, column/integer row formats, and worker counts.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`. Defines `truncate` supporting real truncate and a disabled remove-loop mode, plus `check`. Uses `session.truncate`, `simulate_crash_restart`, `conn.rollback_to_stable`, `stat.dsrc.rec_page_delete_fast`, and `stat.conn.rec_page_delete_fast_instantiated`.

Control flow: writes baseline data at timestamp 10, sets stable to 10, reopens to clear memory, truncates most keys at timestamp 20, verifies fast-delete occurred, checkpoints, then either restarts or calls runtime RTS. It then checks page-instantiation stats and verifies all rows are visible at timestamps 15 and 25.

State and persistence behavior: unstable fast-delete pages must be instantiated or otherwise restored so stable content is visible. Recovery and runtime paths should both restore table contents.

Dependencies and integration points: integrates fast-delete reconciliation, checkpoint, restart simulation, and RTS page instantiation accounting.

Risks: fast-delete depends on page layout; the remove-loop scenario is commented out, indicating only true truncate currently matters. TSan or slow environments could affect timing less than in checkpoint-race tests.

Test signals: positive fast-delete pages, positive read-deleted/page-instantiated stats for truncate mode, and full row-count/value checks after rollback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable36.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable37.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable37.py

Purpose: tests RTS dry-run versus real mode when a no-timestamp update exists after a long history chain. It ensures dry-run does not mutate state and real RTS retains the no-timestamp value.

Important APIs/types/functions: extends RTS base; connection config uses large cache, statistics log, logging disabled, and RTS verbosity. Uses repeated `large_updates`, an old reader at timestamp 10, checkpoints, `conn.rollback_to_stable('dryrun=...')`, and `stat.conn.txn_rts_keys_removed`.

Control flow: writes 300 timestamped versions of one key range, opens an old reader, writes value B at 2000, writes no-timestamp value C, writes value D at 3000, checkpoints, sets stable to 2000, checkpoints again, runs RTS in dry-run or real mode, then checks visibility around 1000/2000/3000.

State and persistence behavior: no-timestamp value C should be globally visible after real RTS, while dry-run should leave later value D visible at timestamp 3000. Old reader preserves historical content during setup.

Dependencies and integration points: integrates dry-run RTS mode, no-timestamp update semantics, history-store pressure, and stats.

Risks: dry-run and real branches intentionally expect different visibility at the newest timestamp. Misreading the scenario flag can look like corruption.

Test signals: branch-specific checks for value C versus value D and `keys_removed == 0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable37.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable38.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable38.py

Purpose: intended to test history-store btree truncation and fast-delete behavior during recovery RTS over a very large table. The test is currently skipped unconditionally for TSan-related stderr/cache-stuck concerns.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`, snapshot isolation, 50MB cache, `SimpleDataSet`, local `check`, `simulate_crash_restart`, `stat.conn.cache_hs_btree_truncate`, and `stat.dsrc.rec_page_delete_fast`.

Control flow: if not skipped, it would create a one-million-row table, pin a transaction, write one value, write another value, checkpoint, rollback by crashing/restarting, then assert history-store btree truncate and fast-delete page stats are positive.

State and persistence behavior: targets large-scale history-store cleanup and fast-delete interaction during recovery. The pinned transaction is meant to retain history before crash.

Dependencies and integration points: integrates recovery RTS, history-store btree truncation stats, fast-delete stats, and very large dataset creation.

Risks: currently disabled by `self.skipTest("Not compatible with TSan")`, so it provides no active coverage unless the skip is changed. If enabled, it is expensive and sensitive to sanitizer/runtime performance.

Test signals: active signal is the skip. Intended signals are positive `cache_hs_btree_truncate` and `rec_page_delete_fast` stats after restart.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable38.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable39.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable39.py

Purpose: tests checkpoint races where removed stable content and later updates interact with recovery RTS. It covers row/column formats and prepared/non-prepared updates.

Important APIs/types/functions: extends RTS base; uses `checkpoint_thread`, `simulate_crash_restart`, `large_updates`, `large_removes`, retry handling for rollbacks, `stat.conn.checkpoint_state`, and RTS statistics. `conn_config` enables checkpoint slow or history-store checkpoint delay timing stress depending on mode.

Control flow: writes value A at 20, removes at 30, sets stable around 30/40, starts checkpoint thread, writes value C and value B while checkpointing with retry-on-rollback behavior, simulates crash/restart, and validates the stable deleted state plus older history.

State and persistence behavior: the stable point is around a remove, while concurrent checkpoint may persist later updates. Recovery RTS should not count ordinary runtime RTS work and should preserve the stable deleted state.

Dependencies and integration points: integrates checkpoint thread timing, prepared operations, recovery RTS, and history-store stats.

Risks: rollbacks can occur while checkpoint is running, so update logic must retry. Timing affects whether history-store entries are removed or swept, and prepared mode changes stable boundaries.

Test signals: post-restart visibility checks, zero keys removed/restored/update-aborted/history removals for the first stat block, and later checks/stats demonstrating valid history-store cleanup when additional work is present.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable39.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable40.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable40.py

Purpose: regression test for obsolete history-store updates after globally visible updates and eviction reset page time windows. It uses a tiny table to exercise a precise history layout.

Important APIs/types/functions: extends RTS base with snapshot isolation; uses timestamped cursor updates, `session.checkpoint`, `conn.set_timestamp`, debug eviction cursor, `simulate_crash_restart`, and RTS stats.

Control flow: inserts three keys at 20, updates first/last key at 1000, updates middle key repeatedly to create history, checkpoints, pins oldest/stable to 500, evicts the globally visible update, checkpoints to move globally visible updates to a key range, writes another update at 501, opens a read at 1000, restarts, and inspects stats.

State and persistence behavior: tests that obsolete history-store records with larger timestamps are not explicitly removed in a way that corrupts stable/global visibility. Logging is enabled and cache is small to force reconciliation.

Dependencies and integration points: integrates history-store obsolescence, eviction reset of time windows, checkpoint, recovery RTS, and snapshot reads.

Risks: comments describe subtle internal behavior; small changes in reconciliation could change which updates are in history store while preserving visible results.

Test signals: direct eviction read assertion, successful restart, zero RTS calls/key removal/restoration, nonnegative aborted updates, and positive pages visited.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable40.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable41.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable41.py

Purpose: small focused test for `rollback_to_stable(dryrun=true)`: a dry-run must not remove unstable updates, while a subsequent real RTS must remove them.

Important APIs/types/functions: extends RTS base; uses `SimpleDataSet`, `large_updates`, `check`, `conn.set_timestamp`, and two calls to `conn.rollback_to_stable`, first with `dryrun=true` and then real with worker threads.

Control flow: writes value A at 10 and value B at 30, sets stable to 20, runs dry-run RTS and verifies value B is still visible, then runs real RTS and verifies reads at 30 return value A.

State and persistence behavior: no checkpoint or restart is involved; this isolates runtime dry-run behavior on in-memory state.

Dependencies and integration points: uses shared helper methods and worker-thread scenario coverage.

Risks: minimal; primarily catches accidental mutation in dry-run path.

Test signals: value B remains after dry-run; value A is restored after real RTS.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable41.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable42.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable42.py

Purpose: tests reopening a database after an RTS-needed file is deleted externally. It verifies WiredTiger handles missing files during shutdown/startup RTS without crashing.

Important APIs/types/functions: imports `test_rollback_to_stable_base` from `test_rollback_to_stable01`, uses `SimpleDataSet`, `os.remove`, `simulate_crash_restart`, `conn.set_timestamp`, `large_updates`, and `session.checkpoint`.

Control flow: skips tiered storage and Windows because file deletion assumptions are unreliable there. Otherwise it creates `table:test_rollback_to_stable42`, sets stable to 40, writes unstable updates, checkpoints them, removes the table file `test_rollback_to_stable42.wt`, and simulates crash/restart.

State and persistence behavior: deletion occurs after checkpoint so RTS would need the file during shutdown/startup. The intended state is an externally missing data file, not a logical table drop.

Dependencies and integration points: integrates filesystem behavior, recovery RTS, platform-specific skips, and tiered storage capability checks.

Risks: highly platform/storage-engine dependent; tiered storage can obscure file names, and Windows file locking prevents removal.

Test signals: successful restart without uncaught exception is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable42.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable43.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable43.py

Purpose: multi-table RTS test covering dry-run, in-memory/disk modes, row/column formats, and worker counts 0 through 4. It ensures dry-run does not mutate and real RTS rolls many tables back consistently.

Important APIs/types/functions: extends RTS base; uses `SimpleDataSet`, repeated `large_updates` and `check` over ten tables, `session.checkpoint`, `conn.rollback_to_stable('dryrun=...,threads=N')`, and stats for calls, key removal/restoration, pages visited, and aborted updates.

Control flow: creates ten tables, pins oldest/stable to 1, writes values at 10/20/30/40, sets stable to 20, checkpoints disk cases, runs dry-run or real RTS, checks each table according to branch, then inspects stats.

State and persistence behavior: real RTS should remove updates after timestamp 20 across all tables; dry-run should leave the latest value visible. In-memory cases have different update-abort expectations because no disk checkpoint is used.

Dependencies and integration points: integrates multi-dhandle traversal, dry-run mode, in-memory configuration, and worker-thread fanout.

Risks: large scenario matrix can be expensive. Counter expectations differ significantly by dry-run and in-memory flags.

Test signals: per-table visibility checks and stats: one RTS call, no key removal/restoration, positive pages visited in disk cases, zero aborts in dry-run, and real-mode abort counts at least `nrows * 2 * ntables` where applicable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable43.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable44.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable44.py

Purpose: verifies that an uncommitted prepared update evicted to disk has no effect after crash/recovery RTS. It covers column and integer row formats.

Important APIs/types/functions: extends RTS base; defines local `evict` with `debug=(release_evict)` and `ignore_prepare=true`. Uses a second session for the prepared transaction, `prepare_transaction`, `session.checkpoint`, `simulate_crash_restart`, and helper `check`.

Control flow: writes value A to all keys at timestamp 10, opens a second session and prepares an update of the first key at timestamp 20 without committing, evicts the page containing that prepared update, checkpoints, restarts, then checks reads before and after the prepare timestamp.

State and persistence behavior: unresolved prepared update should be ignored/rolled back during recovery; stable/oldest timestamps are deliberately not set. The committed timestamp-10 value remains visible, and prepared value B never appears.

Dependencies and integration points: integrates prepare handling, eviction with ignore-prepare reads, checkpoint, and recovery RTS.

Risks: prepared updates on disk are delicate; failing to ignore unresolved prepare state can expose uncommitted data or fail recovery.

Test signals: empty read at timestamp 5 and value A for all rows at timestamps 15 and 25 after restart.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable44.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable46.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable46.py

Purpose: tests RTS when a table has inserts on multiple pages, eviction/reconciliation has written some stable updates to disk, and later inserts are unstable. It covers column/integer-row scenario names, in-memory/disk, and worker counts.

Important APIs/types/functions: extends RTS base; uses `SimpleDataSet`, manual cursor inserts, transaction read at timestamp 30 to trigger eviction/reconciliation, `conn.rollback_to_stable`, direct cursor searches, `session.checkpoint`, and helper `check`.

Control flow: creates 5,000-row table, pins oldest/stable to 10, inserts 5,000 records at timestamp 20, performs a read at timestamp 30 to trigger eviction/reconciliation, inserts another 2,000 records at timestamp 30, verifies values, checkpoints disk cases, runs RTS to stable 10, then verifies both timestamped insert sets are gone. It also directly searches for the unstable later records before rollback.

State and persistence behavior: because stable is 10, all timestamped inserted records should be deleted by RTS, even if some were already reconciled to disk. In-memory mode disables logging and uses connection in-memory state.

Dependencies and integration points: integrates cursor-level insertion, eviction/reconciliation side effects, checkpoint, and RTS across page boundaries.

Risks: the `format_values` entry named `column` still uses `key_format='i'`, so scenario naming may be misleading. Eviction trigger via read transaction is indirect.

Test signals: direct cursor searches confirm later inserts exist before RTS; after RTS, `check(value_a, uri, 0, 20)` and `check(value_b, uri, 0, 30)` confirm all inserted records were removed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable46.py -->
