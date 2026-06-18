# subset-b-009089 Research

Grouped research for `subset-b-009089`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep06.py

## Purpose
`test_sweep06.py` is a WiredTiger sweep-server regression test. It checks that table data handles are not incorrectly marked expired or closed while their underlying file data handles are active under heavy concurrent access.

## Important APIs, Types, and Functions
The main class is `test_sweep06`, a `wttest.WiredTigerTestCase` plus `suite_subprocess` test. It configures the connection with aggressive file-manager sweep settings, high `session_max`, and `verbose=(sweep:3)`. `make_scenarios` runs the case with cursor caching disabled and enabled. The helper `insert(i, start, rows)` opens an independent session and cursor per table, inserts rows in one transaction, and closes both handles.

## Control Flow
`test_dhandles` optionally enables cursor caching, creates 199 numbered table URIs, and then performs 99 rounds of concurrent inserts across all tables using `wtthread.Thread`. After all worker threads join, it reads `statistics:` and asserts both `stat.conn.dh_sweep_dead_close` and `stat.conn.dh_sweep_expired_close` remain zero.

## State and Persistence Behavior
The test creates many tables and durable row updates, but the observed state is the connection data-handle cache and sweep accounting rather than table contents. Transactions are committed per worker session so handles are repeatedly acquired and released under concurrency.

## Dependencies and Integration Points
It integrates with `wtthread.Thread`, `suite_subprocess`, `wiredtiger.stat`, WiredTiger session/cursor APIs, and the sweep verbose subsystem. It is skipped for the disaggregated hook because multi-threaded tests are incompatible there.

## Risks and Test Signals
The risk under test is an invalid pointer or premature data-handle sweep when table/file handle relationships overlap. The pass signal is strict: no dead or expired dhandle close statistics may increase after the workload.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep07.py

## Purpose
`test_sweep07.py` is a regression test for WT-15647. It verifies that a table handle can be swept after the last cursor and session references are released.

## Important APIs, Types, and Functions
The file defines `test_sweep07`, a `WiredTigerTestCase` using `file_manager=(close_scan_interval=1,close_idle_time=1,close_handle_minimum=1)` to make sweep activity observable quickly. It uses `wiredtiger.stat.conn.dh_sweep_remove` to detect actual handle removal.

## Control Flow
`test_sweep_with_cursor` creates a table, opens and closes an initial cursor after writing one key, then sleeps to allow unrelated history-store cleanup. It records the initial sweep-remove statistic, checkpoints, opens a second session and cursor, reads one record, closes them, closes the original session to release the final reference, sleeps again, then reopens a session and asserts the remove statistic increased.

## State and Persistence Behavior
The table has one persisted key and a checkpoint so the dhandle is eligible for normal lifecycle management. The important state transition is from referenced handle to unreferenced handle after session close.

## Dependencies and Integration Points
The test depends on `time.sleep`, WiredTiger session/cursor/checkpoint/statistics APIs, and file-manager sweep timing configuration.

## Risks and Test Signals
Timing is the main fragility: it relies on short sweep intervals and sleeps. The signal is `remove2 > remove1`, proving the sweep server removed at least one eligible handle after cursor/session closure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered02.py

## Purpose
`test_tiered02.py` validates basic tiered table behavior across checkpoints, `flush_tier`, open cursors, connection restarts, and both simple and complex dataset layouts.

## Important APIs, Types, and Functions
`test_tiered02` combines `WiredTigerTestCase` with `TieredConfigMixin`. Scenarios come from `gen_tiered_storage_sources(..., tiered_only=True)` and a simple/complex dataset dimension. `get_dataset` selects `SimpleDataSet` or `ComplexDataSet`, `confirm_flush` checks the directory-store bucket object count, and `conn_extensions` loads the configured storage source extension.

## Control Flow
The test creates and populates a table with 10 rows, checkpoints, flushes to the shared tier, and verifies data. It closes and reopens the connection, grows the dataset to 50 rows while holding a table cursor open, checkpoints and flushes again, then grows to 100 and 200 rows with further checkpoints, flushes, cursor closure, and restart. Finally it appends 300 rows without a tier flush and checks that object count does not increase on plain checkpoint.

## State and Persistence Behavior
It exercises local object creation, shared-tier object copies, metadata survival across `close_conn`/`reopen_conn`, and readback from tiered objects after local state changes. Directory-store checks track monotonically increasing bucket entries only after flushes.

## Dependencies and Integration Points
The test integrates with `helper_tiered`, `wtdataset`, `os.listdir`, WiredTiger checkpoint configuration, and storage-source extension scenarios.

## Risks and Test Signals
It is sensitive to asynchronous object visibility, so `confirm_flush` retries before failing. Signals include dataset `check()` success after each phase and object-count increase only when `flush_tier` is expected.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered03.py

## Purpose
`test_tiered03.py` is intended to test sharing tiered data between a primary and secondary database using block-log-structured/tiered configuration, but its only test is currently skipped.

## Important APIs, Types, and Functions
`test_tiered03` uses `TieredConfigMixin`, `get_conn_config`, `SimpleDataSet`, and quick scenarios for record count. `conn_config` customizes the bucket and cache directory, using an absolute bucket path for the directory store so multiple connections can share it.

## Control Flow
The skipped `test_sharing` would populate a primary file, checkpoint it, create a `SECONDARY` home, copy metadata into a writable metadata cursor under a relative URI, read the original checkpoint from the secondary, update the primary, extract the new checkpoint string from metadata, alter the secondary metadata, and verify the new data.

## State and Persistence Behavior
The intended state model is two WiredTiger homes sharing the same tiered bucket while using distinct local cache directories. Metadata checkpoint strings are the persistence boundary that lets the secondary advance from an older object view to a newer one.

## Dependencies and Integration Points
It integrates with metadata cursors, `session.alter`, secondary connection creation, regular expressions for checkpoint metadata extraction, and tiered storage source configuration.

## Risks and Test Signals
The explicit skip states that sharing the checkpoint file containing transaction ids is unsupported. If re-enabled, risks include metadata string parsing, relative URI correctness, cache isolation, and checkpoint consistency across homes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered04.py

