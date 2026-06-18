# subset-b-009088 Research

Grouped research for `subset-b-009088`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable47.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable47.py

Purpose: regression coverage for rollback-to-stable and reconciliation when RTS-created tombstones are later made globally obsolete under a mixed stable/unstable update chain. The test reproduces an out-of-order durable timestamp shape that previously risked invariant failures.

Important APIs/types/functions: `test_rollback_to_stable47` extends `test_rollback_to_stable_base`; it uses `SimpleDataSet`, `wiredtiger.WT_NOTFOUND`, `stat.conn.checkpoint_snapshot_acquired`, `checkpoint_thread`, backup cursors, timestamp helpers, prepared transactions, and `debug=(release_evict)`.

Control flow: create a small row/column table, write stable keys at ts 10 and unstable keys at ts 30, checkpoint, copy a backup, reopen the backup so recovery RTS tombstones unstable keys at stable ts 20, reinsert prepared data at durable ts 26, advance stable/oldest to 30, write newer unstable data at ts 35, then run checkpoint and eviction concurrently under `checkpoint_slow`.

State and persistence behavior: the test deliberately moves data between in-memory update chains, on-disk checkpoint images, backup recovery, and eviction/reconciliation. The persistent signal is that backup recovery removes keys 6-10, while later prepared and unprepared reinserts create the chain shape reconciliation must preserve.

Dependencies/integration points: integrates RTS, backup cursor copying, crash-recovery semantics, checkpoint timing stress, transaction timestamps, prepared updates, eviction, and statistics. Risks are timing sensitivity and hook incompatibilities around timestamp ordering, backup content, and eviction not occurring; assertions verify stable values, missing unstable values, and absence of reconciliation failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable47.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_salvage01.py

Purpose: verifies WiredTiger salvage through both the `wt salvage` utility and the Python API, for empty, healthy, and intentionally damaged row-store and variable-length column-store files.

Important APIs/types/functions: `test_salvage01` extends `WiredTigerTestCase` and `suite_subprocess`; helpers include `moreinit`, key/value generators, `populate`, `check_populate`, `check_damaged`, `damage_inner`, `runWt`, `session.salvage`, `salvageUntilSuccess`, and `session.verify`. Scenarios cover string row keys, record-number column keys, and optional `failpoint_eviction_split` timing stress.

Control flow: each test creates `table:test_salvage01.a`, optionally populates 1000 records with one unique corruption target, runs salvage in-process or via subprocess, and revalidates contents. Damaged tests close the connection, modify the `.wt` file byte matching the unique string, reopen with prefetch disabled, confirm verify reports checksum damage, then salvage and accept a partial but internally consistent table.

State and persistence behavior: damage is performed directly on the persisted table file after clean close, so salvage must rebuild from disk structures rather than in-memory state. VLCS uses small pages to avoid losing the entire table to one-page corruption.

Dependencies/integration points: covers file naming, table/file URI differences, external `wt`, stdout/stderr filtering, checksum detection, and prefetch interaction. Risks include brittle byte searching, page-size sensitivity, and partial salvage expectations; test signals are no error output for clean salvage, full record preservation for undamaged data, and at least some correct records after repair.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_salvage02.py

Purpose: validates startup with `salvage=true` after the history store file is removed, ensuring primary table data remains openable and readable after history-store loss.

Important APIs/types/functions: `test_salvage02` uses `SimpleDataSet`, timestamped transactions, `wiredtiger_strerror`, `WT_ROLLBACK`, `WiredTigerError`, and `make_scenarios` for row-integer and column key formats. `large_updates` writes each row in its own transaction and rolls back if a rollback error is surfaced.

Control flow: populate a table with 1000 rows, write value A at commit ts 1, pin oldest/stable at 1, write value B at commit ts 2 to create history store content, checkpoint, close the connection, delete `WiredTigerHS.wt`, reopen with `salvage=true`, and read the table.

State and persistence behavior: the key state transition is from a timestamped table with history store contents to a deliberately incomplete home directory. The test does not validate historical reads; it checks that salvage can reconstruct a usable current table view with the expected row count.

Dependencies/integration points: exercises history store file handling, salvage startup configuration, checkpoint durability, timestamp metadata, and dataset key formatting. Risks include assumptions about the history store filename and value visibility after salvage; the test signal is successful reopen plus exactly `nrows` records from `session.open_cursor`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_salvage03.py

Purpose: tests salvage behavior when key metadata or data files are removed from a copied WiredTiger home, distinguishing files that should still open, files salvage can repair, and files known not to be salvageable.

Important APIs/types/functions: `test_salvage03` extends `WiredTigerTestCase` and `suite_subprocess`; it uses `helper.copy_wiredtiger_home`, `databaseCorrupted`, `reopen_conn`, scenario sets for `WiredTiger`, `WiredTiger.basecfg`, `WiredTiger.turtle`, `WiredTiger.wt`, `WiredTigerHS.wt`, and `test_salvage03.wt`, plus row and column key formats.

Control flow: create and populate a table, copy the live home to `RESTART`, close, remove one selected file, copy that corrupted directory to `RESTART2`, and try both normal and salvage opens depending on the scenario. For salvageable cases it opens with `cache_size=1GB,salvage=true`; for known bad cases it expects `WiredTigerError`.

State and persistence behavior: persistence is modeled by directory copies taken before clean close, then metadata/data loss on the copy. The test checks whether recovery plus salvage can rebuild enough metadata and file state to open.

Dependencies/integration points: integrates metadata files, turtle/base config handling, history store absence, table file absence, row/column formats, and skip hooks for tiered storage. Risks include intentionally broad error regexes and a skipped turtle anomaly; signals are successful salvage opens or expected open failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema01.py

Purpose: verifies basic table, column group, and cursor behavior across empty/recreated schema lifecycle and reopen boundaries.

Important APIs/types/functions: `test_schema01` extends `TieredConfigMixin` and `WiredTigerTestCase`; it uses `gen_tiered_storage_sources`, `make_scenarios`, `session.create`, `dropUntilSuccess`, and table cursors. Static inputs `pop_data` and `expected_out` define country/year/population rows and expected padded string-key ordering.

