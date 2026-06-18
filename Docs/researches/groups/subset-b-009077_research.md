# subset-b-009077 Research

Grouped source research for WiredTiger Python suite files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_random02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor_random02.py

Purpose: verifies that `next_random=true` cursors over an insert-list-heavy table return a reasonable spread of keys and do not simply walk in key order. It scenarios table type with record counts from 1 through 50000.

Important APIs and control flow: `SimpleDataSet.populate()` creates `table:random` with `leaf_page_max=100MB` to avoid page splits. The test opens `session.open_cursor(uri, None, 'next_random=true')`, calls `cursor.next()` once per record, records `cursor.get_key()`, and tracks adjacent sequential returns.

State and persistence: all state is in one populated WiredTiger table and in Python counters (`visitedKeys`, `sequentialKeys`). No restart is involved; the page layout choice is part of the test signal.

Dependencies and integration: depends on `wttest`, `SimpleDataSet`, and `make_scenarios`. It targets the random cursor implementation for insert-list contents.

Risks and test signals: statistical assertions are intentionally loose: more than one quarter of keys must be seen and a multi-row table must not be entirely sequential. Failures indicate broken random distribution or unexpected ordered traversal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_random02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_random03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor_random03.py

Purpose: regression test for WT-12225, where two random cursors opened close together could produce identical streams because the random seed pattern repeated.

Important APIs and control flow: creates `table:random` with exactly 2135 rows and `leaf_page_max=100MB`, then loops 5000 times. Each loop records 100 keys from a first `next_random=true` cursor, closes it, opens a second random cursor, and checks that at least one of the next 100 keys differs at the same position.

State and persistence: state is transient table content plus in-memory `random_keys`. There is no checkpoint or restart; the timing-sensitive risk is exercised by opening cursors back to back.

Dependencies and integration: uses `wttest` and `SimpleDataSet`. The fixed record count is part of the bug reproducer because it shapes random skip-list estimation.

Risks and test signals: a false failure is possible only if two independent random streams happen to match for 100 positions, which is extremely unlikely. Failure points at cursor random seeding or `__wt_random` behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_random03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_tracker.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor_tracker.py

Purpose: reusable cursor test harness, not a standalone test method. It mirrors WiredTiger cursor contents in Python so descendant tests can insert, remove, search, iterate, and verify cursor position and key/value correctness.

Important APIs and types: `TestCursorTracker` extends `WiredTigerTestCase`. It exposes helpers such as `cur_initial_conditions`, `cur_insert`, `cur_remove_here`, `cur_search`, `cur_recno_search`, `cur_first`, `cur_last`, `cur_next`, `cur_previous`, and `cur_check_here`. Encoders map `(major, minor, version)` triples into row-store string keys or column-store recnos.

Control flow: `cur_initial_conditions` populates initial records, closes and reopens the connection to force disk-backed baseline state, then later operations mutate both WiredTiger and Python state (`bitlist`, `vers`, `curpos`, `curbits`, `nopos`, `curremoved`).

State and persistence: Python state distinguishes existing, deleted, positioned, and removed cursor states. Reopening after initial population ensures tests cover both on-disk values and update-list behavior.

Dependencies and risks: uses `wiredtiger`, `wttest`, and `hashlib` for deterministic padding. Since it is a shared harness, mistakes in `bitlist` ordering, recno encoding, or `WT_NOTFOUND` expectations can cascade into many cursor tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_tracker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_info.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_info.py

Purpose: smoke tests the undocumented `WT_CONNECTION::debug_info` entry points for handles, sessions, cursors, special cursors, and backup state.

Important APIs and control flow: `test_debug` wraps `conn.debug_info()` calls with `expectedStdoutPattern`. `conn_cursors` creates a file, inserts keys, positions a cursor by reading key 50, calls `debug_info('cursors')`, and expects positioned-cursor output. `conn_cursors_special` opens `backup:`, `log:`, `metadata:`, and `statistics:` cursors and checks that their URIs appear.

State and persistence: connection logging and fast statistics are enabled. The test creates a file and an incremental backup cursor, but validates stdout diagnostics rather than persisted data.

Dependencies and integration: relies on `wttest` stdout pattern capture and special WiredTiger cursor URI support.

Risks and test signals: output strings such as `Data handle dump`, `Active`, `POSITIONED`, and backup ID `ID1` are brittle but useful integration signals for diagnostic formatting regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_info.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode01.py

Purpose: validates `debug_mode=(rollback_error=N)` by forcing simulated `WT_ROLLBACK` errors during inserts and updates, then confirms the setting can be disabled.

Important APIs and control flow: `rollback_error(val, insert=True)` loops through integer keys, begins a transaction, sets key/value, calls either `cursor.insert()` or `cursor.update()`, and uses `assertRaisesException(..., '/WT_ROLLBACK/', True)` to count simulated conflicts. Conflicting operations roll back; successful operations commit.

State and persistence: data lives in `file:test_debug`. The control signal is transactional success versus rollback; no restart is needed.

Dependencies and integration: uses `wiredtiger.WiredTigerError`, transaction APIs, explicit cursor primitives, and `conn.reconfigure`.

Risks and test signals: with rollback errors enabled, total rollbacks across insert/update phases must exceed `entries // 5`. After `debug_mode=(rollback_error=0)`, rollback count must be zero, catching both failure to inject and failure to reconfigure off.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode02.py

Purpose: tests `debug_mode=(checkpoint_retention=N)` interaction with log file removal and reconfiguration.

Important APIs and control flow: connection config enables logging with `file_max=100K` and checkpoint retention. `advance_log_checkpoint` writes enough data to roll to a new log file, then checkpoints. `check_remove` polls for a named log file to disappear. `test_checkpoint_retain` confirms log sets grow as a superset until retention is exceeded, then the first log is removed.