## Purpose
`test_tiered04.py` is a broad basic tiered-storage API test. It verifies `flush_tier`, local retention, per-object metadata, statistics, reconfiguration, forced flushes, and restart behavior.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `get_conn_config`, `get_check`, `wiredtiger.stat`, and metadata cursors. Helpers include `check_metadata(uri, val_str)`, `get_stat(stat, uri)`, and `check(tc, base, n)`. The connection config sets `tiered_storage=(...,local_retention=3)`.

## Control Flow
The test creates a default tiered table, a tiered table with explicit bucket/prefix/retention, and a local non-tiered table. It writes records, calls checkpoint with `flush_tier=(enabled)` repeatedly, observes skipped and switched counts, waits for local retention, forces tier processing, checks local object removal, writes through open cursors, validates metadata for `tiered:`, `tier:`, `file:`, and `object:` URIs, tests statistics, reconfigures retention, exercises timeout/sync/force options, restarts, and verifies post-restart flush behavior.

## State and Persistence Behavior
It covers local `.wtobj` lifecycle, bucket object creation, metadata fields such as `last`, `oldest`, `tiered_object`, retention-driven local cleanup, and persistence of checkpoint/flush timing across restart.

## Dependencies and Integration Points
It integrates with schema creation, checkpoint manager, tiered manager worker units, statistics, metadata, directory-store buckets, and connection reconfiguration.

## Risks and Test Signals
The test is time-sensitive because retention cleanup is asynchronous. Signals include exact skip/switch/flush statistic values, object existence/removal checks, metadata substrings, and successful data verification after writes and restart.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered06.py

## Purpose
`test_tiered06.py` directly tests WiredTiger storage-source and customized file-system APIs used internally by tiered storage.

## Important APIs, Types, and Functions
The class exposes helpers `get_storage_source`, `get_fs_config`, `suffix`, `check_dirlist`, `check_home`, `check_local_objects`, and `create_wt_file`. It uses `wiredtiger.StorageSource`, `wiredtiger.FileSystem`, `ss_customize_file_system`, `ss_flush`, `ss_flush_finish`, `fs_directory_list`, `fs_exist`, `fs_open_file`, `fh_read`, `fs_size`, `fh_size`, `fh_lock`, `fs_rename`, and `fs_remove`.

## Control Flow
`test_ss_basic` customizes a file system, verifies nonexistence, creates a local file, flushes it to the store, reads it back, checks size and locking, tests bad open, rename, remove, and termination behavior. `test_ss_write_read` writes a large file non-sequentially, flushes it, and validates random and backward reads. `test_ss_file_systems` creates independent file systems for different buckets/cache directories, checks bad bucket errors, flushes multiple files, verifies prefix directory listing, duplicate flush behavior for local storage, and termination independence.

## State and Persistence Behavior
The tests distinguish local WT home files, cache-directory copies, and shared bucket objects. Directory-store checks map "cloud" state to bucket directories.

## Dependencies and Integration Points
It integrates with storage-source extension entry points, file-handle read/size APIs, Python filesystem operations, error-pattern helpers, and tiered scenario setup.

## Risks and Test Signals
Risks include overwrite policy gaps for non-local stores, cache assumptions, and provider-specific error messages. Signals are exact directory listings, byte-for-byte block checks, expected exceptions, and successful termination.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered07.py

## Purpose
`test_tiered07.py` tests schema operations on tiered tables, especially drop semantics, name reuse, similarly named tables, and `remove_files` behavior.

## Important APIs, Types, and Functions
`test_tiered07` uses only the directory-store tiered scenario and a first-checkpoint dimension. It relies on `TieredConfigMixin`, `get_check`, `session.create`, `session.drop`, checkpoint `flush_tier`, and `wiredtiger.WiredTigerError`.

## Control Flow
The test creates three tiered tables with overlapping names plus one local table, inserts one item into each, optionally checkpoints before flushing, calls `flush_tier`, and then drops one tiered and one local table. It asserts default drop removes local object files, verifies `force=true` drops succeed for nonexistent tables, verifies normal drops fail for missing tables, tests whether recreating the same tiered name is blocked when bucket objects exist, verifies similarly named remaining tables still read correctly, creates a new table name, and drops another table with `remove_files=false`.

## State and Persistence Behavior
It observes local `.wtobj` files generated by tiered flush/drop and bucket-object collision state that can prevent table-name reuse.

## Dependencies and Integration Points
The test integrates with schema manager create/drop paths, tiered object naming, flush checkpoint ordering, and local directory-store filesystem state.

## Risks and Test Signals
Important risks are prefix/name overlap mistakes and accidental removal of similarly named table objects. Signals are file existence checks, expected create/drop failures, and cursor readback from surviving tables.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered08.py

## Purpose
`test_tiered08.py` stress-tests concurrent inserts with background checkpoints and occasional tier flushes.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `flush_checkpoint_thread`, fast statistics, and `timing_stress_for_test=(tiered_flush_finish)`. Helpers `get_stat`, `key_gen`, `value_gen`, `populate`, and `verify` control workload generation and validation.

## Control Flow
`test_tiered08` creates a tiered table with small pages, starts a background `flush_checkpoint_thread` that checkpoints every millisecond and flushes roughly one quarter of the time, then inserts batches of 100,000 keys until the connection statistics reach at least 200 checkpoints and 50 flushes. During population it periodically opens a reader cursor to touch existing data. After stopping the thread, it verifies sampled keys, closes and reopens the connection, and verifies again.

## State and Persistence Behavior
The workload creates a large table while checkpoint and tiered object switching can interleave with active writes. Restart verification tests that local and shared tier state remain consistent after concurrent operations.

## Dependencies and Integration Points
It integrates with `wtthread.flush_checkpoint_thread`, connection statistics `checkpoints_api` and `flush_tier`, tiered flush timing stress, and normal cursor read/write paths.

## Risks and Test Signals
Risks include races among checkpoint, flush-finish, object switching, and active writes. Signals are reaching the target stats without errors and sampled key/value correctness before and after reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered09.py

