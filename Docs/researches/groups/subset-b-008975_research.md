# subset-b-008975 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_metadata.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_metadata.c

## Purpose
Implements the WiredTiger `metadata:` cursor family. It exposes metadata as a cursor over the metadata btree while also virtualizing the metadata table's own schema entry, which lives in the turtle file rather than as an ordinary metadata-table row. The `metadata:create` variant additionally strips internal-only schema details into a configuration suitable for `WT_SESSION.create`.

## Important APIs, types, and functions
The public entry point is `__wt_curmetadata_open`, which allocates `WT_CURSOR_METADATA`, installs metadata cursor methods, opens an underlying metadata file cursor, and optionally opens a second cursor for create-only config expansion. `WT_MD_CURSOR_NEEDKEY` and `WT_MD_CURSOR_NEEDVALUE` synchronize the public cursor buffers into the backing file cursor before delegated operations. `__schema_source_config` follows a `source=` URI in a metadata config and returns that source object's metadata. `__schema_create_collapse` removes non-create options and merges implicit column-group/source config for simple tables, named column groups, indices, and tiered shared-table column groups. `__curmetadata_setkv` copies a backing row into the public cursor, applying create-only collapse when required.

## Control flow
Opening sets key/value formats to `S`, then opens a metadata btree cursor via `__wt_metadata_cursor_open`; `metadata:create` sets `WT_MDC_CREATEONLY` and gets a second metadata cursor for source lookups. `next` starts at the synthetic metadata-table row if unpositioned, then scans the backing cursor at read-uncommitted isolation and skips incomplete entries. `prev` walks the backing cursor backwards and returns the synthetic metadata-table row when the backing scan reaches the beginning. `search` and `search_near` special-case keys matching `metadata:` or `file:WiredTiger.wt`; all other operations delegate to the backing cursor at read-uncommitted isolation. Inserts, updates, and removes call `__wt_metadata_insert`, `__wt_metadata_update`, and `__wt_metadata_remove` rather than directly mutating through the backing cursor.

## State, persistence, and dependencies
Cursor state is tracked with `WT_MDC_POSITIONED`, `WT_MDC_ONMETADATA`, and `WT_MDC_CREATEONLY`, plus standard cursor key/value flags. Persistent state is the WiredTiger metadata table and turtle-file metadata entry. The file depends on config parsing/collapse helpers, schema naming helpers, metadata cursor/search/update helpers, transaction-isolation macros, and the standard cursor initialization/close path.

## Integration points
This cursor is opened through `WT_SESSION.open_cursor` for `metadata:` and `metadata:create`; schema code uses it to inspect or copy object definitions. It integrates with the metadata subsystem instead of ordinary file cursor writes so metadata update semantics, locking, and turtle-file handling stay centralized.

## Risks and test signals
Risk centers on returning create-compatible configuration without leaking internal metadata, preserving read-uncommitted visibility for schema scans, and correctly ordering the synthetic metadata-table row relative to real rows. Tests should cover forward/reverse scans, search/search_near for both `metadata:` and `file:WiredTiger.wt`, readonly default behavior, write-enabled metadata cursors, implicit and tiered-shared column-group collapse, missing source entries, and incomplete metadata rows skipped during scans.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_prepared_discover.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_prepared_discover.c

## Purpose
Implements the prepared-transaction discovery cursor. The cursor enumerates prepared transaction IDs discovered during recovery or prepared-discovery setup, allowing callers to claim or inspect outstanding prepared work.

## Important APIs, types, and functions
The entry point is `__wt_cursor_prepared_discover_open`, which creates a `WT_CURSOR_PREPARE_DISCOVERED` with key format `Q` and no value columns. `__cursor_prepared_discover_setup` applies prepared-discovery filtering to handles, then populates the cursor list. `__cursor_prepared_discover_list_create` copies prepared IDs from `S2C(session)->txn_global.pending_prepare_items` into a cursor-owned, zero-terminated array. Cursor methods are intentionally narrow: `next`, `reset`, and `close` are supported; value, search, update, compare, and reverse iteration are not.

