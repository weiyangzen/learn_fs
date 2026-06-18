# Research Group subset-b-008974

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_dump.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_dump.c

## Purpose
`cur_dump.c` implements the wrapper cursor used when a WiredTiger cursor is opened with dump formatting. It does not own storage access itself; it sits in front of a child cursor and converts keys and values between raw WiredTiger binary formats and printable dump encodings. It supports normal escaped-hex dump output, hex-only output, pretty printable output, JSON dump output, and raw mode variants.

## Important APIs, Types, and Functions
The central type is `WT_CURSOR_DUMP`, whose public `WT_CURSOR` interface is initialized by `__wti_curdump_create`. The wrapper stores a `child` cursor and reuses the child URI, key format, and value format. `__raw_to_dump` and `__dump_to_raw` are the binary/string conversion helpers, selecting `__wt_raw_to_hex`, `__wt_raw_to_esc_hex`, `__wt_hex_to_raw`, or `__wt_esc_hex_to_raw` based on `WT_CURSTD_DUMP_HEX`.

`__curdump_get_key` and `__curdump_get_value` are the core read paths. They either unpack JSON using `__wt_json_alloc_unpack`, format record-number keys as decimal strings, pretty-print with `__wt_buf_set_printable_format`, or convert raw buffers to dump strings. `__curdump_set_keyv` and `__curdump_set_valuev` reverse the process for write operations, including JSON input conversion through `__wt_json_to_item` and record-number parsing through `str2recno`. `WT_CURDUMP_PASS` forwards `next`, `prev`, `reset`, `search`, `insert`, `update`, and `remove` directly to the child cursor; `bound` and `search_near` are small explicit pass-throughs.

## Control Flow
Cursor creation copies dump-related flags from the child (`WT_CURSTD_DUMP_HEX`, `WT_CURSTD_DUMP_JSON`, `WT_CURSTD_DUMP_PRETTY`, and `WT_CURSTD_DUMP_PRINT`), optionally allocates a shared `WT_JSON` object, and calls `__wt_cursor_init`. Reads call the child first, then translate into the public dump cursor buffers before returning either a `const char *` or `WT_ITEM *` depending on raw mode. Writes read application arguments, translate them into `cursor->key` or `cursor->value`, then call `child->set_key` or `child->set_value`.

Record-number stores get special handling: non-raw dump keys are decimal strings, while JSON keys are unpacked from the JSON item and decoded as packed unsigned integers. Errors in `set_keyv` and `set_valuev` are saved in `cursor->saved_err` and clear the corresponding key/value-set flags.

## State and Persistence Behavior
This file is a presentation layer. It does not persist data directly and does not change transaction semantics beyond invoking the child cursor. It owns transient conversion buffers in the public cursor and a JSON-private object when JSON mode is active. Closing a dump cursor closes the child cursor, clears `internal_uri` because the URI memory is shared with the child, closes JSON state, and frees the wrapper cursor.

## Dependencies and Integration Points
The implementation depends on standard cursor API macros, raw/escaped hex helpers, JSON helpers, format-aware printable-buffer helpers, and the child cursor's full operation table. It is created from the standard cursor open path when a file/table/index cursor is opened with dump configuration. Index and table cursor code intentionally disables nested dump behavior for their internal child cursors so only the top-level user cursor becomes a dump wrapper.

## Risks and Edge Cases
The main risks are format conversion mismatches and state flag drift between the wrapper and child. Record-number parsing rejects signs, prefixes, and trailing text, but it still relies on string input matching decimal recno expectations. Pretty-print mode ignores formatting failures with `WT_IGNORE_RET`, so it may fall back less visibly than hard conversion paths. JSON mode shares `json_private` between wrapper and child, making close ordering important. Because many operations are passed straight through, child cursor errors and positions are authoritative, while wrapper buffers only reflect the latest successful get/set path.

## Test Signals
Relevant coverage appears in dump and salvage usage, plus `test_cursor_bound16.py`, which exercises bounded cursor behavior on dump cursors. Broader smoke coverage comes from backup/verify/dump workflows and format failure-dump paths. Useful additional signals would include JSON dump round trips, record-number set/get failures, raw-mode `WT_ITEM` lifetime checks, and child-error propagation through forwarded operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_file.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_file.c

## Purpose
`cur_file.c` is the primary `WT_CURSOR_BTREE` implementation for file-backed WiredTiger objects. It adapts the public `WT_CURSOR` API to btree cursor primitives, handles checkpoint cursor transaction substitution, supports bulk load and random cursors, manages cursor caching/reopen, and enforces cursor state invariants around position, key, and value flags.

