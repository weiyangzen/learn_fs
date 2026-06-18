# Research: subset-b-008793

Grouped research report for the SQLite source files assigned to `subset-b-008793`.
Each source section is delimited for reconciliation into its source-tree-aligned
per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/sqliteLimit.h -->
# Research: sources/storage-engines/sqlite/src/sqliteLimit.h

## Purpose

`sqliteLimit.h` centralizes SQLite's compile-time resource limits and default
capacity policy. It is not executable code; it is a configuration contract used
by parser, VDBE, pager, btree, function, trigger, page-cache, and public limit
APIs to keep resource use bounded and file-format assumptions consistent.

The file provides default values when the build has not supplied
`-DSQLITE_MAX_*` or related options, and it enforces a few hard caps with
preprocessor errors or normalization. These constants shape both security
posture and compatibility: lowering them can constrain hostile SQL inputs,
while raising some values is impossible because internal fields, varint
encodings, page layout, or 32-bit signed lengths would no longer be safe.

## Important Limits And Macros

- `SQLITE_MAX_LENGTH` defaults to 1,000,000,000 bytes and bounds TEXT, BLOB,
  row, and index-record sizes. `SQLITE_MIN_LENGTH` records the minimum runtime
  length-limit value accepted elsewhere.
- `SQLITE_MAX_ALLOCATION_SIZE` caps one `sqlite3_malloc()` or
  `sqlite3_realloc()` request. It defaults to `2147483391`, slightly below
  2 GiB, and is rejected above that value to preserve a 256-byte overflow
  margin.
- `SQLITE_MAX_COLUMN` defaults to 2000 and is capped at 32767 because column
  counts and related limits are stored in signed 16-bit fields in several
  places.
- `SQLITE_MAX_SQL_LENGTH`, `SQLITE_MAX_EXPR_DEPTH`, and
  `SQLITE_MAX_PARSER_DEPTH` bound parse input size, expression recursion, and
  parser stack depth.
- `SQLITE_MAX_COMPOUND_SELECT`, `SQLITE_MAX_VDBE_OP`, and
  `SQLITE_MAX_FUNCTION_ARG` bound statement complexity. The function argument
  count defaults to 1000 and is constrained by a 32767 hard storage limit.
- `SQLITE_DEFAULT_CACHE_SIZE` and `SQLITE_DEFAULT_WAL_AUTOCHECKPOINT` supply
  default page-cache and WAL checkpoint policy.
- `SQLITE_MAX_ATTACHED` defaults to 10 and is documented as limited to 125
  because attached database indexes fit in a signed 8-bit counter after
  reserving slots for `main` and `temp`.
- `SQLITE_MAX_VARIABLE_NUMBER` defaults to 32766, avoiding extra `Expr` storage
  for very large parameter indexes.
- `SQLITE_MAX_PAGE_SIZE` is forcibly set to 65536 even if a build attempts to
  override it. This preserves file-format compatibility around 16-bit offsets
  and crash recovery.
- `SQLITE_DEFAULT_PAGE_SIZE` and `SQLITE_MAX_DEFAULT_PAGE_SIZE` are normalized
  so defaults never exceed `SQLITE_MAX_PAGE_SIZE`, and the automatic default
  maximum never drops below the explicit default.
- `SQLITE_MAX_PAGE_COUNT`, `SQLITE_MAX_LIKE_PATTERN_LENGTH`, and
  `SQLITE_MAX_TRIGGER_DEPTH` provide default caps for database file pages,
  pattern matching input, and trigger recursion.

## Control Flow And Validation Behavior

The control flow is preprocessor-only. Most definitions follow the same pattern:
if a macro is not already defined by the build, define a conservative default.
Some macros add an `#elif` or `#if` guard to reject unsupported values. Page-size
macros are more assertive: any external `SQLITE_MAX_PAGE_SIZE` definition is
undefined and replaced with 65536, while page-size defaults are clamped by
preprocessor rewrites.

