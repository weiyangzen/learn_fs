# Research: subset-b-009079

Grouped research report for WiredTiger Python suite files. Each file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs25.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs25.py

Purpose: verifies that reconciliation/eviction handles a prepared update chain correctly when adjacent keys have different history-store requirements. The test focuses on the update structure for each key when prepared updates are present but ignored by an eviction reader.

Important APIs and functions: `test_hs25` extends `wttest.WiredTigerTestCase`; `make_scenarios` runs column-store recno (`r`) and integer row-store (`i`) variants. The main API calls are `set_timestamp`, `session.create`, `begin_transaction`, `commit_transaction`, `prepare_transaction`, `rollback_transaction`, and a debug cursor opened with `debug=(release_evict)`.

Control flow: the test pins oldest and stable timestamps to 1, creates `table:test_hs25`, writes key 1 and key 2 at timestamp 2, advances key 2 to timestamp 3, then starts a prepared transaction on key 1 containing two in-memory updates. A second session begins `ignore_prepare=true`, opens the eviction cursor, reads key 1 as the committed old value and key 2 as the newer committed value, then rolls back both sessions.

State and persistence behavior: the prepared transaction is deliberately not committed; its updates must not be surfaced to the ignore-prepare eviction path as committed history. Eviction is the persistence signal because it drives reconciliation and update-chain processing without requiring an explicit checkpoint.

Dependencies and integration points: uses the WiredTiger Python test harness, timestamp helpers from `wttest`, and the debug eviction cursor path. It integrates with history-store reconciliation and prepared transaction visibility.

Risks and edge cases: failures would suggest prepared updates can corrupt per-key update-chain state or leak into eviction reads. The test is narrow: only two key formats are covered, and it relies on debug eviction behavior rather than verifying on-disk history-store records directly.

Test signals: passing assertions are exact value reads through the eviction cursor: key 1 remains `a`, key 2 is `b`; no statistics are checked.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs25.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs26.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs26.py

Purpose: tests variable-length column-store history-store reads when RLE groups from older and newer batches overlap. It targets corruption/loss risks when duplicate values are reconciled, RLE-encoded, evicted, and later read through history.

Important APIs and functions: `test_hs26` uses `SimpleDataSet` with `key_format='r'` and `value_format='S'`. Scenario axes cover whether the first timestamp is globally visible, first/second row counts (`103` or `211`), and RLE grouping moduli (`7`, `13`, `17`). Helpers `make_value`, `make_updates`, `expected_value`, `expected_numvalues`, and `check` encapsulate the generated value pattern and read validation.

Control flow: the test populates an empty table, pins oldest/stable to 1, writes the first duplicate-value run at timestamp 2, optionally advances oldest/stable to make it globally visible, opens a long-running read transaction at timestamp 2, writes a second run at timestamp 100, verifies reads at both timestamps, evicts every 41st key via `debug=(release_evict)`, then validates the old reader and latest reader again.

State and persistence behavior: old versions remain visible through a pinned timestamp reader while newer versions may force older values into the history store. The RLE suffix pattern makes adjacent values compressible while mismatched group sizes create overlap at group boundaries.

Dependencies and integration points: depends on `wtdataset.SimpleDataSet`, `wtscenario.make_scenarios`, timestamp visibility, history-store reads, and variable-length column-store RLE reconciliation.

Risks and edge cases: important risks are off-by-one RLE grouping errors, incorrect key counts when the second write has fewer rows, and failure to retain old values after eviction. It is deliberately column-store-only because the hazard is tied to VLCS RLE encoding.

Test signals: `check` asserts exact value content and expected record counts before and after eviction for timestamp 2 and timestamp 100.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs26.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs27.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs27.py

Purpose: verifies that VLCS reconciliation does not RLE-compact adjacent identical values when their timestamps are heterogeneous. The same value may appear in adjacent cells, but timestamp boundaries must remain observable through time-travel reads.

Important APIs and functions: `test_hs27` uses `SimpleDataSet`, timestamped transactions, and `make_scenarios`. Scenario axes vary number of write timestamps (`2`, `3`, `10`), keys per timestamp (`1`, `2`, `3`), optional initialization, group ordering, and key ordering. Helpers map logical timestamp groups to physical keys (`get_writetime`, `get_readtime`, `get_key`, `invert_key`, `invert_timestamp`) and validate with `check1`, `check2`, `check3`, `check`, and `checkall`.

Control flow: the test optionally initializes the table with `value_1`, then writes `value_2` to adjacent key groups at distinct commit timestamps. It validates expected visibility across all read timestamps, forces eviction/reconciliation, and repeats validation so RLE-encoded pages are read back.

State and persistence behavior: timestamp group metadata is the state under test. Although values may be byte-identical and adjacent, each group has separate start times and must not be collapsed into one RLE run with a single time window.

Dependencies and integration points: integrates VLCS RLE, timestamp visibility, eviction, and the history-store path. It depends on the WiredTiger test transaction helpers and dataset key generation.

Risks and edge cases: ordering axes exercise forward/backward writes to catch assumptions that only ascending insertion order preserves timestamp boundaries. The test is sensitive to the exact key range around 71 and to off-by-one inversions in helper logic.

Test signals: expected scans at every generated read timestamp must match `value_1` or `value_2`; count and value mismatches indicate timestamp/RLE corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs27.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs28.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs28.py

Purpose: ensures reconciliation inserts full updates into the history store, rather than reverse modifies, when a modify follows a squashed on-page value. This protects reconstruction correctness for modify chains.

Important APIs and functions: `test_hs28` extends `WiredTigerTestCase`; scenarios cover column-store recno and integer row-store. `conn_config` enables all statistics and JSON stats logging. The test uses `wiredtiger.Modify`, cursor `modify`, `session.checkpoint`, and statistics `cache_hs_insert_full_update` and `cache_hs_insert_reverse_modify`.

Control flow: the test creates a table, inserts a full value at timestamp 2, applies a modify at timestamp 5, then commits multiple updates on the same key at timestamp 10. A checkpoint moves older versions to the history store. It reads connection statistics and asserts the expected insert mode.

State and persistence behavior: checkpoint reconciliation is the persistence transition. The previous on-page value has been squashed, so using reverse modify would not leave enough information to reconstruct old values safely.

Dependencies and integration points: uses the Python WiredTiger API `Modify` object, history-store insert statistics, and reconciliation policy for update chains.

Risks and edge cases: this is a statistic-based behavioral assertion; if implementation changes update accounting while preserving correctness, the expected counts may require adjustment. It does not read historical values directly.