State and persistence: the test inspects real `WiredTigerLog.*` files under the test home. Checkpoints and log archival are the persistence behavior under test.

Dependencies and integration: uses `suite_subprocess`, filesystem `os.listdir`, `fnmatch`, `time.sleep`, `wiredtiger.WiredTigerError`, and `conn.reconfigure`.

Risks and test signals: timing is inherently asynchronous, so removal polling runs up to 90 seconds. Reconfiguration checks include allowed same-value toggles and a prohibited change to another nonzero retention value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode03.py

Purpose: verifies `debug_mode=(table_logging=true)` causes file-backed table updates to appear in WiredTiger log records, including timestamped operations.

Important APIs and control flow: helper `timestamp(kind, ts)` formats timestamps. `add_data` writes binary values, `add_data_at_ts` commits data at a timestamp, and log-scanning helpers read `WiredTigerLog.*` files looking for value bytes or packed timestamp encodings. Test cases cover table logging enabled, disabled by reconfigure, and timestamp-bearing log records.

State and persistence: real log files are the primary persisted artifact. The table itself is a file URI with binary `value_format`.

Dependencies and integration: uses `struct` to build byte patterns, `wttest`, logging configuration, timestamps, and `conn.reconfigure`.

Risks and test signals: binary log parsing is sensitive to record encoding changes. Passing tests show table logging includes expected data when enabled and stops after `debug_mode=(table_logging=false)`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode04.py

Purpose: simple coverage for `debug_mode=(eviction=true)`, ensuring forced debug eviction mode does not break normal file-table writes and checkpoints.

Important APIs and control flow: `add_data` creates `file:test_debug`, opens a cursor, inserts a set of key/value pairs, closes it, and checkpoints. One test runs with eviction debug mode enabled from `conn_config`; another disables it with `conn.reconfigure('debug_mode=(eviction=false)')` before doing the same workload.

State and persistence: table data is persisted through a checkpoint. The expected behavior is absence of errors rather than a statistic assertion.

Dependencies and integration: uses `wttest`, session create/open cursor/checkpoint, and connection reconfiguration.

Risks and test signals: this is mostly a stability guard. It catches crashes, assertion failures, or configuration plumbing regressions in the debug eviction path but does not prove a specific eviction policy was exercised.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode05.py

Purpose: exercises table logging debug mode with rollback-to-stable behavior, ensuring logged updates and timestamp rollback coexist.

Important APIs and control flow: with logging and `debug_mode=(table_logging=true)` enabled, the test creates a file, writes timestamped values, advances stable timestamps, checkpoints, writes newer values, calls rollback-to-stable, and verifies the stable version is visible.

State and persistence: state spans the update chain, log records, stable timestamp, and checkpointed table content. The core persistence signal is that rollback-to-stable discards unstable updates without corrupting the logged table.

Dependencies and integration: uses `wttest`, timestamps, transaction commit timestamps, `conn.set_timestamp`, checkpoints, and `conn.rollback_to_stable`.

Risks and test signals: this test is vulnerable to timestamp ordering or logging semantics changes. It is an integration guard for debug table logging paths that otherwise tend to be covered by log byte inspection rather than rollback behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode06.py

Purpose: validates `debug_mode=(slow_checkpoint=true)` by making checkpoints deliberately slow and confirming the mode can be disabled.

Important APIs and control flow: `insert_data(assert_time=0)` creates a file, writes one key, calls `session.checkpoint()`, and optionally reads `wiredtiger.stat.conn.checkpoint_time_recent` from `statistics:` to assert the recent checkpoint time is at least a minimum. `test_slow_checkpoints` expects at least 10 ms; `test_slow_checkpoints_off` reconfigures `debug_mode=(slow_checkpoint=false)` and reruns without the timing assertion.

State and persistence: the file is checkpointed, but the key signal is checkpoint latency induced by debug mode.

Dependencies and integration: uses `wttest`, `wiredtiger`, session create/open cursor/checkpoint, and `conn.reconfigure`.

Risks and test signals: timing tests can be environment-sensitive. The value is that it catches loss of slow-checkpoint debug plumbing and validates the reconfigure path for turning it off.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode07.py

Purpose: smoke tests `debug_mode=(realloc_exact=true)` from WT-4919 and confirms it can be turned off.

Important APIs and control flow: `insert_data` creates `file:test_debug_mode07`, writes one string key/value, closes the cursor, and checkpoints. One test runs under the initial debug config; the other calls `conn.reconfigure('debug_mode=(realloc_exact=false)')` before the same workload.

State and persistence: a single record and checkpoint exercise allocation and reconciliation paths where `realloc` is frequently used.

Dependencies and integration: uses `wttest`, session create/open cursor/checkpoint, and connection reconfiguration.

Risks and test signals: there is no direct allocator introspection, so passing means the mode does not break ordinary operation. It is primarily a crash/assertion guard for exact reallocation debug behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode08.py

Purpose: runs inherited base cursor tests with `debug_mode=(cursor_copy=true)` and explicitly tests reconfiguring cursor-copy debug mode off and back on.

Important APIs and control flow: `test_debug_mode08` subclasses `test_base03.test_base03`, so the base suite executes under cursor-copy mode. Its local `test_reconfig` creates a file, opens/writes/closes cursors, reconfigures to `cursor_copy=false`, repeats cursor activity, reconfigures back to the class config, and repeats again.

State and persistence: cursor operations update a file-backed object; persistence is secondary to exercising debug allocation/copy behavior around cursor buffers.

Dependencies and integration: uses `wttest`, `test_base03`, and `conn.reconfigure`.

