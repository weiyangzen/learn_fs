# Research: subset-b-009081

This grouped report covers WiredTiger layered cursor, page delta, and disaggregated eviction tests. Each file section preserves the original source path and is bounded by the markers consumed by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor13.py

Purpose: regression coverage for bounded layered cursors on a follower over a 1000-key dataset. It verifies lower and upper cursor bounds, inclusive and exclusive edge behavior, nonexistent bound keys, tombstones, search/search_near under bounds, bound rebinding, and positioned updates during scans.

Important APIs and types: `test_layered_cursor13` derives from `wttest.WiredTigerTestCase` and is wrapped by `@disagg_test_class`. It uses `gen_disagg_storages(..., disagg_only=True)` and `make_scenarios`, WiredTiger cursor APIs `bound`, `next`, `prev`, `search`, `search_near`, `update`, `set_key`, `set_value`, and transaction timestamps through `timestamp_str`. Helpers include `insert_stable`, `insert_ingest`, `remove_ingest`, `populate_*`, `set_bounds`, `scan_forward`, `scan_backward`, `open_bounded_cursor`, and `expected_range`.

Control flow: `setUp` creates the same layered URI on leader and follower sessions. Stable rows are written on the leader, checkpointed, and exposed to the follower with `disagg_advance_checkpoint`; ingest rows and tombstones are written directly on the follower. Each test populates one data layout, opens a bounded follower cursor, scans or searches, then asserts returned key order and visibility.

State and persistence behavior: stable data represents checkpointed leader state, while ingest data and tombstones represent follower-local overlay state. The tests exercise merge ordering across stable and ingest constituents, and assert tombstones hide stable values even inside or at bounds. Timestamped commits and stable timestamp advancement make the checkpoint boundary explicit.

Dependencies and integration: integrates with WiredTiger disaggregated storage helpers, layered table creation, cursor bounds, and follower checkpoint advancement. Risks are off-by-one bound filtering, stale constituent cursor position after bound changes, tombstone leakage, and write positioning corrupting a scan. Test signals are direct equality checks for complete key ranges and explicit `WT_NOTFOUND`/search result assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor14.py

Purpose: broad layered cursor iteration coverage on a follower. It stresses forward and backward scans, duplicate keys in stable plus ingest, tombstone skipping, direction changes, scans after `search` and `search_near`, reset behavior, empty tables, ingest-only/stable-only data, interleaved stable and ingest key spaces, and positioned updates mid-scan.

Important APIs and functions: `test_layered_cursor14` is a `WiredTigerTestCase` decorated with `@disagg_test_class`. It uses `cursor.next`, `cursor.prev`, Python cursor iteration, `search`, `search_near`, `reset`, `update`, `remove`, transaction timestamps, `session.checkpoint`, and `disagg_advance_checkpoint`. Helper methods produce formatted keys/values, insert into leader stable or follower ingest, remove ingest rows, open follower cursors, and walk expected next/prev sequences.

Control flow: setup creates leader and follower layered URIs. Population helpers generate all-stable, all-ingest, and split even/odd layouts. Tests then execute scans from unpositioned cursors, scans after positioning calls, zigzag next/prev transitions, searches around tombstones, and many search_near cases where only one constituent has the nearest key or both constituents are on one side of the probe.

State and persistence behavior: checkpointed leader rows become stable constituent data; follower writes and deletes become ingest constituent state. Tombstones are deliberately applied to ingest keys to hide stable data. The cursor's internal constituent positions are repeatedly reused across direction switches and transaction-free operations, making stale alternate-cursor state a central risk.

Dependencies and integration: depends on disaggregated leader/follower test infrastructure, WiredTiger cursor positioning semantics, timestamped transactions, and layered merge logic. Risks include duplicate visible rows when a key exists in both constituents, skipped rows after direction changes, stale search_near side choice, tombstone visibility, and positioned write interactions. Test signals are complete list equality, key/value equality, `WT_NOTFOUND` at edges, and relational assertions around nearest keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor15.py

Purpose: exhaustive-ish follower layered cursor iteration over combinations of key states. It models each key as ingest only (`I`), stable only (`S`), both (`B`), stable hidden by ingest tombstone (`R`), or ingest tombstone with no stable row (`X`), then verifies iteration and point lookup for many generated state strings.

Important APIs and functions: top-level `generate_unique_situations(max_len)` builds state sequences with bounded repetition. `test_layered_cursor15` uses `@disagg_test_class`, transaction context helpers, `open_cursor`, `next`, `prev`, `search`, `remove`, `disagg_advance_checkpoint`, and timestamped commits. `_apply_ops` mutates leader or follower rows based on state letters, `_verify_zigzag` alternates scan directions, and `_verify_cursor` checks forward, backward, zigzag, and point reads.

Control flow: the leader creates one layered table per generated situation. Stable states are first inserted and checkpointed. Leader and follower remove `X` states, then the follower inserts ingest-visible rows and tombstones `R` states. After checkpoint advancement, the follower verifies each table.

