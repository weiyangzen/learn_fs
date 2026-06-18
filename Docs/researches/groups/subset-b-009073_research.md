# subset-b-009073 research

Grouped research report for WiredTiger Python suite files in `sources/storage-engines/wiredtiger/test/suite`. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug009.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug009.py

Purpose: regression test for reconciliation page splitting with prefix-compressed string keys. The test creates a file object with `prefix_compression=1`, 4KB internal/leaf pages, `leaf_value_max=3096`, and string key/value formats, then inserts two similarly prefixed keys with large values sized around the split boundary.

Important APIs/types/functions: `wttest.WiredTigerTestCase`, `session.create`, `session.open_cursor`, cursor item assignment, and the file URI `file:test_bug009`. There are no helper methods; all behavior is in `test_reconciliation_prefix_compression`.

Control flow: create the object, open one cursor, insert `fill_2__b_27` and `fill_2__b_28`. The absence of an exception is the test signal.

State/persistence behavior: the inserted records force reconciliation to account for prefix compression when deciding how much material fits on a page. The risk under test is overestimating on-page size and choosing an invalid split.

Dependencies/integration: exercises btree reconciliation, prefix compression, page-size limits, and large value handling through the public Python API.

Risks/test signals: the test is narrow and has no explicit readback; its value is detecting assertions, write failures, or crashes during insert/reconciliation pressure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug009.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug010.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug010.py

Purpose: regression test that checkpoints do not leave files marked clean when a checkpoint did not write all updates. It creates many tables, races a background checkpoint with updates, then verifies the next checkpoint sees a consistent value in every table.

Important APIs/types/functions: `wttest.WiredTigerTestCase`, `wtthread.checkpoint_thread`, `threading.Event`, `session.create`, `session.checkpoint`, and checkpoint cursors opened with `checkpoint=WiredTigerCheckpoint`. The class uses `conn_config = checkpoint_sync=false` to make checkpointing faster and `num_tables` scales under long-test mode.

Control flow: populate `num_tables` tables with key `a=0`; checkpoint; for iterations 1-9 start a checkpoint thread while updating every table to the next integer; stop/join the thread; take a foreground checkpoint; read every table from the checkpoint and assert the value matches the iteration.

State/persistence behavior: stresses dirty tracking across many btrees while checkpoints overlap with writes. The key invariant is that a later checkpoint cannot skip a file because an earlier concurrent checkpoint left it incorrectly clean.

Dependencies/integration: skipped for disaggregated hooks because checkpoint cursors are unsupported there. Integrates threading, checkpoint metadata, table handles, and checkpoint cursor visibility.

Risks/test signals: timing-sensitive by design; failures show as mismatched checkpoint values or checkpoint cursor errors rather than explicit internal stat checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug010.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug011.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug011.py

Purpose: long-running eviction stress test for more trees than the eviction server can walk simultaneously. It opens 2,000 tables, more than the built-in 1,000-tree walk limit described in the comments, and repeatedly searches across all of them.

Important APIs/types/functions: `SimpleDataSet`, `wttest.longtest`, `conn_config` returning `cache_size=1GB`, `reopen_conn`, cursor `set_key`, `search`, and `reset`.

Control flow: create and populate 2,000 small-page tables with 10,000 rows each; reopen to force on-disk trees; open one cursor per table to keep handles active; run 10,000 outer operations, searching a random row in every table on each pass.

State/persistence behavior: table pages are persisted before the main loop, then repeatedly faulted/searched/reset under cache pressure. The state under test is hazard-pointer allocation and eviction traversal over many open btrees.

Dependencies/integration: uses `random` for access spread and `SimpleDataSet` key generation. It is explicitly marked `longtest`, so normal quick runs may skip it.

Risks/test signals: extremely expensive; primary signal is survival without eviction failures, hazard pointer exhaustion, crashes, or search errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug011.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug012.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug012.py

Purpose: validates configuration error handling for illegal collator, key format, value format, and compressor names. It ensures invalid configuration strings fail predictably rather than being accepted or failing later.

Important APIs/types/functions: `wiredtiger.WiredTigerError`, `wttest.WiredTigerTestCase.assertRaisesWithMessage`, and `session.create`. The imported `ComplexDataSet` is unused.

Control flow: four independent test methods each call `session.create('table:A', invalid_config)` inside `assertRaisesWithMessage`. Expected messages are `/unknown collator/`, `/Invalid type/`, and `/unknown compressor/`.

State/persistence behavior: no durable data should be created. The tested state is parser/extension registry validation before object creation.

Dependencies/integration: exercises the public schema creation path and error-message contracts for extension-driven configuration fields.

Risks/test signals: depends on stable error message fragments. A false negative can occur if validation still fails correctly but wording changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug012.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug014.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug014.py

Purpose: regression for WT-2115, where fast-delete pages could be incorrectly lost after a crash with an uncommitted truncate. It covers both column-store and row-string scenarios.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, `copy_wiredtiger_home`, `session.truncate`, separate checkpoint session, `setUpConnectionOpen`, and `setUpSessionOpen`.

Control flow: populate 1,000 rows on small pages, reopen to permit fast-delete, begin a transaction, truncate keys 250 through 500, checkpoint from another session while the truncate is uncommitted, copy the home directory as a simulated crash image, open the copy, and verify all 1,000 records still exist.

State/persistence behavior: the key state is an uncommitted fast-truncate visible to checkpoint processing but not durable committed data. The recovery image must not persist the logical deletion.

Dependencies/integration: exercises transaction visibility, checkpointing, fast truncate, copied-home crash simulation, and dataset key abstraction.

Risks/test signals: failure appears as missing records after opening `RESTART`; it is skipped only implicitly by scenario availability, not by hooks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug014.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug015.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug015.py

Purpose: regression for WT-2162, where dropping and recreating indexes in a particular lexical order triggered a NULL pointer dereference.

Important APIs/types/functions: `wttest.WiredTigerTestCase`, `session.create`, `session.drop`, table URI `table:test_bug015`, and index URIs `index:test_bug015:aab` and `index:test_bug015:aaa`.

Control flow: create a table with columns `(k,v)`, create two indexes on column `v`, drop/recreate `aab`, then drop/recreate `aaa`.

State/persistence behavior: manipulates metadata and index handles only; no row data is inserted. The test targets index lifecycle state and namespace ordering.

Dependencies/integration: uses the schema/index metadata subsystem and forced drops through the Python API.

Risks/test signals: no assertions are needed; success means no crash or exception during the exact DDL sequence.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug015.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug016.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug016.py

Purpose: regression for WT-2757 covering when `WT_CURSOR.get_key()` is valid after `insert`. The valid case is append-mode record-number column store; non-append and row-store inserts should require the key to be set again.

Important APIs/types/functions: `wiredtiger.WiredTigerError`, `session.create`, `session.open_cursor`, cursor `set_key`, `set_value`, `insert`, `get_key`, and `assertRaisesWithMessage`.

Control flow: six methods cover simple file column store append, simple column store non-append, simple row store, complex table column store append, complex column store non-append, and complex row store. Append cases assert returned key `1`; all others expect `/requires key be set/`.

