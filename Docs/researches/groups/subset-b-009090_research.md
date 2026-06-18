# subset-b-009090 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp14.py

Purpose: Exercises WiredTiger global timestamp queries for `all_durable`, `oldest_reader`, `oldest_timestamp`, and `pinned`, across row-store integer keys and column-store recno keys. It verifies that running transactions, prepared transactions, read timestamps, and no-timestamp transactions affect global timestamp state as documented.

Important APIs/types/functions: `test_timestamp14` extends `wttest.WiredTigerTestCase` and `suite_subprocess`; scenarios are built with `make_scenarios`. The tests use `conn.query_timestamp()`, `conn.set_timestamp()`, `session.begin_transaction()`, `session.timestamp_transaction()`, `session.prepare_transaction()`, `session.commit_transaction()`, cursors, and `assertTimestampsEqual`.

Control flow: `test_all_durable_old` walks historical all-committed/all-durable cases: no timestamp, single timestamped commit, lower in-flight commit timestamp, out-of-order pending timestamp, and no-timestamp work. `test_oldest_reader` opens multiple sessions to prove only timestamped readers pin `oldest_reader`. `test_pinned_oldest` moves oldest past an active reader and checks `pinned`. `test_all_durable` adds prepared-transaction durable timestamp cases and repeated `commit_timestamp` setting. `test_all` combines oldest, reader, pinned, and all-durable movement in one scenario.

State and persistence behavior: State is in connection-wide timestamp metadata plus transactional updates to temporary tables. The file does not restart WiredTiger, but it depends on precise live transaction accounting and prepared transaction durable timestamp tracking.

Dependencies and integration points: Integrates with the Python WiredTiger test harness, timestamp string helpers, scenario expansion, and transaction manager internals surfaced through `query_timestamp`. It is a direct regression surface for timestamp visibility, checkpoint safety, and oldest/pinned timestamp advancement.

Risks: The tests are sensitive to subtle timestamp ordering semantics; changes in prepared transaction accounting can make apparently unrelated assertions fail. Multiple sessions share the same table, so leaked transactions or cursors would poison later timestamp queries.

Test signals: Strong signal comes from exact timestamp equality checks after each transition, including all-durable moving backward for lower in-flight timestamps and pinned falling back to oldest after readers close.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp16.py

Purpose: Confirms that a transaction read timestamp is cleared after rollback or commit and cannot leak into later timestamped checkpoints.

Important APIs/types/functions: `test_timestamp16` extends `WiredTigerTestCase` and `suite_subprocess`. The main API calls are `session.begin_transaction('read_timestamp=...')`, `rollback_transaction`, `commit_transaction`, `session.checkpoint('use_timestamp=true')`, `conn.set_timestamp`, and `conn.query_timestamp('get=last_checkpoint')`.

Control flow: The test creates a table, starts and rolls back a read transaction at timestamp 100, checkpoints with timestamps, and expects `last_checkpoint` to stay zero. It then sets stable timestamp 2, repeats a rollback path, and expects checkpoint timestamp 2. Finally it commits a transaction that had read timestamp 150 and verifies the next timestamped checkpoint remains at stable timestamp 2.

State and persistence behavior: The durable state under test is the checkpoint timestamp stored in connection metadata. The important transient state is the session transaction read timestamp; the test ensures it is reset before checkpoint timestamp selection.

Dependencies and integration points: Connects transaction lifecycle cleanup to checkpoint timestamp selection. It depends on the harness timestamp comparison helper and WiredTiger metadata query path.

Risks: A regression would allow stale read timestamp state to make a checkpoint appear newer than the stable timestamp or to report an unexpected last checkpoint timestamp.

Test signals: Exact `last_checkpoint` assertions provide focused signals for rollback and commit cleanup paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp17.py

Purpose: Tests a non-timestamped tombstone written after timestamped updates, ensuring it hides all historical versions and continues to do so as oldest timestamp advances.

Important APIs/types/functions: `test_timestamp17` uses `make_scenarios` for integer row-store and column-store keys. It relies on cursor `remove`, `search`, `WT_NOTFOUND`, `begin_transaction('no_timestamp=true')`, timestamped commits, and `conn.set_timestamp('oldest_timestamp=...')`.

Control flow: The test writes one key at timestamps 25, 50, and 200, verifies it is absent before the first update, then removes it without a timestamp. It reads at several historical and future read timestamps and expects `WT_NOTFOUND`. It then advances oldest to 49, 99, 100, and 200 while continuing to verify invisibility at relevant read timestamps.

State and persistence behavior: The key's update chain contains timestamped values followed by a globally visible no-timestamp tombstone. Oldest timestamp advancement may discard older history, but must not expose covered timestamped values.

Dependencies and integration points: Exercises transaction visibility, history-store reconciliation rules, tombstone semantics, and row/column key formats through the Python test harness.

Risks: Bugs in no-timestamp tombstone handling could resurrect historical values after history cleanup or oldest timestamp advancement. Column-store handling is especially important because recno keys have different deleted-value behavior.

Test signals: Repeated `WT_NOTFOUND` checks across read timestamps and oldest movements catch value resurrection or incorrect history truncation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp18.py

Purpose: Verifies mixed timestamped and non-timestamped writes, both non-timestamped updates and non-timestamped deletes, over large row and column tables.

Important APIs/types/functions: `test_timestamp18` defines `get_key` to normalize string-row and recno keys. It uses scenario dimensions for key format and non-timestamp operation kind, cursor updates/removes, timestamped commits, `begin_transaction('no_timestamp=true')`, checkpoint, and read-timestamp validation.