State and persistence behavior: the file explicitly documents the stable/ingest/tombstone state machine and then creates those states with timestamped transactions and checkpoint handoff. The expected visible set is only `I`, `S`, and `B`. The same cursor must transition correctly from unpositioned state to data, across visible and hidden keys, and back to `WT_NOTFOUND`.

Dependencies and integration: relies on layered disaggregated table support, follower connections, precise checkpointing, and WiredTiger transaction helpers. Risks include combinatorial gaps in merge transitions, hidden tombstones appearing in scans, point search disagreeing with iteration, and infinite loops in zigzag iteration. Test signals are strict expected list equality, value equals key checks, `WT_NOTFOUND` assertions, and a loop guard in `_verify_zigzag`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor16.py

Purpose: verifies `reserve()` behavior on layered cursors for keys present on the leader, on the follower stable constituent, on the follower ingest constituent, in both constituents, and missing from the table.

Important APIs and functions: `test_layered_cursor16` uses `@disagg_test_class`, `WiredTigerTestCase`, `session.begin_transaction`, timestamped `commit_transaction`, `session.checkpoint`, `conn.set_timestamp`, `wiredtiger_open` for a follower, `disagg_advance_checkpoint`, and cursor `reserve`. Helpers are `write`, `checkpoint`, `open_follower`, and `do_reserve`.

Control flow: each test creates the layered URI, writes or checkpoints enough data to establish one key state, then calls `do_reserve` inside a transaction. Existing keys should return `0`; missing keys are expected to raise `WiredTigerError`.

State and persistence behavior: leader tests cover pre-checkpoint and post-checkpoint data in the leader role. Follower tests split visibility between checkpointed stable data and follower-local ingest data. Transactions are rolled back after `reserve`, so the operation's lock/reservation behavior is tested without persisting additional state.

Dependencies and integration: integrates with disaggregated leader/follower opening, stable timestamp advancement, layered cursor reserve handling, and exception mapping through the Python API. Risks include treating missing layered keys as reservable, failing to search both constituents before reserving, and role-specific differences between leader and follower. Test signals are `assertEqual(..., 0)` for successful reserve and `assertRaises(wiredtiger.WiredTigerError)` for missing-key paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor17.py

Purpose: scenario-driven coverage that follower cursor operations succeed on keys that exist only in the stable table, meaning they were written by the leader and checkpointed before the follower observed them.

Important APIs and functions: top-level wrappers `_op_reserve`, `_op_search`, `_op_search_near`, `_op_update`, `_op_remove`, and `_op_modify` normalize different cursor APIs to a return code. `test_layered_cursor17` uses `make_scenarios` to run one test body per operation, and uses `wiredtiger.Modify` for modify coverage.

Control flow: `insert_keys` writes ten timestamped keys on the leader. The leader sets the stable timestamp and checkpoints, the follower is opened and advanced to the checkpoint, and a follower cursor performs the parameterized operation on key `5` inside a transaction that is then rolled back.

State and persistence behavior: all target keys live only in the stable constituent; no follower ingest write is needed to make them visible. Update/remove/modify paths are validated for their ability to position and operate from stable data while the rollback prevents durable mutation of the test dataset.

Dependencies and integration: depends on disaggregated storage scenarios, follower checkpoint advance, layered cursor operation dispatch, and Python modify bindings. Risks include operation-specific code paths that only search ingest, stable-only positioned writes failing after a stable lookup, and `search_near` returning success but positioning incorrectly. Test signals are a single `0` return assertion for each operation scenario plus rollback cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor18.py

Purpose: regression tests for stale alternate constituent cursor state when a single layered follower cursor is reused across transactions. It covers read timestamp changes and snapshot generation changes caused by new follower ingest writes between calls.

Important APIs and functions: `test_layered_cursor18` uses `DisaggConfigMixin` indirectly through disaggregated helpers, `wiredtiger_open` for a follower, timestamped transactions, `next`, `prev`, and assertion helpers `follow_next` and `follow_prev`. It also defines reusable snapshot-generation helpers `snapshot_gen_ingest_next` and `snapshot_gen_ingest_prev`, with test variants for explicit transaction and auto-transaction combinations.

Control flow: each scenario creates leader stable data and follower ingest data such that one constituent is selected as current while the other is left parked as an alternate. The next operation runs under a different read timestamp or after a new ingest write, and the test asserts the cursor re-searches the alternate constituent under the new snapshot before returning data.

State and persistence behavior: leader checkpoint data provides stable histories at older timestamps; follower ingest data provides newer versions or newly committed keys. The same cursor object crosses transaction boundaries, so persistence correctness depends on invalidating or refreshing cached constituent state.

Dependencies and integration: integrates with layered merge cursors, transaction snapshots, follower ingest writes, and checkpointed stable pages. Risks include returning stale values, using a parked alternate key from an older snapshot, and mismatches between explicit and implicit transaction paths. Test signals are exact key/value assertions after each `next` or `prev`, with inline comments documenting previously buggy returns.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor19.py

Purpose: validates follower write cursor open behavior for layered cursors. With overwrite enabled, follower insert/update should write to ingest without opening stable; with `overwrite=false`, the operation must check for existing stable data and therefore open the stable constituent.

