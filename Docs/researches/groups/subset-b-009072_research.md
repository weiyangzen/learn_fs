# Research Group: subset-b-009072

This grouped report covers the WiredTiger Python suite files assigned to `subset-b-009072`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_alter01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_alter01.py

Purpose: smoke-tests `WT_SESSION.alter` for file/table metadata options `access_pattern_hint` and `cache_resident` across plain files, simple tables, column groups, indexes, tiered storage, and optional reopen. Important APIs are `session.create`, `session.alter`, `session.open_cursor('metadata:')`, cursor inserts, and `reopen_conn`; the test type is `test_alter01(TieredConfigMixin, WiredTigerTestCase)`.

Control flow builds a matrix from tiered storage, URI shape, create-time hint/cache settings, and reopen mode, creates the main object and optional subobject, writes integer rows, verifies default or explicit metadata, then loops all alter combinations. State and persistence are checked through metadata cursor scans before and after reopen. Dependencies include `helper_tiered` and `wtscenario`. Integration risk is high around default value changes, because defaults are hard-coded as `access_pattern_hint=none` and `cache_resident=false`. Test signals are metadata string assertions and tiered file URI skips.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_alter01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_alter02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_alter02.py

Purpose: verifies altering per-object logging with connection logging enabled/disabled at create and reopen time. It covers files, tables, column groups, indexes, tiered storage scenarios, and table create/alter logging combinations. Key APIs are `wiredtiger_open`, `session.alter`, `session.open_cursor('log:')`, metadata cursor scans, and binary string writes used to distinguish logged versus unlogged records.

Control flow overrides connection/session open to control `log=(enabled=...)`, creates the object with `log=(enabled=true|false)`, writes the first batch, counts expected log cursor appearances, optionally reopens with a different connection log state, alters object/subobject logging, writes a second batch, and verifies expected log record counts. Persistence behavior combines metadata and log files, with log cursor counts doubled because records are returned both as full commit records and operations. Risks include exact log cursor encoding assumptions, binary value matching, and tiered file URI restrictions. Test signals are metadata checks, log count assertions, and expected error-free reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_alter02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_alter03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_alter03.py

Purpose: checks `app_metadata` alteration semantics for table and backing file metadata, including the `exclusive_refreshed` switch. It uses `test_alter03(TieredConfigMixin, WiredTigerTestCase)` with tiered scenarios and direct metadata lookup.

Important APIs are `session.create`, `session.alter`, `open_cursor('metadata:')`, cursor writes, `wiredtiger.WT_NOTFOUND`, `assertRaisesException`, and `reopen_conn`. Control flow creates a table with metadata, writes rows, verifies table and file metadata, performs alters with default exclusive behavior, explicit `exclusive_refreshed=true`, and `exclusive_refreshed=false`, then repeats with an open cursor to assert exclusive refresh failures while non-exclusive metadata-only table updates succeed. State is persisted and checked after connection reopen. Integration points are table/file metadata naming, including tiered file object naming. Risks include stale backing file metadata when non-exclusive alter is used by design. Test signals are exact metadata strings and expected `WiredTigerError` paths with open handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_alter03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_alter04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_alter04.py

Purpose: smoke-tests `WT_SESSION.alter` for `os_cache_max` and `os_cache_dirty_max` metadata settings across files, simple tables, column groups, indexes, tiered storage, create-time defaults, and reopen behavior. The main class combines `TieredConfigMixin` and `WiredTigerTestCase`.

Control flow creates the object with explicit or default cache setting, optionally creates a column group or index subobject, inserts rows, checks metadata, then alters to `1M` and `100K`, reopening when scenario demands. Important APIs are `session.create`, `session.alter`, metadata cursor iteration, and cursor writes. Persistence is represented by metadata propagation to file entries and survival across reopen. Dependencies include `helper_tiered` and scenario generation. Risks are default sensitivity (`setting=0` is hard-coded) and special handling of subobjects, where the test alters both top-level and sub-URI metadata. Test signals are metadata substring assertions and tiered file skip behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_alter04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_alter05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_alter05.py

Purpose: verifies that altering a file after timestamped modifications succeeds, triggers checkpoint accounting, and fails correctly while a cursor remains open. It focuses on file URI behavior with statistics enabled and tiered storage configuration.

Important APIs are `conn_config`, `session.create`, `conn.set_timestamp`, transaction begin/commit with commit timestamps, `session.alter`, statistics cursor access to `wiredtiger.stat.conn.session_table_alter_trigger_checkpoint`, and metadata lookup. Control flow creates a logged file, pins timestamps, writes timestamped data, advances stable timestamp, alters logging off, checks metadata, and asserts the alter-triggered checkpoint statistic increments. It then writes through an open cursor and asserts altering back to logged fails, while checkpoint count still advances. State/persistence behavior involves stable timestamp movement, metadata durability, and checkpoint side effects. Risks include file-only assumptions and exact statistic semantics. Test signals are metadata checks, statistic increments, and `WiredTigerError` on open-handle alter.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_alter05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_app_thread_evict01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_app_thread_evict01.py

Purpose: stresses eviction so an application thread is pulled into eviction and refreshes an eviction snapshot. The class uses a 100MB cache, one eviction thread, low eviction trigger/target percentages, and connection statistics.

