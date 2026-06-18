# subset-b-009086 grouped research

Grouped research for the WiredTiger Python suite files assigned to subset-b-009086. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_cursor01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_cursor01.py

Purpose: validates `WT_CURSOR.next` and `WT_CURSOR.prev` behavior when cursor movement encounters prepared inserts, updates, and removes. It runs row-store/table scenarios under read-committed and snapshot isolation, while timestamp hooks are disabled so exact prepare, commit, and durable timestamps are controlled by the test.

Important APIs and types: `wttest.WiredTigerTestCase`, `SimpleDataSet`, `make_scenarios`, `wiredtiger.WT_NOTFOUND`, `wiredtiger.WiredTigerError`, session `begin_transaction`, `prepare_transaction`, `timestamp_transaction`, `commit_transaction`, cursor `search`, `next`, `prev`, `insert`, `update`, `remove`, `get_key`, and `get_value`.

Control flow: the test creates keys 2-50, then cycles through four scenarios: prepared insert at both ends, prepared update at both ends, prepared remove at both ends, and prepared remove inside the key range. For each scenario, it positions four readers: before the prepare timestamp, between prepare and commit, after commit, and non-timestamped. It asserts prepare conflicts while the update is unresolved, then commits the prepared transaction and verifies timestamp visibility and cursor position recovery.

State and persistence behavior: all state is local to one table, but the test stresses update chains with prepared state and timestamp visibility. It verifies that prepared updates block reads at and after the prepare timestamp until resolution, that pre-prepare readers keep seeing older state, and that after commit the resolved insert/update/remove is visible according to commit timestamp.

Dependencies and integration points: this is a cursor-navigation regression test integrated with WiredTiger timestamp semantics, prepare conflict detection, and the Python scenario runner. It deliberately excludes column-store scenarios through `include=keep` because the scenario matrix only keeps non-recno keys.

Risks: cursor state after a prepare conflict is subtle; the test explicitly moves the conflicted cursor in the opposite direction before retrying, guarding against stale positioning and repeated-conflict bugs. Timestamp changes must remain ordered or the assertions become misleading.

Test signals: success is no unexpected `WiredTigerError`, expected prepare conflicts on unresolved prepared records, correct `WT_NOTFOUND` at range boundaries, and exact key/value checks after commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_cursor01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_cursor02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_cursor02.py

Purpose: verifies that a reader encountering a single prepared insert in an otherwise empty table receives repeated prepare conflicts for `search`, `next`, and `prev`, rather than silently skipping or corrupting cursor position.

Important APIs and types: `WiredTigerTestCase`, `SimpleDataSet`, `make_scenarios`, `wiredtiger.WiredTigerError`, session `prepare_transaction`, cursor `search`, `next`, `prev`, and scenario coverage for row-store integer keys and column-store recno keys.

Control flow: the main session inserts key 1 and prepares at timestamp 100. A second session starts a transaction and opens a cursor on the same URI. It sets key 1, asserts `search` raises a prepare conflict, then calls `next` twice and expects both to raise. It repeats the pattern for `prev`. The prepared writer is rolled back at the end.

State and persistence behavior: no checkpoint or recovery is involved; the durable state remains empty after rollback. The key state is an in-memory prepared update visible enough to block conflicting cursor operations.

Dependencies and integration points: integrates prepare conflict handling with bidirectional cursor navigation and both row/column key formats through `wtscenario`.

Risks: repeated calls after an error can expose cursor reset bugs. The test relies on the default session configuration for the reader; changes to isolation defaults could affect conflict timing.

Test signals: every read attempt against the prepared key raises `WiredTigerError`; no operation returns a found key or `WT_NOTFOUND` while the prepare is unresolved.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_cursor02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover01.py

Purpose: tests that a pending prepared transaction persisted in a checkpoint/backup can be discovered after reopening and rolled back through `prepared_discover:`.

Important APIs and types: `suite_subprocess.backup`, `wiredtiger_open`, `prepared_discover:` cursor, `claim_prepared_id`, `rollback_transaction(rollback_timestamp=...)`, timestamp setters, and `prepared_id_str`.

Control flow: it creates committed keys at timestamp 60, prepares keys 3-5 at timestamp 100 with prepared id 123, advances stable to 150, checkpoints, and backs up the home. The backup is opened with `precise_checkpoint=true,preserve_prepared=true`; a prepared-discover cursor is walked, the id is claimed, and the transaction is rolled back at timestamp 200.

State and persistence behavior: the key feature is preserving prepared artifacts in the backup checkpoint and resolving them in the reopened copy. Rolling back should remove the prepared inserts while leaving timestamp-60 data intact.

Dependencies and integration points: integrates backup copying, recovery/open, prepared transaction metadata, and discover-cursor iteration. The scenario matrix only includes row-store integer keys and a commit-ended setup.

Risks: the discovered key is asserted as integer 123, so `prepared_id_str` and cursor key encoding must stay consistent. Failure to claim before close would violate discover cursor protocol.

Test signals: exactly one prepared id is discovered and rollback completes without error.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover02.py

Purpose: validates the commit path for a prepared transaction discovered from a preserved backup checkpoint, including timestamped read visibility before and after the commit timestamp.

Important APIs and types: `prepared_discover:`, `claim_prepared_id`, `commit_transaction(commit_timestamp=...,durable_timestamp=...)`, `wiredtiger.WT_NOTFOUND`, timestamped read transactions, and backup/open helpers.

Control flow: after writing committed keys 1-2 at timestamp 60, it prepares keys 3-5 with id 123 at timestamp 100, advances stable, checkpoints, backs up, and opens the backup. It discovers and claims id 123, commits it at commit timestamp 200/durable 210, then reads at timestamp 60 and 200.

State and persistence behavior: before commit timestamp 200, only the original committed keys must be visible. At read timestamp 200, the prepared keys become committed and visible. The test exercises persisted prepared metadata and subsequent visibility in the same reopened backup home.

Dependencies and integration points: tied to `preserve_prepared=true`, precise checkpoints, backup copying, and timestamp visibility rules in the storage engine.

Risks: loops for read checks set constant keys inside the loop in the source, so the test verifies representative values rather than every intended key. The primary signal remains commit visibility of the discovered prepared transaction.