This file therefore runs before C compilation of the SQLite core. Runtime code
does not call into it, but many runtime decisions assume the invariants it
establishes. A bad value here usually causes either compile failure or latent
breakage in allocation, parser recursion, statement construction, or file I/O.

## State And Persistence Behavior

The header maintains no runtime state and persists nothing directly. Its values
can affect persistent database shape indirectly. `SQLITE_MAX_PAGE_SIZE`,
`SQLITE_DEFAULT_PAGE_SIZE`, and `SQLITE_MAX_PAGE_COUNT` interact with database
header fields and pager/btree decisions. The forced 64 KiB page-size maximum is
especially important because a process compiled with incompatible page limits
could otherwise fail to roll back a transaction created by another build.

Other values affect only per-process resource ceilings, such as expression
depth, SQL text length, and allocation size. Those limits can influence which
schemas or SQL statements a given build accepts.

## Dependencies And Integration Points

`sqliteLimit.h` is consumed through SQLite internal headers, primarily
`sqliteInt.h`, and feeds:

- public `sqlite3_limit()` categories such as length, SQL length, columns,
  expression depth, compound select terms, variable number, function arguments,
  LIKE/GLOB pattern length, and trigger depth;
- parser and code generator arrays and recursion checks;
- VDBE program construction and function invocation checks;
- btree and pager page-size logic;
- WAL auto-checkpoint defaults and page-cache default sizing.

The comments include requirement tags for cache-size defaults, so this file is
also part of SQLite's evidence-backed documentation/test matrix.

## Risks

The highest-risk changes are values tied to storage widths or file format:
`SQLITE_MAX_COLUMN`, `SQLITE_MAX_FUNCTION_ARG`, `SQLITE_MAX_ATTACHED`,
`SQLITE_MAX_VARIABLE_NUMBER`, and all page-size/count constants. Increasing
limits without auditing downstream integer types can introduce truncation,
overflow, parser stack exhaustion, or incompatible database files.

Lowering limits is usually safer but can break applications or tests that rely
on SQLite's documented defaults. Raising `SQLITE_MAX_ALLOCATION_SIZE` is
explicitly blocked above the hard cap; changing that guard would reduce defense
against 32-bit signed overflow bugs.

## Test Signals

Useful validation signals include compile-time tests that deliberately override
macros near hard boundaries, `sqlite3_limit()` API tests, parser stress tests
for deeply nested expressions and compound selects, large BLOB/TEXT boundary
tests, function argument count tests, and database open/recovery tests for page
sizes up to 65536. Requirement tests should continue to verify the documented
default cache size and WAL auto-checkpoint values.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/sqliteLimit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/status.c -->
# Research: sources/storage-engines/sqlite/src/status.c

## Purpose

`status.c` implements SQLite's global `sqlite3_status()` /
`sqlite3_status64()` APIs and per-connection `sqlite3_db_status()` /
`sqlite3_db_status64()` APIs. It records memory/page-cache counters, exposes
current and high-water values, and computes connection-local statistics such as
lookaside usage, schema memory, statement memory, pager cache activity,
temporary spill bytes, and deferred foreign-key state.

The file is deliberately small but important for observability. Many counters
are maintained by other subsystems and read here under the same mutexes that
protect updates.

## Important APIs, Types, And Data

- `sqlite3StatValueType` is `sqlite3_int64` on pointer sizes greater than four
  bytes and `u32` otherwise.
- `sqlite3StatType` contains `nowValue[10]` and `mxValue[10]`, the current and
  high-water values for global status verbs.
- `sqlite3Stat` is writable static data unless `SQLITE_OMIT_WSD` requires the
  `GLOBAL()` indirection through `wsdStat`.
- `statMutex[]` maps each global status verb to either the allocator mutex or
  the pcache1 mutex.
- `sqlite3StatusValue()`, `sqlite3StatusUp()`, `sqlite3StatusDown()`, and
  `sqlite3StatusHighwater()` are internal update/read helpers. They assert that
  callers hold the correct mutex.
