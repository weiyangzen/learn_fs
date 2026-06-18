# Research: subset-b-008773

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/json.c -->
# sources/storage-engines/sqlite/src/json.c

## Purpose

`json.c` implements SQLite's built-in JSON subsystem when `SQLITE_OMIT_JSON` is not defined. It provides scalar functions (`json`, `jsonb`, `json_array`, `json_extract`, `json_set`, `json_patch`, `json_valid`, `json_error_position`, etc.), aggregate/window functions (`json_group_array`, `json_group_object` and JSONB variants), the `->` and `->>` operators, and the `json_each`/`json_tree` plus `jsonb_each`/`jsonb_tree` table-valued functions.

The file's central design is to normalize inputs into SQLite's internal JSONB representation (`JsonParse.aBlob`) and then operate on that binary representation for lookup, mutation, rendering, validation, and traversal. Text JSON remains the public canonical output format for `json_*` functions, while `jsonb_*` functions return BLOB JSONB. JSON5-style input extensions are accepted and canonicalized to strict RFC-8259 JSON text on text output.

## Important APIs, Types, and Functions

- `JsonParse` owns or references parsed JSONB bytes, original text, parse/cache metadata, edit state (`eEdit`, `delta`, `aIns`, `nIns`, `iLabel`), error flags, depth, and DB allocator context.
- `JsonString` is the output accumulator used for JSON text and intermediate strings. It starts with static storage and grows into reference-counted strings.
- `JsonCache` stores up to four `JsonParse` entries in SQLite auxdata, keyed by JSON argument text, so repeated function calls within a statement can avoid reparsing.
- JSONB type codes `JSONB_NULL` through `JSONB_OBJECT` encode primitive, text, array, and object nodes. Payload sizes live in the high nibble or in 1/2/4/8-byte big-endian size fields.
- Parser and encoder functions include `jsonTranslateTextToBlob`, `jsonConvertTextToBlob`, `jsonArgIsJsonb`, `jsonFunctionArgToBlob`, `jsonBlobAppendNode`, `jsonbPayloadSize`, and `jsonbValidityCheck`.
- Renderer functions include `jsonTranslateBlobToText`, `jsonTranslateBlobToPrettyText`, `jsonReturnFromBlob`, `jsonReturnTextJsonFromBlob`, `jsonReturnParse`, and `jsonReturnString`.
- Path lookup and edit are centered on `jsonLookupStep`, supported by `jsonLabelCompare`, `jsonCreateEditSubstructure`, `jsonBlobEdit`, `jsonAfterEditSizeAdjust`, and `jsonInsertIntoBlob`.
- Scalar SQL entry points include `jsonQuoteFunc`, `jsonArrayFunc`, `jsonArrayLengthFunc`, `jsonExtractFunc`, `jsonPatchFunc`, `jsonObjectFunc`, `jsonRemoveFunc`, `jsonReplaceFunc`, `jsonSetFunc`, `jsonTypeFunc`, `jsonPrettyFunc`, `jsonValidFunc`, and `jsonErrorFunc`.
- Aggregate/window entry points are `jsonArrayStep`, `jsonArrayCompute`, `jsonArrayValue`, `jsonArrayFinal`, `jsonObjectStep`, `jsonObjectCompute`, `jsonObjectValue`, `jsonObjectFinal`, and optionally `jsonGroupInverse`.
- Virtual table support uses `JsonEachConnection`, `JsonEachCursor`, `JsonParent`, `jsonEachConnect`, `jsonEachBestIndex`, `jsonEachFilter`, `jsonEachNext`, `jsonEachColumn`, and `jsonEachModule`.
- Public registration is through `sqlite3RegisterJsonFunctions()` and, when virtual tables are enabled, `sqlite3JsonVtabRegister()`.

## Control Flow

For scalar functions, SQL arguments enter through function-specific wrappers. Most functions call `jsonParseFuncArg()` for the primary JSON input. That routine checks NULL handling, searches the auxdata cache for text inputs, recognizes JSONB BLOBs via `jsonArgIsJsonb()`, falls back to parsing text with `jsonConvertTextToBlob()`, and caches immutable parses. Editable operations request `JSON_EDITABLE`, causing cached parses to be copied into writable storage before mutation.