Test signals: exactly one discovered id, no duplicate claims, `WT_NOTFOUND` for keys 3-5 at timestamp 60, and successful reads of prepared values at timestamp 200.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover03.py

Purpose: ensures `prepared_discover:` reports an error if it is closed while another persisted prepared transaction remains unclaimed, and that an already claimed prepared id cannot be claimed again.

Important APIs and types: `prepared_discover:`, `claim_prepared_id`, `assertRaisesWithMessage`, `wiredtiger.WiredTigerError`, backup/reopen helpers, and two separate prepared transactions with ids 123 and 150.

Control flow: it creates committed baseline data, then prepares one insert transaction with id 123 and another update transaction with id 150. After stable advancement, checkpoint, backup, and reopen, it walks the discover cursor, claims and commits only the first prepared id, breaks the loop, tries to claim id 123 again, and finally closes the discover cursor expecting an error about one unclaimed prepared transaction.

State and persistence behavior: persisted prepare metadata must track both unclaimed and claimed states. Closing the discover cursor is part of the correctness contract because unresolved prepared artifacts must not be ignored.

Dependencies and integration points: exercises recovery, backup, prepared metadata accounting, duplicate-claim rejection, and discover cursor close validation.

Risks: the loop asserts discovered id 123, so ordering matters; if discovery order changes, this test may become brittle unless the implementation preserves deterministic id order.

Test signals: duplicate claim raises `WiredTigerError`, and closing the cursor raises a message matching `Found 1 unclaimed prepared transactions`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover04.py

Purpose: verifies a prepared delete captured in a backup checkpoint can be discovered and resolved by either commit or rollback, then checkpointed after stable timestamp advancement.

Important APIs and types: `prepared_discover:`, `claim_prepared_id`, cursor `remove`, `commit_transaction` with durable timestamp, `rollback_transaction` with rollback timestamp, `make_scenarios` for commit and rollback endings.

Control flow: the test commits two baseline keys at timestamp 60, prepares deletes of both keys with prepared id 150 at timestamp 100, advances stable to 150, checkpoints, and backs up. In the reopened backup it walks `prepared_discover:`, claims the id, commits at 200/210 or rolls back at 200 according to the scenario, then advances stable to 220 and checkpoints.

State and persistence behavior: prepared tombstones are persisted through backup and then resolved in the copied database. The final checkpoint verifies the resolved prepared delete state can be made durable.

Dependencies and integration points: backup subsystem, timestamped deletes, prepare metadata, and checkpoint after resolution.

Risks: the test does not perform post-resolution reads, so its main failure surface is discovery/claim/checkpoint stability rather than logical value assertion. It still covers a historically risky prepared tombstone path.

Test signals: exactly one prepared id is discovered, resolution completes, stable timestamp can advance, and checkpoint finishes without error.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover05.py

Purpose: regression test for prepared delete artifacts that are resolved after discovery, then forced through eviction and checkpoint verification without crashing while unpacking prepared cells written by eviction.

Important APIs and types: same `test_prepare_discover04` class/name pattern in the source, `prepared_discover:`, `claim_prepared_id`, `release_evict_page`, `ignore_prepare=true`, and scenario-driven commit/rollback resolution.

Control flow: it mirrors the prepared-delete setup: baseline keys at timestamp 60, prepared removes with id 150, checkpoint, backup, reopen, discover and resolve. After resolution it opens a debug eviction session, reads keys under `ignore_prepare=true` to force page release, rolls back the eviction transaction, and runs checkpoint.

State and persistence behavior: the test focuses on disk-format and reconciliation safety. Eviction may write prepared/resolved state to disk; checkpoint verification must be able to unpack those cells after the discover/claim flow.

Dependencies and integration points: integrates prepared discovery with eviction debug hooks, reconciliation, and checkpoint disk verification. It depends on the suite subprocess backup helper.

Risks: the class and method names still say `test_prepare_discover04`, which can confuse test reporting and research indexing. The behavior is distinct from file 04 because of the forced eviction path.

Test signals: one prepared id discovered, resolution succeeds, eviction under `ignore_prepare=true` completes, and checkpoint does not crash.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover06.py

Purpose: tests prepared transaction discovery for layered tables in disaggregated storage, with leader checkpoint handoff to a follower and commit/rollback resolution.

Important APIs and types: `@disagg_test_class`, `gen_disagg_storages`, `layered:` URI, `disaggregated=(role="leader"/"follower",checkpoint_meta=...)`, `disagg_get_complete_checkpoint_meta`, `prepared_discover:`, and `claim_prepared_id`.

Control flow: the leader creates a layered table, writes baseline committed data, prepares additional inserts, advances stable, checkpoints, captures checkpoint metadata, and reopens as a follower using that metadata. The follower verifies committed data, discovers the prepared id, claims it, commits or rolls it back according to scenario, advances stable, and verifies reads after resolution.

State and persistence behavior: prepared updates are persisted in the disaggregated checkpoint and transferred via checkpoint metadata rather than a backup directory. The test validates that follower resolution changes layered-table visibility consistently after stable advancement.

Dependencies and integration points: disaggregated storage helper infrastructure, layered table support, prepared metadata preservation, timestamped reads, and role reconfiguration.

Risks: layered/disaggregated tests are sensitive to checkpoint metadata format and role semantics. Scenario expansion can be expensive because it combines storage variants with commit/rollback resolution.

Test signals: committed keys remain visible at old timestamps, exactly one prepared id is discovered, and prepared keys are visible only for commit resolution and absent for rollback resolution at later timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover07.py

Purpose: validates the analogous disaggregated layered-table flow for a prepared tombstone transaction, ensuring committed values are deleted on commit and preserved on rollback.

Important APIs and types: `layered:` cursor, `prepared_discover:`, `claim_prepared_id`, `wiredtiger.WT_NOTFOUND`, disaggregated leader/follower configuration, checkpoint metadata, and commit/rollback scenarios.

Control flow: leader commits keys 1-6, prepares removes for keys 4-6 with id 123, checkpoints with stable timestamp after the prepare, and reopens as a follower from checkpoint metadata. The follower discovers and claims the id, commits or rolls back it, then reads at timestamp 60 and 200/220 to assert final state.

