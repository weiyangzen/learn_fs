# Research Group subset-b-008979

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/conf.h -->
# sources/storage-engines/wiredtiger/src/include/conf.h

## Purpose
`conf.h` defines WiredTiger's compiled-configuration representation. It turns generated configuration metadata into fixed-size, position-independent structures so API default/user configuration can be precompiled once and queried by numeric key IDs instead of reparsing strings on every call.

## Important APIs, Types, and Functions
The public-facing helpers are macros: `__wt_conf_gets`, `__wt_conf_getones`, and `__wt_conf_gets_def`, which wrap `__wt_conf_gets_func`/`__wt_conf_gets_def_func` with IDs from `WT_CONF_ID_STRUCTURE`. `WT_CONF_BINDINGS` and `WT_CONF_BIND_DESC` describe fast-path bound configuration values, including type, legal choices, and a session binding-table offset.

`WT_CONF` is the central compiled config object. It stores a default bitmap, diagnostic source/default/API strings, a `value_map` from key ID to `WT_CONF_VALUE`, counts and capacity for nested sub-configs and values, and binding descriptors. `WT_CONF_VALUE_TABLE_ENTRY` computes the inline value table address from `conf_value_table_offset`, keeping the structure copyable without pointer fixups.

The generated `WT_CONF_API_DECLARE` declarations define per-API superstructures such as `WT_CONF_API_TYPE(WT_SESSION, create)`, and sizing macros expose their total size/counts for compilation.

## Control Flow
API code compiles one or more config strings against a `WT_CONFIG_ENTRY`, producing a superstructure containing `WT_CONF[]` and `WT_CONF_VALUE[]`. Later callers use numeric IDs built from `conf_keys.h` through `WT_CONF_ID_STRUCTURE`. The lookup path first checks `bitmap_default` for cheap default detection, then consults `value_map` and the value table when an explicit value, binding descriptor, or sub-config entry is present.

## State and Persistence Behavior
The state is in-memory only. A `WT_CONF` owns only `source_config`; `api_config` and `default_config` are borrowed but guaranteed to outlive the compiled object. Position independence is a key persistence-like invariant inside memory: callers can copy the entire superstructure as bytes and still recover value-table entries via offsets.

## Dependencies and Integration Points
This header depends on generated IDs from `conf_keys.h`, parser/checking structures from `config.h`, bit-string helpers, `WT_CONFIG_ITEM`, and `WT_CONFIG_ENTRY`. It integrates with connection-level compiled config arrays in `WT_CONNECTION_IMPL` and session binding state.

## Risks and Edge Cases
The main risk is generator drift: the declared per-API counts must match generated checks/defaults, or compiled config writes can overrun or lookups can miss values. The 1-based `value_map` and offset-derived value table make off-by-one bugs costly. Bound values are optimized around a small fixed table (`WT_CONF_BIND_VALUES_LEN`), so adding many bound values requires coordinated sizing changes.

## Test Signals
Useful test signals are configuration parsing/validation suites, API open/create/reconfigure tests that exercise compiled and string configs equivalently, tests for default shortcuts, nested sub-config lookup, choice matching, and sanitizer coverage around generated count mismatches.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/conf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/conf_inline.h -->
# sources/storage-engines/wiredtiger/src/include/conf_inline.h

## Purpose
`conf_inline.h` provides small, hot inline helpers for compiled configuration detection, validation, default lookup, and hex decoding. It keeps common config operations close to call sites without forcing full parser logic into every user.

## Important APIs, Types, and Functions
`__wt_conf_is_compiled` checks whether a config pointer lies inside `conn->conf_dummy`; `__wt_conf_get_compiled` converts that dummy pointer offset into `conn->conf_array[]`. `__wt_conf_check_choice` validates string choices and canonicalizes successful matches to generated `__WT_CONFIG_CHOICE_*` string addresses, enabling `WT_CONF_STRING_MATCH` pointer comparisons.

`__wt_conf_check_one` runs any custom check function, choice checks, and numeric min/max validation from `WT_CONFIG_CHECK`. `__wt_conf_gets_def_func` implements the fast default path for callers supplying an override default. `__wt_conf_parse_hex` parses up to 64 bits of hexadecimal text with explicit invalid-character and length errors.

## Control Flow
Compiled config callers pass a dummy string. The inline detection path treats it as an index into the connection's compiled config array. Validation of each value is layered: custom callback first, then generic choice/min/max checks only when a check string exists. Default lookup short-circuits through the compiled config bitmap before falling back to the full lookup function.