- `sqlite3_status64()` and `sqlite3_status()` are public global status query
  interfaces. The 32-bit variant truncates the 64-bit results to `int`.
- `sqlite3LookasideUsed()` counts connection lookaside slots.
- `sqlite3_db_status64()` and `sqlite3_db_status()` are public
  connection-local status query interfaces.

## Control Flow

Global status updates are simple counter operations. The helper functions check
array bounds and mutex ownership in asserts, update `nowValue`, and optionally
advance or reset `mxValue`. `sqlite3_status64()` validates the verb, optionally
checks output pointers under API armor, enters the mutex selected by
`statMutex[]`, copies current/high-water values, resets the high-water value to
the current value if requested, and leaves the mutex.

Per-connection status is a switch inside `sqlite3_db_status64()` protected by
`db->mutex`:

- lookaside status counts slots on `pInit`, `pFree`, and, when enabled, the
  two-size lookaside lists. Resetting folds free lists back into init lists so
  the next high-water baseline changes;
- lookaside hit/miss counters return the accumulated high-water-style value and
  reset the selected `anStat` entry if requested;
- cache memory walks all `db->aDb[]` btrees, asks each pager for memory used,
  and optionally divides shared cache usage by the connection count;
- schema memory temporarily routes frees into `db->pnBytesFreed`, disables
  lookaside allocation by shrinking `lookaside.pEnd`, and calls schema object
  destructors to measure memory without actually losing the live schema;
- statement memory uses the same `pnBytesFreed` accounting trick around all
  VDBEs on the connection;
- cache hit/miss/write/spill totals are accumulated through
  `sqlite3PagerCacheStat()`;
- temporary spill bytes combine temp database pager writes converted to bytes
  with `db->nSpill`;
- deferred foreign-key status reports whether immediate or deferred constraint
  counters are nonzero.

Unknown per-connection verbs return `SQLITE_ERROR`.

## State And Persistence Behavior

The global `sqlite3Stat` object is process-local mutable state. It is not
persistent across process lifetime and is reset only by process initialization
or high-water reset calls. Updates are expected to happen from allocator or
page-cache code under the mutex selected for the status verb.

Connection status reads depend on live `sqlite3` state. Resetting some status
verbs mutates in-memory counters (`lookaside.anStat`, `db->nSpill`) or lookaside
bookkeeping lists, but it does not write database files. The schema and
statement memory calculations deliberately use SQLite's destructor paths in a
measurement mode driven by `db->pnBytesFreed`; their correctness depends on
those destructors honoring the counting convention and not actually releasing
live structures in this path.

## Dependencies And Integration Points

This file includes `sqliteInt.h` and `vdbeInt.h`. It integrates with:

- memory allocation status through `sqlite3MallocMutex()` and allocator update
  hooks;
- pcache status through `sqlite3Pcache1Mutex()`;
- btree/pager APIs such as `sqlite3BtreeEnterAll()`, `sqlite3BtreePager()`,
  `sqlite3PagerMemUsed()`, `sqlite3PagerCacheStat()`, and
  `sqlite3BtreeConnectionCount()`;
- schema hash tables and destructors (`sqliteHashFirst()`,
  `sqlite3DeleteTrigger()`, `sqlite3DeleteTable()`);
- VDBE ownership through `db->pVdbe` and `sqlite3VdbeDelete()`;
- lookaside allocator internals on `sqlite3.lookaside`.

The public API result codes are part of SQLite's stable C API, so behavior here
is visible to applications and testfixture scripts.

## Risks

The main risk is mutex discipline. Internal status helpers rely on asserts
rather than runtime locking, so callers must already hold the right mutex. A new
status verb must be added consistently to the arrays, mutex map, public enum
definitions, and update sites.

The measurement paths for schema and statement memory are subtle: they reuse
delete routines while diverting freed byte counts and temporarily disabling
lookaside. Changes to destructors, lookaside fields, or `pnBytesFreed` could
turn a measurement into a real free or undercount allocations.

The 32-bit wrappers mask 64-bit values with `0x7fffffff` for db-status and cast
for global status, so tests that compare very large counters need to use the
64-bit APIs.