State/persistence behavior: writes a single record per case, but persistence is incidental. The tested state is cursor key retention after insert across URI kind and key format.

Dependencies/integration: exercises both file and table cursors, record-number allocation, append cursor configuration, and error handling.

Risks/test signals: depends on exact cursor API semantics. Any API broadening that preserves keys after non-append inserts would need corresponding test intent review.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug016.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug017.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug017.py

Purpose: regression for WT-2987, where opening a cursor on an incomplete table with declared but missing column groups could crash.

Important APIs/types/functions: `wiredtiger.WiredTigerError`, `session.create`, `session.open_cursor`, and `assertRaisesWithMessage`.

Control flow: create `table:bug17` with key/value formats and `columns=(id,country,year,population),colgroups=(main,population)` but without creating the column group objects. Then attempt `open_cursor("table:bug17(country)")` and expect an error matching `/column groups/`.

State/persistence behavior: creates incomplete metadata intentionally. The invariant is that cursor open validates column group completeness and reports an error instead of dereferencing missing structures.

Dependencies/integration: touches table metadata, projection cursor parsing, and column group validation.

Risks/test signals: narrow message-fragment assertion. The absence of a crash is the core signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug017.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug018.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug018.py

Purpose: regression for WT-3590, where a write failure during connection close could leave tables updated in one transaction out of sync after recovery.

Important APIs/types/functions: `suite_subprocess`, `copy_wiredtiger_home`, Linux `/proc/self/fd` inspection, `wiredtiger.WiredTigerError`, `expectedStderrPattern`, `run_subprocess_function`, and cursor iteration. The class enables logging and is skipped for nonstandalone and tiered hooks.

Control flow: in a subprocess, open filler file descriptors, create two file tables, commit the same key/value to both in one transaction, close filler descriptors, close the OS file descriptor for the second table underneath WiredTiger, then close the connection expecting a possible error. The parent copies the home for forensics, reopens, reads table 1, tries to read table 2, and asserts both result sets are equal, treating inability to open table 2 as an empty result only if error output exists.

State/persistence behavior: tests atomic recovery of a transaction spanning multiple files when one file write fails late. Logging and recovery must leave both tables aligned.

Dependencies/integration: Linux-specific file descriptor manipulation, subprocess isolation, recovery, error capture, and filesystem copy helpers.

Risks/test signals: platform and sanitizer sensitive; skipped outside Linux/POSIX and for TSan. Failure is divergence between tables or unhandled close/recovery errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug018.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug019.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug019.py

Purpose: regression that log preallocation only keeps a small moving range of prepared log files, originally targeting accumulation on Windows directory-list handling.

Important APIs/types/functions: `wiredtiger.stat`, `statistics:` cursor, `stat.conn.log_prealloc_used`, `stat.conn.log_prealloc_max`, `session.checkpoint`, `fnmatch.filter`, `os.listdir`, and timing loops.

Control flow: create a logged table with 100KB log file max; populate enough 2KB values to churn many log files and increase `log_prealloc_max`; wait for `*Prep*` files; loop 9 times ensuring `log_prealloc_used` advances after each populate/checkpoint; finally wait up to 90 seconds for the preallocation max to drop below its observed maximum.

State/persistence behavior: writes many unique keys and checkpoints to force log allocation, use, and cleanup. The relevant persistent artifacts are log files and preallocated `Prep` files.

Dependencies/integration: relies on logging subsystem statistics, background log server timing, and filesystem visibility.

Risks/test signals: timing-sensitive, with 90-second waits to reduce flake. Failures indicate no preallocation, nonmoving preallocation use, or failure to shrink when idle.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug019.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug020.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug020.py

Purpose: verifies that an existing `WiredTiger.turtle.set` file can replace a missing `WiredTiger.turtle` file during open.

Important APIs/types/functions: `SimpleDataSet.populate`, `close_conn`, `open_conn`, `os.rename`, and `expectedStdoutPattern`.

Control flow: populate `table:bug020` with 1,000 rows, close the connection, rename `WiredTiger.turtle` to `WiredTiger.turtle.set`, and reopen while expecting stdout containing `WiredTiger.turtle not found`.

State/persistence behavior: manipulates the turtle metadata file after a clean close. The tested open path must recover/recognize the `.set` copy and continue.

Dependencies/integration: filesystem metadata handling, connection startup, and turtle file recovery logic.

Risks/test signals: no readback of table contents; the startup path itself is the signal. Message wording is part of the assertion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug020.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug022.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug022.py

Purpose: ensures modifies are not allowed on top of tombstone updates. It covers row-string and record-number column-store key formats.

Important APIs/types/functions: `wiredtiger.Modify`, `wiredtiger.WT_NOTFOUND`, `make_scenarios`, timestamp APIs, cursor `remove`, `modify`, and `search`.

Control flow: create a file object, set oldest timestamp to 1, insert 9,999 500-byte values at timestamp 2, remove every key at timestamp 3, checkpoint, then for every key attempt `cursor.modify([Modify('B', 0, 100)])` and assert `WT_NOTFOUND`, rolling back each attempted transaction. Finally search every key and assert `WT_NOTFOUND`.

State/persistence behavior: creates on-page tombstones through checkpointing and validates that modify does not resurrect or layer onto deleted versions.

Dependencies/integration: timestamped update chains, checkpoint reconciliation, row/column key abstraction, and modify semantics.

Risks/test signals: high row count for coverage; failures show as successful modify on deleted keys or visible records after tombstone.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug022.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug023.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug023.py

Purpose: regression for WT-5930: a failed `wiredtiger_open` of a backup due to compatibility mismatch must not corrupt the backup so that a later correct open loses data.

Important APIs/types/functions: `backup_base`, `take_full_backup`, `wiredtiger_open`, `wiredtiger.WiredTigerError`, compatibility configs `release=3.2.0`, `require_min=3.2.0`, and `require_min=3.3.0`.

Control flow: create a logged file with compatibility 3.2, write/checkpoint 10 entries, write 10 more entries after the checkpoint, record original cursor data, take a full backup, close the original connection, intentionally open the backup with `require_min=3.3.0` expecting `/Version incompatibility detected:/`, then reopen with `require_min=3.2.0` and compare backup data to original data.

State/persistence behavior: tests backup recovery of post-checkpoint logged updates after a failed compatibility open. The failed startup must not leave metadata/log state partially advanced.

Dependencies/integration: backup harness, logging, compatibility gating, startup recovery, and data comparison.

Risks/test signals: only small data volume, but specifically targets a startup state transition after an expected open failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug023.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug024.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug024.py

Purpose: regression for WT-6526: a readonly connection should open successfully if the database was stopped while a temporary turtle file existed.

Important APIs/types/functions: `SimpleDataSet`, `shutil.copy`, `wiredtiger_open`, `conn.close`, and hook skips for tiered and disaggregated storage.

Control flow: create and populate `table:test_bug024`, close the connection, copy `WiredTiger.turtle` to `WiredTiger.turtle.set`, open the home with `readonly`, then close it.