Risks and test signals: comments note there is no practical way to observe the extra malloc/free behavior directly. The signal is successful execution of broad inherited cursor behavior while the debug flag is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode09.py

Purpose: tests `debug_mode=(update_restore_evict=true)`, which forces update-restore eviction under cache pressure.

Important APIs and control flow: connection config sets a small cache, all statistics, low `eviction_target`, and update-restore debug mode. `trigger_eviction` writes 20000 rows in separate transactions, each with a 500-byte value. The test then reads `stat.conn.cache_write_restore_scrub` from the connection statistics cursor.

State and persistence: repeated committed updates pressure cache and eviction. The statistic is persistent only as runtime stats, not table data.

Dependencies and integration: uses `wiredtiger.stat`, `wttest`, transaction APIs, and `statistics:`.

Risks and test signals: eviction behavior depends on cache pressure. The test mitigates that with a low target and large data volume. Success requires the restore-scrub counter to become greater than zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode10.py

Purpose: smoke tests `debug_mode=(realloc_malloc=true)`, an allocation debug mode that exercises malloc-style reallocation behavior.

Important APIs and control flow: `insert_data` creates `file:test_debug_mode10`, writes one string record, closes the cursor, and checkpoints. `test_realloc_exact` runs with the mode enabled; `test_realloc_exact_off` reconfigures with `debug_mode=(realloc_malloc=false)` and repeats.

State and persistence: the checkpoint is intentionally included because reconciliation and checkpoint code invoke reallocation paths repeatedly.

Dependencies and integration: uses `wttest`, cursor item assignment, `session.checkpoint`, and `conn.reconfigure`.

Risks and test signals: like other allocator debug tests, it does not inspect allocator internals. It catches errors, crashes, or inability to reconfigure while preserving normal file-table behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_debug_mode11.py

Purpose: verifies close configuration `debug=(skip_checkpoint=true)` by checking whether uncheckpointed data survives restart.

Important APIs and control flow: scenarios cover normal close and skip-shutdown-checkpoint close. The test creates a table, writes `ckpt_1st`, explicitly checkpoints, writes `ckpt_2nd` without checkpointing, closes with scenario-specific config, reopens, and uses `verify_key` with `WiredTigerCursor` to search for expected values.

State and persistence: `ckpt_1st` is durable because of the explicit checkpoint. `ckpt_2nd` is durable only if shutdown checkpoint runs during close. No logging is enabled to mask the checkpoint behavior.

Dependencies and integration: uses `wiredtiger.WT_NOTFOUND`, `wttest.skip_for_hook("tiered")`, `make_scenarios`, and `helper.WiredTigerCursor`.

Risks and test signals: clear pass/fail signal is visibility after reopen. Tiered storage is skipped because object persistence semantics differ.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_debug_mode11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dictionary01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dictionary01.py

Purpose: smoke test that dictionary compression is effective for repeated values in row-store and variable-length column-store files.

Important APIs and control flow: scenarios use `key_format=S` and `key_format=r`. The test creates `file:test_dictionary01` with `leaf_page_max=64K,dictionary=100,value_format=S`, inserts 25000 alternating repeated values using `simple_key`, checkpoints, and reads `stat.dsrc.rec_dictionary`.

State and persistence: checkpoint forces reconciliation, where dictionary compression decisions are made. The statistic records dictionary reuse during reconciliation.

Dependencies and integration: uses `make_scenarios`, `simple_key`, `wiredtiger.stat`, and `statistics:<uri>`.

Risks and test signals: alternating values prevent VLCS run-length encoding from collapsing the whole workload. The assertion expects dictionary reuse for almost all entries (`> nentries - 100`), catching dictionary compression regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dictionary01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dictionary02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dictionary02.py

Purpose: verifies dictionary reuse when repeated cells also carry run-length encoding information, especially for VLCS.

Important APIs and control flow: row and variable-column scenarios create a file with dictionary compression. The test pins oldest and stable timestamps at 1, writes two unique large values, then writes keys 3 through 9 with the first value. After checkpoint, it reads `stat.dsrc.rec_dictionary`.

State and persistence: checkpointed reconciliation creates the dictionary entries and RLE encoding. Timestamp pinning prevents global visibility from simplifying the cells unexpectedly.

Dependencies and integration: uses `simple_key`, `make_scenarios`, and `wiredtiger.stat`.

Risks and test signals: expected dictionary counts differ by format: row-store writes seven reused cells, while VLCS RLE collapses them to one reused cell. This catches interactions between dictionary and RLE encoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dictionary02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dictionary03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dictionary03.py

Purpose: tests dictionary reuse when a repeated value also has time-window validity metadata.

Important APIs and control flow: row and variable-column scenarios create a dictionary-compressed file, set oldest and stable timestamps, write two base values, then begin a transaction and write a third key with the first value at commit timestamp 20. After checkpoint, it reads `stat.dsrc.rec_dictionary`.

State and persistence: timestamped transaction metadata becomes part of the reconciled cell. The checkpoint forces the time-window-bearing cell through dictionary compression.

Dependencies and integration: uses `make_scenarios`, `simple_key`, timestamp helpers from `wttest`, and dsrc statistics.

Risks and test signals: the expected dictionary reuse count is exactly one. Failure indicates time-window metadata prevented valid dictionary reuse or statistics accounting changed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dictionary03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dictionary04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dictionary04.py

Purpose: combines the dictionary/RLE scenario with timestamp time-window metadata to verify the encodings compose correctly.

Important APIs and control flow: creates a dictionary-compressed file for row-store and VLCS scenarios, pins timestamps, writes two unique values, then writes keys 3 through 9 with the first value in a timestamped transaction. Checkpoint triggers reconciliation and the test reads `stat.dsrc.rec_dictionary`.