## State and Persistence Behavior
The helpers mutate only returned `WT_CONFIG_ITEM` values and choice string pointers. Canonicalizing choices changes `value->str` from the original input span to a generated static choice string, which is intentionally stable for pointer comparisons. No durable state is written.

## Dependencies and Integration Points
The file depends on `WT_CONNECTION_IMPL` compiled config arrays, `WT_CONFIG_CHECK`, `WT_CONFIG_ITEM`, generated choice symbols from `config.h`, and WiredTiger error macros. It is used by compiled config accessors and by compilation/checking code that wants fast validation in headers.

## Risks and Edge Cases
Pointer-range compiled detection assumes dummy config pointers are never forged and that `conf_dummy`/`conf_size` accurately cover the dummy string table. Blank strings are legal choices only through `__WT_CONFIG_CHOICE_NULL`, which can surprise callers expecting ordinary choice text. Hex parsing uses character values as table indexes and rejects strings longer than 16 hex digits to avoid overflow.

## Test Signals
Tests should compare compiled and uncompiled config lookup results, verify choice canonicalization including blank choices, assert min/max failure messages, and exercise invalid/too-long hex strings. Fuzzing config input should reach `__wt_conf_parse_hex` and choice validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/conf_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/conf_keys.h -->
# sources/storage-engines/wiredtiger/src/include/conf_keys.h

## Purpose
`conf_keys.h` is generated configuration-key metadata. It assigns stable numeric IDs to every configuration key and exposes a nested `WT_CONF_ID_STRUCTURE` so code can refer to dotted configuration names in C syntax while compiled config lookup uses compact integer IDs.

## Important APIs, Types, and Functions
The first generated section defines `WT_CONF_ID_*` constants and `WT_CONF_ID_COUNT`. The second section defines a static nested structure containing categories such as `Debug_mode`, `Eviction`, `Log`, `Tiered_storage`, and direct scalar keys. Dotted names are encoded by OR-ing key IDs into 16-bit lanes, for example `Category | (child << 16)` and deeper children with `<< 32`.

## Control Flow
The file has no functions. It participates in control flow at preprocessing/compile time: macros in `conf.h` expand `WT_CONF_ID_STRUCTURE.Operation_tracking.enabled` or similar field references into packed numeric IDs. Lookup code then extracts those packed IDs to traverse compiled sub-configs.

## State and Persistence Behavior
There is no runtime-owned state beyond one generated static constant. The practical persistence contract is ABI/source compatibility: IDs and category packing must stay consistent with generated config entries and any precompiled config structures created for a running connection.

## Dependencies and Integration Points
The file is generated by `dist/api_config.py` and consumed by `conf.h`, `conf_inline.h`, API implementation files, and configuration compiler/checker code. It must align with `config.h`'s `WT_CONFIG_ENTRY_*` values and generated choice/check tables in the build.

## Risks and Edge Cases
Because IDs are packed into fixed bit lanes, very large key counts or deeper nesting would require representation changes. Manual edits would desynchronize source references from generated parser tables. Fields named after C keywords are adjusted, such as `_default`, so users must reference the generated structure name rather than assuming raw config spelling.

## Test Signals
Compile coverage is the first signal: stale field references fail to build. Runtime config tests for nested keys, generated default strings, and compiled lookup equivalence catch ID/check-table drift. Regeneration diffs from `dist/api_config.py` are important review artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/conf_keys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/config.h -->
# sources/storage-engines/wiredtiger/src/include/config.h

## Purpose
`config.h` defines the runtime parser/checking metadata for WiredTiger configuration strings. It supplies parser state, generated API entry IDs, generated choice symbols, type codes used by compiled config, and convenience macros for default matching and quote preservation.

## Important APIs, Types, and Functions
`WT_CONFIG` tracks a parser over a string with original/end/current pointers, nesting depth, top-level state, and a tokenizer jump table. `WT_CONFIG_CHECK` describes one legal key: name, type, optional check callback, sub-config checks/jump table, compiled type, key ID, min/max, and choices. `WT_CONFIG_ENTRY` describes one API method's base config, check table, method ID, and compiled-config sizing.

