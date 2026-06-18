# Research Report: subset-b-009080

This grouped report covers WiredTiger layered/disaggregated checkpoint, configuration, and cursor Python tests. Each section preserves the source path and is bounded by reconciliation markers for source-tree-aligned per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint03.py

Purpose: regression coverage for follower-side ingest-table pruning during disaggregated checkpoint pickup. It targets WT-15158 prune timestamp initialization, WT-15192 table-local checkpoint order mismatch, and first-GC behavior when older checkpoints are pinned by cursors.

Important APIs/types/functions: `test_layered_checkpoint03` extends `wttest.WiredTigerTestCase` and is wrapped by `disagg_test_class`; storage scenarios come from `gen_disagg_storages` and `make_scenarios`. Helpers `setup`, `leader_put_data`, `checkpoint`, `create_follower`, and `follower_open_close_dummy_cursor` orchestrate leader writes, stable timestamp advancement, leader checkpoints, follower connections, and checkpoint pickup through `disagg_advance_checkpoint`.

Control flow: setup creates one or more `layered:` URIs with `block_manager=disagg`, populates them, opens a follower, checkpoints, and advances the follower. The first test pins checkpoint 1 with an open follower cursor, creates checkpoint 2, opens a second table to initialize prune timestamp, then creates checkpoint 3. The second test forces one table through many checkpoint orders before checkpointing a second table. The third delays ingest GC participation until a cursor is opened on a previous checkpoint.

State and persistence behavior: mutable state is leader/follower connection state, timestamp counter, stable timestamps, table contents, and open cursors that pin historical checkpoint visibility. Persistence is via shared disaggregated metadata and follower ingest/stable table metadata.

Dependencies/integration points: depends on WiredTiger transactions, checkpoint metadata ordering, `disagg_advance_checkpoint`, and the disaggregated storage helper framework. It integrates with follower checkpoint pickup and ingest garbage collection code.

Risks: failures are timing/state bugs rather than simple value mismatches; tests mostly assert no crash/error, so regressions may surface as assertion failures, checkpoint pickup failures, or hangs. Cursor lifetime and per-table checkpoint order assumptions are central risk points.

Test signals: successful completion across disagg scenarios signals prune timestamps can be initialized/updated while older checkpoints are in use and while metadata order differs by table.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint04.py

Purpose: verifies that a leader can create a disaggregated checkpoint solely to publish a stable timestamp update, even with no dirty table data, and that followers cannot publish such checkpoints themselves.

Important APIs/types/functions: `test_layered_checkpoint04` uses `disagg_test_class`, `gen_disagg_storages`, `make_scenarios`, `wiredtiger_open`, `disagg_get_complete_checkpoint_ext`, `disagg_get_complete_checkpoint_meta`, `disagg_advance_checkpoint`, `query_timestamp('get=last_checkpoint')`, and stdout pattern matching.

Control flow: the test creates a layered table, opens a follower, writes timestamp 10 data, checkpoints, verifies complete checkpoint timestamp 10, advances the follower, and checks follower last checkpoint. It then advances only the leader stable timestamp to 20 and checkpoints without dirtying data. It verifies the complete checkpoint timestamp changed to 20 and the follower picks it up. Next, it writes on the follower and checkpoints there at timestamp 30, then verifies the shared complete checkpoint remains timestamp 20. Finally, it advances the same checkpoint again and checks idempotent log output plus unchanged metadata LSN.

State and persistence behavior: tracks leader stable timestamp, follower last checkpoint timestamp, complete checkpoint metadata, and metadata LSN. Follower-local writes must not mutate shared checkpoint state.

Dependencies/integration points: exercises disaggregated leader/follower role semantics, checkpoint metadata publication, timestamp query APIs, and checkpoint pickup idempotence.

Risks: false positives are limited because timestamp and metadata LSN assertions are explicit. A subtle risk is the test assumes the expected stdout message for repeated pickup remains stable.

Test signals: passing proves timestamp-only leader checkpoints are durable/pickup-visible, follower checkpoints are local-only for shared metadata, and duplicate pickup leaves shared metadata unchanged.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint05.py

Purpose: tests creating an empty layered table while a slow precise checkpoint is already running, then verifies the table is visible and empty to a follower and after restart.

Important APIs/types/functions: class extends `checkpoint_util` and uses `wait_for_checkpoint_start`, `wtthread.Thread`, `timing_stress_for_test=[checkpoint_slow]`, `precise_checkpoint=true`, `restart_without_local_files(step_up=True)`, `disagg_advance_checkpoint`, and standard session create/checkpoint/cursor APIs.

Control flow: the connection starts as follower, steps up to leader, sets stable timestamp 1, creates and populates a separate table, and starts checkpointing in a background thread. Once checkpoint start is detected, the main session creates the empty target table and waits for checkpoint completion. It disables timing stress, takes another checkpoint, opens a follower and advances it, then scans the new table expecting zero rows. It restarts without local files as leader and checks the table remains present and empty.

State and persistence behavior: validates metadata persistence for a concurrently created empty layered table, including shared checkpoint pickup and local-file reconstruction. The important state is table existence rather than row contents.

Dependencies/integration points: integrates checkpoint utility timing detection, disaggregated role reconfiguration, follower checkpoint pickup, and restart-without-local-files helper behavior.

Risks: timing-stress dependence can make the test sensitive to checkpoint scheduling; the short post-start sleep assumes the checkpoint is sufficiently in progress. It also depends on precise checkpoint timestamp setup.

Test signals: pass means concurrent table create is synchronized with checkpoint metadata and survives follower pickup and leader restart without local files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint06.py

Purpose: verifies disaggregated role changes are synchronized with checkpointing so a checkpoint cannot partly complete as leader and partly as follower.

Important APIs/types/functions: extends `checkpoint_util`; uses `restart_without_local_files`, `wtthread.Thread`, `wait_for_checkpoint_start`, `timing_stress_for_test=[checkpoint_slow]`, role `reconfigure`, `disagg_get_complete_checkpoint_ext`, and timestamped transactions.

Control flow: it starts as follower, steps up to leader, creates data at timestamp 1, checkpoints, then restarts as follower. In part 1 it writes timestamp 2 data while follower, sets stable timestamp 2, steps up, verifies the latest disagg checkpoint is still timestamp 1, then checkpoints and expects timestamp 2. In part 2 it writes timestamp 3 data as leader, starts a slow checkpoint in another thread, waits for it to start, steps down to follower while checkpointing, joins, disables stress, and verifies the checkpoint timestamp is 3. After restart it reads all three values.

State and persistence behavior: state is role, stable timestamp, checkpoint timestamp, and durable table values across local-file restart. The checkpoint should preserve the role captured at checkpoint start.

Dependencies/integration points: exercises connection reconfiguration, checkpoint publication, recovery without local files, timing stress, and disaggregated role transition synchronization.