State and persistence behavior: the prepared tombstone is captured in the stable checkpoint chain. Commit resolution makes keys 4-6 not found at later read timestamps; rollback resolution restores their committed values.

Dependencies and integration points: disaggregated storage, layered table ingest/stable components, prepare discovery, timestamped deletion visibility, and role handoff.

Risks: the source contains a `self.session.breakpoint()` inside validation, which may be intentional debug support but is notable because breakpoints can affect automated runs depending on harness behavior.

Test signals: exactly one id 123 is discovered, baseline keys always read correctly, and keys 4-6 match the expected found/not-found behavior for commit versus rollback.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover08.py

Purpose: ensures `prepared_discover:` can be the first cursor opened on a reopened layered-table connection, for both follower and leader reopen roles.

Important APIs and types: `role_scenarios`, `disagg_test_class`, `prepared_discover:`, `claim_prepared_id`, `reopen_conn`, `disagg_get_complete_checkpoint_meta`, and `prepared_id_str`.

Control flow: the leader commits baseline keys, prepares inserts for keys 4-6, advances stable, checkpoints, closes the table cursor, and reopens either as follower with checkpoint metadata or as leader. Without opening any data cursor first, it opens `prepared_discover:`, discovers id 123, claims and commits it at 200/210, and closes the cursor.

State and persistence behavior: discovery must initialize or access layered-table prepared metadata without relying on prior table cursor open side effects. Prepared inserts are committed in the reopened connection.

Dependencies and integration points: layered/disaggregated table open paths, discover cursor initialization, checkpoint metadata pickup, and role-specific connection open behavior.

Risks: this is a startup/order-of-operations regression test; future lazy-open changes to layered tables must keep discover cursor discovery independent of ordinary table cursor opens.

Test signals: the discovered id list is exactly `[123]`, and cursor close succeeds because all discovered prepared transactions were claimed and committed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover09.py

Purpose: verifies a single prepared transaction spanning both a layered table and a non-layered local table is surfaced once by follower `prepared_discover:` and resolved consistently for all participating tables.

Important APIs and types: `@skip_for_hook("tiered")`, `@disagg_test_class`, `local_uri`, `layered_uri`, helper methods `populate_and_prepare`, `reopen_as_follower`, `discover_and_resolve`, `assert_table_state`, `claim_prepared_id`, and commit/rollback scenarios.

Control flow: both tables are created and receive committed keys 1-3 at timestamp 60. One transaction writes prepared keys 4-6 to both tables with prepared id `0x1234`, stable advances, and the leader checkpoints. After reopening as follower, the discover cursor claims and commits or rolls back the id, then each table is read at timestamp 250.

State and persistence behavior: prepared metadata must represent a cross-table transaction as one prepared id. Resolution must atomically affect all written btrees, not just the layered table.

Dependencies and integration points: disaggregated checkpoint transfer, local non-logged table handling, layered table ingest, timestamp visibility, and prepared transaction coordinator metadata.

Risks: cross-table resolution is a broad integration surface; partial application would leave divergent local/layered state. Tiered storage is skipped because layered tables are unsupported there.

Test signals: discovered ids equal `[0x1234]`; committed keys are always visible; prepared keys are visible after commit resolution and `WT_NOTFOUND` after rollback resolution on both URIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover10.py

Purpose: tests that a prepared transaction reclaimed on a follower through `claim_prepared_id` survives step-up even though the reclaim session has no normal transaction id, and then resolves correctly after step-up.

Important APIs and types: properties `uri_b` and `_uris`, `multi_table` scenarios, disaggregated role reconfiguration, `prepared_discover:`, `claim_prepared_id`, `timestamp_transaction`, and checkpoint helpers.

Control flow: the leader creates one or two layered tables, commits baseline keys, prepares inserts for keys 4-6 with id 12345, checkpoints, rolls back the leader-side transaction, and closes without checkpoint. The follower discovers and claims the prepared id but keeps the claim live, steps up to leader, then commits or rolls back the claimed transaction. It checkpoints and reads both before and after resolution timestamps.

State and persistence behavior: step-up drain must match operations by prepared id rather than transaction id and patch operations onto the stable btree. Multi-table scenarios verify this logic across multiple layered tables.

Dependencies and integration points: disaggregated ingest drain, prepared id metadata, role step-up, layered-table timestamp visibility, and checkpointing after resolution.

Risks: this covers a narrow metadata matching path; failures can appear as successful discovery followed by missing or stale data after step-up.

Test signals: discovered id list is `[12345]`; keys 4-6 are absent at timestamp 60; at timestamp 220 they contain prepared values for commit resolution and are absent for rollback resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover11.py

Purpose: verifies that a follower-claimed prepared transaction committed before step-up remains readable after stable timestamp advancement, eviction, and follower step-up to leader.

Important APIs and types: helper methods `_open_follower` and `_checkpoint`, `prepared_discover:`, `claim_prepared_id`, `timestamp_transaction`, `release_evict_page`, disaggregated role reconfigure, and timestamped reads.

Control flow: leader commits keys 1-3, prepares keys 4-6 with id 99999, checkpoints, rolls back locally, and closes. The follower opens from checkpoint metadata, discovers id 99999, claims and commits it at timestamp 200, advances stable to 250, forces eviction of keys 4-6, steps up to leader, checkpoints, and validates reads at timestamps 60 and 220.

State and persistence behavior: the committed prepared updates must survive eviction from follower memory and be properly drained during role step-up. They are invisible before the prepare/commit timeline and visible after commit timestamp.

Dependencies and integration points: prepared discovery, follower ownership of claim, stable timestamp advancement, eviction, disaggregated step-up drain, and layered table read paths.

Risks: bugs here can be masked if pages remain in memory; the explicit eviction is essential because it forces disk/restoration behavior.

Test signals: exactly `[99999]` is discovered; keys 4-6 are not found at timestamp 60 and equal prepared values at timestamp 220 after step-up.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover12.py

Purpose: validates that a prepared insert rolled back on a follower stays absent after step-up and checkpoints, including when a newer regular commit on the same key is written before step-up.