## Purpose
`test_tiered09.py` verifies that one database can reopen sequentially with different bucket prefixes while preserving each tiered object's original prefix metadata and remaining readable.

## Important APIs, Types, and Functions
The test uses `TieredConfigMixin`, `get_conn_config`, `get_check`, manual `wiredtiger_open`, and directory-store object checks. Key constants define expected object names for `table:test_tiered09` and `table:test_second09`.

## Control Flow
The test creates a table under the default prefix, writes data, forces `flush_tier`, closes, and checks directory-store bucket object placement. It removes local object copies, reopens with `bucket_prefix1`, creates a second table, updates the original table, forces another flush, closes, and verifies both prefixes in the bucket. After removing local copies again, it reopens with `bucket_prefix2` and verifies both tables can read all data.

## State and Persistence Behavior
The core persistence invariant is that object metadata stores the prefix used when each object was created, so later connection-level prefix changes must not change lookup paths for existing objects.

## Dependencies and Integration Points
It integrates with tiered connection config, manual reopen paths, bucket prefix configuration, local object deletion, and directory-store bucket naming.

## Risks and Test Signals
Risks include using the current connection prefix for historical object reads or losing pending local cleanup work across close. Signals are bucket file existence under expected prefixes and full cursor readback after prefix changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered10.py

## Purpose
`test_tiered10.py` tests simultaneous WiredTiger homes sharing one bucket directory with different prefixes and identical table names.

## Important APIs, Types, and Functions
`test_tiered10` uses `TieredConfigMixin`, `get_conn_config`, `extensionsConfig`, manual `wiredtiger_open`, and `get_check`. `conn_config` creates two database directories and returns a dummy base connection while preparing a shared saved config.

## Control Flow
The test opens two independent connections in `first_dir` and `second_dir`, both using the same bucket but different `bucket_prefix` values. Each creates `table:test_tiered10`, writes distinct key ranges, forces `flush_tier`, and verifies expected bucket objects for directory store. Both connections close, local object files are removed, connections reopen with the same parameters, and each table is verified against its own data.

## State and Persistence Behavior
The state surfaces are two local homes, one shared bucket, and prefix-disambiguated object names. Removing local objects forces reads through shared storage or cache on reopen.

## Dependencies and Integration Points
It integrates with extension loading, relative bucket paths from subdirectories, tiered object naming, and multi-home connection management.

## Risks and Test Signals
The main risk is cross-home object collision when table URIs and object base names are identical. Signals are two distinct bucket objects and correct readback from both reopened connections.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered11.py

## Purpose
`test_tiered11.py` verifies that tiered metadata records the checkpoint flush timestamp and a nonzero flush time for both tiered and object URIs.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `get_conn_config`, `metadata:` cursors, `timestamp_str`, and `conn.set_timestamp`. `add_data(start)` writes ten records with spaced commit timestamps and advances oldest/stable to the last logical stable timestamp.

## Control Flow
The test creates an integer tiered table, calls `add_data(1)`, checkpoints, then calls `add_data(nentries)` to advance the stable timestamp after the checkpoint. It then performs `checkpoint('flush_tier=(enabled)')`, performs another normal checkpoint, and checks metadata for the tiered URI and first object URI.

## State and Persistence Behavior
The key persistence behavior is that a flush records the stable timestamp of the checkpoint being flushed, not a later stable timestamp set after that checkpoint. Metadata also stores `flush_time`, which must not remain zero.

## Dependencies and Integration Points
It integrates tiered flush metadata with WiredTiger timestamp management and metadata cursor inspection.

## Risks and Test Signals
The risk is recording the wrong stable timestamp when stable advances between checkpoint and flush. Signals are metadata containing `flush_timestamp="<end_ts>"` and not containing `flush_time=0` for both `tiered:` and `object:` URIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered12.py

## Purpose
`test_tiered12.py` checks that `flush_tier` returns after the shared-storage copy completes and does not wait unnecessarily for delayed `flush_finish` work.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `get_conn_config`, `get_check`, and `timing_stress_for_test=(tiered_flush_finish)`. Connection config sets short local retention and a one-second artificial delay in flush finish.

## Control Flow
`test_tiered` creates a tiered table, writes one record, verifies it, and calls forced `checkpoint('flush_tier=(enabled,force=true)')`. For directory store it immediately checks that the bucket object exists, then sleeps long enough for delayed background flush-finish processing.

## State and Persistence Behavior
The test distinguishes completion of copying an object to shared storage from later local/cache finish work. The expected state after the flush call is that the shared object already exists even though finish work can lag.

## Dependencies and Integration Points
It integrates with tiered manager timing-stress hooks, directory-store bucket files, checkpoint flush code, and helper readback checks.

## Risks and Test Signals
The risk is synchronous flush waiting on unnecessary finish work or returning before the copy is durable in the bucket. The signal is successful forced flush and immediate directory-store object existence.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered13.py

## Purpose
`test_tiered13.py` verifies that importing tiered tables or tiered object files is rejected through all relevant import paths.

## Important APIs, Types, and Functions
The test class inherits `test_import_base` and `TieredConfigMixin`. It uses metadata cursors, file copying helpers, `shutil`, `wiredtiger.WiredTigerError`, and tiered connection setup for an import database.

## Control Flow
The test creates a tiered table, writes and force-flushes object 1, writes more data and checkpoints so object 2 exists, then extracts metadata for the current file object and table. After closing, it creates `IMPORT_DB`, opens it with tiered storage enabled, copies the object into several target names, builds import configurations with and without `file_metadata`, and asserts failures for table URI import, table URI plus tiered metadata, file URI import, file URI plus metadata, and renamed file plus metadata.

## State and Persistence Behavior
It uses real tiered object files and exported metadata to exercise import validation. The expected persistence rule is that tiered objects are not portable through generic import because their metadata and object lifecycle are tiered-managed.

## Dependencies and Integration Points
It integrates with WiredTiger import configuration, metadata export, tiered file-object metadata, and test import base helpers.