Risks: concurrent role change timing is central; if wait detection is imprecise the test may miss the target interleaving. It also assumes checkpoint timestamp is a sufficient proxy for whether a disagg checkpoint was published.

Test signals: pass indicates step-up does not retroactively publish a follower checkpoint and step-down does not invalidate an in-flight leader checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint07.py

Purpose: validates checksum handling in disaggregated checkpoint metadata, including backward-compatible missing-checksum pickup and rejection of corrupted checksum metadata.

Important APIs/types/functions: uses `disagg_get_complete_checkpoint_meta`, regex extraction/replacement, `conn.reconfigure(disaggregated=(checkpoint_meta=...))`, `restart_without_local_files(pickup_checkpoint=False)`, `captureout.checkAdditionalPattern`, and `assertRaisesWithMessage`.

Control flow: the test creates a layered table, writes three values at timestamp 1, sets stable timestamp, checkpoints, and captures the checkpoint metadata string. It asserts `metadata_checksum=` exists, extracts it, steps down to follower, and restarts without auto-pickup. It removes the checksum field from metadata and reconfigures with that metadata, expecting a missing-checksum log but successful data reads. It restarts again, flips checksum bits, reconfigures with corrupted metadata, and expects a `Checkpoint metadata corruption detected` error.

State and persistence behavior: the durable state is the checkpoint metadata string and the data reachable through it. The test intentionally mutates metadata only through reconfigure strings to validate checksum parsing before/while pickup.

Dependencies/integration points: covers checkpoint metadata serialization, follower pickup validation, checksum compatibility policy, and error reporting.

Risks: the missing-checksum branch is explicitly temporary via FIXME-WT-16000; future behavior changes will require test updates. Regex assumptions must track metadata formatting.

Test signals: pass means valid metadata contains checksum, legacy no-checksum metadata still works with warning, and corrupted metadata is rejected before silently loading bad state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint08.py

Purpose: tests dropping an empty layered table while a slow checkpoint is active, including the case where sweep has closed the idle data handle.

Important APIs/types/functions: extends `checkpoint_util`; uses `file_manager` close settings, `timing_stress_for_test=[checkpoint_slow]`, connection statistics `wiredtiger.stat.conn.dh_sweep_dead_close`, `wtthread.Thread`, `session.drop(..., checkpoint_wait=false)`, and follower `disagg_advance_checkpoint`.

Control flow: the test steps up to leader, sets stable timestamp, creates an empty table in a second session, waits for sweep to close the idle handle by polling stats, then starts a slow checkpoint in a thread. After checkpoint start it drops the table without waiting for checkpoint, joins the checkpoint, disables stress, opens a follower, advances it, and verifies the table still exists and is empty at the checkpoint being picked up. It then performs another leader checkpoint, advances the follower again, and verifies the table can no longer be opened.

State and persistence behavior: table metadata must remain visible to the checkpoint that began before the drop, then disappear after a later checkpoint. The sweep-closed handle ensures the path works without an open local handle.

Dependencies/integration points: data handle sweep, checkpoint/drop synchronization, disaggregated metadata, follower pickup, and checkpoint visibility rules.

Risks: polling sweep progress is inherently timing-dependent, though bounded by 60 seconds. The final open failure checks the leader session rather than follower session, so the key signal is metadata transition after later checkpoint.

Test signals: pass indicates concurrent drop does not corrupt the active checkpoint and later checkpoint correctly removes the object.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint09.py

Purpose: verifies checkpoint-size and database-size accounting for disaggregated metadata under simple, large, repeated, no-checkpoint, follower-no-pickup, deferred-checkpoint, and multi-table cases.

Important APIs/types/functions: class uses `verifyUntilSuccess`, `reopen_conn(config=...,verify_metadata=true)`, `open_conn`, `close_conn`, role reconfiguration, `session.checkpoint`, cursor updates/removes, and `disagg_get_complete_checkpoint_meta` indirectly through verify startup behavior.

Control flow: the first four tests create layered data sets of increasing complexity, checkpoint, and call verify. Database-size tests reopen with `verify_metadata=true` after checkpointed writes; deliberately avoid shutdown checkpoints by stepping down to follower; reopen without checkpoints; recreate/checkpoint after deferred no-checkpoint startup; open as follower without checkpoint metadata; and run a multi-table sequence with size growth and negative deltas from deletes.

State and persistence behavior: the core persistent field is shared metadata `database_size` relative to btree checkpoint sizes plus fixed overhead. Some paths intentionally leave database size and checkpoint sizes at zero to ensure verification skips comparison until there is a meaningful checkpoint/pickup.

Dependencies/integration points: disaggregated metadata verification path, checkpoint size accounting, startup verify, follower open behavior, and metadata update logic across table changes.

Risks: large data counts make runtime heavier. Tests rely on verify skipping in zero/no-pickup cases rather than directly asserting internal counters, so log/debug regressions could be missed unless they become verify failures.

Test signals: pass means metadata database-size accounting matches checkpoint sizes when applicable and avoids false mismatch checks when no checkpoint or pickup has populated the accounting state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint10.py

Purpose: stress-tests follower cursors when a new leader checkpoint is applied while the cursor is actively scanning. It focuses on monotonic ordering, bounds preservation, tombstone handling, completeness, and the `layered_curs_reopen_stable` statistic.

Important APIs/types/functions: helper methods format keys/values, insert/remove on leader/follower, `checkpoint_and_advance`, read follower stats, and start read-timestamp transactions. Uses `wiredtiger.stat.conn.layered_curs_reopen_stable`, cursor `next`, `prev`, `bound`, `reset`, and read timestamps.

Control flow: setup creates leader and follower connections and matching layered tables. Tests build combinations of checkpointed leader data and local follower ingest data, begin read-timestamp transactions, position cursors, scan partway, then insert more leader data and advance the follower checkpoint mid-scan. Variants cover forward/backward scans, bounded scans, follower tombstones, multiple checkpoint advances, and a restart-like continued scan after a key is removed and a new read timestamp is used.

State and persistence behavior: data is split between stable checkpoint content and follower ingest/local updates. Read timestamps determine visibility, while checkpoint pickup may reopen the stable side under an active cursor. Tombstones must remain hidden and order must not change.

Dependencies/integration points: cursor layering logic, follower checkpoint pickup, stable cursor reopening, transaction timestamp visibility, bounds, and tombstone reconciliation.

Risks: mid-scan switching is sensitive to exact cursor state. Some tests assert at least one statistic increment, so stat semantics changes can break tests even if behavior remains correct.

Test signals: pass indicates active follower scans survive checkpoint advances without skipped, duplicated, deleted, or out-of-order keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint11.py

Purpose: verifies a follower can pick up multiple checkpoints for the same layered table and read the latest values after each pickup. It includes a `debug_mode=(cursor_copy=true)` variant to catch metadata cursor value lifetime/use-after-free issues under sanitizers.