## Test Signals

Strong tests include allocator/page-cache status increments under
threadsafe builds, high-water reset checks, API armor null-pointer checks,
lookaside reset behavior with both one-size and two-size lookaside builds,
schema and statement memory reporting with prepared statements and attached
databases, cache hit/miss/write/spill counters before and after reset, temp
buffer spill accounting, and deferred foreign-key status inside and after
transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/table.c -->
# Research: sources/storage-engines/sqlite/src/table.c

## Purpose

`table.c` implements the legacy convenience APIs `sqlite3_get_table()` and
`sqlite3_free_table()` when `SQLITE_OMIT_GET_TABLE` is not defined. These APIs
run SQL through `sqlite3_exec()`, collect the entire result set into a
malloc-owned `char **` table, and return row and column counts to the caller.

This module is intentionally separate so builds that do not use the get-table
interface can avoid linking it.

## Important APIs, Types, And Functions

- `TabResult` is the accumulator passed as the `sqlite3_exec()` callback
  context. It stores the result vector, error text, allocated slots, row count,
  column count, used data slots, and callback return code.
- `sqlite3_get_table_cb()` is the row callback that grows the result vector,
  stores column names on the first row, checks column-count consistency across
  statements, copies row values, and stops execution on allocation failure.
- `sqlite3_get_table()` initializes `TabResult`, invokes `sqlite3_exec()`,
  handles callback aborts and exec errors, shrinks the result vector, and
  returns `&res.azResult[1]` to hide an internal slot containing the allocation
  size.
- `sqlite3_free_table()` reverses the pointer adjustment, reads the stored slot
  count from `azResult[-1]`, frees all non-null strings, and frees the result
  array.

## Control Flow

`sqlite3_get_table()` first validates the database handle and output pointer
under API armor, clears output arguments, allocates an initial 20-slot result
array, and reserves `azResult[0]` for metadata. It then calls `sqlite3_exec()`
with `sqlite3_get_table_cb()`.

The callback calculates how many slots the current invocation needs. On the
first data row it reserves space for both column names and row values; after
that it reserves only row values. It doubles previous allocation and adds the
current need when growth is required. The first row also initializes
`nColumn` and copies all column names with `sqlite3_mprintf()`. Later rows must
have the same column count; otherwise the callback sets a specific
incompatible-query error, stores `SQLITE_ERROR`, and aborts. Row values are
copied with `sqlite3_malloc64()` and `memcpy()`, preserving SQL NULLs as null
pointers.

After exec returns, `sqlite3_get_table()` stores `nData` in the hidden metadata
slot using pointer/int conversion macros. If execution was aborted by the
callback, it frees partial results, propagates the callback's own error message
where appropriate, sets `db->errCode`, and returns `res.rc`. If exec itself
failed, it frees the partial table and returns the exec code. On success it
shrinks the array to exactly the number of used slots and returns the pointer
one element past the metadata slot.

## State And Persistence Behavior

The module owns only transient heap state. It does not alter persistent database
format beyond whatever SQL text passed to `sqlite3_get_table()` executes via
`sqlite3_exec()`. The result allocation layout is an important ABI detail:
callers must free with `sqlite3_free_table()` rather than `sqlite3_free()`
because the visible pointer is offset by one slot.

The API stores column names as a first logical row before data rows, matching
SQLite's documented `sqlite3_get_table()` behavior. Even if a statement returns
zero rows, the result array still has internal metadata and a visible pointer
may be returned on success.

## Dependencies And Integration Points

The implementation depends on `sqliteInt.h`, `sqlite3_exec()`, SQLite memory
APIs (`sqlite3_malloc64()`, `sqlite3Realloc()`, `sqlite3_free()`,
`sqlite3_mprintf()`), string helpers (`sqlite3Strlen30()`), and internal
error-code conventions (`SQLITE_NOMEM_BKPT`, `SQLITE_ABORT`, `SQLITE_OK`).