Important APIs and functions: `test_layered_cursor19` uses `DisaggConfigMixin`, `@disagg_test_class`, statistics cursor access via `stat.conn.cursor_create_count`, helper methods `get_conn_stat`, `measure_cursor_opens`, and `seed_leader_and_advance_follower`, plus cursor configurations `overwrite=true` and `overwrite=false`.

Control flow: setup creates the layered table and a follower connection. `seed_leader_and_advance_follower` writes stable rows on the leader, checkpoints, and advances the follower. Each test measures the delta in connection cursor-create count around one follower insert or update. Overwrite tests assert only ingest-open overhead; no-overwrite tests assert additional stable cursor opens.

State and persistence behavior: stable rows are checkpointed leader state, while follower writes land in ingest. The test observes implementation behavior indirectly through cursor creation statistics rather than data reads, making it sensitive to constituent-open decisions in the write path.

Dependencies and integration: integrates with WiredTiger statistics, disaggregated leader/follower setup, layered overwrite semantics, and cursor open accounting. Risks include performance regressions from unnecessary stable opens, correctness regressions when no-overwrite skips stable existence checks, and stat noise from unrelated cursor activity. Test signals compare measured cursor-create deltas against expected thresholds for overwrite and no-overwrite cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor20.py

Purpose: follower cached-cursor coverage for standby-style cursor opening. It checks that repeated follower cursor opens over layered URIs reuse cached constituent cursors enough to stay below a cursor-create limit.

Important APIs and functions: `test_layered_cursor20` uses `@disagg_test_class`, leader and follower disaggregated configurations, `stat.conn.cursor_create_count`, helper methods `show_cursor_create_stats` and `check_cursor_create_stats`, and `disagg_advance_checkpoint`. The main test is `test_standby_open_cursor`.

Control flow: the leader creates multiple layered tables, writes data with timestamped transactions, checkpoints, and advances the follower. The follower repeatedly opens and closes cursors over the layered URIs while the test samples cursor-create statistics before and after the operation batch.

State and persistence behavior: stable checkpoint metadata is shared from leader to follower. The state under test is not row content but internal cursor cache behavior on the follower, especially whether layered cursors repeatedly create stable/ingest constituent cursors.

Dependencies and integration: depends on WiredTiger connection statistics, disaggregated checkpoint advance, layered cursor opening, and the test harness follower connection. Risks include cache leaks, excessive cursor creation, failure to cache stable constituent cursors, or stale cached cursor state if reused unsafely. Test signals are statistic thresholds in `check_cursor_create_stats`, supplemented by diagnostic stat printing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor21.py

Purpose: regression coverage for `next_random` on layered tables when every reachable row is a tombstone. It targets WT-15189 behavior: return `WT_NOTFOUND` rather than spinning when all records are deleted.

Important APIs and functions: `test_layered_cursor21` uses `@disagg_test_class`, `@wttest.skip_for_hook("tiered", ...)`, URI scenarios for `layered:` and `table:` with `block_manager=disagg,type=layered`, follower setup through `setup_follower`, range deletion helpers `truncate_range` and `remove_range`, and `open_cursor(..., "next_random=true")`.

Control flow: tests create base data, advance checkpoint state to a follower, then delete all visible records either by truncate or per-row remove. Cases cover ingest-only tombstones and scattered tombstones split between stable and ingest. `assert_random_notfound` opens a random cursor and asserts the call returns `WT_NOTFOUND`.

State and persistence behavior: stable data can be empty or partially populated, while tombstones may live entirely in ingest or across stable/ingest after checkpoint advancement. Range truncation and per-key removes create different tombstone shapes but the final visibility set is empty.

Dependencies and integration: integrates layered random cursor selection, disaggregated storage, row-store table creation, timestamped deletes, truncation, and tiered-storage skip hooks. Risks include random cursor loops over invisible rows, tombstone density causing retry exhaustion bugs, and different behavior between `layered:` and `table:` URIs. Test signals are direct `WT_NOTFOUND` assertions for random lookup after each all-deleted setup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_cursor21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta01.py

Purpose: baseline leaf page delta read/write coverage for layered disaggregated tables. It verifies follower reads across updates, modifies, deletes, inserts, multiple deltas, and delete/insert cycles under encryption and compression scenarios.

Important APIs and functions: `test_layered_delta01` uses `DisaggConfigMixin`, `@disagg_test_class`, compression and encryption extension loading, `page_delta=(delta_pct=100)`, `stat.conn.rec_page_delta_leaf`, timestamped transactions, `wiredtiger.Modify`, checkpointing, and reopening as a follower with `checkpoint_meta`.

Control flow: each test creates a layered table, loads initial timestamped values, checkpoints, applies a second timestamped mutation type, checkpoints again, asserts at least one leaf delta was reconciled, reopens with follower disaggregated configuration, and verifies historical reads at older and newer read timestamps.

State and persistence behavior: leader checkpoints generate base images and deltas in the disaggregated page log. Follower reopen consumes complete checkpoint metadata and must reconstruct correct historical values from base plus delta chains. Deletes are verified with `WT_NOTFOUND`; modifies verify partial-value reconstruction.