State and persistence: checkpointed cells may include time windows and, for VLCS, RLE metadata. The dictionary statistic is the behavioral signal.

Dependencies and integration: uses `simple_key`, `make_scenarios`, timestamps, and WiredTiger statistics.

Risks and test signals: row-store expects seven dictionary reuses; VLCS expects one because RLE compresses adjacent repeated values. It catches regressions in dictionary eligibility when both RLE and time windows are present.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dictionary04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size01.py

Purpose: validates that disaggregated stable table checkpoint metadata includes a `size=` field and that it reflects compression, growth, and restart persistence.

Important APIs and control flow: `@disagg_test_class` runs a leader layered table. `conn_extensions` loads zstd and disaggregated extensions. `find_checkpoint_size` parses all `,size=N,` entries and returns the latest. Tests create `layered:` tables, write 1000 or 1500 rows, checkpoint, and read `metadata:` for `file:<uri_base>.wt_stable`.

State and persistence: stable table metadata is the ground truth. The restart test reopens after checkpoint and expects the checkpoint size to be unchanged.

Dependencies and integration: uses `DisaggConfigMixin`, disaggregated storage, zstd extension, metadata cursors, and checkpointing.

Risks and test signals: non-compressed size must exceed raw payload threshold; zstd-compressed size must be below it; second checkpoint must grow after more data. Failures indicate metadata size calculation or persistence regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size02.py

Purpose: tests database-level `database_size=` stored in disaggregated checkpoint completion records.

Important APIs and control flow: `get_database_size` parses `disagg_get_complete_checkpoint_meta()`. Tests cover no completed checkpoint error, initial table checkpoint, size increases with inserts, size decreases after removing most rows, similar deltas across multiple btrees, restart preservation, and crash behavior through `simulate_crash_restart`.

State and persistence: size lives in complete checkpoint metadata rather than individual stable file metadata. `disagg_size_buffer` accounts for the 1 MB buffer included for new databases.

Dependencies and integration: uses `@disagg_test_class`, `wiredtiger.WiredTigerError`, layered tables, checkpoint metadata helpers, and crash/restart helper.

Risks and test signals: assertions compare monotonic growth, reduction after truncation, approximate restart equality, and no change after an uncheckpointed crash. Failures point at checkpoint completion accounting or crash recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size03.py

Purpose: regression suite for disaggregated checkpoint-size leaks involving `bytes_total`, page deltas, full-page rewrites, eviction, and cumulative-size reconstruction.

Important APIs and control flow: configured as disaggregated leader with page deltas enabled. `get_checkpoint_size` reads latest stable metadata size. Tests rewrite constant-size data under different `page_delta` settings, inspect `stat.dsrc.rec_page_delta_leaf`, evict pages with `debug=(release_evict)`, force full images by reconfiguring `delta_pct=1`, and compare final sizes to baselines.

State and persistence: state lives in disaggregated stable page images, delta chains, and metadata size fields. Eviction forces pages to be read back from page service to exercise cumulative-size restoration.

Dependencies and integration: uses `DisaggConfigMixin`, page-delta configuration, dsrc stats, metadata cursors, transactions, and debug eviction.

Risks and test signals: size must remain near baseline despite repeated rewrites. Failures indicate leaked old blocks, incorrect delta chain termination, or cumulative-size mis-accounting after eviction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size04.py

Purpose: verifies disaggregated database-level size decreases when layered tables are dropped.

Important APIs and control flow: `get_database_size` parses `database_size` from complete checkpoint metadata. `test_drop_reduces_database_size` checkpoints an empty table, inserts 1000 large rows, checkpoints, drops the table, checkpoints again, and compares sizes. `test_drop_one_of_multiple_tables` inserts equal data into two tables, drops one, and verifies partial reclamation.

State and persistence: drop is queued and only reflected after the next checkpoint, matching WiredTiger metadata and checkpoint semantics.

Dependencies and integration: uses `@disagg_test_class`, layered URIs, `session.drop`, checkpoints, and disaggregated checkpoint metadata.

Risks and test signals: assertions allow metadata overhead slack but require substantial size reduction and surviving table accounting. Failures point at drop cleanup, free block accounting, or database-size metadata updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size05.py

Purpose: ensures `stat.dsrc.block_size` reflects disaggregated checkpoint size for stable files and agrees across slow and fast statistics paths.

Important APIs and control flow: helpers insert rows, read `block_size` from `statistics:<stable_uri>` with `statistics=(all)` and `statistics=(size)`, and parse metadata `size=` as ground truth. Tests cover zero before first checkpoint, agreement with metadata, growth after new checkpoint, correctness after restart, layered URI aggregation, unchanged value without checkpoint even after eviction, and crash survival.

State and persistence: the statistic must reflect the last successful checkpoint, not dirty uncheckpointed data. Restart initializes block manager handles from metadata.

Dependencies and integration: uses `@disagg_test_class`, `wiredtiger.stat`, `simulate_crash_restart`, layered and stable URIs, metadata cursors, and debug eviction.

Risks and test signals: mismatches indicate fast-path metadata reads, slow-path dhandle initialization, or checkpoint/crash accounting regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size06.py

Purpose: tests checkpoint-size accounting for disaggregated delta chains, especially WT-16864 scenarios where full-image replacement should obsolete prior delta cumulative sizes.

Important APIs and control flow: helpers read checkpoint size from stable metadata, insert rows, evict a page with `debug=(release_evict)`, and read dsrc/connection stats. Tests build baseline pages, create deltas with `delta_pct=90`, evict to force page-service readback, reconfigure `delta_pct=1` to force full images, checkpoint, and compare size bounds across cycles.

