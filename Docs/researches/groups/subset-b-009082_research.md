# Research: subset-b-009082

This grouped report covers WiredTiger disaggregated/layered storage tests for follower behavior and follower fast truncate. Each section preserves the source path so it can be split into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate01.py

Purpose: tests basic follower-side range truncate behavior for layered objects, across both `layered:` URIs and `table:` URIs configured with `block_manager=disagg,type=layered`.

Important APIs/types/functions: `test_layered_fast_truncate01` derives from `LayeredFastTruncateConfigMixin` and `wttest.WiredTigerTestCase`, is expanded by `@disagg_test_class` and `make_scenarios`, and uses `wiredtiger.WT_NOTFOUND`, `session.truncate`, explicit transactions, `reopen_conn`, and `disagg_get_complete_checkpoint_meta`.

Control flow: each test creates and populates 1000 string-keyed rows on a leader, checkpoints, reopens as follower at the produced checkpoint, and then exercises truncate. `test_truncate_basic` checks isolation before commit and invisibility after commit from a second session. `test_truncate_rollback` checks rollback restores visibility. `test_truncate_write_conflict_1` keeps a truncate uncommitted and verifies a concurrent update inside the range raises the expected conflict.

State and persistence behavior: the test transitions stable checkpointed data into follower mode, then verifies follower-local truncate state affects only committed visibility unless rolled back.

Dependencies/integration points: depends on WiredTiger Python test harness, disaggregated storage helpers, checkpoint metadata pickup, and the shared fast-truncate mixin. Risks are missed cleanup of cursors/sessions and scenario differences between native layered and table-layered configurations. Test signals are exact search return codes and expected conflict message text.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate02.py

Purpose: validates that a follower reading a checkpoint containing leader-created fast-truncated pages sees correct MVCC visibility and cursor behavior.

Important APIs/types/functions: class `test_layered_fast_truncate02` uses `LayeredFastTruncateConfigMixin` helpers `leader_checkpoint`, `truncate`, `open_follower`, and `search_at`, plus `wiredtiger.WT_NOTFOUND`. It sets `cache_size=50MB,statistics=(all),disaggregated=(role="leader")` and creates a `layered:` table with integer keys.

Control flow: `setup_leader` inserts 5000 rows at timestamp 10, checkpoints, then walks a `debug=(release_evict)` cursor so truncation can use page-level fast-delete markers. `test_visibility` truncates 1001-4000 at ts=20, checkpoints, opens a follower, and checks deleted, boundary, and exterior keys at ts=20 and ts=15. `test_pre_truncation_read_sees_all_rows` scans at ts=10 and expects all rows. `test_cursor_scanning` verifies forward scans, reverse scans, and `search_near` skip the truncated range.

State and persistence behavior: the important state is a stable checkpoint containing fast-delete metadata and timestamped deletes that remain invisible to pre-truncate reads.

Dependencies/integration points: integrates eviction, timestamped checkpoints, follower checkpoint advance, cursor search paths, and disaggregated layered pages. Risks include insufficient eviction preventing fast-delete coverage and cursor-direction edge cases. Test signals are counts, exact landed keys, and timestamped visibility assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate03.py

Purpose: proves follower reads of leader fast-truncated pages do not dirty stable pages and that deleted state survives eviction, follower reopen, ingest writes, and timestamped instantiation.

Important APIs/types/functions: `test_layered_fast_truncate03` uses `wiredtiger.stat`, `cache_pages_dirty`, `cache_read_deleted`, mixin helpers `evict_range`, `search_at`, `open_follower`, and a local `advance_follower` wrapper around leader checkpoint plus `disagg_advance_checkpoint`.

Control flow: `setup_leader` inserts timestamped rows, checkpoints, and evicts all pages; optional `leaf_page_max=4096` forces many leaf pages. `test_no_dirty_on_read` reads sample deleted keys, evicts/reloads them, and asserts dirty-page stats stay unchanged. `test_page_split_with_ingest_writes` writes a subset of truncated keys on the follower after checkpoint advance and checks timestamped visibility. `test_state_preserved_on_reopen` opens two cold follower connections against the same checkpoint. `test_instantiation_not_globally_visible` reads below the truncate timestamp, expecting `cache_read_deleted` to rise without dirtying.

State and persistence behavior: deleted-page state is kept as checkpoint metadata / fast-delete state, while later ingest writes override only their keys at later timestamps.

Dependencies/integration points: depends on statistics stability, debug eviction, disaggregated checkpoint pickup, and timestamp reads. Risks are false negatives if page eviction does not happen or stats are reused unexpectedly. Test signals are WT_NOTFOUND, stable values, and counter deltas.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate04.py

Purpose: validates follower cursor read paths over fast-truncated ranges, including scans, `search`, `search_near`, open-ended bounds, multiple ranges, overlaps, appends, and updated-then-truncated keys.

Important APIs/types/functions: uses `LayeredFastTruncateConfigMixin` methods `setup_leader`, `setup_follower`, `truncate`, `visible_keys`, `search_near_key`, `populate`, and `key_exists`. The local `key` returns zero-padded string keys so string ordering matches numeric ordering; scenarios cover both `layered:` and table-layered URIs.

Control flow: each test populates 1000 leader rows, reopens as follower, applies one or more truncates, and then checks expected key lists. Cases cover bounded [100,700], full-table truncates, truncates to end, disjoint and overlapping ranges, mixed bounded/open-ended ranges, appends after open-ended truncate, local updates later covered by truncate, and `search_near` direction fallback.