Dependencies and integration: integrates page delta reconciliation, compression/encryption extensions, timestamp visibility, follower checkpoint metadata, and layered table storage. Risks include delta corruption under compression/encryption, timestamp history loss, delete tombstones not replaying, and insert ranges not materializing. Test signals are leaf delta statistic increments and exhaustive key/value checks under both read timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta02.py

Purpose: constructs long delta chains and validates follower reconstruction for both explicit `layered:` tables and shared disaggregated `table:` objects with `block_manager=disagg`.

Important APIs and functions: `test_layered_delta02` uses `@disagg_test_class`, `precise_checkpoint=true`, `make_scenarios` over `layered` and `shared` prefixes, timestamped updates, repeated `conn.set_timestamp`, `session.checkpoint`, follower `wiredtiger_open`, and `disagg_advance_checkpoint`.

Control flow: the test creates the table, inserts 500 records at timestamp 100, checkpoints, then updates one key ten times at consecutive timestamps, advancing stable timestamp and checkpointing after each update. A follower is opened and advanced, then every key is read; the updated key must have the tenth value and all other keys must retain the base value.

State and persistence behavior: the key under test accumulates a chain of page deltas across multiple checkpoints. Follower reads validate that page-log delta chain traversal applies the latest update and does not affect unrelated rows.

Dependencies and integration: depends on disaggregated block manager configuration, precise checkpoints, layered and non-layered URI paths, and follower checkpoint synchronization. Risks include exceeding max delta chain assumptions, broken chain ordering, lost base image rows, or differences between layered and shared table handling. Test signals are full-table value equality after follower reconstruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta03.py

Purpose: verifies that `page_delta=(max_consecutive_delta=1)` prevents reading a long leaf delta chain by forcing full images often enough that follower reads do not report leaf-delta reads.

Important APIs and functions: `test_layered_delta03` uses URI scenarios for `layered:` and `file:` with `block_manager=disagg`, `stat.conn.cache_read_leaf_delta`, `session.checkpoint`, follower reopen with `checkpoint_meta`, and ordinary cursor indexing for reads and writes.

Control flow: the test loads 1000 rows, checkpoints, updates every tenth row, checkpoints, repeats the same update pattern and checkpoints again, then reopens as a follower. It verifies visible values and asserts `cache_read_leaf_delta` is zero.

State and persistence behavior: repeated checkpoints with a low consecutive-delta limit should materialize a full image instead of requiring follower delta-chain reads. The expected state is latest values for every tenth key and original values for the rest.

Dependencies and integration: integrates page delta policy configuration, disaggregated block manager, follower checkpoint metadata, and connection statistics. Risks include ignoring the consecutive-delta cap, creating a readable but unexpectedly long chain, or stat misclassification of full-image reads. Test signals are exact data verification plus zero leaf-delta read statistic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta04.py

Purpose: stress-tests 32 consecutive page deltas across encryption, compression, URI kind, and timestamped versus non-timestamped operation modes.

Important APIs and functions: `test_layered_delta04` uses `DisaggConfigMixin`, compressor and encryptor extension registration, URI scenarios for layered and disaggregated file tables, `page_delta=(delta_pct=100)`, timestamped commits when enabled, repeated checkpointing, and follower reopen with complete checkpoint metadata.

Control flow: the test inserts ten base rows, checkpoints, then runs 32 rounds where key `0` is updated and checkpointed. In timestamped scenarios, follower reads are run at the base timestamp and after every update timestamp. In non-timestamped scenarios, only the latest value is validated.

State and persistence behavior: a compact dataset receives a long sequence of persisted deltas. Timestamped mode verifies historical reconstruction at each point in the delta chain; non-timestamped mode verifies final state. Compression/encryption broaden the physical encoding cases.

Dependencies and integration: depends on page-log delta apply, timestamp visibility, compression/encryption extensions, and both layered and file-backed disaggregated objects. Risks include chain-order errors, historical read regressions, encrypted/compressed delta decoding bugs, and URI-specific differences. Test signals are exhaustive key/value assertions at every relevant timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta05.py

Purpose: validates internal page delta writing and reading for disaggregated file tables under configurations that enable leaf only, internal only, both, or neither page-delta type.

Important APIs and functions: `test_layered_delta05` uses `page_delta=(delta_pct=100)`, small page sizes with `block_manager=disagg`, `stat.conn.rec_page_delta_leaf`, `stat.conn.rec_page_delta_internal`, `stat.conn.cache_read_internal_delta`, and helpers `insert`, `verify`, and `get_stat`.

Control flow: `test_internal_page_delta_simple` populates 1000 rows, reopens to force disk reads, updates a few keys, checkpoints, checks write statistics by configured delta type, reopens as leader and follower, and verifies internal delta reads. `test_internal_page_delta_split_internal` expands selected keys to force splits, then shrinks them to encourage internal-page merge deltas and verifies after reopen.

State and persistence behavior: the tests drive base images, leaf updates, and internal tree shape changes. Reopen clears cache so verification must reconstruct from stored full images and page deltas. Follower mode checks the same persisted state from a disaggregated consumer role.