Text parsing is recursive descent in `jsonTranslateTextToBlob()`. It recognizes objects, arrays, strings, numbers, booleans, nulls, JSON5 whitespace/comments, single-quoted strings, identifier labels, hex numbers, `Infinity`, and `NaN` variants. The parser appends JSONB nodes into `aBlob`, backpatches array/object payload sizes after children are parsed, tracks non-standard JSON features in `hasNonstd`, and enforces `JSON_MAX_DEPTH`.

JSONB inputs take a faster path. `jsonArgIsJsonb()` verifies the outer element's type and size and performs full validation for small payloads that could be confused with text JSON cast to BLOB. Strict validation is delegated to `jsonbValidityCheck()`, which recursively checks type-specific payload syntax, object label/value pairing, and nesting limits.

Extraction and mutation use `jsonLookupStep()`. Path segments are parsed as object labels (`.name`, `."quoted"`) or array indexes (`[N]`, `[#]`, `[#-N]`). On exact matches the routine recurses into child nodes. With an edit mode set, it deletes, replaces, inserts, sets, or array-inserts in-place by calling `jsonBlobEdit()`. Missing paths for insert/set can synthesize intermediate object or array substructures through `jsonCreateEditSubstructure()`.

Rendering reverses JSONB into SQL results. Primitive nodes can return SQL NULL/integer/real/text from `jsonReturnFromBlob()`. Arrays and objects render to JSON text through `jsonTranslateBlobToText()` unless JSONB output is requested. `json_pretty` uses `JsonPretty` and `jsonTranslateBlobToPrettyText()` to add indentation. Generated text JSON is tagged with `JSON_SUBTYPE` where appropriate so nested JSON builders know when text arguments are already JSON.

`json_patch` implements RFC-7396 merge patch in `jsonMergePatch()`. It recursively updates a writable target JSONB object, deletes members whose patch value is null, replaces non-object targets for object patches with an empty object shell, and tracks edit deltas so parent payload sizes are repaired.

Aggregates append JSON text incrementally in a `JsonString` stored in aggregate context. The JSONB aggregate variants convert the final accumulated text to JSONB. Window inverse support removes the first serialized aggregate element by scanning over strings and nested containers to find the top-level comma.

The virtual table flow begins with `jsonEachBestIndex()` requiring a usable equality constraint on the hidden `json` column and optionally one on `root`. `jsonEachFilter()` parses JSON/JSONB, resolves the root path, initializes cursor bounds, and chooses either one-level (`json_each`) or recursive (`json_tree`) traversal. `jsonEachNext()` advances by payload-size skipping and maintains a parent stack for recursive paths. `jsonEachColumn()` materializes `key`, `value`, `type`, `atom`, `id`, `parent`, `fullkey`, `path`, and hidden columns.

## State and Persistence Behavior

This file does not persist JSON state to database pages by itself; it computes SQL function results and virtual table rows. JSONB BLOBs returned by `jsonb_*` functions can be stored by callers and later re-enter these routines.

Per-statement parse state may be cached in SQLite auxdata as `JsonCache`, with reference-counted `JsonParse` and `zJson` buffers. Cached parse objects are read-only and are freed when auxdata is destroyed. Editable calls copy cached JSONB before mutation.

Memory allocation follows SQLite DB/context allocators (`sqlite3DbMalloc*`, `sqlite3DbFree`, `sqlite3RCStr*`) and reports OOM through SQLite result APIs. `JsonString` and `JsonParse` carry explicit OOM/error flags to avoid using partially built outputs. Mutation state in `JsonParse.delta` is transient but critical for repairing JSONB parent sizes after edits.

## Dependencies and Integration Points

`json.c` includes `sqliteInt.h` and depends on SQLite internals for memory management, value/result APIs, function registration macros (`JFUNCTION`, `WAGGREGATE`), subtype propagation, UTF-8 helpers, path globbing, printf/str accumulators, virtual table APIs, and test controls.