It is a wrapper over the main exec callback interface rather than a separate
prepare/step/finalize path. That keeps behavior aligned with `sqlite3_exec()`
semantics for multi-statement SQL and callback aborts.

## Risks

The hidden metadata slot is fragile: any caller that passes a shifted or
manually modified pointer to `sqlite3_free_table()` can corrupt frees. The code
also relies on `sizeof(char*) >= sizeof(u32)` for storing `nData` in a pointer
slot, which is asserted.

Because the entire result set is materialized, this API can consume large
amounts of memory and is inappropriate for unbounded queries. Multi-statement
queries must return compatible column counts or the wrapper aborts with an
error specific to `sqlite3_get_table()`.

The callback uses `SQLITE_ABORT` detection through `(rc&0xff)==SQLITE_ABORT`,
so changes to extended result-code encoding or callback abort handling would
need care.

## Test Signals

Useful tests cover successful SELECTs with column-name row placement, SQL NULL
preservation as null pointers, zero-row results, multi-statement compatible and
incompatible result shapes, allocation-failure injection, propagation of
callback errors through `pzErrMsg`, `sqlite3_free_table(NULL)`, and API armor
misuse cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/tclsqlite.c -->
# Research: sources/storage-engines/sqlite/src/tclsqlite.c

## Purpose

`tclsqlite.c` implements SQLite's Tcl extension and optional standalone
`tclsh`-style executable. It exposes a top-level `sqlite3` Tcl command that
opens an SQLite connection and creates a Tcl command for that connection. The
connection command then provides methods for SQL evaluation, statement cache
control, callbacks/hooks, backup/restore, serialization, incremental BLOB
channels, user-defined SQL functions/collations, transactions, tracing, and
test-oriented features.

The file is designed to build both appended to the SQLite amalgamation and as a
separate source file. It embeds a copy of `tclsqlite.h` near the top so the
amalgamated Tcl source has the same Tcl include and Tcl 8.6/9.0 compatibility
logic.

## Important Types And State

- `SqlFunc` records Tcl-backed SQL scalar functions: interpreter, script object,
  owning database, safe-eval flag, requested return type, name, and linked-list
  pointer.
- `SqlCollate` records Tcl-backed collations: interpreter, script text, and
  linked-list pointer.
- `SqlPreparedStmt` wraps a cached `sqlite3_stmt`, SQL text identity, LRU links,
  and Tcl object references for parameters bound with `SQLITE_STATIC`.
- `SqliteDb` is the central per-connection state and deliberately stores
  `sqlite3 *db` first. It owns the Tcl interpreter, callback script strings,
  hook Tcl objects, user function/collation lists, prepared statement cache,
  open incremental blob channel list, recent statement statistics, nested
  transaction count, URI open flags, reference count, and test-only legacy
  prepare mode.
- `IncrblobChannel` wraps `sqlite3_blob` as a Tcl channel with current seek
  offset, close flags, associated `SqliteDb`, and connection-local linked-list
  links.
- `DbEvalContext` is the state machine for `$db eval`: SQL text, current
  prepared statement, target array/dict variable, cached column names, and eval
  flags.

## Top-Level Open Flow

`Sqlite3_Init()` initializes Tcl stubs, creates the `sqlite3` command and,
unless `SQLITE_3_SUFFIX_ONLY` is defined, a legacy `sqlite` alias, then provides
the Tcl package. Safe interpreter init and unload entry points return
`TCL_ERROR` because SQLite uses filesystem and persistent state.

The `sqlite3` command is implemented by `DbMain()`. With `-version`,
`-sourceid`, or `-has-codec`, it returns metadata. Otherwise it parses handle
name, filename, and options including `-vfs`, `-readonly`, `-create`,
`-nofollow`, `-nomutex`, `-fullmutex`, `-uri`, and `-translatefilename`. The
default open mode is read-write/create with `SQLITE_OPEN_NOMUTEX`, unless
`SQLITE_TCL_DEFAULT_FULLMUTEX` selects full mutexes for test builds.