Control flow: The test writes 9,999 keys at commit timestamps 2, 3, and 4. It then applies no-timestamp changes to even keys, either deleting them or overwriting with `value4`, checkpoints, and reads at timestamps 2 and 3. Even keys must reflect the non-timestamp operation, while odd keys must retain timestamp-appropriate values.

State and persistence behavior: The test creates dense update chains and then adds globally visible non-timestamp updates. Checkpointing forces reconciliation so the history-store representation is also covered.

Dependencies and integration points: Integrates timestamp visibility, reconciliation, history-store correction for no-timestamp updates, and both row-store and column-store key handling.

Risks: Off-by-one or adjacent-key corruption is explicitly guarded by changing every second key. A bug could allow older timestamped values to appear behind a no-timestamp update or delete.

Test signals: Full-table scans at historical read timestamps validate both coverage of even keys and preservation of odd-key history.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp19.py

Purpose: Ensures the oldest timestamp persisted in metadata is restored as the connection's oldest timestamp after restart.

Important APIs/types/functions: `test_timestamp19` uses `SimpleDataSet`, `updates()`, `conn.set_timestamp`, `session.checkpoint('use_timestamp=true')`, `close_conn`, `setUpConnectionOpen`, and `query_timestamp`.

Control flow: The test sets oldest/stable to 10, writes batches at 20, 30, and 40, checkpoints, advances oldest/stable to 40, writes more batches at 50, 60, and 70, checkpoints again, and reopens the connection. It then verifies setting oldest back to 10 fails and that oldest is recovered as 40, before advancing both oldest and stable to 70.

State and persistence behavior: The key state is metadata persisted by timestamped checkpoints. Restart recovery must seed the in-memory oldest timestamp from metadata, preventing illegal rollback of oldest.

Dependencies and integration points: Exercises metadata recovery, timestamp validation, checkpoint timestamping, and restart path in the WiredTiger test harness.

Risks: If metadata recovery loses oldest, applications could set oldest too far back after restart, invalidating history-store cleanup assumptions.

Test signals: The expected `WiredTigerError` message for setting oldest to 10 and exact query checks for 40 and 70 are the main pass/fail signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp20.py

Purpose: Exercises correction of updates without timestamps in the history store, including full updates and modify chains.

Important APIs/types/functions: `test_timestamp20` uses `wiredtiger.Modify`, `debug=(release_evict)` cursors in `evict`, timestamped and no-timestamp transactions, checkpoints, and old-reader sessions.

Control flow: `test_timestamp20_standard` writes three timestamped versions for 9,999 keys, opens an old reader at timestamp 20, then writes two no-timestamp/current updates that should force history-store correction. After checkpoint and eviction, a read at timestamp 30 sees the no-timestamp value while the old reader sees the timestamp-30 value. `test_timestamp20_modify` repeats the pattern with modify records, keeping an old reader at timestamp 20 and verifying reconstructed modify history after later no-timestamp updates.

State and persistence behavior: The tests intentionally force pages to disk and into the history store, then evict them. They depend on transaction ID visibility and timestamp correction so old readers retain access to older versions while new timestamp reads do not bypass no-timestamp updates.

Dependencies and integration points: Integrates update-chain reconciliation, history-store writes, modify reconstruction, eviction debug hooks, and old-reader visibility.

Risks: Modify chains are sensitive to corruption because deltas can be applied to the wrong base value. No-timestamp updates can incorrectly shadow or expose history if correction logic is wrong.

Test signals: Value comparisons for all keys under current and old-reader transactions catch both visibility and reconstruction errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp22.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp22.py

Purpose: Randomly misuses timestamp APIs to confirm WiredTiger rejects invalid combinations without crashing, while preserving predictable global timestamp state and final row contents.

Important APIs/types/functions: `test_timestamp22` uses `suite_random`, `SimpleDataSet`, `make_scenarios`, a custom `expect` context manager, `updates`, `set_global_timestamps`, `expected_result_set_timestamp`, `prepare_transaction`, `timestamp_transaction`, `set_timestamp`, and stderr pattern handling.

Control flow: The randomizer runs 1,000 iterations normally or 100,000 in long-test mode. Each iteration may perform timestamped writes, prepared transactions, illegal durable/commit/read timestamp combinations, or global timestamp updates. The helper predicts whether each operation should succeed. It tracks `oldest_ts`, `stable_ts`, `last_commit_ts`, `last_durable`, and the last committed value, then validates final table contents.

State and persistence behavior: State is primarily in transaction metadata and global timestamp connection metadata. The test deliberately avoids cases that would panic the diagnostic suite after failed timestamp setting, then checks query_timestamp against the model after each global timestamp operation.

Dependencies and integration points: Broadly integrates transaction timestamp validation, prepared timestamp rules, global oldest/stable timestamp ordering, stderr cleanup, and row/column table formats.

Risks: Randomized tests can be hard to minimize, but the seed is printed. The expected-state model must track WiredTiger semantics closely or it can hide true engine regressions behind test-model mistakes.

Test signals: Every generated operation is wrapped in a success/failure expectation; final row verification ensures successful commits had the expected lasting effect.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp22.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp23.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp23.py

Purpose: Regression test for repeatedly deleting and restoring a key at successive timestamps, then attempting a conflicting remove from an older read transaction.

Important APIs/types/functions: `test_timestamp23` uses `SimpleDataSet`, timestamped begin/commit calls, cursor `remove`, `debug=(release_evict)` eviction, a second session, and checks for `WT_ROLLBACK`.