## Control flow
Open allocates the cursor, installs methods, and runs setup under checkpoint and schema locks to keep the metadata and prepared-artifact view consistent. `next` checks whether the cursor list exists and whether the current slot is nonzero, packs the prepared ID into the cursor key buffer using the `Q` format, advances the array index, and marks the key internal. `reset` rewinds the index and clears key/value flags. `close` frees the cursor list and then walks any remaining pending-prepared hash buckets, treating them as unclaimed transactions.

## State, persistence, and dependencies
Cursor-owned state is the copied prepared-ID array, list allocation, and next index. Connection-owned state is `WT_TXN_GLOBAL.pending_prepare_items`, a hash table of `WT_PENDING_PREPARED_ITEM` entries with modification arrays. The cursor close path frees unclaimed transaction operation arrays via `__wt_txn_op_free`; claimed items are expected to have been removed by other prepared transaction claim logic before close.

## Integration points
The file is tied to prepared transaction recovery and discovery, transaction-global prepared maps, schema/checkpoint locks, and standard cursor API wrappers. It provides a cursor API facade around connection-level prepared transaction metadata rather than over a btree.

## Risks and test signals
The close path deliberately errors if unclaimed prepared transactions remain, so ownership transfer and cleanup ordering are critical. Tests should verify empty discovery, multiple hash buckets, reset-and-rescan behavior, key packing format, claimed-item removal by other sessions, unclaimed cleanup error reporting, and lock interaction with schema/checkpoint activity. The TODO about a prepared transaction discovery read/write lock is a concurrency risk signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_prepared_discover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_stat.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_stat.c

## Purpose
Implements WiredTiger statistics cursors for connection, session, file, table, index, colgroup, layered, tiered, and size-only statistics. It snapshots or aggregates stats into `WT_CURSOR_STAT` and exposes each statistic by integer key with description, printable value, and numeric value.

## Important APIs, types, and functions
`__wt_curstat_open` validates statistics configuration, allocates `WT_CURSOR_STAT`, saves cursor config for refresh, initializes the first snapshot, and installs cursor methods. `__wt_curstat_init` dispatches `statistics:` URIs to connection, session, file, table, index, colgroup, layered, or tiered initializers. `__curstat_get_key`, `__curstat_get_value`, `__curstat_set_keyv`, `__curstat_next`, `__curstat_prev`, and `__curstat_search` implement cursor traversal and access. `__wt_curstat_size_local`, `__wt_curstat_size_disagg`, and `__curstat_file_size` provide a fast size-only path. `__wt_curstat_dsrc_final` finalizes data-source stats layout.

## Control flow
Open parses the `statistics` configuration, enforcing compatibility with connection stats flags and rejecting incompatible combinations such as `size` plus `clear`. It sets key format `i` and value format `SSq`. Traversal lazily refreshes if `notinitialized` is set, then uses `stats_base`, `stats_count`, and optional `next_set` callbacks to walk one or more statistic sets. Search validates the requested statistic ID range and returns the corresponding offset. Reset marks the cursor for reinitialization and clears session stats immediately for `statistics:session`.

## State, persistence, and dependencies
Statistics are copied or aggregated into the cursor union (`conn_stats`, `dsrc_stats`, or `session_stats`) and are not persistent user data. The cursor may clear live connection/data-source/session counters when `WT_STAT_CLEAR` is set. File size may come from local filesystem/block-manager size or from disaggregated checkpoint metadata. Layered-table stats aggregate ingest and stable constituent tables, with followers reading the most recent stable checkpoint name.