`DbMain()` optionally translates the Tcl filename, opens with
`sqlite3_open_v2()`, converts open failures into Tcl errors, initializes a
`SqliteDb` with a default 10-statement cache, and creates the connection Tcl
command. On Tcl versions with non-recursive evaluation support, it registers an
NRE adaptor so `$db eval` and `$db transaction` can avoid deep Tcl recursion.

## Connection Command Surface

`DbObjCmd()` dispatches connection methods using `Tcl_GetIndexFromObj()`. Major
method groups are:

- SQL execution: `eval`, `exists`, `onecolumn`, and `format`.
- Transaction control: `transaction`, with `deferred`, `immediate`, or
  `exclusive` top-level begin style and savepoint-based nesting.
- Statement cache: `cache flush` and `cache size n`, capped by
  `MAX_PREPARED_STMTS`.
- Binding behavior: automatic Tcl variable binding for `$`, `:`, and `@`
  parameters plus `bind_fallback`.
- Hooks and callbacks: `busy`, `progress`, `authorizer`, `commit_hook`,
  `rollback_hook`, `wal_hook`, `update_hook`, `preupdate hook`,
  `collation_needed`, `trace`, `trace_v2`, `profile`, and `unlock_notify`.
- User extensions: `function` and `collate`.
- File and memory movement: `backup`, `restore`, `serialize`, `deserialize`,
  and the legacy `copy` importer.
- Connection metadata/actions: `changes`, `total_changes`,
  `last_insert_rowid`, `errorcode`, `erroroffset`, `interrupt`, `complete`,
  `config`, `enable_load_extension`, `timeout`, `status`, `version`,
  `nullvalue`, and `close`.
- Incremental BLOB I/O: `incrblob`, returning a Tcl channel name.

Many methods are conditionally compiled and return explicit Tcl errors when
the required SQLite feature was omitted.

## Statement Preparation, Binding, And Evaluation

`dbPrepare()` selects `sqlite3_prepare_v3()` and uses
`SQLITE_PREPARE_PERSISTENT` when the statement cache is large enough to make
lookaside preservation more valuable. In `SQLITE_TEST` builds it can use legacy
`sqlite3_prepare()` for compatibility tests.

`dbPrepareAndBind()` trims leading whitespace, looks for a cached prepared
statement whose SQL prefix matches the next statement, unlinks cache hits from
the LRU list, or prepares and allocates a new `SqlPreparedStmt`. It then binds
host parameters named with `$`, `:`, or `@` from Tcl variables. Missing
variables either bind NULL or invoke `zBindFallback`. Binding preserves Tcl
object lifetimes for blobs and text passed with `SQLITE_STATIC` by incrementing
object refcounts and storing them in `apParm`; `dbReleaseStmt()` later decrefs
them.

Binding type decisions inspect Tcl object internal type names. Bytearrays with
no string representation, and all `@name` parameters, bind as BLOBs. Boolean,
integer, wide integer, and double Tcl objects bind as the corresponding SQLite
numeric types. Other values bind as UTF-8 text. Missing values bind NULL.

`DbEvalContext` drives multi-statement SQL execution. `dbEvalStep()` prepares
the next statement as needed, steps it until a row or completion, records
statement status counters on reset, handles schema retry only for legacy
prepare test mode, and releases statements back to the cache or discards them
on error. `dbEvalRowInfo()` lazily builds column-name Tcl objects and populates
the target array/dict `*` entry. `dbEvalColumnValue()` converts SQLite column
types back into Tcl objects, using `pDb->zNull` for SQL NULL.

`$db eval SQL` without a script returns a flat Tcl list of all column values.
With a script, `DbEvalNextCmd()` fills either same-named variables, an array, or
a dict for each row, supports `-withoutnulls` and `-asdict`, evaluates the
script for each row, and treats `break` as normal completion.

## Transactions And Persistence Behavior