Important APIs/types/functions: uses `follower_conn_config`, `insert_data`, `check_data`, `disagg_advance_checkpoint`, `gen_disagg_storages`, `make_scenarios`, and optional `debug_mode=(cursor_copy=true)`.

Control flow: leader creates a layered table, writes `v1-` values, and checkpoints. A follower opens and picks up checkpoint 1, then verifies all rows. The leader writes `v2-` values and checkpoints; follower advances and verifies replacement values. A third `v3-` round repeats the same path to ensure repeated updates remain correct.

State and persistence behavior: table content is overwritten in-place across checkpoints. Follower local metadata is first inserted, then updated on later checkpoint pickups. The cursor-copy scenario stresses that metadata strings used during pickup are not referenced after their cursor buffers become invalid.

Dependencies/integration points: follower checkpoint pickup, local metadata insertion/update, shared metadata parsing, and debug cursor-copy mode.

Risks: fixed 100-row coverage is functional but not broad for page layout; the test targets metadata correctness more than storage scaling.

Test signals: pass means repeated follower pickup for one table returns latest data and remains valid when cursor values are copied/freed differently.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint12.py

Purpose: verifies startup database-size verification is deferred until a follower actually picks up checkpoint metadata.

Important APIs/types/functions: `conn_config` enables verbose verify and leader role. `_follower_config` builds `verify_metadata=true` follower configs with optional `checkpoint_meta`. The test uses `disagg_get_complete_checkpoint_meta`, role reconfiguration, `close_conn`, `open_conn`, `reopen_conn`, stdout regex guards, and `ignoreStdoutPattern`.

Control flow: the leader creates data, checkpoints, and captures checkpoint metadata. It steps down before close to avoid a shutdown checkpoint, then opens as follower without checkpoint metadata under a custom stdout assertion that database-size verification does not report checkpoint-size comparison. It then reopens as follower with checkpoint metadata and expects a verify log indicating the checkpoint-size branch ran. Teardown verify verbosity is ignored.

State and persistence behavior: shared checkpoint metadata exists, but follower startup without metadata must not populate enough state to compare database size. Supplying metadata should trigger pickup and then run the comparison.

Dependencies/integration points: startup open path, follower checkpoint pickup, `verify_metadata=true`, verbose verify logging, and disaggregated database-size verification.

Risks: the test is log-pattern sensitive. It validates branch execution by stdout, not by a direct API counter.

Test signals: pass means startup verify avoids false positives on no-pickup follower opens and activates once checkpoint metadata is supplied.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint13.py

Purpose: tests the materialization frontier behavior in disaggregated storage, ensuring data remains readable when the last materialized LSN is set behind the newest checkpoint LSN.

Important APIs/types/functions: uses `conn.get_page_log`, page-log APIs `pl_get_last_lsn`, `pl_set_last_materialized_lsn`, connection `reconfigure(disaggregated=(last_materialized_lsn=...))`, debug cursor config `debug=(release_evict)`, and a shared-table scenario using `block_manager=disagg,log=(enabled=false)`.

Control flow: the test sets stable timestamp 1, obtains the page log, steps up to leader, creates a shared disaggregated table, writes value `b`, checkpoints, records checkpoint 1 LSN, writes value `c`, checkpoints, and records checkpoint 2 LSN. It sets the materialized LSN back to checkpoint 1, reconfigures the connection with that frontier, forces eviction through a debug cursor, then rereads the row expecting the latest value `c`.

State and persistence behavior: persistent state includes page-log records, checkpoint LSNs, and last-materialized LSN. The test confirms that materialization frontier configuration does not make the latest checkpoint data unreadable after eviction.

Dependencies/integration points: direct page-log extension, disaggregated block manager, eviction/reconciliation, and materialization frontier reconfiguration.

Risks: single-key coverage narrows page-shape diversity. It relies on debug eviction successfully forcing a reload path.

Test signals: pass indicates eviction/read can navigate page-log materialization state and return the newest checkpointed value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint14.py

Purpose: ensures follower reads do not access pages that were freed by earlier leader checkpoints in a layered/disaggregated stable file.

Important APIs/types/functions: uses verbose block/read logging, `wiredtiger.stat.conn.disagg_block_page_discard`, filesystem reading of `stdout.txt`, follower `disagg_advance_checkpoint`, and `verifyUntilSuccess`.

Control flow: the leader creates a layered table, inserts 10,000 rows, checkpoints, updates every even key, checkpoints, updates every hundredth key, and checkpoints. It parses `stdout.txt` for `WT_VERB_BLOCK` `block free` lines for the stable file, records freed page IDs, asserts no page freed twice, and checks discard stat increased. It opens a follower with read verbosity, advances checkpoint, scans all rows, then parses read log lines to assert no read page ID was previously freed.

State and persistence behavior: state spans stable file page IDs, freed-page tracking, and follower-visible row count. The test confirms block-free metadata is honored by follower reads after checkpoint pickup.

Dependencies/integration points: verbose logging format, disaggregated block free/discard logic, follower stable reads, statistics, and layered verify.

Risks: strongly coupled to stdout log text and page_id formatting. It also assumes the workload generates frees and follower reads enough stable pages.

Test signals: pass means pages are not double-freed, discard stats move, follower sees all records, and no freed stable page is read.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint15.py

Purpose: validates checkpoint timestamp publication and follower visibility across layered-prefix, table-with-layered-type, and shared disaggregated table configurations.

Important APIs/types/functions: uses `disagg_get_complete_checkpoint_ext`, `disagg_advance_checkpoint`, `query_timestamp('get=last_checkpoint')`, timestamped transactions, and scenarios for `layered:`, `table:` with `block_manager=disagg,type=layered`, and shared `block_manager=disagg,log=(enabled=false)`.

Control flow: phase 1 writes all rows at timestamp 100, sets stable 100, checkpoints, verifies checkpoint timestamp, opens follower, advances, checks follower last checkpoint timestamp and all values. Phase 2 updates every 50th row at timestamp 200, checkpoints at stable 200, advances follower, and verifies mixed old/new values. Phase 3 updates every 25th row at timestamp 300 but checkpoints at stable 250, advances follower, and verifies timestamp-300 changes are not visible. It then advances leader stable timestamp to include all data for clean teardown.

State and persistence behavior: stable timestamp, commit timestamp, checkpoint timestamp, and follower-visible values are the key state. The third phase confirms checkpoint content follows stable timestamp rather than latest committed timestamp.

Dependencies/integration points: timestamp visibility, disaggregated checkpoint metadata, follower pickup, multiple table configuration styles.

Risks: high row count across scenario matrix increases runtime. The test assumes timestamped visibility semantics are identical across layered and shared modes.

Test signals: pass proves checkpoint timestamps match stable timestamps and followers see only data stable at the checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint16.py

Purpose: verifies picking up a checkpoint that does not change table file metadata does not rewrite follower local file metadata, while a later data-changing checkpoint does.