Important APIs and types: helper methods `_open_follower`, `_checkpoint`, `_evict_key`, `_create_leader_baseline`, `_prepare_then_rollback`, `_commit_value`, `_set_stable_and_checkpoint`, `_assert_search`, `wiredtiger.WT_NOTFOUND`, and disaggregated role reconfiguration.

Control flow: each test creates a leader baseline key, checkpoints, closes, opens a follower, performs and rolls back a prepared insert at key 1, then steps up to leader. One path only checks the rolled-back insert; the other also commits a newer value at timestamp 150. Both paths checkpoint at stable timestamps around the rollback/newer commit, evict the key, advance stable, and assert reads.

State and persistence behavior: rollback timestamps must be reflected in persisted key state. After rollback, key 1 is absent until any newer committed value becomes visible, while the unrelated baseline key remains intact.

Dependencies and integration points: follower-side prepared rollback, stable checkpoint durability, eviction/reload, disaggregated step-up, and timestamp visibility.

Risks: same-key rollback plus newer commit is a high-risk update-chain ordering case. Eviction ensures the test covers disk state, not only memory.

Test signals: key 1 is `WT_NOTFOUND` after rollback-only flow; in the newer-commit flow it is absent at timestamp 120 and has `newer_committed_value` at timestamp 160.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover13.py

Purpose: regression coverage for history-store orphans surviving disaggregated step-up drain because prepared metadata on ingest btrees was hidden or lost.

Important APIs and types: helper methods `open_follower`, `create_hs_orphan_and_close_leader`, `finish_leader_checkpoint_and_close`, `trigger_panic_via_eviction`, `prepared_discover:`, `claim_prepared_id`, `wiredtiger.stat.conn.cache_hs_insert`, eviction debug cursors, and disaggregated role reconfiguration.

Control flow: `create_hs_orphan_and_close_leader` builds a version chain with committed `v_base`, committed `v0`, and prepared `v1`, advances stable, evicts under `ignore_prepare=true`, and asserts HS insertion. Path 1 checkpoints at prepare timestamp, follower claims and commits, writes `v2`/`v3`, advances oldest/stable so the version cursor might truncate, steps up, then writes `v4`/`v5` and evicts. Path 2 checkpoints later, claims/commits, writes `v2`/`v3`, evicts the ingest page so prepared id metadata could be dropped, steps up, then triggers eviction.

State and persistence behavior: the central state is an HS record whose stop timestamp would remain orphaned unless step-up drain sees the resolved prepared entry with its prepared id. Correct behavior is absence of panic during later eviction.

Dependencies and integration points: history store, prepared metadata, ingest btree, disaggregated follower-to-leader step-up, eviction, and statistics.

Risks: this is a negative regression test where the main symptom is no crash. It depends on carefully constructed timestamp and eviction order.

Test signals: HS insertion statistic is positive, discover finds at least one id, and the final eviction sequence completes without out-of-order timestamp panic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover15.py

Purpose: ensures a follower-claimed prepared transaction that is rolled back and checkpointed does not resurface in a later `prepared_discover:` pass on the same checkpoint chain.

Important APIs and types: helper methods `_open_follower`, `_checkpoint`, `_discover_prepared_ids`, `prepared_discover:`, `claim_prepared_id`, `rollback_transaction`, and disaggregated role switches.

Control flow: the leader writes baseline values, prepares updates on several keys with id 17304, checkpoints while prepared, rolls back locally, and closes without checkpoint. The follower discovers and claims the id, rolls it back, steps up to leader, advances stable past rollback timestamp, checkpoints, steps back down to follower, and runs discover again.

State and persistence behavior: rollback resolution must be durable in the post-rollback checkpoint. Once rolled back, the prepared id should not be discoverable again from later checkpoint metadata.

Dependencies and integration points: prepared discovery lifecycle, follower claim rollback, checkpoint durability, role transition, and discover cursor empty/error handling.

Risks: `_discover_prepared_ids` treats an open error as empty, so the key signal is absence of the original id rather than distinction between no prepared content and unavailable cursor.

Test signals: initial discovery returns `[17304]`, and the later discovered id list does not contain `17304`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover16.py

Purpose: validates that a prepared delete captured by a checkpoint and rolled back through follower discovery leaves the original committed stable value readable by a fresh follower after post-rollback checkpointing.

Important APIs and types: `stable_uri`, helper methods `_open_follower`, `_checkpoint`, `_discover_and_claim`, direct cursor open on `file:<tablename>.wt_stable`, `prepared_discover:`, `claim_prepared_id`, and `wiredtiger.WiredTigerError` handling.

Control flow: the leader creates a layered table, commits many keys, prepares a delete of target key 500 with a prepared id, checkpoints while prepared, and closes without final checkpoint. The follower discovers and claims the prepared id, rolls it back, steps up, advances stable, checkpoints, captures post-rollback metadata, closes, and opens a fresh follower. The fresh follower reads the stable constituent directly at timestamp 300.

State and persistence behavior: the rollback must be encoded durably in the stable checkpoint chain, not only masked by ingest state. Directly reading the stable file checks the underlying committed value.

Dependencies and integration points: layered stable constituent files, disaggregated checkpoint metadata, prepared delete rollback, fresh follower open, and timestamped reads.

Risks: direct access to `*.wt_stable` is tightly coupled to layered table implementation details but gives stronger evidence than reading the layered URI.

Test signals: discovery returns the expected id; fresh follower open succeeds; searching target key in the stable URI returns 0 and value `committed_value`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_discover16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_hs01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_hs01.py

Purpose: verifies history-store eviction works correctly when many prepared updates are present and older committed versions must remain readable.

Important APIs and types: `SimpleDataSet`, `make_scenarios`, `conn_config` with small cache and eviction update thresholds, helper methods `check` and `prepare_updates`, timestamped reads, and multiple independent sessions with prepared transactions.

Control flow: the test populates a large table, checkpoints, commits many large values at timestamp 2, then opens three sessions and prepares ranges of updates at timestamp 3. It reads at timestamp 2 to ensure committed values come from history store rather than prepared values, closes prepared sessions to roll them back, and reads again at timestamp 3.