Test signals: after checkpoint, `cache_hs_insert_full_update == 2` and `cache_hs_insert_reverse_modify == 0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs28.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs29.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs29.py

Purpose: reproduces a path where reconciliation can hold three history-store cursors simultaneously: normal reconciliation, delete/reinsert from position, and tombstone cleanup. The test is primarily a crash/assertion regression for cursor-management correctness.

Important APIs and functions: `test_hs29` uses `WiredTigerTestCase`, standard cursor operations, debug eviction cursor `debug=(release_evict=true)`, timestamp pinning, no-timestamp updates, checkpoint, and connection close.

Control flow: it creates a string-key table, writes two timestamped versions for keys `1` and `2`, evicts both keys to push history, opens an old reader at timestamp 2, removes key `1` without a timestamp, updates key `2` without a timestamp, advances stable to 20, checkpoints, and closes the connection to trigger final checkpoint/reconciliation.

State and persistence behavior: the old reader pins visibility while no-timestamp changes create globally visible update/tombstone cases that require history-store cleanup. Closing the connection forces the final reconciliation point where cursor nesting previously mattered.

Dependencies and integration points: integrates history-store reconciliation, no-timestamp update semantics, tombstone cleanup, debug eviction, and final connection shutdown checkpointing.

Risks and edge cases: the test has no explicit post-close data validation; it relies on the absence of errors, assertions, or deadlocks. It is tightly tied to internal cursor acquisition order.

Test signals: success is completing checkpoint and `self.conn.close()` without WiredTiger errors or process aborts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs29.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs30.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs30.py

Purpose: verifies history-store behavior for non-timestamped tables, both logged and unlogged, especially when long-running snapshot transactions require older non-timestamped values after eviction.

Important APIs and functions: `test_hs30` sets `session_config='isolation=snapshot'`. Scenario axes cover recno/integer key formats, logging on/off, early checkpoint, middle checkpoint, and eviction on/off. Helpers `large_updates` write full-table batches without commit timestamps; `evict` uses `debug=(release_evict)`.

Control flow: the test creates a table with chosen logging, writes `value_a`, optionally checkpoints, opens a snapshot reader that sees `value_a`, writes `value_b` and `value_c`, optionally checkpoints, opens a second reader seeing `value_c`, writes `value_d` and `value_e`, optionally evicts pages, then scans both pinned readers and checks the history-store read statistic.

State and persistence behavior: the key state is transaction-ID-based visibility rather than timestamp visibility. Eviction is expected to move old non-timestamped updates to history only when open snapshots need them.

Dependencies and integration points: depends on connection statistics (`stat.conn.cache_hs_read`), logging configuration, snapshot isolation, and debug eviction. It exercises non-timestamped history-store read paths distinct from timestamped tests.

Risks and edge cases: there is a cleanup bug in the source: `evict_cursor.close()` is called at the end even though `evict_cursor` is local to `evict`; when the path reaches that line it can raise `NameError`. The helper also indexes `evict_cursor[1]` in a loop instead of key `i`, making eviction coverage weaker than intended.

Test signals: reader scans must see `value_a` and `value_c`; with eviction, `cache_hs_read` should be at least `nrows * 2`, and without eviction it should be zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs30.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs31.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs31.py

Purpose: ensures no-timestamp removals clear obsolete history-store records once their tombstones become globally visible. It covers column, integer-row, and string-row keys.

Important APIs and functions: `create_key` normalizes string versus numeric keys; `get_stat` reads connection statistics. Scenarios toggle whether globally visible cleanup occurs before a checkpoint. Statistics checked are `cache_hs_key_truncate_onpage_removal` and `rec_hs_wrapup_next_prev_calls`.

Control flow: the test writes timestamped values at timestamps 10 through 14, checkpoints, evicts pages to move history, opens a long-running transaction to pin transaction IDs, removes all keys with `no_timestamp=true`, optionally checkpoints, verifies the long-running reader still sees old content, rolls it back, advances oldest/stable to 10, checkpoints and evicts to remove obsolete entries, inserts new values at timestamp 20, and finally confirms old read timestamps no longer see prior values.

State and persistence behavior: history-store content must remain available while a long transaction pins it, then be truncated after the out-of-order no-timestamp tombstone becomes globally visible.

Dependencies and integration points: integrates no-timestamp tombstones, timestamp history, eviction, checkpoint, and history-store truncation stats.

Risks and edge cases: high row count and many timestamped updates make the test expensive. It depends on stat names and exact cleanup mechanics.

Test signals: old readers initially see `value1`; later reads at timestamps 10-14 return `WT_NOTFOUND`; both history-store cleanup stats are greater than zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs31.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs32.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs32.py

Purpose: verifies that no-timestamp updates or deletions clear the relevant history-store records, including cases with and without a long-running transaction.

Important APIs and functions: `test_hs32` covers column, integer-row, and string-row keys; update type scenarios are `deletion` and `update`; long-running transaction scenarios are enabled/disabled. Helpers `create_key`, `get_stat`, and `evict_cursor` support format conversion, stats, and debug eviction.

Control flow: the test writes timestamped versions 1-4 for 10,000 keys, checkpoints and evicts, optionally writes timestamp 5 and opens a long reader at that timestamp, applies no-timestamp changes to even keys, optionally checkpoints/evicts and rolls back the reader, writes all keys at timestamp 10, checkpoints, then validates reads at timestamps 1-4.

State and persistence behavior: even keys touched by no-timestamp changes should no longer expose stale historical content. Odd keys remain historical controls. Deletion mode expects history-store key truncation to occur.

Dependencies and integration points: depends on WiredTiger transaction context manager support from `wttest`, `WT_NOTFOUND`, `stat.conn.cache_hs_key_truncate`, checkpoint, eviction, and history-store cleanup.

Risks and edge cases: the loop applies a transaction to every key but only mutates even keys, increasing runtime. Behavior differs between update and delete modes; only deletion asserts truncation statistics.

Test signals: at read timestamps 1-4, even deleted keys are not found, even updated keys read `value2`, odd keys retain `value1`; deletion scenarios require `cache_hs_key_truncate > 0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs32.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs33.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs33.py

Purpose: regression test for recovery when many tables have history-store activity and a crash/copy occurs during a checkpoint stop timing-stress point. It protects metadata recovery from opening data files/history too early.

Important APIs and functions: `test_hs33` extends `WiredTigerTestCase` and `suite_subprocess`. Helpers `large_updates` and `add_insert` populate/update many `SimpleDataSet` tables. It uses `checkpoint_thread`, `copy_wiredtiger_home`, `timing_stress_for_test=[checkpoint_stop]`, and statistics `checkpoint_stop_stress_active`.

