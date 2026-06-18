# Research: subset-b-009076 WiredTiger cursor tests

Grouped research report for the requested WiredTiger cursor test subset. Each source-file section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor22.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor22.py

### Purpose
`test_cursor22.py` is a focused Python suite for `WT_CURSOR.get_raw_key_value()` on a simple row-store table with `key_format=S,value_format=S`. It establishes that raw key/value retrieval returns the same logical data as `get_key()` and `get_value()`, and that callers may ignore either or both tuple elements without side effects.

### Important APIs, Types, and Functions
The test class `test_cursor22` derives from `wttest.WiredTigerTestCase`. It uses `session.create`, `session.open_cursor`, explicit `begin_transaction`/`commit_transaction`, `cursor.set_key`, `cursor.set_value`, `cursor.insert`, `cursor.reset`, `cursor.next`, `cursor.get_key`, `cursor.get_value`, `cursor.get_raw_key_value`, and `cursor.close`. Helper methods `check_get_key_and_value` and `check_get_raw_key_value` centralize expected key/value assertions.

### Control Flow and State
The test creates `table:test_cursor22`, inserts keys `key1` through `key9` with values `value101` through `value109` inside one transaction, then scans the table twice in separate transactions. The first scan validates the standard cursor accessors; the second validates `get_raw_key_value`. A final transaction positions at the first row and exercises tuple unpacking patterns: keeping only the key, discarding the returned tuple entirely, and keeping only the value.

### Persistence and Integration
State is persisted through normal WiredTiger table inserts and transaction commits. The test integrates with the Python SWIG cursor binding and depends on cursor positioning from `next()`. It is intentionally independent of datasets or scenario expansion, making it a narrow regression signal for the raw accessor binding.

### Risks and Test Signals
The main risk covered is divergence between raw and decoded key/value accessors for simple string schemas, especially tuple lifetime or SWIG ownership issues when elements are ignored. Passing signals that positioned cursors return stable raw tuples and that repeated raw accesses do not invalidate cursor state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor22.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor23.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor23.py

### Purpose
`test_cursor23.py` extends raw key/value cursor coverage to dataset-created file and table objects. Its active scenarios exercise simple string key/value formats; the conditional complex-schema path documents the expected unsupported behavior for raw key/value access on complex values.

### Important APIs, Types, and Functions
`test_cursor23` derives from `wttest.WiredTigerTestCase` and uses `SimpleDataSet`, `make_scenarios`, `wiredtiger.WiredTigerError`, `assertRaisesWithMessage`, `cursor.get_raw_key_value`, `cursor.get_key`, and `cursor.get_value`. Scenario fields include `type`, `keyfmt`, `valfmt`, `dataset`, and `complex`.

### Control Flow and State
For each active scenario (`file:` and `table:` with `S/S` formats), the test creates a `SimpleDataSet` with 100 records and opens a cursor. It performs one transaction scanning the first nine rows with `get_key`/`get_value`, then another scanning the same range with `get_raw_key_value`. Expected keys are zero-padded strings such as `000000000000001`, and values follow the `SimpleDataSet` string pattern. The unused `complex=True` branch would validate that complex schema values decode through normal accessors but reject raw key/value access with an operation-not-supported error.

### Persistence and Integration
The dataset helper owns population and naming. The test is integrated with WiredTiger scenario expansion and validates both file and table object cursors through the same accessor path. Transactions are read-only around scans, so persistent state comes from the populated dataset.

### Risks and Test Signals
The test guards against raw accessor regressions for dataset-generated records and against accidental support claims for complex schema tuples. A passing simple scenario confirms that raw tuple retrieval remains compatible with file and table cursors using simple packed formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor23.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor24.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor24.py

### Purpose
`test_cursor24.py` validates version cursor metadata for prepared transactions, especially prepare timestamp fields and rollback visibility. It covers committed prepared inserts, committed prepared tombstones, rolled-back prepared inserts, later committed updates after rollback, and non-prepared update chains.

### Important APIs, Types, and Functions
The class `test_cursor24` derives from `wttest.WiredTigerTestCase` and uses `make_scenarios` for row-store integer keys and variable-length column-store record-number keys. It uses `session.open_cursor(..., "debug=(dump_version=(enabled=true...))")` to open version cursors, `prepare_transaction`, `commit_transaction` with commit and durable timestamps, `rollback_transaction`, `release_evict`, and `wiredtiger.WT_NOTFOUND`. Helper methods map the version cursor value tuple: start transaction/timestamps, stop transaction/timestamps, prepare timestamps, update type, prepare state, flags, location, and value.

### Control Flow and State
Each test creates `file:test_cursor24.wt` with scenario key/value formats. `test_prepare_commit_metadata` writes a prepared insert and checks start commit/durable timestamps plus `start_prepare_ts`. `test_prepare_commit_tombstone_metadata` writes a committed value, evicts it to disk, deletes it in a prepared transaction, and verifies stop commit/durable/prepare metadata on the older value. Rollback tests assert that a rolled-back prepare with no committed base yields `WT_NOTFOUND`, and that a subsequent committed insert becomes the only visible version. The non-prepared test verifies prepare fields remain zero or max sentinel values as appropriate.

### Persistence and Integration
The suite uses WiredTiger timestamped transactions, eviction, and the internal debug version cursor, so it directly exercises storage-engine update chain interpretation. `WT_TS_MAX` is used as the expected open-ended timestamp sentinel.

### Risks and Test Signals
Risks include incorrect prepare timestamp propagation, rollback tombstones leaking as versions, and on-disk update chains losing stop metadata. Passing signals that version cursor output is consistent for both row and variable column stores across in-memory and evicted states.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor24.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor25.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor25.py

### Purpose
`test_cursor25.py` tests `debug=(dump_version=(show_prepared_rollback=true))` behavior for in-memory B-trees. It verifies when rolled-back prepared values should be emitted by the version cursor and when tombstone-only rollback artifacts should remain hidden.