State and persistence behavior: stable timestamp 1 pins history, committed updates are evicted into history store, and prepared updates are present but unresolved. Closing sessions aborts the prepared transactions, returning the latest visible state to the committed values.

Dependencies and integration points: cache pressure, eviction, history store, prepared updates, timestamp visibility, and row/column formats.

Risks: large loops can be time-sensitive under slow eviction. The test ignores known long eviction stdout warnings.

Test signals: every checked key returns the committed byte value and never the prepared byte value before and after aborting prepared sessions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_hs01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_hs02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_hs02.py

Purpose: exercises prepared insert, update, remove, and checkpointed-key update chains under both commit and rollback resolution to ensure reconciliation and history store paths can handle them.

Important APIs and types: `suite_subprocess`, `make_scenarios`, row and column table configs, cursor item assignment/removal, `prepare_transaction`, timestamped commit with durable timestamp, rollback, stable/oldest timestamp advancement, checkpoint, and `reopen_conn`.

Control flow: it runs several scenarios in one test: prepare an insert; checkpoint; prepare updates that include existing and newly inserted keys; checkpoint; prepare removes over existing, updated, and newly inserted keys; commit baseline data; checkpoint and reopen; then prepare updates/removes over checkpointed keys. Each prepared transaction is either committed at the next timestamp or rolled back depending on scenario.

State and persistence behavior: the file stresses update-chain shapes that reconciliation may write to disk or history store. Reopen forces subsequent updates to be normal update chains rather than purely in-memory insert chains.

Dependencies and integration points: timestamp manager, checkpoint/reconciliation, history store, prepare commit/rollback resolution, and row/column key formats.

Risks: the test is mostly crash/error oriented and does not assert final values for every scenario; failures are expected as exceptions, reconciliation faults, or checkpoint/reopen issues.

Test signals: all prepare/commit/rollback/checkpoint/reopen phases complete without exceptions for both transaction endings and key formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_hs02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_hs03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_hs03.py

Purpose: validates that prepared updates and history-store state remain recoverable through corruption, salvage, verify, checkpoint, and simulated crash/restart sequences.

Important APIs and types: `copy_wiredtiger_home`, `SimpleDataSet`, `wiredtiger.stat`, helper methods `corrupt_table`, `corrupt_salvage_verify`, `get_stat`, `check_data`, `get_timestamps`, and `prepare_updates`.

Control flow: committed large values are written at an early timestamp, stable/oldest are set, the table is deliberately corrupted and salvaged/verified, then multiple sessions prepare later updates. The test checks mid-timestamp reads still return committed values, closes prepared sessions to roll them back, checks again, repeats corruption/salvage/verify, checkpoints, copies to `RESTART`, reopens, and checks data again.

State and persistence behavior: the committed versions may live in the history store while prepared updates are unresolved. Rollback of prepared sessions must restore visibility of committed values even after salvage and restart.

Dependencies and integration points: history store statistics, salvage/verify, file copying, crash-style reopen, timestamp hooks, and variable key formats.

Risks: corruption/salvage may not recover every key, so `check_data` counts successfully found keys and asserts those have expected values. This makes the test robust to salvage loss but less exhaustive.

Test signals: `cache_write_hs` delta is nonnegative, every recovered key has the committed value, and salvage/verify/restart phases complete.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_hs03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_hs04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_hs04.py

Purpose: tests reading prepared updates from disk with `ignore_prepare`, and resolving prepared inserts over keys that already have tombstones, including crash/restart rollback-to-stable behavior.

Important APIs and types: `copy_wiredtiger_home`, `wiredtiger.stat.conn.cache_write_hs`, `search_keys_timestamp_and_ignore`, `prepare_updates`, debug `release_evict_page`, transaction configs with `ignore_prepare=true/false`, and commit/rollback scenarios.

Control flow: it inserts committed values at timestamp 2, checkpoints, removes them at timestamp 10, advances stable, then opens multiple prepared sessions inserting the same keys at timestamp 20. It reads at timestamp 5 and 20 with/without `ignore_prepare`, optionally commits prepared transactions at timestamp 30, checkpoints, copies the home to `RESTART`, reopens, and validates reads at timestamps 5, 20, and 30.

State and persistence behavior: the test covers prepared updates written to disk over an existing tombstone and how recovery/rollback-to-stable restores or commits them. It distinguishes pre-delete value, deleted state, prepare conflicts, and committed prepare values.

Dependencies and integration points: history store, tombstones, eviction, prepared transaction resolution, crash-copy recovery, and RTS. It is skipped for disaggregated hooks because RTS is not used there.

Risks: many assertions depend on exact timestamp order and `ignore_prepare` semantics. Misordered stable timestamps could obscure whether prepared state or tombstone state is being read.

Test signals: prepare conflicts occur only with `ignore_prepare=false` before resolution; after restart, committed scenarios show prepared values at timestamp 30 and rollback scenarios show `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_hs04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_hs05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_prepare_hs05.py

Purpose: verifies that aborting a prepared transaction restores the correct older history-store version when the latest committed state is a delete.

Important APIs and types: `WT_NOTFOUND`, `make_scenarios`, `cursor.remove`, debug `release_evict=true`, `ignore_prepare=true`, and timestamped reads.

Control flow: the test writes value1 at timestamp 2, then in one transaction writes value2 and removes the key at timestamp 3. It starts a prepared update to value3 at timestamp 4, forces eviction with `ignore_prepare=true` so the prepared update can become the on-disk version and older versions move to history store, rolls back the prepared transaction, checkpoints, and reads old and latest timestamps.

State and persistence behavior: after rollback, timestamp 2 should still read value1 from history store, while the latest state should remain deleted due to the timestamp-3 remove. The aborted prepared update must not resurrect value3.

Dependencies and integration points: history store restoration, prepared update rollback, tombstone handling, eviction, row and column formats.

Risks: the test intentionally evicts while a prepared update exists; incorrect eviction/reconciliation can lose the older value or clear the tombstone.

Test signals: timestamp 2 search returns value1, and an untimestamped/latest search returns `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_prepare_hs05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_readonly01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_readonly01.py

Purpose: broad read-only mode smoke test ensuring data can be read after reopening with `readonly=true` across file/table and row/variable-length formats, logging modes, base config modes, and optional directory chmod.