## Integration points
This file integrates with generated statistic descriptors, connection/stat flag configuration, btree stat initialization, schema stats helpers for tables/indices/colgroups, block manager file sizing, disaggregated checkpoint sizing, layered table handles, and the standard cursor API. It asserts data-source statistics are not available before recovery completes.

## Risks and test signals
Risk areas include correct stat-key base/count arithmetic, config compatibility, clearing behavior, size-only fast path falling back safely, dhandle release in layered and file initialization, and refresh semantics after reset. Tests should cover all URI dispatches, raw and non-raw key/value access, next/prev/search boundaries, `statistics=(all|fast|size|clear|cache_walk|tree_walk)` combinations, local missing files, disaggregated checkpoint sizes, and layered follower checkpoint lookup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_std.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_std.c

## Purpose
Provides shared cursor infrastructure: default unsupported/no-op handlers, key/value packing and unpacking, raw helpers, cursor modify fallback, cursor caching/reopen, runtime reconfiguration, bounds management, position duplication, generic initialization, close, equality, and diagnostic dispatch.

## Important APIs, types, and functions
Default methods include `__wti_cursor_noop`, `__wt_cursor_notsup`, `__wti_cursor_*_notsup`, and `__wti_cursor_set_notsup`. Key/value helpers are `__wti_cursor_get_keyv`, `__wti_cursor_set_keyv`, `__wti_cursor_get_valuev`, `__wti_cursor_set_valuev`, `__wt_cursor_get_raw_key`, `__wt_cursor_set_raw_key`, `__wt_cursor_get_raw_value`, `__wt_cursor_set_raw_value`, and `__wt_cursor_get_raw_key_value`. Cache functions are `__wti_cursor_cache`, `__wti_cursor_reopen`, `__wti_cursor_cache_release`, `__wti_cursors_can_be_cached`, and `__wt_cursor_cache_get`. Other central APIs are `__wti_cursor_reconfigure`, `__wti_cursor_bound`, `__wt_cursor_bounds_save`, `__wt_cursor_bounds_restore`, `__wt_cursor_dup_position`, `__wt_cursor_init`, `__wt_cursor_close`, and `__wt_cursor_equals`.

## Control flow
Get/set helpers wrap standard API accounting, validate key/value flags, and fast-path common formats (`u`, `S`, record numbers, and byte formats) while falling back to WiredTiger struct pack/unpack. Setters release debug-copy buffers, preserve/reuse allocated `WT_ITEM` storage when possible, and record `saved_err` on failure. Cursor close either destroys or, via caller paths, may cache eligible cursors. Cache release resets the cursor, clears bounds, preserves useful buffers, acquires/releases dhandle references, moves the cursor between session open and cache queues, and adjusts statistics. Cache get matches by URI hash and URI, reopens the cursor, repairs flag-only configuration differences, and restores btree read-once/dhandle side effects.

## State, persistence, and dependencies
The file owns no durable data but manages long-lived cursor memory, session cursor queues, cursor flags, bounds buffers, URI hashes, open/cached cursor counts, and dhandle use counts. It depends on config parsing, WiredTiger struct packing, session/dhandle sweep, dump cursor wrapping, transaction isolation for modify, compare/collator helpers, statistics macros, and diagnostic btree/layered debug hooks.

## Integration points
Nearly every cursor type uses these helpers either directly through `WT_CURSOR_STATIC_INIT` method tables or indirectly through `__wt_cursor_init`. Table, metadata, statistics, history/version, btree, dump, and layered cursors rely on this file for consistent API behavior, read-only enforcement, cacheability rules, bounds semantics, and error messages.

## Risks and test signals
This is high-blast-radius code. Risks include dangling application-memory references after set/get, incorrect key/value flag transitions, cached cursor reuse with incompatible config, dhandle lifetime leaks, bounds restore failures across composed cursors, and modify running outside supported transaction isolation. Tests should cover all key/value formats including raw mode, cursor-copy debug, append/overwrite/read-only config, dump wrappers, cache hit/miss/reopen/sweep paths, bounds overlap/equality/inclusive rules, cursor duplication, and fallback modify in explicit snapshot transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_std.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_table.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_table.c