Macros include `WT_CONFIG_REF`, `WT_CONFIG_BASE`, `WT_CONFIG_ITEM_STATIC_INIT`, `WT_CONFIG_PRESERVE_QUOTES`, `WT_CONFIG_MATCHES_DEFAULT`, and `__wt_config_empty`. The generated `WT_CONFIG_ENTRY_*` IDs enumerate every configured API method and metadata schema.

## Control Flow
Parser code initializes `WT_CONFIG` over caller/default strings and walks keys using generated jump tables. Validation consults `WT_CONFIG_CHECK` entries and nested sub-config tables. Compiled-config code uses the same metadata plus `conf_total_size`, `conf_count`, `conf_value_count`, and `compiled_type` to allocate and populate `WT_CONF` objects.

## State and Persistence Behavior
Parser state is transient and references the input strings. `WT_CONFIG_ENTRY` base strings are effectively static defaults. `WT_CONFIG_MATCHES_DEFAULT` uses pointer containment inside the base config string as a fast default heuristic, which is conservative when callers explicitly restate a default.

## Dependencies and Integration Points
This header integrates the string parser, generated API config tables, compiled config system, and public `WT_CONFIG_PARSER` wrapper (`WT_CONFIG_PARSER_IMPL`). It depends on `WT_SESSION_IMPL`, `WT_CONFIG_ITEM`, generated choice symbols, and code generated by `dist/api_config.py`/`dist/flags.py`.

## Risks and Edge Cases
Many invariants are generated rather than hand-maintained. The parser assumes all keys are 7-bit ASCII for jump-table indexing. `WT_CONFIG_PRESERVE_QUOTES` relies on tokenizer rules that the byte after the item is addressable and quote-balanced. Pointer-based default detection can report "default" for text located in the base string even when semantics are more nuanced.

## Test Signals
Signals include parser unit tests for nesting/quoting/lists, API config validation tests, generated table regeneration checks, compiled vs uncompiled lookup comparison, and fuzzing malformed config strings. Tests around quoted values and default matching are especially relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/connection.h -->
# sources/storage-engines/wiredtiger/src/include/connection.h

## Purpose
`connection.h` defines process-wide and connection-wide internal state for WiredTiger. It is the central header for connection lifecycle, subsystem registries, background server state, shared caches, extension lists, data-handle/block lists, backup, disaggregated/tiered storage, diagnostics, and connection flags.

## Important APIs, Types, and Functions
`WT_PROCESS` stores global library state: process spinlock, connection queue, checksum function pointers, timestamp conversion settings, shared cache pool, and a modify pad byte hook. `WT_CONNECTION_IMPL` is the main connection object embedding the public `WT_CONNECTION` interface and holding locks, home/config/version state, session array, data handles, block/file handles, cache/eviction/transaction/log/checkpoint subsystems, extension APIs, compiled configuration arrays, server flags, diagnostics, and filesystem/key-provider interfaces.

Important subsystem structs include `WT_BACKGROUND_COMPACT`, `WT_LAYERED_TABLE_MANAGER`, `WT_DISAGGREGATED_STORAGE`, `WT_PAGE_HISTORY`, `WT_CONN_EXTENSIONS`, `WT_CONN_BACKUP`, `WT_CONN_PREFETCH`, `WT_CONN_CAPACITY`, `WT_CONN_STAT_LOG`, `WT_CONN_SWEEP`, and `WT_CONN_TIERED`. Macros manage dhandle/block insertion/removal, panic checks, hot-backup start, incremental backup flags, bucket-storage context, and close-abort debugging.

## Control Flow
Connection open initializes global/process linkage, locks, extension registries, sessions, config entries, and selected server subsystems. Runtime code routes through `WT_CONNECTION_IMPL`: sessions locate shared cache/txn/log metadata; schema and handle code use the dhandle queues and hash tables; background servers use their embedded sessions, condition variables, and thread IDs; reconfigure updates connection fields under dedicated locks. Close/shutdown tears down server flags, handles, extensions, backup state, and free-on-close allocations.

## State and Persistence Behavior
Most fields are in-memory coordination state, but many mirror durable or externally visible state: compatibility/recovery versions, checkpoint/turtle metadata versions, backup timestamps/file lists, log manager state, disaggregated checkpoint metadata LSNs/checksums/timestamps, database size, pending encryption keys for checkpoint persistence, and metadata operation queues. Atomic/shared fields coordinate readers and server threads without broad locking.