## Important APIs, Types, and Functions
The main exported entry points are `__wt_curfile_open`, `__wt_cursor_checkpoint_id`, and `__wt_curfile_insert_check`. `__curfile_create` installs the method table for btree cursors: compare, equals, next, prev, reset, search, search_near, insert, modify, update, remove, reserve, reconfigure, largest_key, bound, cache, reopen, checkpoint ID, and close. Most methods validate cursor state with helpers such as `__cursor_checkkey`, `__cursor_checkvalue`, and `__cursor_copy_release`, then dispatch to `__wt_btcur_*` operations.

The `WT_WITH_CHECKPOINT` macro is a key piece of this file. It temporarily substitutes a checkpoint dummy transaction into `session->txn`, disables reconciliation, sets the matching history-store checkpoint name, and swaps checkpoint write generation while performing a checkpoint cursor operation. `__curfile_setup_checkpoint` constructs that dummy transaction from `WT_CKPT_SNAPSHOT` metadata and records the history-store checkpoint dhandle and checkpoint ID.

## Control Flow
`__wt_curfile_open` parses `bulk`, `checkpoint_wait`, and `checkpoint_use_history`; obtains the btree/checkpoint dhandle via `__wt_session_get_btree_ckpt`; and passes any matching history-store handle and checkpoint snapshot metadata into `__curfile_create`. Bulk cursors require exclusive access, are disallowed inside transactions, and initialize `WT_CURSOR_BULK`. Random cursors replace the operation table with a limited `next_random`/`reset` surface and seed the btree cursor RNG.

Normal read operations enter the cursor API, check overload and transaction/checkpoint restrictions, optionally wrap btree access in `WT_WITH_CHECKPOINT`, and assert resulting key/value state. Write operations use update API wrappers, measure write latency histograms, and call btree insert/update/modify/remove/reserve. `remove` preserves the special API semantic that a positioned remove remains positioned and rolls back if that initial position is lost. `reserve` repeats a search after the reserve so callers can fetch a value.

Close first tries cursor-cache release, then frees bulk resources, closes the btree cursor, releases checkpoint transaction and history-store handles, frees cursor memory, decrements dhandle use, and releases the dhandle unless the cursor was reopened from a dead handle. Cache and reopen mirror normal file handle lifecycle and reset URI/format fields if the btree handle was reopened.

## State and Persistence Behavior
This file does not implement page storage itself; persistence is delegated to btree modify/search/truncate/reconciliation layers. It does, however, control persistent access mode through dhandle locking, bulk-load flags, checkpoint snapshot metadata, and transaction visibility setup. Checkpoint cursors read a stable historical view by pairing data-store checkpoint metadata with the correct history-store checkpoint and dummy transaction. Cursor state is tracked through `WT_CURSTD_*` flags and `WT_CBT_ACTIVE`; many assertions document which methods should leave the cursor positioned.

## Dependencies and Integration Points
`cur_file.c` integrates with session dhandle lookup/release, checkpoint metadata, transaction timestamp parsing, history-store checkpoint opening, btree cursor primitives, cursor cache infrastructure, bulk cursor support, statistics, random cursor support, and bound handling. It is the underlying child cursor for table, index, dump, history-store, and layered implementations whenever they need ordinary btree access.

## Risks and Edge Cases
Checkpoint cursor correctness is the highest-risk area because it relies on matching data-store checkpoints, history-store checkpoints, snapshot transaction arrays, stable/oldest timestamps, and write generations. Reopen/cache paths must not release dead handles incorrectly. Bulk open interacts with checkpoint locks and exclusive dhandle access. `remove` has subtle retry behavior when a prepared conflict or restart loses a starting position. `largest_key` temporarily changes `WT_CURSTD_KEY_ONLY` and resets the cursor twice; failures must restore state. Bound setting is rejected on positioned cursors, and largest-key is incompatible with bounds.

## Test Signals
Coverage is spread across cursor, checkpoint, bulk, random, bounded cursor, and format workloads. Direct signals include bulk cursor tests and format bulk paths, random cursor tests, bounded cursor suites, checkpoint read timestamp/config coverage, and insert-check use from checkpoint metadata code. Additional targeted tests should stress checkpoint cursors that read history-store values, reopen cached cursors after handle replacement, positioned remove retry behavior, and reserve followed by `get_value`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_hs.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_hs.c