Important APIs and types: `suite_subprocess`, `make_scenarios`, `conn_config`, `close_reopen`, `readonly`, `os.chmod`, `open_cursor`, and scenario matrices for `config_base`, directory permissions, logging, and URI/table type.

Control flow: the test creates a table or file object, inserts 10,000 integer values, closes the original connection, optionally makes the directory read-only on POSIX, reopens with `readonly=true`, scans all records, and verifies key/value order.

State and persistence behavior: the persisted table data must be fully readable without modifying the home. Logging can be enabled or disabled; base config can be on or off.

Dependencies and integration points: connection open configuration, filesystem permissions, logging, table/file object creation, and cursor iteration.

Risks: POSIX permission behavior can differ across environments; the test wraps readonly directory cases with an expected `Permission` stderr pattern.

Test signals: all 10,000 entries are read back with expected values, or permission errors are expected in chmod scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_readonly01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_readonly02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_readonly02.py

Purpose: validates readonly mode rejects illegal configuration and unsafe recovery cases: opening a new database readonly, opening an unclean copy readonly, and combining readonly with log zero-fill.

Important APIs and types: `copy_wiredtiger_home`, `wiredtiger_open`, `assertRaisesWithMessage`, readonly connection configs, `os.mkdir`, and `wiredtiger.WiredTigerError`.

Control flow: during first connection open, it creates a separate directory and asserts `readonly=true` cannot create/open it because required files are absent. The test creates a logged table and inserts data, copies the home as an unclean backup and asserts readonly open needs recovery, then closes and reopens readonly with `log=(enabled,zero_fill=true)` expecting invalid argument.

State and persistence behavior: the test confirms readonly mode never performs creation or recovery writes and rejects logging settings that imply file modification.

Dependencies and integration points: connection open validation, logging configuration, unclean-home detection, filesystem copy helper, and platform-specific error text.

Risks: error message substrings vary by OS; the source handles POSIX versus non-POSIX missing-file wording.

Test signals: expected `WiredTigerError` messages match `No such file` or platform equivalent, `needs recovery`, and `Invalid argument`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_readonly02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_readonly03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_readonly03.py

Purpose: confirms modifying cursor and session methods return unsupported errors after reopening an existing database in readonly mode.

Important APIs and types: `SimpleDataSet`, `cursor_ops` (`insert`, `remove`, `update`), `session_ops` (`alter`, `create`, `compact`, `drop`, `flush_tier`, `log_flush`, `log_printf`, `salvage`, `truncate`), `assertRaisesWithMessage`, and readonly connection configuration.

Control flow: the first open creates and populates a table. `reopen_conn` then uses readonly config. The test opens a cursor and checks each mutating cursor method raises `/Unsupported/`, then iterates through session-level mutating APIs and checks each also raises `/Unsupported/`.

State and persistence behavior: no state should be modified after readonly reopen; all attempted changes are blocked at API level.

Dependencies and integration points: connection readonly flag, cursor write APIs, session DDL/maintenance/log APIs, tier flush path, and error propagation.

Risks: adding new mutating session APIs would not be covered unless added to `session_ops`. The test intentionally uses a fixed list.

Test signals: every listed method raises `WiredTigerError` matching `/Unsupported/`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_readonly03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconcile02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_reconcile02.py

Purpose: verifies reconciliation treats removal of already deleted keys from an old disk image as progress rather than reporting eviction blocked with no progress.

Important APIs and types: `SimpleDataSet`, debug cursor config `release_evict`, timestamped commits, `conn.set_timestamp`, and data-source statistic `cache_eviction_blocked_no_progress`.

Control flow: it inserts keys 1 and 2 at timestamp 10, deletes key 1 at timestamp 20, evicts the page, starts an uncommitted update to key 2 in another session, advances stable/oldest to 20 so the delete is globally visible, evicts again, then reads table statistics.

State and persistence behavior: the old disk image contains a deleted key that can be pruned during reconciliation. An uncommitted update remains in memory to make progress accounting relevant.

Dependencies and integration points: reconciliation, eviction, timestamp visibility, deleted-key pruning, and data-source statistics.

Risks: this test is sensitive to eviction actually running through the page; if debug eviction behavior changes, the stat may no longer measure the intended path.

Test signals: `cache_eviction_blocked_no_progress` for the table remains 0 after the second eviction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconcile02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconfig01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_reconfig01.py

Purpose: smoke-tests runtime `WT_CONNECTION::reconfigure` for shared cache, eviction, statistics, capacity, checkpoints, statistics logging, and file manager settings.

Important APIs and types: `self.conn.reconfigure`, `wiredtiger.WiredTigerError`, `assertRaisesWithMessage`, and configuration strings for `shared_cache`, `eviction`, `io_capacity`, `checkpoint`, `statistics_log`, and `file_manager`.

Control flow: each test method applies a sequence of legal reconfiguration strings and expects success. Negative cases assert too-low `io_capacity` reports `/below minimum/` and non-reconfigurable log path reports `/unknown configuration key/`.

State and persistence behavior: no table state is required; it validates live connection configuration mutation. Some changes affect background components such as eviction and statistics logging.

Dependencies and integration points: connection configuration parser, runtime reconfigurability flags, eviction server, statistics logger, and file manager.

Risks: broad smoke tests can miss semantic effects beyond successful parsing. They are still valuable for guarding config keys and reconfigurability contracts.

Test signals: successful reconfigure calls do not raise; invalid values raise expected errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconfig01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconfig02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_reconfig02.py

Purpose: tests runtime logging-related reconfiguration, especially toggling log removal/preallocation/zero-fill and rejecting immutable log settings.

Important APIs and types: custom `setUpConnectionOpen`, `self.conn.reconfigure`, `fnmatch.filter`, `os.listdir`, `time.sleep`, `reopen_conn`, and log configuration keys.

Control flow: simple reconfig toggles `remove`, `prealloc`, and `zero_fill`. Negative tests assert `enabled`, `compressor`, `file_max`, `path`, and `recover` cannot be reconfigured. The prealloc test waits for `*Prep*` files after enabling preallocation. The remove test writes data, reopens to roll logs, enables log removal, checkpoints, waits, and confirms original log files are gone.