Key APIs are table creation, large cursor inserts, transaction begin/commit, `statistics:` cursor access, and `wiredtiger.stat.conn.application_evict_snapshot_refreshed`. Control flow creates a row-store table, repeatedly inserts about 40MB of small values, then two 20MB updates in one transaction to exceed eviction triggers; it polls the statistic up to 20 attempts because the app thread races internal eviction. State is in cache residency and statistics rather than durable content. Dependencies are `wttest`, `wiredtiger.stat`, and `make_scenarios`. Risks include timing/probabilistic behavior, memory pressure, and platform speed variability. The test signal is a positive application eviction statistic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_app_thread_evict01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_assert06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_assert06.py

Purpose: validates timestamp usage assertions for ordered durable timestamps and write timestamp consistency. It skips diagnostic builds and runs row and variable-length column formats.

Important APIs are `SimpleDataSet`, transaction timestamp methods (`prepare_transaction`, `timestamp_transaction`, commit/rollback), `session.alter(write_timestamp_usage=ordered)`, `assert=(write_timestamp=on)`, and subprocess stdout filtering. Control flow first writes mixed timestamp/no-timestamp histories, alters the object to ordered usage after moving oldest timestamp, then verifies a later untimestamped update fails. The second test creates with assertions enabled and checks per-key ordering, inconsistent timestamp use, commit timestamp placement before/mid/end of a transaction, prepared durable timestamps, and rollback after prepare. State is MVCC timestamp history and assertion metadata. Risks include exact diagnostic/non-diagnostic behavior and message matching. Test signals are expected `WiredTigerError` messages and preserved visible values after failed commits.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_assert06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_assert07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_assert07.py

Purpose: regression coverage for resolved-update assertions when reserved updates appear at different positions in an update chain. It runs string-row and column key formats and uses prepared timestamped transactions.

Important APIs are cursor `reserve`, repeated cursor assignments to the same key, transaction prepare/commit/durable timestamps, and scenario generation. Control flow creates one file, writes an initial value, then exercises reserved updates at the start, end, between updates, and multiple times in the same transaction, always committing with increasing timestamps. State behavior is entirely in the update chain for a single key; persistence is less important than avoiding assertion failure during update resolution. Dependencies include `suite_subprocess` for failure isolation and `wttest`. Risks include lack of explicit final-value assertions, meaning the signal is mostly “no assertion/no crash.” Test signal is successful completion across reserve/update ordering permutations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_assert07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_autoclose.py -->
# sources/storage-engines/wiredtiger/test/suite/test_autoclose.py

Purpose: verifies Python/SWIG handle autoclose behavior for cursors, sessions, and connections. It ensures use-after-close produces catchable errors and subordinate handles become invalid when parent handles close.

Important APIs are `session.create`, cursor insert/next/compare/close, `session.close`, `close_conn`, `truncate`, and assertion helpers matching exception messages. Control flow creates a table, opens cursors, closes cursor/session/connection in different orders, and asserts later operations fail with `wt_cursor.* is None`, `wt_session.* is None`, or `connection is closed`. It also validates two special cases: `truncate` allows null cursor arguments, while `Cursor.compare` rejects closed or null cursor arguments. State is handle lifetime rather than durable data. Risks include platform-dependent exception class (`TypeError` on Darwin, `RuntimeError` elsewhere) and SWIG message changes. Test signals are precise exception type/message matches and successful null-truncate behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_autoclose.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup01.py

Purpose: foundational backup cursor and `wt backup` command coverage for full database backup, selective object backup, cursor reset, and checkpoint deletion while hot backup is active. It extends `wtbackup.backup_base`.

Key APIs include `session.open_cursor('backup:')`, `runWt(['backup'])`, `runWt(['list'])`, `compare_backups`, `confirmPathDoesNotExist`, `session.checkpoint`, and named checkpoint cursors. Control flow populates files and simple/complex tables, backs up the full database and selected subsets, validates list equality and content, iterates backup cursor twice after `reset`, and asserts named checkpoints pinned by an open backup cursor cannot be dropped. State behavior spans copied files, metadata, checkpoints, and backup cursor pinning. Risks include object index lists referencing eight entries although six are visible in `objs`, filesystem cleanup, and timing around checkpoint timestamps. Test signals are content comparisons, missing-object assertions, WT_NOTFOUND, and expected checkpoint-drop errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup02.py

Purpose: stress-tests concurrent checkpoints, backups, and insert/update workload. It uses background thread helpers to run for 10 seconds by default or 60 seconds in long-test mode.

Important APIs and types are `threading.Event`, `queue.Queue`, `wtthread.checkpoint_thread`, `backup_thread`, `op_thread`, and WiredTiger connection/session table creation. Control flow creates three tables, starts checkpoint and backup threads, queues insert work, starts operation worker threads, then repeatedly queues update work with changing values until time expires. The `finally` block joins the queue, signals all threads done, and joins workers. State behavior includes concurrent data mutations, checkpoint generation, and backup directory churn. Dependencies are thread helper classes that own most operation semantics. Risks are concurrency timing, queue draining on exceptions, and backup/checkpoint races. Test signal is successful completion without exceptions or deadlock.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup05.py

Purpose: simulates MongoDB-like `fsyncLock` manual backup: checkpoint, open backup cursor to pin state, copy the live home directory, and recover the copy. It verifies metadata is flushed enough for manual copies.