Control flow: The test pins oldest/stable at 1, writes key 5 and key 6 at commit 11, deletes key 5 at 21, restores it at 31, deletes it again at 41, and evicts the page through key 6. A second session reads key 5 at timestamp 12 and then tries to remove it. The remove must fail with rollback.

State and persistence behavior: The update chain includes values and tombstones newer than the oldest timestamp, then is reconciled through eviction. The older reader sees history but cannot write over a conflicting newer chain.

Dependencies and integration points: Exercises history-store conflict detection, reconciliation of deleted/restored keys, column-store and integer row-store behavior, and rollback error mapping.

Risks: The comments identify a previous column-store bug where the conflicting remove incorrectly succeeded and later reconciliation asserted. This remains a high-risk visibility/conflict area.

Test signals: The required `WT_ROLLBACK` on `cursor2.remove()` is the main signal; any success triggers explicit failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp23.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp24.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp24.py

Purpose: Verifies that a transaction reading an older version cannot later perform a conflicting update after a newer committed version has been reconciled.

Important APIs/types/functions: `test_timestamp24` uses two sessions, `SimpleDataSet`, timestamped commits, read timestamp transactions, cursor reset, `debug=(release_evict)`, and `WT_ROLLBACK` error checking.

Control flow: Session 1 writes value A at timestamp 20, then opens a read transaction at 25 and reads A while leaving the transaction open. Session 2 writes value B at timestamp 50 and evicts the page so B goes to disk and A goes to history. Session 2 rolls back a value C update. Session 1 then tries to write value D and must receive rollback. Final read at timestamp 60 expects value B unless the deliberately flagged broken path occurred.

State and persistence behavior: The page is reconciled while an older reader is open, creating a disk/history split. The test protects against applying an older transaction's update to the wrong version after reconciliation.

Dependencies and integration points: Integrates cursor reset/page unpinning, eviction, history-store placement, conflict detection, and multi-session transaction ordering.

Risks: The comments describe prior corruption where an update was applied to the newest version instead of the transaction's visible version. This is a data-corruption-sensitive test.

Test signals: A successful conflicting write is an explicit failure; final value comparison verifies the visible latest value remains B.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp24.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp25.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp25.py

Purpose: Checks short timestamp query aliases for compatibility with full query names.

Important APIs/types/functions: `test_timestamp25` extends `WiredTigerTestCase` and `suite_subprocess`. It calls `conn.query_timestamp` with `get=all_durable`, `get=all_durable_value`, `get=oldest_reader`, `get=oldest_reader_value`, `get=oldest_timestamp`, `get=oldest_timestamp_value`, `get=pinned`, `get=pinned_timestamp`, `get=stable_timestamp`, and `get=stable_timestamp_value`.

Control flow: The test issues pairs of equivalent query names and asserts each pair returns the same string timestamp. It does not need data setup because it is testing API name mapping rather than timestamp movement.

State and persistence behavior: No table state is created. It reads current connection timestamp metadata and validates query dispatch aliases.

Dependencies and integration points: Integrates the Python binding with WiredTiger's timestamp query parser and backwards-compatible option names.

Risks: Low behavioral complexity, but a parser rename or alias removal could break existing applications even if timestamp internals are correct.

Test signals: Equality assertions between canonical and short/alternate query names.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp25.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp26.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp26.py

Purpose: Comprehensive tests for per-object timestamp usage assertions: write timestamp usage `never`/`ordered`, read timestamp assertions, `alter`, logged/in-memory behavior, and inconsistent per-key timestamp updates.

Important APIs/types/functions: Multiple classes cover targeted cases: `test_timestamp26_wtu_never`, `test_timestamp26_read_timestamp`, `test_timestamp26_alter`, `test_timestamp26_alter_inconsistent_update`, `test_timestamp26_inconsistent_update`, `test_timestamp26_log_ts`, and `test_timestamp26_in_memory_ts`. APIs include `session.create` with `write_timestamp_usage` and `assert=(read_timestamp=...)`, `session.alter`, `timestamp_transaction`, timestamped commits, `no_timestamp=true`, diagnostic/disagg skips, and `DisaggConfigMixin`.

Control flow: Tests verify timestamped commits are rejected for `write_timestamp_usage=never`, reads require or reject read timestamps according to `assert`, altering from `never` to `ordered` changes enforcement, decreasing per-key commit timestamps are rejected, once-timestamped keys must continue to use timestamps, and timestamp checks are ignored for logged/in-memory configurations unless object config overrides the environment.

State and persistence behavior: State is per-table configuration plus per-key timestamp usage history. Some tests move oldest to allow `alter`, and logged/in-memory scenarios validate environment-level timestamp ignoring rather than persistent history.

Dependencies and integration points: Integrates schema creation options, object alteration, transaction timestamp validation, diagnostic build behavior, disaggregated storage restrictions, logging, and in-memory configuration.

Risks: Several assertions are disabled in diagnostic builds because failures can dump transaction diagnostics or panic. Disaggregated storage has explicit incompatibilities for `write_timestamp_usage=never` and alter support.

Test signals: Expected `WiredTigerError` messages for disallowed timestamp use, decreasing timestamp order, missing timestamps, and read timestamp policy are the primary signals; smoke paths confirm valid orders still commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp26.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp27.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp27.py

Purpose: Tests rollback timestamp API validation for prepared and non-prepared transactions, with and without `preserve_prepared`.

Important APIs/types/functions: Two classes cover `preserve_prepared=false` default and `preserve_prepared=true` with `precise_checkpoint=true`. APIs include `rollback_transaction('rollback_timestamp=...')`, `prepare_transaction`, `timestamp_transaction('rollback_timestamp=...')`, `conn.set_timestamp('stable_timestamp=...')`, and begin transaction `roundup_timestamps=(prepare=true)`.