## Purpose
Implements table cursors for non-simple WiredTiger tables. A table cursor composes one cursor per column group and lazily opens index cursors when updates require index maintenance. Simple tables are optimized by returning the single underlying data-source cursor with the public URI adjusted.

## Important APIs, types, and functions
`__wt_curtable_open` is the public entry point. `APPLY_CG` applies cursor operations across column-group cursors. `__wt_apply_single_idx` and `__apply_idx` project table values into index keys and apply index cursor operations. Accessors include `__curtable_get_key`, `__curtable_get_value`, `__curtable_set_key`, and `__curtable_set_valuev`. Cursor operations include `next`, `next_random`, `prev`, `reset`, `search`, `search_near`, `insert`, `update`, `remove`, `reserve`, `largest_key`, `bound`, `close`, and `__wt_table_range_truncate`.

## Control flow
Open resolves the table and optional projection columns, rejects incomplete tables, returns the underlying cursor for simple tables, or allocates `WT_CURSOR_TABLE`. It reformats value format and projection plan for projected cursors, handles `next_random` by disabling unsupported methods, initializes the table cursor, opens column-group cursors immediately, and saves normalized config for later index opens. Reads apply operations across column groups; `search_near` and random next position the primary column group first and then search secondary groups by copied key/recno. Updates open indices lazily. Insert detects duplicate primary keys when indices exist so overwrite can become an update; update removes old immutable-safe index entries before writing new column-group values and reinserting index keys; remove deletes index entries before removing column groups.

## State, persistence, and dependencies
The table cursor owns arrays of column-group cursors, index cursors, temporary value-copy buffers, copied config, projection plan, and the acquired `WT_TABLE` reference. Persistent changes land in underlying column-group and index data sources. Dependencies include schema table/index/column-group metadata, projection planning/merge/slice helpers, range truncate, transaction context checks, cursor bounds helpers, JSON column initialization, and standard cursor initialization/closing.

## Integration points
This file is the bridge from logical table APIs to physical data-source cursors. It coordinates with schema table completeness, column groups, index definitions, dump/json cursor behavior, next-random btree cursors, and truncate/index maintenance.

## Risks and test signals
Risks include index inconsistency on partial failure, preserving primary key/recno across column groups, projection buffer aliasing when users pass pointers from prior `get_value`, bounds rollback across multiple column groups, and lazy index open failure after the table cursor is already live. Tests should cover simple versus multi-column-group tables, projections, indices including immutable indices, overwrite inserts, duplicate keys, remove/update/truncate index cleanup, reserve returning a searchable value, `next_random`, bounds propagation/failure restore, incomplete table errors, dump/json cursors, and close cleanup after partial index-open failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_version.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_version.c

## Purpose
Implements debug version cursors that expose all visible or raw historical versions for a key, including in-memory update-chain entries, the on-disk image, and history-store records. Values are returned as metadata columns followed by the underlying value.

## Important APIs, types, and functions
`__wt_curversion_open` initializes `WT_CURSOR_VERSION`, opens a read-only file cursor, optionally opens a history-store cursor, freezes a connection pinned timestamp when the first version cursor opens, parses `debug.dump_version.*` options, and installs methods. `WT_CURVERSION_METADATA_FORMAT` defines ten timestamp/transaction fields plus type, prepare, flags, and location bytes. Main helpers include `__curversion_process_chain`, `__curversion_process_on_disk`, `__curversion_process_hs`, `__curversion_next_single_key`, `__curversion_skip_starting_updates`, `__curversion_value_return_from_upd`, `__curversion_value_return_from_disk_image`, and `__curversion_value_return_from_hs`.

