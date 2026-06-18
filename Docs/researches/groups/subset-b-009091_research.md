# subset-b-009091 Research

Grouped source research for WiredTiger Python suite tests covering truncate behavior, turtle metadata, transaction visibility/recovery/timestamps, uncommitted update statistics, Unicode metadata, obsolete update pruning, and `wt` utility commands. Each section preserves the source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate20.py

## Purpose
`test_truncate20.py` is a long oplog-like truncate workload. It verifies that repeated range truncation of old records, append of new records, eviction, and checkpoint cleanup do not let the on-disk table file grow without bound.

## Important APIs, Types, and Functions
The file defines `test_truncate20(test_cc_base)`, scenarios for column, integer row, and string row tables, and helpers `append_rows`, `do_truncate`, `evict_cursor`, and `test_truncate`. It uses `SimpleDataSet`, `session.truncate`, debug eviction cursors, connection statistics, `stat.conn.rec_page_delete_fast`, and `test_cc_base.wait_for_cc_to_run`.

## Control Flow
The test populates one million rows, evicts pages with `debug=(release_evict)`, then loops 49 times. Each iteration opens a long transaction to hold visibility, truncates 10,000 starting rows, checks fast-delete stats, appends replacement rows, evicts again, waits for checkpoint cleanup, and checks `oplog.wt` size.

## State and Persistence Behavior
The persisted state is `table:oplog` plus its `oplog.wt` file under logging. The long reader keeps deletes not globally visible while checkpoints and cleanup must still reclaim enough obsolete disk state.

## Dependencies and Integration Points
Depends on `wttest`, `test_cc01.test_cc_base`, `wtdataset.SimpleDataSet`, `wiredtiger.stat`, `os.path.getsize`, and `wtscenario`.

## Risks and Edge Cases
This is resource-heavy and marked longtest. It is sensitive to cache eviction, page layout, checkpoint cleanup timing, and a hard 600 MB disk-size threshold.

## Test Signals
Signals are positive fast-delete page statistics and repeated/final `oplog.wt` size assertions below 600 MB.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate21.py

## Purpose
`test_truncate21.py` tests logging and recovery when a truncate range is repeated and may have no remaining work, including an overlapping insert into the previously truncated range.

## Important APIs, Types, and Functions
The file defines `test_truncate21(wttest.WiredTigerTestCase)`, `trunc_range`, and `test_truncate21`. It uses a small cache, logging, integer row-store keys, `session.truncate`, `session.log_flush`, `copy_wiredtiger_home`, `wiredtiger_open`, and `WT_NOTFOUND`.

## Control Flow
The test creates `table:trunc_row`, inserts 999 committed records one transaction at a time, checkpoints, truncates the middle range, then opens a second session. The first session repeats the truncate while the second inserts the middle key and commits. After the truncate commits, the home is copied, reopened, and the inserted key is searched.

## State and Persistence Behavior
The core state is a logged table and copied home directory `newdir`. Recovery must replay a repeated no-op truncate correctly and must not resurrect or preserve the overlapped key after the truncate transaction commits.

## Dependencies and Integration Points
Integrates WiredTiger Python API transaction/truncate logging with helper-based home copying and restart recovery.

## Risks and Edge Cases
The edge case is a truncate range that already has tombstones while another committed transaction inserts inside that range. Ordering in the log must remain correct.