State/persistence behavior: simulates a home directory containing both stable turtle metadata and a temporary `.set` turtle file. Readonly startup must not require writing cleanup metadata and must not crash.

Dependencies/integration: connection startup, turtle file handling, readonly mode, and filesystem copy semantics.

Risks/test signals: no content assertion; pass condition is successful readonly open/close. Skipped where turtle manipulation is incompatible with storage architecture.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug024.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug025.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug025.py

Purpose: regression for WT-7208: after a missing index file is accessed and returns an error, a later access through the same table cursor must not crash.

Important APIs/types/functions: `ComplexDataSet`, `ds.index_name`, `os.path.getsize`, `os.remove`, `expectedStderrPattern`, `open_conn`, and cursor item assignment.

Control flow: populate a complex table with an index, derive the `.wti` index filename, close the connection, remove the index file, reopen while allowing `No such file or directory` stderr, open the table cursor, attempt an insert twice while catching and printing exceptions, then close the cursor.

State/persistence behavior: intentionally corrupts the database by deleting an index file. The table/index handle error path must remain reusable and not leave a null pointer for the second access.

Dependencies/integration: complex dataset schema/index generation, lazy index file open, error capture, and table update propagation to indexes.

Risks/test signals: error location may vary, so the test only requires the missing-file diagnostic at least once. Core pass signal is absence of process crash.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug025.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug027.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug027.py

Purpose: regression for snapshots containing more than 256 transactions. It ensures many unresolved transaction IDs do not leak into checkpoint/recovery visibility.

Important APIs/types/functions: `SimpleDataSet`, `simulate_crash_restart`, `session_max=512`, multiple sessions/cursors, `session.checkpoint`, and helper `check`.

Control flow: create a nonlogged table, insert 1,000 baseline rows and checkpoint. Open 500 sessions, each begins a transaction and updates a different key to `value_b` without committing. Commit one independent update on the last row to `value_c`, checkpoint, verify a scan sees baseline values except the last row, simulate crash/restart, and verify the same view again.

State/persistence behavior: keeps 499 uncommitted updates live across checkpoint creation. The checkpoint and crash recovery must exclude uncommitted values while preserving the committed last-row value.

Dependencies/integration: transaction snapshot encoding, checkpoint, nonlogged table behavior, crash restart helper, and cursor iteration.

Risks/test signals: resource-heavy due to many sessions. Failures show as unexpected `value_b`, missing `value_c`, or recovery inconsistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug027.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug029.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug029.py

Purpose: regression for WT-9457, verifying that the most recent checkpoint time propagates across restarts so a backup cursor cannot lose its pinned checkpoint.

Important APIs/types/functions: `session.checkpoint(force=1)`, backup cursor `open_cursor('backup:')`, `shutil.copy`, `wiredtiger_open`, `reopen_conn`, and helper `add_data`.

Control flow: populate 2,000 rows and checkpoint, force 100 quick checkpoints, add 2,000 more rows and checkpoint, reopen, modify some rows, open a backup cursor, force 10 checkpoints, add/checkpoint more data to encourage block reuse, copy files listed by the backup cursor into `backup_dir`, open the backup, and sample-read keys every 10 rows from 0 to 3990.

State/persistence behavior: stresses checkpoint deletion and block reuse while a backup cursor pins an older checkpoint after restart. The pinned checkpoint must remain valid for backup restore.

Dependencies/integration: checkpoint metadata timing, backup cursor, filesystem copy, restart behavior, and table reads from the backup home.

Risks/test signals: potential failure is fatal read/panic or wrong sampled values in backup. Uses real backup file copying rather than only metadata inspection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug029.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug030.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug030.py

Purpose: regression for WT-10522 involving aborted tombstones restored from the data store. It ensures reconciliation does not return early when appending a key's original value to an update list.

Important APIs/types/functions: `make_scenarios` for column and integer row formats, `debug_mode=(update_restore_evict=true)`, timestamp APIs, debug eviction cursor `debug=(release_evict)`, `session.checkpoint`, and `reopen_conn`.

Control flow: insert stable values at timestamp 10; set oldest/stable; delete all rows at timestamp 30; evict; write unstable updates at 50; checkpoint and reopen, which rolls back unstable state; delete again at 60; evict all rows at timestamp 70. The final eviction is the regression trigger.

State/persistence behavior: constructs an update chain containing an aborted, restored-from-datastore entry and then reconciles it. The persistence invariant is that original stable values remain reconstructable and reconciliation does not mishandle aborted tombstone flags.

Dependencies/integration: rollback-to-stable during reopen, update restore eviction debug mode, timestamped deletes/updates, and reconciliation.

Risks/test signals: no explicit final read; crashes/assertions during eviction are the signal. Scenario covers both row-store and column-store keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug030.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug031.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug031.py

Purpose: regression for WT-10717/WT-10522 interactions where an original stable update could be missed when the update chain contains aborted updates with `WT_UPDATE_RESTORED_FROM_DS`.

Important APIs/types/functions: `make_scenarios`, timestamp APIs, `reopen_conn` rollback behavior, debug eviction cursor, and timestamped read transactions.

Control flow: insert key at timestamp 10; delete at 20; evict; insert at 30; checkpoint; reopen with stable timestamp 10 causing later updates to abort; start an uncommitted insert and evict to perform update restore; commit it at 40; evict again; then read at timestamp 10 and require the key to be found.

State/persistence behavior: the test deliberately walks the update chain through datastore restore, history store movement, rollback-to-stable, aborted update retention, and a new committed insert. The invariant is that the timestamp-10 original value is not lost when reconciling around aborted restored entries.

Dependencies/integration: row and column scenarios, history store, eviction/reconciliation, checkpoint, and timestamp reads.

Risks/test signals: failure is `WT_NOTFOUND` at timestamp 10 or an eviction assertion. The extensive comments document expected update-chain/disk/HS states and are part of the test's value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug031.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug032.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug032.py

Purpose: regression for WT-11845, ensuring fast truncate does not rely only on aggregated page transaction state when the page contains updates invisible to the truncate transaction.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, `conn.open_session`, transactions in multiple sessions, debug eviction cursor `debug=(release_evict)`, and `truncate_session.truncate`.

Control flow: populate a table with 500 large values on 10KB leaf pages, remove the target key, start `txn1` inserting the key but leave it uncommitted, commit `txn2` on a neighboring key, start the truncate transaction so its snapshot sees `txn2` but not `txn1`, commit `txn1`, evict the page to disk, truncate the whole table, commit the truncate, and verify the `txn1` key still exists.

State/persistence behavior: page aggregate transaction metadata can look visible because of `txn2`, but per-key visibility must prevent fast truncating the page containing `txn1`.

Dependencies/integration: snapshot isolation, fast truncate page selection, eviction, row/column key formats, and dataset page sizing.

Risks/test signals: failure is missing target key after truncate. The scenario is carefully staged so the insert is not converted into a visible modify.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug032.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug033.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug033.py

Purpose: regression for WT-12096, testing insertion of obsolete updates on an update chain after rollback to stable, with checkpoint and eviction racing.