## Dependencies and Integration Points
The header touches nearly every WiredTiger subsystem: sessions, cache, eviction, transaction, logging, checkpoint, rollback-to-stable, block cache, tiered and disaggregated storage, extensions, file systems, encryption/key providers, statistics, background compaction, prefetch, live restore, and generated config. It also depends heavily on queue macros, spin/rw locks, atomics, and flag-generation conventions.

## Risks and Edge Cases
This is high-blast-radius state. Risks include lock-order mistakes across schema/metadata/checkpoint/dhandle locks, stale atomic state during reconfigure or shutdown, incorrect queue/hash count maintenance, server-thread lifetime races, and mismatched durable metadata around disaggregated checkpoints or key rotation. Macros such as `WT_CONN_DHANDLE_INSERT/REMOVE` assume specific locks and a `session` name in scope. Flags are split between regular and atomic fields, so using the wrong accessor can race.

## Test Signals
Relevant tests include connection open/close/reconfigure, recovery/compatibility, backup and incremental backup, background compaction, tiered/disaggregated storage, extension registration/termination, cache/eviction stress, logging/checkpoint shutdown, and diagnostic stress/failpoint suites. Thread sanitizer and long-running concurrency tests are valuable for this header's invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/connection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/crypt_header.h -->
# sources/storage-engines/wiredtiger/src/include/crypt_header.h

## Purpose
`crypt_header.h` defines the on-disk/in-buffer header used for encrypted key data. It standardizes a signature, version compatibility, payload size, checksum, and optional key-rotation timestamp.

## Important APIs, Types, and Functions
`WT_CRYPT_HEADER` contains `signature`, `version`, `compatible_version`, `header_size`, padding, `crypt_size`, `checksum`, and `timestamp`. Constants define the signature (`WT_CRYPT_HEADER_SIGNATURE`), current version, compatible version, and minimum bytes readers must be able to inspect. `__wt_crypt_header_byteswap` swaps multibyte fields on big-endian builds.

## Control Flow
Writers fill the header before encrypted key payloads. Readers inspect at least `WT_CRYPT_HEADER_MIN_SIZE`, verify signature/version compatibility, then use `header_size` to handle optional fields such as the timestamp. Big-endian systems call the inline byteswap before interpreting numeric fields in host order.

## State and Persistence Behavior
This structure is a durability boundary. `header_size` allows forward-compatible extension, `compatible_version` protects older readers, and `checksum` covers the encrypted payload. The timestamp persists key-rotation ordering when used.

## Dependencies and Integration Points
The header depends on fixed-width integer types and WiredTiger byte-swap helpers. It integrates with the key provider/encryptor path, disaggregated pending encryption-key checkpointing, and any metadata/page-log code that writes encrypted key blobs.

## Risks and Edge Cases
Incorrect endian handling or header-size validation can corrupt key interpretation. Fields beyond `WT_CRYPT_HEADER_MIN_SIZE` must remain optional for older readers. The byteswap helper currently swaps signature, payload size, and timestamp; code handling checksum/version fields must understand which are byte-sized or already treated appropriately.

## Test Signals
Tests should cover reading old version-1-compatible headers, current version headers with timestamps, checksum mismatch handling, short-header rejection, and big-endian serialization through dedicated byte-order tests or cross-platform CI.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/crypt_header.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/ctype_inline.h -->
# sources/storage-engines/wiredtiger/src/include/ctype_inline.h

## Purpose
`ctype_inline.h` wraps standard C character classification/conversion routines so WiredTiger passes unsigned bytes and gets predictable boolean behavior across platforms.

## Important APIs, Types, and Functions
Inline wrappers include `__wt_isalnum`, `__wt_isalpha`, `__wt_isascii`, `__wt_isdigit`, `__wt_isprint`, `__wt_isspace`, and `__wt_tolower`. `__wt_isprint` additionally rejects bytes >= `0x80` even if a platform locale would call them printable.

## Control Flow
Parser, dump, logging, and validation code call these wrappers instead of raw `ctype.h` functions. Each wrapper casts through `u_char` at the function boundary, preventing undefined behavior from negative `char` values.

## State and Persistence Behavior
There is no state or persistence. The durable effect is indirect: consistent parsing/printing rules for configuration, keys, diagnostics, and dumps across build environments.

## Dependencies and Integration Points
The file depends only on `<ctype.h>` and WiredTiger's `WT_INLINE`/`u_char` definitions. It is used anywhere byte-oriented parsing or printable checks must not depend on signed `char` behavior.