Important APIs are `session.checkpoint`, `session.open_cursor('backup:')`, `helper.copy_wiredtiger_home`, schema `drop/create`, `verifyUntilSuccess`, and `expectedStdoutPattern('recreating metadata')`. Control flow creates an empty table, reopens, then repeatedly inserts into a data table; every fifth iteration it checkpoints, opens a backup cursor, copies the home with aligned or unaligned copy, verifies schema operations fail during backup cursor lifetime, closes the cursor, confirms schema operations resume, and verifies the copied database. State behavior covers live filesystem copies, metadata recovery, and backup cursor schema protection. Risks include platform-specific unaligned copy support, Windows alignment fallback, and recovery output matching. Test signals are schema-operation errors during backup and successful verification after opening copied home.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup06.py

Purpose: verifies backup cursor opening does not unnecessarily open data handles, while backup schema protection still prevents dropping backed-up objects. It also checks backup cursor reset iteration.

Important APIs are `resource.getrlimit/setrlimit`, `populate_many`, connection reopen, `statistics:` cursor on `stat.conn.dh_conn_handle_count`, `session.open_cursor('backup:')`, schema `create/drop`, and `WT_NOTFOUND`. Control flow populates many file/table objects, reopens to clear handles, compares open handle count before and after opening backup, then separately opens a backup cursor and asserts existing objects cannot be dropped while creating a new schema object is allowed. State behavior is handle-cache and schema protection state, not copied backup content. Dependencies are `backup_base`, datasets, statistics, and Unix resource limits; Windows skips handle-limit test. Risks include handle-count statistic drift and platform limits. Test signals are equal handle counts, expected drop failures, and reset count doubling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup07.py

Purpose: tests full backup recovery when a new table is created while a backup cursor is open and later log records mention that new table. It ensures recovery tolerates log records for files absent from the backup file list.

Important APIs are `backup_base.add_data`, `session.open_cursor('backup:')`, `session.log_flush`, `take_full_backup`, `take_log_backup`, and `wiredtiger_open` on the backup directory. Control flow writes until log file 2 exists, opens a full backup cursor, creates and populates a new table, flushes logs, copies the full backup list, asserts the new table is not included, then copies later logs via duplicate log backup and recovers the backup. State behavior depends on log file rotation, file-id references, and backup cursor file list snapshotting. Risks include log filename assumptions and filesystem timing. Test signal is successful recovery of the backup directory without including the newly created table file.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup08.py

Purpose: verifies checkpoint timestamp metadata survives live backup and is used as the backup recovery timestamp. It models MongoDB collection/oplog tables with logged oplog and non-logged collections.

Important APIs are timestamped transactions, `conn.set_timestamp`, `session.checkpoint(use_timestamp=...)`, `conn.query_timestamp('get=last_checkpoint')`, backup cursor iteration, file copy, and backup `query_timestamp('get=recovery')`. Control flow inserts timestamped data into three collection-like tables, advances stable timestamp per table, checkpoints with `use_timestamp` false/default/true scenarios, validates last checkpoint timestamp, copies files listed by a backup cursor, opens the backup, and verifies recovery timestamp equals the expected checkpoint timestamp. State behavior is stable timestamp persistence in backup metadata. Risks include exact use-stable semantics and manual file copy completeness. Test signals are timestamp equality assertions before and after recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup09.py

Purpose: verifies opening a backup cursor forces a log file switch and that recovery includes only the intended operations unless all log files are copied. It runs checkpoint, no-checkpoint, and all-log-file scenarios.

Important APIs are `session.open_cursor('backup:')`, directory log file counting, `helper.copy_wiredtiger_home`, backup cursor file copy, `wiredtiger_open`, and cursor iteration after restore. Control flow writes 10 records, optionally checkpoints, writes another 10, asserts one log file exists, opens backup cursor and asserts two log files exist, writes a final 10, then copies either only cursor-returned files or all home files. Restore validation counts records up to either backup start or final data. State behavior is log rotation boundary and recovery from selected logs. Risks include platform skip for all-log copy on Windows and assumptions about `WiredTiger.backup` versus turtle output. Test signals are log file counts and restored record cardinality.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup10.py

Purpose: tests duplicate backup cursor behavior for log-only backup after a full backup cursor, under log removal on/off scenarios. It also validates duplicate cursor error rules.

Important APIs are `session.open_cursor('backup:')`, duplicate `open_cursor(None, bkup_c, 'target=("log:")')` via helper methods, `take_full_backup`, `take_log_backup`, `session.log_flush`, and `wiredtiger_open`. Control flow writes until log file 2, opens primary backup cursor, writes/flushed data that lands in the switched log, copies full backup files, opens a duplicate log cursor and checks duplicate logs are a superset with exactly one additional log, then asserts multiple duplicates, duplicate-of-duplicate, and missing log target fail. State behavior is log file lifecycle and one-duplicate-per-primary state. Risks include hard-coded log filenames and exact error messages. Test signal is set membership on logs plus expected `WiredTigerError` messages and successful recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup11.py

Purpose: exercises incremental backup cursor configuration and error validation, including legal log-target duplicate use with an incremental primary and many invalid combinations. It extends `backup_base`.