Important APIs/types/functions: `wiredtiger`, `wtthread.checkpoint_thread`, `stat.conn.checkpoint_state`, `timing_stress_for_test=[checkpoint_slow]`, helper `evict`, timestamp APIs, and `rollback_to_stable`.

Control flow: create timestamped updates at 2 and 4, evict to disk, roll back to stable at 1, insert a new timestamp-2 update, advance oldest/stable to 3 making tombstone/update obsolete, sleep to let oldest ID advance, insert timestamp-4 update, start a slow checkpoint thread, wait for checkpoint state to become active, then evict the key while checkpointing.

State/persistence behavior: constructs a chain with obsolete tombstone/update entries plus an on-disk newer value, then forces reconciliation under checkpoint concurrency. The focus is correct obsolete update insertion/removal without corrupting chain state.

Dependencies/integration: timestamp manager, rollback-to-stable, eviction, checkpoint thread, stats cursor, and timing stress.

Risks/test signals: no final assertions; pass condition is no crash/assertion or incorrect busy/error during the concurrent eviction/checkpoint path.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug033.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug034.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug034.py

Purpose: regression for WT-12602, where evicting a page in parallel with checkpoint could incorrectly return `EBUSY` when history store content included a globally visible tombstone and newer modify/update entries.

Important APIs/types/functions: `wiredtiger.Modify`, `debug_mode=(eviction_checkpoint_ts_ordering=true)`, helper `evict_cursor`, `session.checkpoint`, timestamped and non-timestamped transactions.

Control flow: two tests build similar non-timestamped and timestamped chains. They insert base data, checkpoint it, remove all keys to create tombstones, add updates plus modifies, update again to push update/modify/tombstone content to the history store, checkpoint, then dirty the data and call debug eviction across all keys.

State/persistence behavior: targets history store reconciliation ordering when checkpoint timestamp ordering is simulated. The history store must accept tombstone/update/modify combinations without reporting an artificial busy condition.

Dependencies/integration: modify API, history store, checkpoint, eviction debug mode, global visibility via non-timestamped tombstones or advanced oldest timestamp.

Risks/test signals: absence of assertions means the key signal is no exception during dirty eviction. It covers both non-timestamp and timestamp semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug034.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug035.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bug035.py

Purpose: regression for WT-13716 involving selective backup and fast truncate. It verifies that history-store pages for excluded tables do not reappear after opening the backup and shutdown.

Important APIs/types/functions: `backup_base`, `take_selective_backup`, `wiredtiger_open`, `stat.conn.rec_page_delete_fast`, `backup_restore_target`, `verify_metadata=true`, and helper `add_timestamp_data`.

Control flow: create 10 tables, write 9 timestamped generations of 1,000 records to each, set stable timestamp 15, checkpoint, create a backup directory, take a selective backup excluding the last five tables, open the backup with `backup_restore_target` naming the first five tables, assert fast truncate statistic is greater than zero, close, reopen with `verify_metadata=true`, and close.

State/persistence behavior: opening the selective backup runs rollback-to-stable and truncates history-store pages for tables not in the restore target. Metadata and HS must not retain excluded tables after shutdown/reopen.

Dependencies/integration: selective backup harness, timestamped history store, fast truncate, backup restore target filtering, statistics, and metadata verification.

Risks/test signals: failure is no fast truncate or metadata verification error. The large data volume is intended to produce HS content reliably.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bug035.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bulk01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bulk01.py

Purpose: broad smoke and contract test for bulk-load cursors across file/table URIs, integer/record-number/string keys, and integer/string values.

Important APIs/types/functions: `simple_key`, `simple_value`, `make_scenarios`, `stat.conn.cursor_bulk_count`, `session.open_cursor(..., "bulk")`, bulk `append`, `skip_sort_check`, and error assertions.

Control flow: scenario matrix creates objects and tests normal bulk insert/stat increments, variable-length column-store RLE-friendly repeated values, append mode ignoring supplied keys, skipped record handling in column store, very large record numbers, order checking failures for nonmonotonic keys, bulk open rejection on nonempty objects, and busy rejection while another cursor is open. One row-order skip-sort diagnostic test is currently skipped.

State/persistence behavior: bulk cursors populate newly created btrees and must close into normal readable state. Column-store gaps must persist as missing records, and append allocation must assign sequential record numbers.

Dependencies/integration: cursor statistics, btree bulk load path, row/column formats, diagnostic behavior, checkpoint before nonempty rejection, and public error messages.

Risks/test signals: combines many small scenarios; errors include wrong stat counts, incorrect values after append/gaps, missing order-check errors, or allowing illegal bulk cursors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bulk01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bulk02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_bulk02.py

Purpose: tests bulk-load interactions with checkpoints, hot backup, and transactions.

Important APIs/types/functions: `suite_subprocess`, `simple_key`, `simple_value`, `make_scenarios`, checkpoint configs `name=myckpt` or unnamed, backup helper `backup`, and `assertRaisesWithMessage`.

Control flow: `test_bulkload_checkpoint` opens a bulk cursor, inserts records, checkpoints repeatedly while the cursor is open, closes it, and for named checkpoints verifies the skipped table cannot be opened from that checkpoint. `test_bulkload_backup` inserts via open bulk cursor, optionally checkpoints, runs backup from the same or different session, opens the backup, and confirms the object is empty. `test_bulk_checkpoint_in_txn` verifies opening a bulk cursor inside an active transaction fails with a clear message.

State/persistence behavior: open bulk-load handles are intentionally skipped by checkpoint/backup until closed. Bulk cursor state must not leak partial rows into durable snapshots or backup copies.

Dependencies/integration: checkpoint subsystem, backup tool wrapper, session/connection handle caches, transaction state validation, and file/table plus row/var scenarios.

Risks/test signals: failure indicates checkpoint/backup included unclosed bulk content or transaction restrictions regressed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_bulk02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cache_evict_config01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cache_evict_config01.py

Purpose: validates dynamic reconfiguration of cache eviction controls and rejects invalid eviction ranges without restarting the connection.

Important APIs/types/functions: `conn.reconfigure`, `wiredtiger.WiredTigerError`, `assertRaisesException`, and table cursor read/write operations. Connection config enables `cache_size=50MB,statistics=(all)`.

Control flow: create a table and insert baseline rows; iterate through valid `eviction=[...]` configurations covering `incremental_app_eviction`, `prefer_scrub_eviction`, `app_eviction_min_cache_fill_ratio`, `skip_update_obsolete_check`, and `cache_tolerance_for_app_eviction`; after each reconfigure write/read rows to prove the connection is alive. Then assert invalid negative or too-large ratio/tolerance configs raise `Invalid argument`.

State/persistence behavior: data updates are only liveness checks; the key state is mutable connection-level eviction configuration.

Dependencies/integration: configuration parser, live connection reconfigure path, eviction option validation, and stderr filtering for expected invalid-argument output.

Risks/test signals: does not verify runtime eviction behavior, only acceptance/rejection and continued usability.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cache_evict_config01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cache_evict_config02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cache_evict_config02.py