Important APIs/types/functions: helper methods `insert_data`, `check_data`, `get_stat`, `assertStatEqual`, `assertStatGreater`; statistics `stat.conn.disagg_pick_up_file_meta_inserted` and `stat.conn.disagg_pick_up_file_meta_updated`; `disagg_advance_checkpoint`.

Control flow: the leader creates data at timestamp 10 and checkpoints. A follower opens and advances: data is checked, inserted stat must increase, updated stat remains zero. The leader advances stable timestamp to 15 and checkpoints without table changes; follower advances and should see same data with no new inserts or updates. Finally leader writes `v2-` data at timestamp 20, checkpoints, follower advances, data changes, inserts remain unchanged, and updated stat becomes greater than zero.

State and persistence behavior: separates metadata insertion for new follower files from metadata update for changed file metadata. Stable timestamp-only checkpoints should not cause file metadata churn.

Dependencies/integration points: follower checkpoint pickup diffing, file metadata stats, async stat propagation, and precise checkpoint behavior.

Risks: retry helpers account for asynchronous stats, but stat naming/semantics are part of the test contract. Data writes are full-table overwrites, not sparse updates.

Test signals: pass means idempotent/same-file metadata pickup avoids unnecessary metadata writes, and changed checkpoints still update metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config01.py

Purpose: verifies layered table metadata disables logging even when the connection has logging enabled.

Important APIs/types/functions: `test_layered_config01` uses `disagg_test_class`, `gen_disagg_storages`, `make_scenarios`, `session.create`, and a `metadata:create` cursor. It covers both explicit `layered:` URI creation and `table:` creation with `block_manager=disagg,type=layered`.

Control flow: the test loops over two layered URIs, appending disaggregated layered configuration for the `table:` URI, creates both tables, then calls `check_metadata_cursor`. That helper opens `metadata:create`, searches each URI, and asserts the metadata value contains `log=(enabled=false)`.

State and persistence behavior: persistent state is the table metadata string created by WiredTiger. It confirms local logging configuration is overridden/normalized for layered tables.

Dependencies/integration points: metadata cursor behavior, layered create configuration normalization, and disaggregated storage scenario setup.

Risks: string containment is simple and may not detect duplicate/conflicting log entries if metadata formatting changes. It does not write/read table data.

Test signals: pass means both layered URI styles record logging disabled in create metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config02.py

Purpose: intended to test disaggregated storage with block cache, especially long delta chains and cached page reuse, but currently skips in `early_setup` due to FIXME-WT-15663.

Important APIs/types/functions: when enabled, it would use block cache config `block_cache=(enabled=true,type="dram",size=256MB)`, `stat.conn.block_cache_blocks_removed`, `cache_read_leaf`, `cache_pages_requested_leaf`, debug eviction `debug=(release_evict)`, timestamped checkpoints, and scenarios for `layered:` and shared `table:` prefixes.

Control flow: skipped before execution. The dormant body creates a table, writes 500 rows, checkpoints, records block-cache removal stats, repeatedly updates one key across 10 checkpoints to build deltas, evicts and rereads the key, evicts again, verifies block-cache removal increased, then rereads while checking leaf reads do not increase but page requests do.

State and persistence behavior: persistent state would be checkpointed deltas and block-cache contents after eviction/reload. The expected behavior is that rereads can be satisfied from block cache.

Dependencies/integration points: block cache, disaggregated page reads, eviction, layered/shared table creation, stats.

Risks: currently no behavioral signal because it is skipped. If re-enabled, stat expectations may be sensitive to cache implementation and eviction timing.

Test signals: active signal is only the skip. Future pass would prove block cache integration with disaggregated pages and delta chains.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config03.py

Purpose: ensures disaggregated/layered reconciliation does not generate overflow keys or values even with large logical keys/values and small `leaf_key_max`/`leaf_value_max` settings.

Important APIs/types/functions: uses `stat.conn.rec_overflow_key_leaf`, `stat.conn.rec_overflow_value`, random string generation, timestamped per-key transactions, checkpointing, and scenarios for `layered:` and shared `table:` with `block_manager=disagg,log=(enabled=false)`.

Control flow: the test creates a table with `leaf_key_max=256,leaf_value_max=256`, inserts 500 large keys with small values at timestamp 100, and asserts overflow stats remain zero before checkpoint. It checkpoints at stable 100, then performs several large-value updates at timestamp 200, checkpoints at stable 200, and asserts both overflow stats remain zero again.

State and persistence behavior: the state under test is reconciliation output and checkpointed page encoding for disaggregated storage. Large application values should not use standard overflow item machinery in layered storage.

Dependencies/integration points: reconciliation, page encoding, disaggregated block manager, statistics, timestamped checkpointing.

Risks: random strings are not seeded, so exact key/value contents vary; however only overflow counters are asserted. It does not verify row values after restart.

Test signals: pass means both initial large-key writes and later large-value updates avoid overflow key/value generation in the tested configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config04.py

Purpose: verifies creating a layered table with logging explicitly enabled is rejected with a clear error.

Important APIs/types/functions: uses `assertRaisesWithMessage`, `wiredtiger.WiredTigerError`, `session.create`, and disaggregated scenarios. Connection role is leader.

Control flow: the single test attempts to create `layered:test_layered_config04` with `key_format=S,value_format=S,log=(enabled=true)` and expects a `Logging is not supported for layered` error.

State and persistence behavior: no table should be created and no durable layered metadata should be accepted for an unsupported logged configuration.

Dependencies/integration points: configuration validation for layered tables, error propagation through Python API, and disaggregated test setup.

Risks: scenario generator name references `test_layered_eviction02`, likely harmless but confusing for test identity. The assertion is regex/string dependent.

Test signals: pass means unsupported logged layered tables fail at create time with the expected diagnostic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config05.py

Purpose: tests disaggregated address-cookie version upgrade/downgrade compatibility across checkpoint pickup and continued writes.

Important APIs/types/functions: scenarios cover `disagg_address_cookie_upgrade` values `none`, `compatible`, `incompatible` and optional field true/false. Uses `debug_mode`, `restart_without_local_files`, role reconfiguration, `disagg_get_complete_checkpoint_meta`, checkpoint pickup via reconfigure, and expected `Unsupported disaggregated address cookie version` failures.

Control flow: leader writes 2,000 large values and checkpoints. It restarts with newer address-cookie debug settings and verifies all data. After step-up, it modifies 100 keys and checkpoints. It then steps down, captures checkpoint metadata, restarts with older `disagg_address_cookie_upgrade=none`, and tries to pick up metadata: compatible modes must succeed; incompatible must raise. Compatible paths verify data, step up, modify another range, checkpoint, then restart with newer settings and verify final data.

State and persistence behavior: state includes encoded address cookies in checkpoint metadata/pages and table values across version transitions. Compatibility controls whether older code can interpret newer cookies.

Dependencies/integration points: debug compatibility flags, checkpoint metadata pickup, page address cookie encoding, restart-without-local-files, and disaggregated role changes.