### Important APIs, Types, and Functions
The test uses `WiredTigerTestCase`, `make_scenarios` for row and variable column stores, `wiredtiger.WT_NOTFOUND`, and version cursor debug configuration flags `enabled`, `visible_only`, and `show_prepared_rollback`. Constants model special transaction states: `WT_TXN_ABORTED`, `WT_TS_MAX`, `PREPARE_TS`, and `ROLLBACK_TS`. Helpers include `create`, `open_version_cursor`, `prepared_insert_rollback`, `verify_value`, and `verify_prepare_rollback_value`.

### Control Flow and State
The file creates in-memory, non-logged tables so rolled-back prepared updates remain inspectable. Tests cover: rolled-back prepared insert with no later write; rolled-back insert followed by committed insert; rolled-back overwrite over a committed value; rolled-back prepared delete; rolled-back insert followed by multiple committed updates; insert-then-delete within the same prepared transaction; and explicit `visible_only=false` with `show_prepared_rollback=true`. The final test opens a non-in-memory object and expects an error because the feature is in-memory-only.

### Persistence and Integration
State is transactionally timestamped but configured `in_memory=true,log=(enabled=false)`. The tests integrate with the debug version cursor and validate update-chain metadata including aborted transaction markers and rollback timestamps stored in the durable timestamp field.

### Risks and Test Signals
The covered risks are over-reporting rollback tombstones, under-reporting rolled-back values, wrong ordering relative to committed versions, and allowing unsupported on-disk use. Passing confirms callers such as diagnostic or drain tooling can opt into seeing useful rolled-back prepared values without corrupting normal visible-only behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor25.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor26.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor26.py

### Purpose
`test_cursor26.py` is a regression test for WT-17240. It verifies that a version cursor configured like a disaggregated drain emits both a rolled-back prepared value and the underlying committed value when the prepared update had been reconciled to disk before rollback.

### Important APIs, Types, and Functions
The class uses `conn_config` with `preserve_prepared=true`, `precise_checkpoint=true`, statistics, and a small cache. `open_version_cursor` uses `debug=(dump_version=(enabled=true,raw_key_value=true,visible_only=true,timestamp_order=true,cross_key=true,show_prepared_rollback=true))`. Helpers `commit_put`, `prepared_put_and_rollback`, `force_reconcile`, and `all_versions` wrap timestamped writes, prepared rollback, forced eviction via `debug=(release_evict_page=true)`, and version collection.

### Control Flow and State
The test creates an in-memory, non-logged integer table, commits key `1` at timestamp 10, prepares an update to value `20` at timestamp 20 with a prepared id, forces reconciliation while the prepared update is active, then rolls back at timestamp 30. It sets the stable timestamp to 30 for clean precise-checkpoint closure and collects all version cursor rows for key `1`. The expected order is rolled-back prepared row first (`start_txn == WT_TXN_ABORTED`, value 20), then surviving committed row (`start_ts == 10`, standard update type, value 10).

### Persistence and Integration
The test intentionally crosses in-memory update state with reconciliation behavior to catch a disk/image interaction. It integrates with internal version cursor options used by disaggregated drain-like consumers.

### Risks and Test Signals
The key risk is that aborted prepared history hides or drops the older committed value, preventing downstream history reconstruction. Passing confirms version cursor traversal preserves enough history after prepared rollback plus reconciliation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor26.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound01.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound01.py

### Purpose
`test_cursor_bound01.py` performs basic validation of the cursor bound API across files, tables, index cursors, and layered/disaggregated storage. It checks configuration parsing, clear behavior, unsupported cursor types, and compatibility restrictions.

### Important APIs, Types, and Functions
The class inherits from `wtbound.bound_base` and `helper_disagg.DisaggConfigMixin`. It uses `gen_disagg_storages`, `make_scenarios`, `cursor.bound`, `cursor.largest_key`, `cursor.reset`, `open_cursor(..., "next_random=true")`, and helper methods `gen_key`, `gen_val`, and `set_bounds`. Disaggregated scenarios use a leader configuration and skip tiered hooks.

### Control Flow and State
Each scenario creates a WiredTiger object with optional columns, column groups, or an index. The test asserts that calling `cursor.bound()` with no configuration fails, sets lower and upper bounds using either primary keys or index values, clears bounds, and then skips further edge cases for index cursors. Non-index cursors are checked for `largest_key` incompatibility, default `action=set` behavior when only `bound` is provided, invalid action strings, missing bound config, and substring config rejection. For row-store random cursors, bound setting is expected to be unsupported.

### Persistence and Integration
The test creates object metadata but does not require data population except key state on cursors. It integrates with `bound_base` helper generation and disaggregated page-log storage, giving early API coverage for storage backends that might use different cursor implementations.

### Risks and Test Signals
Risks include accepting invalid configs, failing to preserve key state while setting bounds, allowing largest-key or random-cursor combinations that the engine cannot support, and disaggregated/layered cursor inconsistencies. Passing signals baseline API invariants before deeper traversal tests run.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound01.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound02.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound02.py

### Purpose
`test_cursor_bound02.py` validates bound setting, ordering, inclusivity, key persistence, reset, and clear semantics across many key/value schemas and object types. It is a broad API-level correctness suite for lower/upper bound configuration.

### Important APIs, Types, and Functions
The class derives from `bound_base` and expands scenarios over `file:`, `table:`, column-group tables, key formats `S`, `r`, `i`, `u`, `SSS`, `iS`, and `iSru`, value formats `S` and `SS`, plus inclusive/exclusive configurations. It relies on `set_bounds`, `gen_create_param`, `gen_key`, `gen_val`, `cursor.bound`, `cursor.reset`, `cursor.insert`, and `assertRaisesWithMessage`.

### Control Flow and State
`test_bound_api` creates an object, optionally creates column groups, and opens a cursor. It sets a lower bound then an upper bound, checks that inverted upper/lower assignments fail, then verifies valid bound changes in both directions. It checks that a missing key causes bound setting to fail and that the cursor key remains usable for `insert` after setting lower or upper bounds. Equal lower/upper bounds are allowed only when both sides are inclusive; attempts to mix exclusivity at an equal key fail. `test_bound_api_reset` verifies `cursor.reset()` clears bounds enough to allow previously invalid bound changes. `test_bound_api_clear` checks repeated `action=clear` and clearing one or both bounds before setting new ranges.