## Purpose
`cur_hs.c` implements WiredTiger history-store cursors. These cursors wrap an underlying file cursor on the history-store table, expose a history-store-specific key/value API, apply visibility filtering over time windows, support history-store insert/update/remove/range-truncate operations, and handle multiple history-store IDs for disaggregated storage.

## Important APIs, Types, and Functions
The exported API includes `__wt_curhs_open`, `__wt_curhs_open_ext`, `__wt_curhs_cache`, `__wt_curhs_get_cached`, `__wt_curhs_next_hs_id`, `__wt_curhs_search_near_before`, `__wt_curhs_search_near_after`, `__wt_curhs_range_truncate`, `__wt_curhs_get_btree_id`, and `__wt_curhs_set_btree_id`. `__wt_curhs_open_ext` builds a `WT_CURSOR_HS` with history-store key/value formats and an underlying file cursor opened by `__curhs_file_cursor_open`.

`__curhs_set_key` accepts a variable argument count containing btree ID, optional datastore key, optional start timestamp, and optional counter. It records which pieces are set with `WT_HS_CUR_*` flags and sets the underlying file cursor key. `__curhs_set_value` stores a `WT_TIME_WINDOW` and sets the encoded history-store value fields. `__curhs_next_visible` and `__curhs_prev_visible` are the central visibility filters.

## Control Flow
Underlying file cursor operations run at `WT_ISO_READ_UNCOMMITTED` via `__curhs_file_cursor_next`, `prev`, and `search_near`, then the history-store wrapper filters records according to btree ID, datastore key, and time-window visibility. `next` and `prev` advance the file cursor, call the appropriate visible-skip loop, and expose the file cursor key/value buffers through the history-store cursor. `search_near` handles both directions: it first lands near the encoded key, tries visible records on the initial side, then crosses back through the requested key or btree range if needed.

Insert builds one or two `WT_UPDATE` structures. The standard update is stamped with the start time point; if the time window has a stop point, a tombstone stamped with the stop time is linked before it. The code searches the history-store btree and calls `__wt_hs_modify`, retrying on `WT_RESTART`. Update is a specialized operation that adds a stop timestamp to an existing positioned history-store record. Remove adds an un-timestamped tombstone through `__curhs_remove_int`. Range truncate maps history-store cursors to their underlying file cursors and calls `__wt_cursor_truncate`.

## State and Persistence Behavior
The history-store cursor itself owns transient state: selected `btree_id`, `hs_id`, datastore-key scratch buffer, `WT_TIME_WINDOW`, and key-selection flags. Persistent history data is stored in history-store btrees through update chains, not by this wrapper directly. Visibility behavior deliberately differs from ordinary file cursors: the file cursor reads uncommitted, while this layer decides whether to return all records, non-obsolete committed records, or records visible to the current transaction snapshot. Globally visible tombstones are skipped during reads because newer historical records for the same key may still be needed.

## Dependencies and Integration Points
The file integrates with reconciliation (`rec_hs.c` and `rec_write.c`), rollback-to-stable (`rts_history.c` and `rts_btree.c`), transaction code, history-store verification, btree read/delete paths that pre-cache history-store cursors, schema truncate routing, statistics, and disaggregated shared history-store URIs. It also cooperates with checkpoint cursors by propagating the session's selected history-store checkpoint name or a stable checkpoint URI suffix.

## Risks and Edge Cases
The highest risks are visibility and range-boundary mistakes. The cursor must not leak records from another btree ID unless `WT_CURSTD_HS_READ_ACROSS_BTREE` is set, and `btree_id + 1` is allowed only for truncation stop keys. Search-near must handle concurrent inserts, packed-key ordering differences between datastore keys and history-store keys, and both before/after helper semantics. Insert/update own update memory only until `__wt_hs_modify` succeeds. Disaggregated mode restricts writes to leader-owned history-store btrees. Cursor caching avoids metadata, recovery, no-reconcile, and default-session cases to prevent deadlocks or unsafe handle sweeping.

## Test Signals
History-store cursor behavior is exercised by reconciliation, rollback-to-stable, history-store verification, transaction cleanup, and format's `ops.hs_cursor` path. `test/format/hs.c` directly iterates history-store IDs and opens history-store cursors. Useful targeted tests include visible-skip behavior with globally visible tombstones, `search_near_before/after` across btree boundaries, checkpoint history-store cursor reads, disaggregated shared/private history-store ID mapping, and range truncation with explicit stop cursors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_hs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_index.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_index.c