Control flow: for both no-reopen and reopen cases, create a table with `key_format=5s`, `value_format=HQ`, named columns, and two column groups; insert records via overwrite cursor; optionally reopen the connection; iterate the table; compare stringified rows to expected order; then drop the table.

State and persistence behavior: the reopen scenario verifies schema metadata, column group metadata, padded fixed-size string keys, and records survive close/reopen. The repeated create/drop loop checks cleanup before recreation.

Dependencies/integration points: covers tiered scenario generation, column-group table mappings, fixed-width string keys, `dropUntilSuccess`, and cursor iteration. Risks include expected string formatting being tightly coupled to Python binding display; test signals are exact row order/value strings and successful table drops.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema02.py

Purpose: broad schema API coverage for table column declarations, column group validation, index creation order, populated and post-population index building, and data/index correctness.

Important APIs/types/functions: `test_schema02` uses `wiredtiger.WiredTigerError`, `TieredConfigMixin`, `make_scenarios`, `expect_failure_colgroup`, `populate`, `check_entries`, and `check_indices`. It builds a compound key/value schema with columns `(ikey,Skey,S1,i2,S3,i4)` and two column groups.

Control flow: negative tests assert invalid formats, bad column counts, missing table/colgroup names, invalid columns, key columns in column groups, duplicate exclusive creates, missing value-column coverage, and namespace isolation. Positive tests create indexes before and after column groups, populate 1000 rows with square/cube-derived values, create a late index, and verify primary and index cursor projections.

State and persistence behavior: schema state is entirely metadata-backed; the test stresses ordering of metadata creation and index backfill from existing data. No explicit reopen occurs, but late index creation validates durable table contents are scanned into index structures.

Dependencies/integration points: integrates schema validation, column groups, secondary indexes, compound keys, tiered scenarios, and error-message regexes. Risks include brittle error strings and floating cube-root inference; signals are expected exceptions, cursor counts, and exact value checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema03.py

Purpose: stress-tests complex, predictably random schema combinations: multiple tables, column groups, indexes, creation orders, connection restarts between phases, and index validation after incremental population.

Important APIs/types/functions: helper types `tabconfig`, `cgconfig`, and `idxconfig` generate table formats, keys, values, column group assignments, and index keys. `test_schema03` uses `suite_random`, `wtscenario.quick_scenarios`, resource limit changes, `TieredConfigMixin`, `session.create`, `reopen_conn`, and cursor search/iteration helpers.

Control flow: scenarios choose table count, column-group count, index count, table/index extra args, and restart points. The test builds each table config, assigns columns to groups and indexes, creates tables, creates column groups and indexes in phases, optionally reopens after each phase, populates a partial batch, creates late indexes, populates the rest, and validates every primary and index row.

State and persistence behavior: state spans schema metadata, generated key/value formats, current table entry counts, and reopen checkpoints after selected schema or data operations. It explicitly raises file descriptor limits because many tables and indexes can be open.

Dependencies/integration points: exercises the schema API, metadata persistence, secondary index backfill, file-type tables, tiered storage configs, and Python resource handling. Risks include high scenario complexity, known limitations around column groups after indexes, and Unix-only resource APIs; signals are exact row counts and successful indexed search for every generated entry.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema04.py

Purpose: verifies secondary indexes with duplicate keys, including indexes created before, during, and after table population.

Important APIs/types/functions: `test_schema04` uses `TieredConfigMixin`, `make_scenarios`, `session.create`, table/index cursors, and helpers `create_indices`, `populate`, and `check_entries`. Scenarios vary `create_index` as before first population, between two population phases, or after all rows are inserted.

Control flow: create `table:schema04` with integer primary key and six integer value columns. Populate rows in two halves with multiplication-table values modulo 100, create six single-column indexes at the scenario-selected time, then iterate the table and for each row search the corresponding duplicate index key until the matching value tuple is found.

State and persistence behavior: the primary table owns deterministic duplicated value distributions. Index state may be created empty, partially populated, or backfilled after full population, validating index maintenance across all lifecycle points.

Dependencies/integration points: covers duplicate secondary keys, index backfill, tiered storage scenarios, and cursor traversal through duplicate index entries. Risks include relying on scan-forward among duplicates; test signals are exact primary row/value checks and finding every expected value through each index.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema06.py

Purpose: stresses repeated secondary index creation and removal around column groups after inserting a larger dataset.

Important APIs/types/functions: `test_schema06` uses `TieredConfigMixin`, `make_scenarios`, `dropUntilSuccess`, and helpers `flip`, `unflip`, `create_index`, and `drop_index`. The active test is `test_index_stress`; `check_entries` appears to be leftover validation code for a different `table:main` shape and is not called.

Control flow: create `table:schema06` with string primary key, six string values, and two column groups. Create indexes on `s0` and `s1` around column-group creation, insert 1000 rows using digit-reversed transformed values, close the cursor, then drop both indexes.

State and persistence behavior: table data and column groups remain while index metadata and index files are created and deleted. The test is mostly about schema lifecycle cleanup rather than verifying data after drop.

Dependencies/integration points: covers schema metadata, index file creation/removal, column group interactions, tiered scenarios, and `dropUntilSuccess` retry semantics. Risks include limited final assertions and dead helper code; the main signal is absence of errors during heavy insert and index drop.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema07.py

Purpose: long-running cache pressure test ensuring repeated metadata create/drop activity does not fill a small cache.

Important APIs/types/functions: `test_schema07` uses `TieredConfigMixin`, `make_scenarios`, `wttest.longtest`, `session.create`, `session.open_cursor`, and `dropUntilSuccess`. Connection config sets `cache_size=10MB`.

Control flow: loop 20,000 times creating a unique table name, opening a cursor, inserting one key/value pair, closing the cursor, and dropping the table.