`$db transaction` always opens either a top-level transaction or a savepoint
named `_tcl_transaction`. Nested calls use savepoints. `DbTransPostCmd()`
chooses `COMMIT`, `ROLLBACK`, `RELEASE`, or `ROLLBACK TO ...; RELEASE` based on
the script result and nesting depth. It temporarily disables the authorizer
while running transaction-control SQL so Tcl authorizer scripts do not block the
wrapper's cleanup. If commit fails, it reports the SQLite error and attempts a
rollback.

The extension itself persists only through the underlying SQLite database and
through Tcl-visible channels/commands. Connection state is memory-resident:
prepared statement cache, callback scripts, hook objects, functions,
collations, and incremental blob channels are all freed when the connection Tcl
command is deleted and `SqliteDb.nRef` reaches zero.

`backup` and `restore` use the SQLite backup API in 100-page steps. `restore`
retries a few `SQLITE_BUSY` steps with sleep. `serialize` returns a Tcl
bytearray from `sqlite3_serialize()`, preferring `SQLITE_SERIALIZE_NOCOPY` but
copying when required. `deserialize` copies the Tcl bytearray into SQLite
malloc memory and passes ownership with `SQLITE_DESERIALIZE_FREEONCLOSE`, using
readonly or resizable flags according to options.

The legacy `copy` importer reads a Tcl channel line by line, splits on a
separator, inserts inside a transaction, maps empty or null-indicator fields to
SQL NULL, and rolls back on shape or SQLite errors.

## Callback And Hook Control Flow

The busy, progress, commit, trace, profile, trace_v2, WAL, update, preupdate,
rollback, unlock-notify, authorizer, collation, and SQL function callbacks all
bridge SQLite C callbacks into Tcl script evaluation.

Callbacks append structured arguments to the configured Tcl script. Examples:
the authorizer appends action name and four context strings; update hooks append
operation, database, table, and rowid; WAL hook appends database name and frame
count and expects an integer SQLite return code; trace_v2 appends statement or
connection pointers and event-specific data. Most callbacks reset the Tcl
result after fire-and-forget use; errors in rollback/WAL hooks are reported via
`Tcl_BackgroundError()`.

`tclSqlFunc()` evaluates a Tcl script as an SQL scalar function. It converts
SQLite arguments to Tcl values, evaluates the script efficiently using a
shallow list copy, treats `TCL_BREAK` as SQL NULL, reports Tcl errors via
`sqlite3_result_error()`, and maps the Tcl result back to SQLite using either a
declared `-returntype` or internal Tcl object type inference.

`tclSqlCollate()` evaluates a Tcl script with the two strings to compare and
returns the integer Tcl result as the SQLite collation comparison value.

## Incremental Blob Channels

When incremental BLOB support is enabled, `$db incrblob ?-readonly? ?DB? TABLE
COLUMN ROWID` opens a `sqlite3_blob` and wraps it in a Tcl channel. The channel
type implements close, read, write, seek, wide seek, watch no-op, and handle
failure. Reads clamp to the blob size and advance `iSeek`. Writes reject
attempts past the fixed blob size and return Tcl channel errors on SQLite I/O
failures.

Open channels are linked from `SqliteDb.pIncrblob`. `closeIncrblobChannels()`
unregisters them during connection destruction, and the channel close path
removes the node from the linked list, closes the `sqlite3_blob`, and frees the
channel wrapper.

## Dependencies And Integration Points

This file depends on Tcl C APIs, SQLite public APIs, and, when not amalgamated,
`sqlite3.h`, C runtime headers, and platform process headers. Optional
integration includes QRF (`qrf.h`) for `$db format`, unlock notify, preupdate
hook, deserialize/serialize, load extension, incremental blob, tracing,
progress callbacks, authorization, and standalone `TCLSH`.

It is a major integration point for SQLite's Tcl test suite. Test-only code
supports legacy prepare selection, unlock-notify global test variables,
last-statement pointer inspection, and debug-break behavior in standalone
shell mode.

## Risks

This file has several risk clusters:

- Tcl script callbacks can re-enter SQLite or delete the connection command.
  The reference-counting around `SqliteDb` and eval contexts is therefore
  critical.