## Risks and Test Signals
Risks include accidentally allowing import with file metadata or returning misleading errors. Signals are expected `ENOENT`, `Operation not supported`, and incompatible file-metadata error messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered14.py

## Purpose
`test_tiered14.py` is a randomized tiered-storage workflow test covering arbitrary sequences of data additions, updates, checkpoints, flushes, restarts, and validation.

## Important APIs, Types, and Functions
The class uses `TrackedSimpleDataSet` and optionally `TrackedComplexDataSet` with scenario dimensions for key format, value-size multiplier, dataset type, and storage source. `playback(testnum, ops)` is the core interpreter for operation strings, and `progress` annotates failures with test number and position.

## Control Flow
Each playback creates a unique table URI, populates it, then interprets operations: `a` stores a random range of new keys, `u` updates a random existing range, `c` checkpoints, `r` reopens the connection, `f` flushes tier, and `.` checks the tracked dataset. `test_tiered` runs a fixed sequence, then 10 data-heavy random sequences, then 10 sequences with more operational churn, using `random.seed(0)` for repeatability.

## State and Persistence Behavior
Tracked datasets maintain expected logical contents across local cache, on-disk files, shared tier objects, checkpoints, and restarts. Unique URIs avoid cleanup complexity between randomized runs.

## Dependencies and Integration Points
It integrates with `wtdataset` tracked datasets, tiered flush, reopen behavior, random workload generation, and scenario pruning through the helper configuration.

## Risks and Test Signals
Risks include rare operation-order bugs in tiered metadata and object visibility. The signal is that every inserted/updated expected value survives validation at checkpoints, after flushes, and after reopens.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered15.py

## Purpose
`test_tiered15.py` verifies `session.create` behavior for the `type=` configuration when the connection is tiered and when a table explicitly disables tiered storage.

## Important APIs, Types, and Functions
The class combines `TieredConfigMixin` and `WiredTigerTestCase`. Scenario dimensions enumerate `type` values (`file`, `table`, `tier`, `tiered`, `colgroup`, `index`, `backup`) and expected tiered/non-tiered error behavior. The method under test is `test_create_type_config`.

## Control Flow
The test runs only for tiered connections. For tiered tables, it expects only `type=file` to succeed and all other types to fail with `Operation not supported`. For non-tiered tables inside a tiered connection, it creates with `tiered_storage=(name=none)` and allows some types while asserting configured errors for unsupported types. The `colgroup` non-tiered error scenario is skipped because it is expected to crash.

## State and Persistence Behavior
The test does not rely on data writes; it validates schema metadata creation constraints and the boundary between connection-level tiered defaults and table-level `name=none`.

## Dependencies and Integration Points
It integrates with schema creation, configuration validation, tiered table creation paths, and error-message assertions.

## Risks and Test Signals
The risk is inconsistent type validation when tiered storage is enabled. Signals are successful creation for allowed type combinations and exact expected exceptions for disallowed combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered16.py

## Purpose
`test_tiered16.py` validates `session.drop` with `remove_shared`, including invalid option combinations, bucket/cache cleanup, and drop behavior after reopen.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, directory listing helpers `check_cache` and `check_bucket`, and overrides `tiered_extension_config` to enable cache support. It calls `session.drop` with `remove_files` and `remove_shared` combinations and uses `dropUntilSuccess`.

## Control Flow
The test creates tiered tables A and B, verifies that `remove_files=false,remove_shared=true` is rejected, then in directory-store scenarios writes and force-flushes A and B, writes a second object for B, drops A with shared removal, and checks that only B objects remain in cache and bucket. It then drops B and checks both directories empty. Finally it creates table C, writes and flushes, reopens, writes again, and drops until success.

## State and Persistence Behavior
It observes both cache directory and shared bucket contents. `remove_shared=true` must remove shared tier objects only for the dropped table and preserve unrelated table objects.

## Dependencies and Integration Points
It integrates with tiered drop implementation, object cache, bucket cleanup, forced flushes, reopen logic, and invalid configuration validation.

## Risks and Test Signals
Risks include deleting shared objects for the wrong table, leaving stale cache entries, or failing drops after reopen. Signals are exact cache/bucket listings and expected configuration errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered17.py

## Purpose
`test_tiered17.py` verifies that readonly connection and cursor access do not create new tiered object files.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `get_conn_config`, `fnmatch`, filesystem object counting, checkpoint cursors, and two shutdown scenarios: clean and unclean. Helpers include `get_object_files`, `verify_checkpoint`, and `populate`.

## Control Flow
`populate` creates and writes a tiered table, checkpoints with `flush_tier`, and optionally writes extra uncheckpointed data for the unclean scenario. `verify_checkpoint` opens the named checkpoint and asserts the object-file count is unchanged. `test_open_readonly_conn` populates, verifies checkpoint open, records object files, reopens the whole connection with `readonly=true`, closes, and asserts no count changes. `test_open_readonly_cursor` reopens normally but opens a readonly cursor and performs the same object-count checks.

## State and Persistence Behavior
The test tracks local `.wtobj` and `.wt` files in the WT home. The invariant is that readonly recovery/open paths must not switch or create tiered objects, even with uncheckpointed data from an unclean-style scenario.

## Dependencies and Integration Points
It integrates with checkpoint cursor open, readonly connection config, readonly cursor config, tiered flush, and filesystem object naming.

## Risks and Test Signals
The risk is accidental object creation during readonly open, checkpoint open, or close. The signal is an unchanged object-file count at each phase.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered18.py

## Purpose
`test_tiered18.py` tests schema metadata for tiered shared tables, where active local data and shared tiered data are represented by separate colgroups/files.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `get_shared_conn_config`, and `metadata:create` cursors. `check_metadata` accepts exact or comma-continued metadata substrings so it can validate nested config like `log=(enabled=true,...)`.

## Control Flow
The currently active `test_tiered_shared` creates a table with `tiered_storage=(shared=true)`, then checks metadata for the table URI, active colgroup pointing to a local `file:` URI, shared colgroup pointing to a `tiered:` URI, and log configuration on both file and tiered entries. Several related default/shared-false/alter/drop checks are present but commented out under a FIXME.