Purpose: verifies that enabling `prefer_scrub_eviction` dynamically increases scrub/write-restore activity under cache pressure.

Important APIs/types/functions: `stat.conn.cache_write_restore_scrub`, `conn.reconfigure`, `statistics:` cursor, and repeated cursor updates. Connection config uses a small 5MB cache with statistics enabled.

Control flow: create a table, repeatedly update 100 keys 50,000 times with 5KB values to create dirty/update pressure, read baseline scrub statistic, reconfigure `eviction=[prefer_scrub_eviction=true]`, repeat the update workload, read the statistic again, and assert it increased.

State/persistence behavior: repeatedly overwrites the same key set, generating cache pressure and restored-update scrub opportunities. The durable row contents are not inspected.

Dependencies/integration: cache eviction, scrub eviction preference, runtime reconfiguration, and connection statistics.

Risks/test signals: statistic sensitivity can be workload/platform dependent. Failure means the flag did not measurably affect scrub eviction or stats were not updated.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cache_evict_config02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cc01.py

Purpose: shared base utilities for checkpoint-cleanup tests. It centralizes update generation, modify generation, timestamped reads, table population, and checkpoint-cleanup triggering/stat validation.

Important APIs/types/functions: class `test_cc_base`, `get_stat`, `large_updates`, `large_modifies`, `check`, `populate`, `wait_for_cc_to_run`, and `check_cc_stats`. It uses `wiredtiger.Modify`, `stat.conn.checkpoint_cleanup_success`, `checkpoint_cleanup_pages_visited`, and `checkpoint_cleanup_pages_removed`.

Control flow: helpers open cursors, commit per-row timestamped updates, apply modify lists in one transaction, scan at read timestamps, and force cleanup via `session.checkpoint("debug=(checkpoint_cleanup=true)")`, optionally with a checkpoint name. `wait_for_cc_to_run` loops until the success counter advances.

State/persistence behavior: supports tests that create history-store content and then drive cleanup. The base itself has no tests but defines the state transitions used by `test_cc02` and later files.

Dependencies/integration: imported directly by sibling checkpoint-cleanup tests, relying on statistics cursors and debug checkpoint configuration.

Risks/test signals: if stat names or debug config change, all dependent cc tests can hang or fail. The waiting loop has no explicit timeout.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cc02.py

Purpose: verifies checkpoint cleanup removes obsolete history-store content whether obsolete content remains in memory or has been evicted to disk.

Important APIs/types/functions: inherits `test_cc_base`, uses `make_scenarios`, `stat.conn.checkpoint_cleanup_pages_evict`, `checkpoint_cleanup_pages_removed`, duration and handle stats, and debug eviction session `debug=(release_evict_page=true)`.

Control flow: populate 1,000 rows at timestamp 1, set oldest/stable to 1, update all rows at timestamp 10, set stable to 10, checkpoint so newer values are in the data store and older values in HS. In disk mode, read at timestamp 1 with release-evict to move HS pages to disk. Advance oldest to 10, force checkpoint cleanup, and assert visited/processed/duration stats plus either in-memory eviction or on-disk removal depending on scenario.

State/persistence behavior: intentionally makes timestamp-1 history obsolete by advancing oldest. Cleanup should mark in-memory obsolete pages dirty for eviction or remove on-disk obsolete pages.

Dependencies/integration: history store, checkpoint cleanup, eviction, Windows time granularity handling, and base helper timing loop.

Risks/test signals: different expectations for in-memory vs disk flow; timing stat check is skipped on Windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cc04.py

Purpose: negative checkpoint-cleanup test ensuring pages that are not obsolete are visited but not cleaned.

Important APIs/types/functions: inherits `test_cc_base`, `SimpleDataSet`, `large_updates`, `wait_for_cc_to_run`, and connection stats `checkpoint_cleanup_pages_evict`, `checkpoint_cleanup_pages_removed`, and `checkpoint_cleanup_pages_visited`.

Control flow: create `table:cc04`, pin oldest/stable to 1, perform several rounds of 10,000-row timestamped large updates at timestamps 10 through 70, forcing checkpoint cleanup after selected rounds. After every cleanup, assert no pages were evicted or removed by cleanup while pages were visited.

State/persistence behavior: updates create history-store candidates, but oldest timestamp stays pinned so older versions are still required and must not be removed.

Dependencies/integration: timestamp visibility, history-store retention, checkpoint cleanup selection logic, and stats.

Risks/test signals: if cleanup becomes over-aggressive, removal/eviction stats become nonzero. The test is workload-heavy but straightforward.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cc05.py

Purpose: verifies checkpoint cleanup/garbage collection does not remove a checkpoint that is locked by an open checkpoint cursor. It covers named and unnamed checkpoint flows for column and integer row formats.

Important APIs/types/functions: inherits `test_cc_base`, `SimpleDataSet`, `make_scenarios`, `session.open_cursor(... checkpoint=...)`, `large_updates`, `check_cc_stats`, and skip for disaggregated storage.

Control flow: write values at timestamps 20, 30, 40, set stable to 35, create a named or unnamed checkpoint, open a cursor on it, advance oldest/stable to 40, write more generations at 50/60/70, advance oldest/stable to 70, force cleanup, and verify the open cursor still reads value at timestamp 30 (`value_y`). After closing, named checkpoints should still read `value_y`; unnamed latest checkpoint should read `value_w`.

State/persistence behavior: an open checkpoint cursor pins a checkpoint while cleanup removes older history. Named checkpoints persist by name; unnamed `WiredTigerCheckpoint` resolves to latest after cursor close.

Dependencies/integration: checkpoint cursor pinning, timestamp history, cleanup stats, and named checkpoint support.

Risks/test signals: failure indicates cleanup deleted in-use checkpoint state or named/unnamed checkpoint resolution regressed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cc06.py

Purpose: verifies checkpoint cleanup ignores empty or newly created files.

Important APIs/types/functions: inherits `test_cc_base`, uses `SimpleDataSet`, `make_scenarios`, dsrc stat `checkpoint_cleanup_pages_visited`, `wait_for_cc_to_run`, and `reopen_conn`.

Control flow: create an empty dataset for `table:cc06` with logging disabled and the scenario key/value format, set oldest/stable to 10, force checkpoint cleanup, assert the table-level pages-visited stat is zero, reopen the database, force cleanup again, and assert the same stat remains zero.

State/persistence behavior: tests the empty-file metadata state before and after reopen. Cleanup should not scan pages that do not exist or newly created btrees with no obsolete content.

Dependencies/integration: dsrc statistics, checkpoint cleanup, empty btree handling, connection reopen, column/integer row scenarios.

Risks/test signals: failure is nonzero page visits, indicating wasted or incorrect cleanup work on empty files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cc07.py

Purpose: verifies checkpoint cleanup removes obsolete time-window information from pages and respects heuristic limits on btrees/pages per checkpoint.

Important APIs/types/functions: inherits `test_cc_base`, uses `make_scenarios`, connection config `heuristic_controls=[obsolete_tw_btree_max=...]` and `checkpoint_cleanup_obsolete_tw_pages_dirty_max=...`, dsrc/conn stat `checkpoint_cleanup_pages_obsolete_tw`, and tiered skip.