State and persistence behavior: open-ended truncates capture the end key at commit time rather than hiding later appends; follower ingest updates remain visible only if not later covered by truncate.

Dependencies/integration points: exercises logical layering between stable and ingest tables and layered cursor positioning. Risks are off-by-one boundary bugs and direction-specific cursor leaks. Test signals are exact visible-key arrays, boolean key existence, and `search_near` landed keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate05.py

Purpose: tests that follower `next_random=true` cursors do not return keys hidden by a fast truncate range.

Important APIs/types/functions: `test_layered_fast_truncate05` uses the shared mixin setup/truncate helpers, zero-padded string keys, and a local `sample_assert_random` helper that opens `next_random=true` cursors and samples 200 keys inside a transaction.

Control flow: tests populate 1000 leader rows, reopen as follower, apply truncate 100-700, and repeatedly call `cursor.next()` on a random cursor. The second test first writes keys 200-400 into the follower ingest component, then truncates a range covering them and reuses the random-sampling assertion.

State and persistence behavior: the follower has a stable component from the checkpoint and optionally ingest updates. The truncate must hide both stable and ingest keys in the range when random selection traverses layered visibility.

Dependencies/integration points: depends on random cursor support over layered tables, disaggregated scenarios, and transaction-scoped cursor operations. Risks are probabilistic coverage because random sampling cannot prove absence exhaustively; the 200 draws are a regression signal, not a formal enumeration. Test signals are successful random cursor positioning and no sampled key between the truncated bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate06.py

Purpose: regression test for WT-17267, ensuring `session.verify()` on a layered URI does not discard the follower's in-memory truncate list when it closes and reopens the layered dhandle.

Important APIs/types/functions: `test_layered_fast_truncate06` uses `LayeredFastTruncateConfigMixin`, `session.verify`, timestamped row inserts, `session.checkpoint`, and `super().setup_follower()` to reopen as follower. Scenarios cover both explicit `layered:` URI and table-layered form.

Control flow: `setup_follower` creates 100 integer-keyed rows on the leader, each with its own commit timestamp, checkpoints, and reopens as follower. The main test truncates 30-60, scans outside a transaction via `visible_keys_simple`, verifies the URI, and scans again.

State and persistence behavior: the tested state is the follower truncate list attached to the layered dhandle. It must survive dhandle lifecycle events induced by verify; otherwise truncated rows would reappear.

Dependencies/integration points: integrates verify with layered/disaggregated dhandle management and follower local truncate visibility. Risks are that verify behavior or dhandle cache policy changes can mask the original bug. Test signals are exact visible key lists before and after verify.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate07.py

Purpose: verifies that follower-initiated range truncate resolves NULL start/stop cursors to concrete first/last visible keys and logs the bounded truncate list entry.

Important APIs/types/functions: class `test_layered_fast_truncate07` uses verbose config `verbose=[layered:3]`, `captureout.checkAdditionalPattern`, `cleanStdout`, local `insert_range`, `follower_visible_keys`, `expected_keys`, and `assert_trunc_log`. Scenarios cover string and integer key formats.

Control flow: `setup_follower` creates a layered table, inserts keys 1-100 on the leader, checkpoints, and reopens as follower with checkpoint metadata and layered verbose logging. Tests cover bounded ranges, null start, null stop, both null, open-ended truncates followed by appends, and overlaps where a second open-ended truncate must search-near past already-deleted keys before logging a concrete range.

State and persistence behavior: open-ended API calls are normalized into bounded entries in the follower truncate list. Later appends after an open-ended truncate remain visible.

Dependencies/integration points: relies on verbose log string shape, disaggregated checkpoint metadata, key string formatting, and cursor search-near behavior during overlap resolution. Risks include fragile log-pattern coupling. Test signals are log entries and exact forward/backward visible keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate08.py

Purpose: ensures follower range truncate writes the layered tombstone sentinel into the ingest file instead of creating normal `WT_UPDATE_TOMBSTONE` records via `cursor->remove()`.

Important APIs/types/functions: uses `LayeredFastTruncateConfigMixin`, `contextlib.closing`, byte-string value format `value_format=u`, local `populate`, `get_values`, and direct inspection of `file:<test_name>.wt_ingest`.

Control flow: the leader creates the initial layered table and checkpoint through `setup_layered_table`; the follower reopens and populates ingest keys 0-99. The test truncates 20-80, opens the ingest file directly, and searches every key in the range to collect stored values.

State and persistence behavior: follower truncate is represented as real ingest rows carrying sentinel value `b"\x14\x14"`, so direct ingest-file search still finds each truncated key. This differentiates layered tombstone encoding from ordinary delete tombstones that would be invisible to a cursor search.

Dependencies/integration points: tightly coupled to ingest file naming (`.wt_ingest`) and sentinel encoding. Risks are false failures if sentinel representation or ingest filename convention changes. Test signals are value count equal to truncated key count and all values matching the sentinel.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate09.py

Purpose: covers transaction and timestamp visibility rules for follower truncate-list entries.

Important APIs/types/functions: `test_layered_fast_truncate09` uses `wiredtiger.WT_NOTFOUND`, explicit sessions, `with self.transaction(...)`, local `truncate_range`, `search_in`, `search_near_in`, `next_key_after`, and `commit_truncate`. It sets up in `setUp`, so each test starts with a populated follower.