Risks: matrix expansion is significant. There is a subtle timestamp reuse in later commits, but the test focuses on compatibility and data reads.

Test signals: pass means compatible cookie formats round-trip across old/new nodes, incompatible formats are rejected, and compatible nodes can continue writing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config06.py

Purpose: validates rollback-to-stable behavior in a disaggregated PALite setup: recovery RTS after crash should not roll back disaggregated storage, while explicit runtime RTS still should.

Important APIs/types/functions: uses `SimpleDataSet`, `simulate_crash_restart`, custom `conn_extensions` loading `page_log/palite`, manual `early_setup` creating shared `kv_home` symlink for follower, `skip_for_hook("tiered")`, and `rollback_to_stable`.

Control flow: it creates and populates a normal table under disaggregated PALite config, updates three keys at commit timestamp 30, sets stable timestamp 20, checkpoints, and simulates crash/restart. After restart, it verifies recovery did not roll back the timestamp-30 updates. It then calls runtime `rollback_to_stable` and verifies the same keys return to original dataset values.

State and persistence behavior: distinguishes crash recovery state from runtime rollback state. Disaggregated storage should keep post-stable writes after crash recovery in this context, but runtime RTS remains functional.

Dependencies/integration points: PALite page log extension, crash restart helper, timestamped updates, WiredTiger recovery, and rollback-to-stable.

Risks: no `disagg_test_class` decorator; setup is manual and platform-sensitive around symlinks. It skips tiered hook and handles Windows extension availability.

Test signals: pass means recovery RTS is disabled/benign for disaggregated context while explicit RTS still rewinds unstable updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config07.py

Purpose: directly exercises internal page-log APIs used by disaggregated storage, independent of table operations.

Important APIs/types/functions: class mixes in `DisaggConfigMixin`; uses `conn.get_page_log('palite')`, `PageLogCompleteCheckpointArgs`, `pl_complete_checkpoint`, `pl_open_handle`, `PageLogPutArgs`, `WT_PAGE_LOG_DELTA`, `plh_put`, `PageLogGetArgs`, `plh_get`, `PageLogDiscardArgs`, `plh_discard`, and `terminate`.

Control flow: it completes a synthetic checkpoint, opens a page-log handle, writes full and delta records for page 20 and page 21, then writes a second delta for page 20 chained to the previous delta. It reads page 20 and page 21 at specific LSNs and asserts the returned full+delta lists match expected byte payloads. Finally it discards page 20 with base/backlink LSNs and asserts the discard operation receives a later LSN.

State and persistence behavior: page-log state is identified by file/page IDs, LSNs, base LSNs, backlink LSNs, and delta flags. The test validates chaining and retrieval order plus discard record allocation.

Dependencies/integration points: PALite/page-log extension plumbing, WiredTiger Python page-log bindings, disaggregated helper configuration.

Risks: direct internal API test; application-facing behavior is not covered. Incorrect LSN state would fail assertions or retrieval ordering.

Test signals: pass means basic complete-checkpoint, put/get delta chains, and discard APIs work through Python bindings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config08.py

Purpose: verifies compaction APIs are rejected in disaggregated storage mode with clear `Operation not supported` errors.

Important APIs/types/functions: uses `DisaggConfigMixin`, `session.compact`, `assertRaisesWithMessage`, `wiredtiger.WiredTigerError`, and `skip_for_hook("tiered")` because tiered tables do not support compaction.

Control flow: under a disaggregated connection, the test calls `session.compact('table:test_layered_config08')` and `session.compact(None, 'background=true')`, expecting both to raise unsupported-operation errors.

State and persistence behavior: no durable data is created. The test validates API gating before any compaction state is started.

Dependencies/integration points: disaggregated connection configuration, compact API dispatch, background compact validation, and error propagation.

Risks: the named table is not created; the intended signal is that disaggregated mode rejects compact before object-specific lookup. If validation order changes, the test may need to create a table first.

Test signals: pass means both targeted and background compaction are disabled in disaggregated mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config09.py

Purpose: verifies tiered storage worker startup and tiered object/table creation are disabled in disaggregated storage mode for both leader and follower roles.

Important APIs/types/functions: uses `DisaggConfigMixin`, `disagg_test_class`, role scenarios `leader`/`follower`, URI prefixes `tiered:`, `tier:`, and `object:`, verbose tiered logging, `captureout.checkAdditionalPattern`, and `assertRaisesWithMessage`.

Control flow: connection config enables disaggregated role and `lose_all_my_data=true`. One test checks expected stdout indicating tiered storage was not started because disaggregated storage is active. The create test checks the same message, then attempts to create an object with the selected tiered prefix and expects `Operation not supported`.

State and persistence behavior: no tiered metadata should be created and no tiered worker should run. State under test is startup service gating and create rejection.

Dependencies/integration points: tiered storage subsystem startup, URI-prefix create dispatch, disaggregated mode configuration, and verbose logging.

Risks: log text dependency. Scenario matrix increases coverage but the create body only checks unsupported result, not absence of partial metadata.

Test signals: pass means disaggregated mode suppresses tiered worker startup and rejects tiered/tier/object creates across roles.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config10.py

Purpose: tests `disaggregated=(storage_tier=cold)` table configuration validation and cold-tier read/write statistics.

Important APIs/types/functions: uses `DisaggConfigMixin`, `validate_config`, `reopen_conn`, metadata cursor reads, stats `stat.conn.disagg_block_put_cold` and `stat.conn.disagg_block_get_cold`, `verifyUntilSuccess`, and leader role reconfiguration.

Control flow: `test_disagg_storage_tier` tries invalid empty storage tier, no storage tier, valid `cold`, and invalid typo `coldd`, asserting metadata string presence/absence and invalid-argument errors. `test_cold_write` creates a cold table, checks cold put stat zero, writes/checkpoints 1,000 rows, and asserts cold puts increased. `test_cold_read` creates and checkpoints a cold table, asserts cold gets zero, verifies the table to force page reads, and asserts cold gets increased.

State and persistence behavior: table metadata persists optional `storage_tier=cold` only when configured. Cold tier stats prove disaggregated block operations are routed to cold storage for checkpointed pages and verify reads.

Dependencies/integration points: table config parser, metadata persistence, disaggregated block manager, cold tier stats, and verify.

Risks: stat assertions assume no earlier cold operations in the connection. Error checks rely on stderr pattern `Invalid argument`.

Test signals: pass means storage-tier config is validated/persisted and cold-tier read/write accounting is exercised.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config11.py

Purpose: intended to test read/write behavior across leader-to-follower step-down with compression and encryption combinations, but currently skips because step-down is unsupported.

Important APIs/types/functions: uses `DisaggConfigMixin`, scenario matrices for encryptors `none`/`rotn` and compressors `none`/`snappy`, extension loading for compressors/encryptors, transaction sync fsync, and disaggregated storage scenarios.