Control flow: for each heuristic scenario, append 10 batches of 1,000 1KB values, checkpoint after each batch, and advance stable/oldest to make time windows obsolete. Force cleanup, read per-btree and connection obsolete-time-window cleanup stats, and assert either zero cleanup when limits are disabled or positive cleanup bounded by the configured maximum.

State/persistence behavior: repeated timestamp advancement makes earlier start time windows globally visible and removable. Cleanup should dirty only up to the configured number of pages.

Dependencies/integration: checkpoint cleanup heuristics, time-window reconciliation, statistics logging, and timestamped population helper.

Risks/test signals: failures indicate cleanup ignores disable settings, fails to clean when enabled, or exceeds page dirtying limits.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cc08.py

Purpose: verifies checkpoint cleanup selects logged tables for cleanup only when configured in aggressive reclaim-space mode.

Important APIs/types/functions: inherits `test_cc_base`, uses `make_scenarios`, config `checkpoint_cleanup=[method=none|reclaim_space]`, connection stats `checkpoint_cleanup_pages_read_reclaim_space` and `checkpoint_cleanup_pages_visited`, and skips tiered storage.

Control flow: create a logged small-page table, populate 1,000 rows, checkpoint, reopen with the scenario cleanup method, open a cursor to ensure the data handle is active, force cleanup, then assert selected/visited page stats are positive for `reclaim_space` and zero selected pages for `method=none`.

State/persistence behavior: table is logged and clean on disk after restart. Reclaim-space cleanup should read pages for possible cleanup only under aggressive mode.

Dependencies/integration: logged table handling, checkpoint cleanup method config, dhandle activation, stats.

Risks/test signals: failure means method gating is wrong or logged-table cleanup selection did not run.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cc09.py

Purpose: verifies checkpoint cleanup reads pages from disk to remove obsolete time-window information only when necessary conditions and heuristic limits allow it.

Important APIs/types/functions: inherits `test_cc_base`, uses scenarios for heuristic limits and cleanup preconditions, dsrc stats `checkpoint_cleanup_pages_read_obsolete_tw` and `checkpoint_cleanup_pages_obsolete_tw`, optional delete, timestamp bumping, and tiered skip.

Control flow: populate 100,000 rows, set stable and checkpoint, advance oldest to make part of the time windows obsolete, reopen so pages are on disk, open/read/reset a cursor to activate the handle, optionally delete one key and checkpoint, optionally advance oldest to the end, force cleanup, then assert read/dirty stats based on `expected_cleanup` and whether delete or oldest bump made cleanup valid.

State/persistence behavior: moves pages to disk before cleanup, then tests disk-read cleanup of obsolete time-window metadata. Deletes and oldest timestamp movement provide the trigger conditions.

Dependencies/integration: checkpoint cleanup disk reads, heuristic controls, timestamp manager, dsrc stats, and large table population.

Risks/test signals: large workload; failures identify missing cleanup, unexpected cleanup without triggers, or too many dirtied pages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cc10.py

Purpose: verifies the obsolete checkpoint-cleanup background thread can be configured with different wait intervals and still performs cleanup.

Important APIs/types/functions: inherits `test_cc_base`, uses `make_scenarios`, config `checkpoint_cleanup=[wait=...,file_wait_ms=...]`, verbose checkpoint cleanup output filtering, `time.sleep`, and stats `checkpoint_cleanup_pages_visited`, `checkpoint_cleanup_pages_evict`, `checkpoint_cleanup_pages_removed`.

Control flow: create and populate 1,000 rows at timestamp 1, set oldest/stable to 1, update all rows at timestamp 10, set stable to 10 and checkpoint to create HS content, advance oldest to 10 making it obsolete, sleep 5 seconds so the background thread can run, force/wait for cleanup progress, and assert pages were visited and either evicted or removed.

State/persistence behavior: creates obsolete history-store entries and expects background cleanup scheduling to act on them under varied interval configs.

Dependencies/integration: background checkpoint cleanup thread, timing config, history store, stats, and verbose output handling.

Risks/test signals: timing-sensitive because it relies on sleep plus stat progress. Failure means cleanup did not run or did not remove obsolete content.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cc10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint01.py

Purpose: comprehensive checkpoint API suite covering named checkpoint contents, dropping, cursor opens, in-use protection, update rejection, reserved names, and empty checkpoints.

Important APIs/types/functions: multiple `WiredTigerTestCase` classes, `SimpleDataSet`, `make_scenarios`, `session.checkpoint` with `name`, `drop`, `from=all`, checkpoint cursors, `verifyUntilSuccess`, and `wiredtiger.WT_NOTFOUND`.

Control flow: `test_checkpoint` builds a sequence of named checkpoints over overlapping key ranges and verifies each checkpoint's expected record map as checkpoints are dropped. `test_checkpoint_cursor` covers non-existent checkpoint opens, multiple open cursors, and drop/regenerate failures while a cursor is in use. `test_checkpoint_cursor_update` asserts checkpoint cursors reject `insert`, `remove`, and `update`. `test_checkpoint_last` verifies `WiredTigerCheckpoint` resolves to the latest checkpoint repeatedly. `test_checkpoint_illegal_name` validates reserved checkpoint names and grouping characters. `test_checkpoint_empty` verifies named/unnamed checkpoints over empty objects and latest-checkpoint behavior after later writes.

State/persistence behavior: exercises checkpoint metadata lifecycle and immutable checkpoint snapshots under file/table URIs and precise/fuzzy checkpoint modes.

Dependencies/integration: named checkpoints are skipped for disaggregated and tiered where unsupported. Uses stable timestamp setup for precise checkpoints.

Risks/test signals: failure modes include wrong checkpoint contents, allowing illegal names, allowing writes on checkpoint cursors, or dropping in-use checkpoints.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint02.py

Purpose: concurrency stress test that runs background checkpoints while multiple operation threads insert/update data.

Important APIs/types/functions: `queue.Queue`, `threading.Event`, `wtthread.checkpoint_thread`, `wtthread.op_thread`, `make_scenarios`, and precise/fuzzy checkpoint config.

Control flow: create a table, start a checkpoint thread, enqueue 50,000 inserts and periodic `b` operations, start 10 or 30 worker threads depending on dataset size, wait for queue completion, stop/join all threads, then scan the table and assert keys are sequential from 1 to `nops` with expected value.

State/persistence behavior: mutates one table while checkpoints run concurrently. The final scan validates no committed operation was lost or reordered in the durable/live view.

Dependencies/integration: thread helpers from `wtthread`, checkpoint precision modes, row/column key formats, and queue draining on exceptions.

Risks/test signals: timing/concurrency sensitive; final data assertion catches missing or out-of-order keys, while thread exceptions surface through the test harness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint03.py

Purpose: verifies checkpoints write older updates to the history store and that the latest update remains readable after reopen.

Important APIs/types/functions: `suite_subprocess`, `stat.conn.cache_write_hs`, `make_scenarios`, `session.checkpoint`, timestamp APIs, `setUpConnectionOpen`, and `setUpSessionOpen`.