- Statement caching with `SQLITE_STATIC` bindings depends on accurately
  retaining Tcl object references until `sqlite3_reset()` and release.
- The transaction wrapper can be confused by user scripts that manually issue
  transaction-control SQL inside `$db transaction`; the code comments call out
  this tricky scenario.
- Type inference based on Tcl internal type names is version-sensitive and must
  be kept compatible with Tcl 8.6 and Tcl 9.0.
- The legacy `copy` parser is separator-based rather than CSV-aware and
  materializes/modifies line buffers in place.
- Conditional compilation creates many build surfaces; missing-feature paths
  need tests so Tcl users get deterministic errors rather than unresolved
  symbols.

## Test Signals

High-value tests include opening with every option combination, failing opens,
SQL variable binding for all Tcl value types, `bind_fallback` success/error,
statement cache LRU behavior, eval list/array/dict modes, `-withoutnulls`,
nested transaction commit/rollback/savepoint behavior, callback registration
and clearing, user-defined function return-type mapping, collation callbacks,
authorizer decisions, busy/progress interruption, trace_v2 masks, backup and
restore error paths, serialize/deserialize readonly and max-size options,
incremental blob read/write/seek/close behavior, connection deletion during
callbacks, Tcl 8.6 vs Tcl 9.0 builds, and omitted-feature builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/tclsqlite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/tclsqlite.h -->
# Research: sources/storage-engines/sqlite/src/tclsqlite.h

## Purpose

`tclsqlite.h` is the small interface shim that SQLite components use instead
of including `tcl.h` directly. It centralizes platform-specific Tcl include
selection, calling-convention decoration, and Tcl 8.6/9.0 compatibility types
for SQLite's Tcl extension and Tcl-based test components.

The header explicitly warns that edits must be mirrored in `tclsqlite.c`,
because that C file carries an embedded copy for amalgamated builds.

## Important Macros And Behavior

- If `INCLUDE_SQLITE_TCL_H` is defined, the header includes `sqlite_tcl.h`.
  This supports Windows STDCALL builds where the MSVC makefile creates a
  customized Tcl header with SQLite's needed calling conventions.
- Otherwise it includes the system `<tcl.h>` and defines `SQLITE_TCLAPI` to an
  empty macro if Tcl did not provide one.
- For Tcl 9, it defines `CONST` as `const`.
- For older Tcl headers that do not define `Tcl_Size`, it aliases
  `Tcl_Size` to `int`.

## Control Flow And State

The file has only preprocessor control flow and no runtime state. Its role is
to make downstream C code compile with consistent type names and function
declarations across Tcl header variants. The repeated mirror-warning comments
are part of the maintenance contract.

## Dependencies And Integration Points

The direct dependency is either `sqlite_tcl.h` or `<tcl.h>`. The consumers are
SQLite's Tcl extension (`tclsqlite.c`), Tcl-enabled test files, and any
subcomponent that needs Tcl APIs while respecting SQLite's build conventions.

Because `tclsqlite.c` embeds a copy, this header is not the only source of
truth at build time. Changes must be synchronized manually or separate-source
and amalgamated builds may diverge.

## Risks

The main risk is drift between this header and the copy inside `tclsqlite.c`.
A missing `SQLITE_TCLAPI`, `Tcl_Size`, or `CONST` compatibility change can
break one build mode while the other continues to compile. Windows STDCALL
builds are also sensitive to choosing the correct customized Tcl header.

The compatibility definitions are intentionally minimal. Adding broader Tcl
compatibility here should be checked against Tcl's own headers to avoid
conflicting typedefs or macro definitions.

## Test Signals

Validation should include separate-source and amalgamated Tcl extension builds,
Windows builds with `INCLUDE_SQLITE_TCL_H`, normal Unix-like builds with
system `<tcl.h>`, Tcl 8.6 builds where `Tcl_Size` may need compatibility, and
Tcl 9 builds where `CONST` behavior and `SQLITE_TCLAPI` declarations remain
accepted.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/tclsqlite.h -->