Control flow: the only test immediately calls `skipTest('Step-down is not supported yet.')`. Dormant logic would create a layered table with selected block compressor, insert 10,000 rows, checkpoint, reopen as follower, and verify all rows.

State and persistence behavior: if enabled, it would validate compressed/encrypted disaggregated checkpoint persistence through role transition. Currently no table state is created.

Dependencies/integration points: compressor/encryptor extension loading, page-log/disaggregated configuration, checkpointing, and follower reopen behavior.

Risks: currently no runtime behavioral coverage. When step-down support arrives, the dormant code may need checkpoint metadata pickup or updated role-transition semantics.

Test signals: active signal is skip only; future pass would show encrypted/compressed layered data can be read after step-down/reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config12.py

Purpose: validates unsupported disaggregated/layered configurations return clear errors: read-only disaggregated connections and custom collators on layered tables.

Important APIs/types/functions: uses `conn_extensions` to load `collators/reverse` plus disagg extensions, `wiredtiger_open`, `assertRaisesWithMessage`, `session.create`, `session.open_cursor`, and table drop cleanup.

Control flow: `test_readonly` closes the normal connection and attempts to open the home with `readonly=true` and disaggregated leader config, expecting an error that disaggregated storage is not supported with read-only connections, then reopens normally. `test_reverse_collator` creates a layered table with `collator=reverse`, expects cursor open to fail with `layered tables do not support custom collators`, then drops the table so layered verify teardown does not fail on the unsupported configuration.

State and persistence behavior: read-only open should not create usable disaggregated state. The collator test writes metadata successfully but rejects dhandle/cursor open, then removes the metadata.

Dependencies/integration points: connection open validation, collator extension loading, layered dhandle open checks, and teardown verify.

Risks: behavior intentionally permits create but rejects cursor for collator case; if validation moves earlier, test expectations must change.

Test signals: pass means these unsupported paths produce deterministic user-facing errors and leave teardown clean.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config13.py

Purpose: tests deletion of local files on restart in disaggregated mode, ensuring layered shared data survives through checkpoint metadata while local non-disaggregated table data is removed.

Important APIs/types/functions: overrides `wiredtiger_open` to ensure log directory exists, patches `helper_disagg.disagg_ignore_expected_output`, uses role reconfigure, `disagg_get_complete_checkpoint_meta`, `close_conn`, `open_conn`, expected stdout `Removing local file`, and checkpoint metadata pickup via reconfigure.

Control flow: the node steps up to leader, creates one layered table and one local table, writes values `aaa`, `bbb`, `ccc` to both across checkpoints, captures checkpoint metadata, closes, then opens without explicit metadata and expects local file removal logging. It reconfigures with captured checkpoint metadata, steps up to leader, verifies layered table value is `ccc`, and asserts opening the local table fails.

State and persistence behavior: shared disaggregated table state persists via checkpoint metadata; local table files/metadata are intentionally discarded under `lose_all_my_data=true` restart behavior. Logging is enabled to exercise local log paths while deleting local data.

Dependencies/integration points: restart cleanup, local file removal, checkpoint metadata pickup, role step-up, and helper output filtering.

Risks: stdout pattern dependency. It tests one key per table but multiple checkpoints.

Test signals: pass means restart cleanup removes local files while checkpoint pickup restores shared layered data.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_config14.py

Purpose: comprehensive restart-without-local-files test for layered/shared metadata reconstruction, ingest/stable metadata presence, reads before/after step-up, continued writes, checkpointing, and a second restart.

Important APIs/types/functions: helpers `check_metadata_cursor` and `check_shared_metadata`; uses `metadata:` cursor, `file:WiredTigerShared.wt_stable` cursor, `restart_without_local_files(pickup_checkpoint=False)`, checkpoint metadata reconfigure, role reconfigure, and mixed URI sets: layered table URIs, disagg file URI, and disagg table URI.

Control flow: leader creates all URIs with appropriate disaggregated/log config, writes 500 rows each, checkpoints, and records checkpoint metadata. Restart 1 steps down, restarts without local files and without pickup, verifies no shared URIs in local metadata, picks up metadata, verifies shared/local metadata including ingest files, reads all tables before and after step-up, updates selected URIs, verifies leader reads before checkpoint, checkpoints, verifies metadata and values, steps down, restarts again without local files, picks up latest metadata, steps up, and verifies metadata and values again.

State and persistence behavior: exercises shared metadata table content, local metadata reconstruction, ingest/stable file metadata, table data, and updates across multiple restarts. Some URIs are updated while others must remain unchanged.

Dependencies/integration points: checkpoint metadata pickup, shared metadata table, local metadata population, restart cleanup, role transition, and layered/shared table handling.

Risks: long scenario with many assertions; failure diagnosis may require locating which restart/metadata phase broke. Set-derived `same_uris` can produce nondeterministic iteration order but assertions are order-independent.

Test signals: pass means a node can start without local files, pick up shared disaggregated metadata, serve reads, become leader, write/checkpoint, and repeat restart successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_config14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor01.py

Purpose: broad cursor operation regression suite for layered tables over leader and follower, covering scan order and positioning after inserts, updates, removes, checkpoints, and follower checkpoint advance.

Important APIs/types/functions: uses `Oplog` helper from `helper_disagg`, position helpers for `search`, `search_near`, `next`, and `prev`, scenarios over those positioning functions, `setup_follower`, `create_table`, `oplog_apply_traffic`, `check_cursor_ops`, `checkpoint_and_advance`, and cursor `next`/`prev` traversal.

Control flow: setup opens a follower connection and creates matching leader/follower layered tables. The Oplog applies batches of inserts plus optional updates/removes to both sessions and maintains an expected table snapshot. `check_cursor_ops` sorts expected keys lexicographically, scans forward/backward on both leader and follower, and verifies positioning at start/quarter/mid/three-quarter/end followed by forward and backward iteration. Test variants run empty tables, populated tables, update percentages, remove percentages, combined update/remove cases, and offset cases.

State and persistence behavior: state is mirrored between leader and follower local tables via Oplog operations and then through leader checkpoint/follower advance. Expected state is maintained in Oplog rather than by reading back from one side.

Dependencies/integration points: layered cursor search/iteration, follower checkpoint pickup, Oplog helper semantics, and disaggregated storage scenarios.

Risks: two test method names for `test_populated_tables_with_updates_20_percent` appear, so the later definition overrides the earlier in Python. Also some offset attributes use `updates_offset` while helper reads `update_offset`, reducing intended offset coverage.

Test signals: pass means cursor positioning and bidirectional scans match expected logical table content before and after checkpoint pickup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor02.py

Purpose: verifies `cursor.modify` remains valid on a follower after reopening from a checkpoint, for both item (`u`) and string (`S`) value formats.