Control flow: the test creates 99 logged-disabled tables, inserts small records, opens a long transaction, updates every table with a larger value, reconfigures checkpoint stop timing stress, starts a checkpoint thread, waits for the stress statistic, copies the home to `RESTART`, stops the checkpoint thread, closes the original connection, then reopens `RESTART` with aggressive dirty eviction settings to trigger recovery replay paths.

State and persistence behavior: the copied home represents an incomplete checkpoint with metadata log records in flight. Recovery must complete using correct checkpoint metadata and avoid opening files before metadata recovery has selected the proper checkpoint.

Dependencies and integration points: integrates checkpoint timing stress, threading, home-copy helper, recovery, metadata logging, history-store state, and eviction.

Risks and edge cases: timing-stress polling can hang if the stat is not reached; it is concurrency-sensitive. The test does not verify all table values after restart, so its main signal is successful recovery under low cache/eviction pressure.

Test signals: opening the copied home under recovery completes without WiredTiger errors or assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs33.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs_evict_race01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_hs_evict_race01.py

Purpose: exercises a race between checkpoint, eviction, history-store activity, and no-timestamp updates. It uses checkpoint slowdown to widen the window.

Important APIs and functions: `test_hs_evict_race01` uses `timing_stress_for_test=(checkpoint_slow)`, scenarios for recno and integer row-store keys, `simulate_crash_restart`, and `wtthread` checkpoint threading. Main methods are `test_mm_ts` and `no_timestamp_update_and_evict`.

Control flow: the test creates a one-row table, writes timestamped values, starts or coordinates checkpoint activity, performs no-timestamp updates and debug eviction, then uses crash/restart simulation to verify durable state. The helper performs a no-timestamp update and evicts the page to force reconciliation while checkpoint timing is stressed.

State and persistence behavior: timestamped versions and later no-timestamp updates must maintain correct history-store and durable visibility across eviction and crash recovery.

Dependencies and integration points: integrates timing stress, checkpoint threads, debug eviction, crash-restart helper, timestamp APIs, and WiredTiger transaction visibility.

Risks and edge cases: race tests are sensitive to timing and scheduler behavior. With only one row, it targets a specific interleaving rather than broad page coverage.

Test signals: assertions validate expected values during the race and after restart; absence of crash/recovery errors is also a signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_hs_evict_race01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import01.py

Purpose: provides the shared file-import helper base and tests successful file import both into a different database home and back into the same home after dropping the file object.

Important APIs and functions: `test_import_base` defines `update`, `delete`, `check_record`, `check`, `config_compare`, `strip_subconfig`, `populate`, and `copy_file`. `test_import01` sets binary keys/values, timestamp list, and `create_config='allocation_size=512,key_format=u,value_format=u'`.

Control flow: `test_file_import` creates a file, writes/checkpoints two batches, exports metadata via `metadata:` cursor, closes, creates `IMPORT_DB`, populates unrelated files, advances oldest timestamp, copies the source file, imports with `import=(enabled,repair=false,file_metadata=(...))`, verifies, compares metadata excluding IDs/checkpoints, appends remaining data, and checkpoints. `test_file_import_dropped_file` backs up the file, drops it, copies it back, imports into the same database, and validates.

State and persistence behavior: the test depends on checkpointed on-disk file state and exported metadata. Oldest timestamp must be advanced beyond imported timestamps so import timestamp validation succeeds.

Dependencies and integration points: integrates metadata cursors, file copying, `session.create` import config, `verifyUntilSuccess`, and binary key/value formats. Later import tests depend on `test_import_base`.

Risks and edge cases: metadata comparison strips only IDs and checkpoint subconfigs; future metadata fields may require updates. Random table names in `populate` make auxiliary data varied but not deterministic.

Test signals: imported contents match original checkpointed keys, metadata is equivalent after stripping unique fields, and new post-import writes/readbacks succeed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import02.py

Purpose: validates error handling for invalid file import operations: missing metadata, importing over an existing URI, and importing a missing file.

Important APIs and functions: `test_import02` inherits `test_import_base`. `no_metadata_helper` creates/checkpoints source data, closes the connection, opens a new home, copies the file, and attempts import using caller-provided config. Error tests use `assertRaisesWithMessage` with `wiredtiger.WiredTigerError`.

Control flow: empty `file_metadata=()` and absent `file_metadata` both call `no_metadata_helper` and expect invalid-argument failures. The existing-URI case creates a target in the destination before import and expects an error. The missing-file case collects example metadata from an existing generated table but does not copy the target file, expecting a filesystem error.

State and persistence behavior: source files are checkpointed before copy attempts. The tests exercise metadata contract validation before and during `session.create` import.

Dependencies and integration points: depends on `test_import_base.populate`, metadata cursor iteration, filesystem copy behavior, and WiredTiger import parser/validation paths.

Risks and edge cases: error-message regexes are part of the contract and can be brittle. The example metadata in the missing-file case is taken from any generated table, so it validates missing file handling rather than metadata-object identity.

Test signals: expected exceptions include invalid argument for missing metadata and `/No such file or directory/` for absent data files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import03.py

Purpose: tests successful table import, including table metadata plus backing file metadata, for simple and named-column table layouts.

Important APIs and functions: scenarios cover a recno/integer simple table and a named-column table with value format `SSi`. It inherits data helpers from `test_import_base` and uses `metadata:` to capture both `table:` and `file:` configs.

Control flow: the test populates unrelated tables, creates `table:original_db_table`, writes/checkpoints two batches, exports table and file metadata, builds an import config combining table config and `file_metadata`, closes, opens `IMPORT_DB`, populates unrelated objects, advances oldest timestamp, copies `original_db_table.wt`, imports the table, verifies it, checks imported rows, compares table metadata, appends remaining rows, and checkpoints.

State and persistence behavior: table import must reconstruct both logical table metadata and physical file metadata. For named columns, column metadata and value layout must survive import.

Dependencies and integration points: integrates table-level import syntax, file copy, timestamp validation, `verifyUntilSuccess`, and `config_compare`.

Risks and edge cases: random sample values are generated at module/scenario creation time, which can affect reproducibility of exact values but not test invariants. It only copies one backing `.wt` file because these table forms are single-file tables.

Test signals: successful import, equivalent table metadata after stripping unique fields, correct data visibility, and successful post-import writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import04.py

Purpose: covers success and failure scenarios for table import, including existing target objects, dropped objects with retained files, missing files, missing table config, and missing file metadata. It is skipped for tiered storage.

