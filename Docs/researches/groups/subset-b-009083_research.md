# subset-b-009083 Research

Grouped research for WiredTiger disaggregated layered follower, prepare, and schema tests. Each section preserves the original source path for source-tree-aligned split output.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower15.py

## Purpose

This test validates layered follower reads when a `MODIFY` update depends on an on-disk base value that may be garbage-collection eligible in the follower ingest tree. It covers both single-key and multi-key pages, cursor `next()` and `search()`, and the case where the base value must remain readable across its visibility window.

## Important APIs, Types, and Functions

The class is decorated with `disagg_test_class` and runs over `gen_disagg_storages(..., disagg_only=True)` scenarios. It configures leader and follower connections with `statistics=(all),precise_checkpoint=true` and `disaggregated=(role=...)`. Helpers create matching leader/follower layered tables, commit timestamped items, apply `wiredtiger.Modify`, set stable timestamps on both connections, checkpoint the leader, advance the follower checkpoint, and force follower eviction through a debug `release_evict_page` session.

## Control Flow

`setup_single_key_chain` creates a value at timestamp 10, optionally makes it orphanable by advancing stable to 11, applies a long modify at 20, writes a full replacement at 30, checkpoints, advances the follower, and evicts the key. The tests then read from the follower's ingest file URI at timestamps 15, 25, and 30. The multi-key setup places neighbors on the same page so the target key's modify reconstruction can be checked against neighboring data.

## State, Persistence, and Dependencies

The test persists update chains through stable timestamp movement, checkpoints, disaggregated checkpoint pickup, and forced eviction. It depends on `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`. It integrates with layered URI creation, ingest file cursor access, timestamped transactions, modify reconstruction, checkpoint metadata transfer, eviction, and `verifyLayered` teardown constraints.

## Risks and Test Signals

The main risk is reconstructing a modify against the wrong base: either a pruned base, a neighbor key's value, or an incorrectly visible base. The assertions check exact values, key order, neighbor survival preconditions, `WT_NOTFOUND` at scan end, and visibility at multiple read timestamps. The teardown advances stable and checkpoints to avoid verification failures from deliberately pinned timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower16.py

## Purpose

This test verifies lazy stable-cursor opening on a layered follower. Before the follower has picked up a checkpoint, operations must not open the stable tree. After checkpoint pickup, reads and non-overwrite writes should open stable, while default-overwrite insert/update operations should not.

## Important APIs, Types, and Functions

Top-level operation helpers implement `insert`, `update`, `search`, `search_near`, `next`, `prev`, `remove`, `reserve`, `modify`, and `largest_key`. Scenario dimensions combine operation type, cursor overwrite mode, and transaction end mode (`rollback`, `commit`, `survive`). `get_stat` reads connection statistics, especially `layered_curs_open_stable` and `layered_curs_reopen_stable`.

## Control Flow

The leader creates and populates a layered string-key table. A follower opens the same table and replays the initial writes into ingest. The test opens a follower cursor, performs the scenario operation before checkpoint pickup, and asserts stable-open count remains zero. It then timestamps and checkpoints the leader, advances the follower checkpoint, repeats the same operation, ends or preserves the transaction according to the scenario, and checks whether stable opened.

## State, Persistence, and Dependencies

The file depends on `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`. It uses timestamped transactions, follower ingest replay, disaggregated checkpoint transfer, cursor overwrite configuration, and connection statistics as persistent behavioral signals. `_insert_counter` avoids duplicate keys for non-overwrite insert scenarios.

## Risks and Test Signals

The test guards against premature stable cursor opening, missed stable opening after checkpoint pickup, and unnecessary stable reopen churn. A subtle risk is that operation semantics vary with overwrite and transaction state; the `opens_stable` predicate encodes the intended exception for overwrite insert/update. Strong signals are exact statistic assertions before and after checkpoint advancement across many cursor APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare01.py

## Purpose

This regression test covers WT-17257: forward iteration on a layered follower cursor after a prepared remove is rolled back. It ensures that a prepare conflict does not leave the cursor positioned such that stable keys are skipped.

## Important APIs, Types, and Functions

The class is a `disagg_test_class` with scenarios varying which stable keys receive prepared removes. `safe_next` converts a raised `WiredTigerError` containing `WT_PREPARE_CONFLICT` into the return code for direct assertion. The table is created as `type=layered` with `block_manager=disagg`.