Important APIs/types/functions: uses `DisaggConfigMixin`, PALite page log config, `modify_utils.create_value`, `modify_utils.create_mods`, deterministic `random.Random(42)`, `cursor.modify`, timestamped commits, and `reopen_conn` with `checkpoint_meta`.

Control flow: leader creates a layered table with selected value format, inserts 1,000 random large values, stores originals, and checkpoints. It reopens the same home as follower with the latest checkpoint metadata. For each key, it computes modifications from the original value, applies `cursor.modify` in a timestamped transaction, commits, and asserts reading the key returns the expected new value.

State and persistence behavior: base values are checkpointed; modifies are applied after checkpoint pickup on follower state. The test verifies modify can reconstruct from the checkpointed base value and produce correct current values.

Dependencies/integration points: disaggregated checkpoint pickup, modify vector application, item/string value formats, PALite page log, and modify utility generation.

Risks: variables `size`, `repeats`, `nmods`, and `maxdiff` used during modification are the last generated values from the insert loop, not per-key values; `create_mods` still uses each key's old value, but the distribution is less varied than it appears.

Test signals: pass means follower-side modify after checkpoint pickup works for both raw item and string formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor03.py

Purpose: minimal smoke test for layered table creation and cursor open/close.

Important APIs/types/functions: uses `disagg_test_class`, connection config with `verbose=[layered]`, `disaggregated=(role="leader")`, and `lose_all_my_data=true`; calls `session.create`, `session.open_cursor`, and `cursor.close`.

Control flow: creates a `layered:` table with string key/value formats, opens a cursor, then closes it.

State and persistence behavior: only table metadata and cursor handle lifecycle are exercised. No rows are inserted and no checkpoint is taken explicitly.

Dependencies/integration points: layered URI create path, disaggregated leader setup, cursor open path, and verbose layered logging.

Risks: very narrow coverage; it catches basic open/create regressions but not read/write or persistence issues.

Test signals: pass means a layered table can be created and opened with a cursor under the configured disaggregated leader connection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor04.py

Purpose: basic layered cursor insert/read/traversal smoke test.

Important APIs/types/functions: uses `disagg_test_class`, layered verbose leader config, `session.create`, `open_cursor`, direct cursor item assignment, `set_key`, `search`, `get_value`, `reset`, `next`, `prev`, and close/reopen cursor flow.

Control flow: creates a layered table, opens a cursor, inserts three string key/value pairs, searches for `Hello`, reads value via both `get_value` and `cursor["Hello"]`, scans forward, scans backward, closes, reopens a cursor, and scans forward again.

State and persistence behavior: verifies in-memory/current-session layered cursor state for inserted rows and cursor traversal. No explicit checkpoint or follower pickup is used.

Dependencies/integration points: layered insert path, search path, bidirectional cursor iteration, cursor reset/reopen lifecycle, and disaggregated leader setup.

Risks: printed traversal is not asserted beyond lack of error, and the final reopened cursor is not closed in the source. It does not check exact scan order with assertions.

Test signals: pass means basic insert/search/scan operations on a leader layered cursor do not fail and return at least the searched value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor05.py

Purpose: extensive `search_near` and iteration edge-case suite for follower layered cursors combining stable checkpoint data, local ingest writes, and tombstones.

Important APIs/types/functions: helper methods format keys/values, insert/remove on arbitrary session, `insert_stable` with leader checkpoint and follower advance, `insert_ingest`, `remove_ingest`, search-near check helpers, notfound checks, either-neighbor checks, and sorted forward/backward assertions. Uses cursor `search_near`, `next`, `prev`, and bounds.

Control flow: setup creates leader/follower layered tables. Tests cover empty tables, ingest-only odd keys, stable-only even keys, split stable/ingest complete keyspace, opposite-side stable/local neighbors, far neighbors, multiple local/stable neighbor arrangements, all-larger/all-smaller cases, exact key tombstoned from stable or ingest-only state, all-deleted tables, cross-table tombstone overrides, iteration after search_near, consecutive tombstone ranges, full forward/backward scans of interleaved data, local overrides of stable values, beyond-max searches, and bounded search/next through tombstones.

State and persistence behavior: stable data is checkpointed through leader and visible after follower pickup; ingest data and tombstones are follower-local. Correct behavior requires merging these sources while hiding deleted keys and preserving sorted cursor movement.

Dependencies/integration points: layered cursor merge logic, `search_near` return-code semantics (`-1`, `0`, `1`, `WT_NOTFOUND`), tombstone visibility, bounds, follower checkpoint pickup.

Risks: where both adjacent neighbors are valid, tests allow either result, matching WiredTiger semantics. The suite is broad but focused on string-formatted numeric keys.

Test signals: pass means `search_near` handles stable/ingest boundaries, tombstones, empty sets, and subsequent iteration without returning deleted or out-of-order keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor06.py

Purpose: verifies `next_random=true` cursors work on layered tables with data and return notfound on empty tables.

Important APIs/types/functions: uses `session.open_cursor(..., "next_random=true")`, leader checkpointing, follower reopen with `checkpoint_meta`, `wiredtiger.WT_NOTFOUND`, and disaggregated scenarios.

Control flow: `test_layered_random_cursor` creates a layered table, inserts 1,000 rows, checkpoints, inserts another 1,000 rows without checkpointing, opens a random cursor on the leader and expects `next()` success, then reopens as follower with checkpoint metadata and expects random cursor `next()` success there too. `test_empty_table` creates an empty layered table and expects random cursor `next()` to return `WT_NOTFOUND`.

State and persistence behavior: leader random cursor sees current table with both stable and newer data; follower reopen sees checkpointed data through metadata. Empty table state should not fabricate a row.

Dependencies/integration points: random cursor support, checkpoint metadata pickup, layered cursor implementation, and disaggregated leader/follower roles.

Risks: only checks success/notfound, not randomness distribution or which key is returned. Follower sees only checkpointed rows, but the test does not assert that boundary.

Test signals: pass means random cursors are supported for non-empty layered data on leader and follower and behave correctly for empty tables.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor07.py

Purpose: basic test for `cursor.modify` on layered tables.

Important APIs/types/functions: uses `wiredtiger.Modify`, `cursor.modify`, transactions, direct cursor reads, and disaggregated leader scenario setup.

Control flow: creates a layered table, inserts a long base value for key `1`, then in a transaction applies a modify that appends `A` at offset 130 and asserts `get_value()` returns base plus `A`. It commits and verifies direct read. It then applies a second modify appending `B` at offset 131 and verifies base plus `AB` both before and after commit.

State and persistence behavior: state is an update chain containing a full value followed by modify records. No explicit checkpoint/restart is used, so this targets current-session modify semantics.

Dependencies/integration points: layered update/modify support, value reconstruction, transaction commit, and Python `wiredtiger.Modify` binding.

Risks: only one key and append-style modifications are tested. No timestamp, checkpoint, follower, or eviction behavior is covered.

Test signals: pass means layered cursors can apply sequential modifies and reconstruct the expected value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor08.py