Control flow: setup writes 1000 integer-keyed stable rows at timestamp 10, checkpoints at stable timestamp 10, and reopens as follower. Tests assert a session sees its own uncommitted truncate, another session ignores that uncommitted truncate, rollback restores visibility, committed truncates obey read timestamps, and overlapping truncates at timestamps 20 and 40 expose only the timestamp-visible delete ranges.

State and persistence behavior: truncate entries participate in transaction isolation and timestamp visibility, including overlap union only for entries visible to the reader.

Dependencies/integration points: integrates session isolation, read timestamps, layered `search`, `search_near`, and cursor `next` movement. Risks include helper methods opening cursors outside caller transaction expectations. Test signals are search return/value tuples, `search_near` exact/landed pairs, and next-key assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate10.py

Purpose: verifies follower fast truncate operates over the logical union of stable and ingest data, independent of which physical component contains a key.

Important APIs/types/functions: uses `LayeredFastTruncateConfigMixin`, `concat`, `range_inclusive`, and scenarios for `layered:fast_truncate` plus `table:fast_truncate`. Shared helpers create stable data with `setup_leader`, follower ingest data with `setup_follower`, apply `truncate`, and enumerate `visible_keys`.

Control flow: tests cover empty stable/ingest, ranges that hit no keys, ranges that cover only stable keys, only ingest keys, disjoint stable/ingest keys, overlapping stable/ingest keys, and partial overlap across both tables. Each test computes the exact expected logical key list after truncate.

State and persistence behavior: stable keys come from leader checkpoint state; ingest keys are follower-local writes. Truncate must treat the layered view as one sorted table and hide every key in the specified range regardless of component.

Dependencies/integration points: checks integration between stable table cursor, ingest table cursor, range delete bookkeeping, and table-layered configuration. Risks are duplicate/overlap resolution bugs where one component leaks a key hidden in the other. Test signals are exact visible-key arrays.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate11.py

Purpose: tests follower fast-truncate range specification: NULL start/end, full table, single-key truncates, empty gaps, invalid ordering, and open-ended behavior after later appends.

Important APIs/types/functions: uses `LayeredFastTruncateConfigMixin`, `concat`, `range_inclusive`, `wiredtiger.WiredTigerError`, `assertRaisesWithMessage`, and scenarios for native layered and table-layered URIs.

Control flow: each case creates a follower with specified keys, calls `truncate` with one range shape, and checks `visible_keys`. `test_truncate_with_start_greater_than_end` expects `/Invalid argument/`, rolls back the session, and verifies all rows remain. The open-ended append case truncates 80-end, then populates 200-210 and verifies those later keys survive.

State and persistence behavior: open-ended bounds are resolved against the visible table at commit time. Empty gaps do not alter state; invalid ranges must fail without partial effects.

Dependencies/integration points: integrates API-level `session.truncate` argument validation with layered visibility and follower ingest writes. Risks include off-by-one errors and inconsistent rollback state after an invalid truncate. Test signals are exact key arrays and specific WiredTiger error matching.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate12.py

Purpose: comprehensively validates cursor iteration and point-search APIs over follower truncated ranges.

Important APIs/types/functions: uses shared helpers `visible_keys`, `key_exists`, `search_near_key`, `populate`, `auto_closing_cursor`, `transaction`, `concat`, and `range_inclusive`. The local `random_sample_keys` reads from a `next_random=true` cursor.

Control flow: tests create followers with keys 1-100 or stable-only setup, truncate ranges such as 30-60 or 30-end, and verify forward scans, backward scans, random cursor samples, search inside/boundary cases, `search_near` inside/boundary cases, forward-then-backward fallback, and choosing a live ingest key inside an earlier truncated stable range before the next stable key.

State and persistence behavior: truncates hide stable keys, but later follower ingest writes can make a key in the range visible again at the latest view. API paths must converge on the same logical visibility.

Dependencies/integration points: exercises multiple cursor implementations in the layered cursor. Risks include random sample probabilism and direction-sensitive cursor bugs. Test signals are exact scan lists, no random key in range, boolean searches, and expected `search_near` exact/landed pairs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate13.py

Purpose: verifies follower truncate composition with existing truncates, per-key removes, and reinsertion.

Important APIs/types/functions: uses the shared mixin plus local `remove_key`, which opens a cursor, positions on `self.key(key)`, and calls `cursor.remove()` in a transaction. Scenarios cover both URI forms.

Control flow: each test builds a 1-100 follower dataset, then performs combinations: per-key remove before truncate, same truncate twice, broader truncate after a narrower one, overlapping ranges, disjoint ranges, bounded plus open-ended ranges, truncate then reinsert within the same transaction, and truncate then reinsert in a later transaction.

State and persistence behavior: multiple truncate-list entries must compose as unions for scans; duplicate entries must be harmless. Per-key tombstones and later inserted values must layer correctly over earlier range tombstones. Reinsertion at key 45 is expected to make only that key visible within the formerly truncated range.

Dependencies/integration points: stresses update-chain ordering in the ingest component, range-list overlap logic, and transaction-local ordering when truncate and insert occur in one transaction. Risks include redundant truncates corrupting state or reinserts being masked. Test signals are exact expected visible-key lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate14.py