## Control Flow

The leader writes scenario `stable_keys` at commit timestamp 100, advances stable to 200, checkpoints, and transfers the checkpoint to a follower. A follower prepare session removes `prepared_keys` in ingest and prepares at timestamp 300. A reader at timestamp 400 opens a layered cursor and expects the first `next()` to conflict. After the prepared transaction is rolled back, the same cursor continues iteration and must return every stable key in order.

## State, Persistence, and Dependencies

Persistent state includes stable checkpoint content on the leader and unresolved prepared tombstones on the follower ingest tree. The test depends on `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`, and integrates with prepared transactions, timestamped checkpoints, follower checkpoint pickup, and layered cursor merge state.

## Risks and Test Signals

The risk is stale cursor state after a prepare conflict, especially when the prepared remove is first, middle, last, or covers multiple keys. The primary signal is that after rollback the cursor returns exactly `stable_keys` and ends with `WT_NOTFOUND`. This catches both skipped stable records and duplicate/incorrect ordering after conflict recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare02.py

## Purpose

This file tests forward iteration after `search()` or `search_near()` returns `WT_PREPARE_CONFLICT` on a layered follower cursor. The expected behavior is that subsequent `next()` calls start from a clean cursor state and return the correct stable rows.

## Important APIs, Types, and Functions

Scenarios choose between `search` and `search_near`. Helpers `safe_next`, `safe_search`, and `safe_search_near` normalize prepare-conflict exceptions into return codes. `_setup_follower` creates a stable checkpoint with keys `1`, `2`, `3`, opens a follower, prepares an ingest update on one key, and returns the sessions and cursor needed by each test.

## Control Flow

The first test positions the cursor at key `3`, then searches key `2` and hits a prepare conflict. After rolling back the prepare, `next()` must return all stable keys from the beginning. The second test first conflicts on `next()` at key `1`, then conflicts again via `search` or `search_near` on the same key, rolls back the prepare, and verifies full forward iteration.

## State, Persistence, and Dependencies

The test relies on persisted stable records from a leader checkpoint plus unresolved prepared follower ingest updates. It uses `precise_checkpoint=true`, timestamped checkpoint transfer, prepared transactions, and read timestamps that cover the prepare. Dependencies are `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`.

## Risks and Test Signals

The risk is that a conflicting point lookup preserves an old position or partially initialized layered merge state, causing later scans to skip keys. Exact `got == stable_keys` assertions after rollback provide the signal. Running both `search` and `search_near` is important because those APIs can position cursors differently internally.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare03.py

## Purpose

This focused test verifies that a layered follower cursor resumes correctly when the very first `next()` call returns `WT_PREPARE_CONFLICT`. It protects the boundary case where there is no prior returned key or saved scan position.

## Important APIs, Types, and Functions

The class uses `disagg_test_class` and a leader connection with `precise_checkpoint=true`. `safe_next` catches `wiredtiger.WiredTigerError` and returns `wiredtiger.WT_PREPARE_CONFLICT` only for the expected conflict. The table is a layered disaggregated table with string keys and values.

## Control Flow

The leader writes stable keys `1`, `2`, `3`, advances stable to 200, and checkpoints. A follower opens and picks up the checkpoint. The follower then prepares an ingest update for key `1`, so a read-committed scan conflicts on its first `next()`. After the prepare is rolled back, the same cursor continues and must return all three stable keys in order.

## State, Persistence, and Dependencies

State spans stable checkpoint contents and an unresolved prepared update in the follower ingest tree. The reader uses `isolation=read-committed` rather than an explicit read timestamp, making the conflict path sensitive to current prepared visibility. Dependencies are limited to `wiredtiger`, `wttest`, and `helper_disagg`.

## Risks and Test Signals