`sqlite3RegisterJsonFunctions()` is called from `src/func.c` during built-in function registration. `sqlite3JsonVtabRegister()` is declared in `sqliteInt.h` and reached from module creation paths in `src/build.c` for the JSON table-valued functions. Build files include `json.o`, and the manifest/test tree includes focused JSON tests such as `test/json101.test` through `test/json109.test`, `test/json501.test`, `test/json502.test`, and `test/jsonb01.test`.

Compile-time gates shape behavior: `SQLITE_OMIT_JSON` removes the subsystem, `SQLITE_OMIT_VIRTUALTABLE` removes `json_each`/`json_tree`, `SQLITE_OMIT_WINDOWFUNC` removes inverse aggregate behavior, `SQLITE_DEBUG` enables `json_parse` and self-check/debug printing, `SQLITE_JSON_MAX_DEPTH` customizes nesting depth, `SQLITE_LEGACY_JSON_VALID` restores old NULL handling for `json_valid`, and `SQLITE_BUG_COMPATIBLE_20250510` restores an older JSON5 `\0` escape bug.

## Risks and Edge Cases

The largest risk area is malformed or ambiguous JSONB. Some paths intentionally perform superficial validation for performance, so downstream routines must guard each `jsonbPayloadSize()` and type-specific traversal. The code acknowledges that malformed JSONB can sometimes produce an error and sometimes incorrect JSON, so consumers should use strict `json_valid(...,8)` when they require full validation.

Depth handling is security-sensitive because parsing and rendering recurse; the code enforces `JSON_MAX_DEPTH` but edits and virtual table traversal also need correct depth accounting. Payload-size backpatching and `delta` propagation are another high-risk area because a missed parent size adjustment corrupts the JSONB structure after edits.

Compatibility behavior is deliberate but surprising: non-JSONB BLOB inputs may be interpreted as text JSON for historical compatibility, JSON5 extensions are accepted but canonicalized, `json_valid()` defaults to strict canonical text unless flags are supplied, and `->`/`->>` accept abbreviated PostgreSQL-style paths. Small JSONB validation has special rules to avoid false positives for text JSON cast to BLOB.

Aggregate inverse logic edits serialized JSON text by scanning for top-level separators; string escaping and nested bracket tracking are therefore important regression points. Object aggregate NULL-name handling uses `@` sentinels that are removed later, which is subtle and should be tested with window frames and NULL labels.

Virtual table risks include planner contracts around hidden-column constraints, root-path path length/key derivation, malformed input after partial cursor initialization, and parent stack growth. Since `id` values are byte offsets into JSONB rather than stable logical IDs, tests should avoid assuming portability beyond documented behavior.

## Test Signals

Strong test signals are the JSON TCL tests in `sources/storage-engines/sqlite/test/json101.test` through `json109.test`, JSON5 coverage in `json501.test`/`json502.test`, JSONB coverage in `jsonb01.test`, join tests that exercise `json_each`, and `test/json/json-speed-check.sh` for performance-sensitive parser/JSONB behavior. `test/json104.test` specifically maps to `json_patch` and edit/extract semantics.

Useful focused tests for changes in this file include: malformed JSONB validation flags, BLOB-as-text compatibility, JSON5 whitespace/comments/numeric forms, Unicode escapes and surrogate pairs, object label comparison with escaped labels, deep nesting at `JSON_MAX_DEPTH`, all edit operations with size-changing replacements, multiple path extraction, JSONB/text subtype propagation through nested function calls, aggregate window inverse with nested arrays/objects, and `json_each`/`json_tree` with root constraints and malformed roots.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/json.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/legacy.c -->
# sources/storage-engines/sqlite/src/legacy.c

## Purpose

`legacy.c` implements `sqlite3_exec()`, SQLite's legacy convenience API for executing one or more semicolon-separated SQL statements with an optional row callback. It is intentionally thin over the prepared-statement engine: prepare each statement, step it to completion, invoke the caller's callback for result rows, finalize, then continue with the remaining SQL tail.

## Important APIs, Types, and Functions