## State and Persistence Behavior
The test validates metadata shape rather than data contents. Shared tiered tables persist as a table with active and shared colgroups, each linked to the expected underlying file/tiered data source.

## Dependencies and Integration Points
It integrates with shared tiered storage connection setup, schema create metadata generation, colgroup metadata, file metadata, and tiered metadata.

## Risks and Test Signals
The risk is wrong schema decomposition for shared tiered tables. Signals are required metadata links and log settings for active and shared components.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered20.py

## Purpose
`test_tiered20.py` checks that tiered storage never overwrites existing shared objects and detects conflicts across local databases sharing a bucket.

## Important APIs, Types, and Functions
The file defines `wt_boolean`, `test_tiered20`, `additional_conn_config`, `create_flush_drop`, and `file_contains`. Tiered scenarios use short retention/interval settings and `debug_mode=(tiered_flush_error_continue=true)` so flush errors can be asserted instead of crashing the test process.

## Control Flow
The test first repeatedly creates, flushes, and drops a table with `remove_shared=true`. It then creates and drops another table without removing shared objects and verifies recreating the same URI detects `EEXIST`. Next it creates a second WT home sharing the directory-store bucket via symlink, creates the same URI in both homes, writes different payloads, checkpoints both, flushes from the first home successfully, and expects the second flush to fail with `EEXIST`. It verifies the original bucket file still contains the first payload, waits for local removal, reopens, and reads through the cloud copy.

## State and Persistence Behavior
It exercises shared object immutability, bucket collision detection, local retention cleanup, and data recovery after local object removal.

## Dependencies and Integration Points
It integrates with tiered drop, flush error handling, directory-store no-overwrite policy, multi-home connections, symlinked bucket directories, and binary file inspection.

## Risks and Test Signals
Risks include clobbering shared objects or missing collisions after local metadata is removed. Signals are expected `EEXIST`, unchanged file contents, and successful cloud readback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered21.py

## Purpose
`test_tiered21.py` verifies that tiered storage rejects incompatible connection options, specifically `in_memory=true`.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `gen_tiered_storage_sources(..., tiered_only=True)`, `open_with(additional_config)`, and assertions around `wiredtiger.WiredTigerError`.

## Control Flow
`test_options` closes the default connection and attempts to reopen with the normal tiered configuration plus `in_memory=true`, expecting an incompatibility error. `test_reconfigure` attempts `conn.reconfigure('in_memory=true')` on an existing tiered connection and expects an unknown configuration key error.

## State and Persistence Behavior
No data is created. The test validates configuration state transitions at open and reconfigure time. The persistent behavior is negative: an in-memory engine cannot be combined with tiered storage's durable object model.

## Dependencies and Integration Points
It integrates with connection-open validation, connection reconfigure validation, tiered connection scenario setup, and error-message matching.

## Risks and Test Signals
The risk is accepting unsupported option combinations and later failing in less clear paths. Signals are precise failures for open-time incompatibility and reconfigure-time invalid key handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered22.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered22.py

## Purpose
`test_tiered22.py` verifies that compaction is not supported on tiered object files.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `gen_tiered_storage_sources(..., tiered_only=True)`, `session.create`, `session.compact`, and `assertRaisesWithMessage`.

## Control Flow
The test creates `table:tiered` with string keys and values, asserts that the expected first local tiered object file `tiered-0000000001.wtobj` exists, then calls `session.compact` on that local object file and expects `Operation not supported`.

## State and Persistence Behavior
The test relies on schema creation producing a local tiered object file before data writes. It validates that object files managed by tiered storage are not compacted through the normal file compaction API.

## Dependencies and Integration Points
It integrates with tiered object file naming, schema create side effects, and compaction command validation.

## Risks and Test Signals
The risk is allowing compaction to mutate an object whose lifecycle belongs to tiered storage. The signal is the expected unsupported-operation error after confirming the file exists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered22.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered23.py -->
# sources/storage-engines/wiredtiger/test/suite/test_tiered23.py

## Purpose
`test_tiered23.py` tests tiered storage behavior when the local storage-source extension injects delays into tiered operations.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `SimpleDataSet`, and a `tiered_extension_config` override that returns `delay_ms=130,force_delay=3` for local storage. The main method is `test_tiered`.

## Control Flow
For each row count from 10 through 90, the test creates/populates a `SimpleDataSet`, checks it, calls `checkpoint('flush_tier=(enabled)')`, and checks it again. Reusing the same URI with increasing row counts exercises repeated populate and flush cycles under storage-source delay injection.

## State and Persistence Behavior
The test covers tiered data visibility before and after delayed flush operations. It does not inspect object files directly; dataset checks ensure table contents remain correct despite delayed storage-source calls.

## Dependencies and Integration Points
It integrates with local `dir_store` extension delay knobs, tiered flush checkpointing, and dataset population/check helpers.

## Risks and Test Signals
The risk is timing bugs in tiered flush or file-system callbacks when operations are delayed. The signal is successful data verification before and after each flush-tied checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_tiered23.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp01.py

## Purpose
`test_timestamp01.py` covers basic timestamp parsing and range validation for transaction commit timestamps.

## Important APIs, Types, and Functions
The class `test_timestamp01` inherits `WiredTigerTestCase` and `suite_subprocess`. The single method `test_timestamp_range` uses `session.begin_transaction`, `session.timestamp_transaction`, `session.commit_transaction`, `timestamp_str`, and `assertRaisesWithMessage`.

## Control Flow
The test first asserts that setting a commit timestamp outside a running transaction fails. It then starts separate transactions to validate rejection of zero timestamps, overly long hexadecimal timestamps, negative timestamp formatting, and invalid non-hex characters. Finally it commits transactions with valid timestamp forms: timestamp one, uppercase hex, and the maximum 64-bit timestamp expression used by the test.

## State and Persistence Behavior
No table is created and no records are written. The state under test is transaction timestamp metadata attached to running transaction handles and parser acceptance/rejection.