## Control flow
Setting a key resets version state and forwards key packing to the underlying file cursor. Search requires snapshot isolation, verifies the file cursor is not already positioned, performs a key-only btree search, skips aborted/invisible starting updates, and returns the newest version. `next` either advances within one key or, with `cross_key`, walks to the next btree key after all versions for the current key are exhausted. For one key, processing order is update chain, on-disk image, then history store. Tombstones record stop metadata before advancing to value updates. Modify updates are reconstructed before value return. Timestamp-order and start-timestamp modes prune duplicates or stop when older versions are no longer relevant.

## State, persistence, and dependencies
The cursor stores `next_upd`, exhaustion flags for update/on-disk/history-store phases, stop transaction/timestamps/prepared metadata, optional `start_timestamp`, file cursor, and history-store cursor. It does not mutate persistent data, but it reads volatile update chains, stable on-page time windows, and history-store records. Dependencies include btree cursor internals, update visibility, prepared-state atomics, transaction global pinned timestamps, history-store cursor APIs, modify reconstruction, time-window macros, and standard cursor packing.

## Integration points
Version cursors are debug/open-cursor functionality layered over ordinary file cursors. They integrate with transaction visibility and history-store internals, require snapshot isolation for stable global visibility, and expose raw-key/value and cross-key options for diagnostic tooling and Python API marking via `WT_CURSTD_VERSION_CURSOR`.

## Risks and test signals
Risk is high because the cursor interprets MVCC internals. Important cases include prepared rollback visibility, tombstone stop metadata, globally visible pruning, start timestamp cutoff, history-store modify reconstruction, on-disk overflow restart, cross-key reset, raw mode metadata/data splitting, and correct decrement of `version_cursor_count` on close. Tests should cover row and variable-column pages, in-memory btrees, history-store present/absent, prepared updates and tombstones, timestamp-order output, visible-only output, show-prepared-rollback restrictions, snapshot-isolation enforcement, and failure cleanup after partial open.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/Makefile -->
# sources/storage-engines/wiredtiger/src/docs/Makefile

## Purpose
Small make wrapper for WiredTiger documentation generation.

## APIs and control flow
The default `all` target changes to `../../dist` and runs `sh s_docs -t`, which likely builds targeted documentation output. `clean` runs `sh s_docs -a`, likely a broader rebuild/cleanup mode. Both targets are marked phony.

## State, dependencies, integration, risks
It has no persistent state beyond artifacts produced by `dist/s_docs`. It depends on relative repository layout from `src/docs` to `dist`, POSIX shell, and the `s_docs` script. Tests/signals are make invocation from `src/docs`, correct relative path resolution, and ensuring generated docs are cleaned or rebuilt by the intended `s_docs` flags.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/build-pydoc.sh -->
# sources/storage-engines/wiredtiger/src/docs/build-pydoc.sh

## Purpose
Builds Python API pydoc HTML for WiredTiger.

## APIs and control flow
The script computes `DOCS` from its own path, sets `TOP=$DOCS/..`, sources `$TOP/config.sh`, changes into `python`, and runs `pydoc -w wiredtiger` with `PYTHONPATH` pointing at `../../lang/python/src` and a Thrift Python 2.6 site-packages directory under `$THRIFT_HOME`.

## State, dependencies, integration, risks
It writes pydoc-generated HTML in the `python` directory. Dependencies are shell, `config.sh`, Python/pydoc, generated or source WiredTiger Python bindings, and Thrift environment variables. Risks are stale Python 2.6 Thrift path assumptions, execution from unexpected locations, missing `$THRIFT_HOME`, and pydoc importing code with side effects. Test signals are successful import of `wiredtiger` under the constructed `PYTHONPATH` and reproducible generated HTML.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/build-pydoc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/js/sorttable.js -->
# sources/storage-engines/wiredtiger/src/docs/js/sorttable.js

## Purpose
Bundled browser-side sortable table library, modified for WiredTiger so alphabetic sorting is case-insensitive. It enables Doxygen/reference-manual HTML tables with class `sortable` to sort when a header is clicked.