Important APIs are `session.open_cursor('backup:', config='incremental=(...)')`, duplicate cursor creation, `take_full_backup`, `take_log_backup`, `add_data`, and backup directory recovery. Control flow performs an initial incremental full backup with `this_id=ID1`, copies logs through a duplicate, then tests invalid primary/duplicate configurations: file on primary, incremental duplicate without incremental primary, consolidation on duplicate, multiple duplicate cursors, file target misuse, mixed incremental/log target, IDs on duplicate, force stop on duplicate, missing known source ID, unknown source ID, reserved WiredTiger namespace IDs, illegal grouping characters, and same source/target IDs. State behavior is incremental ID metadata and cursor-open state. Risks are brittle regex messages and sequencing of ID history. Test signals are expected errors and final backup recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup12.py

Purpose: validates block-based incremental backup through a full backup, later changes, table drop, and cleanup of stale files in the backup directory. It uses large keys/values to dirty multiple blocks.

Important APIs are table create/drop, `add_data`, `take_full_backup`, `take_log_backup`, `take_incr_backup`, manual `os.remove`, and `wiredtiger_open` recovery. Control flow creates three tables, writes data, opens an incremental primary with granularity and `this_id=ID1`, performs a full copy plus log backup, closes the primary, writes more data to two tables, drops one table, runs incremental backup ID1 to ID2, removes files from the backup directory that are no longer in the current backup set, and opens the backup. State behavior spans incremental block metadata, log backup, and deletion propagation. Risks include file-set bookkeeping and removing required files if helper semantics change. Test signal is successful recovery after applying incremental changes and removals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup13.py

Purpose: tests block incremental backup plus `force_stop` cleanup under different session isolation levels. It also verifies old incremental metadata cannot be reused after force stop, crash restart, or normal restart.

Important APIs are scenario `session_config`, `add_data`, `take_full_backup`, `take_incr_backup`, `wiredtiger_open`, `session.open_cursor('backup:', 'incremental=(force_stop=true)')`, and `simulate_crash_restart`. Control flow creates a table, writes data or expects errors for read-committed/read-uncommitted isolation, performs initial incremental full backup and later incremental backup, removes stale files, recovers the backup, force-stops incremental state, then asserts a backup with old `src_id=ID1` fails after force stop, simulated crash, and reopen. State behavior centers on persisted incremental ID metadata and its reset semantics. Risks include isolation-specific unsupported transaction behavior and crash simulation effects. Test signals are expected errors and backup recovery success.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup14.py

Purpose: broad block incremental backup workflow test covering add/update, remove-all, drop/recreate table, new table introduction, and bulk logged versus non-logged table inserts. It validates incremental backup directories against full backup directories after each phase.

Important APIs are `backup_base.setup_directories`, `add_data`, `take_full_backup`, `take_incr_backup`, `compare_backups`, table `drop/create`, `runWt list`, bulk cursor configuration, and manual cursor `remove`. Control flow switches home to `WT_BLOCK`, initializes full/incremental homes, seeds the main table, alternates full and incremental backups, removes all records and validates, drops `table:main` and creates `table:extra`, recreates main with new content, then bulk inserts into logged and non-logged tables and compares backups. State behavior includes block incremental metadata across deletes, schema churn, and logging modes. Risks include shared mutable class fields, filesystem directory reuse, and shell `grep` use. Test signals are backup content comparisons and absence of dropped table in listings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup15.py

Purpose: stresses block incremental backup with large data followed by hotspot updates to a single key, alternating the order of full and incremental backups to detect interference.

Important APIs are custom `add_complex_data`, `take_full_backup`, `take_incr_backup`, `compare_backups`, `setup_directories`, checkpoints, and cursor writes. Control flow creates `WT_BLOCK` home, writes an initial large dataset, takes an initial full backup into the incremental home, then for several iterations writes either new keys or repeated updates to the saved key, checkpoints, alternates full-before-incremental versus incremental-before-full, compares backup contents, and resets directories. State behavior is dirty block tracking for both broad inserts and concentrated repeated updates. Risks include runtime cost (`nops=100000`), class-level counters affecting backup IDs, and sensitivity to checkpoint behavior. Test signals are repeated full/incremental content equality checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup16.py

Purpose: verifies incremental backup range cursors return only files with changed or required content and do not copy unnecessary files. It distinguishes old unchanged files, old changed files, new empty files, and new populated files.

Important APIs are primary incremental backup cursor, duplicate per-file incremental cursors, `get_keys()` range/length results, checkpoints, and helper `add_data`. Control flow creates initial tables, writes data to two, checkpoints and opens/closes an initial incremental full backup (`ID0`), creates new tables, writes to selected old/new tables, checkpoints, and calls `verify_incr_backup` with expected file lists across three generations. State behavior is incremental file/block metadata and whole-file inclusion for new files without checkpoint information. Risks include exact expected files when checkpoint metadata writes change. Test signals are per-file inclusion assertions, nonzero copy lengths, and exact expected file counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup17.py

Purpose: tests incremental backup consolidation, ensuring adjacent dirty ranges are collapsed when `consolidate=true` and not collapsed otherwise. It compares range lengths and total byte coverage.

Important APIs are incremental full backup, `take_incr_backup(..., consolidate)`, helper `add_data`, and assertions on returned file length lists. Control flow creates two tables, writes initial data to both, opens an incremental primary with 100K granularity, takes a full backup, then writes identical changes to table one and takes an unconsolidated incremental backup; it writes similar changes to table two and takes a consolidated backup. State behavior is dirty block range tracking and consolidation in incremental metadata. Risks include eviction/checkpoint internal operations adding small dirty ranges, so total length comparison uses tolerance. Test signals are presence/absence of ranges larger than granularity, fewer consolidated ranges, and approximate equal total length.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup18.py