## Risks and Edge Cases
Locale-sensitive C library behavior can still affect `isalnum`/`isalpha`/`isspace` unless callers constrain input expectations. The explicit ASCII cap in `__wt_isprint` is intentional but means UTF-8 bytes are not treated as printable by this helper.

## Test Signals
Parser tests with high-bit bytes, signed-char platforms, and locale variation are useful. Unit tests should assert that bytes over `0x7f` are not printable and that digit/space checks match expected ASCII behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/ctype_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cursor.h -->
# sources/storage-engines/wiredtiger/src/include/cursor.h

## Purpose
`cursor.h` defines WiredTiger's internal cursor families and cursor state layout. It extends the public `WT_CURSOR` with btree, backup, metadata, table, index, history-store, statistics, version, layered-table, and other specialized cursor implementations.

## Important APIs, Types, and Functions
`CUR2S` maps any cursor to its internal session. `WT_CURSOR_STATIC_INIT` initializes static public cursor vtables. `WT_CURSOR_BTREE` is the main storage cursor, tracking dhandle, current page/ref/slot, insert-list search state, row/column iteration state, cached keys/values, checkpoint transaction metadata, random cursor state, prepare-conflict retry state, and diagnostic key-order fields.

Specialized structs include `WT_CURSOR_BACKUP` for full/incremental backup traversal, `WT_CURSOR_HS` for history-store access, `WT_CURSOR_INDEX` and `WT_CURSOR_TABLE` for schema projection over child cursors, `WT_CURSOR_METADATA`, `WT_CURSOR_STAT`, `WT_CURSOR_VERSION`, and `WT_CURSOR_LAYERED`. Macros identify primary table cursors, recno cursors, raw-output modes, cursor bounds, and positioned btree cursors.

## Control Flow
Public cursor API calls enter through the function pointers embedded in `WT_CURSOR`. Btree cursors search pages and insert lists, cache enough state for next/prev/update/remove, and expose keys/values through buffers owned by the cursor or page. Table/index cursors project values through column-group/index child cursors. Backup and statistics cursors iterate over synthetic lists rather than ordinary btree records. Layered cursors switch between ingest and stable component cursors based on read state.

## State and Persistence Behavior
Cursors are in-memory handles, but they pin durable resources: data handles, pages, checkpoint transactions, history-store checkpoint handles, backup file lists, and incremental backup bitmaps. Cursor flags record API-visible state such as key/value set, bounds, raw mode, active positioning, and cursor-family-specific behavior.

## Dependencies and Integration Points
This header integrates sessions, btrees, pages/refs, insert/update structures, schema tables/indexes, backup metadata, statistics arrays, history store, layered tables, checkpoint transactions, and random utilities. It also relies on generated flag definitions and queue/list conventions.

## Risks and Edge Cases
Cursor state is dense and performance-sensitive. Risks include stale page references after reset, failing to copy page-owned keys before movement, inconsistent active cursor counts, prepare-conflict restart errors, row-store iteration slot mistakes, and bounds checks that do not match positioning state. Backup/incremental cursor flags must stay synchronized with connection backup state.

## Test Signals
Signals include cursor API suites for search/next/prev/update/remove/modify/reserve, bounds tests, raw and dump cursor tests, checkpoint cursor consistency, backup/incremental backup tests, history-store/version cursor tests, random cursor tests, and diagnostic key-order assertions under stress.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cursor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cursor_inline.h -->
# sources/storage-engines/wiredtiger/src/include/cursor_inline.h

## Purpose
`cursor_inline.h` implements hot cursor lifecycle and key/value helper routines shared by multiple cursor `.c` files. It handles cursor activation, reset, key/value ownership, dhandle use counts, table/index value projection, and row-store key fast paths.

## Important APIs, Types, and Functions
`__wt_curhs_get_btree` and `__wt_curhs_get_cbt` unwrap history-store cursors. `__cursor_set_recno`, `__cursor_checkkey`, `__cursor_checkvalue`, `__wt_cursor_localkey`, `__cursor_localvalue`, `__cursor_needkey`, and `__cursor_needvalue` maintain public cursor key/value state. `__cursor_enter`/`__cursor_leave`, `__cursor_reset`, and `__wt_cursor_func_init` implement the main active cursor lifecycle.