Important APIs and functions: `test_import04` inherits `test_import_base`, uses `make_scenarios` for simple and named-column tables, and relies on `wiredtiger.WiredTigerError` plus `assertRaisesException`/`assertRaisesWithMessage`.

Control flow: it creates and checkpoints a target table, exports table and file metadata, reopens the same home and confirms importing over an existing table fails, drops the table with `remove_files=false` and successfully imports it, then creates a fresh `IMPORT_DB`. In the new home it first expects failure before the file is copied, then expects invalid-argument failures when omitting table config or file metadata, then performs a valid import, verifies data/metadata, appends rows, and checkpoints.

State and persistence behavior: drop-without-remove leaves the backing file as importable state. Timestamp advancement is required before importing timestamped data. Metadata completeness is enforced for non-repair table import.

Dependencies and integration points: integrates drop semantics, metadata cursor export, import parser validation, file existence checks, and table verification.

Risks and edge cases: the test relies on single-file table backing names and is not valid for tiered hooks. Error-message matching may need updates if WiredTiger changes diagnostic text.

Test signals: expected failures occur in invalid states; valid imports retain values and metadata; post-import updates work.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import05.py

Purpose: verifies file import rejects objects whose aggregated durable timestamps are newer than the selected global timestamp, for both metadata import and repair import.

Important APIs and functions: scenarios cover latest operation type (`insert` or `delete`), import mode (`repair=false` with `file_metadata` or `repair=true`), and comparison timestamp (`oldest` or `stable`). The test uses `expectedStderrPattern` and `assertRaisesException`.

Control flow: it writes all but the last record, checkpoints, then either inserts the last record or deletes the first record at the last timestamp and checkpoints again. After copying the file to a new home, it constructs import config with optional `compare_timestamp=stable_timestamp`. It first imports with global timestamp unset and expects failure, then sets the chosen global timestamp to one less than the last operation and expects start or stop timestamp failure, then sets it equal to the last timestamp and expects success.

State and persistence behavior: the object's aggregated newest start/stop durable timestamps are persisted in metadata/checkpoint state and compared against oldest or stable timestamp during import.

Dependencies and integration points: depends on import timestamp validation, repair mode metadata reconstruction, durable timestamp aggregation, and error reporting.

Risks and edge cases: exact stderr patterns are part of the test. Delete mode specifically validates stop timestamp handling, which can regress separately from start timestamp handling.

Test signals: failures mention `newest start durable` or `newest stop durable` as appropriate; final import succeeds after advancing the selected global timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import06.py

Purpose: tests `repair=true` file import without supplied file metadata across allocation sizes, compression extensions, and encryption extensions.

Important APIs and functions: scenarios combine allocation sizes 512-4096, compressors (`none`, `nop`, `lz4`, `snappy`, `zlib`, `zstd`), and encryptors (`none`, `nop`, `rotn`, `sodium`). `conn_extensions` loads compressor/encryptor extensions with `skip_if_missing`; `conn_config` configures encryption including the sodium test key.

Control flow: the test creates an encrypted/compressed file, writes/checkpoints two batches, exports metadata only for later comparison, closes, opens `IMPORT_DB` with compatible encryption config, populates unrelated files, advances oldest timestamp, copies the data file, imports with `import=(enabled,repair=true)`, verifies, checks imported rows, compares reconstructed metadata with original metadata, appends remaining rows, and checkpoints.

State and persistence behavior: repair import reconstructs metadata from the file itself, so allocation size, compression, and encryption metadata must be discoverable and compatible with the destination connection.

Dependencies and integration points: integrates extension loading, encryption/compression configuration, repair import, metadata comparison, and binary key/value data.

Risks and edge cases: extension availability controls scenario skips. Encryption mismatches would surface at import/open time. The `nop` encryptor scenario maps to `encryptor='none'` in this file, which may reflect test naming rather than a true nop encryptor.

Test signals: import succeeds, verification passes, metadata comparison succeeds, and subsequent writes/readbacks work.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import07.py

Purpose: verifies import is rejected for unsupported data-source URI prefixes, specifically `colgroup:` and `index:`.

Important APIs and functions: `test_import07` inherits `test_import_base` and uses scenarios for `prefix='colgroup:'` and `prefix='index:'`. It builds a valid-looking import config from example table metadata but applies it to an unsupported URI.

Control flow: the test populates/checkpoints generated tables, grabs any `table:` metadata config, builds `import=(enabled,repair=false,file_metadata=(...))`, prefixes `original_db_file` with the scenario data source, and calls `session.create`. The create must fail before file existence matters.

State and persistence behavior: no target file state is required; this validates import routing/validation based on URI data source.

Dependencies and integration points: depends on metadata cursor iteration, import configuration parser, and data-source dispatch validation.

Risks and edge cases: if WiredTiger adds import support for colgroups or indexes, this test's expected behavior must change. It does not validate `file:` or `table:` success paths because other import tests cover those.

Test signals: `session.create` raises `WiredTigerError` matching `/Operation not supported/`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import08.py

Purpose: ensures imported files retain or reset write-generation state correctly so old transaction IDs from a different database do not hide imported records.

Important APIs and functions: scenarios cover metadata import and repair import. `parse_write_gen` extracts `write_gen=<num>` from metadata using a regex. The test uses a second session to hold a transaction ID pinned across checkpoints.

Control flow: it populates many generated tables to allocate transaction IDs, opens a second session, removes an entry inside an uncommitted transaction to pin IDs, creates the import file, writes each record at a timestamp with a checkpoint after each write to raise the btree write generation, exports metadata, rolls back the pinned transaction, copies the file to `IMPORT_DB`, opens the new home, advances oldest timestamp, imports with either metadata or repair mode, verifies, checks that metadata write generation is greater than 1, and validates all records are visible.

State and persistence behavior: pages may contain transaction IDs and write generations from the source database. Import must use the btree-specific base write generation to decide when to clear IDs in the destination.

Dependencies and integration points: integrates transaction ID visibility, checkpoint write generations, metadata parsing, import repair/metadata modes, and timestamped binary data.

Risks and edge cases: regex parsing is simple and assumes `write_gen` appears in metadata. The test intentionally manipulates transaction IDs; changes in reconciliation ID-obsolescence rules may alter setup requirements.

Test signals: imported metadata has `write_gen > 1` and all source records are visible in the fresh connection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import09.py

Purpose: tests table import with `repair=true` and no exported metadata across table layouts, allocation sizes, compressors, and encryptors. It is skipped under tiered storage.

Important APIs and functions: scenarios combine simple/named-column table definitions, allocation sizes, compressors, and encryptors. `conn_extensions` loads compression/encryption extensions, and `conn_config` sets destination encryption parameters.