Control flow: Non-prepared transactions must reject rollback timestamps. Prepared transactions can set a rollback timestamp. With preserved prepared transactions, rollback timestamp must be newer than stable and cannot be combined with commit or durable timestamps. The test also rejects prepare timestamp roundup under preserve-prepared.

State and persistence behavior: The state under test is prepared transaction metadata and stable timestamp ordering. No table data is needed; the API validation occurs on transaction state.

Dependencies and integration points: Integrates transaction prepare/rollback timestamp parsing, stable timestamp validation, preserve-prepared connection configuration, and precise checkpoint mode.

Risks: The class contains two methods with the same Python name `test_rollback_timestamp_with_commit_timestamp`; the second definition shadows the first, so only the durable-timestamp variant actually runs. That is a coverage risk for the combined rollback+commit config case.

Test signals: Expected `WiredTigerError` messages for non-prepared use, not-newer-than-stable rollback timestamps, invalid combined timestamp options, and prohibited prepare roundup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp27.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp28.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp28.py

Purpose: Smoke test that commit timestamps are validated both when supplied at commit time and when set earlier with `timestamp_transaction`, including the earliest commit timestamp in a transaction.

Important APIs/types/functions: `test_timestamp28` uses `SimpleDataSet`, scenarios over `stable_timestamp` and `oldest_timestamp`, `conn.set_timestamp`, `session.timestamp_transaction('commit_timestamp=...')`, `commit_transaction`, and expected error patterns for each global timestamp type.

Control flow: The test sets stable or oldest to 30, then tries to commit at 20 and expects failure. It then sets a transaction commit timestamp 50, advances the global timestamp to 60 before commit, and expects commit failure. Finally, it sets commit timestamps 70 and 71 in one transaction, advances the global timestamp to 75, and confirms the earliest commit timestamp is used for validation even when commit is called with 80.

State and persistence behavior: The relevant state is the transaction's stored commit timestamp list/first commit timestamp and connection global timestamp. Table data is incidental.

Dependencies and integration points: Covers timestamp validation in both `timestamp_transaction` and `commit_transaction`, and integrates global oldest/stable constraints with transaction commit metadata.

Risks: If validation only checks the final commit argument, transactions could sneak older operations past oldest/stable constraints. Error strings differ by stable versus oldest path, so parser/message changes affect assertions.

Test signals: Three expected exceptions per scenario, each matched against the timestamp-specific error pattern.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp28.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp29.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp29.py

Purpose: Tests setting, querying, and statistics for the stable disaggregated schema epoch timestamp.

Important APIs/types/functions: `test_timestamp29` uses `conn.set_timestamp('stable_disaggregated_schema_epoch=...')`, `conn.query_timestamp('get=stable_disaggregated_schema_epoch')`, statistics cursor reads for `stat.conn.txn_set_ts_stable_disagg_epoch` and `_upd`, and retry-aware `assertStatEqual`.

Control flow: The test verifies the default epoch is 0, sets it to 10 and 20, repeats 20 as a no-op, rejects a backward move to 10, rejects zero, sets epoch together with oldest/stable timestamps, and then advances it independently to 50 and 100. It checks call and update counters after each stage.

State and persistence behavior: State is connection-level timestamp metadata for a disaggregated schema epoch plus asynchronous statistics counters. The epoch is monotonic and independent of oldest/stable ordering except that it can be set in the same config string.

Dependencies and integration points: Integrates timestamp parser support for a newer timestamp field, query path, stats publication, and disaggregated storage metadata semantics.

Risks: Stats are asynchronous, so the helper retries. Incorrect monotonicity, zero handling, or counter increments would indicate API contract drift.

Test signals: Exact epoch comparisons, expected errors for backward/zero transitions, and call/update stat counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp29.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate01.py

Purpose: Base and broad API coverage for `session.truncate` over files, tables, simple/complex datasets, cursor ranges, empty objects, timestamp/no-timestamp transactions, and varied key formats.

Important APIs/types/functions: Defines `test_truncate_base` with common connection config and multiple test classes for bad arguments, URI truncation, cursor ordering, cursor past-end ranges, empty objects, timestamp handling, and cursor-range truncation. Uses `SimpleDataSet`, `ComplexDataSet`, `confirm_empty`, `simple_key`, `make_scenarios`, `session.truncate`, and helper `truncateRangeAndCheck`.

Control flow: The file first validates invalid argument combinations and unset cursor keys. It then truncates whole objects by URI, rejects reversed cursor ranges, permits ranges past the end, handles empty objects, and tests no-timestamp truncate under logging. The large cursor-range suite constructs many record layouts with skipped/inserted prefixes and suffixes, optionally checkpoints/reopens, truncates selected ranges, and validates remaining keys.

State and persistence behavior: Tests both in-memory insert-list state and on-disk state after checkpoint/reopen. It also covers logged versus unlogged object timestamp rules and complex table indexes/column groups.

Dependencies and integration points: This is the baseline for later truncate tests; `test_truncate02.py` inherits `test_truncate_base`. It integrates schema, cursor positioning, file/table namespaces, disaggregated hook skips, and transaction synchronization/statistics config.

Risks: Scenario count is high and uses pruning; regressions can be format-specific. The `test_truncate_complex` method appears to run only when `type == 'table:'` and `runningHook('disagg')`, despite comments suggesting broad table smoke coverage, so non-disagg complex table coverage may be intentionally or accidentally skipped.

Test signals: Expected exceptions, `confirm_empty`, `WT_NOTFOUND` for deleted keys, exact retained values, and drop/reopen cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate02.py