## Important APIs and control flow
The global `sorttable` object exposes `init`, `makeSortable`, `guessType`, `getInnerText`, `reverse`, sort comparators, and `shaker_sort`. Initialization runs on DOM ready across modern browsers, old IE, Safari polling, and `window.onload`. `makeSortable` ensures a `thead`, moves `sortbottom` rows into `tfoot`, detects column types or explicit `sorttable_<type>` classes, attaches header click handlers, builds decorated row arrays, sorts, and appends rows back into the tbody. Repeated clicks reverse the current ordering and update sort indicators.

## State, dependencies, integration, risks
State is stored directly on DOM nodes (`sorttable_sortfunction`, column index, tbody reference, CSS classes, indicator spans) and in global helpers such as `forEach` and event handlers. It depends only on browser DOM APIs. Risks are global-variable leakage, old-browser compatibility code, non-stable default JavaScript sort, numeric/date parser ambiguity, missing cells in ragged tables, and `innerHTML` indicators. Test signals are sortable Doxygen tables with text, numeric, date, custom-key, input-containing, no-sort, sortbottom, and repeated reverse-click cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/js/sorttable.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/style/DoxygenLayout.11.xml -->
# sources/storage-engines/wiredtiger/src/docs/style/DoxygenLayout.11.xml

## Purpose
Doxygen layout definition for newer Doxygen navigation and page structure, likely Doxygen 1.11-era output.

## Structure and integration
The XML declares nav tabs for main page, pages, topics titled `Modules`, namespaces, classes, files, examples, and user tabs for Community and License. It defines class, namespace, file, group, and directory page sections, controlling visibility for descriptions, include graphs, member declarations, member definitions, author sections, and directory graphs. Variables such as `$ALPHABETICAL_INDEX`, `$SHOW_INCLUDE_FILES`, `$CLASS_GRAPH`, `$COLLABORATION_GRAPH`, `$INCLUDE_GRAPH`, `$INCLUDED_BY_GRAPH`, `$GROUP_GRAPHS`, and `$SHOW_USED_FILES` defer behavior to Doxygen config.

## State, dependencies, risks, tests
The file is declarative and has no runtime state. It depends on Doxygen accepting `version="1.0"` layout syntax and the `topics` tab type. Risks are schema drift between Doxygen versions, accidental visibility changes, and divergence from the non-`.11` layout. Test signals are successful Doxygen generation with expected nav tabs and no layout warnings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/style/DoxygenLayout.11.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/style/DoxygenLayout.xml -->
# sources/storage-engines/wiredtiger/src/docs/style/DoxygenLayout.xml

## Purpose
Base Doxygen layout definition for WiredTiger documentation output.

## Structure and integration
The XML is parallel to `DoxygenLayout.11.xml` but uses a `modules` nav tab and hides the top-level classes tab. It defines the same page families: class, namespace, file, group, and directory. It exposes file lists and globals, user tabs for Community and License, and standard Doxygen sections for member declarations and definitions.

## State, dependencies, risks, tests
It is a declarative Doxygen input with no persistent state. It depends on Doxygen layout syntax and config variables such as `$SHOW_INCLUDE_FILES` and `$GROUP_GRAPHS`. Risks are mismatched behavior across Doxygen versions, hidden classes navigation surprising users, and maintaining two nearly identical layout files. Test signals are Doxygen builds across supported versions and visual checks for nav availability, file/source links, examples, modules, community, and license pages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/style/DoxygenLayout.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/tools/doxfilter -->
# sources/storage-engines/wiredtiger/src/docs/tools/doxfilter

## Purpose
Shell wrapper for the C/comment Doxygen filter.

## APIs and control flow
The script determines its directory with `dirname $0` and executes `python $tooldir/doxfilter.py "$@"`. It preserves all arguments for Doxygen's input-filter invocation.