Purpose: checks that `cursor.next()` skips truncated stable keys after `search_near` lands exactly on an ingest key.

Important APIs/types/functions: class `test_layered_fast_truncate14` uses `LayeredFastTruncateConfigMixin` and local `keys_after_search_near`, which positions a cursor with `search_near`, requires exact match, then drains subsequent `next()` keys inside a rollback transaction.

Control flow: tests set up small stable key sets and follower ingest keys, truncate a range in stable space, call `keys_after_search_near` from an ingest key, and assert the subsequent sequence omits any truncated stable key. Cases include one truncated stable key, multiple consecutive stable keys, an ingest key adjacent to the range, and multiple ingest keys before the truncated gap.

State and persistence behavior: the cursor is positioned on ingest while the next stable candidate may be hidden by the truncate list. The layered cursor must advance past hidden stable keys and continue merging remaining stable/ingest keys.

Dependencies/integration points: narrow integration test for layered merge-cursor movement after `search_near`. Risks are stateful cursor-position bugs that only appear after exact ingest hits. Test signals are absence of truncated keys and exact next-key lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate15.py

Purpose: validates that follower truncate tombstones only ingest keys inside the truncate range and does not tombstone flanking ingest keys.

Important APIs/types/functions: uses the shared mixin with `setup_leader`, `setup_follower`, `truncate`, `key_exists`, and `visible_keys`. Scenarios cover native layered and table-layered URIs.

Control flow: tests create small stable key sets with follower ingest keys below, above, or on both sides of a truncate range. After truncation, they check stable keys inside the range are hidden while ingest keys outside the range remain visible. One case checks the complete scan result `[0, 5, 25, 30]`.

State and persistence behavior: the ingest component may contain keys close to, but outside, the stable range being truncated. The truncate implementation must avoid over-eager tombstone writes beyond the bounds.

Dependencies/integration points: focuses on boundary handling in the follower truncate code that drains/marks ingest keys. Risks are off-by-one or cursor-position errors that tombstone adjacent ingest entries. Test signals are point existence assertions and one full visible-key scan.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate16.py

Purpose: verifies that pending follower truncates are drained correctly into stable storage when a follower steps up to leader, across range shapes, timestamps, mixed per-key histories, and layered removes.

Important APIs/types/functions: class `test_layered_fast_truncate_stepup` uses the fast-truncate mixin, separate `conn_follow/session_follow`, local `populate_on_leader`, `write_kv`, `remove_kv`, `truncate_range`, `assert_visible`, `assert_deleted`, and `assert_keys_gone`. `step_up()` comes from the mixin and calls `disagg_switch_follower_and_leader`.

Control flow: setup creates 1000 stable integer keys at ts=10 and opens a follower. Tests cover stable-only truncates, ranges with follower updates, reinsert after truncate, single/start/end/full/empty ranges, multiple/duplicate/overlapping truncates, snapshot reads before/at/after truncate timestamps, mixed stable and follower-updated keys, empty truncate list step-up, post-step-up writes, ingest keys exactly at bounds, truncates below stable timestamp, and remove/truncate combinations including same timestamp.

State and persistence behavior: follower truncate-list state must be replayed into leader-stable history with correct commit timestamps, while reinserts and previous removes preserve MVCC gaps.

Dependencies/integration points: tests role transition, ingest drain, stable reconciliation, timestamp reads, and layered tombstone semantics. Risks are timestamp ordering regressions and boundary ownership bugs between stable windows and ingest entries. Test signals are exhaustive key sweeps plus timestamped point reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate17.py

Purpose: confirms step-up replay of follower truncates uses page-level fast truncate (`WT_REF_DELETED`) rather than only per-key deletes.

Important APIs/types/functions: uses `wiredtiger.stat`, `stat.conn.rec_page_delete_fast`, `LayeredFastTruncateConfigMixin`, `open_follower`, `leader_checkpoint`, `search_at`, and local `assert_fast_truncate_fired` and `assert_ranges_deleted`. The table uses `leaf_page_max=4096` and 5000 rows to make interior pages eligible.

Control flow: setup creates the leader table, writes all rows at ts=10, checkpoints, and opens a follower. Tests create one large interior truncate or three disjoint ranges on the follower, record the fast-delete statistic, step up, assert the statistic increased, and then scan/search all keys at ts=30 for expected deletion.

State and persistence behavior: pending follower truncate ranges become stable deleted-page state during role promotion. Boundary pages are left outside the range to make fast-delete eligibility clear.

Dependencies/integration points: integrates follower step-up drain with WiredTiger reconciliation fast-delete counters. Risks include test sensitivity to page layout or stat semantics. Test signals are counter increase and full key-space visibility validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate18.py

Purpose: tests write conflict detection for overlapping follower fast-truncate operations.

Important APIs/types/functions: uses `closing`, `nullcontext`, `WiredTigerError`, shared mixin helpers, and local explicit-session helpers `cursor_on`, `auto_closing_session`, `cursor_for_key`, and `truncate_on`. The expected conflict message is `/conflict between concurrent operations/`.

Control flow: tests start from a 1-100 stable follower dataset. They verify multiple truncates in the same transaction do not self-conflict; overlapping uncommitted truncates from another session conflict with and without ingest keys; non-overlapping truncates commit; a rolled-back truncate leaves no residual conflict; an invisible committed truncate still conflicts for a reader at an older timestamp; and a visible committed truncate does not conflict for a later read timestamp.