Purpose: Tests fast-delete transactional visibility when truncating leaf pages that are not in memory.

Important APIs/types/functions: `test_truncate_fast_delete` inherits `test_truncate_base`, uses `SimpleDataSet`, `cursor_count`, `outside_count`, `session.truncate`, cursor iteration forward/backward, `reopen_conn`, and isolation modes `read-committed` and `read-uncommitted`.

Control flow: The test creates a large small-page file/layered object, optionally adds overflow records, checkpoints and reopens, optionally reads or writes rows before truncation, then truncates a large middle range inside a transaction. It optionally reads/writes after truncation, checks visibility from the same transaction and separate sessions, and finally commits or rolls back and validates final record counts.

State and persistence behavior: Fast-delete state is stored in page references for pages not in cache. The test covers committed and aborted truncate transaction state, as well as pages forced into memory by overflow, reads, or writes.

Dependencies and integration points: Integrates btree fast-delete, transaction visibility, isolation levels, row/column/string key formats, optional disaggregated layered tables, and overflow item behavior.

Risks: Counts depend on inclusive/exclusive range behavior and isolation semantics. Overflow or prior page instantiation can force slow paths, so scenarios are designed to vary fast-delete eligibility.

Test signals: Forward/backward cursor counts before and after commit/rollback are the main signals, including outside read-committed/uncommitted visibility differences.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate03.py

Purpose: Exercises address-deleted cells produced by truncating unloaded pages, recovery, freeing deleted pages, and later instantiating empty pages.

Important APIs/types/functions: `test_truncate_address_deleted` uses `SimpleDataSet`, `reopen_conn`, `verifyUntilSuccess`, explicit checkpointing, cursor update/scan, `raisesBusy`, and `session.verify`.

Control flow: `address_deleted` creates a large small-page file, reopens and verifies, starts a long transaction to force checkpoint behavior, truncates a broad range, checkpoints address-deleted cells to disk, reopens, verifies, dirties and walks the tree, and checkpoints again to free pages. One test loops verify until not busy; the other writes into keys in the deleted range, checkpoints/reopens, verifies, and reads those values back.

State and persistence behavior: Focuses on on-disk internal-page address-deleted cells, recovery conversion to free pages, and synthetic empty-page instantiation after underlying leaf pages are removed.

Dependencies and integration points: Integrates reconciliation, checkpoint, recovery/reopen, verification, btree deleted-page handling, and row/column formats.

Risks: Bugs here can surface as verify failures, missing free-page conversion, or inability to create pages for writes into previously deleted ranges.

Test signals: Successful verify after recovery/freeing, absence of busy after checkpoints, and exact readback of newly written values in the formerly deleted range.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate05.py

Purpose: Ensures truncating at a read timestamp older than a newer committed update fails rather than deleting over invisible newer data.

Important APIs/types/functions: `test_truncate05` uses small cache config, `session.truncate`, timestamped commits, `reopen_conn`, large insert workload for eviction pressure, and expected `WiredTigerError`.

Control flow: The test inserts keys 1-999 at timestamp 2, reopens to force content to disk, updates key 500 at timestamp 3, inserts many more keys at timestamp 4 to pressure eviction, begins a read transaction at timestamp 2, then attempts to truncate keys 1-1000 and expects failure.

State and persistence behavior: The key state is a newer update not visible to the truncating transaction. The test forces eviction/disk state so truncate must inspect or protect against unseen newer history.

Dependencies and integration points: Integrates timestamp read visibility, truncate conflict detection, eviction pressure, and row/column store formats.

Risks: If truncate ignores newer invisible updates, it can corrupt history by deleting data outside the reader's snapshot.

Test signals: The truncate call must raise `WiredTigerError`; rollback then cleans the read transaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate06.py

Purpose: Tests timestamped truncate over timestamped updates/removes in the presence of older history, with fast-delete, checkpoint, and conflicting/non-conflicting timestamp cases.

Important APIs/types/functions: `test_truncate06` uses scenario dimensions for update vs remove, eviction, checkpoint, and truncate timestamp. Helpers include `evict` with `debug=(release_evict)` and `truncate`, which can use either `session.truncate` or per-key `remove` reference mode.

Control flow: The test writes 10,000 rows at timestamp 10, marks them stable, modifies every other even key in the middle third at timestamp 20, optionally evicts and checkpoints, then truncates a broad range at timestamp 15 or 25 using a read timestamp one less than commit. Timestamp 15 should conflict and return `WT_ROLLBACK`; timestamp 25 should commit.

State and persistence behavior: It covers history chains with stable baseline data and newer updates/removes, with pages optionally in fast-delete-eligible disk state.

Dependencies and integration points: Integrates timestamp conflict detection, fast-delete, checkpointing, update versus tombstone history, row/column formats, and rollback error handling.

Risks: The same logical operation can run through fast-delete or instantiated pages, and bugs may only occur in one path. The disabled remove reference scenario is useful for debugging but not normally part of coverage.

Test signals: Exact `WT_ROLLBACK` versus success depending on truncate time, followed by stable timestamp advancement for clean shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate07.py

Purpose: Checks that truncating ranges containing prepared updates/removes fails correctly.

Important APIs/types/functions: `test_truncate07` uses `WT_ROLLBACK`, `WT_PREPARE_CONFLICT`, `prepare_transaction`, `session.truncate`, optional eviction/checkpoint scenarios, and a helper `truncate` that maps exceptions to WiredTiger return codes.