State and persistence behavior: creates a logged table and log files; reconfiguration affects log preallocation and cleanup behavior on disk.

Dependencies and integration points: logging subsystem, background preallocation/removal threads, checkpoint, filesystem listing, and connection reopen.

Risks: sleep-based background-thread tests can be timing-sensitive on slow systems, though loops are used for preallocation.

Test signals: expected log files appear/disappear after reconfiguration, and immutable log settings raise `/unknown configuration key/`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconfig02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconfig03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_reconfig03.py

Purpose: mirrors MongoDB-style connection reconfiguration workloads, changing eviction/cache/shared-cache settings while a populated table and periodic checkpoints are active.

Important APIs and types: `SimpleDataSet.populate`, `time.sleep`, `self.conn.reconfigure`, log/checkpoint/cache connection config, and checkpoint log-size config.

Control flow: `test_reconfig03_mdb` populates increasing numbers of rows, sleeps to allow checkpoint activity, and reconfigures `eviction_target`, `cache_size`, `eviction_dirty_target`, and `shared_cache`. `test_reconfig03_log_size` reconfigures checkpoint log-size thresholds among small, 1M, and zero.

State and persistence behavior: table contents grow while background checkpointing and logging are enabled. The test stresses runtime config changes under active data modification.

Dependencies and integration points: cache sizing, eviction thresholds, checkpoint thread, shared cache parser, logging, and dataset population.

Risks: sleeps make it timing-dependent, but the goal is smoke coverage rather than exact statistics.

Test signals: all reconfiguration calls and subsequent population phases complete without error.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconfig03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconfig04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_reconfig04.py

Purpose: smoke-tests `WT_SESSION::reconfigure` for session cache-ignore and isolation settings.

Important APIs and types: `self.session.reconfigure`, `ignore_cache_size`, and isolation values `snapshot`, `read-committed`, and `read-uncommitted`.

Control flow: the test toggles `ignore_cache_size=false`, cycles through isolation modes, sets `ignore_cache_size=true`, and sets isolation to snapshot again.

State and persistence behavior: no table data is created. The state under test is session-local configuration.

Dependencies and integration points: session configuration parser and runtime session options.

Risks: this only checks accepted configuration strings, not behavioral effects of isolation modes.

Test signals: each `session.reconfigure` call succeeds without exception.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconfig04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconfig05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_reconfig05.py

Purpose: tests that connection reconfiguration parses nested structs without the `=` separator form issues, specifically around cache size and log OS cache dirty percentage.

Important APIs and types: `self.session.create`, `self.conn.reconfigure`, `log=(enabled)`, and config strings `cache_size=1GB`, `log=(os_cache_dirty_pct=30/50)`.

Control flow: it creates a simple string-key/string-value table, then applies three connection reconfiguration strings: cache only, cache plus nested log option, and nested log option only.

State and persistence behavior: minimal table state is created to ensure an initialized connection/table context. The real target is configuration parsing and live mutation.

Dependencies and integration points: connection config parser, log configuration parser, cache manager, and reconfigure path.

Risks: successful parsing does not validate runtime side effects of `os_cache_dirty_pct`.

Test signals: all three reconfiguration calls return successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reconfig05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_recovery01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_recovery01.py

Purpose: tests recovery/shutdown progress logging while validating logged and non-logged table recovery semantics across crash-style and clean reopen paths.

Important APIs and types: `simulate_crash_restart`, `SimpleDataSet`, `stat`, `make_scenarios`, `large_updates`, `check`, verbose config `recovery_progress`, and log-enabled connection config.

Control flow: it creates one logged table and one non-logged table, pins oldest/stable to 1, writes value A and value B to both tables, using timestamps only for the non-logged table. It sets stable to 10, checkpoints, then either simulates a crash restart or cleanly reopens. It checks logged table keeps the latest value B while non-logged table rolls back to stable value A at timestamps 10 and 20.

State and persistence behavior: logged table updates are recovered from logs; non-logged timestamped updates beyond stable are rolled back to stable on recovery. The test also suppresses expected recovery-progress stdout.

Dependencies and integration points: logging, recovery, rollback-to-stable during recovery, timestamped non-logged tables, crash simulation, and verbose recovery messages.

Risks: this test assumes stable timestamp 10 should make value B at timestamp 20 disappear for non-logged data while logged data remains durable.

Test signals: post-restart logged reads return value B for all rows; non-logged reads return value A at both read timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_recovery01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reserve.py -->
# sources/storage-engines/wiredtiger/test/suite/test_reserve.py

Purpose: validates `WT_CURSOR.reserve` semantics on supported row/column/file/table datasets and rejection on invalid cursor states or non-standard cursor types.

Important APIs and types: `SimpleDataSet`, `SimpleIndexDataSet`, `ComplexDataSet`, `make_scenarios`, cursor `reserve`, `update`, `insert`, `remove`, transaction commit/rollback, and special cursors such as backup/config/log/metadata/statistics.

Control flow: the main test populates data, updates a record, asserts reserve fails for a missing record, reserves existing records with commit and rollback, reserves then updates, and verifies another transaction cannot update a reserved record. Additional tests check reserve requires a key, requires a running transaction, returns the current value on success, and is unsupported on bulk/dump and system cursors.

State and persistence behavior: reserve creates transactional write intent without changing value unless followed by update. Commit and rollback paths are exercised, along with conflict behavior from another session.

Dependencies and integration points: cursor API contracts, transaction conflict detection, dataset abstractions, index/complex table cursor wrappers, and hook-specific disagg behavior for bulk cursor support.

Risks: there is a likely copy/paste comment mismatch where the "reserve then update and rollback" loop actually commits; research consumers should inspect before changing semantics.

Test signals: reserve returns 0 and current value when valid, raises required-key/no-transaction/unsupported errors in invalid modes, and conflicting update from another session raises `WiredTigerError`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_reserve.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback01.py

Purpose: ensures a cursor `next()` that gets forced into eviction under cache pressure can return `WT_ROLLBACK` without retrying indefinitely, and leaves the cursor unpositioned.

Important APIs and types: `wttest.skip_for_hook("disagg")`, `wiredtiger.wiredtiger_strerror`, `wiredtiger.WT_ROLLBACK`, debug `release_evict`, `conn.reconfigure(cache_max_wait_ms=...,cache_size=...)`, cursor `search_near`, `next`, and `get_key`.