Control flow: create a table, commit three updates to key 1 at timestamps 2, 3, and 4, set oldest/stable to 1/4, checkpoint, assert `cache_write_hs >= 1`, commit another update at timestamp 5, set stable to 5, checkpoint again, assert `cache_write_hs >= 2`, close/reopen, and verify key 1 reads value 4.

State/persistence behavior: checkpoint reconciliation should place older versions in the HS and latest stable value in the data file. Reopen validates persisted latest state.

Dependencies/integration: history store write statistics, timestamped updates, checkpoint precision modes, and row/column formats.

Risks/test signals: HS stat is coarse, so assertions are lower bounds. Failure can indicate no HS write or incorrect latest persisted value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint04.py

Purpose: validates checkpoint timing statistics are populated and ordered as expected, especially that preparation timing is less than total checkpoint timing.

Important APIs/types/functions: `SimpleDataSet`, `stat.conn.checkpoints_api`, `checkpoint_state`, `checkpoint_prep_running`, `checkpoint_prep_min/max/recent/total`, `checkpoint_time_min/max/recent/total`, `reopen_conn`, and precise/fuzzy scenarios.

Control flow: in a retry loop with increasing value size, create 50 tables, update 100 rows per table, checkpoint, recreate/update tables with a different value, checkpoint again, read and print timing stats, assert checkpoint count, state, and prep_running values, and exit only when prep stats are all less than corresponding total time stats. Reopen resets stats between retries and fails if multiplier reaches 100.

State/persistence behavior: workload creates enough dirty data across many tables for measurable checkpoint timings. Statistics are the main persisted connection state under test.

Dependencies/integration: statistics subsystem, checkpoint implementation, precise checkpoint stable timestamp requirement, and dataset helper.

Risks/test signals: designed to handle coarse timers by retrying; failures may be platform timing issues or bad stat accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint05.py

Purpose: ensures WiredTiger does not accumulate many checkpoints while a backup cursor is open; checkpoints created after backup start should still be deleted as usual.

Important APIs/types/functions: metadata cursor `metadata:`, helper `count_checkpoints`, backup cursor `open_cursor('backup:')`, forced checkpoints, logging config with `remove=false`, and precise/fuzzy scenarios.

Control flow: create a table, insert 16 rows, checkpoint, open a backup cursor, count checkpoint strings in metadata, sleep 2 seconds to avoid immediate pinning effects, force 50 checkpoints, count metadata checkpoint references again, and assert the final count is less than three times the initial count.

State/persistence behavior: backup cursor pins a checkpoint, but later internal checkpoints should not accumulate unbounded metadata entries.

Dependencies/integration: backup cursor pinning, checkpoint deletion/metadata cleanup, logging, and precise checkpoint stable timestamp setup.

Risks/test signals: threshold is intentionally generous. Failure indicates checkpoint cleanup was blocked too broadly by the backup cursor.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint06.py

Purpose: verifies rollback-to-stable rolls back a truncate committed after the stable timestamp, including prepared-transaction and non-prepared variants.

Important APIs/types/functions: `make_scenarios`, `session.truncate`, `prepare_transaction`, `timestamp_transaction`, `rollback_to_stable`, `reopen_conn`, and row/column formats.

Control flow: insert 10,000 rows at timestamp 2, set stable to 2, reopen to flush to disk, truncate from key 5 to the end at timestamp 3, optionally prepare with durable timestamp 5 while stable is 4, write another table at timestamp 6 to trigger eviction, checkpoint, call `rollback_to_stable`, and verify every original row remains.

State/persistence behavior: the truncation is beyond stable and must be undone even if it was included in a checkpoint or had a durable timestamp later than stable. Auxiliary table writes increase eviction/checkpoint pressure.

Dependencies/integration: truncate, timestamps, prepared transactions, checkpoint, eviction pressure, RTS.

Risks/test signals: failure is missing rows after RTS. The prepared path specifically checks commit/durable timestamp ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint07.py

Purpose: tests dsrc statistic `btree_clean_checkpoint_timer` behavior for clean vs dirty tables, forced checkpoints, and backup cursor pinning.

Important APIs/types/functions: `stat.dsrc.btree_clean_checkpoint_timer`, checkpoint `force=true`, backup cursor `backup:`, precise/fuzzy scenarios, and tiered skip.

Control flow: create three tables, insert initial rows and checkpoint, dirty table 1 and checkpoint, assert table 1 timer is zero while clean tables have nonzero timers. Force checkpoint and assert all timers reset to zero. Dirty tables 1 and 2 and checkpoint, expecting only table 3 to have a clean timer. Open a backup cursor, perform writes/checkpoints so pinned checkpoints affect timer values, compare finite timer values against the saved "forever" value, close backup cursor, and confirm clean table timer returns to forever behavior.

State/persistence behavior: the timer records whether clean checkpoints can be skipped or must be retained because backup pins older checkpoint generations.

Dependencies/integration: checkpoint cleaner, backup cursor, per-dsrc statistics, precise timestamp setup.

Risks/test signals: time values can differ by one second, handled by tolerance checks. Failures indicate clean checkpoint timer accounting regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint09.py

Purpose: verifies reconciliation clears obsolete time-window metadata for on-disk cells as oldest/stable timestamps advance.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, `stat.conn.rec_time_window_start_ts`, helper `large_updates`, `check`, `evict_cursor`, `debug=(release_evict)`, and `wttest.prevent(["timestamp"])`.

Control flow: populate 1,000 rows, pin oldest/stable to 1, update all rows at timestamp 10, checkpoint and assert time-window start count equals 1,000. Evict, update every 10th row at timestamp 20, set oldest/stable 10/20, checkpoint and assert count increased by 100. Evict, update every 100th row at timestamp 30, set oldest/stable 20/30, checkpoint and assert count increased by 10.

State/persistence behavior: advancing oldest makes older time-window metadata obsolete, and checkpoints should rewrite cells accordingly. Eviction ensures pages are reconciled from disk state.

Dependencies/integration: timestamp manager, reconciliation stats, eviction debug cursor, row/column formats, and disaggregated page-delta config override.

Risks/test signals: exact stat counts make the test sensitive to reconciliation behavior changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint10.py

Purpose: tests reading checkpoints created while a large transaction commits concurrently, without timestamps. The checkpoint must show either the pre-transaction or post-transaction state, never a torn intermediate state.

Important APIs/types/functions: `checkpoint_thread`, `named_checkpoint_thread`, `stat.conn.checkpoint_state`, `timing_stress_for_test=[checkpoint_slow]`, `SimpleDataSet`, `make_scenarios`, and checkpoint cursor scans.

Control flow: write baseline `value_a` rows and checkpoint, start a second session transaction writing `value_b` over an overlapping or nonoverlapping range, start named or unnamed checkpoint in a background thread, wait until checkpoint state is active, commit the transaction, optionally reopen, then scan the checkpoint and compare observed value counts to one of two valid maps.

State/persistence behavior: stresses checkpoint snapshot consistency across file/table generations, named/unnamed checkpoints, logging/nonlogging, and precise/fuzzy modes.