Control flow: The test writes baseline data at timestamp 10 and marks it stable. A second session modifies every other even key in the middle third and prepares at timestamp 20. The main session optionally evicts and checkpoints, then attempts to truncate a range covering prepared changes. The truncate must return `WT_ROLLBACK`, and the transaction is rolled back.

State and persistence behavior: Prepared updates remain unresolved while the truncate tries to delete across them. Optional eviction lets fast-delete metadata interact with prepared update visibility.

Dependencies and integration points: Integrates prepared transaction conflict detection, fast-delete, checkpointing, timestamp stable advancement, and row/column store behavior.

Risks: Prepared update interactions can return either rollback or prepare conflict depending on path; this test codifies the expected rollback behavior for range truncate.

Test signals: `err == WT_ROLLBACK` after truncate and no successful commit of the truncating transaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate08.py

Purpose: Regression test for avoiding `WT_PREPARE_CONFLICT` when iterating after a committed prepared fast-truncate transaction.

Important APIs/types/functions: Uses `session.truncate`, `prepare_transaction`, `timestamp_transaction` for commit and durable timestamps, `commit_transaction`, `simple_key`, `simple_value`, and cursor iteration.

Control flow: The test populates an 80,000-row small-page table, reopens to force disk state, starts a transaction, truncates keys 10,000 through 70,000, writes a replacement value on a fast-truncated page, prepares at 10, commits/durably commits at 20, and then scans the whole table.

State and persistence behavior: It creates a prepared transaction that both fast-deletes a range and modifies a key on a deleted page, then commits it. After commit, no prepared state should remain visible to readers.

Dependencies and integration points: Integrates fast-delete, prepared transaction resolution, modify-after-truncate behavior, and cursor traversal over row/column tables.

Risks: A stale prepared state in deleted-page metadata can leak `WT_PREPARE_CONFLICT` to ordinary readers after commit.

Test signals: Full cursor traversal completes without error; any prepare conflict during `cursor.next()` fails the test.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate09.py

Purpose: Tests rollback-to-stable behavior for fast-truncated ranges and single-row removes after crash restart.

Important APIs/types/functions: `test_truncate09` uses `simulate_crash_restart`, `session.truncate`, timestamped commits, oldest/stable timestamp setting, checkpoints, `simple_key`, and `simple_value`. It skips disaggregated storage because RTS is unsupported there.

Control flow: The test populates 80,000 rows, reopens, sets oldest/stable to 100, truncates keys 20,000-40,000 at timestamp 150, advances stable to 200 and checkpoints, then truncates 50,000-70,000 and removes key 75,000 at timestamp 250 without stabilizing them. After checkpoint and crash restart, it expects the stabilized truncate to remain deleted but the unstable truncate and remove to be rolled back.

State and persistence behavior: Combines on-disk fast-delete metadata, stable timestamp advancement, checkpointed unstable changes, and recovery-time rollback-to-stable.

Dependencies and integration points: Integrates checkpoint, crash restart, RTS, fast-delete, and row/column formats.

Risks: RTS must distinguish stable and unstable deleted-page metadata. Incorrect handling can either resurrect stable deletes or retain unstable deletes/removes.

Test signals: Searches after restart: key 30,000 not found, key 60,000 found, and key 75,000 found.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate10.py

Purpose: Verifies fast-truncate prepared at 20, committed at 25, and durable at 30 behaves correctly across stable timestamp/checkpoint combinations.

Important APIs/types/functions: `test_truncate10` uses `session.truncate`, prepared transaction APIs, `stat.conn.rec_page_delete_fast`, `check` with read timestamps, snapshot isolation, and scenario dimensions for stable timestamp and checkpoint.

Control flow: The test writes 10,000 rows at timestamp 10, marks stable, reopens, truncates half the table, prepares at 20, commits at 25 with durable 30, checks fast-delete stats, optionally advances stable to 10/20/25/30 and checkpoints, then reads at 10, 20, 25, and 30 to verify expected row counts.

State and persistence behavior: It stresses commit timestamp versus durable timestamp for fast-delete visibility. Reads before commit see all rows; reads at commit/durable see half the rows deleted.

Dependencies and integration points: Integrates prepared transaction timestamp ordering, durable timestamp handling, fast-delete stats, checkpoint, stable timestamp, and tiered hook variability.

Risks: The comment notes reading between commit and durable can be problematic but is currently permitted. Any semantic change there would affect the test.

Test signals: Fast-delete page count, plus exact row counts at each read timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate11.py

Purpose: Ensures checkpoint does not read many pages deleted by a fast-truncate that is not visible to that checkpoint.

Important APIs/types/functions: Uses `checkpoint_thread`, `threading.Event`, `timing_stress_for_test=[checkpoint_slow]`, statistics `stat.conn.checkpoint_state` and `stat.conn.cache_read_deleted`, and `session.truncate`.

Control flow: The test creates an 80,000-row small-page table, reopens, sets oldest/stable to 100, writes a few timestamp-120 updates, starts a checkpoint thread, waits until checkpoint begins, then truncates keys 20,000-40,000 at timestamp 150 and commits. After joining the checkpoint thread, it asserts `cache_read_deleted` is less than 10.

State and persistence behavior: The checkpoint is intentionally concurrent with a later fast-truncate. Deleted pages should not be pulled into cache unnecessarily by a checkpoint that cannot see the truncate.

Dependencies and integration points: Integrates checkpoint concurrency, timing stress, statistics, fast-delete visibility, and thread cleanup. Tiered hook is skipped because regular checkpoint timing matters.

Risks: Race sensitivity is controlled by checkpoint state polling, but timing-based tests can still be environment-sensitive. Excessive deleted-page reads indicate performance and cache pressure regressions.