## State, dependencies, integration, risks
The wrapper has no state. It depends on `/bin/sh`, `python` on `PATH`, and `doxfilter.py` in the same directory. It integrates with Doxygen `INPUT_FILTER` configuration where a stable executable script path is more convenient than embedding a Python script path. Risks are Python version ambiguity and paths containing unusual shell characters. Test signals are executable permissions and successful filtered output for a sample documented C source.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/tools/doxfilter -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/tools/doxfilter.py -->
# sources/storage-engines/wiredtiger/src/docs/tools/doxfilter.py

## Purpose
Input filter for WiredTiger reference documentation. It rewrites documentation comments and expands custom `@arch_page` markers with structured architecture-page metadata from `dist/docs_data.py`.

## Important APIs and control flow
The script imports `docs_data.arch_doc_pages` into `arch_doc_lookup`. `process` converts `/*!` to `/**`, then calls `process_arch` if `@arch_page` appears. `process_arch` validates syntax, extracts page identifier and title, looks up data structures and files, and emits `@arch_page_top`, optional `@arch_page_table`, and `@arch_page_caution` directives. `err` reports filename and line context, although the visible code does not increment `linenum`. Main reads the first filename argument, prints processed content, and exits after one file.

## State, dependencies, integration, risks
State is transient lookup dictionaries and current filename/line globals. It depends on repository layout to locate `dist/docs_data.py`, Python, regular expressions, and Doxygen macros that understand the emitted commands. Risks include KeyError for unknown architecture page IDs, incomplete line-number reporting, processing only the first argument, and custom macro drift. Test signals are C docs with plain comments, valid and invalid `@arch_page` markers, pages with and without table data, and missing docs_data entries.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/tools/doxfilter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/tools/doxypy.py -->
# sources/storage-engines/wiredtiger/src/docs/tools/doxypy.py

## Purpose
Vendored `doxypy` input filter that converts Python docstrings into Doxygen-compatible comment blocks before documentation generation.

## Important APIs and control flow
`FSM` implements transition-driven parsing. `Doxypy` configures regexes for single and double triple-quoted strings, `def`/`class` lines, multiline definitions, imports, comments, and empty lines. The FSM tracks file head, definition/class discovery, body, multiline definition, and docstring states. Callback methods collect docstrings, optionally prefix a brief line, emit `##` plus `#` comment lines at the same indentation, and then emit the triggering definition/class block. `parseFile` streams input line by line and flushes output. `optParse` supports `--autobrief` and `--debug`.

## State, dependencies, integration, risks
Parser state lives in `output`, `comment`, `filehead`, `defclass`, `indent`, and FSM current state. It depends on Python `re`, `sys`, and `optparse`. It integrates with `pyfilter`, which pipes its output into `fixlinks.py`, and with Doxygen filter settings. Risks include Python 2-era idioms, mutable default argument in `FSM.__init__`, limited syntax recognition for decorators/async/type annotations, docstring association edge cases, and GPL licensing considerations for vendored tooling. Test signals are module, class, function, multiline definition, raw/unicode docstring, autobrief, no-docstring, and broken-pipe cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/tools/doxypy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/tools/fixlinks.py -->
# sources/storage-engines/wiredtiger/src/docs/tools/fixlinks.py

## Purpose
Post-processes `doxypy` output for WiredTiger Python API documentation so generated comments link back to corresponding C API documentation.

## Important APIs and control flow
`process` applies regex substitutions to stdin text. It rewrites `Proxy of C ... struct` comments into Python wrapper wording plus `@copydoc` references, uppercases generated `wt_*` class references, maps `char` pointer wording to `string`, adds method-level `@copydoc WT_CONNECTION/WT_CURSOR/WT_SESSION::method` references, adds global function `@copydoc ::wiredtiger_*` references, and removes generated handle parameters from comments. Main reads all stdin and writes transformed output.