State and persistence behavior: this test repeatedly creates and destroys schema metadata and table files while relying on eviction/metadata cleanup to prevent the cache from remaining pinned. There is no final stats assertion; progress through all iterations is the signal.

Dependencies/integration points: integrates metadata cache behavior, table lifecycle, tiered storage scenario generation, and long-test scheduling. Risks include runtime cost and dependence on cache/metadata cleanup timing. Test signals are successful completion without cache stalls, rollbacks, or create/drop failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema08.py

Purpose: validates recovery behavior for schema operations by truncating log copies at each schema log record boundary and running recovery/listing on the partial homes.

Important APIs/types/functions: `test_schema08` mixes `TieredConfigMixin`, `suite_subprocess`, log cursors, `session.log_flush`, `session.alter`, `session.drop`, checkpoint, `runWt`, and filesystem copying/truncation via `os` and `shutil`. Scenarios cover file/table URIs, column groups, indexes, no-op/alter/drop operations, and optional checkpoints.

Control flow: create a main object, optionally checkpoint, create a column group or index subobject, optionally alter or drop the schema, walk the log cursor to collect whole-record LSN offsets, copy the home once per LSN, truncate `WiredTigerLog.0000000001` to that offset, then run `wt -R -h <backup> list -v`.

State and persistence behavior: state is persisted in the log and metadata files; each backup represents recovery before a selected record. Tiered scenarios skip backup/recovery truncation because copied local logs are not equivalent.

Dependencies/integration points: covers schema logging, metadata recovery, log cursor record semantics, external `wt`, and backup-like copies. Risks include one-log-file assumption, platform lock-file exclusions, and broad expected error handling; signals are successful recovery/listing for all truncated states.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema09.py

Purpose: regression test for recovery cleanup of incomplete table metadata left by crashes at precise schema create/drop points.

Important APIs/types/functions: `test_schema09` extends `WiredTigerTestCase` and `suite_subprocess`; it uses `conn.reconfigure` with `debug_mode=(crash_point=...)`, subprocess function execution, metadata cursors, `wiredtiger.WT_NOTFOUND`, and `expectedStdoutPattern`. Hooks skip tiered and disaggregated storage.

Control flow: close the main connection, run a subprocess that enables one crash point and performs create or drop expected to crash, reopen the resulting home and expect "removing incomplete table", disable the crash point, verify file/table/colgroup metadata entries are gone, assert open/drop fail, then create and drop the same table successfully.

State and persistence behavior: the test relies on log-enabled recovery and deliberately inconsistent metadata involving table, file, and colgroup entries. Recovery must force-drop incomplete schema artifacts before normal use resumes.

Dependencies/integration points: integrates debug crash points, subprocess isolation, metadata cursor lookup, recovery messages, and schema APIs. Risks include crash-point names and stdout text coupling; signals are metadata absence after recovery and successful recreate/drop lifecycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema10.py

Purpose: validates that `session.create` rejects URI types with an empty object name.

Important APIs/types/functions: `test_schema10` uses `make_scenarios`, `wiredtiger.WiredTigerError`, and `assertRaisesWithMessage`. Scenarios cover `colgroup:`, `file:`, `index:`, `layered:`, and `table:`.

Control flow: for each URI prefix with no name, call `session.create(self.uri, "key_format=S,value_format=S")` and expect a `WiredTigerError` matching `URI requires a non-empty name`.

State and persistence behavior: no persistent objects should be created; the test is purely validation of URI parsing and schema admission control.

Dependencies/integration points: covers the schema dispatch path shared by multiple URI kinds, including layered objects. Risks are minimal but error text is asserted exactly by regex. Test signal is rejection before any object creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_scrub_eviction_prepare.py -->
# sources/storage-engines/wiredtiger/test/suite/test_scrub_eviction_prepare.py

Purpose: verifies that scrub eviction of a page containing a prepared update writes the prepared state cleanly enough that later checkpoints do not repeatedly reconcile the leaf page.

Important APIs/types/functions: `test_scrub_eviction_prepare` uses `wttest.skip_for_hook`, multiple sessions, prepared transactions, `debug=(release_evict)`, `session.checkpoint`, and data-source statistic `stat.dsrc.btree_checkpoint_pages_reconciled`. Connection config enables all stats and JSON stats logging.

Control flow: create an integer/string table, insert key 2 committed in one session, prepare an update for key 1 in another session, close the updating cursor, release-evict key 2 to evict the page containing both keys, checkpoint, record reconciled pages, read key 2 to fault the page back in, checkpoint twice more, and assert the reconciled page count remains 1.

State and persistence behavior: prepared update state is persisted by scrub eviction and re-instantiated cleanly. The test avoids prepared conflicts by reading key 2, not key 1.

Dependencies/integration points: integrates prepare, eviction, scrub/reconciliation, checkpoint stats, and session isolation; tiered is skipped. Risks include eviction not happening if cursors pin pages, which the test addresses by closing the cursor. Signals are stable reconciliation stats across repeated reads/checkpoints.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_scrub_eviction_prepare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_search_near01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_search_near01.py

Purpose: verifies `search_near` behavior for a search key past the end of a table after the last key is updated or deleted.

Important APIs/types/functions: `test_search_near01` uses scenarios for record-number and row-store integer keys, update/delete modes, table creation, cursor operations, checkpoint, and `debug=(release_evict)`.

Control flow: create a file object with integer values, insert keys 1 through 1000 with value 1, checkpoint, evict all rows, then either delete key 1000 or update it to value 2. Start a transaction, set the cursor key to 1100, call `search_near`, and verify the positioned key/value.

State and persistence behavior: checkpoint and eviction force a disk image with later in-memory changes to the last key. Delete mode expects the nearest visible key to move to 999; update mode expects key 1000 with the new value.

Dependencies/integration points: covers cursor search-near positioning, row-store and VLCS key spaces, deletion visibility, and eviction. Risks include implicit transaction visibility and not checking the return sign from `search_near`; signals are exact positioned key/value assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_search_near01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_search_near02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_search_near02.py