Test signals: `cache_read_deleted < 10` after concurrent checkpoint and truncate.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate12.py

Purpose: Ensures transaction IDs on fast-truncate metadata remain valid after recovery, even when truncate information is loaded during rollback-to-stable and remains in cache.

Important APIs/types/functions: Uses `simulate_crash_restart`, `stat.conn.rec_page_delete_fast`, `stat.conn.cache_read_deleted`, `session.truncate`, named checkpoint `pointy`, timestamped transactions, and helper `check`.

Control flow: The test writes baseline rows in table 1 at timestamp 10 and stabilizes them, reopens, writes many timestamp-20 rows to table 2 to advance transaction IDs, fast-truncates most of table 1 at timestamp 30, updates retained rows at timestamp 40, advances stable to 35, checkpoints, crashes/restarts, and verifies retained/truncated data at timestamp 50 and in the named checkpoint.

State and persistence behavior: The test depends on fast-delete metadata written to disk and recovery-time RTS rolling back timestamp-40 updates while retaining timestamp-30 truncate. It also verifies deleted pages were not instantiated during recovery.

Dependencies and integration points: Integrates transaction ID visibility, fast-delete, RTS during crash recovery, named checkpoints, statistics, and row/column formats.

Risks: Mishandling write generation or transaction IDs can make truncates invisible after recovery. Instantiating deleted pages during recovery would show up as cache/stat regressions.

Test signals: Fast-delete count, `cache_read_deleted == 0`, and exact data checks in live and checkpoint cursors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate13.py

Purpose: Tests reading gaps created by fast-delete under unstable, stable, and globally visible timestamp states, optionally followed by new data.

Important APIs/types/functions: Uses `session.truncate`, `stat.conn.rec_page_delete_fast`, `debug=(release_evict)`, timestamped checks, and scenarios over range location, timestamp advancement, add/no-add, and key format.

Control flow: The test writes full-table value A at timestamp 20 and value B at timestamp 30, evicts pages, advances stable to 25, checkpoints, then fast-deletes half the table at timestamp 35 from the start, middle, or end. It optionally advances stable and oldest, checkpoints, optionally writes value C at timestamp 45, and validates reads before and after the deletion.

State and persistence behavior: The deleted range can be unstable, stable, or globally visible depending on timestamp advancement. The test validates reads behind the deletion when oldest has not advanced and reads after deletion in all cases.

Dependencies and integration points: Integrates fast-delete, history-store reads through deleted gaps, oldest/stable advancement, checkpoint, eviction, and row/column formats.

Risks: Large deleted gaps can break cursor key ordering or cause missing history when reading behind the delete. Optional new data checks that later updates can repopulate the namespace.

Test signals: Fast-delete stats and exact ordered cursor scans with expected counts and generated values at timestamps 20, 30, 40, and optionally 50.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate14.py

Purpose: Generates very large namespace gaps with truncate to stress instantiation and reconciliation logic over sparse key spaces.

Important APIs/types/functions: Uses `session.truncate`, `stat.conn.rec_page_delete_fast`, `SimpleDataSet`, `simulate_crash_restart` import though not used, timestamped read checks, and scenarios for action `instantiate`, `checkpoint`, and `checkpoint-visible`.

Control flow: The test writes a dense blob, then 20,000 sparse keys separated by 1,000,000,000, then another dense blob at timestamp 20. It stabilizes and reopens, truncates the sparse range at timestamp 30, checks fast-delete stats, stabilizes the truncate, validates remaining rows, and then either reads behind the truncate, checkpoints while not globally visible, or advances oldest before checkpointing. It validates remaining rows again.

State and persistence behavior: Sparse keys create huge logical gaps. The truncate deletes across the sparse namespace, and subsequent actions cover page instantiation and internal-page reconciliation before and after global visibility.

Dependencies and integration points: Integrates fast-delete key-range handling, sparse row/column namespaces, checkpoint, oldest/stable timestamps, and cursor iteration over large key gaps.

Risks: Loops over logical key ranges must not scale with key-space size. Incorrect gap handling can lose the dense boundary rows or hang during instantiation.

Test signals: Row-count checks before and after truncate plus positive fast-delete page stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate15.py

Purpose: Ensures read-only database reads of fast-truncated pages do not leave cache stuck or produce rollback under tight cache settings.

Important APIs/types/functions: `test_truncate15` uses `session.truncate`, prepared transaction commit/durable timestamps, `stat.conn.rec_page_delete_fast`, read-only reopen config, `check`, and `evict_cursor` helper. It skips disaggregated storage because readonly connections are not supported.

Control flow: The test writes 100,000 rows at timestamp 10, stabilizes them, reopens, fast-truncates half the table in a prepared transaction with commit 25 and durable 30, verifies fast-delete occurred, advances stable to 30 and checkpoints, then reopens readonly with a 1MB cache. It reads at timestamps 10, 20, 25, and 30 and treats `WT_ROLLBACK` during reads as failure.

State and persistence behavior: The database is reopened readonly after checkpointing fast-delete metadata. The test verifies read-only cache behavior while reading deleted pages at multiple timestamps.

Dependencies and integration points: Integrates readonly connection mode, fast-delete, prepared durable timestamps, cache eviction settings, and timestamp reads.

Risks: The test is large by design; 50,000 rows was insufficient to trigger the original issue. Cache pressure makes false retries undesirable, so rollback is explicitly trapped and failed.

Test signals: Positive fast-delete count and successful read checks without `WT_ROLLBACK`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate16.py