Dependencies/integration: concurrency, checkpoint state stats, transaction commit racing with checkpoint, and checkpoint cursor visibility.

Risks/test signals: disabled crash/RTS crosscheck notes flakiness in generating inconsistent checkpoints. Active assertion only checks visible checkpoint state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint11.py

Purpose: timestamped version of inconsistent checkpoint visibility testing. It verifies checkpoint reads at explicit timestamps return complete valid states even when a timestamp-30 transaction commits during checkpointing.

Important APIs/types/functions: `checkpoint_thread`, `named_checkpoint_thread`, `stat.conn.checkpoint_state`, debug checkpoint cursor option `checkpoint_read_timestamp`, `SimpleDataSet`, scenario matrices for stable timestamp, overlap, advance, named/unnamed, and reopen behavior.

Control flow: set oldest/stable to 5, write full-table values at timestamps 10 and 20, checkpoint, prepare a large timestamp-30 transaction in another session, set stable to scenario value, start checkpoint thread, wait for checkpoint state, commit at 30, optionally reopen, build expected value-count maps for read timestamps 5/15/25/35 and default stable read, optionally advance timestamps to 50, then scan the checkpoint at each timestamp.

State/persistence behavior: validates checkpoint timestamp metadata and snapshot isolation under a concurrent commit. Default checkpoint read should reflect the stable timestamp at checkpoint creation.

Dependencies/integration: timestamped reads from checkpoints, slow checkpoint stress, named checkpoints, scenario filtering, and row/column formats.

Risks/test signals: crash/RTS crosscheck is disabled for reliability. Main failure is a torn value-count map at any timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint12.py

Purpose: validates that checkpoint cursor reads are forbidden after the owning session has prepared a transaction, preserving the blanket ban on operations after prepare.

Important APIs/types/functions: `make_scenarios` over cursor operations `search`, `next`, `prev`, `search_near`, `prepare_transaction`, checkpoint cursor `WiredTigerCheckpoint`, and `assertRaisesWithMessage`.

Control flow: create and populate a column-store table, set timestamps, write data at timestamp 10, checkpoint, write more data at timestamp 20, open a checkpoint cursor and set its key, begin a new transaction updating half the rows, prepare at timestamp 30, then invoke the scenario operation on the checkpoint cursor and expect `Invalid argument`.

State/persistence behavior: the checkpoint cursor has its own internal read transaction, but the session is in prepared state. The API must reject reads rather than mixing transaction contexts.

Dependencies/integration: prepared transactions, checkpoint cursor reads, timestamped updates, and disaggregated skip for checkpoint cursors.

Risks/test signals: operation matrix ensures all major read entry points fail consistently.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint13.py

Purpose: tests checkpoint cursor API restrictions and timestamp bounds for named and unnamed checkpoints.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, checkpoint `name`, checkpoint cursor `checkpoint_read_timestamp`, `wiredtiger.WT_NOTFOUND`, and error assertions for `/before the checkpoint oldest/` and `/cannot be dropped/`.

Control flow: set oldest/stable to 10, write values at timestamp 20, set stable 20 and create named or unnamed checkpoint, write timestamp-30 values, open checkpoint cursor and verify it reads timestamp-20 data both outside and inside an ordinary transaction, then open at read timestamp 10 and see no data, and assert opening at timestamp 5 fails. For named checkpoints, keep a cursor open and assert regenerating or dropping that checkpoint fails.

State/persistence behavior: checkpoint snapshots carry oldest timestamp bounds and remain immutable while later updates occur. Named checkpoint metadata must be pinned by open cursors.

Dependencies/integration: checkpoint timestamp metadata, cursor transaction handling, named checkpoint lifecycle, precise/fuzzy modes, and hook skips.

Risks/test signals: comments mention older restrictions; current expected behavior allows reads inside a normal transaction but not before checkpoint oldest.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint14.py

Purpose: verifies each checkpoint has its own snapshot by creating two successive checkpoints while transactions commit concurrently and then reading both.

Important APIs/types/functions: `checkpoint_thread`, `named_checkpoint_thread`, `stat.conn.checkpoint_state`, `timing_stress_for_test=[checkpoint_slow]`, `simulate_crash_restart`, `SimpleDataSet`, and precise/fuzzy scenarios.

Control flow: write baseline `value_a` and checkpoint, start a transaction writing all rows to `value_b`, start first checkpoint thread and wait until active, commit transaction, repeat with `value_c` and the second checkpoint, then read the first checkpoint expecting all `value_a` and the second expecting all `value_b`. Finally simulate crash/restart; the RTS consistency statistic check is present but disabled.

State/persistence behavior: each checkpoint must retain the snapshot it was created with and not accidentally use a later checkpoint's visibility state.

Dependencies/integration: named/unnamed checkpoint combinations, checkpoint concurrency, snapshot isolation, crash restart helper, and hook skips.

Risks/test signals: comments note timing lag could make the race less deterministic. Assertions focus on snapshot separation rather than torn transaction detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint15.py

Purpose: verifies each checkpoint carries independent timestamp metadata by writing multiple checkpoints at different stable/oldest times and reading all accessible timestamps.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, `session.checkpoint` named/unnamed helper `do_checkpoint`, `checkpoint_read_timestamp`, and `wiredtiger.WiredTigerError` for before-oldest reads.

Control flow: set oldest/stable to 5, write timestamp-10 data and checkpoint, write timestamp-20 data and create first checkpoint, write timestamp-30 data, set oldest 15 and create second checkpoint, write timestamp-40 data, set oldest 25 and create third checkpoint. Reads verify first checkpoint can read timestamp 10 and 20/default, second rejects 10 but reads 20 and 30/default, and third rejects 10/20 but reads 30 and 40/default.

State/persistence behavior: checkpoint metadata stores both the stable content and the oldest timestamp boundary at creation time. Later oldest advancement must not rewrite older checkpoint metadata incorrectly.

Dependencies/integration: named/unnamed checkpoint availability, timestamped checkpoint reads, precise/fuzzy modes, and row/column formats.

Risks/test signals: unnamed checkpoints are only used for the most recent checkpoint because older unnamed checkpoints cannot be reopened by name.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_checkpoint16.py

Purpose: ensures a table that is clean when a later checkpoint is taken can still be read from that checkpoint.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, helper `large_updates`, helper `do_checkpoint`, checkpoint cursor reads, and named/unnamed plus precise/fuzzy scenarios.

Control flow: create two tables, set oldest/stable to 5, write `value_a` to both tables and checkpoint, write `value_b` only to table 2, take a named or unnamed second checkpoint, then open table 1 from the second checkpoint and verify all 1,000 rows still read `value_a`.

State/persistence behavior: table 1 is clean for the second checkpoint but must still be included/addressable in that checkpoint. The test guards against checkpoint metadata omitting clean handles needed for reads.

Dependencies/integration: checkpoint metadata over multiple tables, clean-table handling, row/column formats, and hook skips for storage modes without named checkpoints.

Risks/test signals: failure is inability to open/read table 1 from the second checkpoint or wrong row values/count.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_checkpoint16.py -->