The risk is losing the ability to restart a scan after an initial conflict, either by assuming a previous key exists or by leaving the cursor marked positioned. The test signal is compact and strong: first `next()` must conflict, then after rollback iteration must return exactly `['1', '2', '3']` and end with `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare04.py

## Purpose

This suite tests layered ingest garbage collection around prepared and aborted prepared updates. It ensures prepared updates and rollback records are retained until their prepare or rollback timestamps are safely covered by the checkpoint timestamp, and then become collectible at the correct time.

## Important APIs, Types, and Functions

The class runs both `layered:` and `table:` layered creation forms over disaggregated storage scenarios. Connections enable `statistics=(all),precise_checkpoint=true,preserve_prepared=true`. `create_follower` opens a follower; each test manually mirrors leader writes into follower ingest. Assertions read data-source statistics including `rec_ingest_garbage_collection_keys_update_chain`, `rec_ingest_garbage_collection_keys_disk_image`, and `rec_ingest_keep_prepare_rollback`.

## Control Flow

The tests create committed baseline records, introduce prepared inserts or updates, sometimes roll them back at timestamp 30, move stable timestamps in phases, checkpoint the leader, advance the follower checkpoint, force follower eviction, and inspect reconciliation counters. Cases include a live prepared insert, rolled-back prepared insert, live prepared update, rolled-back prepared update, and obsolete rolled-back prepared insert later superseded by a committed update.

## State, Persistence, and Dependencies

Persistent behavior is observed through checkpointed stable tables, follower ingest updates, rollback timestamps, oldest/stable timestamp movement, and eviction-triggered reconciliation. Dependencies include `wiredtiger`, `wttest`, `helper_disagg`, `wtscenario`, and `wiredtiger.stat`.

## Risks and Test Signals

The main risk is over-aggressive GC that removes a prepared cell or prepare rollback before it is globally safe, or under-aggressive GC that retains obsolete entries after all relevant timestamps are stable. Statistics assertions give precise signals about whether GC came from update chains or disk images and whether prepare rollback retention was counted. The phased timestamp movement makes regressions visible at the exact transition points.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare05.py

## Purpose

This test checks reconciliation of rolled-back prepared updates in layered tables. It ensures the old committed value or deletion state is written correctly after a prepared update, reinsert, or remove is rolled back, across full-image and page-delta checkpoint modes.

## Important APIs, Types, and Functions

The test class extends `prepare_util.test_prepare_preserve_prepare_base`, inheriting `checkpoint_and_verify_stats`. Scenarios vary forced eviction and page delta support. `conn_config` disables internal and leaf page deltas when the `delta` scenario is false. The tested statistics are `rec_time_window_prepared`, `rec_page_delta_leaf`, and `rec_page_full_image_leaf`.

## Control Flow

Each test seeds keys 1-19, advances stable, checkpoints, optionally evicts the page, then opens a separate session to prepare and roll back a change to key 19. It first verifies that checkpointing before the prepare timestamp skips or minimally writes the page. It then advances stable to the prepare timestamp and expects a prepared time window to be reconciled. Finally it advances stable to the rollback timestamp and expects the committed base state to be written, then verifies the key's final value or absence.

## State, Persistence, and Dependencies

The tests are timestamp-heavy: committed timestamps 21/22, stable timestamps 20/21/30/35/45, prepare timestamp 35, and rollback timestamp 45. They depend on `wiredtiger`, `wttest`, `helper_disagg`, `prepare_util`, and `wtscenario`, and integrate with layered reconciliation, eviction, page deltas, durable tombstones, and preserve-prepare-base behavior.

## Risks and Test Signals

The risk is losing the pre-prepare base when a prepared update rolls back, especially after eviction or when a removed key is reinserted. Statistics verify whether a checkpoint actually wrote a prepared time window or page image/delta, and final cursor checks verify user-visible state. The reinsert case documents an expected extra write when eviction removed the prior tombstone from memory.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare06.py

## Purpose

This broad suite tests layered cursor walking on a follower after checkpoint advancement, especially the two-cursor merge path between stable and ingest trees. It verifies correct scan position around overwrite updates, prepared conflicts, prepare commits, prepare rollbacks, boundary conflicts, and reverse iteration.

## Important APIs, Types, and Functions

Helpers include `early_setup` for follower storage links, `populate_leader_and_checkpoint`, `open_follower`, `walk_next_collect`, `walk_prev_collect`, `setup_committed_then_prepared`, `setup_prepared_rollback`, `commit_prepared`, and `rollback_prepared`. The class uses `preserve_prepared=true`, `precise_checkpoint=true`, `wiredtiger.WT_PREPARE_CONFLICT`, and `wiredtiger_strerror` for reliable conflict detection.

## Control Flow

The first test positions a follower cursor through `search`, performs an overwrite update, advances a checkpoint, and verifies `next()` only returns keys greater than the search key. The remaining tests build stable data on the leader and follower-ingest committed or prepared writes, then scan forward or backward until a prepare conflict. They resolve the prepare by commit or rollback and continue scanning on the same cursor, checking set coverage, no duplicates, and monotonic ordering. Cases cover conflicts at scan start, middle, end, ingest-only keys, rolled-back never-committed keys, and rolled-back overwrites that must reveal prior committed values.

## State, Persistence, and Dependencies

State crosses leader stable checkpoint data, follower ingest writes, prepared transactions at timestamp 50, read transactions at timestamp 60, and role-specific disaggregated connection state. Dependencies include `os`, `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`.

## Risks and Test Signals

The risk is losing the merge cursor position when a conflict interrupts a scan, causing skipped odd stable-only keys, duplicate keys, out-of-order results, or disappearance of a rolled-back overwrite's base value. Strong signals include exact set equality with all expected keys, no repeated keys across scan segments, ascending/descending order checks, and direct verification that rolled-back overwrites expose `committed_3`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare07.py

## Purpose

This suite verifies that follower cursor operations do not raise `WT_PREPARE_CONFLICT` when the primary has checkpointed unresolved prepared updates and the follower has rolled back its own replayed copy. The follower should return committed values from stable storage.

## Important APIs, Types, and Functions

Key helpers are `setup_primary_and_follower`, `prepare_on_conn`, `checkpoint_with_prepare`, `setup_with_prepare`, `evict_page`, `collect_keys`, `resolve_prepared`, and `run_walk_test`. The connection config enables `statistics=(all),precise_checkpoint=true,preserve_prepared=true`. The suite tests `next`, `prev`, `search`, and `search_near`.

## Control Flow

The common setup commits initial values on both primary and follower, checkpoints them, prepares the same update or delete on both sides using the same prepared ID, and checkpoints the primary with the prepare active. The follower advances to that checkpoint, rolls back its local prepared transaction, evicts affected pages to force reading checkpointed prepared cells, and then scans or searches. Cleanup rolls back the primary prepare, advances stable, and checkpoints so teardown does not see dangling prepared state.

## State, Persistence, and Dependencies

The test deliberately persists prepared cells in the primary checkpoint while also keeping the follower's in-memory transaction state consistent with rollback. It depends on `wiredtiger`, `wttest`, `helper_disagg`, `wtscenario`, and disaggregated checkpoint transfer.

## Risks and Test Signals

The main risk is treating checkpointed prepared cells as active conflicts on a follower after oplog replay rollback has resolved the prepare locally. Signals are sorted key equality for forward and backward scans over prepared updates and tombstones, plus direct `search`/`search_near` assertions that key 2 returns `committed_2` without conflict.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare08.py

## Purpose

This narrow regression test protects a layered cursor comparison guard after the ingest cursor becomes exhausted. It ensures a scan does not assert when a prepared ingest key conflicts, is rolled back, and then disappears before the next scan step.

## Important APIs, Types, and Functions

The class uses leader and follower configs with `cache_size=10MB,statistics=(all),precise_checkpoint=true,preserve_prepared=true`. It opens a follower with `disagg_advance_checkpoint`, creates a prepared transaction on the follower ingest tree, and uses `assertRaisesException` for the expected `WiredTigerError`.

## Control Flow

The leader writes stable keys 1, 3, and 5 and checkpoints. The follower picks up the stable checkpoint and prepares a single ingest key 2 at prepare timestamp 15. A reader at timestamp 20 calls `next()`: stable advances to key 1 while ingest hits key 2 and returns a prepare conflict. The prepared transaction rolls back at timestamp 30, removing key 2. A second `next()` must skip invalid ingest comparison state, return stable key 1, then continue with 3 and 5 before `WT_NOTFOUND`.

## State, Persistence, and Dependencies

State is split between stable checkpoint data and a transient prepared follower-ingest key. The test depends on `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`, and integrates with timestamped reads, prepare rollback, and layered cursor current-cursor selection.

## Risks and Test Signals

The risk is an internal assertion or invalid key comparison when the ingest cursor has a ref but no valid current key after rollback. The signal is that the retry returns only the stable keys in order and reaches `WT_NOTFOUND`, proving the merge path handles an unpositioned exhausted ingest cursor.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare09.py

## Purpose

This suite tests follower step-up when a leader checkpoint captures unresolved prepared transactions. It verifies that replicated prepare resolution on the follower, either commit or rollback, produces the correct durable history after the follower becomes leader.

## Important APIs, Types, and Functions

The class is skipped for tiered hooks, uses `preserve_prepared=true`, and scenarios vary `commit=True/False`. Helpers `_open_follower`, `_checkpoint`, and `_step_up` apply checkpoint metadata, checkpoint a connection, and promote a follower by reconfiguring `disaggregated=(role="leader")`. Tests use `disagg_get_complete_checkpoint_meta`, prepared IDs, commit/durable timestamps, rollback timestamps, and timestamped reads.

## Control Flow

Each captured-prepare test builds leader history, leaves a prepare unresolved while stable is advanced beyond the prepare timestamp, checkpoints, stores checkpoint metadata, rolls back the leader copy, and closes the leader without another checkpoint. A follower opens on that metadata, replays the same prepared operation, resolves it by scenario, steps up, and verifies reads at historical timestamps. Cases cover prepared inserts, updates followed by newer updates, deletes, a delete between older and newer committed values, and multiple updates to the same key within one prepared transaction. The not-captured tests set `prepare_ts > stable_ts` at checkpoint time and verify the follower sees only durable pre-prepare state without replay.

## State, Persistence, and Dependencies

State is persisted through checkpoint metadata rather than normal checkpoint pickup. The tests depend on `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`. They integrate with disaggregated role changes, prepared transaction replication, durable timestamp semantics, and historical timestamp reads.

## Risks and Test Signals

Risks include applying unresolved prepares twice, losing rollback semantics, exposing prepares not durable at checkpoint time, or mishandling multiple writes to one key. Signals are precise timestamp reads: original values before prepare, commit-vs-rollback behavior at resolution timestamps, newer value preservation at timestamp 220, and `WT_NOTFOUND` for committed prepared deletes or absent not-captured inserts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_prepare09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema01.py

## Purpose

This is the basic layered tree creation test. It verifies that creating a `layered:` URI creates the expected metadata entries for the logical layered object and its stable and ingest file constituents.

## Important APIs, Types, and Functions

The test uses `disagg_test_class` and a leader connection with verbose layered logging and `lose_all_my_data=true`. `StorageSource` is imported for constant access but not used in the test body. `check_metadata` opens `metadata:create` and asserts that a URI's metadata string contains an expected substring.

## Control Flow

The single test creates `layered:test_layered_schema01` with string key/value formats, then checks metadata for the layered URI, `file:test_layered_schema01.wt_ingest`, and `file:test_layered_schema01.wt_stable`. The expected substring is empty, so the test primarily asserts that each metadata entry exists and can be read.

## State, Persistence, and Dependencies

The persistent state is WiredTiger metadata for the layered table and its component files. Dependencies include `os`, `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`, although scenarios are not used here. The integration point is the schema creation path for disaggregated layered tables.

## Risks and Test Signals

The risk is a schema create regression where the layered wrapper exists without one of its component files, or metadata lookup behavior changes. The signal is minimal but foundational: all expected URIs must exist in metadata immediately after create.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema02.py

## Purpose

This test ensures that a follower dropping a layered table does not fall back to reading the stable table from a checkpoint. After a follower-side drop, opening the logical table must fail even though stable data may exist in shared storage.

## Important APIs, Types, and Functions

The class uses `disagg_test_class`, a leader connection, and a manually opened follower. It writes `nitems * 3` string records, advances a checkpoint to the follower, uses `drop(..., force=true)` on the follower, and later reopens the leader connection before dropping the leader table.

## Control Flow

The leader and follower create the same layered table. The leader writes three key prefixes for 10,000 indices, checkpoints, and the follower picks up the checkpoint. The follower scans to confirm all data is visible, drops the table with force, and verifies opening the cursor now raises `WiredTigerError`. The leader is then scanned to prove its table still has data, reopened to avoid cached-handle effects, dropped, and similarly verified inaccessible.

## State, Persistence, and Dependencies

State spans leader data, follower stable checkpoint visibility, follower local schema metadata, and leader schema after reopen. Dependencies are `os`, `wiredtiger`, `wttest`, and `helper_disagg`. The integration points are layered drop, checkpoint pickup, cursor open failure behavior, and local-vs-shared metadata precedence.

## Risks and Test Signals

The key risk is a dropped follower table resurrecting from shared stable metadata. Signals include row-count validation before drop and expected cursor-open failures after follower and leader drops. The large row count gives a meaningful scan signal that checkpoint pickup worked before the drop assertion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema03.py

## Purpose

This suite validates that dropping layered tables removes local metadata, prevents cursor opens, updates shared metadata correctly, and does not crash later sweep. It covers both `layered:` creation and `table:` with `block_manager=disagg,type=layered`.

## Important APIs, Types, and Functions

Helpers `check_metadata_entry`, `check_shared_metadata`, and `validate_drop` inspect `metadata:`, `file:WiredTigerShared.wt_stable`, and cursor-open behavior. Connection config enables statistics logging and fast file-manager close scanning. Scenarios combine table prefix/type with disaggregated storage.

## Control Flow

`test_create_drop` creates, populates, checkpoints, drops, validates local metadata removal, checkpoints again, and checks shared metadata no longer contains the table. `test_create_drop_checkpoint` does the same through a custom session that is closed to release dhandle references for sweep. `test_create_drop_follower` creates and checkpoints on leader, reopens as a follower using checkpoint metadata, drops locally, validates local removal, checkpoints, and expects shared metadata still to contain the table because a follower drop should not erase the leader's shared metadata.

## State, Persistence, and Dependencies

The tests persist local metadata, shared metadata, data files, and dhandle lifecycle through checkpoint and sweep. Dependencies include `re`, `os`, `wiredtiger`, `wttest`, `helper_disagg`, `wtscenario`, and `wiredtiger.stat`.

## Risks and Test Signals

Risks include stale metadata entries, incorrect shared metadata removal on followers, cursor access to dropped tables, and sweep crashes from closed handles. Signals are direct metadata `WT_NOTFOUND` checks, shared metadata containment checks, expected cursor-open failures, and successful completion after checkpoint/sweep-sensitive paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema04.py

## Purpose

This long test stress-tests schema creation by creating a large number of layered tables. It is aimed at file-id allocation, metadata scaling, and resource handling for many disaggregated layered objects.

## Important APIs, Types, and Functions

The class uses `disagg_test_class`, `gen_disagg_storages(..., disagg_only=True)`, and a leader connection with statistics and statistics logging. The single `test_create_tables` method is marked with `wttest.longtest('lots of tables')` and loops over 10,000 `session.create` calls.

## Control Flow

For each index from 0 to 9999, the test creates `layered:test_table<i>` with string key/value formats and asserts `session.create` returns zero. There are no writes, scans, checkpoints, or drops in the test body; its purpose is creation throughput and schema scalability.

## State, Persistence, and Dependencies

The persistent state is the metadata and component files for 10,000 layered tables in one leader home. Dependencies are `wttest`, `helper_disagg`, and generated disaggregated storage scenarios. The test integrates with layered table creation, metadata table growth, and any storage-source file naming/allocation behavior under high object count.

## Risks and Test Signals

Risks include metadata exhaustion, duplicate names or IDs, handle leaks, slow path failures, and object-count limits in disaggregated schema code. The test signal is simple but high volume: every create must return success. Because it is marked long, it may not run in short suites and is best treated as a stress signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema05.py

## Purpose

This test verifies that missing local stable files for layered tables are recreated correctly from disaggregated metadata on restart. It covers both empty and populated tables.

## Important APIs, Types, and Functions

The class starts as a follower with statistics, statistics logging, and `precise_checkpoint=true`. Scenarios cover `layered:` URIs and `table:` URIs configured as layered disaggregated tables. It uses `restart_without_local_files()` to simulate loss of local files after stepping up and checkpointing.

## Control Flow

The test creates an empty table and a filled table, writes one timestamped row to the filled table, advances stable to timestamp 10, reconfigures the connection from follower to leader, and checkpoints. It then restarts without local files. After restart, it opens the empty table and confirms it has zero rows, then opens the filled table and confirms key `a` reads value `b`.

## State, Persistence, and Dependencies

State is persisted through role transition, stable timestamp, checkpoint, disaggregated metadata, and restart with local files removed. Dependencies include `wiredtiger`, `wttest`, `helper_disagg`, `wtscenario`, and generated disaggregated storage scenarios.

## Risks and Test Signals

The risk is that layered schema recovery cannot recreate missing stable constituents, or recreates them without the right data. Signals cover both an empty table and a table with committed content, ensuring recovery handles table existence and data visibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema06.py

## Purpose

This suite validates WiredTiger file ID namespaces for disaggregated layered metadata. It ensures special shared files have fixed IDs, local and shared dynamic files use the correct namespaces, prohibited PALI-reserved IDs are not emitted, and leader/follower metadata remains consistent.

## Important APIs, Types, and Functions

Constants model local, shared, and special namespaces and the three namespace bits. `extract_id` from `metadata_helper` parses file IDs from metadata values. `check_metadata_ids` iterates `metadata:` entries, validates fixed IDs for `WiredTigerShared.wt_stable`, `WiredTigerSharedHS.wt_stable`, and `metadata:`, validates dynamic namespaces for `WiredTigerHS.wt` and explicit layered stable/ingest files, and fails on unexpected file/metadata entries.

## Control Flow

Tests cover an empty leader and follower, one table populated on the leader, one table picked up by a follower after checkpoint transfer, ten tables picked up by a follower, and ten tables created on both leader and follower. Creation formats include bare layered, layered with disagg block manager, and `table:` layered type. Expected stable files are shared namespace; ingest files are local namespace.

## State, Persistence, and Dependencies

State lives in metadata IDs assigned by schema creation, implicit history store creation, shared metadata, and checkpoint pickup. Dependencies include `re`, `wttest`, `metadata_helper`, `helper_disagg`, and `wtscenario`.

## Risks and Test Signals

Risks include backward-incompatible fixed ID changes, namespace collisions, use of PALI-reserved IDs, duplicate IDs in a namespace, follower ingest files receiving shared IDs, and unexpected metadata entries. The signal is comprehensive metadata iteration with explicit expected-file maps for each scenario.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema07.py

## Purpose

This suite tests `WT_SESSION::publish` for disaggregated schema operations on leaders. It verifies that create and drop operations are not included in checkpoints until published with a schema epoch and that checkpoint processing respects the stable disaggregated schema epoch.

## Important APIs, Types, and Functions

Helpers set stable schema epochs, run timestamped leader checkpoints, open followers, check follower table visibility after checkpoint pickup, call `session.publish`, and poll statistics. It uses `suite_subprocess` for expected panic cases and statistics such as `session_table_publish_success`, `session_table_publish_fail`, `checkpoint_disagg_metadata_unstable`, and `checkpoint_disagg_metadata_apply`.

## Control Flow

Functional tests show create is invisible before publish and visible after publish plus checkpoint, and drop is deferred until the drop is published. Error tests reject zero epochs, epochs not newer than the current stable schema epoch, and unsupported URI types. Two subprocess tests intentionally panic by checkpointing dirty table data when the required CREATE metadata is unpublished or published at an epoch later than the stable epoch. The stats test verifies success/failure publish counters and checkpoint apply/defer counters.

## State, Persistence, and Dependencies

State includes the metadata operation queue, stable schema epoch, transactional timestamps, shared metadata, follower checkpoint pickup, and connection statistics. Dependencies include `os`, `time`, `wiredtiger`, `wttest`, `helper_disagg`, `suite_subprocess`, `wtscenario`, and `wiredtiger.stat`.

## Risks and Test Signals

Risks include exposing unpublished schema to followers, applying drops too early, allowing invalid publish epochs, skipping required panic paths, or miscounting stats. Signals combine follower visibility checks, precise error-message assertions, subprocess nonzero return codes, and retrying statistic equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema08.py

## Purpose

This suite verifies that shared metadata queue operations are deferred until checkpoint processing. It also tests operations enqueued concurrently after checkpoint prepare, which must remain deferred until the next checkpoint.

## Important APIs, Types, and Functions

The class extends `checkpoint_util`, uses `wtthread.Thread`, and defines URI helpers for logical, stable, layered, table, and colgroup metadata names. `check_shared_metadata` scans `file:WiredTigerShared.wt_stable` and asserts expected containment or absence. Scenarios cover `layered:` and `table:` layered forms.

## Control Flow

Basic tests show create does not appear in shared metadata until checkpoint, drop remains visible until checkpoint, create+drop in the same checkpoint leaves no entry, and extra checkpoints without schema changes leave metadata unchanged. Concurrent tests use `timing_stress_for_test=[checkpoint_slow]` and `wait_for_checkpoint_start()` so a create or drop occurs after checkpoint prepare. The first checkpoint skips the newly deferred operation; the next checkpoint applies it. The drop case additionally configures fast dhandle sweep and uses `checkpoint_wait=false` so the drop can proceed during a checkpoint.

## State, Persistence, and Dependencies

State includes deferred metadata queue entries, checkpoint prepare/end phases, shared metadata table contents, dhandle sweep state, and timing stress configuration. Dependencies are `time`, `wiredtiger`, `wttest`, `wtthread`, `checkpoint_util`, `helper_disagg`, and `wtscenario`.

## Risks and Test Signals

Risks include applying schema operations too early, losing queue entries across checkpoints, mishandling create/drop pairs, and races between checkpoint and schema operations. Signals are direct shared metadata containment checks before and after each checkpoint, plus thread synchronization around checkpoint start.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema09.py

## Purpose

This test verifies persistence of the stable disaggregated schema epoch in checkpoints. It distinguishes the current stable schema epoch set by the caller from the last schema epoch recorded in the latest checkpoint.

## Important APIs, Types, and Functions

`assertEpochEqual` queries `get=stable_disaggregated_schema_epoch`; `assertLastCheckpointEpochEqual` queries `get=last_disaggregated_schema_epoch`. The connection runs as a disaggregated leader with statistics and `lose_all_my_data=true`. The test creates a layered table so checkpointing exercises disaggregated storage.

## Control Flow

The first checkpoint before setting an epoch records last checkpoint epoch 0. The test then sets oldest, stable, and stable schema epoch to 10, checkpoints, and expects last checkpoint epoch 10. After restart, the last checkpoint epoch remains 10. It advances timestamps and epoch to 30, checkpoints, and expects 30. A checkpoint changing only stable timestamp leaves last epoch at 30. A checkpoint changing only the schema epoch to 40 updates last checkpoint epoch to 40. A final restart confirms the current epoch resets to 0 while the last checkpoint epoch persists as 40.

## State, Persistence, and Dependencies

State crosses queryable timestamp state, checkpoint metadata, restart, and local file removal. Dependencies include `wttest`, `helper_disagg`, and `wiredtiger.stat` though the stat import is not used.

## Risks and Test Signals

Risks include failing to write schema epoch into checkpoint metadata, incorrectly restoring it as current mutable state, or skipping checkpoints when only the schema epoch changes. Signals are timestamp equality assertions before and after checkpoints and restarts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_schema10.py

## Purpose

This suite tests the publish API on followers and schema step-up behavior. Schema operations queued while a node is a follower must be replayed correctly when that node becomes leader, and then flushed to shared metadata only when the stable schema epoch reaches their publish epoch.

## Important APIs, Types, and Functions

Helpers set stable schema epochs on arbitrary connections, run leader checkpoints, publish URIs, compute stable constituent URIs, check local metadata via cursor-open, check shared metadata via `file:WiredTigerShared.wt_stable`, seed an initial epoch checkpoint, swap roles, open followers, and checkpoint/advance back to the original connection. `suite_subprocess` isolates an expected panic for split create/drop epochs.

## Control Flow

Tests cover follower-created tables becoming locally available after role swap, create-then-drop on a follower leaving no trace, follower-created data becoming visible to the old leader after checkpoint pickup, multiple follower-created tables published at different epochs flushing independently, follower drops removing shared metadata only after the drop epoch, unpublished follower creates never flushing, and schema-epoch-only advancement forcing a checkpoint to run. The split-epochs subprocess creates and drops a table at different epochs before step-up; checkpointing at the intermediate epoch is expected to panic because the table should be visible but its stable constituent was never created.

## State, Persistence, and Dependencies

State includes follower metadata queues, local metadata, shared metadata, role reconfiguration, stable schema epoch, transactional stable timestamps, checkpoint pickup, and skip-checkpoint connection close behavior. Dependencies include `wiredtiger`, `wttest`, `helper_disagg`, `suite_subprocess`, and `wtscenario`.

## Risks and Test Signals

Risks include losing follower-queued schema operations on step-up, flushing operations at the wrong epoch, treating unpublished operations as publishable, skipping checkpoints when only schema epoch advances, and mishandling create/drop pairs. Signals are explicit local/shared metadata assertions after role swaps and checkpoint pickups, plus a subprocess nonzero exit for the intentional API-violation panic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_schema10.py -->