- `sqlite3_exec(sqlite3 *db, const char *zSql, sqlite3_callback xCallback, void *pArg, char **pzErrMsg)` is the only function in this file.
- It uses `sqlite3_prepare_v2()` to compile each statement and `sqlite3_step()` to execute it.
- It uses `sqlite3_column_count()`, `sqlite3_column_name()`, `sqlite3_column_text()`, and `sqlite3_column_type()` to prepare callback metadata and row values.
- It finalizes statements with `sqlite3VdbeFinalize()` rather than the public wrapper, because this is core code operating on the internal `Vdbe`.
- It reports connection-level status through `sqlite3Error()`, `sqlite3ApiExit()`, `sqlite3_errmsg()`, and `sqlite3DbStrDup()`.

## Control Flow

The routine first validates the database handle with `sqlite3SafetyCheckOk()`, treats a NULL SQL string as an empty string, enters the database mutex, and clears the connection error state. It then loops while the current SQL pointer is non-empty and no error has occurred.

Each iteration prepares the next statement and receives `zLeftover`, the tail after that statement. If preparation returns no statement, the input was whitespace or a comment, so it advances to `zLeftover`. Otherwise it steps the statement until completion.

Callback setup is lazy. On the first result row, or on `SQLITE_DONE` when `SQLITE_NullCallback` is set and no row has been seen, it allocates one array large enough for column names plus values and a trailing NULL. Column names are filled once. For each `SQLITE_ROW`, it fills the value half with text pointers and calls `xCallback(pArg, nCol, azVals, azCols)`.

If the callback returns non-zero, `sqlite3_exec()` aborts the statement, sets `SQLITE_ABORT`, finalizes immediately, and exits. When stepping returns anything other than `SQLITE_ROW`, it finalizes, advances to the leftover SQL, skips whitespace, frees callback column storage, and proceeds to the next statement.

On exit, any active statement and column storage are finalized/freed. The return code passes through `sqlite3ApiExit()`. If the final code is not `SQLITE_OK` and `pzErrMsg` is supplied, it duplicates `sqlite3_errmsg(db)` using the non-connection allocator so the caller can free it. On success, `*pzErrMsg` is set to NULL.

## State and Persistence Behavior

`sqlite3_exec()` does not add persistent state beyond whatever the SQL statements themselves do. It temporarily holds the connection mutex, temporarily allocates callback metadata from the database allocator, and may set the connection error state. Statements are finalized before return unless a severe internal path interrupts normal flow.

The callback receives pointers owned by the current statement for values and names; they are not persistent beyond the callback call/statement lifetime. When a non-NULL, non-text column cannot provide text, the routine treats that as OOM by calling `sqlite3OomFault(db)`.

## Dependencies and Integration Points

This file includes `sqliteInt.h` and depends on the VDBE, prepare, column, mutex, allocator, error, and safety-check internals. The extension API table in `loadext.c` exports `sqlite3_exec` to loadable extensions. Many internal and test utilities call this convenience API when they do not need manual statement control; examples appear in `analyze.c`, `table.c`, `prepare.c`, `vdbe.c`, the shell, TCL bindings, and tests.

The callback contract is part of the public C API, and this implementation preserves documented behavior such as aborting with `SQLITE_ABORT` when the callback returns non-zero and invoking the callback once with NULL values for empty result sets when `SQLITE_NullCallback` is enabled.

## Risks and Edge Cases

The main risk is callback lifetime and reentrancy. The function holds the connection mutex while invoking user code, so callbacks that interact with the same connection must rely on SQLite's supported mutex/reentrancy semantics. Callback-provided pointers must not be retained by callers.

Error handling must preserve the first meaningful failing code while still finalizing statements. OOM can happen while allocating the column-name/value array or duplicating the final error string; the latter converts the return to `SQLITE_NOMEM_BKPT`.

Multi-statement parsing depends on `sqlite3_prepare_v2()` setting `zLeftover` correctly. Whitespace/comment-only input must not loop forever. The `SQLITE_NullCallback` path is subtle because it can invoke the callback on `SQLITE_DONE` without row values.

## Test Signals

Relevant test signals include public C API tests in `src/test1.c` wrappers (`sqlite3_exec`, `sqlite3_exec_nr`, hex/printf variants), `test/capi3d.test` callback/reentrancy cases, bad UTF/OOM tests, and any test using `sqlite3_get_table()` because `table.c` builds on `sqlite3_exec()`.