State and persistence: the target state is page-log full images and deltas plus metadata `size=`. Eviction and reconfiguration intentionally move through delta-chain termination paths.

Dependencies and integration: uses `DisaggConfigMixin`, `@disagg_test_class`, page delta config, `wiredtiger.stat`, metadata cursors, and debug eviction.

Risks and test signals: checkpoint size must drop or stabilize after full-image replacement rather than accumulate old deltas. Failures indicate cumulative-size double counting or error-path leaks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_corruption_mixin.py -->
# sources/storage-engines/wiredtiger/test/suite/test_disagg_corruption_mixin.py

Purpose: exercises `DisaggCorruptionMixin` helpers against palite-backed disaggregated storage to ensure corruption utilities mutate page-log rows as intended.

Important APIs and control flow: scenarios come from `gen_disagg_storages(..., disagg_only=True)`, but each test skips unless `ds_name == 'palite'`. `_populate` writes ten layered rows and checkpoints. Tests call mixin helpers to corrupt a page image, delete a page image, mark a page discarded, and truncate a delta chain; each then queries palite SQLite data with `sqlite_select_json`.

State and persistence: persistent state is palite `pages` rows, including `page_data`, `flags`, `discarded`, page IDs, LSNs, and delta chains.

Dependencies and integration: uses `DisaggCorruptionMixin`, disaggregated extension configuration, `make_scenarios`, and SQLite-backed palite inspection.

Risks and test signals: asserts byte `FF`, deleted row count zero, discarded flag mask set, and delta chain reduced to the kept LSN. Failures break corruption-test infrastructure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_corruption_mixin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_util01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_disagg_util01.py

Purpose: validates automatic pickup of latest disaggregated checkpoints in library leader mode and through the `wt` utility in follower mode.

Important APIs and control flow: `test_leader_auto_pickup` writes rows as leader, checkpoints, steps down to follower, restarts without local files as leader, verifies rows, and checkpoints new writes. `_run_wt_as_follower` closes the leader, creates a follower home symlinked to `kv_home`, loads the page-log extension path, and runs `wt` with follower config. Other tests check `wt list`, no-checkpoint stderr, and latest-checkpoint dump content.

State and persistence: checkpoint metadata and page-log contents are shared across leader/follower homes; local files are intentionally removed or separate.

Dependencies and integration: uses `@disagg_test_class`, `suite_subprocess`, `wt_builddir`, page-log extension discovery, symlinks, and utility output.

Risks and test signals: checks row visibility, `layered:` listing, `no complete checkpoint found`, and absence of old values. Failures indicate pickup or utility follower regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_util01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_util02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_disagg_util02.py

Purpose: tests the diagnostic `wt page` command against palite-backed disaggregated storage, covering help, validation errors, full page images, and delta chains.

Important APIs and types: `PalitePage` is a `NamedTuple` matching palite page table fields. `test_disagg_wt_page` configures a leader layered table, computes page-log follower config, runs `wt page`, populates rows, dirties subsets, and queries palite SQLite via the built `sqlite3`.

State and persistence: page-log state includes table IDs, shard DBs, page IDs, LSNs, base/backlink LSNs, and flags. The command output is validated against these stored page-chain headers.

Dependencies and integration: uses `DisaggConfigMixin`, `get_shard_id`, `get_table_id`, `wt_builddir`, `suite_subprocess`, `wiredtiger.diagnostic_build()`, and skips tiered hooks.

Risks and test signals: diagnostic builds only. It asserts required argument errors, `WT_NOTFOUND`, full-image count 1 with row-store output, and delta-chain count greater than 1.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_disagg_util02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_drop.py -->
# sources/storage-engines/wiredtiger/test/suite/test_drop.py

Purpose: broad coverage for `WT_SESSION.drop` across files, simple tables, indexed tables, complex tables, cursors, transactions, reopen, and non-existent URIs.

Important APIs and control flow: scenarios cover `file:` and `table:`. Helper `drop` populates a dataset in a transaction, verifies open-cursor drop failure, verifies active-transaction EBUSY and rollback requirement, optionally reopens, chooses data or index URI, calls `dropUntilSuccess`, and confirms absence. `test_drop_dne` checks force succeeds on missing file/colgroup/index while non-force fails.

State and persistence: datasets may include indices and column groups. Reopen validates persisted state before drop.

Dependencies and integration: uses `SimpleDataSet`, `SimpleIndexDataSet`, `ComplexDataSet`, `confirm_does_not_exist`, `wiredtiger`, and skip for tiered storage.

Risks and test signals: catches incorrect busy handling, dirty transaction cleanup, dropped-index behavior, metadata removal, and force semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_drop.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_drop01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_drop01.py

Purpose: intended to test that dropping a table removes associated history-store records, but the test is currently skipped for known WT-16857.

Important APIs and control flow: helpers commit timestamped updates to a two-column-group table and count entries by opening `file:WiredTigerHS.wt`. The skipped test creates column groups, writes two timestamped versions of one key, checkpoints, expects two history-store records, drops the table, and expects history-store size zero.

State and persistence: covers timestamped updates, checkpoint-created history-store records, and drop cleanup across column groups.

Dependencies and integration: uses `wttest`, `unittest.skip`, timestamp commit strings, history store file cursor, table/colgroup metadata.

Risks and test signals: because it is skipped, it documents a desired invariant rather than enforcing it. If enabled, failures would indicate incomplete history-store truncation on drop.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_drop01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_drop03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_drop03.py

Purpose: tests dropping a table around an active transaction and dirty content, with explicit force true/false semantics.