Purpose: timestamped variant of search-near past end, ensuring an invisible last-key update or delete does not hide the older visible value.

Important APIs/types/functions: `test_search_near02` mirrors `test_search_near01` with scenarios for record-number and row keys, update/delete mode, checkpoint, release eviction, commit timestamps, and read timestamps.

Control flow: insert keys 1 through 1000 with value 1, checkpoint and evict them, update or delete key 1000 at commit timestamp 10, then open a transaction at read timestamp 5 and call `search_near` for key 1100.

State and persistence behavior: the committed change at ts 10 is not visible to the read at ts 5, so both update and delete scenarios must position on key 1000 with value 1. This validates history/update-chain visibility at the high end of the key space after eviction.

Dependencies/integration points: integrates cursor positioning, timestamp visibility, tombstones, row/VLCS formats, and on-disk pages. Risks mirror the non-timestamped test plus timestamp setup assumptions; signals are exact key 1000 and old value assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_search_near02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_shared_cache01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_shared_cache01.py

Purpose: exercises basic shared-cache behavior across multiple independent WiredTiger home directories and connections, including joining/leaving, full allocation, verbose output, default configs, mixed shared/non-shared connections, and invalid absolute eviction configuration.

Important APIs/types/functions: `test_shared_cache01` manually manages connections by overriding setup/close hooks. Helpers `openConnections`, `closeConnections`, and `add_records` use `wiredtiger_open`, `shared_cache=(name=pool,...)`, filesystem directory setup, sessions, and overwrite cursors.

Control flow: tests open two to four homes with a shared cache, create the same table in each, and insert data. Specialized cases fill the cache with repeated batches, add a late third connection, close one connection while others continue, check verbose output for pool creation, open one connection outside the pool, and exercise default shared-cache values.

State and persistence behavior: each home persists its own table, while cache quota and eviction settings are shared by pool name across connections. The test mostly validates configuration and operation completion rather than detailed persisted data reads.

Dependencies/integration points: integrates connection-level shared cache, eviction config validation, capture output, directory management, and multi-connection lifecycle. Risks include memory/runtime cost and global shared-cache side effects; signals are successful writes/closes and expected errors for absolute eviction thresholds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_shared_cache01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_shared_cache02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_shared_cache02.py

Purpose: validates shared-cache reconfiguration semantics, especially pool size/reserve changes and rejection of absolute eviction values during reconfigure.

Important APIs/types/functions: `test_shared_cache02` has the same manual multi-connection harness as `test_shared_cache01`: `openConnections`, `closeConnections`, `add_records`, `wiredtiger_open`, `Connection.reconfigure`, and `assertRaisesWithMessage`.

Control flow: create two connections in a shared pool, write data, then reconfigure pool size successfully. Other tests start with a 50M pool and 20M reserves, attempt an over-quota reserve update that must fail, perform a valid reserve update, switch previously non-shared connections into a shared cache, and verify absolute `eviction_trigger`/`eviction_target` values are rejected while percentage values pass.

State and persistence behavior: state is primarily connection configuration and shared-cache pool accounting; table data is present to make the connections active and consume cache. Failed reconfigure must not corrupt the current pool configuration.

Dependencies/integration points: covers reconfiguration admission control, reserve accounting across multiple connections, and eviction percentage validation. Risks include test sensitivity to memory quotas and config parser messages; signals are successful reconfigure calls or exact expected `WiredTigerError` messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_shared_cache02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_split.py -->
# sources/storage-engines/wiredtiger/test/suite/test_split.py

Purpose: checks that reconciliation creates expected leaf page splits for a simple row-store file as records are appended and inserted.

Important APIs/types/functions: `test_split` uses `WiredTigerTestCase`, `stat.dsrc.btree_row_leaf`, `session.create`, cursors, and repeated `reopen_conn` calls. Connection config enables all statistics.

Control flow: create a file with 4KB allocation and leaf pages plus `split_pct=75`, insert 35 records sized to fit one leaf page, reopen and assert one row leaf page, append 10 records enough to exceed the page target, reopen and assert two leaf pages, then insert five records in the key gap and confirm the leaf-page count remains two.

State and persistence behavior: each `reopen_conn` stabilizes the table by closing and reopening, forcing reconciliation and durable page layout. The assertions depend on physical page sizes, not only logical contents.

Dependencies/integration points: integrates reconciliation split policy, file-store page sizing, statistics, and connection reopen. Risks are explicitly noted: changes in reconciliation page sizing can legitimately alter expected counts. Test signals are exact `btree_row_leaf` values after each phase.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_split.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat01.py

Purpose: foundational statistics cursor tests for connection stats, data-source stats, checkpoint-specific stats, size stats, and missing-file error handling.

Important APIs/types/functions: `test_stat01` uses `wiredtiger.stat`, `SimpleDataSet`, `simple_key`, `make_scenarios`, helper `statstr_to_int`, and `check_stats`. Scenarios cover file/table URIs and column/string-row keys.

Control flow: connection stats populate and checkpoint a dataset, scan `statistics:` entries for block writes, and verify keyed lookup consistency. Data-source stats create overflow-prone values, reopen, inspect page-size and overflow stats, check backup stats are readable, and open a size-only stats cursor. Checkpoint stats create named checkpoints and verify entry counts per checkpoint. Missing-file stats expects an open failure.

State and persistence behavior: reopen and named checkpoint paths validate stats from persisted btree state and checkpoint metadata. String stat values are parsed and compared to integer stat fields.

Dependencies/integration points: covers connection, dsrc, checkpoint, and size statistics APIs plus dataset helpers. Risks include stat descriptions changing and timestamp hook skip on checkpoint stats; signals are found stats, min thresholds, self-consistent value strings, and expected errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat02.py

Purpose: comprehensive statistics cursor configuration tests: database-level enabled modes, cursor mode compatibility, clear behavior, fast-vs-all collection, invalid mode combinations, and cache/tree walk options.