Purpose: tests the `backup:query_id` cursor API for listing incremental backup IDs and verifies related statistics. It covers unconfigured, active-backup, reopen, force-stop, and crash-restart states.

Important APIs are `session.open_cursor('backup:query_id')`, incremental backup primary cursors, `statistics:` cursor for `backup_cursor_open`, `backup_incremental`, `backup_granularity`, `simulate_crash_restart`, and sorted ID comparison. Control flow asserts query fails before configuration, opens an incremental primary and checks stats/default granularity, asserts query cannot be used as a duplicate or while backup cursor is open, closes and checks IDs, advances IDs through ID2/ID3, reopens and confirms persistence, force-stops and confirms query becomes unconfigured, configures again, then force-stops and simulates crash to ensure state is cleared. Risks include exact stats and error messages. Test signals are ID list equality, stat values, and expected errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup19.py

Purpose: focused block incremental backup test where later incremental backup is driven by source identifier state maintained by the helper. It resembles a shorter version of the complex-data/hotspot path.

Important APIs are custom `add_complex_data`, `take_full_backup`, `take_incr_backup`, `compare_backups`, checkpoints, and directory setup. Control flow switches home to `WT_BLOCK`, creates `table:main`, initializes full and incremental backup directories, writes initial data, takes a full backup into incremental home, checkpoints, writes more complex data, checkpoints again, takes a separate full backup, then takes an incremental backup and compares. State behavior is incremental block tracking across one source-to-current generation. Risks include reliance on `backup_base` defaults for source-only incremental ID handling and class-level counters. Test signal is full/incremental backup equivalence for the main table.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup20.py

Purpose: regression test for WT-7027, ensuring incremental backup `force_stop` works without a checkpoint and does not assert when the session uses snapshot isolation. It runs default, read-committed, read-uncommitted, and snapshot session configurations.

Important APIs are scenario `session_config`, table creation, opening an incremental primary backup cursor, opening a `force_stop=true` backup cursor, and explicit session/connection close. Control flow creates a table, opens/closes a primary incremental backup with granularity and `this_id=ID1`, then immediately opens/closes a force-stop cursor without taking a checkpoint. State behavior is incremental metadata setup and teardown without checkpoint persistence. Dependencies are `suite_subprocess` for assertion isolation. Risks are narrow: the test signals only absence of crash/assertion, not data content. Test signal is successful close under all isolation scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup21.py

Purpose: tests create/drop operations racing with full backup cursors. It validates snapshot semantics: newly created tables after cursor open are not in backup, while tables dropped after cursor open remain listed.

Important APIs are `op_thread`, `queue.Queue`, `threading.Event`, `session.open_cursor('backup:')`, `take_full_backup`, and helper `add_data`. Control flow creates and populates a base table, starts an operation thread, then for 50 iterations opens a backup cursor, queues a create or drop operation, copies full backup files, and checks file list membership. At midpoint it drains creates before switching to drops. State behavior is schema metadata as seen by a backup cursor versus concurrent mutations. Risks include queue timing, file naming assumptions, and backup directory reuse. Test signals are file-list assertions for new/dropped tables and clean thread shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup22.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup22.py

Purpose: tests interaction between import and incremental backup, especially importing a dropped table and then expecting an incremental backup into an empty directory to copy the full file. It covers metadata import and repair import, with and without checkpoint.

Important APIs are metadata cursor reads, `session.drop(remove_files=false)`, `session.create(import=...)`, `take_full_backup`, `take_incr_backup`, `compare_backups`, and scenario generation. Control flow creates/populates a table, checkpoints, captures table and file metadata, opens an incremental full backup (`ID1`), drops the table without removing files, imports it using either original metadata or repair mode, optionally checkpoints, then takes incremental backup ID1 to ID2 into an empty directory and compares against the full backup. State behavior includes import metadata, checkpoint state, and incremental changed-file detection. Risks include exact import config string construction and whole-file copy expectations. Test signal is backup equivalence.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup22.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup23.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup23.py

Purpose: verifies opening a backup restore with `verify_metadata=true` fails with a clear error, and that the same backup remains usable afterward with the correct configuration.

Important APIs are transaction writes, checkpoint, `take_full_backup`, `wiredtiger_open`, `assertRaisesWithMessage`, and cursor materialization into lists. Control flow creates a file, writes and checkpoints initial data, writes additional logged data after the checkpoint, captures original cursor contents, takes a full backup, closes the source, asserts opening the backup with metadata verification enabled raises “restoring a backup is incompatible,” then opens with normal config and verifies backed-up data equals original data. State behavior is backup recovery plus metadata verification mode gating. Risks include config-specific behavior and exact error message. Test signals are expected open failure and data equality after subsequent successful open.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup23.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup24.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup24.py

Purpose: tests recovering a selective backup containing some logged and non-logged tables while additional logged/non-logged tables are created after backup cursor open. It validates partial restore metadata cleanup.