State and persistence behavior: truncate entries carry transactional visibility and conflict metadata beyond simple read visibility. A truncate invisible to a transaction can still cause write conflict if overlapping.

Dependencies/integration points: integrates WT rollback/conflict detection, timestamped transactions, and layered truncate list bookkeeping. Risks are leaks from hand-managed transactions if a failure path changes. Test signals are expected exceptions or successful commit paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate19.py

Purpose: verifies that fast truncate suppresses internal page delta writes when reconciliation sees a deleted child reference.

Important APIs/types/functions: this class derives directly from `wttest.WiredTigerTestCase`, enables `page_delta=(internal_page_delta=true,leaf_page_delta=false,delta_pct=100)`, and reads dsrc/connection stats including `rec_page_delta_rejected_invalid_page_id`, `rec_page_delta_internal`, `rec_page_delete_fast`, and `cache_read_deleted`.

Control flow: setup uses tiny page sizes to create a multi-level tree, inserts 200 rows, checkpoints, and evicts leaves. Before reopen, a normal update should reject delta due to invalid disaggregated page id. After `reopen_disagg_conn`, normal updates outside the truncation range must increase internal delta stats. Then `truncate_and_checkpoint(50,150,20)` must trigger fast delete, avoid instantiating deleted pages, and leave the internal delta counter unchanged.

State and persistence behavior: the test follows page-id assignment, fast-deleted leaf state, and internal reconciliation output across checkpoint/reopen.

Dependencies/integration points: highly dependent on page layout, eviction, page-delta feature flags, and stat counters. Risks are brittle configuration if page eligibility changes. Test signals are stat deltas, WT_NOTFOUND for truncated boundaries, and no `cache_read_deleted` increase.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate20.py

Purpose: exercises `debug_mode.disagg_slow_truncate_follower` parsing and verifies the knob selects slow versus fast follower truncate behavior.

Important APIs/types/functions: uses `LayeredFastTruncateConfigMixin`, `wiredtiger.WiredTigerError`, `wiredtiger.stat`, `stat.conn.layered_curs_remove`, `reopen_conn`, `reconfigure`, `reopen_disagg_conn`, and `expectedStderrPattern`.

Control flow: the config smoke tests open connections with the knob true, false, omitted, toggle it by reconfigure, and reject a non-boolean value. Behavior tests populate 500 leader keys, reopen as follower with the knob set, capture `layered_curs_remove`, truncate 100-400, and compare stat deltas. Slow mode must call cursor remove once per key; fast mode must not call cursor remove when ingest is empty.

State and persistence behavior: the knob affects the follower truncate implementation path, not the logical output. The observed state is a connection statistic showing whether per-key remove was used.

Dependencies/integration points: integrates connection config parsing, debug-mode reconfiguration, fast truncate, and statistics. Risks include stat renames or slow path behavior changing. Test signals are accepted/rejected config and exact/remove-zero stat deltas.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate21.py

Purpose: regression test for parent reconciliation after instantiated fast-truncate leaves become globally visible; parent images must be rebuilt as full base images rather than unsafe deltas referencing freed leaf blocks.

Important APIs/types/functions: uses direct `wttest.WiredTigerTestCase`, page-delta config, `wiredtiger.stat`, tiny page sizing, `debug=(release_evict)`, `reopen_disagg_conn`, timestamp management, and `session.verify`.

Control flow: setup inserts 200 rows, checkpoints, evicts leaves, and reopens so internal pages have valid disaggregated page ids. It fast-truncates 50-150 at ts=20 and checkpoints while oldest remains low, so proxy cells remain. It then reads inside the truncated range at ts=10 to instantiate fully covered leaves, advances oldest/stable to 30, updates only boundary leaves at ts=35 to encourage parent delta mode, checkpoints, and verifies the table.

State and persistence behavior: tracks deleted leaf instantiation, global visibility, proxy-cell removal, block freeing, and parent reconciliation. The correctness signal is that verify passes after the potentially dangerous state transition.

Dependencies/integration points: relies on fast-delete eligibility, page-delta machinery, oldest timestamp advancement, and verify catching stale block references. Risks are page layout sensitivity. Test signals are fast-delete and read-deleted stat increases followed by successful `session.verify`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate_stress01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate_stress01.py

Purpose: long-running randomized stress test for follower fast truncate correctness across repeated leader/follower switches in disaggregated WiredTiger.

Important APIs/types/functions: defines `operations` enum, `OpenTruncate`, `HistoryEntry`, `ValidationModel`, and `test_layered_fast_truncate_stress01`. It uses `random`, timestamped transactions, `disagg_switch_follower_and_leader`, `disagg_advance_checkpoint`, and model-based validation.

Control flow: `populate_initial_leader` seeds all keys and the validation model. Each round builds a random stream of inserts, updates, removes, and truncates; keeps non-overlapping truncates open; commits them at new timestamps; skips conflicting single-key writes inside open truncate ranges; then switches roles, restarts the old leader as follower, advances checkpoint, and validates the new leader. Regular mode uses 5000 keys and 160 rounds; long mode scales to 200000 keys and 1600 rounds.

State and persistence behavior: `ValidationModel` stores full per-key timestamp history, latest snapshots, and value-at-timestamp lookups. It verifies both current full scans and sampled historical reads after every switch.