Important APIs and control flow: writes initial values, verifies them, starts a transaction that overwrites values, then `session.drop(uri, "force=false")` must raise busy. The active transaction still sees new values; commit must fail with "transaction requires rollback"; after rollback, old values are visible. A later non-force drop of dirty table still fails, while `force=true` succeeds.

State and persistence: table content transitions between committed base values, uncommitted transactional values, rollback, dirty table state, and final metadata removal.

Dependencies and integration: uses `confirm_nonempty`, `confirm_does_not_exist`, `raisesBusy`, and `wiredtiger.WiredTigerError`.

Risks and test signals: covers important user-visible drop semantics: active transaction protection, rollback requirements, and missing-table force behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_drop03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_drop04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_drop04.py

Purpose: regression test for WT-15225, repeatedly creating and dropping an empty logged table after checkpoint cleanup.

Important APIs and control flow: `test_drop04` extends `test_cc_base`, enabling checkpoint cleanup coordination. With logging enabled, `test_drop_after_bulk_load` loops 100 times: create `table:test_drop04`, wait for checkpoint cleanup using `wait_for_cc_to_run`, then drop with `force=false`.

State and persistence: the table is empty but logged. The test stresses metadata, logging, and checkpoint cleanup interactions rather than data content.

Dependencies and integration: imports `test_cc_base`, uses `wttest`, logging config, and checkpoint cleanup helpers.

Risks and test signals: repeated success is the signal. Failures would expose races or stale metadata state when dropping recently created empty logged tables after checkpoint cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_drop04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_drop_create.py -->
# sources/storage-engines/wiredtiger/test/suite/test_drop_create.py

Purpose: tests repeated drop/create cycles and session table-cache invalidation when a table name is reused with different schema.

Important APIs and control flow: `test_drop_create` closes the default session, opens a new one, repeatedly force-drops and creates `table:test` with string schema, drops it, closes/reopens sessions, and creates again. `test_drop_create2` uses two sessions: one creates and drops the table, the other opens cursors before and after recreation with a different value format.

State and persistence: metadata for `table:test` is removed and recreated. The important state is per-session table cache awareness after drop and schema change.

Dependencies and integration: uses raw WiredTiger session APIs through `self.conn.open_session()`, `create`, `drop`, `open_cursor`, and explicit session close.

Risks and test signals: failures indicate stale cached schema or incorrect table name reuse across sessions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_drop_create.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dump.py

Purpose: end-to-end `wt dump` and `wt load` coverage for files, simple tables, indexed tables, complex tables, key formats, and text/hex dump modes.

Important APIs and control flow: scenarios combine object type, key format, and dump format. The test populates a dataset, runs `wt dump` optionally with `-x`, loads into a separate home, compares `wt list`, reopens that home and checks content, reloads into original home, verifies `load -n` fails on overwrite, dumps complex-table index content, and tests `load -r` rename.

State and persistence: dump files, separate home directories, loaded metadata, table data, and index data are all validated.

Dependencies and integration: uses `suite_subprocess`, `SimpleDataSet`, `SimpleIndexDataSet`, `ComplexDataSet`, `shutil`, and filesystem directories.

Risks and test signals: validates utility compatibility with schema metadata and data values. Differences in value lines, missing list entries, or empty error output signal dump/load regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dump01.py

Purpose: tests `wt dump -px`, the pretty-hex mode that prints keys in pretty form and values in hex form.

Important APIs and control flow: creates `table:test_dump` with integer keys and byte-array values. `get_bytes` generates deterministic binary values with a trailing null. The test writes values, runs `wt dump -x`, `wt dump -p`, and `wt dump -px`, then compares outputs line by line.

State and persistence: dumped output files are the primary artifacts. Table data includes bytes that require escaping/hex encoding.

Dependencies and integration: uses `suite_subprocess`, external `wt dump`, and file reads.

Risks and test signals: header lines must match pretty output except `Format=print hex`, data start must align, keys must match pretty output, and values must match hex output. It catches formatting regressions in utility output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dump02.py

Purpose: tests key filtering and lower/upper bound options in `wt dump`.

Important APIs and control flow: populates `table:test_dump` with byte-array keys `key1` through `key99`. `get_num_data_lines_from_dump` finds the `Data\n` header and counts data lines. Test cases run full dump, exact key `-k`, nearest `-k ... -n`, lower bound `-l`, upper bound `-u`, and combined bounds.

State and persistence: output file `dump.out` is overwritten for each utility invocation. Each record contributes two data lines, key and value.

Dependencies and integration: uses `suite_subprocess`, `wt dump`, and file parsing.

Risks and test signals: expected line counts encode lexicographic key ordering, including surprising string ranges such as `key6` through `key9` with lower bound `key50`. Failures indicate bound or nearest-key semantics changed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dump03.py

Purpose: verifies `wt dump -k KEY -w WINDOW` returns the requested key plus a symmetric window around it, clipped at table boundaries.

Important APIs and control flow: scenarios specify key, window size, and expected data line count. The test populates `key1` through `key99`, runs `wt dump -k <key> -w <winsize>`, then counts lines after the `Data` header.

State and persistence: table content is stable during a single utility run. Output line count is the validation surface, with two lines per record.

Dependencies and integration: uses `suite_subprocess`, `make_scenarios`, and utility dump output.

Risks and test signals: boundary scenarios at start/end and zero window catch off-by-one errors in window expansion and clipping.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dump04.py

Purpose: tests `wt dump -j` JSON output combined with `-k` key filtering.

Important APIs and control flow: creates a byte-array key/value table with three records. Helpers format expected plain or JSON/unicode strings, assert file contains or omits key/value pairs, and load the output through `json.load` for validity. `run_test` builds dump args with optional `-j` and `-k`.