Control flow: it creates a table, inserts 100 1KB values, evicts the page, positions a second read cursor near key 10, shrinks cache/max wait aggressively, starts a transaction that writes a 5MB value, waits for accounting, and loops calling `read_cursor.next()` until a rollback error is observed. It then asserts `get_key` fails because the cursor is unpositioned.

State and persistence behavior: the oversized uncommitted update creates cache pressure. The read cursor is expected to be pulled into eviction and rolled back rather than transparently retried.

Dependencies and integration points: cache accounting, eviction, rollback error propagation, cursor positioning state, and connection reconfiguration.

Risks: timing and cache pressure can be environment-sensitive; the loop and sleep are there to give accounting time to trigger.

Test signals: a rollback error occurs within 80 `next()` attempts, and subsequent `get_key` raises `/requires key be set/`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable01.py

Purpose: tests rollback-to-stable clears a newer remove operation and restores stable data, with variants for row/column formats, in-memory mode, prepared updates, dry run, and RTS worker threads.

Important APIs and types: `test_rollback_to_stable_base`, `large_updates`, `large_removes`, `check`, `conn.rollback_to_stable`, `stat.conn.txn_rts*` counters, and `make_scenarios`.

Control flow: it writes 10,000 rows at timestamp 10, verifies them, removes all keys at timestamp 20, verifies the table appears empty, sets stable to 20 for prepared mode or 10 otherwise, checkpoints when not in-memory, runs RTS with dryrun/thread options, checks final visibility, and validates RTS statistics.

State and persistence behavior: the stable state should contain the original value. Non-dryrun restores it after rolling back the remove; dryrun leaves the remove in place. In-memory mode has different accounting because there is no disk history restoration.

Dependencies and integration points: RTS, prepared timestamp convention in the base helper, history store/disk restore, in-memory mode, dryrun accounting, and worker threading.

Risks: statistic expectations branch by dryrun and in-memory, so changes to RTS accounting can break the test even if data behavior is correct.

Test signals: data visibility matches dryrun versus real RTS expectations, calls equal 1, pages visited is positive, and aborted/restored dryrun counters match row count.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable02.py

Purpose: verifies rollback-to-stable replaces newer on-disk values with the stable history-store value after multiple full updates.

Important APIs and types: `test_rollback_to_stable_base`, `large_updates`, `check`, `conn.rollback_to_stable`, dryrun/thread scenarios, in-memory/prepared scenarios, and RTS statistics including update-aborted and HS-removed counters.

Control flow: it writes four full-value generations at timestamps 10, 20, 30, and 40. Stable is set to 30 for prepared mode or 20 otherwise, the table is checkpointed when not in-memory, and RTS is run. Dryrun expects the latest value to remain; real RTS expects value B to be visible even at a later read timestamp. It also verifies older timestamp reads.

State and persistence behavior: newer updates beyond the stable point must be removed from both update chains and history store as appropriate, leaving the stable full value visible.

Dependencies and integration points: RTS history restore, dryrun accounting, prepared timestamp adjustment, in-memory mode, and worker-thread variants.

Risks: this test counts at least two generations per row as aborted/removed; internal history-store accounting changes may require stat expectation updates.

Test signals: post-RTS reads return value B unless dryrun, calls equal 1, pages visited is positive, and update-aborted/dryrun counters are at least `nrows * 2` in the expected branch.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable03.py

Purpose: checks rollback-to-stable clears history-store updates from reconciled pages and reports btree applied/skipped counters correctly across repeated RTS calls.

Important APIs and types: `WiredTigerCursor`, `statistic_uri`, `test_rollback_to_stable_base`, `large_updates`, `check`, `conn.rollback_to_stable`, and RTS counters such as `txn_rts_hs_removed`, `txn_rts_btrees_applied`, and `txn_rts_btrees_skipped`.

Control flow: it writes three generations at timestamps 10, 20, and 30, sets stable to 30 for prepared or 20 otherwise, checkpoints when not in-memory, runs RTS, verifies values B and A at timestamps 20 and 10, and checks stats. It then runs RTS a second time and verifies btree applied/skipped behavior differs for in-memory and non-in-memory modes.

State and persistence behavior: value C should be rolled back to value B at stable, with older value A still available. Non-in-memory RTS can clear modified flags through checkpoint, causing a second RTS to skip clean btrees; in-memory keeps modified flags.

Dependencies and integration points: history store cleanup, RTS btree scanning, checkpoint side effects, in-memory mode, and prepared update semantics.

Risks: applied/skipped accounting is nuanced and can be affected by eviction modifying the tree before the second RTS.

Test signals: data checks pass, first RTS has one applied btree and zero skipped, and second RTS counters match mode-specific expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable04.py

Purpose: ensures RTS restores a full stable update from history store when the update chain includes many modify records and full updates.

Important APIs and types: helper `mod_val`, base helper methods `large_updates`, `large_modifies`, `evict_cursor`, `check`, `conn.rollback_to_stable`, dryrun/evict/in-memory/prepare/thread scenarios, and RTS statistics including HS sweep counters.

Control flow: it writes value A at timestamp 20, applies modifies Q/R/S at 30/40/50, optionally evicts, then writes/modified many later generations through timestamp 140. Stable is set to 40 for prepared mode or 30 otherwise. After checkpoint and RTS, it verifies the stable modified value Q is visible at timestamp 30 and at a future timestamp for real RTS, while dryrun retains the latest value at future timestamp.

State and persistence behavior: RTS must not reconstruct stable state from a partial modify chain incorrectly; it must use a full update or correctly resolved history value. Later full updates and modifies are removed or counted.

Dependencies and integration points: modify chains, history store, eviction, RTS dryrun, in-memory mode, prepared timestamp handling, and statistics.

Risks: this is sensitive to full-update versus modify reconstruction semantics. Statistics expect at least eleven rolled-back generations per row.

Test signals: value checks across every generation pass before RTS; after RTS, non-dryrun future reads return `value_modQ`; dryrun retains latest `value_modZ`; RTS counters match mode-specific branches.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable04.py -->