Important APIs are custom `add_data/check_data`, `session.open_cursor('backup:')`, `take_selective_backup`, `take_log_backup`, `session.log_flush`, `wiredtiger_open(... backup_restore_target=...)`, metadata cursor searches, and `debug_mode=(table_logging=true)`. Control flow creates logged and non-logged tables, writes until log 2, checkpoints, writes post-checkpoint data, opens a backup cursor, creates new logged/non-logged tables, flushes logs, takes a selective backup excluding one non-logged table, copies logs, restores with target URIs, and asserts excluded/new non-logged tables are absent from files and metadata while included tables are readable. State behavior spans selective file copying, logs, and partial recovery metadata pruning. Risks include log filename timing and target list formatting. Test signals are file absence, metadata WT_NOTFOUND, and data checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup24.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup25.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup25.py

Purpose: verifies commit-level durability when the source crashes while a backup cursor is open. It checks that recovery from `WiredTiger.backup` still replays logged changes made after the backup cursor opened, even when later checkpoints are discarded.

Important APIs are `add_data`, `session.checkpoint`, `session.open_cursor('backup:')`, `session.log_flush`, `copy_wiredtiger_home`, `wiredtiger_open`, and expected stdout pattern for both turtle and backup files. Control flow writes until log file 2, checkpoints, writes pre-backup data, opens backup cursor, writes and checkpoints two backup-era keys, writes a third uncheckpointed key, flushes logs, copies the live home to a new directory while backup cursor remains open, closes cursor, opens the copy, and verifies all backup-era keys are present. State behavior is log durability versus backup checkpoint pinning. Risks include filesystem copy fidelity and log flush timing. Test signals are recovered key/value assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup25.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup26.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup26.py

Purpose: scalability and correctness test for selective backup partial recovery with many tables and reversed target lists. It uses 500 tables normally and 10000 in long-test mode.

Important APIs are `SimpleDataSet.populate/check_cursor`, `take_selective_backup`, `wiredtiger_open(... backup_restore_target=...)`, time measurement, and scenario generation over percentage excluded and target-order reversal. Control flow creates many tables, splits them into removed and retained sets based on percentage, checkpoints, copies a selective backup excluding removed files, opens the backup with target URIs in normal or reverse order, asserts removed tables cannot be opened, and checks all retained tables. State behavior is partial restore metadata scaling and table/file schema correctness. Risks include a typo in scenario label only, high runtime in long mode, and large target list config strings. Test signals are expected open failures for removed URIs and dataset validation for retained URIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup26.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup27.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup27.py

Purpose: verifies selective backup with history store contents clears history entries for tables excluded from partial restore while preserving history for restored tables.

Important APIs are timestamped transactions, `conn.set_timestamp`, checkpoint, `take_selective_backup`, `wiredtiger_open(... backup_restore_target=...)`, read timestamp transactions, cursor search, and creating a missing table after restore. Control flow creates two tables, writes values at timestamps 1 and 5, advances stable timestamp to 10 and checkpoints to retain history store data, selectively backs up excluding one table file, restores only the included URI, validates older and newer timestamp reads for included table, asserts excluded table open fails, recreates the excluded table, then verifies no historical records are visible at timestamps 1 or 10. State behavior is history store filtering during partial recovery. Risks include timestamp visibility semantics and omitted file metadata. Test signals are timestamped value checks and WT_NOTFOUND on recreated excluded table history.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup27.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup28.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup28.py

Purpose: verifies partial backup restore target URI validation across file, simple table, column group, and index scenarios. Only table URIs are supported in `backup_restore_target`.

Important APIs are `session.create` for tables, column groups, and indexes; `take_selective_backup`; `wiredtiger_open(... backup_restore_target=...)`; and message-based error assertions. Control flow creates a file or table with column group/index structures, checkpoints for table subobjects, takes a full backup, then opens partial restore with scenario target list. If the target list begins with `table:table0`, restore should succeed and the table cursor should open; otherwise restore should fail with a message saying partial backup restore only supports table formats. State behavior is metadata schema type validation during recovery. Risks include scenario labels swapping `table-cg`/`table-index` target types and exact error message regex. Test signals are successful cursor open for table target and expected `WiredTigerError` for file/index/colgroup targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup28.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup29.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup29.py

Purpose: regression test for incremental backup bitmaps after uncached data handles are reopened by connection restart or file-manager sweep. It ensures checkpoint plus incremental metadata interactions do not lose required block-mod information.

Important APIs are statistics cursor reads, metadata cursor parsing of `blocks=<hex>`, initial incremental cursor with `granularity=4k`, `reopen_conn`, file-manager close configuration, repeated checkpoints, and open-file statistics. Control flow creates two tables, writes initial rows, checkpoints, opens/closes incremental full backup to enable bitmap tracking, writes many rows, checkpoints, stores block bitmap metadata, then either reopens the connection or waits for dhandle sweep by updating an active table until open-file count drops. It reopens both target tables, modifies one then the other with checkpoints, and parses block metadata. State behavior is persisted incremental bitmap state across dhandle lifecycle. Risks include currently commented-out bitmap comparison, timing in sweep wait, and exact open-file count. Test signal is successful validation path and statistics expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup29.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup30.py -->
# sources/storage-engines/wiredtiger/test/suite/test_backup30.py

Purpose: tests `conn.query_timestamp('get=backup_checkpoint')` while backup cursors are opened and closed. It confirms the backup checkpoint timestamp is pinned to the cursor’s checkpoint even if later checkpoints advance stable timestamp.