### Persistence and Integration
Inserted records at keys 30 and 90 prove bound calls do not consume or clear the cursor key/value. Column groups exercise bound propagation to underlying column group cursors.

### Risks and Test Signals
The test guards against stale bounds surviving reset/clear, invalid range acceptance, equal-bound inclusivity bugs, and composite-format packing mistakes. Passing confirms the bound API can be reused safely across schema shapes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound02.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound03.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound03.py

### Purpose
`test_cursor_bound03.py` verifies `next()` and `prev()` traversal with cursor bounds. It exercises lower-only, upper-only, both-bound, out-of-data-range, empty-range, changed-bound, and cleared-bound cases across object and schema scenarios.

### Important APIs, Types, and Functions
The test inherits from `bound_base` and uses scenario dimensions for object type, key format, value format, evict/no-evict, inclusive combinations, and direction. It depends heavily on `create_session_and_cursor`, `set_bounds`, `cursor_traversal_bound`, `cursor.bound("action=clear")`, and `cursor.reset`.

### Control Flow and State
The helper creates and populates the table with keys 20 through 79, optionally evicting pages. The test sets an upper bound at 50 and traverses, clears it, then sets a lower bound at 45 and traverses. It repeats with both bounds, with bounds beyond the stored data range, and with a range containing no data. It verifies clearing bounds restores full traversal. Later cases mutate upper and lower bounds from one value to another, both within range and across out-of-range values, and validate traversal count/key constraints after each change.

### Persistence and Integration
State is persistent table data inserted by `bound_base`; eviction scenarios force both in-memory and on-disk cursor paths. The same assertions cover row, column, byte-array, and composite key encodings.

### Risks and Test Signals
The suite catches off-by-one inclusivity errors, early exit mistakes at bounds, failure to reconfigure active bounds, and differences between forward and reverse traversal. Passing gives strong signal that bounded cursor traversal respects configured ranges after repeated clear/change cycles.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound03.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound04.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound04.py

### Purpose
`test_cursor_bound04.py` covers special bounded traversal scenarios, especially switching between `next()` and `prev()` and manipulating bounds on positioned cursors. It validates cursor behavior when bounds are cleared while positioned and when callers attempt to reset bounds after movement.

### Important APIs, Types, and Functions
The class uses `bound_base`, `make_scenarios`, `create_session_and_cursor`, `set_bounds`, `cursor.next`, `cursor.prev`, `cursor.get_key`, `cursor.set_key`, `cursor.bound`, `cursor_traversal_bound`, and `assertRaisesWithMessage`.

### Control Flow and State
`test_bound_special_scenario` sets lower or upper bounds, advances the cursor, and verifies first returned keys. It then tries to set new bounds with a positioned cursor and explicitly set keys, expecting invalid-argument errors. It also checks inclusive bound changes on positioned cursors, clearing bounds on positioned cursors, and continuing traversal outside the old range after clearing. `test_bound_combination_scenario` validates alternating `next`/`prev`: walking forward from a lower bound then stepping backward to the bound, walking backward from an upper bound then stepping forward, traversing an entire bounded range then reversing direction, and clearing bounds before traversing in the opposite direction.

### Persistence and Integration
The test relies on populated keys from `bound_base`, with optional eviction. It applies the same operations to file, table, and column-group scenarios with simple and composite keys.

### Risks and Test Signals
The major risks are stale cursor position interacting incorrectly with new bounds, direction-change logic crossing bounds, and clear operations leaving internal low/high cursors partially constrained. Passing indicates bounded cursors remain coherent across bidirectional movement.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound04.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound05.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound05.py

### Purpose
`test_cursor_bound05.py` exercises prefix-like string bounds where the configured bound keys are shorter than actual stored keys. It validates that internal cursor searches position correctly when all stored keys share longer string forms.

### Important APIs, Types, and Functions
The test derives from `bound_base`, uses fixed `key_format=S,value_format=S`, overrides `start_key=1000` and `end_key=1999`, and runs file/table scenarios with eviction and no-eviction. It uses `set_bounds`, `cursor_traversal_bound`, and `cursor.bound("action=clear")`.

### Control Flow and State
The helper populates string keys `"1000"` through `"1999"`. The test sets a lower bound `"10"` and expects all matching keys to be traversable in both directions. It sets upper bound `"20"` exclusive and expects 1000 entries below it. It combines lower `"10"` inclusive and upper `"20"` exclusive, then narrows to lower `"10"` and upper `"11"` exclusive, expecting 100 entries. It then verifies lower bounds above the data range return no rows and upper bounds above the data range return all rows.

### Persistence and Integration
The test works through normal B-tree data and optional eviction, so it covers both insert-list and reconciled page search paths. It focuses on string comparison semantics rather than helper-generated numeric range arithmetic.

### Risks and Test Signals
Risks include prefix bounds being treated as exact keys, incorrect lexicographic endpoint handling, and early exit failures when the search key is not physically present. Passing confirms bounded traversal handles prefix-style string ranges predictably.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound05.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound06.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound06.py

### Purpose
`test_cursor_bound06.py` validates `cursor.search()` with bounds. It checks unbounded searches, searches outside lower or upper bounds, searches inside both bounds, and searches exactly on inclusive/exclusive boundary keys.

### Important APIs, Types, and Functions
The class inherits from `bound_base`, expands scenarios over file/table/column-group objects, many key formats, value formats, inclusive/exclusive settings, and eviction. It uses `create_session_and_cursor`, `set_bounds`, `cursor.set_key`, `cursor.search`, `cursor.reset`, `wiredtiger.WT_NOTFOUND`, and `cursor.close`.