Other helpers reset bounds, release debug key/value copies, increment/decrement dhandle session use, return btree key/value pairs, free cached cursor memory, merge projected table/index values, and return row-store slot keys. `__wt_tombstone` plus `__wt_clayered_deleted` encode layered-table deletion markers.

## Control Flow
Before most btree operations, `__wt_cursor_func_init` optionally resets the old position, clears stale insert-stack state, checks cache pressure, activates the cursor, and marks transaction cursor activity. Reset clears position flags, decrements active cursor count, releases read-committed snapshots when no cursors remain, marks delete-heavy pages for eviction/reconciliation, and releases page refs. Key/value helpers copy tree-owned memory into cursor-owned buffers when the application needs stable access across movement.

## State and Persistence Behavior
The helpers mutate cursor flags, buffers, page refs, session active cursor counts, transaction read state, dhandle `session_inuse`, and statistics. They do not directly persist data, but reset can dirty/evict pages to clean obsolete tombstones, and cursor initialization participates in transaction visibility.

## Dependencies and Integration Points
The file depends on eviction, transaction, buffer, schema projection, page release/dirtying, row key unpacking, history-store cursors, layered cursors, and statistics macros. It is included by cursor implementations that need low-overhead access to these shared operations.

## Risks and Edge Cases
Reset ordering is subtle: snapshots are released before page refs because page release can trigger eviction. Dhandle decrement checks `timeofdeath` before subtracting because the handle may be freed afterward. Copy-on-need must correctly distinguish internal page-owned data from cursor-owned buffers. The layered tombstone byte sequence can collide with application values, causing extra copy/check work.

## Test Signals
Cursor reset/close tests, read-committed snapshot release tests, forced eviction/debug reset tests, cursor cache reuse tests, table/index projection tests, prepare-conflict iteration tests, and layered-table deletion tests all exercise this header's behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cursor_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/dhandle.h -->
# sources/storage-engines/wiredtiger/src/include/dhandle.h

## Purpose
`dhandle.h` defines WiredTiger data handles: named, lockable references to btrees, tables, tiered objects, metadata, and other data-source handles. It also provides macros for safely swapping a session's current handle and tracking handle lifecycle/debug state.

## Important APIs, Types, and Functions
Context macros include `WT_WITH_DHANDLE`, `WT_WITH_BTREE`, `WT_WITHOUT_DHANDLE`, and `WT_SAVE_DHANDLE`. `WT_DHANDLE_CLEAR` clears `session->dhandle` while recording source location in a circular `WT_DHANDLE_CLEAR_LOG`. `WT_DHANDLE_ACQUIRE`, `WT_DHANDLE_RELEASE`, and `WT_DHANDLE_NEXT` manage reference counts while walking handle queues.

`WT_DATA_HANDLE` contains locking (`rwlock`, `close_lock`), queue/hash links, URI/checkpoint identity, metadata config and hashes, reference/use counts, exclusive-session fields, data-source pointer, generic handle pointer, type, stats arrays, lifecycle flags, timestamp assertion flags, lock flags, and advisory eviction flags.

## Control Flow
Schema/session code sets `session->dhandle` before operating on an object and restores it afterward using the context macros. The connection keeps handles in both list and hash queues; walkers use `WT_DHANDLE_NEXT` under handle-list locks to acquire/release references as they progress. Exclusive operations use the handle rwlock and flags to prevent concurrent opens/closes.

## State and Persistence Behavior
The handle itself is in-memory but mirrors durable object identity and metadata configuration. `meta_base`, hashes, checkpoint names/orders, and timestamp flags describe persisted metadata state. `references`, `session_inuse`, `timeofdeath`, and lifecycle flags drive when handles can be swept, reopened, discarded, or marked dead.

## Dependencies and Integration Points
This header integrates with sessions, btrees, metadata cursors, connection dhandle queues, tiered work units, cached cursors, statistics, schema operations, and checkpoint/open/close paths. It depends on atomic helpers, queue macros, and lock primitives.

## Risks and Edge Cases
Reference/use-count ordering is critical because handles may be freed after the final decrement. `WT_DHANDLE_INACTIVE` and `WT_DHANDLE_CAN_REOPEN` encode subtle flag combinations that affect handle reuse. Macros assume appropriate locks are already held; misuse can corrupt connection queues or race with sweep/checkpoint. The clear log is debug-only aid and should not be treated as synchronization.