Dependencies and integration: integrates page reconciliation, internal/leaf delta toggles, connection statistics, disaggregated reopen helpers, and page split/merge behavior. Risks include writing deltas despite disabled configuration, failing to read internal deltas, losing split/merge keys, and stat mismatches. Test signals combine statistic thresholds with full-table value verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta06.py

Purpose: verifies that an empty or non-durable delta candidate is skipped and does not produce a leaf page delta, while stable data remains readable by a follower.

Important APIs and functions: `test_layered_delta06` uses compression/encryption scenarios, layered and file URI variants, `page_delta=(delta_pct=80)`, `precise_checkpoint=true`, `disaggregated=(lose_all_my_data=true)`, `local_files_action=ignore` in follower reopen, `stat.conn.rec_page_delta_leaf`, and timestamped reads.

Control flow: the test loads 100 rows at timestamp 5, sets stable timestamp and checkpoints, writes one later update at timestamp 10, checkpoints, then reopens as follower with complete checkpoint metadata. It reads at timestamp 5 and asserts all original values are present, then checks the leaf delta write statistic is zero.

State and persistence behavior: the later update is intentionally not part of the stable view being validated, so reconciliation should not persist an empty meaningful delta for the follower's stable read. `local_files_action=ignore` preserves needed local checkpoint metadata during reopen.