### Control Flow and State
After population, the test first searches for a non-existent key without bounds and expects `WT_NOTFOUND`, then searches for existing key 50 and expects success. It sets a lower bound at 30 and searches key 20, then an upper bound at 40 and searches key 60; both must return not found. With lower 20 and upper 40, searching key 35 succeeds. It checks keys adjacent to bounds and exact bound equality. For exact bound searches, success depends on the `inclusive` scenario flag; exclusive boundaries must return `WT_NOTFOUND`.

### Persistence and Integration
Data is the standard `bound_base` key range, optionally evicted. The test integrates boundary comparison logic with search rather than traversal, covering row, record-number, byte-array, and composite-key encodings.

### Risks and Test Signals
The test catches search paths that ignore bounds, mishandle equality at exclusive endpoints, or compare packed composite/byte keys incorrectly. Passing confirms `search()` applies bound filters before reporting an exact match.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound06.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound07.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound07.py

### Purpose
`test_cursor_bound07.py` targets column-store bounded traversal, especially deleted record ranges, run-length encoded values, and insert-list records. It verifies bounds across visible ranges separated by deleted records.

### Important APIs, Types, and Functions
The class extends `bound_base` but overrides `create_session_and_cursor`. It uses fixed `key_format='r'`, file/table scenarios, direction scenarios, RLE toggles for live and deleted records, and eviction toggles. APIs include transactional inserts/removes, `cursor.remove`, `debug=(release_evict)`, `set_bounds`, and `cursor_traversal_bound`.

### Control Flow and State
The custom setup inserts records 10-29 and 70-99, then inserts and removes records 30-69 to create a deleted middle range. Values can be identical for RLE or unique per record. The test traverses upper-bound, lower-bound, both-bound, and deleted-range cases. It then inserts records 50-59 into the deleted range and rechecks traversal counts around key 55. Finally it adds records 101 and 102 to test inclusive/exclusive behavior between RLE and normal records beyond the initial range.

### Persistence and Integration
Column-store record-number state includes committed deletes and optional page eviction. The test exercises interactions among column-store visibility, deleted slots, insert lists, and bounded next/prev.

### Risks and Test Signals
Risks include counting deleted records as visible, skipping valid records after deleted ranges, RLE-specific boundary mistakes, and direction differences. Passing confirms bounded cursor traversal handles sparse column stores and deleted intervals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound07.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound08.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound08.py

### Purpose
`test_cursor_bound08.py` verifies connection statistics for bounded cursor operations and checks that bounds reduce search-near traversal work under timestamp visibility constraints.

### Important APIs, Types, and Functions
The class uses `conn_config='statistics=(all)'`, `wiredtiger.stat`, and `bound_base`. It reads statistics via `session.open_cursor('statistics:')`. It checks stats such as `cursor_bounds_next_early_exit`, `cursor_bounds_prev_early_exit`, `cursor_bounds_next_unpositioned`, `cursor_bounds_prev_unpositioned`, `cursor_bounds_reset`, `cursor_bounds_search_early_exit`, `cursor_bounds_search_near_repositioned_cursor`, `cursor_next_skip_total`, and `cursor_prev_skip_total`.

### Control Flow and State
`test_bound_basic_stat_scenario` runs bounded forward and reverse traversals, reset, out-of-bound searches, and search-near repositioning, asserting exact stat increments after each operation. `test_bound_perf_stat_scenario` populates 1000 keys at commit timestamps 100 and 200, starts reads at timestamp 50 so no records are visible, and compares skip counts for unbounded search-near versus bounded search-near with upper, lower, and both bounds. Bounds should materially reduce skip work.

### Persistence and Integration
The performance portion uses timestamped persistent data and optional eviction to cover history/visibility paths. The stats portion integrates public Python tests with internal connection-level diagnostic counters.

### Risks and Test Signals
Risks include missing stat increments, over-counting across reset/clear, and performance regressions where bounds fail to limit invisible-record scans. Passing confirms both user-visible behavior and diagnostic counters align.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound08.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound09.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound09.py

### Purpose
`test_cursor_bound09.py` validates bounded cursor behavior in the presence of prepared updates. It checks `search`, `search_near`, `next`, and `prev` with and without `ignore_prepare=true`, including prepared keys at boundaries and out-of-bound search-near inputs.

### Important APIs, Types, and Functions
The class uses `bound_base`, `make_scenarios`, `wiredtiger_strerror`, `WT_PREPARE_CONFLICT`, `WiredTigerError`, and `wiredtiger.WT_NOTFOUND`. It expands over object type, key format, inclusive/eviction settings, and ignore-prepare mode. It uses separate sessions, prepared transactions, `set_bounds`, cursor operations, and explicit rollback of prepared transactions.

### Control Flow and State
The test populates the standard key range, then prepares updates on keys 30-35. A second session opens a bounded cursor over 20-40 and runs search-like operations on key 30. Without `ignore_prepare`, prepare conflicts are accepted; with `ignore_prepare`, operations must return valid results subject to exclusivity. It repeats with a bound exactly on prepared key 30 and validates `prev` behavior. It then rolls back, prepares keys 29-30, and tests `search_near` from key 20 with lower bound 30. Final logic checks non-inclusive bounds where `next()` may hit a prepare conflict and leave the cursor key at the prepared boundary.

### Persistence and Integration
Prepared updates are held open across sessions and then rolled back. This directly exercises WiredTiger conflict handling in bounded traversal and search paths.

### Risks and Test Signals
The suite catches bugs where bounds hide prepare conflicts, return unprepared keys out of order, or corrupt cursor key state after conflicts. Passing confirms bounded operations honor prepare isolation and `ignore_prepare`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound09.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound10.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound10.py

### Purpose
`test_cursor_bound10.py` validates bounded `next`/`prev` traversal with timestamp visibility and history-store-like version visibility. It checks that bounds and read timestamps combine to produce expected visible counts.

### Important APIs, Types, and Functions
The class inherits from `bound_base`, overrides population, and expands over file/table/column-group objects, record-number and integer/composite key formats, eviction, and direction. It uses timestamped `commit_transaction`, `begin_transaction(read_timestamp=...)`, `set_bounds`, and `cursor_traversal_bound`.