Important APIs/types/functions: the file defines several test classes using `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, `wiredtiger.stat`, and `wiredtiger_open`. It exercises `statistics=(none|fast|all|size|clear|cache_walk|tree_walk)` at connection and cursor scope.

Control flow: scenario tests populate data and verify which cursor configurations open or fail. Clear tests read stats twice to confirm selected counters reset while others persist. Fast tests confirm btree entry counts are omitted from fast cursors and present in all cursors. Error tests reject conflicting statistics modes. Cache-walk tests reconfigure live connections and assert cache/tree walk stats appear independently.

State and persistence behavior: statistics state is mutable and sometimes cleared on cursor open; populated datasets provide counters. Cache-walk stats can persist because many are not clearable, so the test orders cases carefully.

Dependencies/integration points: covers connection open config parsing, session cursor config parsing, dsrc stats, cache walk, tree walk, and complex dataset index/colgroup behavior. Risks include ordering-sensitive clear semantics and exact error regexes; signals are successful/failed cursor opens and precise stat values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat03.py

Purpose: verifies that resetting a data-source statistics cursor refreshes values, and that complex datasets report multiplied entry counts through table, index, and column-group stats.

Important APIs/types/functions: `test_stat_cursor_reset` uses `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, `stat.dsrc.btree_entries`, helper `stat_cursor`, and dataset methods `colgroup_count`, `index_count`, `index_name`, and `colgroup_name`.

Control flow: populate 100 entries for file/table simple row/var and complex table scenarios. Open a stats cursor and assert initial `btree_entries`, insert one more record through a data cursor, check the stale stats cursor still reports the old count, call `statc.reset`, and verify the updated count. For complex datasets, also check a direct index and colgroup stats cursor reports the base row count.

State and persistence behavior: the stats cursor snapshots values until reset. Complex table stats aggregate multiple backing btrees, so count state differs between the logical table and individual btrees.

Dependencies/integration points: covers statistics cursor reset semantics, dataset abstraction, index/colgroup backing stores, and key/value formats. Risks include assumptions about entry multiplication; signals are exact counts before and after reset.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat04.py

Purpose: validates that the `btree_entries` statistic accurately tracks key/value pair counts through inserts, removes, and reopen for row and column stores with different value sizes.

Important APIs/types/functions: `test_stat04` uses `suite_subprocess`, `make_scenarios`, `stat.dsrc.btree_entries`, and helpers `init_test`, `genkey`, `genvalue`, and `checkcount`. Scenarios cover small, medium, large, and jumbo value workloads.

Control flow: create a table for the selected key format and workload size, insert entries while checking count every 50 records, remove a deterministic subset by modular key selection and check after each successful remove, close the cursor, reopen the connection, and verify the final count again.

State and persistence behavior: the statistic must be correct both in memory and after the btree is written and reopened. Jumbo values also exercise overflow/value storage while preserving entry counts.

Dependencies/integration points: covers row/column key generation, statistics with `clear`, large data volumes, and persistent btree metadata. Risks include runtime for large scenarios and exact count tracking under duplicate removal attempts; signals are exact `btree_entries` equality throughout.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat05.py

Purpose: verifies that size-only data-source statistics cursors can be opened and walked across table/file types, in-memory configurations, and complex datasets while a table grows.