Control flow: the test creates/populates unrelated data, creates `table:original_db_table` with scenario storage options, writes/checkpoints two batches, exports table/file metadata only for later comparison, closes, opens `IMPORT_DB`, populates unrelated data, advances oldest timestamp, copies the `.wt` file, imports with `import=(enabled,repair=true)`, verifies, checks imported rows, compares reconstructed file and table metadata to originals, appends remaining rows, and checkpoints.

State and persistence behavior: repair import must reconstruct both table and file metadata from the copied file while preserving storage options and named-column schema.

Dependencies and integration points: integrates extension loading, table repair import, metadata comparison, and data verification. It reuses helper logic from `test_import01`.

Risks and edge cases: test matrix is large and extension-dependent. Random values are generated for simple table scenarios. Tiered storage is excluded because backing-file assumptions do not hold.

Test signals: successful import and verification, equivalent reconstructed metadata, preserved rows, and successful post-import writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import10.py

Purpose: validates import/export interaction while a backup cursor is open. Imported files should not be included in the in-progress backup file list.

Important APIs and functions: `test_import10` extends `wtbackup.backup_base`. Scenarios cover import with metadata and repair import. `get_stat` reads `session_table_create_import_success` and `session_table_create_import_repair`.

Control flow: the test creates and populates `table:test_import10`, checkpoints, exports table/file metadata, drops the table with `remove_files=false`, verifies opening it fails, opens a `backup:` cursor, imports the table using the scenario config, checks import statistics, verifies and reads all rows, then performs a full backup using the still-open backup cursor and asserts the imported file is absent from the backup file set.

State and persistence behavior: the backup cursor captures a backup view before import. The imported file should not retroactively enter that view even though it exists by the time backup files are copied.

Dependencies and integration points: integrates backup cursor semantics, table import, drop-with-retained-files, import stats, and `take_full_backup`.

Risks and edge cases: relies on backup cursor snapshot semantics and file naming. It checks integer data only, not timestamped import.

Test signals: import success stat equals 1; repair stat matches scenario; all rows read correctly; `test_import10.wt` is not in the full backup file list.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import11.py

Purpose: tests tiered-storage import using an exported metadata file (`WiredTiger.export`) and rejects incompatible `file_metadata` import forms for tiered tables.

Important APIs and functions: this file defines its own `test_import_base` mixing `TieredConfigMixin` with `WiredTigerTestCase`. Helpers include timestamped `update/delete/check`, `populate`, file-copy helpers, and `checkpoint_and_flush_tier`. `test_import11` uses `gen_tiered_storage_sources`, `backup:export`, `tiered_conn_config`, and import success/failure statistics.

Control flow: it creates and populates two tiered tables, opens `backup:export` to produce `WiredTiger.export`, copies the export file into `IMPORT_DB`, reopens there, populates unrelated data, advances oldest timestamp, copies local/bucket/cache-bucket files, validates that `file_metadata` import configs fail in tiered scenarios and increment failure stats, then imports both tables with `metadata_file="WiredTiger.export"`, checkpoint/flushes after each, checks success stats, removes the export file, validates imported values, writes remaining rows, and checkpoints.

State and persistence behavior: tiered import state spans local files, bucket data, cache-bucket data, and an export metadata file. `file_metadata` is intentionally incompatible with this mode.

Dependencies and integration points: integrates tiered hooks, backup export, object-store-like directory layout, import stats, and timestamp validation.

Risks and edge cases: the source contains a likely bug while reading metadata (`table_config = cursor[k]` uses `cursor`, not `meta_c`). This path only matters inside the tiered invalid-config block and may raise `NameError` before the intended assertions. Verification is disabled for tiered storage with a FIXME.

Test signals: invalid tiered configs increment import-fail stats; both valid imports increment success stats; imported values are readable and post-import writes work.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_import12.py

Purpose: stresses repeated import/drop/reimport of a file after checkpoints and alters, including fallback to `repair=true` when a second metadata import encounters checkpoint/root-page problems.

Important APIs and functions: inherits `test_import_base`; uses `WiredTigerError`, `wiredtiger_strerror`, and `WT_ERROR` to normalize expected repairable failures. Class attributes define original/new file names, two `access_pattern_hint` alter configs, and `max_ckpt=2`.

Control flow: the test creates the original file, writes/checkpoints two batches, exports metadata, closes, then loops over checkpoint counts 0-2. For each loop it recreates `IMPORT_DB`, imports the copied file under a new URI, checkpoints one or more times, alternates an `alter` setting, checkpoints, confirms latest metadata contains the alter, drops the table with `remove_files=false`, tries a second metadata import with `panic_corrupt=false`, falls back to `repair=true` if WT_ERROR occurs, verifies, checks values, appends rows, and closes the connection.

State and persistence behavior: the first import/drop leaves a file with multiple checkpoints and altered metadata. The second import tests whether import selects a valid/latest checkpoint; repair import is expected to recover when normal import cannot.

Dependencies and integration points: integrates import, alter, checkpoint force mode, drop without remove, repair import, metadata inspection, verification, and stderr/stdout ignore hooks.

Risks and edge cases: comments reference known issues WT-13639 and WT-14713. Some repair metadata assertions are commented out, so the test currently validates usability more than exact metadata preservation after fallback.

Test signals: latest metadata includes the alter before drop; second import or repair succeeds; verification and data checks pass across all checkpoint-loop variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_import12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_index01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_index01.py

Purpose: basic coverage for WiredTiger secondary indexes over a table with composite keys, named columns, and multiple index key definitions.

Important APIs and functions: `test_index01` creates `table:test_index01` with `key_format=Si`, `value_format=SSii`, and columns `(name,ID,dept,job,salary,year)`. It creates six indexes over different column combinations. Helpers wrap table/index cursor creation, insert/update/remove operations, duplicate insertion checks, and existence checks.

Control flow: tests cover empty table lookup and empty indexes, insert and expected index cursor order/content, update including nonexistent updates, insert with overwrite including duplicate rejection, delete and index cleanup, and exclusive index creation failure after non-exclusive recreation.

State and persistence behavior: index state is automatically maintained when base records are inserted, overwritten, updated, or removed. No checkpoint is required; this is logical cursor/index consistency.

Dependencies and integration points: uses the core WiredTiger cursor API, index cursor projection behavior, `WT_NOTFOUND`, duplicate-key error handling, and `dropUntilSuccess`.

Risks and edge cases: expected index rows are hard-coded as rendered Python lists, so output order/projection changes are visible. Coverage is functional but limited to a small number of records.