## Dependencies and Integration Points
It integrates with WiredTiger transaction timestamp parsing, Python binding error reporting, `timestamp_str`, and subprocess-capable test harness behavior.

## Risks and Test Signals
Risks include accepting invalid timestamps, rejecting valid uppercase hex, or allowing timestamp assignment without an active transaction. Signals are expected errors and successful commits for valid boundary inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp02.py

## Purpose
`test_timestamp02.py` tests core timestamp visibility, oldest/stable/durable timestamp movement, timestamp statistics, and read-your-writes behavior for row and column stores.

## Important APIs, Types, and Functions
The class defines `get_stat`, `check(session, txn_config, expected)`, `test_basic`, and `test_read_your_writes`. Scenarios vary key format. It uses `conn.query_timestamp`, `conn.set_timestamp`, `session.begin_transaction`, `commit_transaction`, `timestamp_transaction`, and connection timestamp statistics.

## Control Flow
`test_basic` inserts keys 1..100 at timestamps matching keys, verifies historical reads, advances oldest, updates keys at timestamps 101..200, manipulates durable timestamp, sets stable, verifies mixed old/new reads, advances oldest, deletes keys at timestamps 201..300, and verifies deletion visibility. It then validates invalid oldest/stable movements, combined timestamp setting, forced oldest movement, and related statistics. `test_read_your_writes` starts a read-timestamp transaction, assigns a later commit timestamp, writes, and verifies the transaction sees its own write.

## State and Persistence Behavior
The table stores timestamped versions and tombstones. Connection timestamp state controls what reads are legal and what versions are visible. Statistics track oldest/stable/durable/force timestamp calls.

## Dependencies and Integration Points
It integrates with WiredTiger MVCC timestamp visibility, timestamp query APIs, cursor iteration/search, stats cursors, and scenario generation.

## Risks and Test Signals
Risks include incorrect timestamp ordering validation, visibility errors across updates/deletes, and stats regressions. Signals are exact dictionaries at many read timestamps and exact error messages/stat counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp03.py

## Purpose
`test_timestamp03.py` validates timestamped checkpoint behavior across logged and non-logged objects, plus metadata logging flags for data files and the history store.

## Important APIs, Types, and Functions
The class uses `copy_wiredtiger_home`, `suite_subprocess`, `make_scenarios`, metadata cursors, `check`, `backup_check`, and `ckpt_backup`. Scenarios vary URI type, key format, checkpoint `use_timestamp` setting, and log compatibility configuration.

## Control Flow
The test creates four tables: timestamped logged, timestamped non-logged, non-timestamped logged, and non-timestamped non-logged. It inserts timestamped and non-timestamped values, verifies reads at many timestamps, advances oldest/stable, updates all tables, tests rounded reads before oldest, and checks timestamped checkpoint backups for old/new values according to `use_timestamp`. After advancing stable, it checks that backups include newer values. It then writes a third value, flushes the log without checkpoint, and verifies backup visibility differences between logged and non-logged tables. Finally it verifies metadata `log=(enabled=...)` values, including history store logging disabled.

## State and Persistence Behavior
It distinguishes log durability from checkpoint durability and timestamped checkpoint selection. Backup copies are the persistence oracle.

## Dependencies and Integration Points
It integrates with checkpoints, log flush, backup copy helpers, metadata, history store metadata, logging compatibility, and timestamp MVCC.

## Risks and Test Signals
Risks include recovering the wrong logged record, checkpointing unstable updates, or wrong metadata logging flags. Signals are backup value counts and metadata substring checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp04.py

## Purpose
`test_timestamp04.py` verifies `rollback_to_stable` visibility rules for timestamped/non-timestamped and logged/non-logged tables under different logging and cache configurations.

## Important APIs, Types, and Functions
The class defines custom connection opening through `ConnectionOpen(cacheSize)`, a `check` helper that can assert missing keys, and `test_rollback_to_stable`. Scenarios vary connection logging mode, cache size, and row/column format.

## Control Flow
The test opens four tables representing timestamp/logging combinations, inserts 10,000 timestamped keys plus non-timestamped values, verifies visibility, sets stable to half the key range, checkpoints, calls `conn.rollback_to_stable`, and checks rollback statistics. It verifies non-timestamped tables keep all data, non-logged timestamped tables retain only stable-range keys, and logged timestamped behavior depends on connection logging. It advances oldest, writes value 2 at later timestamps, advances stable to one quarter into the later range, rolls back again, checks cumulative rollback stats, and verifies expected value 1/value 2 visibility.

## State and Persistence Behavior
The test stresses in-cache and evicted update chains using small pages and optional small cache. Rollback mutates persisted/in-memory state back to stable timestamp while respecting logging rules.

## Dependencies and Integration Points
It integrates with rollback-to-stable, connection statistics, eviction settings, logging, checkpointing, and timestamped reads.

## Risks and Test Signals
Risks include rolling back logged data incorrectly, missing evicted updates, or bad rollback accounting. Signals are exact key dictionaries/missing checks and rollback stat thresholds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp05.py

## Purpose
`test_timestamp05.py` checks that timestamped create and bulk-load workflows can checkpoint at a stable timestamp without leaking timestamps into metadata or failing dirty-tree handling.

## Important APIs, Types, and Functions
The class uses `WiredTigerTestCase`, `suite_subprocess`, `make_scenarios`, and two tests: `test_create` and `test_bulk`. Scenarios vary integer-row and column-store key formats.

## Control Flow
`test_create` sets oldest/stable to 50, creates a table inside a transaction committed at timestamp 100, writes an additional value to dirty the tree, and checkpoints with `use_timestamp=true`. `test_bulk` creates a table, bulk-loads 100 records through a bulk cursor, sets timestamps to 50, closes the bulk cursor in a transaction committed at timestamp 100, dirties the tree, and checkpoints at stable timestamp. The bulk test is skipped for the disaggregated hook.

## State and Persistence Behavior
The test focuses on metadata and checkpoint interactions rather than explicit readback. It exercises timestamped schema creation and bulk completion when the stable checkpoint timestamp precedes the create/bulk commit timestamp.