## State, dependencies, integration, risks
The script is stateless aside from regex processing. It depends on Python regex semantics and exact generated wrapper comment shapes. It integrates in `pyfilter` after `doxypy.py`. Risks are broad regex replacements inside comments, API naming drift, missed modern annotations, and incorrect rewriting if wrapper text changes. Tests should feed representative generated Python binding snippets for connection, cursor, session, struct wrappers, global functions, `char` arguments, and already-qualified C references.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/tools/fixlinks.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/tools/pyfilter -->
# sources/storage-engines/wiredtiger/src/docs/tools/pyfilter

## Purpose
Shell wrapper for Python documentation filtering.

## APIs and control flow
The script computes its own directory and runs `python $tooldir/doxypy.py "$@" | python $tooldir/fixlinks.py`. It first converts Python docstrings into Doxygen-style comments, then rewrites links and C API references.

## State, dependencies, integration, risks
The wrapper has no durable state. It depends on `/bin/sh`, `python`, the two sibling Python scripts, and pipe behavior. It integrates with Doxygen as an input filter for Python sources. Risks are losing the upstream `doxypy.py` exit status through the pipeline in plain `sh`, Python version ambiguity, and path quoting limitations. Test signals are executable permissions, successful transformation of a sample Python binding file, and failure behavior when either Python script is missing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/docs/tools/pyfilter -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict.h -->
# sources/storage-engines/wiredtiger/src/evict/evict.h

## Purpose
Defines the public internal eviction subsystem state structure, flags, exported eviction APIs, and inline helper prototypes for WiredTiger cache eviction.

## Important APIs, types, and fields
`struct __wt_evict` tracks eviction progress, application waits/evictions, max page sizes per checkpoint, max eviction latency, nested history-store eviction time, lock wait time, read generations, eviction pass generations, condition variables/spinlocks, dirty/clean/update trigger and target percentages, checkpoint/scrub targets, cache wait/stuck timeouts, tuning data, LRU walk state, eviction queues, pass interruption, eviction slots, aggression score, empty-queue score, cache flags, and tuning/use-NPOS booleans. Defines include pressure/aggression constants, cache state flags (`WT_EVICT_CACHE_*`), call flags (`WT_EVICT_CALL_*`), `WT_EVICT_MAX_WORKERS`, and prototypes for eviction create/destroy/config, eviction calls, file eviction, exclusive file eviction, worker thread lifecycle, stats, verbose dump, priority, server wake, and many static inline helpers.

## Control flow and state model
The header is not executable control flow but establishes the shared state contract consumed by eviction server, worker, application-assist, checkpoint, cache accounting, and page-management code. The queue pointers (`current`, `fill`, `other`, `urgent`) model double-buffered LRU candidate queues plus urgent eviction. Progress and aggression counters determine when eviction becomes more forceful or declares the cache stuck. Threshold fields separate clean, dirty, update, hard, checkpoint, and scrub pressure.

## Persistence, dependencies, and integration
Eviction state is in-memory connection/cache state, not durable data, but it drives when dirty pages are written and pages leave cache. It includes `evict_private.h` and depends on core WiredTiger types such as `WT_SESSION_IMPL`, `WT_REF`, `WT_PAGE`, `WT_BTREE`, `WT_CACHE_OP`, locks, condition variables, and queue definitions. Generated prototype sections are maintained by `prototypes.py`.

## Risks and test signals
Risks are race conditions on shared counters/flags, threshold misconfiguration, queue pointer invariants, worker tuning instability, stuck-cache false positives/negatives, and prototype drift if generated sections are edited manually. Tests/signals include cache pressure workloads, dirty/update-heavy workloads, checkpoint scrub behavior, urgent eviction, application assist, worker scaling, exclusive file eviction, in-memory and history-store reentry scenarios, stats accuracy, and generated-prototype verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict.h -->