### Control Flow and State
Setup inserts keys 1-100 at timestamp 50, keys 101-600 at timestamp 200, and keys 601-1000 at timestamp 100, optionally evicting the range. The test applies upper bound 900 and reads at timestamps 10, 75, 150, and 250, expecting 0, 100, 400, and 900 visible rows. It repeats lower bound 50 with expected counts 0, 51, 451, and 951. With both lower 50 and upper 900, counts are 0, 51, 351, and 851.

### Persistence and Integration
Timestamped commits and optional eviction force traversal through visibility checks and on-disk pages. The test integrates bounds with historical reads and record-number/composite-key generation.

### Risks and Test Signals
Risks include bounds being applied before/after visibility in a way that changes counts, incorrect history-store traversal under eviction, and direction asymmetry. Passing confirms bounded traversal filters visible versions correctly across timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound10.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound11.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound11.py

### Purpose
`test_cursor_bound11.py` tests prefix search scenarios migrated to bounded cursor logic. It focuses on performance/skip behavior and row-search guarantees when prefix ranges contain invisible, deleted, or prepared updates.

### Important APIs, Types, and Functions
The class derives directly from `wttest.WiredTigerTestCase`, enables statistics, and uses `wtbound.set_prefix_bound`. Helpers include `get_stat` for statistics cursors and `unique_insert`, which models unique-index insertion by inserting a prefix key, removing it, searching near it, then inserting a full `(prefix,id)`-style key.

### Control Flow and State
`test_base_scenario` inserts all keys `aaa` through `zzz`, starts an older reader, evicts pages, and compares unbounded `search_near('aa')` skip counts with prefix-bounded searches for `aa` and `bb`. `test_unique_index_case` simulates unique-index insertion patterns for prefixes `aa` through `zz`, skipping `cc`, and verifies prefix bounds limit search work and early-exit stats. `test_row_search` verifies assumptions around invisible inserted keys and removed adjacent keys. `test_prepared` combines an older reader, a visible committed `cc`, prepared updates for most prefixes, eviction, prefix-bounded search-near, and `ignore_prepare=true`.

### Persistence and Integration
The tests rely on committed data, older read transactions, prepared transactions, eviction, and connection statistics. They integrate prefix-bound construction with search-near optimization counters.

### Risks and Test Signals
Risks include prefix-bounded search-near traversing entire keyspaces, cursor-cache flags surviving cursor reopen, row-search skip-count assumptions breaking, and prepared invisible data defeating early exit. Passing confirms prefix bounds can optimize search without losing correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound11.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound12.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound12.py

### Purpose
`test_cursor_bound12.py` checks `search_near` return keys under visibility rules and prefix bounds. It compares unbounded nearest-key behavior with bounded prefix behavior at different read timestamps.

### Important APIs, Types, and Functions
The test uses `wttest.WiredTigerTestCase`, `make_scenarios`, and `set_prefix_bound`. Key formats include fixed string `10s`, variable string `S`, and byte array `u`; eviction is optional. `check_key` normalizes expected keys for byte and fixed-length string formats.

### Control Flow and State
The test inserts `aaa` through `aay` at timestamp 200, `aaz` at timestamp 50, and `aazab` at timestamp 250, optionally evicting all keys. At read timestamp 100, only `aaz` is visible; unbounded searches from nearby prefixes return it, while prefix bounds for `az` or `b` return `WT_NOTFOUND`. At timestamp 25 no keys are visible. At timestamp 250 all keys are visible; unbounded and prefix-bounded searches return the nearest matching key for prefixes such as `a`, `aa`, `aaz`, and `aaza`, while prefix `az` has no match.

### Persistence and Integration
Timestamped commits and optional eviction test search-near visibility on both in-memory and reconciled pages. Prefix bounds are implemented by setting inclusive lower and exclusive synthetic upper bounds.

### Risks and Test Signals
The suite catches cases where `search_near` returns a key outside bounds, ignores visibility, or misreports direction/exactness around prefixes. Passing confirms prefix-bounded search-near respects both timestamps and key format normalization.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound12.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound13.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound13.py

### Purpose
`test_cursor_bound13.py` validates prefix-bounded `search_near` when matching keys span multiple pages. It protects against early exit before reaching a visible key on another page.

### Important APIs, Types, and Functions
The class uses `WiredTigerTestCase`, `make_scenarios`, and `set_prefix_bound`. It runs variable string and byte-array key formats. The test uses large repeated string keys (`key_size=200`) and `debug=(release_evict=true)` to force multi-page/on-disk behavior.

### Control Flow and State
The test inserts large keys based on `aaa` through `aay` at timestamp 200 and `aaz` at timestamp 50, then evicts them. At read timestamp 100, only the large `aaz` key is visible. Unbounded `search_near` from several locations returns that key. Prefix-bound cases for `a`, `aa`, `aaz`, and the full repeated key must also find the visible `aaz` key, even though traversal may cross page boundaries.

### Persistence and Integration
Timestamped visibility plus forced eviction creates a page layout where prefix-bound search optimization must cooperate with row-search traversal. Byte-array scenarios ensure binary key comparisons follow the same logic.

### Risks and Test Signals
The regression risk is that bounded search-near exits at a page boundary or synthetic upper bound before seeing the only visible key. Passing confirms multi-page prefix searches remain correct after migration to cursor-bound logic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound13.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound14.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound14.py

### Purpose
`test_cursor_bound14.py` validates write operations on bounded cursors. It checks that inserts, updates, reserves, modifies, and removes respect lower and/or upper bounds, including boundary inclusivity.

### Important APIs, Types, and Functions
The class derives from `bound_base` and expands scenarios over object types, key/value formats, cursor overwrite config, lower/upper/both bound selection, and eviction flags. It uses `cursor.insert`, `cursor.update`, `cursor.reserve`, `cursor.modify` with `wiredtiger.Modify`, `cursor.remove`, `wiredtiger.WT_NOTFOUND`, and error assertions for item-not-found messages.