Dependencies/integration points: integrates randomized workload generation, role switching, checkpoint pickup, follower truncate replay, and MVCC history. Risks include deliberate exclusion of write-conflict scenarios (FIXME-WT-17637) and seed-dependent failures. Test signals include reproducible seed logging, full-scan equality, and sampled point-read assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate_stress01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower01.py

Purpose: validates that a disaggregated follower can use the ingest component of a layered table without any stable component.

Important APIs/types/functions: class `test_layered_follower01` derives from `wttest.WiredTigerTestCase`, uses `@disagg_test_class`, `gen_disagg_storages`, `make_scenarios`, `wiredtiger.Modify`, `WT_NOTFOUND`, cursor scans, `largest_key`, and `next_random=true`.

Control flow: the connection starts as `disaggregated=(role="follower")`. Tests create a layered table, write only follower-local ingest records, and then exercise forward scan, reverse scan, modify operations, search and `search_near` on missing/found keys, `largest_key`, and random cursors. `test_secondary_modifies_without_stable` updates every tenth value via `cursor.modify`.

State and persistence behavior: all data lives in the follower ingest table; no stable checkpoint data is required. The test checks that reads, writes, modifies, and cursor navigation work in this ingest-only state.

Dependencies/integration points: integrates layered cursor APIs with the follower role, timestamped commits, and value modification. Risks are large loop cost (`nitems=10000`) and assumptions about lexical largest key among `"Hello"`, `"Hi"`, and `"OK"` prefixes. Test signals are item counts, exact modified values, search return codes, largest key, and random key prefix.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower02.py

Purpose: tests leader/follower disaggregated operation with oplog-style replicated writes and repeated checkpoint pickup.

Important APIs/types/functions: uses `helper_disagg.Oplog`, `WiredTigerCursor`, `statistic_uri`, connection statistics `checkpoints_total_succeed` and `layered_table_manager_checkpoints_disagg_pick_up_follower`, plus `disagg_advance_checkpoint`.

Control flow: the leader creates a layered table and an `Oplog` stream. A follower connection creates the same table. The test applies insert/update traffic to the leader, checkpoints, applies a prefix of operations to the follower, advances checkpoint, and validates follower contents. A loop repeats checkpoint creation, optional new leader traffic, follower catch-up to at least checkpoint position, checkpoint pickup, and full checks.

State and persistence behavior: leader stable checkpoints coexist with follower-applied ingest operations. Checkpoint pickup should add stable content without losing or double-applying follower-local oplog progress.

Dependencies/integration points: integrates helper oplog generation, statistics logging, disaggregated checkpoint manager, and layered table reads. Risks include quadratic checking from position 0 and dependence on exact statistic counts. Test signals are oplog consistency checks and checkpoint/pickup statistic equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower03.py

Purpose: verifies historical reads after reopening or restarting without local files in disaggregated/layered configurations.

Important APIs/types/functions: uses `restart_without_local_files`, `disagg_get_complete_checkpoint_meta`, `reopen_conn`, `conn.reconfigure`, timestamped transactions, and scenarios for `layered:` URI, table-layered disagg, and shared table disagg without logging.

Control flow: a node starts as follower, steps up to leader, creates a table, writes 500 rows at timestamp 100, checkpoints, updates all rows at timestamp 200, sets oldest/stable timestamps, and checkpoints again. It verifies reads at both timestamps, then reopens while keeping local files and reconfigures checkpoint metadata/leader role. Finally it restarts without local files and again verifies reads at both timestamps.

State and persistence behavior: tests that stable checkpoint and history-store content are available after local-file loss and role changes, preserving older values at timestamp 100 and newer values at 200.

Dependencies/integration points: uses precise checkpoints, checkpoint metadata, history store, role reconfiguration, and helper restart mechanics. Risks include precise-checkpoint timestamp requirements. Test signals are exact per-key values under timestamped reads after both restart paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower04.py

Purpose: ensures a follower picking up a checkpoint adds the stable component of a layered table, and that this works after role reversal.

Important APIs/types/functions: uses `disagg_advance_checkpoint`, direct `conn.reconfigure` role switches, precise checkpoint config, and scenarios for native `layered:` and table-layered URIs.

Control flow: the initial node starts as follower, steps up to leader, creates a follower connection, and creates matching tables. The leader writes 5000 rows and checkpoints; before checkpoint advance, only the leader sees the rows. After `disagg_advance_checkpoint`, the follower sees them. Then the follower is promoted to leader and the old leader steps down. The new leader writes another 5000 rows and checkpoints; the old leader only sees old rows until checkpoint advance, after which it sees all rows.

State and persistence behavior: checkpoint pickup materializes stable table content on the follower; role switch preserves and extends the stable component.

Dependencies/integration points: integrates role transitions, precise checkpoint timestamp setup, and layered/table-layered creation. Risks are missing timestamp updates before precise checkpoint. Test signals are scan item counts before and after checkpoint pickup in both directions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower05.py

Purpose: verifies a follower picks up and applies file ID high-water marks so new tables created after step-up do not reuse old leader file IDs.

Important APIs/types/functions: uses `metadata_helper.extract_id`, `metadata:` cursors, `disagg_advance_checkpoint`, role reconfiguration, `debug=(skip_checkpoint=true)` close, and layered table creation/drop.