Test signals: exact index iteration output matches expected strings; duplicate insert raises; nonexistent update returns `WT_NOTFOUND`; delete leaves all indexes empty; exclusive recreate raises.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_index01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_index02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_index02.py

Purpose: tests `search_near` behavior on index cursors for exact matches, between-key searches, and empty indexes.

Important APIs and functions: defines a Python `cmp` helper. `test_index02` scenarios include index key `columns=(v)` and index key including primary key `columns=(v,k)`, with `ncol` selecting key width. The test uses table and index cursors, `set_key`, `search_near`, and `get_key`.

Control flow: `test_search_near_exists` populates values and verifies `search_near` on existing index keys returns exact matches. `test_search_near_between` searches for keys not present and validates returned direction/order relative to nearby index entries. `test_search_near_empty` validates behavior on an empty index.

State and persistence behavior: all state is in-memory logical index content created during the test. No persistence or checkpointing is involved.

Dependencies and integration points: integrates index cursor key projection, duplicate/primary-key tie-breaking when index includes table key, and WiredTiger `search_near` return semantics.

Risks and edge cases: correctness depends on key ordering and the number of columns in each index scenario. Empty-index behavior is a separate edge case because no nearest key exists.

Test signals: return values and keys from `search_near` match the expected comparison direction and exact/near key values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_index02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_index03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_index03.py

Purpose: regression coverage for creating an index after a table already contains enough data to require bulk index population.

Important APIs and functions: `test_index03` uses helper methods `key` and `value` to generate string keys and values, creates a table, inserts records, then creates an index over a value column.

Control flow: the test creates a table with named columns, inserts a range of generated rows, creates the index after data exists, and then validates index behavior through cursor operations.

State and persistence behavior: the important state transition is index creation on a populated table. WiredTiger must scan existing records and build a consistent index rather than only indexing future writes.

Dependencies and integration points: depends on table/index DDL, column metadata, cursor insertion, and index backfill.

Risks and edge cases: the file is small and targets a specific populated-create path. It does not cover updates/removals after index creation because `test_index01` covers those basics.

Test signals: successful index creation and expected index lookup/iteration behavior over pre-existing records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_index03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_inmem01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_inmem01.py

Purpose: tests in-memory cache capacity behavior: successful inserts under capacity, failure over capacity, making space by deletes/replacements, and wedged-cache recovery behavior.

Important APIs and functions: `conn_config` enables `in_memory=true` with 5MB cache; `table_config` sets small pages. Scenarios cover recno and string-row keys. Tests use `SimpleDataSet`, large string values, `WT_CACHE_FULL`, and `sleep`.

Control flow: `test_insert` inserts a modest dataset. `test_insert_over_capacity` inserts until the cache fills and expects `WT_CACHE_FULL`. `test_insert_over_delete` fills, deletes records, then verifies inserts can proceed. `test_insert_over_delete_replace` checks replacement after deletions. `fill` is a helper for repeated inserts; `test_wedge` stresses behavior after the cache is wedged/full and then recovers after space is freed.

State and persistence behavior: because `in_memory=true`, there is no eviction-to-disk escape path for excess data. Memory accounting, deleted content reclamation, and cache-full state transitions are the main state under test.

Dependencies and integration points: depends on the WiredTiger in-memory engine, cache accounting, cursor insert/remove/update behavior, and dataset helpers.

Risks and edge cases: tests can be sensitive to cache-size/page-size accounting changes. Timing/sleep in wedge recovery may be environment-sensitive.

Test signals: expected `WT_CACHE_FULL` errors occur only when over capacity; after deletion/replacement, inserts and checks succeed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_inmem01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_inmem02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_inmem02.py

Purpose: verifies that an in-memory database permits updates beyond the nominal cache size up to the configured allowance rather than failing too early.

Important APIs and functions: `conn_config` enables `in_memory=true` with a 3MB cache and small pages. The test uses `SimpleDataSet`, large values, and `WT_CACHE_FULL` handling.

Control flow: `test_insert_over_allowed` creates/populates an in-memory table and writes enough data to exceed ordinary cache expectations while staying within the special in-memory allowance. It checks that inserts succeed until the intended threshold and that the cache-full condition is not raised prematurely.

State and persistence behavior: the state under test is in-memory cache accounting and the allowance for over-capacity operations. There is no disk persistence path.

Dependencies and integration points: integrates cache sizing, in-memory storage mode, table page sizing, and cursor writes.

Risks and edge cases: sensitive to exact memory accounting and build configuration. Small cache sizes make this a targeted stress test rather than a general workload.

Test signals: inserts complete as allowed, and any `WT_CACHE_FULL` behavior must align with the expected over-capacity threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_inmem02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_intpack.py -->
# sources/storage-engines/wiredtiger/test/suite/test_intpack.py

Purpose: validates WiredTiger integer packing across all signed and unsigned integer format codes by writing values as keys and values and checking secondary indexes.

Important APIs and functions: `PackTester` manages four cursors/tables per format: forward table (`int key -> packed value`), reverse table (`packed key -> int value`), and inverse indexes. Methods `initialize`, `truncate`, `closeall`, and `check_range` encapsulate setup and validation. `test_intpack` scenarios cover `b/B/h/H/i/I/l/L/q/Q`.

Control flow: for each format, the test asserts the valid range size equals `2 ** nbits`, initializes tables/indexes, checks a base range around zero, checks ranges around `2**32` for 32-bit-or-larger formats, and checks ranges near powers of two up to `1 << 60` for 64-bit formats after truncation.

State and persistence behavior: data is stored in table keys, table values, and secondary indexes to exercise both pack and unpack directions. Persistence is not checkpoint-focused; correctness is immediate cursor/index retrieval.

Dependencies and integration points: depends on WiredTiger format-code handling, table schema creation, index creation, cursor lookup, and long-test mode (`wttest.islongtest`) for wider ranges.

Risks and edge cases: extreme unsigned/signed boundaries and powers of two are included to catch variable-length integer encoding bugs. Runtime grows substantially in long-test mode.

Test signals: every written value must round-trip through direct cursors and inverse index cursors with exact equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_intpack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_isolation01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_isolation01.py

Purpose: tests transaction isolation-level restrictions for writes and `session.reset_snapshot`.

Important APIs and functions: scenarios cover `read-uncommitted`, `read-committed`, and `snapshot`. The test uses `begin_transaction('isolation=...')`, cursor `insert`, `reset_snapshot`, and expected error regexes.