Important APIs/types/functions: `test_stat_cursor_config` uses `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, `conn_config=statistics=(fast)`, helper `openAndWalkStatCursor`, and dataset cursor helpers. Scenarios cover file/table row, file/table var, in-memory row/var, and complex-row table.

Control flow: choose row or variable-length column key/value formats, populate 100 records, open and fully iterate a `statistics=(size)` cursor, then insert records 100 through 40000 while reopening/walking the size stats cursor every 100 records, and once again at the end.

State and persistence behavior: size stats must remain available during ongoing growth and under fast database statistics. In-memory scenarios have no disk size in the same sense, but cursor open/walk must still be valid.

Dependencies/integration points: covers size stats, fast stats compatibility, large insert loops, file/table/in-memory data sources, and complex dataset backing objects. Risks are runtime and scenario-specific size stat availability; signal is absence of cursor open/iteration failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat06.py

Purpose: checks that statistics collection starts or remains disabled according to connection configuration, including interaction with statistics logging.

Important APIs/types/functions: `test_stat06` uses manual close/reopen with `wiredtiger_open`, `sleep`, `stat.conn.file_open`, and `assertRaisesWithMessage`. Default test config disables statistics.

Control flow: `test_stats_on` closes the default connection, opens with `statistics=(fast)`, creates two tables, waits, and confirms `statistics:` opens and reports file-open count. `test_stats_off` opens with `statistics=(none),statistics_log=(json)`, creates tables, waits, and expects opening `statistics:` to fail with a database statistics configuration error.

State and persistence behavior: statistics availability is connection-scoped runtime state; the test does not depend on table data beyond creating objects to affect file stats.

Dependencies/integration points: covers connection-level statistics config, statistics log config, cursor open admission, and background timing. Risks include sleep-based timing and exact error message coupling; signals are successful stats cursor read or expected cursor open failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat07.py

Purpose: validates session statistics cursor configuration compatibility and reset behavior.

Important APIs/types/functions: `test_stat_cursor_config` uses `SimpleDataSet`, `make_scenarios`, `session.open_cursor('statistics:session')`, `session.reset`, cursor `reset`, and `assertRaisesWithMessage`. Connection scenarios cover `statistics=none`, `fast`, and `all`; cursor scenarios cover empty, fast, and all.

Control flow: populate a small file dataset, build the cursor statistics config string, and either open a session stats cursor or assert the database statistics configuration rejects it. For valid combinations, call `session.reset`, reset the stats cursor, iterate all session stat values, and assert each value is zero while at least one stat was present.

State and persistence behavior: session statistics are per-session runtime counters and should be cleared by session reset plus cursor reset. No persistent data assertion beyond dataset population is required.

Dependencies/integration points: covers session stat URI, database statistics modes, config compatibility matrix, and session reset. Risks include expectations that every stat is zero after reset; signal is complete zeroed iteration or expected open failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat08.py

Purpose: checks session-level cache read and transaction dirty-byte statistics, including reset behavior.

Important APIs/types/functions: `test_stat08` uses `wiredtiger.stat.session.bytes_read`, `read_time`, `txn_bytes_dirty`, `stat.conn.cache_bytes_dirty`, `statistics:session`, `statistics:`, and a session opened with `debug=(release_evict_page=true)`.

Control flow: create a table, start a transaction, assert transaction dirty bytes start at zero and do not exceed connection dirty bytes, insert many large values while checking dirty bytes increase, periodically roll back/restart the transaction and verify dirty bytes reset, commit, scan the table, then read session stats for bytes read and page read time. Finally reset the session stats cursor and assert all values are zero.

State and persistence behavior: the test uses a large in-memory workload and explicit transaction boundaries rather than checkpoint/reopen. It validates runtime accounting for dirty bytes and reads into cache after cursor scans.

Dependencies/integration points: covers session stats, connection stats, release-evict debug behavior, transaction accounting, and Windows time-granularity skip. Risks include large loop cost and timing stat portability; signals are monotonic dirty byte changes, positive read stats, and zeroed reset stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat09.py

Purpose: verifies connection statistics for the oldest active read timestamp and the timestamp range pinned by that reader.

Important APIs/types/functions: `test_stat09` uses timestamped transactions, random insert order, `statistics:`, helper `check_stats`, and helper `check_stat_oldest_read`. It inspects stats by description string rather than `wiredtiger.stat` constants.

Control flow: create a table, insert keys 1 through 100 with commit timestamp equal to key, open a reusable stats cursor, confirm no active reader reports zero, then create five sessions with read timestamps 10, 20, 30, 40, and 50. Commit readers and advance oldest timestamp through several values, checking oldest-reader and pinned-range stats after each change. Commit the remaining readers and verify stats return to zero.

State and persistence behavior: state is transactional: active sessions pin read timestamps independently of newest commits and oldest timestamp. Pinned range is computed relative to oldest timestamp only when oldest is at or beyond the active reader.

Dependencies/integration points: covers timestamp manager, active transactions, connection stats, session lifetimes, and randomized writes. Risks include stat description text coupling; signals are exact stat values at every phase.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat10.py

Purpose: validates table-type-specific btree statistics for row-store and variable-length column-store under timestamped updates, deletes, overflow values, and eviction.

Important APIs/types/functions: `test_stat10` uses `make_scenarios` with oldest/stable timestamp constraints, `stat.dsrc.btree_entries`, `btree_row_empty_values`, `btree_column_deleted`, `btree_column_rle`, `btree_overflow`, backup block stats, and release eviction.

Control flow: create a row or VLCS table with raw-byte values, set oldest/stable to 10, insert 100 records at ts 20 with a mix of invariant values, compound values, empty row values, and overflow-sized keys/values, delete two keys at ts 30, advance oldest/stable per scenario, evict sample keys, open data-source stats, and validate each stat based on format and timestamp scenario.

State and persistence behavior: eviction is required to materialize RLE and overflow accounting. Timestamp visibility is intentionally not fully specified, so assertions encode expected current behavior separately from format-specific expectations.

Dependencies/integration points: covers row/VLCS btree encoding, timestamps, overflow, tombstones, eviction, backup stat access, and disaggregated-storage skips/adjustments. Risks include physical encoding sensitivity; signals are exact stat values by scenario.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat11.py

Purpose: smoke test ensuring selected eviction-blocked connection statistics exist in the Python stat namespace and can be read.

Important APIs/types/functions: `test_stat11` imports `wiredtiger`, opens `statistics:`, and dynamically resolves stat keys from `wiredtiger.stat.conn` names such as `cache_eviction_blocked_checkpoint`, `cache_eviction_blocked_hazard`, and several conflict/block reasons.

Control flow: open a connection statistics cursor and for each stat name fetch `stat_cursor[getattr(wiredtiger.stat.conn, s)][2]`, asserting the value is not `None`.

State and persistence behavior: no workload is required; the test only validates stat registration and cursor access. Values may be zero and are not semantically checked.

Dependencies/integration points: covers the generated Python stat bindings and connection statistics cursor. Risks are limited to renamed/removed stats; signal is successful lookup and non-`None` value for every listed stat.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat12.py

Purpose: validates eviction trigger and application-thread fill-ratio statistics exist, increment under cache pressure, and are bucketed by actual cache fill ratio.

Important APIs/types/functions: `test_stat12` and `test_stat12_fill_ratio_bucketing` use small-cache connection configs, eviction target/trigger settings, `wiredtiger.stat.conn.cache_eviction_trigger_*`, fill-ratio bucket stats, helper `populate_data`, and timed polling.

Control flow: existence tests simply read trigger and fill-ratio stats. Increment tests create a table, insert large values to fill a 1MB cache, checkpoint, dirty many records, read clean pages, then poll stats until eviction trigger and fill-ratio counters increase. Bucketing test configures all triggers above 50%, writes and dirties enough data, polls upper buckets, and asserts lower buckets stay zero.

State and persistence behavior: state is runtime cache pressure and dirty/update thresholds. Checkpoint separates clean from dirty phases, while polling allows eviction threads to process.

Dependencies/integration points: covers eviction configuration, app-thread eviction accounting, connection stats, dirty/update triggers, and floating-point fill-ratio computation. Risks include timing sensitivity under slow machines; signals are nonzero trigger/fill counters and correct bucket distribution.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat13.py

Purpose: checks that `btree_maximum_depth` is computed and remains discoverable after reopen for small two-level row and column-store trees.

Important APIs/types/functions: `test_stat13` uses `SimpleDataSet`, `make_scenarios`, `stat.dsrc.btree_maximum_depth`, `session.checkpoint`, `reopen_conn`, and dataset cursor helpers.

Control flow: populate 100 records in a row or column table, checkpoint, assert maximum depth is 2, reopen the connection, read one key to instantiate the btree depth information, and assert depth is still 2.

State and persistence behavior: the checkpoint persists the btree. After reopen, the maximum-depth statistic is populated only after an operation touches the table, so the test performs a cursor search before reading stats.

Dependencies/integration points: covers btree depth accounting, checkpoint/reopen behavior, row and column key formats, and data-source stats. Risks include page-size changes that alter tree depth; signals are exact depth value before and after reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat14.py

Purpose: verifies eviction threshold statistics report default and reconfigured values using percentage values multiplied by 100 for two decimal places of precision.

Important APIs/types/functions: `test_stat14` uses `wiredtiger.stat.conn.eviction_threshold_*`, `Connection.reconfigure`, `helper.WiredTigerCursor`, and `statistic_uri`. The unused `get_stat` helper can assert data-source stats but the active test reads connection stats.

Control flow: open a connection statistics cursor and assert defaults for cache full target/trigger, dirty target/trigger, and auto-derived updates target/trigger. Then reconfigure each eviction threshold individually (`eviction_target`, `eviction_trigger`, `eviction_dirty_target`, `eviction_dirty_trigger`, `eviction_updates_target`, `eviction_updates_trigger`) and assert the corresponding stat reflects the scaled value.

State and persistence behavior: this is live connection configuration state, not persisted data state. Auto-derived defaults validate internal config normalization.

Dependencies/integration points: covers configuration parsing, reconfiguration, stats precision/scaling, and helper cursor context management. Risks include default value changes; signals are exact scaled integer stats after each config.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat15.py

Purpose: verifies `cache_pages_inuse` and `cache_pages_inuse_leaf` connection statistics track cached leaf pages and decrease after cache clearing.

Important APIs/types/functions: `test_stat15` uses `stat.conn.cache_pages_inuse_leaf`, `stat.conn.cache_pages_inuse`, `get_conn_stat`, table cursors, checkpoint, and `reopen_conn`. Connection config enables all stats with a 100MB cache.

Control flow: first test creates a row table, inserts 1000 small records, reads leaf and total page counts, and asserts leaf pages are positive and total pages are at least leaf pages. Second test creates a larger table with 10,000 large records, checkpoints, records leaf pages before reopen, reopens to clear cache, and asserts leaf pages drop.

State and persistence behavior: inserted data populates cache; checkpoint persists the larger table before reopening. Reopen clears in-memory cache state while preserving data on disk.

Dependencies/integration points: covers cache page accounting, connection stats, checkpoint/reopen behavior, and btree page residency. Risks include background pages remaining after reopen or small workloads not allocating pages; signals are positive/increasing relationships and decrease after reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat16.py

Purpose: verifies cache read statistics distinguish internal and leaf page reads when a multi-page btree is faulted in from disk.

Important APIs/types/functions: `test_stat16` uses `stat.conn.cache_read_internal`, `stat.conn.cache_read_leaf`, helper `get_conn_stat`, small `leaf_page_max` and `internal_page_max`, checkpoint, `reopen_conn`, and full cursor iteration.

Control flow: create a row table with 4KB leaf/internal pages, insert 5000 records to force multiple leaves and internal pages, checkpoint, reopen to clear the cache, iterate the full table so disk pages are read into cache, then assert both internal and leaf read counters are positive.

State and persistence behavior: checkpoint pushes the btree to disk; reopen clears resident pages. The subsequent scan forces both page classes back into cache and updates connection-level counters.

Dependencies/integration points: covers page sizing, btree structure, checkpoint/reopen, cursor scans, and cache read accounting. Risks include page-layout changes or preloading that could reduce reads; signals are positive internal and leaf read stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat_log01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat_log01.py

Purpose: tests statistics log file creation under default path, custom path, periodic and on-close modes, plus readonly reopen compatibility after statistics logging is recorded in base config.

Important APIs/types/functions: `test_stat_log01` manually opens connections with `wiredtiger_open`, disables default setup/session hooks, uses `glob` to find `WiredTigerStat.[0-9]*`, sleeps for periodic logging, and closes connections to trigger on-close logging. `test_stat_log01_readonly` uses normal fixture setup and then `wiredtiger_open(..., "readonly")`.

Control flow: each logging test opens a connection with `statistics=(fast)` and a `statistics_log` config, waits or closes as needed, and asserts at least one stats file exists in the expected directory. The readonly test closes a logged home and verifies a readonly open succeeds.

State and persistence behavior: stats logging writes external `WiredTigerStat` files and may persist logging config into base configuration. Readonly open validates those persisted settings do not require writes.

Dependencies/integration points: covers stats logging, filesystem paths, on-close behavior, readonly open, and tiered skip for readonly crash. Risks include sleep timing and file glob assumptions; signals are stats file presence and successful readonly open.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat_log01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat_log02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat_log02.py

Purpose: validates JSON statistics log output and `sources=[file:]` inclusion of table/file statistics.

Important APIs/types/functions: `test_stat_log02` manually opens connections, uses `glob`, `json.loads`, helper `check_stats_file`, `check_file_is_json`, and `check_file_contains_tables`. It creates a `table:foo` object and expects `file:foo.wt` in the JSON `wiredTigerTables` object when sources are enabled.

Control flow: `test_stats_log_json` opens with `statistics_log=(wait=1,json,on_close=1)`, closes to force output, then parses every line of the first stats file as JSON. `test_stats_log_on_json_with_tables` opens with JSON stats logging and file sources, creates/writes a table, closes, verifies JSON syntax, and searches for table source output.

State and persistence behavior: output state is the on-disk stats log. On-close ensures deterministic generation without waiting for periodic timing.

Dependencies/integration points: covers stats logging JSON encoder, source filtering, table-to-file source naming, and file globbing; tiered is skipped for the table-source case. Risks include only checking the first stats file and expected JSON key names; signals are parseable JSON and expected table source presence.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat_log02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_strerror01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_strerror01.py

Purpose: verifies the Python session `strerror` API returns expected strings for WiredTiger sub-level error codes.

Important APIs/types/functions: `test_strerror` extends `WiredTigerTestCase` and `suite_subprocess`; it uses constants such as `WT_NONE`, `WT_BACKGROUND_COMPACT_ALREADY_RUNNING`, `WT_CACHE_OVERFLOW`, multiple conflict codes, and `session.strerror`.

Control flow: iterate the `sub_errors` list of `(code, expected_string)` pairs and call `check_error_code`, which asserts `self.session.strerror(error) == expected`.

State and persistence behavior: no persistent state is involved; this is a binding/API mapping test.

Dependencies/integration points: covers Python exposure of C error-code constants, string formatting, and session API behavior. Risks are exact string coupling and new/renamed codes; the signal is equality for every listed code, including live restore and disaggregated-storage conflict codes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_strerror01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep01.py

Purpose: verifies the sweep server closes and removes inactive data handles/files even while checkpoints keep one active table busy.

Important APIs/types/functions: `test_sweep01` uses `suite_subprocess`, `make_scenarios` for row/VLCS tables, `stat.conn` sweep/file stats, `session.checkpoint`, sleeps, and connection config `file_manager=(close_handle_minimum=0,close_idle_time=3,close_scan_interval=1)`.

Control flow: create 30 tables with 1000 records each, capture baseline sweep/file-open stats, create one active table, then loop up to 60 seconds doing checkpoints and inserts on the active table while polling `file_open` and sweep removal stats. Finally compare baseline and final counters.

State and persistence behavior: many table handles become inactive after cursor close. Checkpoints and active writes keep the connection busy while the background sweep server must close dead handles and reduce open files to the expected core set.

Dependencies/integration points: covers file manager sweep, session handle sweeping, checkpoint interaction, file-open accounting, row/VLCS formats, and hook skips for disagg/tiered. Risks include timing sensitivity and expected final file count; signals are increased close/remove/sweep counters and reduced open file count equal to five.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep02.py

Purpose: basic configuration smoke tests for file-manager sweep options at connection open.

Important APIs/types/functions: `test_sweep02` overrides setup hooks to manage connections manually and uses `wiredtiger_open` with `create` plus `file_manager` configs. Constants define a test home `WT_TEST` and table URI but active tests only open connections.

Control flow: five tests open a connection with empty `file_manager=()`, `close_scan_interval=1`, `close_idle_time=1`, `close_handle_minimum=500`, and a combination of scan interval plus idle time.

State and persistence behavior: opening a home with each config validates config parsing and initialization; no table data is created.

Dependencies/integration points: covers connection configuration admission for sweep/file-manager settings. Risks are low; signal is successful connection open without exceptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep03.py

Purpose: verifies `close_idle_time=0` disables idle handle sweeping while still allowing explicit drop cleanup paths to close handles and reclaim cache.

Important APIs/types/functions: `test_sweep03` extends `sweep_util` and `suite_subprocess`; it uses `wait_for_sweep`, `stat.conn.dh_sweep_dead_close`, `cache_bytes_inuse`, `dh_sweeps`, `dropUntilSuccess`, and verbose sweep filtering. Scenarios cover row and VLCS table formats.

Control flow: `test_disable_idle_timeout1` creates 40 tables, waits for two sweeps, and asserts no dead handles were closed. Drop-force and drop tests create a table, fill it, capture cache/close stats, drop with or without `force=true`, wait for sweeps, and compare cache and close counts.

State and persistence behavior: idle handles remain open when idle timeout is disabled. Dropped objects should release cache and handles through drop-specific paths rather than normal idle sweep; disaggregated row mode may close two handles for force drop.

Dependencies/integration points: covers file-manager idle timeout, sweep server stats, forced and normal drop, cache reclamation, and hook-specific expectations. Risks include timing and hook exclusions; signals are zero idle closes, expected close counts for force drop, and reduced cache use after drop.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep04.py

Purpose: intended long stress test for whether data-handle sweep keeps up with a workload that continuously drops/creates transient tables while repeatedly accessing a core set; currently skipped due to `FIXME-WT-13706`.

Important APIs/types/functions: module helper `average_slope` computes average and least-squares slope without numpy. `test_sweep04` uses `suite_random`, `stat.conn.dh_conn_handle_count`, `file_open`, many sessions, `session.drop(..., "force")`, and file-manager sweep config.

Control flow: if enabled, the test would create core and transient tables, open 100 sessions, run a long loop whose first half replaces transient tables while occasionally examining them and whose second half only touches core tables, sample dhandle counts every 100 iterations, then compare slopes and end averages.

State and persistence behavior: transient table churn grows and then should shrink in-memory dhandle state as sweep catches up. The slope analysis is the persistent test signal over time rather than a single stat.

Dependencies/integration points: covers sweep behavior under many sessions and handles, random access, forced drops, and statistical trend analysis. Risks are high runtime and flakiness, reflected by the unconditional skip; current signal is the skip, while `average_slope` remains testable utility logic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep05.py

Purpose: extra-long tests for detecting sessions that have not run session sweep recently, with separate coverage for five-minute and sixty-minute violation counters.

Important APIs/types/functions: `test_sweep05` uses `wttest.extralongtest`, `wiredtiger.stat.conn.no_session_sweep_5min`, `no_session_sweep_60min`, verbose sweep filtering, `time.sleep`, session `reset`, and helper methods `get_stats`, `assert_stats`, `create_table`, and `use_session`.

Control flow: `test_short` creates two tables and two extra sessions, repeatedly uses/resets one session while leaving others idle, sleeps enough to trigger five-minute detections, verifies counters, resets idle sessions, then repeats to confirm counters increment cumulatively. `test_long` keeps sessions swept for 55 minutes, then allows selected sessions to become idle long enough to trigger 5-minute and 60-minute counters.

State and persistence behavior: state is runtime session sweep timestamps and cumulative connection counters, not persisted table data. Table reads create session handle activity; `session.reset` marks sweep progress.

Dependencies/integration points: covers session sweep monitoring, verbose warning output, connection stats, and long wall-clock behavior. Risks are extreme runtime and timing sensitivity; signals are exact cumulative counter values after sleeps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep05.py -->