## Dependencies and Integration Points
It integrates with session create, bulk cursor close, transaction commit timestamps, stable timestamp checkpoints, and hook-specific bulk support.

## Risks and Test Signals
The risk is incorrectly timestamping metadata or mishandling dirty pages whose create/bulk timestamp is newer than stable. The signal is completing both workflows without errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp06.py

## Purpose
`test_timestamp06.py` verifies multistep transactions that set multiple commit timestamps before final commit, especially checkpoint and rollback behavior for logged versus non-logged timestamped tables.

## Important APIs, Types, and Functions
The class uses `copy_wiredtiger_home`, helpers `check`, `backup_check`, and `ckpt_backup`, plus scenarios for key format, checkpoint `use_timestamp`, and logging compatibility.

## Control Flow
The test creates a logged timestamp table and a non-logged timestamp table. In one transaction it sets commit timestamp 1 and writes value 1 for all keys, then timestamp 101 and writes value 2, then timestamp 201 and writes value 3, then commits at timestamp 301. It verifies latest reads, sets oldest 100 and stable 200, verifies logged tables see value 3 while non-logged tables see value 2 at stable, and checks backup contents depending on checkpoint timestamp mode. If the checkpoint used timestamps, it calls rollback-to-stable and verifies logged tables keep value 3 while non-logged tables roll back to value 2 for both timestamped and non-timestamped reads.

## State and Persistence Behavior
The same transaction contains multiple timestamped update phases, so the first and later commit timestamps must be recorded correctly for checkpoint and rollback selection.

## Dependencies and Integration Points
It integrates with timestamped transaction API, checkpoints, backup copies, logging, rollback-to-stable, and cursor verification.

## Risks and Test Signals
Risks include checkpointing the final update for non-logged tables despite stable being earlier or rollback using the wrong timestamp. Signals are backup value counts and post-rollback dictionaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp07.py

## Purpose
`test_timestamp07.py` validates timestamped checkpoint and backup behavior for a non-logged timestamped table alongside a logged non-timestamped table, with file/table and row/column scenarios.

## Important APIs, Types, and Functions
The class uses `copy_wiredtiger_home`, binary string values, `check`, `check_reads`, `backup_check`, `ckpt_backup`, and `check_stable`. Scenarios vary key format, URI type, logging config, and key count.

## Control Flow
The test creates a non-logged timestamped table and a logged non-timestamped table. It inserts initial values at timestamps 1..n and verifies point reads at each timestamp. It advances oldest/stable to `nkeys`, updates both tables to value2 at timestamps `n+key`, and verifies a timestamped checkpoint/backup at stable excludes value2 from the non-logged table but includes it for the logged table. After advancing stable to `2*nkeys`, it verifies value2 appears everywhere. It then writes value3 at later timestamps, flushes logs without checkpoint, and verifies backup/checkpoint visibility remains stable for non-logged data while logged data appears.

## State and Persistence Behavior
Backups from copied WT homes are the persistence oracle. Stable timestamp controls non-logged timestamped data; logging controls the non-timestamped table.

## Dependencies and Integration Points
It integrates with checkpoint `use_timestamp=true`, log flush, backup copying, timestamped reads, and URI/key-format scenario coverage.

## Risks and Test Signals
Risks include checkpointing unstable non-logged updates or missing logged updates. Signals are exact value counts in live reads and copied backups.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp08.py

## Purpose
`test_timestamp08.py` tests the integer timestamp API variants, read timestamp behavior, oldest-reader queries, and all-durable timestamp calculation.

## Important APIs, Types, and Functions
The class uses `session.timestamp_transaction_uint` with `WT_TS_TXN_TYPE_COMMIT`, `READ`, `PREPARE`, and `DURABLE`; `conn.query_timestamp`; `conn.set_timestamp`; `prepare_transaction`; and `standalone_build` conditional error expectations.

## Control Flow
`test_timestamp_api` validates zero timestamp rejection, first-commit ordering, oldest/stable constraints, non-monotonic commits across separate transactions, read timestamp rejection below oldest, read visibility at timestamps 7 and 8, `oldest_reader` results, and forced backward oldest movement. `test_all_durable` checks all-durable before first commit, after commits, while lower-timestamp transactions are running, across prepared transactions with durable timestamps, with multiple commit timestamps in one transaction, and after checkpoint/reopen.

## State and Persistence Behavior
The table stores timestamped records and prepared transaction metadata. Connection timestamp state and running transaction state affect `oldest_reader` and `all_durable`. Checkpoint/reopen verifies checkpoint timestamp survives recovery.

## Dependencies and Integration Points
It integrates Python integer timestamp bindings with transaction, prepare, checkpoint, recovery, and timestamp query APIs.

## Risks and Test Signals
Risks include divergence between string and integer timestamp APIs and incorrect all-durable minima. Signals are expected errors, point read visibility, and exact queried timestamp values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp09.py

## Purpose
`test_timestamp09.py` is the string-configuration counterpart to timestamp API validation, covering commit/read timestamp ordering and oldest/stable constraints.

## Important APIs, Types, and Functions
The class uses `session.timestamp_transaction`, `session.commit_transaction`, `begin_transaction(read_timestamp=...)`, `conn.set_timestamp`, `conn.query_timestamp`, and standalone versus MongoDB-build error handling.

## Control Flow
The test creates a table, writes initial data, verifies that a second commit timestamp in one transaction cannot move earlier than the first, verifies `commit_transaction` also rejects earlier timestamps, checks commit timestamps older than oldest via both APIs, validates oldest/stable ordering and monotonic movement, verifies commit timestamps must be after stable, commits records with timestamps 6, 8, and 7, rejects reads below oldest, checks visibility of key 8 at read timestamps 7 and 8, queries `oldest_reader`, forces oldest backwards, and verifies a read below the forced oldest is still rejected while timestamp 6 updates `oldest_reader`.

## State and Persistence Behavior
The test maintains several timestamped versions in one table and exercises connection timestamp state. No restart or checkpoint is needed.