Focused regression tests should cover multiple statements, whitespace/comment-only SQL, callback abort, NULL `zSql`, NULL callback, `SQLITE_NullCallback`, OOM during callback metadata allocation, error message allocation failure, and statements that produce zero columns versus result rows.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/loadext.c -->
# sources/storage-engines/sqlite/src/loadext.c

## Purpose

`loadext.c` implements SQLite's loadable-extension support. It builds the `sqlite3_api_routines` thunk passed to extensions, implements dynamic shared-library loading for `sqlite3_load_extension()`, tracks per-connection dynamic-library handles for cleanup, exposes `sqlite3_enable_load_extension()`, and manages the process-global auto-extension list used to initialize statically linked extensions on every new connection.

When `SQLITE_OMIT_LOAD_EXTENSION` is defined, dynamic loading code is omitted, but auto-extension registration/loading still exists and passes a NULL API thunk to auto extensions.

## Important APIs, Types, and Functions

- `sqlite3Apis` is the ordered `sqlite3_api_routines` table exported to extensions. Omitted SQLite features map corresponding entries to NULL, and newer APIs are appended to preserve ABI compatibility.
- `sqlite3LoadExtension()` is the internal dynamic loader. It opens the shared library, locates the entry point, calls it, and records the library handle.
- `sqlite3_load_extension()` is the public mutex/API-exit wrapper around `sqlite3LoadExtension()`.
- `sqlite3CloseExtensions()` closes all dynamic libraries associated with a database connection.
- `sqlite3_enable_load_extension()` toggles `SQLITE_LoadExtension` and `SQLITE_LoadExtFunc` flags on the connection.
- `sqlite3_auto_extension()`, `sqlite3_cancel_auto_extension()`, `sqlite3_reset_auto_extension()`, and `sqlite3AutoLoadExtensions()` manage the global auto-extension list.
- `sqlite3AutoExtList` stores `nExt` and a realloc-grown array of extension init function pointers. `wsdAutoext` abstracts writable-static-data versus `SQLITE_OMIT_WSD` builds.

## Control Flow

At the top of the file, `SQLITE_CORE` is forced before including `sqlite3ext.h` so the core sees real API symbols instead of extension macro remaps. Conditional defines replace unavailable API functions with NULL table entries when features such as UTF-16, authorizers, virtual tables, WAL, deserialize, carray, or deprecated APIs are omitted.

Dynamic loading starts in `sqlite3_load_extension()`, which enters the connection mutex, calls `sqlite3LoadExtension()`, normalizes the result through `sqlite3ApiExit()`, and leaves the mutex. The internal loader first checks `SQLITE_LoadExtension`; loading is disabled by default for security. It rejects oversized paths and empty filenames, tries to open the file as provided, and on Unix/Windows also retries with platform suffixes (`.so`, `.dylib`, or `.dll`).

After opening a library through the VFS dynamic-loading methods, it resolves the requested entry point or the default `sqlite3_extension_init`. If the default is missing and no entry point was specified, it derives `sqlite3_X_init` from the filename by taking the basename, skipping a leading `lib`, lowercasing ASCII alphabetics up to the first dot, and retrying with digits included on the second pass.

The entry point is called as `xInit(db, &zErrmsg, &sqlite3Apis)`. `SQLITE_OK_LOAD_PERMANENTLY` is treated as success without recording the handle for close. Any other non-zero code becomes `SQLITE_ERROR` with an initialization message and the library handle is closed. On success, the handle is appended to `db->aExtension`, reallocating and copying the existing handle array, so `sqlite3CloseExtensions()` can close each handle when the connection closes.

`sqlite3_enable_load_extension()` is a simple mutex-protected flag toggle. Enabling sets both dynamic loading and the SQL `load_extension()` function flag; disabling clears both. API armor validates the DB handle when enabled.

Auto-extension registration calls `sqlite3_initialize()` unless autoinit is omitted, locks `SQLITE_MUTEX_STATIC_MAIN`, avoids duplicate function pointers, reallocates the global array, and appends the init pointer. Cancellation swaps the last entry into the removed slot. Reset frees the global array. `sqlite3AutoLoadExtensions()` early-outs if no entries exist, then repeatedly locks just long enough to read the next pointer, unlocks, and invokes the extension initializer against the connection. This allows callbacks to modify the auto-extension list without holding the global mutex across user code.