### Control Flow and State
The test populates via `create_session_and_cursor`, inserts out-of-range keys 10 and 95, then sets selected bounds around 45-50. It attempts inserts outside the lower and upper bounds, expecting errors only for the active bound side. It updates existing out-of-bound records, reserves them inside a transaction, modifies string values when supported, and removes them, checking `WT_NOTFOUND` or success according to active bounds. It finally updates keys exactly at lower and upper boundaries, with results controlled by inclusive flags.

### Persistence and Integration
The test mutates persistent table state and uses transactions for reserve/modify cases. Column groups and composite values exercise bound checks through complex cursor implementations.

### Risks and Test Signals
Risks include write paths bypassing bounds, inconsistent error codes between insert and update-like operations, modify support leaking into unsupported value formats, and boundary inclusivity failures. Passing confirms bounds constrain both read and write APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound14.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound15.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound15.py

### Purpose
`test_cursor_bound15.py` checks `search_near` exact/direction return values with explicit bounds and prefix bounds. It targets edge cases where the nearest visible key lies at, inside, or just outside the configured range.

### Important APIs, Types, and Functions
The class inherits from `bound_base`, uses `set_prefix_bound`, and runs string and byte-array formats with eviction/no-eviction. It uses timestamped inserts, `cursor.search_near`, `cursor.get_key`, `cursor.reset`, and `set_bounds`.

### Control Flow and State
The test inserts `aaa` through `aay` at timestamp 200 and `aaz` at timestamp 50, optionally evicts, then reads at timestamp 250. Lower-only cases search keys beyond the upper end and expect nearest previous/next results with exact values `-1`, `0`, or `1`. Upper-only and both-bound cases similarly validate returned key and direction. Prefix-bound cases use prefixes `aaz`, `aaa`, and `a`, including searches such as `aaza`, `ab`, `aac`, and `aa`, to ensure return values match the closest visible key within prefix-derived bounds.

### Persistence and Integration
Timestamped data and optional eviction exercise search-near logic over both update chains and disk pages. Byte-array normalization is handled by `check_key`.

### Risks and Test Signals
The risk is not just wrong key selection but wrong `search_near` sign, which callers use to know whether the returned key is before or after the search key. Passing confirms exactness semantics survive bound and prefix-bound repositioning.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound15.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound16.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound16.py

### Purpose
`test_cursor_bound16.py` validates cursor bounds on dump cursors. It covers dump output encodings and verifies bounded traversal, search-near, search, reset, and clear behavior against dump-formatted keys.

### Important APIs, Types, and Functions
The class derives from `bound_base` with `key_format=S,value_format=S`, file/table scenarios, and dump options `print` and `hex` (JSON disabled by a FIXME). It uses `session.open_cursor(uri, None, "dump=<mode>")`, custom `gen_dump_key`, `set_bounds`, `cursor_traversal_bound`, `cursor.search_near`, `cursor.search`, `cursor.reset`, and `cursor.bound("action=clear")`.

### Control Flow and State
Setup inserts string keys 20-79 and computes dump-format start/end keys. The test opens a dump cursor, sets lower bound 30 and upper bound 50 in dump-key representation, and traverses 21 rows forward and backward. It checks `search_near` for keys below, inside, and above the range, expecting repositioning to lower, exact, or upper keys. It checks exact `search` outside and inside the range. A `reset()` should clear bounds for full traversal, and `action=clear` should do the same after bounds are re-applied.

### Persistence and Integration
The persisted table is ordinary string data, but cursor output is dump-encoded. This integrates the bound API with dump cursor key translation layers.

### Risks and Test Signals
Risks include comparing raw table keys against dump-formatted bound keys incorrectly, reset/clear inconsistency for special cursor types, and dump mode-specific search-near errors. Passing confirms bounds work after dump encoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound16.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound17.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound17.py

### Purpose
`test_cursor_bound17.py` verifies that internal session-wide cursor resets do not accidentally clear user-configured bounds. It distinguishes ordinary `cursor.reset()` from resets triggered by checkpoint, transaction completion, reconfigure, and session reset.

### Important APIs, Types, and Functions
The class uses `bound_base`, broad schema scenarios, `set_bounds`, `cursor_traversal_bound`, `session.checkpoint`, `session.begin_transaction`, `session.rollback_transaction`, `session.commit_transaction`, `session.reconfigure("cache_cursors=false")`, `session.reset`, and `cursor.reset`.

### Control Flow and State
For each scenario, the test sets lower 30 and upper 60 and validates traversal in both directions. It then runs a checkpoint and validates the same bounds still apply. It repeats the pattern around a rolled-back transaction, a committed transaction, cursor-cache reconfiguration, and `session.reset()`. After each internal reset source, traversal must remain bounded until an explicit `cursor.reset()` is issued. At the end, after explicit reset, full unbounded traversal is expected.

### Persistence and Integration
The test uses standard populated data from `bound_base`, optionally evicted. It integrates cursor-bound state with broader session lifecycle APIs that internally reset cursor positions.

### Risks and Test Signals
Risks include losing bound state during checkpoint/transaction cleanup, incorrectly clearing bounds during cursor-cache changes, or retaining bounds after explicit cursor reset. Passing confirms bound state lifetime matches API intent.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound17.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound18.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound18.py

### Purpose
`test_cursor_bound18.py` checks column-group bound rollback semantics. When setting a bound on one underlying column group fails, the original primary/table bounds must remain intact rather than leaving a partially updated state.

### Important APIs, Types, and Functions
The class derives from `bound_base`, forces `use_colgroup=True` and `uri='table:'`, and expands over key/value formats, inclusivity/eviction configs, and direction. It uses `create_session_and_cursor`, `set_bounds`, `cursor_traversal_bound`, and `assertRaisesWithMessage`.

### Control Flow and State
The test creates a column-group-backed table and sets initial lower 40 and upper 90. Attempts to set an upper bound below the lower bound and a lower bound above the upper bound must fail. It then successfully sets lower 50 and upper 80 and validates traversal. A later failed upper-bound change to 40 should not destroy prior bound state; traversal from an explicitly set key validates the expected retained range. It successfully narrows upper to 70, then a failed lower change to 80 must leave the 50-70 range intact. Final successful setting of both bounds confirms the cursor remains usable.