Purpose: Verifies reads from a page fast-truncated by an unresolved prepared transaction return prepare conflict and instantiate only the needed deleted page.

Important APIs/types/functions: Uses `session.truncate`, `prepare_transaction`, read timestamp transactions, `stat.conn.rec_page_delete_fast`, `stat.conn.cache_read_deleted`, expected `WiredTigerError` with prepare conflict text, and optional checkpoint scenarios.

Control flow: The test writes/stabilizes 10,000 rows at timestamp 10, reopens, starts a second-session transaction that fast-truncates the middle half and prepares at timestamp 20, optionally checkpoints, then reads a key in the truncated range at timestamp 30. The read must raise prepare conflict. It then rolls back the prepared transaction and scans the full table.

State and persistence behavior: Prepared fast-delete metadata remains unresolved. Reading one key should instantiate one deleted page for conflict handling. Rolling back the prepared transaction should not instantiate additional pages.

Dependencies and integration points: Integrates prepared transaction visibility, fast-delete page instantiation, checkpoint interaction, statistics, and row/column formats.

Risks: A regression could either miss the prepare conflict, instantiate too many pages, or leave rollback unable to restore the table view.

Test signals: Expected prepare conflict, `cache_read_deleted` equals 1 for fast-delete cases, full-table scan after rollback, and unchanged deleted-page read count.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate17.py

Purpose: Checks data-source statistics for a prepared fast-truncate and confirms stats instantiate deleted pages without changing page counts before rollback.

Important APIs/types/functions: Adds `stat_tree` over `statistics:<uri>` to read btree entry and page counts. Uses `session.truncate`, `prepare_transaction`, `stat.conn.rec_page_delete_fast`, `stat.conn.cache_read_deleted`, and optional checkpoint scenarios.

Control flow: The test writes 10,000 rows at timestamp 10, stabilizes and reopens, records baseline btree entry/page counts, reopens again, prepares a second-session fast-truncate of the middle half, optionally checkpoints, then reads data-source stats. Stats should show half the entries but unchanged page counts. It verifies `cache_read_deleted` equals the number of fast-deleted pages, then rolls back and checks that value remains unchanged.

State and persistence behavior: Data-source stats are non-transactional/read-uncommitted, so they observe the prepared truncate's logical entry count while the physical deleted pages still exist.

Dependencies and integration points: Integrates btree statistics, prepared fast-delete metadata, checkpoint, page instantiation counters, and row/column page-stat distinctions.

Risks: Stats can accidentally instantiate or discard pages, or report transactionally hidden values. This test deliberately codifies the read-uncommitted behavior.

Test signals: Baseline entries equal nrows, post-prepare entries equal nrows/2, page tuple equals baseline, and `cache_read_deleted == fastdelete_pages`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate18.py

Purpose: Regression test for verification when deleted pages full of obsolete values are optimized into physically empty pages, especially near the leftmost leaf.

Important APIs/types/functions: Uses `session.truncate`, `verifyUntilSuccess`, small `internal_page_max`, timestamp advancement, checkpoints, repeated `reopen_conn`, and `stat.conn.rec_page_delete_fast`.

Control flow: The test writes baseline data at timestamp 10, stabilizes and reopens, truncates either the front or back 7/8 of the table at timestamp 20, verifies fast-delete occurred, stabilizes and reopens, advances oldest so baseline data is obsolete, writes and deletes key 1 to force reconciliation of the first leaf/internal pages, stabilizes/ages out that scratch change, checkpoints, reopens, and runs verify.

State and persistence behavior: The scenario creates globally visible fast-deleted pages containing obsolete values, then forces partial internal-page reconciliation. The key concern is whether verify can handle empty-page optimization without losing physical key-order information.

Dependencies and integration points: Integrates reconciliation, verification, obsolete-value cleanup, fast-delete, oldest/stable advancement, and row/column formats.

Risks: Comments note a known assertion scenario in verify. The test is specific and relies on tree shape from small internal pages and 10,000 rows.

Test signals: Positive fast-delete stats and successful `verifyUntilSuccess(uri=ds.uri)` after the constructed state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate19.py

Purpose: Mimics MongoDB oplog truncation workload and verifies repeated fast-truncate plus append cycles do not leave excessive disk usage.

Important APIs/types/functions: `test_truncate19` uses `SimpleDataSet`, helper `append_rows`, helper `do_truncate` with a high cursor and no low cursor, `stat.conn.rec_page_delete_fast`, checkpoints from another session, `os.path.getsize`, and `suite_random` import though not used. It skips tiered and disaggregated hooks because object file sizes are central to the assertion.

Control flow: The test creates an `oplog` table with one million rows and a dummy table, checkpoints, reopens, then loops 49 times. Each iteration starts a long-running transaction in a third session to keep truncate from becoming globally visible, truncates the oldest 10,000 rows from the main session, verifies fast-delete count, checkpoints, asserts `oplog.wt` is under 600MB, rolls back the long transaction, appends 10,000 rows at the tail, and advances start/end counters. A final checkpoint repeats the size assertion.

State and persistence behavior: The workload repeatedly creates and checkpoints fast-delete metadata while a long-running transaction affects global visibility, then appends new rows to keep logical size steady.

Dependencies and integration points: Integrates fast-delete, checkpoint cleanup, file block reuse/freeing, long-running transaction visibility, and real WT file sizing.

Risks: File-size thresholds can be platform/storage-layout sensitive, so tiered/disagg are skipped. The million-row setup is expensive but necessary to model oplog behavior.

Test signals: Positive fast-delete stats in every iteration and `oplog.wt` remaining below 600,000,000 bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate19.py -->