## Purpose
`cur_index.c` implements read-only secondary-index cursors for WiredTiger tables. An index cursor scans an index btree, exposes the index key to the user, and reconstructs requested table values by positioning the necessary column-group cursors on the primary key carried inside each index entry.

## Important APIs, Types, and Functions
The exported entry point is `__wt_curindex_open`. It parses `index:<table>:<index>` URIs, opens the table and index metadata, initializes a `WT_CURSOR_INDEX`, opens the child cursor on `idx->source`, and opens only the column-group cursors needed by the index cursor projection. `__curindex_get_value` delegates to the inline `__wt_curindex_get_valuev`, while `__curindex_set_valuev` always returns `ENOTSUP` because index cursors are read-only.

`__curindex_move` is the core positioning helper. After the child index cursor moves, it exposes the child key through the public cursor, projects the primary-key columns out of the index key with `__wt_schema_project_slice`, copies that key to all required column-group cursors, and searches the column groups whose values are needed. `__curindex_search` and `__curindex_search_near` implement prefix-aware lookup because user-specified index keys usually omit the appended primary key.

## Control Flow
Opening first resolves table/index metadata, handles optional projection syntax in the URI, computes cursor value format and projection plan if projection columns were supplied, initializes the public cursor, opens the child index btree cursor, and opens required column groups with dump disabled. JSON dump column metadata is initialized when needed.

Iteration calls the child cursor's `next` or `prev`, then `__curindex_move`. Search sets the raw child key to the user key, calls child `search_near`, steps forward when it lands below the prefix, validates the found key has the requested prefix, repacks for custom collators when needed, and then moves column-group cursors. Search-near follows similar prefix logic but returns an exact sign that matches public cursor expectations. Reset resets both child and column-group cursors and clears child bounds on user-visible reset.

## State and Persistence Behavior
Index cursors are read-only. They persist no data directly and reject insert, update, remove, modify, reserve, cache, reopen, and largest-key operations. Their state is a coordinated set of cursor positions: the index child cursor determines the public key, and column-group cursors are positioned to provide table values. Projection plans and formats may be borrowed from metadata or allocated for a projected cursor and are freed on close.

## Dependencies and Integration Points
The implementation depends on schema metadata (`WT_TABLE`, `WT_INDEX`, column groups), structure packing/reformatting/planning helpers, collators, child file cursors, JSON column initialization, and bounded cursor helpers. `session_api.c` dispatches `index:` URIs here. Table cursor code coordinates with index cursors during table operations, and docs explicitly present table/index cursors as schema-layer cursor types.

## Risks and Edge Cases
Prefix matching is subtle because internal index keys append primary-key columns for uniqueness while users search only the declared index key. Custom collators require complete visible fields, so the code repacks found keys before comparison. Bound handling has special byte-increment logic: exclusive lower bounds and inclusive upper bounds must be shifted because the hidden primary key suffix is not part of the user's bound. Fixed-length all-`UINT8_MAX` lower bounds cannot be incremented and return `EINVAL`; all-maximum upper bounds clear the upper bound. Column-store indexes based only on a recno primary key are explicitly rejected.

## Test Signals
Index cursor coverage includes `test_index01.py`, custom-collator duplicate index tests, bounded cursor prefix-index C++ coverage, and `test_cursor_bound19.py`/`test_cursor_bound20.py` for basic and edge-case index bounds. Additional useful signals would include projected value retrieval across multiple column groups, prefix searches with custom collators, exact-sign behavior for search-near around duplicate index prefixes, and close cleanup after partial open failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_layered.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_layered.c

## Purpose
`cur_layered.c` implements cursors for WiredTiger layered tables, primarily for disaggregated storage. A layered cursor merges two constituent btrees: an ingest table for recent follower writes and a stable table for checkpointed/shared data. It presents a single `WT_CURSOR` API while handling leader/follower role differences, stable-checkpoint advancement, ingest tombstones, truncate-list visibility, and writes routed to the correct constituent.

## Important APIs, Types, and Functions
The exported cursor opener is `__wt_clayered_open`, and truncate integration is exported through `__wt_layered_truncate` and `__wt_clayered_range_truncate_stable_replay`. The cursor type is `WT_CURSOR_LAYERED`, with fields for ingest cursor, stable cursor, current cursor, layered dhandle, leader state, snapshot generation, read timestamp, stable checkpoint metadata LSN, and random cursor settings.