Control flow: it creates a string table, begins a transaction at the scenario isolation level, attempts an insert, expecting failure for read-uncommitted/read-committed and success for snapshot. It then calls `reset_snapshot`, expecting failure after snapshot writes and unsupported-isolation failure for read-committed/uncommitted. A second transaction searches a key and verifies `reset_snapshot` succeeds only for snapshot read-only state.

State and persistence behavior: transaction state transitions matter more than durable persistence. `reset_snapshot` is legal only before modifications in snapshot isolation and unsupported in weaker isolation modes.

Dependencies and integration points: depends on WiredTiger transaction isolation rules, cursor write validation, and reset-snapshot API error reporting.

Risks and edge cases: exact error text regexes may need updates if diagnostics change. The snapshot second transaction searches without asserting search result, focusing only on reset legality.

Test signals: writes fail/succeed per isolation mode, and `reset_snapshot` raises or succeeds according to transaction state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_isolation01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_jsondump01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_jsondump01.py

Purpose: tests `wt dump -j` and `wt load -j` utility behavior for JSON dump/load using standard dataset classes and multiple key formats.

Important APIs and functions: imports `SimpleDataSet`, `SimpleIndexDataSet`, `ComplexDataSet`, `compare_files`, and `suite_subprocess`. `FakeCursor` is a small iterator wrapper used to compare generated output. Scenarios combine URI/data-set types (`file:`, simple table, indexed table, complex table) with integer, recno, and string keys.

Control flow: `test_jsondump_util` creates/populates a dataset, runs the `wt dump -j` utility through `runWt`, and compares output against expected JSON-formatted cursor data. `test_jsonload_util` dumps data, drops/recreates or loads it, and validates loaded content. The exact operations depend on dataset type.

State and persistence behavior: utility dump/load is persistence-oriented: data must round-trip through on-disk dump files while preserving keys, values, indexes, and complex schema content.

Dependencies and integration points: integrates command-line `wt` utility execution, JSON dump/load format, dataset helper abstractions, file comparison helper, and subprocess test harness.

Risks and edge cases: expected dump formatting can be brittle. Complex/indexed datasets broaden coverage but also tie the test to helper dataset behavior.

Test signals: JSON dump files match expected output, `wt load -j` succeeds, and loaded datasets verify correctly.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_jsondump01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_jsondump02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_jsondump02.py

Purpose: direct JSON cursor and JSON dump/load coverage for strings, byte arrays, column groups, indexes, malformed JSON, and byte escaping. Both test methods are currently skipped due to a known JSON cursor failure.

Important APIs and functions: `test_jsondump02` extends `WiredTigerTestCase` and `suite_subprocess`. Helpers `set_kv`, `set_kv2`, `populate_squarecube`, `check_json`, `load_json`, `generate_key`, `generate_value`, and `bytes_to_str` build and validate JSON cursor data. It uses cursors opened with `dump=json` and utility calls `wt dump -j`/`wt load -jf`.

Control flow: `test_json_cursor` would create several tables plus column groups and indexes, insert special strings/unicode/byte data, validate JSON cursor output, truncate/load JSON back, check many malformed-token/type/order errors, dump/load tables through utility files, and revalidate. `test_json_all_bytes` would generate 256 byte-array/string cases, validate JSON escaping, round-trip through JSON cursors and utility files.

State and persistence behavior: intended coverage includes in-memory JSON cursor conversion and persistence through dump/load files. It also checks index and column-group JSON projections.

Dependencies and integration points: integrates JSON parser/serializer, WiredTiger dump/load utility, Unicode escaping, byte-array formats, indexes, colgroups, and subprocess harness.

Risks and edge cases: both tests call `skipTest('Known failure in JSON cursor')`, so current suite execution records skips rather than coverage. If re-enabled, many exact error-message and escaping expectations may need maintenance.

Test signals: current signal is intentional skip. When enabled, exact JSON key/value strings, expected parser errors, and dump/load round trips are the signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_jsondump02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg01.py

Purpose: tests basic disaggregated key-provider behavior with PALite storage, including key metadata persistence across reopen and crash/restart.

Important APIs and functions: decorated with `@disagg_test_class`; scenarios combine PALite disaggregated storage and crash versus reopen. `conn_extensions` loads the test `key_provider` extension with `early_load=true` and configurable `key_expires`. SQLite helpers read PALite `pages_*.db` files via the build `sqlite3`.

Control flow: the test skips non-PALite scenarios, populates a layered dataset, checkpoints twice and validates key-provider metadata, adds more rows, changes `key_expire` to 12 hours, then either simulates crash/restart or reopens the connection. It validates the metadata page and key-provider/turtle row counts, adds more data, checkpoints, and validates again.

State and persistence behavior: the main persisted state is the main KEK page in PALite special key-provider/turtle tables. Metadata must record page id 1 and expected version 1, and key-provider rows must track or exceed shared metadata rows depending on expiry.

Dependencies and integration points: integrates disaggregated storage helpers, PALite SQLite layout, key-provider extension, layered table data, checkpoint, reopen, and crash recovery.

Risks and edge cases: uses hard-coded PALite special file IDs and regex parsing of page data. It skips non-PALite backends, so coverage is backend-specific.

Test signals: dataset checks pass; SQLite metadata validates page id/version; key-provider row counts match expectations after reopen/crash and checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg02.py

Purpose: ensures a crash during checkpoint key rotation does not corrupt persisted key-provider metadata.

Important APIs and functions: decorated with `@disagg_test_class`; scenarios cover crash trigger points `before_key_rotation`, `during_key_rotation`, and `after_key_rotation`. It extends `suite_subprocess` to run `subprocess_func` in a child. SQLite helper `sqlite_fetch_shared_meta` reads the latest turtle metadata and optionally writes it to `key_provider.results`.

Control flow: the child populates a layered dataset, checkpoints, records shared metadata, then checkpoints with `debug=(checkpoint_crash_trigger_point=...)`, which is expected to crash/fail. The parent runs this subprocess, reopens/recoveries the home, fetches current metadata, and compares page id, LSN, and version against the pre-crash recorded metadata.

State and persistence behavior: key rotation during checkpoint must be atomic with respect to shared metadata. After crash recovery, metadata must remain at the last consistent pre-crash state.

Dependencies and integration points: integrates checkpoint crash debug hooks, key-provider extension, disaggregated PALite storage, subprocess crash harness, SQLite inspection, and recovery.

Risks and edge cases: crash trigger names are internal contracts. Regex parsing of page data and result-file handoff are brittle but direct.

Test signals: after recovery, page id, LSN, and version match the saved pre-crash metadata for each crash point.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg03.py