### Persistence and Integration
The important integration point is propagation from a table cursor to its column-group cursors. Persistent data comes from `bound_base`.

### Risks and Test Signals
The risk is partial state corruption when multi-cursor bound propagation fails. Passing confirms failures are atomic from the caller’s perspective and previous bounds remain valid.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound18.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound19.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound19.py

### Purpose
`test_cursor_bound19.py` tests bounds on index cursors, including duplicate index values. It verifies traversal counts, search-near positioning, exact search, reset, clear, and exclusive lower-bound behavior for secondary indexes.

### Important APIs, Types, and Functions
The class derives from `bound_base`, sets `use_index=True`, and runs table/column-group scenarios with many key and value formats. It creates an index URI `index:<file_name>:i0` over all value columns, opens an index cursor, and uses `set_bounds`, `cursor_traversal_bound`, `search_near`, `search`, and `reset`.

### Control Flow and State
`create_session_and_cursor` first populates the primary table with duplicate values for index testing, then the test creates the index. It sets lower 30 and upper 40; because duplicate values are generated up to the range, traversal expects 22 entries. Search-near below, inside, and above the range should return 30, 35, and 40 respectively; exact search outside the range should be not found. After `reset`, full traversal expects 60 index entries. After `action=clear`, full traversal is rechecked. The exclusive lower-bound case excludes duplicates at 30, yielding 20 entries and moving a below-range search-near to 31.

### Persistence and Integration
The test integrates cursor bounds with secondary index key/value encoding and duplicate index entries. Column-group table scenarios exercise index creation over table layouts with column groups.

### Risks and Test Signals
Risks include applying bounds to primary keys instead of index keys, duplicate handling off-by-one errors, reset/clear not restoring full index traversal, and exclusive lower bounds failing to skip duplicates. Passing confirms index cursor bounds are value-key-aware.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound19.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound20.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound20.py

### Purpose
`test_cursor_bound20.py` targets edge cases in index bound upper-key increment logic when index keys contain maximum byte/string values. It ensures max values do not accidentally disable upper bounds or overflow comparisons.

### Important APIs, Types, and Functions
The test derives from `bound_base`, uses table URIs with string primary keys, overrides `set_bounds` to accept raw index keys directly, and defines `gen_uval` plus `gen_index_table`. It tests fixed-length string value format `4s` and byte-array value format `u`, opens `index:<file_name>:i0`, and uses traversal, `search_near`, and `search`.

### Control Flow and State
`test_cursor_index_bounds_fixed` inserts rows whose indexed fixed-string value is four maximum ASCII characters, creates an index, bounds from `"0000"` to the max fixed string, and validates full traversal and exact search-near/search on the max key. It then sets an exclusive lower bound at the max key and expects empty traversal and not-found search results. `test_cursor_index_bounds_byte` repeats the pattern with a two-byte `0xff,0xff` maximum byte-array index key and generated byte values.

### Persistence and Integration
The test persists table rows, creates a secondary index, and then interacts only through index cursors. It directly exercises low-level packed-key increment behavior for upper-bound synthesis.

### Risks and Test Signals
Risks include overflow when incrementing maximum keys, treating exclusive max lower bounds as inclusive, and losing upper-bound enforcement for all-maximum byte arrays. Passing confirms index bounds handle terminal key values safely.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound20.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound21.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound21.py

### Purpose
`test_cursor_bound21.py` validates prepare-conflict correctness when a bounded cursor positions for `next()` and `prev()`. It covers inclusive and non-inclusive bounds and cases where the prepared key is missing from the committed key set.

### Important APIs, Types, and Functions
The class derives from `bound_base` and runs key formats `S`, `r`, `i`, and `u`. It uses separate sessions/cursors, prepared transactions, `cursor.bound`, `cursor.next`, `cursor.prev`, `wiredtiger_strerror`, `WT_PREPARE_CONFLICT`, `WiredTigerError`, and commit with durable timestamps.

### Control Flow and State
`test_cursor_bound_bug` prepares key 1, sets a lower bound at key 1 in another cursor, and calls `next()` three times, expecting only prepare conflicts. After commit, `next()` must return key 1. It repeats symmetrically with key 2 and an upper bound using `prev()`. `test_not_inclusive_bound` sets a lower exclusive bound matching prepared keys; when a committed key exists beyond the bound, next can skip the bound key, but a later prepared range should still conflict before commit and return key 4 after commit. `test_missing_bound_key_prepare` inserts committed keys 1, 5, and 10, prepares missing key 4, sets lower bound 2, expects repeated prepare conflicts, then after commit expects key 4.

### Persistence and Integration
Prepared state persists across sessions until commit. Byte-array key scenarios normalize expected keys through decoding.

### Risks and Test Signals
The covered risk is a bounded positioning loop returning not-found, a wrong key, or stale cursor state instead of a prepare conflict. Passing confirms conflict detection remains stable across repeated calls and after commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound21.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound_fuzz.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound_fuzz.py

### Purpose
`test_cursor_bound_fuzz.py` is a randomized correctness fuzzer for cursor bounds. It generates random bounds, random updates/removes/truncates, optional prepared transactions, and random cursor operations, then validates WiredTiger cursor results against an in-memory model.

### Important APIs, Types, and Functions
The file defines enums `operations`, `key_states`, `bound_scenarios`, and `bound_type`, plus a `key` model class. The test uses `wtbound.bound` and `wtbound.bounds`, `WiredTigerTestCase`, `make_scenarios`, random value generation, timestamped transactions, `session.truncate`, `cursor.next`, `prev`, `search`, `search_near`, `WT_NOTFOUND`, and `WT_PREPARE_CONFLICT`.