Important lifecycle helpers include `__clayered_enter`, `__clayered_leave`, `__clayered_open_ingest`, `__clayered_open_stable`, `__clayered_update_stable`, `__clayered_reopen_stable`, `__clayered_update_state`, `__clayered_close_cursors`, `__clayered_cache`, and `__clayered_reopen`. Read helpers include `__clayered_lookup`, `__clayered_iterate_constituents`, `__clayered_iterate_int`, `__clayered_search_near_int`, and `__clayered_get_current`. Write helpers include `__clayered_put`, `__clayered_remove_follower`, `__clayered_remove_leader`, `__clayered_modify_leader`, and `__clayered_modify_follower`.

## Control Flow
Opening validates a `layered:` URI, rejects in-memory, checkpoint, and bulk modes, obtains a layered dhandle, initializes the public cursor, optionally configures next-random behavior, and lets cursor initialization/cache logic finish setup. Constituent cursors are opened lazily in `__clayered_enter`: ingest is opened on first use, and stable is opened directly on leaders or on the latest stable checkpoint for followers once a checkpoint LSN is available. `__clayered_update_stable` also advances follower stable cursors to newer checkpoints when transaction and positioning rules allow it, or reopens stable on role changes.

Search checks ingest first on followers, treating ingest tombstones as deletes, checks the committed truncate list if ingest has no entry, and finally searches stable if stable reading is enabled. Iteration positions or advances both constituents, skips deleted ingest values, suppresses ingest reads on leaders, and chooses the smallest or largest visible key depending on direction. Search-near compares candidates from both constituents, prefers exact matches, then larger keys, then smaller keys, and has extra handling for deleted ingest entries and stable keys hidden by truncate-list ranges.

Writes route by role. Leaders write directly to stable. Followers write to ingest, using encoded tombstones for removes and special value encoding when user values begin with the tombstone marker. Non-overwrite follower insert/update paths first check the visible layered view and detect conflicts with committed truncate ranges. Modify can use fast modify only when the base value is suitable; otherwise it materializes the full value and updates ingest or stable.

## State and Persistence Behavior
Layered cursor state is split between the top-level cursor and constituent cursor positions. The public cursor points at the selected constituent key/value and tracks `WT_CURSTD_KEY_INT`/`VALUE_INT`; `current_cursor` identifies which constituent supplied the value. Ingest tombstones and tombstone-prefixed user values are encoded so deletes are distinguishable from real values. Follower range truncation writes layered tombstones into ingest for matching ingest keys and records a truncate-list entry so stable keys in the range are hidden. Stable checkpoint advancement is gated by transaction snapshot generation and read timestamp to avoid changing a cursor's view mid-transaction.

## Dependencies and Integration Points
This file integrates with layered table metadata, disaggregated storage checkpoint LSNs, stable checkpoint metadata lookup, file cursor operations, btree random cursor internals, truncate-list conflict/visibility helpers, schema truncate routing, transaction isolation and snapshot generation, cursor cache/reopen infrastructure, statistics, and diagnostic page/history-store dump hooks. It uses ordinary file cursors for both constituents and therefore depends on `cur_file.c` behavior for btree reads/writes, bounds, random access, and modification semantics.

## Risks and Edge Cases
This is a high-risk cursor because it merges two mutable ordered streams while roles and checkpoints can change. Role changes require all cursors to be unpositioned. Stable checkpoint advancement must not break repeatable reads or positioned stable cursors. Ingest tombstones must hide stable values without accidentally hiding user values that begin with the tombstone marker. Search-near must avoid returning keys inside committed truncate ranges and must recover when deleting entries changes the nearest key. Prepared conflicts can leave an ingest btree cursor with a page reference but no key flag, so iteration has special restart handling. The code also contains known FIXME areas around leader-mode ingest assumptions, asynchronous step-up, and cursor layering violations for random cursors.

## Test Signals
Signals come from disaggregated/layered table workloads, truncate routing tests, random cursor coverage, bounded cursor behavior, and diagnostic builds. Important scenarios to keep covered are leader versus follower write routing, stable checkpoint advancement while iterating, search/search-near when ingest tombstones shadow stable rows, range truncate conflict detection, role-change reopen behavior, next-random fallback from stable to ingest, and modify paths over tombstone-encoded values. Diagnostic helpers `__wt_debug_layered_cursor_page` and `__wt_debug_layered_cursor_tree_hs` provide triage signals by dumping both constituents around the same key.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_layered.c -->