## Test Signals
After recovery, searching `insert_key` returns `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate22.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate22.py

## Purpose
`test_truncate22.py` verifies that a full range truncate committed at a timestamp removes historical keys after restart/checkpoint and does not leave the first key visible.

## Important APIs, Types, and Functions
The test class uses `SimpleDataSet`, `make_scenarios` for row and column key formats, `timestamp_str`, `conn.set_timestamp`, `session.timestamp_transaction`, `session.truncate`, `session.checkpoint`, and `reopen_conn`.

## Control Flow
It pins oldest and stable timestamps at 1, populates 10,000 rows at commit timestamp 2, reopens, starts a transaction with commit timestamp 5, opens start and stop cursors at keys 1 and `nrows`, truncates that complete range, commits, advances stable timestamp to 10, checkpoints, then searches key 1.

## State and Persistence Behavior
The table's timestamped update chain is persisted across reopen and checkpoint. Stable timestamp advancement makes the truncate durable and checkpointable.

## Dependencies and Integration Points
Depends on WiredTiger timestamp semantics, `SimpleDataSet` key conversion, and the test harness reopen behavior.

## Risks and Edge Cases
The important edge is a range truncate spanning the entire populated dataset after an initial restart. A regression could leave a boundary key visible or fail under column-store key handling.

## Test Signals
The final signal is `assertNotEqual(cursor.search(), 0)` for key 1, proving the key is absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate22.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate23.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate23.py

## Purpose
`test_truncate23.py` exercises truncate boundary behavior with and without prepared transactions, especially records inserted on, outside, and adjacent to truncate bounds.

## Important APIs, Types, and Functions
The class defines `in_range`, `scenario`, and `test_truncate23`. It uses `session.create`, `session.truncate` with URI/start/stop combinations, prepared transaction APIs (`prepare_transaction`, timestamped commit/durable timestamps), and a helper `scenario_num` to generate separate table URIs.

## Control Flow
Each scenario creates a no-logging table, inserts committed boundary records, optionally runs a second prepared transaction inserting the same set, truncates a selected range, commits the truncate, commits the prepared writer if enabled, then scans and compares expected keys and values.

## State and Persistence Behavior
The table is ephemeral test state, but it models timestamped prepared updates interacting with truncate-generated deletes. Values for keys outside the truncated range must persist; values inside the range must be removed or masked according to commit ordering.

## Dependencies and Integration Points
Depends on WiredTiger's prepared transaction protocol, unsigned integer key/value table format, and truncate cursor boundary rules.

## Risks and Edge Cases
The file explicitly covers start-only, stop-only, both-bound, and full-object truncates, plus exact-bound and adjacent-key cases. The test is currently skipped for `FIXME-WT-13232`, making it a known-risk coverage placeholder.

## Test Signals
When enabled, the full cursor scan must match the computed `expect` dictionary for each generated scenario.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate23.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate24.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate24.py

## Purpose
`test_truncate24.py` validates full-table truncate visibility at timestamps, ensuring fast-delete pages are created while readers at an earlier timestamp still see pre-truncate values.

## Important APIs, Types, and Functions
The class uses row and column scenarios plus a timestamp/no-timestamp scenario set. It calls `session.truncate(uri, None, None, None)`, `timestamp_transaction`, timestamped commit, read timestamp transactions, `stat.conn.rec_page_delete_fast`, and `runningHook('disagg')` skip logic.

## Control Flow
The test populates a dataset, reopens, reads values, starts a transaction, timestamps the truncate at 10 when configured, truncates the whole URI, opens a second cursor before commit to verify old values are visible, commits at timestamp 20, verifies fast-delete stats, then reads at timestamp 10 and checks which keys are absent or visible.

## State and Persistence Behavior
It stresses timestamped truncate durability and snapshot reads. Full-table truncate creates page-level fast deletes but historical reads must retain correct older versions.

## Dependencies and Integration Points
Depends on WiredTiger timestamp machinery, connection statistics, `SimpleDataSet`, and disaggregated-storage hook behavior.

## Risks and Edge Cases
Column-store support differs under the disagg hook. Boundary risks include incorrect read timestamp visibility and fast-delete stats not incrementing after full-object truncate.

## Test Signals
Signals are successful pre-commit reads, `fastdelete_pages > 0`, and timestamped post-commit searches returning the expected found/not-found result.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate24.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate25.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate25.py

## Purpose
`test_truncate25.py` verifies that a no-timestamp range truncate after stable checkpointing does not produce fast-delete pages and preserves timestamped visibility semantics.

## Important APIs, Types, and Functions
The class defines `uri`, `nrows`, and `test_truncate25`. It uses timestamped inserts at 30 and 50, `conn.set_timestamp`, `session.checkpoint`, `reopen_conn`, transactions with `no_timestamp=true`, `session.truncate`, `stat.conn.rec_page_delete_fast`, and read timestamp checks.

## Control Flow
Rows are first inserted at timestamp 30, updated at timestamp 50, stabilized and checkpointed, then the connection is reopened. A no-timestamp transaction truncates keys 1 through `nrows`, commits, stats are checked, one more timestamped update occurs at 60, stable is advanced, checkpoint/reopen happens again, and a read at timestamp 30 searches key 1.

## State and Persistence Behavior
The test combines stable checkpoints, non-timestamped deletes, and later timestamped updates. No-timestamp truncate should not fast-delete pages in this historical visibility situation.

## Dependencies and Integration Points
Depends on `SimpleDataSet`, WiredTiger statistics, timestamp APIs, and restart semantics.

## Risks and Edge Cases
Incorrect fast-delete optimization could discard historical values needed for timestamp reads or produce inconsistent replay after reopen.

## Test Signals
The key signal is `fastdelete_pages == 0`; final timestamped search verifies absence at the selected historical read point.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate25.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate26.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate26.py

## Purpose
`test_truncate26.py` checks session ownership validation for truncate cursors: start and stop cursors must belong to the same session that issues `truncate`.

## Important APIs, Types, and Functions
The file defines `test_cursor24(wttest.WiredTigerTestCase)` with `test_cursor24_truncate`. It uses `SimpleDataSet`, two sessions, start/stop cursors opened in different sessions, `session.truncate`, and `assertRaisesWithMessage`.

## Control Flow
After populating a small table, the test opens start/stop cursors from the primary session and from a second session. A truncate with both second-session cursors succeeds. Three mixed-cursor combinations are then attempted from the second session and are expected to fail.

## State and Persistence Behavior
Persistence is minimal; the table is a small validation fixture. The persistent data is less important than the API contract that cursor handles carry session ownership.

## Dependencies and Integration Points
Depends on WiredTiger cursor/session handle validation and the Python test harness error assertion helper.

## Risks and Edge Cases
The risk is accepting a cursor from another session, which can corrupt transaction context, locking, or cursor lifecycle assumptions. Both mixed-start and mixed-stop cases are covered.

## Test Signals
One valid truncate returns 0, and each mixed-session call raises `WiredTigerError` with a message matching "same session".
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate26.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate27.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate27.py

## Purpose
`test_truncate27.py` verifies recovery after timestamped fast truncate, later stable timestamp movement, further updates, checkpoint, and crash restart.

## Important APIs, Types, and Functions
The test defines `evict_cursor`, `get_fast_truncated_pages`, and `test_truncate27`. It uses release-evict debug cursors, column-store table format, timestamped row inserts, `stat.conn.rec_page_delete_fast`, `session.truncate`, checkpoints, and `simulate_crash_restart`.

## Control Flow
It creates and populates 10,000 timestamped rows, advances stable timestamp and checkpoints, evicts pages, checkpoints again, truncates from key 1 to the end at the next timestamp, asserts fast-delete stats increased, advances stable, writes one new row after the truncated range, checkpoints, and simulates crash restart.

## State and Persistence Behavior
The test persists a column-store file with timestamped updates and fast-delete page metadata. Recovery must replay the truncate and later insert without losing consistency.

## Dependencies and Integration Points
Depends on the helper crash restart path, WiredTiger statistics, timestamp APIs, and debug eviction support.

## Risks and Edge Cases
The important edge is fast-delete metadata crossing a crash boundary after timestamps and checkpoints have moved. A missed recovery path may leave deleted rows visible or corrupt the new append.

## Test Signals
The direct signal is `fast_truncates_pages > 0`; successful crash restart without assertion failure completes the recovery check.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate27.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate28.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate28.py

## Purpose
`test_truncate28.py` tests that fast truncate cannot be committed with an invalid timestamp ordering relative to a prepared update, and that the expected timestamp usage error is raised.

## Important APIs, Types, and Functions
The class defines `evict_cursor` and `test_truncate28`. It uses diagnostic/standalone build guards, timestamped inserts, prepared transactions (`prepare_transaction`, `timestamp_transaction` for commit and durable timestamps), stable timestamp movement, eviction, truncate, and `assertRaisesWithMessage`.

## Control Flow
The test skips unsupported builds, populates timestamped rows, creates a prepared update at chosen prepare/commit/durable timestamps, stabilizes and checkpoints, evicts data, then starts a truncate from key 1 and attempts to commit it at an earlier timestamp that violates rules.

## State and Persistence Behavior
The table carries prepared update metadata and timestamped fast-delete candidates. No successful persistence of the invalid truncate is expected.

## Dependencies and Integration Points
Depends on WiredTiger build-mode introspection, prepared transaction validation, timestamps, and error pattern reporting.

## Risks and Edge Cases
This protects against accepting a truncate timestamp that conflicts with prepared update visibility. Build skips mean coverage applies only to non-diagnostic standalone builds.

## Test Signals
The truncate commit must raise `WiredTigerError` with `/unexpected timestamp usage/`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate28.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate29.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate29.py

## Purpose
`test_truncate29.py` checks that fast truncate can operate correctly on variable-sized random byte-like string values and reports fast-delete page statistics.

## Important APIs, Types, and Functions
The class defines `generate_random_string`, `get_fast_truncated_pages`, and `test_truncate29`. It uses `random`, `string`, `SimpleDataSet`, row/column scenarios, `session.truncate`, `session.checkpoint`, and `stat.conn.rec_page_delete_fast`.

## Control Flow
The test populates a file-backed table with 10,000 rows of random string values, checkpoints to make pages durable, records the current fast-delete statistic, truncates a key range using positioned cursors, checkpoints again, and compares the statistic after truncation.

## State and Persistence Behavior
The persisted state is `file:test_truncate29` with random values large enough to exercise page-level storage behavior. Fast-delete metadata should persist through checkpoint rather than expanding into per-key deletes.

## Dependencies and Integration Points
Depends on Python random/string generation, `SimpleDataSet` key handling, and WiredTiger fast-delete statistics.

## Risks and Edge Cases
Random values can vary page packing and may expose assumptions about fixed-size values. The test also risks flakiness if the generated data does not produce pages eligible for fast truncate.

## Test Signals
The main signal is an increase in `rec_page_delete_fast` after checkpointing the truncated range.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate29.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_turtle01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_turtle01.py

## Purpose
`test_turtle01.py` validates the `WiredTiger.turtle` metadata file for both empty and non-empty databases, especially the stored version fields and checkpoint metadata formatting.

## Important APIs, Types, and Functions
The class defines constants for turtle keys and regex formats, plus `init_values`, `test_validate_turtle_file`, `check_metadata`, `find_and_check_wt_version`, `check_turtle`, `find_kv`, and `read_turtle`.

## Control Flow
The test reads the initial turtle file and validates version fields. It then creates `table:test_turtle`, writes 1,000 rows in one transaction, checkpoints, rereads the turtle file, revalidates version fields, and checks that checkpoint metadata in the final line is comma-separated.

## State and Persistence Behavior
The file directly reads persisted `WiredTiger.turtle`. Table creation and checkpointing should update metadata while preserving consistent version key/value pairs.

## Dependencies and Integration Points
Depends on `wttest`, Python `re`, WiredTiger's metadata/turtle file layout, and the local filesystem.

## Risks and Edge Cases
Regex strings use non-raw `\d` escapes, which work today but produce Python syntax warnings. The test assumes turtle file key/value lines and final metadata layout.

## Test Signals
Signals are successful regex matches, equality between numeric version tuple and version-string tuple, and comma-separated checkpoint metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_turtle01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn01.py

## Purpose
`test_txn01.py` covers basic transaction visibility across row/column and file/table object types, and verifies that read-committed is the default isolation level.

## Important APIs, Types, and Functions
It defines `test_txn01` with helpers `cursor_count`, `check_checkpoint`, `check_txn_cursor`, `check_txn_session`, `check`, and `test_visibility`, plus `test_read_committed_default`. It uses `make_scenarios`, transaction begin/commit, checkpoints, and isolation strings.

## Control Flow
`test_visibility` creates a dataset, inserts 1,000 records inside a transaction, periodically checks that the current cursor and read-uncommitted readers see uncommitted rows while snapshot/read-committed and checkpoints see only committed rows, then commits all rows and rechecks. The default-isolation test creates one uncommitted row and verifies a separate reader does not see it.

## State and Persistence Behavior
Checkpoints provide persisted visibility assertions; transactional changes remain isolated until commit. Column-store phantom handling filters only rows with the test value.

## Dependencies and Integration Points
Depends on WiredTiger isolation levels, checkpoint cursors, and scenario generation.

## Risks and Edge Cases
Column-store append phantoms require special counting. Any default isolation change would break the second class.

## Test Signals
Counts for current, read-uncommitted, snapshot, read-committed, and checkpoint readers must match expected committed/total values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn02.py

## Purpose
`test_txn02.py` is a scenario matrix for transaction operations, visibility, and logged recovery across multiple operations and commit/rollback choices.

## Important APIs, Types, and Functions
The class `test_txn02` inherits `WiredTigerTestCase` and `suite_subprocess`. It defines scenario lists for table type, up to four operations, and commit/rollback outcomes, with helpers `conn_config`, `check`, `check_all`, `check_log`, and `test_ops`.

## Control Flow
Each scenario creates a table, performs a sequence of writes/truncates/removes inside transactions, updates expected current and committed dictionaries according to commit/rollback, checks visibility from different isolation levels, then uses a copied/recovered home or log inspection path to verify committed state after recovery.

## State and Persistence Behavior
The test exercises logged table state and transaction state transitions. Only committed operations should survive checkpoints, recovery, and backup-style reads.

## Dependencies and Integration Points
Depends on `suite_subprocess`, `runWt`/log tooling, filesystem log files, `make_scenarios`, and WiredTiger transaction isolation.

## Risks and Edge Cases
The matrix is pruned because the Cartesian product is large. Risk clusters include incorrect rollback of range operations, read-uncommitted visibility errors, and mismatched log replay.

## Test Signals
Dictionary comparisons in `check_all` and recovery/log checks must match the scenario's expected committed state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn03.py

## Purpose
`test_txn03.py` verifies transaction cursor behavior for update/rollback/commit on row-store, variable-length column-store, and fixed-length column-store style scenarios.

## Important APIs, Types, and Functions
The class defines `test_ops` over scenarios carrying create parameters, key, and two values. It uses `session.create`, cursor assignment/search, `begin_transaction`, `rollback_transaction`, and `commit_transaction`.

## Control Flow
The test creates a table, inserts an initial value in a transaction, checks visibility before and after rollback, writes a second value in a transaction, checks same-transaction visibility, commits, and checks that the committed value remains visible.

## State and Persistence Behavior
All state is table-local and transactional. The test confirms that rolled-back writes do not persist and committed writes do, across key formats.

## Dependencies and Integration Points
Depends on `wtscenario.make_scenarios`, the WiredTiger cursor mapping interface, and transaction APIs.

## Risks and Edge Cases
Column-store record numbers and row-store string keys exercise different cursor key paths. A rollback bug could leave dirty cursor state visible.

## Test Signals
Searches and value reads before rollback, after rollback, before commit, and after commit match the scenario values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn04.py

## Purpose
`test_txn04.py` tests transaction visibility and hot backup recovery for simple transactional operations with commit or rollback outcomes.

## Important APIs, Types, and Functions
The class defines `conn_config`, `check`, `check_all`, `hot_backup`, `ops`, and `test_ops`. It uses `suite_subprocess`, `backup:` cursors, filesystem copying, `wiredtiger_open`, and isolation-level checks.

## Control Flow
For each scenario, the test creates a table, applies an operation inside a transaction, checks current and committed visibility before transaction resolution, commits or rolls back, rechecks, then creates a hot backup and opens it to confirm only committed state is present.

## State and Persistence Behavior
The persisted signal comes from a backup directory opened as a separate WiredTiger home. The backup must contain only durable committed changes.

## Dependencies and Integration Points
Depends on WiredTiger backup cursors, transaction isolation, `suite_subprocess`, `os`/`shutil`, and scenario pruning.

## Risks and Edge Cases
Backup taken around active transactions can reveal improper visibility or copied-log ordering. Scenario pruning reduces exhaustive coverage.

## Test Signals
Visibility dictionaries and backup-open reads must equal the expected committed dictionary.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn05.py

## Purpose
`test_txn05.py` checks logged transaction behavior for a scenario set of operations and commit/rollback decisions, with explicit validation of log replay.

## Important APIs, Types, and Functions
The class defines `conn_config`, `check`, `check_all`, `check_log`, and `test_ops`. It uses small log files, disabled log removal, `transaction_sync`, `suite_subprocess`, log file enumeration, and recovery-style validation.

## Control Flow
The test creates a table, performs the scenario operation inside a transaction, checks visible current and committed states under isolation levels, resolves the transaction, forces/log-checks persistence, and validates committed state through log/recovery inspection.

## State and Persistence Behavior
Logged records in `WiredTigerLog.*` are central. Rollbacks must not produce recovered updates, while commits must survive log replay.

## Dependencies and Integration Points
Depends on Python `fnmatch`, `os`, `time`, the suite subprocess harness, `make_scenarios`, and WiredTiger log configuration.

## Risks and Edge Cases
Small log files and operation matrices stress log rotation, transaction sync, and rollback records. Scenario pruning avoids very long combinations.

## Test Signals
Expected dictionaries from `check_all` and `check_log` must align with the committed state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn06.py

## Purpose
`test_txn06.py` verifies long-running snapshots pin transaction state and produce the expected verbose diagnostic output while concurrent inserts allocate new transaction IDs.

## Important APIs, Types, and Functions
The class defines `test_long_running` with row and column scenarios. It uses `SimpleDataSet`, a source table and destination table, two sessions, verbose transaction logging, `captureout.checkAdditionalPattern`, and `ignoreStdoutPattern`.

## Control Flow
The test populates a large source table, opens a cursor in the main session to scan it, creates a destination table, and writes each source row into the destination through a second session. The source scan keeps a snapshot pinned while many inserts advance transaction state.

## State and Persistence Behavior
Persistent table data is incidental; the important state is in-memory transaction ID pinning caused by an active cursor/session snapshot.

## Dependencies and Integration Points
Depends on the capture-output test harness, `SimpleDataSet`, and WiredTiger verbose transaction diagnostics.

## Risks and Edge Cases
The signal is diagnostic-output based and may be sensitive to logging wording or background timing. It also writes 100,000 rows.

## Test Signals
The test requires an output pattern containing "pinned in session" and ignores trailing occurrences during teardown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn07.py

## Purpose
`test_txn07.py` covers truncate operations inside transactions under logging, different transaction sync modes, and log compressors, verifying visibility and backup recovery.

## Important APIs, Types, and Functions
The class defines `conn_config`, `conn_extensions`, `check`, `check_all`, and `test_ops`. Scenarios cover row/column formats, truncate modes (`all`, `both`, `start`, `stop`), commit/rollback, and compressors (`nop`, `snappy`, `zlib`, none).

## Control Flow
The test populates keys 1-5 with large values, begins a transaction, applies the scenario truncate, updates the current expected dictionary, checks visibility under isolation levels and in a copied backup, then commits or rolls back and validates final state.

## State and Persistence Behavior
Logged table state, compressed log records, and backup recovery are all exercised. `session.log_flush(sync=off)` is used before backup to make committed records available.

## Dependencies and Integration Points
Depends on WiredTiger compressor extensions, log configuration, statistics, `suite_subprocess.backup`, and scenario generation.

## Risks and Edge Cases
Missing compressors are skipped. Large values stress compression and log size; truncates exercise cursor-bound range deletes and rollback.

## Test Signals
Isolation-level dictionary comparisons and backup-open checks must match current or committed expectations as appropriate.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn08.py

## Purpose
`test_txn08.py` validates `wt printlog` JSON output when transaction log records contain Unicode keys or values.

## Important APIs, Types, and Functions
The class defines `conn_config` and `test_printlog_unicode`, uses key-format scenarios, `json`, `suite_subprocess.runWt`, and the WiredTiger log subsystem.

## Control Flow
The test creates a logged table, writes rows containing Unicode text through transactions, closes or flushes enough state for log reading, runs `wt printlog`, parses JSON output, and verifies that Unicode content is represented consistently.

## State and Persistence Behavior
The important persistence surface is the transaction log. Unicode data must survive encoding into log records and decoding through the utility's JSON output.

## Dependencies and Integration Points
Integrates WiredTiger transaction logging with the external `wt printlog` command and Python JSON parsing.

## Risks and Edge Cases
Text encoding, JSON escaping, key-format differences, and Python string/bytes conversions are the main risks.

## Test Signals
Parsed printlog records must contain the expected Unicode table/key/value content without parse failures or mojibake.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn09.py

## Purpose
`test_txn09.py` is another transaction operation matrix focused on visibility across up to four operations and commit/rollback combinations without the heavier log-file inspection of neighboring tests.

## Important APIs, Types, and Functions
The class defines scenario dimensions for table types and operation/transaction pairs, plus `conn_config`, `check`, `check_all`, and `test_ops`.

## Control Flow
Each scenario creates a table, performs sequential transactional operations, updates current and committed dictionaries, checks current-session visibility, snapshot/read-committed/read-uncommitted visibility from another session, and resolves each transaction.

## State and Persistence Behavior
State is mostly in the table and active transaction manager. The key invariant is that uncommitted current changes are only visible where allowed and committed state evolves only after commit.

## Dependencies and Integration Points
Depends on `wtscenario.make_scenarios`, `suite_subprocess`, and WiredTiger transaction/isolation APIs.

## Risks and Edge Cases
Scenario pruning means the selected subset must remain representative. Multi-operation sequencing can reveal stale expected-state handling or isolation regressions.

## Test Signals
`check_all` dictionary comparisons across isolation levels must match `current` and `committed`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn10.py

## Purpose
`test_txn10.py` tests recovery correctness for file ID allocation so log records for a table created after restart are not applied to an earlier table.

## Important APIs, Types, and Functions
The class defines `test_recovery`, table URIs `t1` and `t2`, logging configuration with dsync transaction sync, `reopen_conn`, `simulate_crash_restart`, and cursor iteration assertions.

## Control Flow
It creates `t1`, cleanly reopens, creates `t2`, writes 10,000 rows to `t2`, simulates a crash restart, then scans `t2` for all expected rows and scans `t1` to ensure it remains empty.

## State and Persistence Behavior
The test uses logged metadata and data records across a clean restart followed by a crash recovery. File ID mapping must be durable and replay-safe.

## Dependencies and Integration Points
Depends on `helper.simulate_crash_restart`, `suite_subprocess`, and WiredTiger log recovery.

## Risks and Edge Cases
The bug class is metadata/file-ID reuse: recovery might associate `t2` log records with `t1`.

## Test Signals
`t2` contains exactly keys 0-9999 with values key+1, and `t1` contains zero records after recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn11.py

## Purpose
`test_txn11.py` checks empty checkpoints and log removal, ensuring repeated checkpoints can advance beyond original log files and reopening with log removal disabled succeeds.

## Important APIs, Types, and Functions
The class defines dynamic `conn_config`, `run_checkpoints`, and `test_ops`. It uses `SimpleDataSet`, `fnmatch.filter` over `*gerLog*`, repeated `session.checkpoint`, and `reopen_conn`.

## Control Flow
The test populates a source table, records original log files, repeatedly checkpoints until current log files are disjoint from the originals or a 500-checkpoint cap is reached, then changes `remove` to false and reopens.

## State and Persistence Behavior
The state under test is log file lifecycle and checkpoint metadata. Empty checkpoints should permit old logs to be removed/retired without corrupting later opens.

## Dependencies and Integration Points
Depends on filesystem log enumeration, WiredTiger logging/checkpointing, and the test harness reopen path.

## Risks and Edge Cases
The loop can be timing-sensitive if log file retirement is delayed. It assumes log filenames match `*gerLog*`.

## Test Signals
No explicit final value assertion exists; success is reaching reopen without errors after checkpoint/log transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn12.py

## Purpose
`test_txn12.py` verifies that a failed cursor-open configuration operation does not poison the active transaction and prevent commit.

## Important APIs, Types, and Functions
The class defines `test_txn12`, uses `session.open_cursor` with invalid `next_random=bar`, `assertRaisesWithMessage`, read-only and read/write transactions, and commit.

## Control Flow
It opens a read-only transaction, performs a harmless cursor `next`, attempts an invalid cursor open and expects a boolean-configuration error, then commits successfully. It repeats in a read/write transaction after inserting key 123.

## State and Persistence Behavior
The second transaction persists one table update if commit succeeds. The main state is the transaction error flag, which should not be set by this failed open-cursor validation.

## Dependencies and Integration Points
Depends on WiredTiger cursor configuration parsing and transaction error handling.

## Risks and Edge Cases
The edge is differentiating API validation failure from an operation failure that should force transaction rollback.

## Test Signals
Both commits must succeed after the expected `next_random.*boolean` errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn13.py

## Purpose
`test_txn13.py` stress-tests very large logged transaction records. It expects 1 GB and 2 GB aggregate transactions to commit and a 4 GB aggregate to fail.

## Important APIs, Types, and Functions
The class defines dynamic `conn_config`, `test_large_values`, scenarios for row/column keys and value sizes, and uses `wttest.longtest`, `wiredtiger.WiredTigerError`, and `assertRaisesWithMessage`.

## Control Flow
For each scenario, the test creates a logged table with a 20 GB cache, builds a huge string prefix, inserts eight records inside one transaction, and either commits or expects a maximum-size error.

## State and Persistence Behavior
Large update values are logged as part of one transaction. Successful cases persist giant values; the oversized case must fail commit without pretending the transaction committed.

## Dependencies and Integration Points
Depends on WiredTiger log record sizing, Python memory capacity, cache configuration, and longtest scheduling.

## Risks and Edge Cases
This test is extremely memory/disk intensive. It also ignores long eviction warning output that can appear while handling huge values.

## Test Signals
`gotException` must equal `expect_err`; oversized scenarios match `/exceeds the maximum/`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn14.py

## Purpose
`test_txn14.py` verifies `session.log_flush` with `sync=off` and `sync=on`, confirming flushed logged updates survive simulated crash recovery.

## Important APIs, Types, and Functions
The class defines `mkvalue` and `test_log_flush`, scenarios for sync mode and key format, logging with small log files, and `simulate_crash_restart`.

## Control Flow
It creates a table, writes 10,000 rows, calls `log_flush` with the scenario sync value, writes five more rows, flushes again, simulates crash restart, scans the table, and verifies keys and values.

## State and Persistence Behavior
The transaction log is the persistence target. Both flush modes should ensure all writes before crash simulation are recoverable.

## Dependencies and Integration Points
Depends on WiredTiger log flush implementation, crash restart helper, and row/column key format behavior.

## Risks and Edge Cases
`sync=off` still requires records to be written enough for the simulated crash flow used by the test. Off-by-one scan assertions cover record count.

## Test Signals
After recovery, all `entries + extra_entries` rows are present with values `key + 1`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn15.py

## Purpose
`test_txn15.py` validates transaction sync configuration precedence between connection defaults, begin-transaction settings, and commit-transaction settings.

## Important APIs, Types, and Functions
The class defines `conn_config`, `mkvalue`, `syncLevel`, and `test_sync_ops`. Scenarios cover key formats, connection sync enabled/method, begin `sync=` settings, and commit `sync=` settings. It uses `stat.conn.log_release_write_lsn` and `stat.conn.log_sync`.

## Control Flow
Illegal scenarios with both begin and commit sync overrides return early. Legal scenarios create a table, snapshot log write/sync stats, perform one transaction, snapshot stats again, compute expected sync level, and compare stats accordingly.

## State and Persistence Behavior
Persistent data is a committed table update, but the main observed state is logging statistics that indicate whether release code explicitly waited for write or sync.

## Dependencies and Integration Points
Depends on WiredTiger logging stats, transaction sync config parsing, and `skip_for_hook("disagg")`.

## Risks and Edge Cases
Background log worker threads can increment sync stats, so the test only requires sync changes when explicit sync is expected.

## Test Signals
Write LSN stat changes when write/sync is expected; it remains equal when no waiting should occur.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn16.py

## Purpose
`test_txn16.py` tests that repeatedly toggling a database between logging enabled and disabled does not keep generating or reusing incorrect old log files.

## Important APIs, Types, and Functions
The class defines `populate_table`, `run_toggle`, and `test_recovery`, with `conn_on`, `conn_off`, and logging-enabled `conn_config`. It uses `helper.copy_wiredtiger_home`, `wiredtiger_open`, `fnmatch` log enumeration, and manual log removal.

## Control Flow
The test populates three tables with occasional checkpoints, copies the home to simulate crash state, closes the original, then runs the toggle loop on both original and copy. Each loop opens with logging on, records log names, removes logs, opens with logging off, and checks generated log sets.

## State and Persistence Behavior
The persistent state includes checkpointed table files and log files in two home directories. Re-enabled logging must not collide with removed original logs or keep adding new names indefinitely.

## Dependencies and Integration Points
Depends on filesystem log handling, WiredTiger logging/no-logging configuration, and tiered-storage skip behavior.

## Risks and Edge Cases
Manual log deletion is intentionally invasive. The test is skipped for tiered storage.

## Test Signals
Current log sets must be disjoint from original logs and stable across repeated toggles.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn17.py

## Purpose
`test_txn17.py` validates API calls tagged as requiring or forbidding active transactions.

## Important APIs, Types, and Functions
The class defines `test_txn_api` and uses `timestamp_transaction`, `commit_transaction`, `rollback_transaction`, `begin_transaction`, `checkpoint`, `timestamp_str`, and `assertRaisesWithMessage`.

## Control Flow
It first verifies timestamp, commit, and rollback calls fail when no transaction is running. It then begins a transaction and verifies a nested begin is rejected. Finally, it begins another transaction and verifies checkpoint is rejected while the transaction is active.

## State and Persistence Behavior
No durable table state is created. The test focuses on session transaction state and API validation.

## Dependencies and Integration Points
Depends on WiredTiger session API state checks and precise error messages.

## Risks and Edge Cases
Message matching is strict enough to catch wording changes. The timestamp value uses a huge shift but should fail due to state before timestamp size matters.

## Test Signals
Each invalid call raises `WiredTigerError` matching "only permitted in a running transaction" or "not permitted in a running transaction".
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn18.py

## Purpose
`test_txn18.py` verifies `log=(recover=error)` and `log=(recover=on)` behavior before and after recovery is required.

## Important APIs, Types, and Functions
The class defines `mkvalue` and `test_recovery`, scenarios for key format, configs `conn_recerror` and `conn_recon`, `helper.copy_wiredtiger_home`, `wiredtiger_open`, and transaction log recovery assertions.

## Control Flow
The test creates and checkpoints metadata for a logged table, writes 10,000 rows, copies the home to two directories, closes the original, verifies opening with `recover=error` fails while recovery is needed, opens with `recover=on`, validates all data, closes cleanly, then reopens with `recover=error`.

## State and Persistence Behavior
Copied homes represent crash states with unapplied logs. After recovery and clean shutdown, no recovery should be required.

## Dependencies and Integration Points
Depends on helper home copying, log recovery modes, and row/column key scenarios.

## Risks and Edge Cases
If metadata checkpointing is removed, create metadata may not be durable enough. Error message matching depends on "recovery must be run".

## Test Signals
`recover=error` fails before recovery, `recover=on` succeeds and data scans correctly, and `recover=error` succeeds after clean shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn19.py

## Purpose
`test_txn19.py` tests recovery and salvage behavior when transaction log files or core metadata files are corrupted in many ways.

## Important APIs, Types, and Functions
The module-level `corrupt` helper mutates files. `test_txn19` models log corruption with helpers for log-file mapping, expected corruption, recovery failure, recovered record count, and `test_corrupt_log`. `test_txn19_meta` corrupts `WiredTiger`, `WiredTiger.basecfg`, `WiredTiger.turtle`, `WiredTiger.wt`, and `WiredTigerHS.wt` and tests open/salvage expectations.

## Control Flow
Log tests create large records so log files contain predictable record counts, copy a crash home, corrupt selected logs, attempt normal recovery, run salvage, validate recovered records, insert more records, and recover again. Metadata tests create several tables, copy homes, corrupt one metadata file, try normal open, then test salvage paths on two copies.

## State and Persistence Behavior
This file directly mutates persisted log and metadata files and marks the database corrupted. It verifies which damage is fatal, warning-only, openable, salvageable, or recoverable.

## Dependencies and Integration Points
Depends on `helper.copy_wiredtiger_home`, `wiredtiger_open`, salvage config, stdout/stderr pattern expectations, and scenario pruning.

## Risks and Edge Cases
It is highly platform- and message-sensitive. Some combinations are intentionally classified as benign because partial final log records can resemble crash remnants.

## Test Signals
Expected opens fail or succeed with matched errors/warnings, salvage yields expected records where supported, and subsequent recovery preserves inserted records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn20.py

## Purpose
`test_txn20.py` gives a focused isolation-level check for dirty reads and non-repeatable reads across string row and column-store key formats.

## Important APIs, Types, and Functions
The class defines scenarios for `read-uncommitted`, `read-committed`, and `snapshot`, plus `test_isolation_level`. It uses one writer session and one reader session with `begin_transaction('isolation=...')`.

## Control Flow
The test writes an old value, begins a writer transaction, updates the key without committing, then starts a reader transaction at the selected isolation. Read-uncommitted should see the new value while the other levels see old. After writer commit, snapshot still sees old; read-committed and read-uncommitted see new.

## State and Persistence Behavior
State is active in-memory transactional visibility; the table contains one key whose visible version changes by isolation and commit timing.

## Dependencies and Integration Points
Depends on WiredTiger isolation implementation and scenario key conversion.

## Risks and Edge Cases
The test distinguishes dirty reads from non-repeatable reads. Column-store record-number keys must behave the same as row-store keys.

## Test Signals
Value assertions before and after writer commit match the selected isolation semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn21.py

## Purpose
`test_txn21.py` is a smoke test for transaction-level `operation_timeout_ms` configuration.

## Important APIs, Types, and Functions
The class defines `test_operation_timeout_txn`. It passes `operation_timeout_ms=2000` to `begin_transaction`, `rollback_transaction`, and `commit_transaction`.

## Control Flow
The test begins and rolls back a transaction with timeout configured at begin, begins another transaction and passes timeout to rollback, then begins a third transaction and passes timeout to commit.

## State and Persistence Behavior
No table data is created. State is limited to session transaction lifecycle and config parsing.

## Dependencies and Integration Points
Depends on WiredTiger transaction config parsing for begin, commit, and rollback.

## Risks and Edge Cases
This is smoke coverage only; it does not force an operation timeout. It protects against rejecting the option on any of the transaction entry points.

## Test Signals
All three transaction sequences complete without `WiredTigerError`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn23.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn23.py

## Purpose
`test_txn23.py` ensures read timestamps are not cleared or lost under cache pressure while multiple historical versions exist.

## Important APIs, Types, and Functions
The class defines `large_updates`, `check`, and `test_txn`. It uses `SimpleDataSet`, timestamped commit transactions, `conn.set_timestamp`, read timestamp transactions, and a small 5 MB cache.

## Control Flow
Two tables are created. Oldest and stable are pinned at 10. Four rounds of large updates write 2,000 rows per table at timestamps 20, 30, 40, and 50. The test then reads every row at each timestamp and expects the corresponding value.

## State and Persistence Behavior
Each key has a timestamped update chain. Cache pressure from large values should not cause WiredTiger to clear the active read timestamp and return the wrong version.

## Dependencies and Integration Points
Depends on timestamp visibility, history-store/cache behavior, and `SimpleDataSet`.

## Risks and Edge Cases
Small cache plus many large updates stresses eviction. The test may be runtime-heavy because it performs many timestamped transactions and reads.

## Test Signals
Every read at timestamps 20, 30, 40, and 50 returns the value committed at that timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn23.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn24.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn24.py

## Purpose
`test_txn24.py` validates transaction/eviction interaction: eviction threads must make progress under long-running transactions, and verbose logging should identify the session pinning the oldest transaction ID.

## Important APIs, Types, and Functions
The class defines `conn_config`, `get_stat`, `test_snapshot_isolation_and_eviction`, and `test_oldest_id_log`. It uses eviction thread config, verbose transaction output, `wiredtiger.stat.conn.capacity_bytes_evict`, multiple sessions, and `captureout`.

## Control Flow
The first test populates 480,000 rows, checkpoints, starts a long transaction, updates many rows through three other sessions, then asserts eviction wrote bytes before the long transaction commits. The second starts two long transactions, advances many transaction IDs in a third session, commits the oldest, checkpoints, and checks verbose output.

## State and Persistence Behavior
Persistent table updates and cache eviction are both exercised. Transaction ID pinning state drives eviction and verbose diagnostics.

## Dependencies and Integration Points
Depends on WiredTiger eviction threads, capacity stats, verbose transaction messages, and `rollbacks_allowed = 0`.

## Risks and Edge Cases
Large row counts and eviction timing can be sensitive. Output text matching can break on diagnostic wording changes.

## Test Signals
Evicted bytes increase, and output contains "oldest id ... pinned in session".
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn24.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn25.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn25.py

## Purpose
`test_txn25.py` verifies write generation cleanup across restart so old on-disk transaction IDs do not hide the latest data after IDs restart from low values.

## Important APIs, Types, and Functions
The class defines `getkey` and `test_txn25`, with scenarios for row/column keys and logging/no-logging connection configs. It uses a long-running transaction, repeated per-row commits, checkpoint, `reopen_conn`, and read assertions.

## Control Flow
The test creates a file, holds a second session transaction open, writes all rows three times with values A, B, and C in separate transactions, checkpoints to force pages with transaction IDs to disk, rolls back the pinned transaction, reopens, and reads all rows in a new transaction.

## State and Persistence Behavior
The key state is persisted cell transaction IDs/write generations. After restart, transaction IDs begin again, so stale IDs in cells must be wiped or ignored correctly.

## Dependencies and Integration Points
Depends on WiredTiger restart behavior, checkpointing, write generation logic, and scenario-specific key formatting.

## Risks and Edge Cases
Holding transaction IDs around before checkpoint is required to create the on-disk condition. Bugs may show as older values or not-found rows after reopen.

## Test Signals
Every row reads as the final `value3` after reopening.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn25.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn27.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn27.py

## Purpose
`test_txn27.py` validates the error-info API for rollback errors, ensuring the saved rollback reason distinguishes write conflicts from oldest-for-eviction rollback.

## Important APIs, Types, and Functions
The class inherits `error_info_util`, defines `test_rollback_reason`, and uses `assert_error_equal`, `WT_ROLLBACK`, `WT_WRITE_CONFLICT`, `WT_OLDEST_FOR_EVICTION`, `WT_NONE`, small cache configuration, and `SimpleDataSet`.

## Control Flow
Session1 updates key 5 inside a transaction. Session2 tries to update the same key and receives a write conflict; the saved error reason is checked. After rollback clears the error, session1 starts a huge update that pins cache state, sleeps for accounting, then another update triggers rollback due to oldest pinned transaction ID.

## State and Persistence Behavior
No successful durable state is central; it stresses active transaction conflict and eviction rollback metadata.

## Dependencies and Integration Points
Depends on `error_info_util`, WiredTiger rollback reason tracking, cache pressure, and time-based accounting delay.

## Risks and Edge Cases
The eviction rollback path may be timing-sensitive due to `time.sleep(2)`. Error text and reason constants must remain stable.

## Test Signals
Saved error info matches write conflict, clears after rollback, then matches oldest-for-eviction for the cache-pressure rollback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn27.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn28.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn28.py

## Purpose
`test_txn28.py` checks that `conn.debug_info('txn')` reports snapshot arrays whose printed count matches the number of IDs shown.

## Important APIs, Types, and Functions
The class defines regex helpers `get_number_after_substring`, `count_integers_between_substrings`, and `test_snapshot_array_dump`. It uses `expectedStdoutPattern`, `conn.debug_info('txn')`, and reads `stdout.txt`.

## Control Flow
The test creates a table, opens three sessions with active transactions and updates, dumps transaction debug info, scans stdout lines containing `snapshot count`, counts integer IDs inside the `snapshot: [...]` segment, and compares the two counts. It also tracks the maximum count.

## State and Persistence Behavior
State is in-memory transaction snapshot arrays for concurrent transactions. The filesystem is used only to read captured stdout.

## Dependencies and Integration Points
Depends on debug-info formatting, stdout capture naming, regex parsing, and transaction snapshot internals.

## Risks and Edge Cases
The file appears to open `cursor3` from `session2` while beginning `session3`, which may reduce intended coverage or rely on shared transaction state. Formatting changes can break parsing.

## Test Signals
Every printed snapshot count equals the number of integers in its snapshot list, and the maximum list length is 2.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn28.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn29.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn29.py

## Purpose
`test_txn29.py` verifies that a transaction which fails commit after logging an invalid timestamp does not leave rolled-back data recoverable after crash restart.

## Important APIs, Types, and Functions
The class defines `test_transaction_logging`, uses `wiredtiger.diagnostic_build` skip logic, logged and non-logged files, timestamped `commit_transaction(sync=on,commit_timestamp=...)`, `assertRaisesException`, `simulate_crash_restart`, and `WT_NOTFOUND`.

## Control Flow
The test writes `aaaa` to both logged and non-logged files at timestamp 20, then attempts to write `bbbb` at timestamp 10 and expects commit failure. After crash restart, it verifies the non-logged file has no key and the logged file still has `aaaa`, not `bbbb`.

## State and Persistence Behavior
Logged table data should recover the first transaction only. The non-logged table's failed update must not be durable.

## Dependencies and Integration Points
Depends on timestamp validation, transaction logging, crash restart helper, and diagnostic-build behavior.

## Risks and Edge Cases
It specifically protects against a logged transaction becoming unrecoverably partially durable after commit failure.

## Test Signals
The second commit raises, recovery shows `uri2` not found and `uri1` value `aaaa`, and expected timestamp-usage stderr is ignored if present.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn29.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn30.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn30.py

## Purpose
`test_txn30.py` checks that a failed schema operation inside a transaction does not block committing data changes made in that transaction.

## Important APIs, Types, and Functions
The class defines `test_txn30`, uses `session.create(..., exclusive=true)`, `begin_transaction`, cursor update, `assertRaises`, and `commit_transaction`.

## Control Flow
It creates a file exclusively, begins a transaction, inserts key 1, attempts to create the same object again with exclusive create and expects failure, then commits the transaction.

## State and Persistence Behavior
The data update should commit despite the schema create failure. The test does not reopen or read the value; success is no transaction error flag from the failed schema operation.

## Dependencies and Integration Points
Depends on WiredTiger schema API error handling and transaction error-state rules.

## Risks and Edge Cases
Like `test_txn12`, this guards the boundary between API/schema validation errors and transaction-fatal errors.

## Test Signals
The duplicate create raises `WiredTigerError`, and the following commit succeeds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn30.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn_uncommitted.py -->
# sources/storage-engines/wiredtiger/test/suite/test_txn_uncommitted.py

## Purpose
`test_txn_uncommitted.py` validates connection and session statistics for uncommitted transaction updates and dirty bytes.

## Important APIs, Types, and Functions
The class defines `get_sstat`, `get_cstat`, `txn_one`, `txn_two`, `txn_two_seq`, `txn_many`, `txn_many_many`, and `test_session_stats`. It uses `wiredtiger.stat.conn.cache_updates_txn_uncommitted_count`, `cache_updates_txn_uncommitted_bytes`, `stat.session.txn_updates`, and `txn_bytes_dirty`.

## Control Flow
The test creates a table, then runs cases with one session, two concurrent sessions, two sequential sessions, many sessions with one update each, and many sessions with many updates each. After each write, commit, or rollback, it checks connection aggregate counts/bytes and per-session stats.

## State and Persistence Behavior
The durable table data is secondary. The important state is live uncommitted update accounting, which must increase as updates are made and return to zero after commit or rollback.

## Dependencies and Integration Points
Depends on all-statistics connection config, statistics cursors, and many active sessions.

## Risks and Edge Cases
Byte assertions use greater-than or greater-equal because internal overhead exceeds value length and can vary.

## Test Signals
Connection counts/bytes and session update/dirty-byte stats match expected values at each step and reset after transactions resolve.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_txn_uncommitted.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_unicode01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_unicode01.py

## Purpose
`test_unicode01.py` is a smoke test that WiredTiger metadata configuration accepts Unicode text.

## Important APIs, Types, and Functions
The class defines `test_unicode` and calls `session.create('table:t', metadata_string)` with a metadata string containing Unicode characters.

## Control Flow
The test builds a metadata/config string and creates a table. There are no reads or additional assertions; failure would occur during create/config parsing.

## State and Persistence Behavior
The created table's metadata is persisted in WiredTiger metadata files. Unicode content must survive config parsing and metadata storage.

## Dependencies and Integration Points
Depends on `wttest`, Python Unicode string handling, and WiredTiger metadata/config parsing.

## Risks and Edge Cases
This is minimal coverage: it only tests acceptance, not dump/reopen behavior or exact metadata round-tripping.

## Test Signals
The table create call completes without raising a `WiredTigerError`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_unicode01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_update_obsolete_short_chain.py -->
# sources/storage-engines/wiredtiger/test/suite/test_update_obsolete_short_chain.py

## Purpose
`test_update_obsolete_short_chain.py` verifies that obsolete update pruning does not occur too early for a short update chain, but does occur after a checkpoint once enough obsolete history exists.

## Important APIs, Types, and Functions
The class defines `get_stat`, `update_with_ts`, `pin_timestamps`, and `test_short_chain_no_prune_then_prune`. It uses `SimpleDataSet`, timestamped commits, `conn.set_timestamp`, `stat.conn.cache_obsolete_updates_removed`, and checkpoint.

## Control Flow
The test creates a no-logging table, writes value A at timestamp 10 and pins timestamps, records removed-obsolete stats, writes value B at 20 and verifies the stat did not increase, writes value C at 30, checkpoints, verifies obsolete-removal stat increased, and reads the latest value.

## State and Persistence Behavior
The table keeps timestamped update chains for one key. Checkpoint and timestamp pinning govern when obsolete updates can be pruned.

## Dependencies and Integration Points
Depends on WiredTiger history/update-chain pruning, cache statistics, and timestamp APIs.

## Risks and Edge Cases
The important edge is a short chain where aggressive pruning after the second update would be incorrect.

## Test Signals
Obsolete removed count is unchanged after the second update, increases after checkpoint following the third update, and the latest value is `value-c`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_update_obsolete_short_chain.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util01.py

## Purpose
`test_util01.py` tests `wt dump` and dump cursors for byte-array key/value data, printable and hex output, and timestamp-filtered process dumps.

## Important APIs, Types, and Functions
The class defines byte generation/formatting helpers (`get_bytes`, `dumpstr`, `dump_kv_to_line`), comparison helpers, `write_entries`, `dump`, and seven test methods. It uses `wiredtiger.wiredtiger_version`, `runWt(['dump'])`, dump cursors, and timestamped commits.

## Control Flow
Each test creates a `key_format=u,value_format=u` table, writes deterministic binary-like keys and values, builds `expect.out` in the expected dump format, produces `dump.out` via either the `wt` process or dump cursor, and compares the files. Timestamp cases write at two timestamps and dump at a read timestamp.

## State and Persistence Behavior
The table stores all byte values including null terminators. Timestamped cases verify dump reads only versions visible at the requested timestamp.

## Dependencies and Integration Points
Depends on the external `wt dump` utility, dump cursor API, filesystem output files, and binary formatting conventions.

## Risks and Edge Cases
Output is deliberately format-sensitive. The comparison relaxes header config ordering but not data formatting.

## Test Signals
`expect.out` and `dump.out` compare equal for process/API, print/hex, and timestamp cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util02.py

## Purpose
`test_util02.py` tests `wt load` by dumping a populated table, loading it into a renamed table, and validating command-line metadata override handling.

## Important APIs, Types, and Functions
It defines `test_util02` with `get_string`, `get_key`, `get_value`, `dumpstr`, `table_config`, `load_process`, and load tests, plus `test_load_commandline` for command-line error/success combinations.

## Control Flow
The load-process tests create and populate a complex dataset, run `wt dump` optionally with `-x`, create a target table, run `wt load -f dump.out -r target`, and verify key/value formats and content. Command-line tests run `load` with varying trailing config arguments and check stderr presence/absence.

## State and Persistence Behavior
Dumped data is persisted through `dump.out` and reloaded into a second table. Metadata overrides are parsed but should reject invalid or duplicate configurations.

## Dependencies and Integration Points
Depends on `ComplexDataSet`, `suite_subprocess.runWt`, external `wt dump/load`, and scenario formats `SS`, `rS`, `ri`, and `ii`.

## Risks and Edge Cases
Command-line parsing is a major edge surface: invalid URI/config pairs must fail while allowed metadata keys are accepted.

## Test Signals
Reloaded cursor formats and values match originals; command-line cases produce expected empty or non-empty error files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util03.py

## Purpose
`test_util03.py` tests `wt create` for ordinary creation and import-style creation after preserving a dropped file.

## Important APIs, Types, and Functions
It defines `test_util03.test_create_process` over key/value format scenarios and `test_util03_import.test_create_process_import` over file-metadata and repair import modes. It uses `runWt(['create', '-c', ...])`, metadata cursors, `session.drop(remove_files=false)`, and import config.

## Control Flow
The ordinary create test runs the `wt create` command, opens the table, checks cursor key/value formats, and verifies the table is empty. The import test creates/populates/checkpoints a file, saves its file metadata, drops metadata while retaining files, verifies open fails, then recreates with `import=(...)` and reads values.

## State and Persistence Behavior
The import path preserves underlying `.wt` files while removing and reconstructing metadata. Data must remain readable after import.

## Dependencies and Integration Points
Depends on the external `wt create` utility, metadata cursor access, import/repair config, and file retention behavior.

## Risks and Edge Cases
Import metadata must match the preserved file; repair mode has looser expectations. Incorrect config could make a retained file unreadable.

## Test Signals
Cursor formats match requested formats, ordinary tables are empty, dropped files cannot open before import, and imported records read correctly.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util04.py

## Purpose
`test_util04.py` tests the `wt drop` command against a table created through the API.

## Important APIs, Types, and Functions
The class defines `test_drop_process`, uses `session.create`, `tableExists`, `runWt(['drop', ...])`, and `assertRaises` on `session.open_cursor`.

## Control Flow
It creates `table:test_util04.a`, asserts the table exists, runs `wt drop table:test_util04.a`, asserts the table no longer exists, and verifies opening a cursor raises `WiredTigerError`.

## State and Persistence Behavior
The test mutates schema metadata and removes the table object. The dropped table must not remain accessible through metadata or data files.

## Dependencies and Integration Points
Depends on the external `wt drop` utility and the test harness `tableExists` helper.

## Risks and Edge Cases
This is a simple process/API integration test; it does not cover force flags or dependent schema objects.

## Test Signals
Existence transitions from true to false, and cursor open fails after drop.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util07.py

## Purpose
`test_util07.py` validates `wt read` for missing and present string keys, including behavior across explicit connection close/open helper paths.

## Important APIs, Types, and Functions
The class defines `populate`, `close_conn`, `open_conn`, `test_read_empty`, and `test_read_populated`. It uses `runWt(['read', ...])`, output/error files, and file-content check helpers.

## Control Flow
The empty-table test creates a table and runs `wt read` for `NoMatch`, expecting command failure, empty stdout, and "not found" stderr. The populated test inserts uppercase `KEYnn` values, reads `KEY49` successfully, then reads lowercase `key49` and expects not found.

## State and Persistence Behavior
The table contains simple string key/value records. Persistence is accessed through the external `wt` utility after connection lifecycle changes.

## Dependencies and Integration Points
Depends on `suite_subprocess`, external `wt read`, and test harness output-file assertions.

## Risks and Edge Cases
Case sensitivity is an explicit edge: `KEY49` succeeds and `key49` fails.

## Test Signals
Expected stdout/stderr contents and process success/failure states are verified.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util08.py

## Purpose
`test_util08.py` is a smoke test for the `wt copyright` utility command.

## Important APIs, Types, and Functions
The class defines `test_copyright` and uses `suite_subprocess.runWt(['copyright'])` with an output file.

## Control Flow
It runs the utility, reads `copyright.out`, and checks that the text contains the word "Copyright".

## State and Persistence Behavior
No database state is created or persisted. The only file state is the captured command output.

## Dependencies and Integration Points
Depends on the external `wt` binary being available through the test harness and producing copyright text.

## Risks and Edge Cases
The assertion is intentionally broad, so it catches total command failure but not detailed formatting regressions.

## Test Signals
The output file contains "Copyright".
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_util09.py

## Purpose
`test_util09.py` tests `wt loadtext` from a file and stdin, for both empty input and populated text input.

## Important APIs, Types, and Functions
The class defines `populate_file`, `check_keys`, and four test methods. It uses `runWt(['loadtext', ...])`, `infilename`, a string table, and cursor scans.

## Control Flow
Each test creates `table:test_util09.a`, writes `loadtext.in` with either no key/value pairs or a numeric range, runs `wt loadtext` using `-f` or stdin, and scans the table to verify loaded keys and values.

## State and Persistence Behavior
The loaded text creates persistent string-key/string-value table entries. Empty input must leave the table empty; populated input must create exactly the generated pairs.

## Dependencies and Integration Points
Depends on external `wt loadtext`, filesystem input file handling, stdin redirection through `suite_subprocess`, and cursor validation.

## Risks and Edge Cases
Input pair formatting and range boundaries are the main risks. Separate stdin/file modes protect two command paths.

## Test Signals
`check_keys` verifies every expected key maps to its generated value and that no extra keys are present.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_util09.py -->