## State and Persistence Behavior

Per-connection dynamic extension state is stored in `db->aExtension` and `db->nExtension`. It persists until connection close, where `sqlite3CloseExtensions()` must run while holding `db->mutex` and calls `sqlite3OsDlClose()` for each handle.

Process-global auto-extension state lives in `sqlite3Autoext` or the writable-static-data substitute. It persists across connections until explicitly reset and is protected by the static main mutex. The array stores function pointers only; it does not own extension-specific resources beyond the pointer list allocation.

The API routine table is static const state. It encodes build capabilities at compile time; extensions must check SQLite version and NULL entries before using optional APIs.

## Dependencies and Integration Points

This file includes `sqlite3ext.h` and `sqliteInt.h`. It integrates with the VFS dynamic loader (`sqlite3OsDlOpen`, `sqlite3OsDlSym`, `sqlite3OsDlError`, `sqlite3OsDlClose`), connection flags, mutexes, SQLite allocators, initialization, and error reporting.

The SQL `load_extension()` function is guarded elsewhere by `SQLITE_LoadExtFunc` (notably in `func.c`), while this file's C API gate uses `SQLITE_LoadExtension`. Connection close calls `sqlite3CloseExtensions()` from `main.c`, and opening a DB invokes `sqlite3AutoLoadExtensions()` from `main.c`. Test-facing wrappers for loading and enabling extensions appear in `src/test1.c`; `src/test_loadext.c` is a specific test extension.

The ordered `sqlite3Apis` table is ABI-sensitive. New API entries are appended by version blocks, including current entries through `sqlite3_str_free`, optional carray bindings, and `sqlite3_incomplete`. Changing order would break loadable extensions compiled against `sqlite3ext.h`.

## Risks and Edge Cases

Dynamic loading is security-sensitive. Loading is intentionally disabled by default, empty filenames are rejected to avoid linking the running application, and path length is bounded to avoid platform `dlopen()` issues. Any change to flag gating can expose the SQL `load_extension()` function or the C loader unexpectedly.

Entry-point derivation is compatibility-sensitive and platform-sensitive. Filename parsing must handle `/` and `\` on Windows, a leading `lib`, case folding, dots, and digits on the second attempt. Error reporting must include both SQLite's message and VFS dynamic-loader error without leaking allocated buffers.

Resource ownership is subtle after `xInit()`. `SQLITE_OK_LOAD_PERMANENTLY` intentionally leaves the handle open without adding it to the close list. Normal success must add the handle to `db->aExtension`; failure must close it. If appending the handle array fails after successful initialization, the current code returns NOMEM without closing the just-loaded handle, which is consistent with an extension that may have registered state but is a resource-retention risk to keep in mind.

Auto-extension callbacks run outside the global mutex, so the loop must tolerate registration/cancellation/reset during loading. It reads the list one entry at a time under lock and stops on errors by setting the connection error message. Duplicate registration is ignored. API armor affects NULL pointer behavior for registration/cancellation.

The API thunk contains many NULLs under feature-omit macros; extensions that fail to check optional pointers can crash. Table order and conditional entries are therefore high-risk for refactors.

## Test Signals

Relevant tests include `src/test_loadext.c`, TCL wrappers in `src/test1.c` for `sqlite3_load_extension` and `sqlite3_enable_load_extension`, shell `.load` behavior in `src/shell.c.in`, and extension/auto-extension usage such as `test_multiplex.c` and shell auto-extension reset checks. Build variants omitting UTF-16, virtual tables, WAL, deprecated APIs, load extension, and writable static data are important because they change API table entries and code paths.

Focused regression tests should cover disabled-by-default loading, enabling/disabling both C and SQL loaders, missing files and suffix retries, explicit and derived entry points, no-entry error messages, extension init failures and `zErrmsg`, `SQLITE_OK_LOAD_PERMANENTLY`, close-time handle cleanup, duplicate auto-extension registration, cancellation, reset, auto-extension init failure, and concurrent auto-extension list changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/loadext.c -->