### Control Flow and State
The fuzzer initializes a key range of 1,000 keys in normal runs or 10,000 in long tests, pre-generates values, and mirrors every database operation into `self.key_range`. For each iteration it applies random lower/upper bounds, performs either batch updates/removes or a truncate, sometimes inside a prepared transaction, then starts a read transaction at the current timestamp and runs one random bound scenario. `run_next` and `run_prev` validate every visible key and every skipped deleted/out-of-bound key. `run_search` validates exact lookups, including prepare conflicts. `run_search_near` checks returned keys are visible, in-bounds, and closest according to deletion and bound state. Prepared conflicts are accepted only when the model contains a prepared key along the path/range.

### Persistence and Integration
The test uses file/table scenarios and row/column key formats. Timestamp commits, checkpoints every ten iterations, prepared commits, and optional truncates exercise multiple storage paths while keeping an authoritative in-memory model.

### Risks and Test Signals
Risks include rare combinations not covered by deterministic tests: deleted gaps, prepared conflicts after internal skips, search-near outside bounds, non-inclusive endpoints, and truncate side effects. The seed is printed for reproduction. Passing gives high confidence in global bounded cursor invariants under randomized mutation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_bound_fuzz.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_compare.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_compare.py

### Purpose
`test_cursor_compare.py` validates `WT_CURSOR.compare` and `WT_CURSOR.equals` behavior for file, table, and index cursors. It checks key ordering/equality, required key state, object identity restrictions, and platform-specific exception wrapping for null cursor arguments.

### Important APIs, Types, and Functions
The class `test_cursor_comparison` uses `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, `cursor.compare`, `cursor.equals`, `cursor.set_key`, `cursor.search`, index cursor opening via `ds.index_name`, and error assertions. It selects `TypeError` on Darwin and `RuntimeError` elsewhere for SWIG null-pointer behavior.

### Control Flow and State
For each file/table and integer/record-number/string key scenario, the test populates two separate objects. Table scenarios also open multiple index cursors: two on the same index, one on another index, and one on the other table. `test_cursor_comparison` first asserts compare fails when keys are unset, then compares unset-position cursors with only key fields assigned. It checks comparisons against different objects and null. It verifies same-index comparisons and rejects main-table-vs-index, unrelated index, and different-index comparisons. It repeats after positioning cursors with `search`. `test_cursor_equality` mirrors the same structure for boolean equality.

### Persistence and Integration
Dataset helpers create both simple file objects and complex indexed tables. The tests integrate Python bindings with cursor object identity and key comparison rules across primary and secondary cursors.

### Risks and Test Signals
Risks include comparing cursors from different objects, requiring physical positioning when a key is already set, index identity confusion, and inconsistent SWIG exception behavior. Passing confirms compare/equals semantics are stable for public cursor APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_compare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_pin.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_pin.py

### Purpose
`test_cursor_pin.py` smoke-tests fast-path searching on pinned pages before re-descending the tree. It validates repeated searches on nearby and distant pages for row and record-number stores, including sparse column-store-like gaps.

### Important APIs, Types, and Functions
The class uses `SimpleDataSet`, `make_scenarios`, `wiredtiger.WT_NOTFOUND`, `session.open_cursor`, `cursor.search`, `cursor.get_value`, and `reopen_conn`. Helper methods `forward` and `backward` iterate searches over a range and compare expected found/not-found outcomes.

### Control Flow and State
`test_smoke` creates a 10,000-entry multi-page file with small page sizes, reopens the connection, searches key 100, then 101 on the likely same/local page, then 9999 on a distant page. `test_basic` searches every key forward and backward after reopen. `test_missing` populates 10,000 entries, adds a later range 13,000-15,000, reopens, and verifies searches through the gap return `WT_NOTFOUND`. It then inserts part of the gap, 11,000-12,000, and verifies forward/backward searches reflect the new present and still-missing ranges.

### Persistence and Integration
Connection reopen forces persistent pages and removes purely in-memory positioning assumptions. Small allocation/page sizes create many pages, making page-pin reuse meaningful.

### Risks and Test Signals
Risks include pinned-page fast paths returning stale not-found/found results across page boundaries, mishandling nearby searches after a page-local hit, and sparse record-number lookup mistakes. Passing confirms page pin optimization preserves search correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_pin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_random.py -->
## sources/storage-engines/wiredtiger/test/suite/test_cursor_random.py

### Purpose
`test_cursor_random.py` validates `next_random` cursor behavior. It covers unsupported operations, empty and single-record trees, randomness over insert-list and disk-page records, deleted ranges, unsupported column stores, and invisible transactional updates.

### Important APIs, Types, and Functions
The file defines three test classes: `test_cursor_random`, `test_cursor_random_column`, and `test_cursor_random_invisible`. It uses `SimpleDataSet`, `ComplexDataSet`, `simple_key`, `simple_value`, `make_scenarios`, `session.open_cursor(..., "next_random=true...")`, optional `next_random_sample_size`, `cursor.next`, `cursor.reconfigure`, `cursor.reset`, unsupported-operation assertions, `truncate`, and `reopen_conn`.

### Control Flow and State
The main class runs file/table scenarios with sampled and unsampled random cursor configs. It verifies unsupported methods (`compare`, `insert`, `prev`, `remove`, `search`, `search_near`, `update`) fail while `next`, `reconfigure`, and `reset` are allowed. Empty trees repeatedly return not-found; single-record trees repeatedly return the same key. Multi-record helpers populate 2,000 or 10,000 records and assert 99 random reads yield more than 80 unique keys, both in insert-list state and after optional reopen to disk pages. Deleted-partial tests truncate most records but expect random next to find remaining ones; deleted-all expects not-found. Column-store class asserts opening next-random on `key_format=r` fails. Invisible tests use uncommitted updates in one session and random cursors in another to ensure only committed visible records can be returned.

### Persistence and Integration
The suite covers in-memory insert lists, reopened disk pages, truncation tombstones, and transaction isolation. macOS-specific eviction warnings are ignored after deliberate connection close.

### Risks and Test Signals
Risks include random cursor methods exposing unsupported operations, sampling bias/regression, returning deleted or uncommitted records, and allowing unsupported column-store random cursors. Passing confirms random selection respects visibility and API limits.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor_random.py -->