Important APIs are timestamped writes, `conn.set_timestamp`, `session.checkpoint`, `conn.query_timestamp`, and backup cursor open/close. Control flow creates a table, writes data at timestamps 1 and 5, sets stable timestamp to 10 and checkpoints, asserts no open backup cursor reports timestamp 0, opens a backup cursor and asserts backup checkpoint equals stable 10, writes later timestamped data, advances stable to 20 and checkpoints while cursor remains open, verifies the query still returns 10, then closes/reopens backup cursor and expects 20. State behavior is backup cursor checkpoint pinning and timestamp query reset on close. Risks are exact timestamp string formatting and stable timestamp assumptions. Test signals are timestamp equality assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_backup30.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_base01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_base01.py

Purpose: basic API smoke test for table create, invalid config handling, missing-key search, insert, and readback across column-store record-number keys and row-store string keys.

Important APIs are `session.create`, `open_cursor`, cursor `set_key/set_value/insert/search/get_value`, `dropUntilSuccess`, and expected stderr matching. Control flow runs scenario key formats, creates tables with page/allocation settings, checks malformed config raises `WiredTigerError` containing invalid argument and stderr “unknown configuration key,” searches for a nonexistent key and expects `WT_NOTFOUND`, then inserts one value and reads it back. State behavior is simple table persistence within one connection; no reopen is used. Dependencies are `wttest`, `wiredtiger`, and `make_scenarios`. Risks include a missing `inscursor.close()` call because the method is referenced without invocation, though test lifetime cleanup masks it. Test signals are expected error capture, WT_NOTFOUND, and value equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_base01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_base02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_base02.py

Purpose: spot-checks WiredTiger configuration parsing for normal config strings and JSON config strings on file and table URIs. It is tagged `config_api`.

Important APIs are `json.dumps`, `session.create`, `session.drop`, and scenario generation for `file:` versus `table:`. Control flow builds combinations of size/page options and column declarations, including extra commas, quoted formats, named columns, and path-like column names, then creates and drops each object. A second test creates and drops JSON-formatted configs with columns, key/value formats, and column groups. State behavior is transient schema creation and cleanup; there is no data persistence validation. Dependencies are Python JSON formatting and WiredTiger config parser compatibility. Risks include broad parser acceptance without metadata verification and inherited `extra_config` allowing subclasses to extend behavior. Test signal is successful create/drop for every config combination.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_base02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_base03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_base03.py

Purpose: basic cursor iteration and type-format test for four key/value combinations: string/string, string/int, int/string, and int/int. It validates ordering and value conversion through the Python cursor API.

Important APIs are `session.create`, `session.open_cursor`, cursor item assignment, `reset`, iteration over `(key, value)`, and a helper `session_create` that prints full context on create failure. Control flow creates a table per format, inserts 10 entries, resets the cursor, iterates in key order, and asserts keys/values match expected sequence and entry count. State behavior is in-memory and on-disk table content during one test method; no reopen or checkpoint is forced. Dependencies are only `wttest`. Integration point is the Python binding’s mapping of WiredTiger format strings to Python values. Risks include tests assuming lexicographic order for `key0` to `key9`, which holds for 10 entries. Test signals are exact key/value and count assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_base03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_base04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_base04.py

Purpose: tests correctness when tables become empty, both without and with forced reconciliation through connection reopen. It covers create, search missing key, insert, delete, and drop.

Important APIs are `session.create`, `open_cursor`, cursor assignment/search/remove, `reopen_conn`, `dropUntilSuccess`, and `wiredtiger.WT_NOTFOUND`. Control flow creates a string/string table, checks missing-key search, then for reconciliation modes inserts a key, verifies it exists, optionally reopens after insert, removes it, optionally reopens after remove, and verifies it is gone before dropping. State behavior specifically targets reconciliation of empty trees and deleted content after reopen. Dependencies are `wttest` and `wiredtiger`. Risks include a likely typo in `test_insert_delete`, where the loop variable `reconcile` is not assigned to `self.reconcile`, so the reopen path may not run there. Test signals are search return codes before and after insert/remove.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_base04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_base05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_base05.py

Purpose: validates storage and retrieval of large mixed strings, UTF/non-ASCII strings, and Python unicode/string conversions through `key_format=S,value_format=S`. It stresses cursor ordering and exact byte/string round trips.

Important APIs are `session.create`, cursor item assignment, cursor `search/get_key/get_value/reset`, iteration, and helper `mixed_string`. Control flow constructs repeatable strings from English text excerpts and non-Latin unicode strings, inserts 1000 mixed key/value pairs, spot-checks search for selected keys, then iterates all records, decodes the numeric suffix, and verifies each key/value pair. Two additional tests insert and read the non-English list either as original strings or after `str()` conversion. State behavior is table content with large variable-length strings. Risks include Python version string/unicode behavior, embedded non-ASCII handling, and very long keys affecting ordering. Test signals are exact search and iteration equality plus complete coverage of the inserted numeric set.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_base05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_baseconfig.py -->
# sources/storage-engines/wiredtiger/test/suite/test_baseconfig.py

Purpose: tests `WiredTiger.basecfg` handling, specifically that invalid base configuration causes open failure unless `config_base=false` is supplied.

Important APIs are `wiredtiger_open`, filesystem `os.mkdir`, `databaseCorrupted`, direct append to `WiredTiger.basecfg`, and `assertRaisesWithMessage`. Control flow creates a separate home `A`, opens it with `create`, marks it as corrupted for test harness expectations, appends invalid text `foo!` to the base config file, closes, then asserts reopening normally fails with an unknown configuration key. It finally opens with `create,config_base=false`, proving base config can be ignored. State behavior is direct persistent file mutation outside WiredTiger APIs. Dependencies are the test harness corruption marker and filesystem path layout. Risks include relying on file name and parser error text. Test signals are basecfg existence, expected open error, and successful open with `config_base=false`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_baseconfig.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug003.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug003.py