Purpose: verifies duplicate-key insert handling for layered cursors opened with `overwrite=false` under both leader and follower roles.

Important APIs/types/functions: scenarios combine disaggregated storage and role `leader`/`follower`; uses `open_cursor(..., 'overwrite=false')`, `cursor.insert`, `assertRaisesHavingMessage`, and duplicate-key error `WT_DUPLICATE_KEY`.

Control flow: creates a layered table, inserts keys `0` through `99` in timestamped transactions through an overwrite-false cursor, then sets key `10` and a different value `20`, calls `insert`, expects duplicate-key error, and asserts `get_value()` is the existing value `10`.

State and persistence behavior: table contains committed rows. A failed duplicate insert should leave the cursor positioned with the existing on-disk/logical value, not the attempted replacement value.

Dependencies/integration points: layered insert path, overwrite-false semantics, duplicate-key error propagation, cursor value state after failed insert, role-specific behavior.

Risks: follower role permits local writes in this test configuration; it does not involve checkpoint pickup. All commits use the same timestamp.

Test signals: pass means duplicate insert returns the expected error and preserves/reloads existing value state on the cursor.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor09.py

Purpose: verifies cursor walking over checkpointed delta pages respects read timestamps and reconstructs updated values in both directions after reopen.

Important APIs/types/functions: uses data-source statistic `stat.dsrc.rec_page_delta_leaf`, timestamped transactions, stable timestamps, checkpoints, `reopen_conn`, read-timestamp transactions, and cursor `next`/`prev`.

Control flow: creates a layered table, inserts keys 1-99 mostly at timestamp 10, with key 50 at timestamp 20, sets stable 20 and checkpoints. It updates key 50 to `value2` at timestamp 30, sets stable 30, checkpoints, then asserts the data-source delta-page stat is greater than zero. After reopening, it reads at timestamp 30 and scans forward/backward expecting all 99 rows with key 50 as `value2`. It then reads at timestamp 10 and scans forward/backward expecting only timestamp-10 visible rows, count 98, all with original `value`.

State and persistence behavior: persistent checkpoint state includes a delta page from the update. Timestamp visibility excludes key 50 at timestamp 10 because it was inserted at timestamp 20.

Dependencies/integration points: delta reconciliation, timestamp visibility, reopen/recovery, forward/backward cursor traversal, and stats.

Risks: assumes workload generates at least one delta page. Cursor reuse across transactions depends on rollback/reset semantics from previous scans.

Test signals: pass means delta pages are generated and cursor walks reconstruct correct values/counts at different read timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor10.py

Purpose: tests layered cursor behavior around prepared update conflicts, especially preserving enough cursor/key state for retry or opposite-direction movement after `WT_PREPARE_CONFLICT`.

Important APIs/types/functions: uses `preserve_prepared=true`, `prepare_transaction`, `prepared_id_str`, commit/rollback scenarios, read timestamps, `cursor.search_near`, `next`, `prev`, `get_key`, and prepare conflict assertions.

Control flow: helper `setup_table_with_data` creates integer-key layered data and commits at timestamp 20. `prepare_key_in_separate_session` opens another session, writes a key, and prepares at timestamp 50. `test_search_near_key_preserved_on_prepare_conflict` searches near a prepared key 2, expects an error, checks key remains 2, then either commits and retries successfully or rolls back. `test_next_key_preserved_on_prepare_conflict` positions at key 1, `next()` hits prepared key 2, `get_key` requires key set, then `prev()` returns key 1; commit path then `next()` returns key 2. `test_prev_key_preserved_on_prepare_conflict` mirrors this from key 5 and prepared key 4.

State and persistence behavior: prepared updates are visible as conflicts to timestamp 60 readers until resolved. Cursor state after conflict must remain recoverable and directionally consistent.

Dependencies/integration points: prepared transaction engine, layered cursor search/iteration, transaction timestamps, error handling, and prepared commit/rollback resolution.

Risks: assertions use generic `WiredTigerError` for conflict rather than checking exact code/message in all cases. Commit path includes a `breakpoint()` call in one test, which may be harness-specific.

Test signals: pass means search_near/next/prev handle prepare conflicts without losing position semantics and can continue correctly after resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor11.py

Purpose: verifies removing a non-existent key from a layered table returns `WT_NOTFOUND`.

Important APIs/types/functions: uses `cursor.remove`, `wiredtiger.WT_NOTFOUND`, transactions, precise checkpoint follower configuration, and disaggregated scenarios.

Control flow: creates an integer-key layered table, opens a cursor, begins a transaction, sets key 1 without inserting it, asserts `cursor.remove()` returns `WT_NOTFOUND`, rolls back, and closes the cursor.

State and persistence behavior: table remains empty and the transaction is rolled back. The test validates absence handling without creating tombstones for missing keys.

Dependencies/integration points: layered remove path, notfound return semantics, transaction rollback, and follower-role local operation support.

Risks: minimal single-operation coverage. It does not test missing-key remove after checkpointed data or with tombstones.

Test signals: pass means delete of absent key returns the expected notfound code rather than succeeding or raising an unexpected error.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor12.py

Purpose: verifies follower cursors see correct data after checkpoint advances, including existing unpositioned cursors, updated/deleted keys, interleaved stable/ingest data, search_near changes, read timestamp visibility, bounds, tombstone persistence, and leader behavior.

Important APIs/types/functions: helpers format keys/values, insert/remove on leader and follower, `do_checkpoint`, `scan_keys`, `scan_kv`; uses `disagg_advance_checkpoint`, cursor `search`, `search_near`, `bound`, `reset`, timestamped transactions, and leader/follower connections.

Control flow: setup creates paired leader/follower layered tables. Tests cover: an existing reset cursor seeing all data after a checkpoint adds odd keys; updated values becoming visible after checkpoint; removed leader keys disappearing; positioned local-key cursor finding newly checkpointed data; interleaved even stable keys plus odd local/checkpointed keys; search_near becoming exact after a key is added in a later checkpoint; read timestamps seeing checkpoint 1 vs checkpoint 2 contents; bounds preserved/reapplied after reset and checkpoint; new data inside bounds appearing; local follower tombstones hiding keys across later checkpoint advances; and leader cursors seeing leader writes across checkpoints.

State and persistence behavior: stable checkpoint data, follower ingest writes, follower tombstones, bounds state, and read-timestamp visibility all interact. Several tests model production replication by applying leader operations to the follower ingest table before checkpoint pickup.

Dependencies/integration points: follower checkpoint pickup, layered cursor merge/reopen behavior, timestamp visibility, search/search_near, bounds, tombstones, and leader/follower role semantics.

Risks: some bounds tests reset and reapply bounds because reset clears bounds, so preservation is partly manual. `scan_kv` is defined but unused.

Test signals: pass means checkpoint advances update follower cursor visibility correctly without losing local deletes, bounds expectations, timestamp isolation, or leader current-state visibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor12.py -->