Control flow: the leader creates 100 layered tables and checkpoints, then scans metadata entries to record the maximum file ID. It drops those tables and checkpoints again. A follower opens, advances to the latest checkpoint, the original leader is closed without a shutdown checkpoint, and the follower steps up. The new leader creates another table, checkpoints, scans metadata again, and asserts the new maximum file ID is greater than the old leader high-water mark.

State and persistence behavior: checkpoint metadata must carry enough ID allocation state for a promoted follower to allocate monotonically increasing IDs even after old objects were dropped.

Dependencies/integration points: integrates metadata parsing, disaggregated checkpoint pickup, PALite/double-free avoidance by skip checkpoint, and file ID allocation. Risks are metadata format changes affecting `extract_id`. Test signal is `follower_max_file_id > max_file_id`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower06.py

Purpose: tests reading pinned history store content on a standby/follower after checkpoint advancement.

Important APIs/types/functions: uses a separate follower connection, timestamped transactions, `disagg_advance_checkpoint`, precise checkpoint config, and a long-running read transaction on the follower.

Control flow: the leader creates a layered table, writes key `"1"` at ts=2 and key `"2"` at ts=3, sets stable/oldest, checkpoints, and advances the follower. The follower begins a read transaction at ts=2 and reads `"1"`. The leader then writes an update at ts=4, advances oldest to 3, checkpoints, and the follower advances again. The still-open follower read transaction resets its cursor and reads `"1"` at ts=2 again.

State and persistence behavior: the follower read transaction pins the history store dhandle/content needed for an older timestamp even after newer checkpoint pickup and obsolete-version movement.

Dependencies/integration points: integrates history store pinning, checkpoint pickup, oldest timestamp advancement, and follower read transactions. Risks include resource pinning semantics changing. Test signal is successful repeated read of `"value1"` at the old timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower07.py

Purpose: confirms checkpoint cleanup does not run on a follower connection.

Important APIs/types/functions: class `test_layered_follower07` derives from `DisaggConfigMixin` and `test_cc_base`, uses `checkpoint_cleanup=[wait=1,file_wait_ms=0]`, `session.checkpoint('debug=(checkpoint_cleanup=true)')`, and statistic `stat.conn.checkpoint_cleanup_success`. It is skipped for the tiered hook.

Control flow: the follower creates and populates a small table via `test_cc_base.populate`, sleeps to let checkpoint cleanup run, forces a checkpoint with cleanup debug enabled, then opens `statistics:` and reads the cleanup-success counter.

State and persistence behavior: even though cleanup is configured and explicitly triggered, follower role should block checkpoint cleanup from running, preserving follower-disaggregated invariants.