Purpose: verifies the key-provider `set_key` push API persists a supplied key once the stable timestamp reaches that key's timestamp.

Important APIs and functions: uses `wiredtiger.CryptKeys`, `conn.get_key_provider().set_key`, PALite SQLite inspection helpers, and the test key-provider extension configured with `version=1`. It validates page id/version in the turtle metadata and counts key-provider pages.

Control flow: the test skips non-PALite storage, populates a small layered dataset, pushes a key at timestamp 1, advances stable timestamp to 1, checkpoints, then verifies at least one key-provider page exists and turtle metadata points to the expected main KEK page/version.

State and persistence behavior: pushed keys are pending until stable timestamp selection. Checkpoint persists the selected pushed key into the key-provider store and updates metadata.

Dependencies and integration points: integrates disaggregated storage, key-provider extension version 1, stable timestamp semantics, `CryptKeys`, checkpoint, and PALite SQLite validation.

Risks and edge cases: only one pushed key and timestamp are tested here. It relies on hard-coded special file IDs and page-data regex.

Test signals: `set_key` returns 0; key-provider page count is at least one; metadata validates page id 1 and version 1.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg04.py

Purpose: verifies data remains readable while toggling key-provider extension behavior between version 0 pull mode and version 1 push mode across restarts.

Important APIs and functions: scenarios start at version 0 or 1. `conn_extensions` loads the test key-provider with `version={current_version}`. `checkpoint` conditionally pushes a `CryptKeys` entry and advances stable timestamp for version 1, or just checkpoints for version 0. `restart_with_version` calls `restart_without_local_files`.

Control flow: the test skips non-PALite storage, sets a starting version, reopens, populates batch 1 and checkpoints, restarts with the other version and verifies, adds batch 2 and checkpoints, restarts back to the start version and verifies, adds batch 3 and checkpoints, then restarts to the other version and verifies all data.

State and persistence behavior: persisted layered data encrypted under keys from both provider modes must remain readable after local-file-less restarts. Push-mode checkpoints require stable timestamp advancement to persist pushed keys.

Dependencies and integration points: integrates disaggregated restart semantics, key-provider extension version toggles, layered table data, `CryptKeys`, checkpoint, and dataset validation.

Risks and edge cases: only PALite is covered. `current_version` is mutable class/test state and must be set before connection opens for extension config correctness.

Test signals: each `SimpleDataSet.check()` succeeds after every version flip and after additional writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg05.py

Purpose: tests selection of pushed keys across checkpoints for key-provider version 1, including draining multiple pending keys and selecting the highest key at or below stable timestamp.

Important APIs and functions: `key_provider_pages` reads PALite key-provider pages via SQLite, extracts the key bytes by parsing the crypt header size, and returns rows ordered by LSN. `key_for` encodes the timestamp into key bytes; `push_key` calls `conn.get_key_provider().set_key` with `CryptKeys`.

Control flow: `test_multiple_pushes_across_checkpoints` pushes keys 1-3, advances stable to 3, writes a row, checkpoints, and validates key 3; then pushes/validates keys 4 and 5 in separate checkpoints. `test_select_highest_at_or_below_stable` pushes keys 1-3, advances stable only to 2, checkpoints and validates key 2, then advances stable to 3 and validates key 3 on the next checkpoint.

State and persistence behavior: key-provider state includes a pending queue of pushed keys plus persisted pages. Checkpoint should persist the latest eligible key at or below stable and leave later keys pending.

Dependencies and integration points: integrates PALite SQLite storage, key-provider extension `version=1,key_expires=0`, `CryptKeys`, stable timestamp selection, layered tables, and checkpoint.

Risks and edge cases: byte parsing assumes crypt-header layout and offset 6 contains header size. Only PALite is validated.

Test signals: latest key-provider page has page id 1 and key bytes matching the expected timestamp after each checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint01.py

Purpose: basic layered-table checkpoint/statistics test for disaggregated leader mode with PALite page log configuration.

Important APIs and functions: decorated with `@disagg_test_class`; `conn_config` enables statistics, JSON stats logging, disaggregated leader role, and a PALite page log. The test uses `statistics:<uri>` and `stat.dsrc.btree_entries`.

Control flow: it creates a layered table, inserts three string-key records per loop for 50,000 loop iterations, scans the table counting all entries, then opens a data-source statistics cursor and checks btree entry count.

State and persistence behavior: layered table state is written under disaggregated storage. The test does not explicitly call checkpoint in the body, so it primarily validates live layered-table insert/read/stat behavior under configured disaggregation.

Dependencies and integration points: integrates layered URI support, disaggregated leader configuration, statistics cursors, and large insert/scan workload.

Risks and edge cases: large `nitems` makes it heavier than a unit smoke test. Without explicit checkpoint, it provides limited checkpoint coverage despite the file name.

Test signals: scan count equals `nitems * 3`, and `stat.dsrc.btree_entries` also equals `nitems * 3`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint02.py

Purpose: tests follower visibility and cursor stability across layered-table checkpoints and leader/follower state changes in disaggregated storage.

Important APIs and functions: decorated with `@disagg_test_class`; scenarios use disaggregated-only storage. Helpers `put_data`, `check_data_follower`, `scan_data_follower`, `close_cursors`, `reset_cursors`, and `reset_follow_cursor` manage leader writes and follower reads. It uses `disagg_advance_checkpoint` and opens a separate follower connection with `disaggregated=(role="follower")`.

Control flow: the test creates layered tables on the leader, opens a follower, writes version 0 and checkpoints/advances follower, verifies. It writes version 1 and keeps follower cursors open, writes version 2 and reopens cursors, writes version 3 and resets cursors, then scans half of version 3 with open cursors, writes/checkpoints version 4 and advances follower, confirms the open layered cursors continue scanning old version 3, then closes/reopens and sees version 4. Later sections continue testing state changes such as follower step-up to leader and visibility of new data.

State and persistence behavior: checkpoint advancement changes the follower's visible state, but open cursor iteration should remain insulated from subsequent state changes. Closed/reset cursors should observe the appropriate latest checkpoint.

Dependencies and integration points: integrates disaggregated leader/follower roles, layered URIs, checkpoint propagation, cursor positioning, string key ordering, and non-layered disagg block-manager configuration paths.

Risks and edge cases: cursor ordering uses lexicographic sorted string keys (`keys_in_order`), not numeric order. Non-layered cursor handling has a source comment about reset/reopen behavior, so layered and non-layered URI expectations differ.

Test signals: follower reads exact value prefixes for each checkpoint version; open layered scans continue old values after checkpoint advancement; reopened scans see new values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint02.py -->