## Dependencies and Integration Points
It integrates with string timestamp config parsing, transaction visibility, timestamp query APIs, and build-specific diagnostics.

## Risks and Test Signals
Risks include inconsistent error ordering or stale oldest-reader calculation. Signals are exact errors, point-read results, and timestamp query equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp10.py

## Purpose
`test_timestamp10.py` verifies saving/querying last checkpoint and recovery timestamps across close, recovery, and optional `wt` utility runs.

## Important APIs, Types, and Functions
The class uses `suite_subprocess`, `runWt`, `conn.query_timestamp('get=last_checkpoint')`, `conn.query_timestamp('get=recovery')`, and helpers `data_and_checkpoint` and `close_and_recover`. Scenarios vary key format, close `use_timestamp` mode, and number of `wt list` runs.

## Control Flow
`data_and_checkpoint` creates an oplog-like logged table and three collection-like non-logged tables, inserts separate timestamp ranges into each collection, sets oldest/stable slightly behind each range, checkpoints, and asserts `last_checkpoint` equals the stable timestamp for each checkpoint. `close_and_recover` closes with default, `use_timestamp=true`, or `use_timestamp=false`, optionally runs the `wt` tool one or two times, reopens, and asserts recovery timestamp. The main test verifies logged data is always present and only the last collection loses unstable records when closing with stable timestamp behavior.

## State and Persistence Behavior
Logged oplog data has commit-level durability. Non-logged collections depend on stable checkpoint recovery when `use_timestamp` is true/default. The recovery timestamp should survive intervening `wt` utility opens.

## Dependencies and Integration Points
It integrates close-time timestamp policy, recovery timestamp metadata, checkpoint timestamp metadata, logging, subprocess `wt`, and cursor verification.

## Risks and Test Signals
Risks include wrong default close policy or losing recovery timestamp after utility opens. Signals are exact `last_checkpoint`/`recovery` timestamps and expected recovered data sets.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp11.py

## Purpose
`test_timestamp11.py` verifies behavior when timestamped and non-timestamped transactions modify the same keys, especially across rollback-to-stable.

## Important APIs, Types, and Functions
The class uses `suite_subprocess`, `make_scenarios`, `session.begin_transaction('no_timestamp=true')`, `timestamp_transaction`, `conn.set_timestamp`, `session.checkpoint`, and `conn.rollback_to_stable`. Scenarios cover string-row and column-store keys.

## Control Flow
The test creates a file, inserts two keys at timestamp 2, updates one key at timestamp 5, then updates the other with `no_timestamp=true`. After setting stable to 2, checkpointing, and rolling back to stable, it verifies the timestamp 5 update rolled back while the no-timestamp update remains visible both with and without a read timestamp. It then repeats with the roles swapped, writes a timestamped value to the second key and a no-timestamp value to the first, and verifies reads without timestamp, at timestamp 2, and at timestamp 5.

## State and Persistence Behavior
Non-timestamped updates override timestamp visibility and survive rollback-to-stable. Timestamped updates newer than stable are rolled back unless reintroduced after rollback.

## Dependencies and Integration Points
It integrates MVCC timestamp visibility, no-timestamp transactions, checkpointing, rollback-to-stable, and row/column key formats.

## Risks and Test Signals
Risks include rolling back no-timestamp updates or hiding them at timestamped reads. Signals are exact value comparisons for both keys after rollback and at two read timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp12.py

## Purpose
`test_timestamp12.py` tests the `use_timestamp` setting when closing a connection, contrasting checkpoint-durable and log-durable tables.

## Important APIs, Types, and Functions
The class uses `conn_config='config_base=false,create,log=(enabled)'`, scenarios for key format and close configuration, `verify_expected`, `close_conn(close_cfg)`, and `open_conn`.

## Control Flow
The test creates a logged table and a non-logged checkpoint table, inserts a first range of keys with commit timestamps and advances oldest/stable to the end of that range, then inserts a second range without advancing stable. It closes and reopens using default close config, `use_timestamp=true`, or `use_timestamp=false`. Expected results are built so logged data always includes all keys, while the non-logged table includes only stable-range keys unless `use_timestamp=false` requests all dirty data.

## State and Persistence Behavior
Close-time checkpoint policy determines whether unstable non-logged updates are persisted. Logged data is independent of stable close behavior because it is recovered from the log.

## Dependencies and Integration Points
It integrates with close-time checkpoint configuration, recovery, logging, non-logged checkpoint durability, and cursor iteration.

## Risks and Test Signals
Risks include changing the default stable-close policy or applying it to logged tables incorrectly. Signals are exact recovered dictionaries for logged and checkpoint tables.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp13.py

## Purpose
`test_timestamp13.py` validates `session.query_timestamp` for commit, first-commit, prepare, and read timestamps.

## Important APIs, Types, and Functions
The class uses `suite_subprocess`, row/column scenarios, `session.query_timestamp`, `session.timestamp_transaction`, `session.prepare_transaction`, and `conn.set_timestamp`.

## Control Flow
`test_degenerate_timestamps` verifies all query choices return zero outside a transaction and before timestamps are set, and that an unknown query key is rejected. `test_query_read_commit_timestamps` sets a read timestamp, checks it, sets a commit timestamp and verifies both commit and first_commit, then sets a second commit timestamp and verifies only commit changes. `test_query_round_read_timestamp` starts a transaction with read timestamp rounding, sets a read timestamp below oldest, verifies it rounded to oldest, and confirms later oldest changes do not alter the stored read timestamp. `test_query_prepare_timestamp` prepares at timestamp 10, then sets commit/durable timestamp 20 and verifies prepare and commit queries.

## State and Persistence Behavior
The test inspects per-session transaction timestamp state. It does not depend on persisted records beyond table creation.

## Dependencies and Integration Points
It integrates with transaction timestamp bookkeeping, read timestamp rounding, prepare transaction state, and query validation.

## Risks and Test Signals
Risks include losing first-commit timestamp, reporting dynamic oldest instead of transaction read timestamp, or allowing invalid query keys. Signals are exact query timestamp values and expected error handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp13.py -->