Dependencies and integration: depends on disaggregated storage metadata handling, page delta skip policy, timestamp visibility, compression/encryption extension loading, and follower reopen behavior. Risks include writing useless deltas, deleting local metadata before follower open, or exposing unstable updates. Test signals are stable timestamp value checks and `rec_page_delta_leaf == 0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta07.py

Purpose: ensures durable entries are not redundantly included in new deltas, and that uncommitted or prepared updates cause reconciliation to skip page writes until they become durable. It covers normal updates, deletes, delete/update/restore, and prepared update/delete combinations.

Important APIs and functions: `test_layered_delta07` uses `page_delta=(delta_pct=100)`, `precise_checkpoint=true`, `preserve_prepared=true`, `stat.dsrc.rec_page_delta_leaf`, timestamp and oldest/stable timestamp advancement, prepared transaction APIs, explicit extra sessions, and debug eviction via `debug=(release_evict_page)`.

Control flow: each test loads ten rows, checkpoints stable base state, applies a durable update or delete and checkpoints to create a first delta. It then opens another session with uncommitted work and checkpoints again, asserting no new delta is written. Prepared tests checkpoint before and after commit/durable timestamp advancement and verify expected statistic increments.

State and persistence behavior: the file is mainly about reconciliation eligibility. Durable changes should appear once; uncommitted changes, prepared state, and already-durable deletes should not be reserialized into additional deltas. Oldest/stable timestamp changes are used to make deletes globally durable.

Dependencies and integration: depends on page delta reconciliation, timestamp/durable timestamp rules, prepared transaction preservation, data-source statistics, and eviction interaction. Risks include duplicate delta generation, including uncommitted updates in durable page state, or missing a committed prepared update. Test signals are exact `rec_page_delta_leaf` counts after each checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta08.py

Purpose: validates internal page deltas that record deleted child/leaf page references after large delete ranges in a disaggregated file table.

Important APIs and functions: `test_layered_delta08` uses small page sizes, `block_manager=disagg`, `page_delta=(internal_page_delta=true,leaf_page_delta=false)`, `stat.dsrc.rec_page_delta_internal_key_deleted`, `stat.dsrc.rec_page_delta_internal`, helpers `insert`, `delete_keys`, `verify`, and timestamped range verification.

Control flow: the test inserts 5000 rows, checkpoints, reopens to force disk state, deletes two large disjoint key ranges at later timestamps, advances oldest and stable timestamps before each checkpoint, and then verifies internal deleted-key delta stats. It checks the latest visible key set before and after reopening.

State and persistence behavior: the two delete ranges remove enough rows to affect multiple leaves and internal keys. Internal reconciliation should encode deleted child keys in deltas, and reopening should apply those deltas to reconstruct the tree with only expected keys present.

Dependencies and integration: integrates internal page delta encoding, deleted-child metadata, timestamped delete visibility, disaggregated file tables, and statistics. Risks include orphaned internal references, deleted keys remaining visible, internal delta not being written when leaf deltas are disabled, and reopen reconstruction failures. Test signals are statistic thresholds and per-key search/`WT_NOTFOUND` validation at the stable timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta09.py

Purpose: tests prefix and suffix compression interactions with page deltas. It ensures normal full-page compression stats behave as configured and that delta pages use expected prefix/suffix compression accounting while remaining readable on leader and follower.

Important APIs and functions: `test_layered_delta09` uses delta scenarios for leaf, internal, and both; `prefix_compression` table config; small page sizes; `stat.dsrc.rec_suffix_compression`, `rec_prefix_compression_full`, `rec_prefix_compression_delta`; `stat.conn.rec_page_delta_*`; and `stat.conn.cache_read_internal_delta`.

Control flow: `verify_compression` creates a table with or without prefix compression, inserts 1000 common-prefix keys, checkpoints, asserts full-page compression stats, reopens, updates a small key prefix range, checkpoints, checks delta stats, then verifies data after leader and follower reopens.

State and persistence behavior: common key prefixes create compression opportunities in base images and deltas. Reopens clear cache so both full image and delta compressed encodings must be decoded correctly. Follower mode validates the stored disaggregated representation.

Dependencies and integration: depends on page delta reconciliation, prefix/suffix compression counters, disaggregated reopen helpers, and internal delta read statistics. Risks include compression metadata mismatch between full images and deltas, delta reads failing when prefix compression is enabled, and stats changing under leaf/internal-only modes. Test signals are compression stat assertions plus complete key/value checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta10.py

Purpose: confirms page delta generation is suppressed when reconciliation splits a page, while a similar non-splitting update produces a leaf delta.

Important APIs and functions: `test_layered_delta10` uses split scenarios, `page_delta=(delta_pct=100,internal_page_delta=true,leaf_page_delta=true)`, small `allocation_size`, `leaf_page_max`, `split_pct`, data-source stats `btree_row_leaf` and `rec_page_delta_leaf`, and `reopen_conn`.

Control flow: the test creates one near-4KB leaf page, reopens and asserts one row leaf. In `page_split` mode it updates one row and appends more rows to exceed the split threshold, checkpoints, asserts zero leaf deltas, reopens, and expects two leaf pages. In `page_no_split` mode it only updates one row, checkpoints, expects one leaf delta, and still one leaf page.

State and persistence behavior: reconciliation has two possible outputs: a structural split requiring full page images, or a small content update eligible for delta encoding. The test distinguishes those paths through statistics and physical leaf count after reopen.

Dependencies and integration: integrates page split policy, delta generation policy, layered disaggregated tables, and data-source statistics. Risks include generating deltas across structural splits, suppressing deltas for ordinary updates, or page-size dependent fragility. Test signals are exact leaf-page and delta-count assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta11.py

Purpose: verifies that internal page deltas are not built when modifications affect the first key or otherwise change separator-key assumptions in ways unsafe for delta encoding.

Important APIs and functions: `test_layered_delta11` uses `DisaggConfigMixin`, `disaggregated=(page_log=palite)`, `page_delta=(delta_pct=100)`, `stat.dsrc.rec_page_delta_internal`, randomized/string data generation, checkpointing, and standard cursor insert/remove/update operations.

Control flow: `test_single_update` modifies the first key after an initial checkpoint. `test_inserts_to_split` inserts keys that force tree shape changes around the first key and split behavior. `test_deletes` removes keys and checkpoints. Each test reads data-source stats and asserts no internal page delta is created.

State and persistence behavior: internal page deltas depend on stable separator-key mapping. Changes to first keys, splits, and deletes can invalidate a compact internal-delta representation; these scenarios should fall back to safer full-page behavior.

Dependencies and integration: depends on palite page log, disaggregated page delta logic, internal tree reconciliation, and statistics. Risks include unsafe internal delta generation that loses separator keys or corrupts navigation after reload. Test signals are exact zero `rec_page_delta_internal` assertions after targeted mutations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta12.py

Purpose: broader internal page delta correctness coverage for disaggregated file tables. It covers internal updates, inserting keys at the end of a base image, base images that have extra tail keys during merge, and keys updated multiple times.

Important APIs and functions: `test_layered_delta12` uses page-delta scenarios for leaf-only, internal-only, both, and none; large cache, small page sizes, `stat.conn.rec_page_delta_internal`, `rec_page_delta_leaf`, `cache_read_internal_delta`, helpers `insert`, `verify`, and `get_stat`.

Control flow: each test creates a dense table, checkpoints a base image, applies a pattern of timestamped key/value changes, checkpoints, checks write statistics according to delta configuration, reopens, and verifies merged values. Some tests compare internal delta read counts before and after reopen to ensure internal deltas were actually consumed.

State and persistence behavior: these tests exercise merge boundaries where modified keys are at the end of the base image, where base images contain more keys than the delta side, and where one key has multiple updates. The expected persisted state is a merge of unchanged initial values plus targeted modifications.

Dependencies and integration: integrates internal/leaf delta configuration, page-log apply, connection statistics, timestamped writes, and full-table verification. Risks include key-order merge bugs, tail-key loss, repeated-update collapse errors, and misreporting delta type. Test signals are statistic assertions and exhaustive key/value verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta13.py

Purpose: verifies eviction with uncommitted updates in a disaggregated file table and checks that writes still reach cache/write statistics without committing unstable data.

Important APIs and functions: `test_layered_delta13` uses `WiredTigerCursor` and `statistic_uri` imports from `helper`, `stat.dsrc.cache_write`, `debug=(release_evict_page)` eviction cursor behavior, timestamped base writes, and normal transaction control.

Control flow: the test creates a disaggregated file table, writes base rows with timestamps, sets a stable timestamp, opens another session with uncommitted work, and uses a debug eviction session to evict/search a key. It then reads data-source cache write statistics and asserts writes occurred.

State and persistence behavior: base rows are stable, while the concurrent transaction remains uncommitted. The eviction path must handle dirty/uncommitted state without persisting it incorrectly, while still exercising cache write behavior.

Dependencies and integration: integrates disaggregated file tables, debug eviction hooks, transaction isolation, timestamp state, and data-source statistics. Risks include evicting uncommitted updates into durable page state, failing eviction under dirty pages, or statistics not reflecting writes. Test signals are a positive `cache_write` statistic after the eviction exercise.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta14.py

Purpose: tests that reconciliation skips writing full pages when it does not make progress, with leaf page deltas disabled and precise checkpointing enabled.

Important APIs and functions: `test_layered_delta14` uses a layered table, `page_delta=(leaf_page_delta=false)`, `precise_checkpoint=true`, `checkpoint_and_verify_stats`, `wiredtiger.stat.dsrc.rec_page_full_image_leaf`, timestamped writes, and the disaggregated leader role.

Control flow: the test creates a layered table, inserts data, advances timestamps, and performs checkpoints while verifying full-page image statistics. It drives a case where reconciliation should recognize no progress and avoid unnecessary full-page writes.

State and persistence behavior: with leaf deltas disabled, reconciliation might otherwise fall back to full images. The intended behavior is to skip page writes when the durable page image would not advance useful state. Timestamps define which writes are eligible for checkpoint materialization.

Dependencies and integration: depends on layered disaggregated reconciliation, precise checkpoint accounting, page delta configuration, and WiredTiger test helper `checkpoint_and_verify_stats`. Risks include excessive full-page writes, checkpoint churn, or stats failing to distinguish skipped pages. Test signals are the expected full-image leaf statistic values observed through the helper.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_delta15.py

Purpose: randomized high-volume internal page delta coverage across encryption, compression, URI type, timestamped/non-timestamped operation, and delta configuration scenarios.

Important APIs and functions: `test_layered_delta15` uses `DisaggConfigMixin`, palite page log, compressor/encryptor extensions, URI scenarios for layered and file tables, `page_delta` variants including leaf-only and none, 10,000-item randomized key/value sets, `stat.conn.rec_page_delta_internal`, `rec_page_delta_leaf`, and `cache_read_internal_delta`.

Control flow: the test creates a small-page table, inserts many randomized records, checkpoints, applies a randomized subset of modifications with optional commit timestamps, checkpoints again, verifies stats according to delta mode, reopens, and validates all expected values against the initial state plus modifications.

State and persistence behavior: the file stresses realistic random internal-tree shapes and values. Timestamped mode requires stable timestamp advancement before checkpoints; non-timestamped mode verifies latest state. Reopen forces reconstruction from stored images/deltas under compression and encryption combinations.

Dependencies and integration: integrates page-log delta encoding, random workload generation, compression/encryption, layered/file disaggregated URIs, timestamp logic, and stats. Risks include nondeterministic flakiness from random data, encoded delta corruption under compression/encryption, internal-delta reads when disabled, and large scenario runtime. Test signals are statistic expectations per delta mode and full data verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_delta15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction01.py

Purpose: ensures a follower does not evict pages ahead of the materialization frontier, and that checkpoint/materialization accounting protects pages that are not yet safe to discard.

Important APIs and functions: `test_layered_eviction01` uses follower role disaggregated config, `disaggregated=(lose_all_my_data=true)`, `stat.conn.cache_eviction_ahead_of_last_materialized_lsn`, `cache_eviction_blocked_precise_checkpoint`, `cache_scrub_restore`, `checkpoint_pages_reconciled_bytes`, `conn.set_context_uint`, page-log `pl_set_last_materialized_lsn`, and a debug eviction cursor helper.

Control flow: the test creates a large layered table, writes many records, checkpoints, manipulates materialized LSN context, reads and evicts ranges with debug eviction, changes connection configuration, and asserts eviction is blocked or counted when pages are ahead of the frontier.

State and persistence behavior: the central state is page-log materialization frontier versus page LSN. Pages ahead of that frontier must remain available in cache or be restored rather than discarded, even under eviction pressure. Timestamps and checkpoints control page reconciliation.

Dependencies and integration: integrates disaggregated follower behavior, page-log frontier APIs, eviction debug hooks, statistics, and precise checkpoint interactions. Risks include data loss from evicting unmaterialized pages, stuck cache if all eviction is blocked, and incorrect frontier stat accounting. Test signals are statistic thresholds, exception assertions, and successful reads around forced eviction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction02.py

Purpose: verifies clean eviction can occur on a follower/standby without explicitly setting a page materialization frontier.

Important APIs and functions: `test_layered_eviction02` uses leader and follower disaggregated connection configs, `disagg_advance_checkpoint`, `stat.conn.cache_eviction_clean`, debug eviction with `debug=(release_evict_page)`, and timestamped leader writes.

Control flow: the leader creates a table, inserts a small timestamped dataset, sets stable timestamp, checkpoints, and advances a follower. The follower opens a debug eviction session and evicts a key. The test reads follower statistics and asserts clean eviction increased.

State and persistence behavior: all data is stable checkpointed state. The follower should be able to discard clean pages without a materialization frontier because no dirty or ahead-of-frontier page state is involved.

Dependencies and integration: depends on follower checkpoint synchronization, eviction debug hooks, clean eviction stats, and layered/disaggregated table visibility. Risks include overly conservative frontier checks that block clean eviction or follower eviction paths that require unavailable leader-only state. Test signals are successful eviction search and positive `cache_eviction_clean`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction03.py

Purpose: ensures follower application threads skip eviction of pages with updates or dirty state, rather than doing unsafe app-thread eviction work in disaggregated follower mode.

Important APIs and functions: `test_layered_eviction03` uses follower disaggregated config, a small cache, random string generation, large inserted values, and `stat.conn.cache_eviction_app_threads_skip_updates_dirty_page`.

Control flow: the test creates enough data in a follower-role connection to apply cache pressure and dirty/update state. It then reads the connection eviction statistic and asserts the skip counter is greater than zero.

State and persistence behavior: follower pages with dirty updates are not supposed to be evicted by application threads. The test's state is intentionally cache-pressure-heavy and follower-local, so eviction policy should choose to skip rather than reconcile unsafe pages.

Dependencies and integration: integrates follower role eviction policy, cache pressure, random data generation, and connection statistics. Risks include app threads evicting dirty follower pages, missing skip accounting, or cache pressure behavior changing enough to make the test flaky. Test signal is a positive skip statistic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction04.py

Purpose: verifies that closing/verifying a file with pages not yet materialized fails rather than silently evicting unsafe pages.

Important APIs and functions: `test_layered_eviction04` uses leader disaggregated config, layered table creation, timestamped writes, `conn.set_context_uint`, page-log `pl_set_last_materialized_lsn`, `session.verify`, `assertRaises`, and `wiredtiger.WiredTigerError`.

Control flow: the test creates and populates a layered table, checkpoints, manipulates materialization LSN state so pages are considered not fully materialized, and then attempts operations such as verify/close that force eviction or file cleanup. It asserts the expected error path is taken.

State and persistence behavior: page data exists in the page log, but the materialization frontier says it is not safe to evict/close. The test ensures the system preserves safety by returning an error rather than discarding or closing around unmaterialized pages.

Dependencies and integration: integrates page-log frontier context, layered table lifecycle, verify/close behavior, and Python exception assertions. Risks include silent data loss during file close, frontier checks being bypassed by verify, or errors being swallowed. Test signals are explicit `WiredTigerError` assertions plus successful setup writes and checkpointing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction05.py

Purpose: ensures obsolete time window cleanup is not reviewed for read-only btrees on followers.

Important APIs and functions: `test_layered_eviction05` inherits `eviction_util` and `WiredTigerTestCase`, uses leader and follower disaggregated configs, `stat.conn.cache_eviction_dirty_obsolete_tw`, `stat.dsrc.cache_eviction_dirty_obsolete_tw`, helper `read`, and `get_stat` from eviction utilities.

Control flow: the leader/follower setup writes checkpointed data, the follower reads rows to bring pages into cache, and the test checks obsolete time window eviction statistics. It expects no dirty obsolete-time-window cleanup activity for the follower read-only btree path.

State and persistence behavior: the follower should observe stable checkpointed data without making btree pages dirty for obsolete time window cleanup. The test guards a read-only invariant: follower reads must not trigger dirty reconciliation work that belongs to writable btrees.

Dependencies and integration: integrates eviction utility helpers, follower connection config, layered table reads, and eviction/time-window stats. Risks include read-only follower pages being dirtied, unexpected reconciliation on followers, and stat accounting regressions. Test signals are zero equality assertions for obsolete time-window dirty eviction stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction06.py

Purpose: regression coverage for dirty disaggregated leaves that reconcile to a skip-write single-block replace while ahead of the materialization frontier. Such pages must stay in cache rather than being discarded and later faulted in ahead of the frontier.

Important APIs and functions: `test_layered_eviction06` uses leader disaggregated config, `stat.conn.disagg_block_read_ahead_frontier`, debug eviction transactions, helper `advance_frontier`, page-log `pl_set_last_materialized_lsn`, `conn.set_context_uint`, timestamped writes, checkpoints, and separate read sessions.

Control flow: the test creates a layered table, writes and checkpoints data, manipulates the materialization frontier, triggers eviction with debug cursors, advances frontier at controlled points, and reads back rows. It samples the ahead-frontier block-read statistic to ensure the unsafe fault-in path is not taken.

State and persistence behavior: the key state is a dirty page whose reconciliation can skip writing because the disk image appears replaceable, but whose materialization frontier still makes discard unsafe. Correct behavior retains or restores the page in cache until it is safe.

Dependencies and integration: integrates page-log frontier APIs, dirty page reconciliation, eviction, skip-write replace behavior, and connection statistics. Risks include discarding scrubbed disk images, reading blocks ahead of frontier, stale page restoration, and data loss after eviction. Test signals are exact read assertions, controlled frontier advancement checks, and no unexpected increase in `disagg_block_read_ahead_frontier`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_eviction06.py -->