State and persistence: checkpoint flushes dirty pages before utility dumps. The output file is inspected across JSON and non-JSON formats.

Dependencies and integration: uses `suite_subprocess`, `json`, file content regex helpers, and `wt dump`.

Risks and test signals: catches JSON escaping issues, key filtering with matching and non-matching keys, and invalid JSON. The method name `check_valid_jason` is misspelled but functional.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dump05.py

Purpose: validates JSON formatting from `wt dump -j` for string and byte-array tables with many variable-length records.

Important APIs and control flow: `validate_json_dump` creates a table, writes 1000 random-length key/value suffixes, runs `wt dump -j`, then uses regex file checks to ensure no junk appears after closing quotes and valid key/value JSON records exist. It runs once for `key_format=S,value_format=S` and once for `key_format=u,value_format=u`.

State and persistence: output is utility-generated JSON. Random record lengths stress buffer reuse and termination boundaries.

Dependencies and integration: uses `suite_subprocess`, Python `random`, and file regex helpers.

Risks and test signals: it is focused on output cleanliness rather than parsing with `json.load`. Failures point to stale buffer bytes, quote handling, or JSON field formatting regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dump05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dupc.py -->
# sources/storage-engines/wiredtiger/test/suite/test_dupc.py

Purpose: tests cursor duplication through `session.open_cursor(None, cursor, None)`.

Important APIs and control flow: scenarios cover file/table and recno/string key formats. `iterate` walks the dataset with a cursor; at each positioned row it duplicates the cursor, compares original and duplicate with `cursor.compare(dupc)`, verifies the duplicate key, closes the original, and continues iteration using the duplicate.

State and persistence: datasets are fully populated before iteration. The test then drops the object before running a complex table scenario.