Purpose: regression test confirming a bulk-load cursor can be opened after a checkpoint, including named and unnamed checkpoint scenarios, for file and table objects.

Important APIs are `session.create`, `session.checkpoint`, `session.open_cursor(..., "bulk")`, and scenario generation. Control flow creates either `file:data` or `table:data`, performs either a default checkpoint or named checkpoint `ckpt`, then opens a bulk cursor on the object. There are no inserts through the bulk cursor; the signal is that checkpoint state does not prevent bulk cursor creation. State behavior is checkpoint metadata and object state before initial bulk load. Dependencies are minimal (`wttest`, `make_scenarios`). Risks include narrow assertion surface: it detects open failures but not correctness of subsequent bulk inserts. Test signal is successful bulk cursor open after checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug003.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug004.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug004.py

Purpose: regression test for overflow keys/values when deleted during reconciliation without being instantiated, ensuring older snapshot readers still see correct versions. It targets btree file-layer behavior with small page sizes.

Important APIs are `simple_key/simple_value`, `session.create` with tiny allocation/leaf pages, cursor writes, `verifyUntilSuccess`, `reopen_conn`, separate session transaction, range `truncate`, checkpoint, and snapshot cursor iteration. Control flow writes large overflow keys/values, verifies before and after reopen, starts a long-running transaction in another session, truncates a range in the main session without instantiating keys, checkpoints to free overflow blocks, then reads through the snapshot transaction and asserts original keys/values remain visible. State behavior is MVCC snapshot visibility plus overflow block lifecycle. Risks include truncate range bounds and key construction differences for row versus column formats. Test signals are exact key/value equality under the old snapshot.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug004.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug005.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug005.py

Purpose: regression test that `verify` succeeds when a file has additional trailing bytes after the last checkpoint. It targets file-level btree verification.

Important APIs are `session.create`, cursor inserts, `verifyUntilSuccess`, `reopen_conn`, and direct filesystem append. Control flow creates `file:test_bug005`, writes 999 string key/value pairs, verifies in-memory state, reopens to force data to disk, verifies again, appends literal random data to the underlying file, and verifies once more. State behavior is persistent file contents, including tolerated bytes after the checkpointed extent. Dependencies are `simple_key/simple_value` and harness retry helpers. Risks include opening `test_bug005` directly assumes the file URI maps to that relative filename, and append mode may behave differently across platforms. Test signal is successful verification after direct trailing-data mutation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug005.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug006.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug006.py

Purpose: regression test that destructive or exclusive session APIs fail while a cursor is open and succeed after it closes. It covers file and table URIs, skipping tiered storage negative API behavior.

Important APIs are `session.create`, cursor writes, `session.drop`, `session.salvage`, `session.verify`, `salvageUntilSuccess`, `session.truncate`, `verifyUntilSuccess`, and `dropUntilSuccess`. Control flow creates and populates the object, keeps the cursor open, asserts drop/salvage/verify all raise `WiredTigerError`, closes the cursor, then salvages, truncates all content, verifies, and drops successfully. State behavior is handle exclusivity and post-salvage/truncate file state. Dependencies are `simple_key/simple_value` and tiered hook detection. Risks include broad exception assertions without message checks and skip behavior tied to hook names. Test signals are expected failures with open cursor and successful operations after close.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug006.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug007.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug007.py

Purpose: regression test for forced salvage on a file with an invalid header. It confirms normal salvage fails and `force` salvage succeeds.

Important APIs are `session.create`, `session.open_cursor`, direct file overwrite, `session.salvage`, and `assertRaisesWithMessage`. Control flow creates a file object, opens/closes a cursor to ensure the file exists, overwrites the underlying file with repeated random text, asserts plain salvage fails with a `WT_SESSION.salvage` error, then calls salvage with `"force"` and expects success. State behavior is direct corruption of the persistent file followed by recovery/salvage. Dependencies are just `wttest` and `wiredtiger`. Risks include filename mapping assumptions and not verifying resulting contents after forced salvage. Test signals are the expected normal-salvage failure and absence of error from forced salvage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug007.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug008.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug008.py

Purpose: regression suite for cursor `search` and `search_near` around empty files, end-of-table, deleted duplicate column-store runs, and invisible insert-list updates. It covers row-store strings and variable-length column store.

Important APIs are `SimpleDataSet`, cursor `set_key/search/search_near/get_key/get_value/remove`, `reopen_conn`, transactions, and separate sessions for visibility isolation. Control flow checks empty-table searches fail, end-of-table searches return correct exact or nearest records, variable-column duplicate runs with deleted boundaries return nearest visible duplicates, and two invisible-update scenarios where another session should not see uncommitted updates/inserts but `search_near` should fall back to the correct visible neighbor. State behavior is on-page records after reopen, insert lists, transaction visibility, deleted records, and column-store duplicate compression. Risks include implementation-specific bias noted in comments and no explicit rollback for open transactions. Test signals are precise return codes (`0`, `WT_NOTFOUND`, `1`, `-1`) and key/value assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug008.py -->