Dependencies/integration points: integrates checkpoint cleanup server, follower role checks, and statistics. Risks include timing sensitivity from `sleep(1)` and stat semantics. Test signal is `checkpoint_cleanup_success == 0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower08.py

Purpose: tests delete behavior on a follower's ingest table for layered tables.

Important APIs/types/functions: uses `wiredtiger.WT_NOTFOUND`, scenarios for string (`S`) and integer (`I`) value formats, a local `value` converter, and follower config with `disaggregated=(lose_all_my_data=true)` plus follower role.

Control flow: the test creates a `layered:test_layered_follower08` table with string keys and scenario value format. It inserts keys `"0"` through `"99"` directly into the follower ingest table, then removes each key through the same layered cursor. It resets the cursor, checks `next()` returns not found, and point-searches every key to ensure removal.

State and persistence behavior: all records are follower-local ingest records; deletes should leave the layered table logically empty for both scan and point-read paths.

Dependencies/integration points: exercises follower ingest deletes independent of stable checkpoints and across value encodings. Risks are lack of explicit transactions around inserts/removes, relying on autocommit semantics. Test signals are successful removes and WT_NOTFOUND for full scan and all point searches.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower09.py

Purpose: tests pinning of ingest table content by an active read transaction while data becomes obsolete and checkpoints advance.

Important APIs/types/functions: uses `Oplog`, `disagg_advance_checkpoint`, `debug=(release_evict)` cursor on `file:test_layered_follower09.wt_ingest`, large cache config, and timestamped read transactions.

Control flow: leader and follower create matching layered tables. An oplog inserts 20000 rows on both. A second follower session starts a read transaction at the insert timestamp and opens a cursor, pinning the ingest content. The oplog then removes all rows on leader and follower, leader advances oldest/stable and checkpoints, follower advances checkpoint, and eviction is triggered across ingest keys. The pinned cursor continues scanning and must still see all original rows.

State and persistence behavior: active readers pin older ingest versions even after those records are deleted, made obsolete, and checkpoint state advances.

Dependencies/integration points: integrates oplog helper, ingest file eviction, timestamped reads, checkpoint pickup, and obsolete cleanup. Risks are heavy row count and eviction loop cost. Test signal is final cursor count equal to `nitems`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower10.py

Purpose: tests garbage collection of redundant follower ingest-table content after stable checkpoints are picked up, including inserts, tombstones, and open-cursor cases.

Important APIs/types/functions: uses `Oplog`, direct ingest URI `file:test_layered_follower10.wt_ingest`, helper `evict_ingest`, `count_ingest`, `disagg_advance_checkpoint`, and precise checkpoint config. `count_ingest` classifies values with length >2 as data and shorter values as tombstones.

Control flow: `setup` creates leader/follower tables. `test_gc_ingest_table` inserts data, advances checkpoint, proves open cursors prevent GC, closes them, advances another checkpoint, and expects ingest empty. `test_gc_ingest_table_with_remove` covers insert-then-remove chains and tombstones becoming removable only after a later stable checkpoint and cursor release. `test_gc_ingest_with_cursor` and `test_gc_ingest_with_no_open_cursor` cover first checkpoint pickup with and without pinned cursors.

State and persistence behavior: ingest records are pruned only when redundant with stable data and not pinned by open cursors; tombstones remain until deletes are represented in stable state.

Dependencies/integration points: integrates eviction-driven ingest GC, checkpoint prune timestamps, cursor pinning, and direct ingest inspection. Risks include value-length tombstone heuristic and heavy eviction loops. Test signals are exact `(data,tombstone)` counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower11.py

Purpose: ensures user tombstones in a follower ingest table are not removed until they are included in a checkpoint.

Important APIs/types/functions: uses separate leader and follower connections, timestamped `leader_put_data`, `checkpoint`, `create_follower`, `debug=(release_evict_page=true)` eviction sessions, `cursor.remove`, and `session.truncate`.

Control flow: both tests create a layered table, write leader data, checkpoint, and advance follower. `test_remove` removes every key on the follower with increasing commit timestamps, makes deletes globally visible on the follower, forces eviction over all deleted keys, and confirms they stay invisible. `test_truncate` performs a follower truncate from the first key to the end, advances stable/oldest, forces eviction, and similarly verifies all keys remain not found.

State and persistence behavior: globally visible user deletes/truncates in ingest must continue to protect visibility until checkpoint machinery has made them durable in the stable component.

Dependencies/integration points: integrates user tombstones, follower stable timestamps, eviction, and checkpoint pickup state. Risks include cursor reuse after eviction and timestamp counter assumptions. Test signals are WT_NOTFOUND during eviction and under timestamped verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower12.py

Purpose: verifies timestamps on follower ingest-table records are not cleared merely because they become globally visible.

Important APIs/types/functions: uses follower role config, precise checkpoint settings, timestamped insert at ts=10, `conn.set_timestamp(stable=20,oldest=20)`, debug eviction session, and role step-up through `conn.reconfigure('disaggregated=(role="leader")')`.

Control flow: the follower creates a layered table, writes key `'a'` at timestamp 10, advances stable/oldest past it, evicts the page through a debug eviction cursor, steps up to leader, and reads key `'a'`.

State and persistence behavior: even though the record is globally visible and evicted, its timestamp metadata must remain valid enough for step-up/drain semantics; clearing it would risk losing or mis-ordering the ingest content.

Dependencies/integration points: integrates ingest eviction, global visibility, timestamp preservation, and follower-to-leader role transition. Risks are narrow coverage with a single key. Test signal is successful read of `'b'` after step-up.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower13.py

Purpose: verifies ingest garbage collection removes associated on-disk values when keys are pruned during eviction.

Important APIs/types/functions: uses direct ingest URI `file:test_layered_follower13.wt_ingest`, `stat.dsrc.rec_ingest_garbage_collection_keys_update_chain`, debug eviction sessions, direct ingest cursor checks, and disaggregated checkpoint advancement.

Control flow: each test creates matching leader/follower layered tables, mirrors an insert at ts=10 to the follower, evicts it to create an on-disk ingest image, applies another operation, checkpoints/advances, evicts again, and checks the ingest btree. The scenarios are: update at ts=20, delete at ts=20, and a no-timestamp/global-visible tombstone placed directly in the ingest btree while the original insert is not prunable.

State and persistence behavior: GC must clear both update chains and any on-disk value image, often by writing a tombstone, so direct ingest searches no longer find the key. The statistic should report one garbage-collected update-chain key.

Dependencies/integration points: integrates eviction reconciliation, direct ingest btree operations, checkpoint pickup, no-timestamp deletes, and per-dsrc stats. Risks include stat counter exactness and direct file URI coupling. Test signals are WT_NOTFOUND in ingest and stat value `1`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower14.py

Purpose: regression coverage for WT-16974, WT-16703, and WT-16798: sweep must not close layered or ingest dhandles on followers or during step-up when that would discard in-memory ingest/truncate state.

Important APIs/types/functions: `test_layered_follower14` derives from `sweep_util`, uses aggressive `file_manager` close settings, `verbose=(sweep:3)`, `wait_for_sweep`, `session.truncate`, role reconfigure to leader, direct ingest cursor pinning, and `wiredtiger.WT_NOTFOUND`.

Control flow: `test_layered_dhandle_not_swept_during_stepup` writes 1000 follower rows, pins the ingest file dhandle, waits several sweep cycles, steps up, and scans to ensure all rows remain. `test_layered_dhandle_not_swept_with_truncate_state` writes rows, commits a follower truncate 100-700 to create truncate-list state, waits for sweep, and scans to ensure only rows outside the range remain.

State and persistence behavior: in-memory ingest data and truncate-list entries attached to dhandles must survive sweep eligibility windows. Closing the wrong handle would create gaps or resurrect deleted ranges.

Dependencies/integration points: integrates sweep server timing, dhandle cache policy, follower role, step-up drain, and follower truncate visibility. Risks are timing (`timeout=120`) and verbose output coupling. Test signals are final scan counts and WT_NOTFOUND scan termination.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower14.py -->