Dependencies and integration: uses `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, `wiredtiger.WT_NOTFOUND`, and `dropUntilSuccess`.

Risks and test signals: exact key equality, compare result zero, full row count, and final `WT_NOTFOUND` validate duplicate cursor positioning and lifetime. Tiered storage is skipped because the complex column-store sequence is not compatible there.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_dupc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_durability01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_durability01.py

Purpose: checks metadata durability after exclusive operations such as verify close file handles and flush data files.

Important APIs and control flow: creates a table, then for 100 iterations writes one row, either checkpoints every fifth row or calls `verifyUntilSuccess` on other iterations, copies the live WiredTiger home to `RESTART`, opens the copy, verifies, and closes it.

State and persistence: the live copy simulates a crash snapshot. The test is looking for metadata checkpoints staying in sync with data files after verify-triggered file close.

Dependencies and integration: uses `copy_wiredtiger_home`, `suite_subprocess`, `setUpConnectionOpen`, `setUpSessionOpen`, and `verifyUntilSuccess`.

Risks and test signals: verification in copied homes must always succeed. Failures suggest metadata was not durably checkpointed while data files changed, creating restart inconsistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_durability01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_durable_rollback_to_stable.py -->
# sources/storage-engines/wiredtiger/test/suite/test_durable_rollback_to_stable.py

Purpose: validates durable timestamp visibility and rollback-to-stable behavior for prepared transactions.

Important APIs and control flow: scenarios cover file/table simple row formats. The test populates 50 records, checkpoints at stable timestamp 100, prepares and commits value 111 at commit 200 durable 220, verifies reads at timestamp 150 and 220, then prepares value 222 with commit 240 but durable 300 while stable is 250. After checkpoint, latest reads see 222, then `conn.rollback_to_stable()` must restore 111.

State and persistence: state includes prepare, commit, durable timestamps, stable timestamp, checkpoint, and rollback-to-stable. Utility `wt verify -s` checks flushed state afterward.

Dependencies and integration: uses `SimpleDataSet`, `make_scenarios`, `suite_subprocess`, timestamp APIs, prepared transactions, and `rollback_to_stable`.

Risks and test signals: catches durable timestamp ordering mistakes where updates visible before rollback are incorrectly retained or discarded after RTS.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_durable_rollback_to_stable.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_durable_ts01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_durable_ts01.py

Purpose: tests durable timestamp recovery across restart, ensuring only updates durable at the stable timestamp survive recovery.

Important APIs and control flow: scenarios cover file/table simple datasets, key formats excluding column store, and read isolation modes. The test follows the durable timestamp pattern: checkpoint initial data at stable 100, commit value 111 with durable 220, verify timestamped visibility, commit later value 222 with commit before stable but durable after stable, checkpoint, restart, and verify recovery shows the durable 111 state.

State and persistence: checkpoint and restart are central; recovery should rollback updates whose durable timestamp exceeds stable. The class skips disaggregated storage because RTS does not run during disaggregated recovery.

Dependencies and integration: uses `SimpleDataSet`, `make_scenarios`, timestamp APIs, sessions with isolation variants, and connection reopen/restart behavior.

Risks and test signals: failures indicate recovery/RTS mishandles durable timestamps, especially prepared or checkpointed unstable updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_durable_ts01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_durable_ts02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_durable_ts02.py

Purpose: negative durable timestamp validation test for prepared transactions.

Important APIs and control flow: the class is named `test_durable_ts03` in this file. It creates a simple dataset, opens a separate session/cursor, sets stable timestamp 100, and checkpoints. The active code path is a large commented block documenting two disabled scenarios: committing with durable timestamp lower than commit timestamp should raise "is less than the commit timestamp", and committing with durable timestamp lower than stable timestamp should raise "is less than the stable timestamp".

State and persistence: current executable code only creates and checkpoints initial data, then leaves the negative scenarios commented out because the source notes the system panics if failure is injected after preparing a transaction.

Dependencies and integration: uses `SimpleDataSet`, `make_scenarios`, session isolation configs, timestamp helpers, prepared transactions in the disabled block, and `wiredtiger.WiredTigerError` references inside that disabled block.

Risks and test signals: as written, this is mostly a placeholder/documented regression case with weak active assertions. If re-enabled, it would protect timestamp ordering validation around prepared commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_durable_ts02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_durable_ts03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_durable_ts03.py

Purpose: checks that checkpoints honor durable timestamps and that recovery exposes only updates durable at the relevant stable timestamp.

Important APIs and control flow: scenarios cover integer row-store and column-store byte values. The test loads 3000 rows with value A at timestamp 50, advances stable/oldest to 100 and checkpoints, then prepares per-row updates to value B with commit 200 and durable 220. It reads the checkpoint cursor and read timestamp 150 as A, reads timestamps 210 and 220 as B, checkpoints with `use_timestamp=true`, reopens with stable/oldest 210 and expects A, then writes value C with durable 240, advances stable to 250, checkpoints, reopens, and expects C.

State and persistence: state spans checkpoint snapshots, timestamped prepared updates, restart recovery, and a small 10 MB cache. The test distinguishes visible-but-not-yet-durable value B from value C that is durable before the final stable timestamp.

Dependencies and integration: uses `wttest`, `make_scenarios`, timestamp APIs, checkpoints, and storage engine eviction/history interactions.

Risks and test signals: tiered is skipped due to hook crashes. Failures indicate checkpoints or recovery included updates whose durable timestamp was too new, or failed to preserve updates whose durable timestamp was stable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_durable_ts03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_empty.py -->
# sources/storage-engines/wiredtiger/test/suite/test_empty.py

Purpose: ensures newly created empty file/table objects do not write blocks beyond the initial allocation sector.

Important APIs and control flow: scenarios cover file/table with recno and string key formats. `test_empty_create` creates the object, closes the session, maps table URI to its `.wt` filename when needed, and checks filesystem size.

State and persistence: the file should exist with size exactly `4 * 1024`. No records are inserted and no explicit checkpoint is needed beyond create/close behavior.

Dependencies and integration: uses `os.stat`, `make_scenarios`, `wttest.skip_for_hook("tiered")`, and column-store related key formats.

Risks and test signals: direct filename inspection is incompatible with tiered storage. A larger file size indicates empty-object creation wrote unexpected pages or metadata blocks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_empty.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_empty_value.py -->
# sources/storage-engines/wiredtiger/test/suite/test_empty_value.py

Purpose: smoke tests row-store zero-length values and verifies they are represented as empty values rather than stored payloads.

Important APIs and control flow: creates `file:test_empty_values` with `key_format=S,value_format=u`, inserts 25000 records with `b''`, reopens the connection to force disk readback, opens `statistics:<uri>` with `statistics=(tree_walk)`, and reads `stat.dsrc.btree_row_empty_values`.

State and persistence: zero-length values are persisted through reopen. Tree-walk statistics count optimized empty-value cells.

Dependencies and integration: uses `wiredtiger.stat`, `wttest`, file btree storage, and tree-walk statistics.

Risks and test signals: the statistic must equal the number of inserted records. Failure indicates empty values were stored incorrectly or not counted during tree walk.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_empty_value.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_encrypt01.py

Purpose: broad encryption/compression matrix test for system-level and per-file encryption.

Important APIs and control flow: scenarios combine file/table URI, encryptors (`none`, `nop`, `rotn`, `rotn-none`, `sodium`), compressors, and early extension loading. `conn_extensions` loads encryptor and compressor extensions with skip-if-missing. `conn_config` sets system encryption and optional log compressor. The test creates the object with file encryption and block compressor, writes 4999 deterministic random keys/values, reopens, and verifies every value.

State and persistence: reopen forces encrypted and compressed pages to disk and back. Random seed 0 makes verification deterministic.

Dependencies and integration: uses extension loading, sodium test key, rotn key IDs, log compression, block compression, and cursor search.

Risks and test signals: high scenario count catches extension-load ordering, encryption inheritance, compression/encryption stacking, and readback corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_encrypt02.py

Purpose: tests encryption configured with secret/password arguments and verifies `wt` utility access with `-E`.

Important APIs and control flow: scenarios cover rotn with no key ID, key ID, secret key, key ID plus secret, and sodium with a hex secret. `conn_extensions` loads rotn and sodium. `conn_config` builds system encryption with optional `secretkey`. The test creates an encrypted file, writes deterministic random records, reopens and verifies them, then runs `wt dump`, adding `-E <secret>` when needed.

State and persistence: encrypted pages must survive reopen and be readable by both library and command-line utility.

Dependencies and integration: uses `suite_subprocess`, encryptor extensions, sodium secret key, random deterministic data, and utility dump.

Risks and test signals: detects secret propagation errors, key ID handling regressions, and utility failure to open encrypted homes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_encrypt03.py

Purpose: tests encryption error handling when table-level encryption is requested but system encryption is `none`.

Important APIs and control flow: scenario creates a table with system encryption `none` and a table encryption setting based on `rotn` plus a key-id argument. `conn_extensions` loads both requested encryptors. `conn_config` applies system encryption. The test builds a table-create string with `encryption=(name=...)` and expects `session.create` to raise `WiredTigerError` matching `/to be set: Invalid argument/`.

State and persistence: no valid table should be created in the error case. The focus is configuration validation before durable data exists.

Dependencies and integration: uses `wiredtiger`, `wttest`, `make_scenarios`, and encryptor extension loading.

Risks and test signals: failures indicate encryption configuration validation changed. Comments note a different inherited-system-encryption case is now permitted and intentionally not tested here.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_encrypt03.py -->