## Test Signals
Useful signals are schema open/close/drop/rename tests, handle sweep tests, checkpoint while closing handles, cached cursor lifetime tests, exclusive access tests, tiered handle tests, and sanitizer/thread-sanitizer coverage for reference counting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/dhandle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/dlh.h -->
# sources/storage-engines/wiredtiger/src/include/dlh.h

## Purpose
`dlh.h` defines the small connection-owned record used to track dynamically loaded extension libraries.

## Important APIs, Types, and Functions
`WT_DLH` stores a queue link, platform dynamic-library `handle`, library `name`, and optional `terminate(WT_CONNECTION *)` callback. There are no functions in this header.

## Control Flow
Extension loading code allocates one `WT_DLH` per opened library, links it into `WT_CONNECTION_IMPL::dlhqh`, stores the `dlopen`/platform handle, resolves callbacks, and later walks the queue during connection close to call `terminate` and unload the library.

## State and Persistence Behavior
The state is process-local and lasts for the connection lifetime. It does not persist to disk, but loaded extension names and termination callbacks affect connection shutdown and resource cleanup.

## Dependencies and Integration Points
It depends on queue macros and the public `WT_CONNECTION` type. It integrates with extension loading, named collator/compressor/encryptor/storage-source registration, and connection close cleanup.

## Risks and Edge Cases
Shutdown ordering matters: callbacks may depend on connection subsystems still being valid. Handles must not be unloaded while registered extension objects are still reachable. A missing or failing terminate callback needs to be handled by extension-management code outside this header.

## Test Signals
Extension load/unload tests, error-path tests for partially loaded extensions, and leak checks at connection close are the main signals. Mock extensions with terminate callbacks are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/dlh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/error.h -->
# sources/storage-engines/wiredtiger/src/include/error.h

## Purpose
`error.h` centralizes WiredTiger error propagation, diagnostic assertions, panic handling, branch prediction hints, and optional error logging hooks. It provides the macros that make the codebase's `ret`/`err:` cleanup style consistent.

## Important APIs, Types, and Functions
Logging/reporting wrappers include `__wt_err`, `__wt_errx`, `__wt_panic`, and `__wt_set_return`, which pass function and line metadata. `WT_ERR*` macros set `ret` and jump to `err`; `WT_RET*` macros return immediately; `WT_TRET*` macros preserve cleanup errors only when they should override an existing return. `WT_ERROR_LOG_ADD` and helpers integrate optional error-log recording.

Diagnostic macros include `WT_DIAGNOSTIC_YIELD`, `WT_ASSERT`, `WT_ASSERT_OPTIONAL`, `WT_ASSERT_ALWAYS`, `WT_ERR_ASSERT`, `WT_RET_ASSERT`, `WT_RET_PANIC_ASSERT`, and `WT_PREFETCH_ASSERT`. `TRIGGER_ABORT` either aborts or records assertion hits for unit-test assertion builds. `WT_LIKELY`/`WT_UNLIKELY` wrap compiler branch prediction.

## Control Flow
Most functions declare `WT_DECL_RET`, use `WT_ERR(...)` for fallible operations, and perform cleanup at `err:` with `WT_TRET(...)` for secondary failures. Immediate-return functions use `WT_RET(...)`. Assertion macros either compile away, abort, return normal errors, or return panic depending on build mode and runtime diagnostic categories.

## State and Persistence Behavior
The macros update session last-error state, optional error logs, statistics in some specialized paths, and connection panic state through panic functions. They do not persist data, but they control whether operations continue, return recoverable errors, or abort the process.

## Dependencies and Integration Points
This file is included broadly across WiredTiger. It depends on session/connection error functions, optional `HAVE_ERROR_LOG` and `HAVE_UNITTEST_ASSERTS` builds, diagnostic flags from `connection.h`, verbose categories, and statistics macros for prefetch assertions.

## Risks and Edge Cases
Macro semantics depend on local names such as `ret`, `err`, and `session`, so misuse can compile incorrectly or alter control flow unexpectedly. `WT_TRET` precedence intentionally lets `WT_PANIC` and selected cleanup errors override prior returns; changing it can hide data-corruption signals. Assertions vary significantly by build and runtime diagnostic settings, so tests must cover both aborting and non-aborting modes.

## Test Signals
Error-path unit tests, fault-injection tests, assertion unit tests with `HAVE_UNITTEST_ASSERTS`, panic/corruption tests, and cleanup paths with multiple failures validate this header. Static analysis can catch macros used without required local variables.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/error.h -->
