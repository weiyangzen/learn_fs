# subset-b-008768 Research

Grouped research for SQLite source files in `sources/storage-engines/sqlite/src`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/callback.c -->
# sources/storage-engines/sqlite/src/callback.c

## Purpose

`callback.c` maintains SQLite connection-local registries for collating sequences and application-defined SQL functions, plus schema-object cleanup and schema allocation. It is not a user callback dispatcher in the general sense; instead it supports callbacks that provide missing collations (`xCollNeeded`/`xCollNeeded16`) and manages the hash-table entries that later parser, expression, and VDBE code use when resolving SQL names.

## Important APIs, Types, and Functions

- `sqlite3FindCollSeq()` locates or optionally creates one of the three `CollSeq` entries associated with a collation name. Each hash entry stores UTF-8, UTF-16LE, and UTF-16BE variants plus a single trailing name string.
- `sqlite3GetCollSeq()` is the resolving wrapper that invokes the collation-needed callback and can synthesize a collation from another encoding using `synthCollSeq()`.
- `sqlite3LocateCollSeq()` resolves by database-native encoding during parsing and creates placeholder entries while schema initialization is busy.
- `sqlite3SetTextEncoding()` changes `db->enc`, resets `db->pDfltColl` to `BINARY`, and expires prepared statements.
- `matchQuality()` scores candidate `FuncDef` entries by argument count and text encoding. `sqlite3FindFunction()` uses it to search application functions first, then built-ins unless creation is requested.
- `sqlite3InsertBuiltinFuncs()` inserts compile-time function definitions into the global `sqlite3BuiltinFunctions` hash, chaining overloads with the same name.
- `sqlite3SchemaClear()` tears down `Schema` hash contents for tables, triggers, indexes, and foreign keys. `sqlite3SchemaGet()` obtains or initializes the schema object attached to a `Btree` or allocates a standalone schema.

Core data structures are `CollSeq`, `FuncDef`, `Schema`, `Hash`, `HashElem`, `Table`, `Trigger`, and `Btree`, all defined in SQLite internals.

## Control Flow and Behavior

Collation lookup begins with `findCollSeqEntry()`, which returns a three-entry encoding array or creates one when allowed. If a collation exists but has no comparison function, `sqlite3GetCollSeq()` calls `callCollNeeded()`. The UTF-8 callback gets a database-owned copy of the name; the UTF-16 callback builds a transient `sqlite3_value` to convert the name to native UTF-16. If the exact encoding remains unresolved, `synthCollSeq()` searches alternate encodings and copies the usable `CollSeq` while intentionally dropping the copied destructor pointer.

Function lookup uses a two-level search. Application-defined functions live in `db->aFunc` and are linked through `pNext`; built-ins live in `sqlite3BuiltinFunctions.a[h]` and can also have `pNext` overload chains. `sqlite3FindFunction()` chooses the highest `matchQuality()` score. With `createFlag`, it allocates a new lowercase-name `FuncDef`, inserts it into the per-connection hash, and returns only mutable application-owned entries.

Schema cleanup snapshots the table and trigger hashes, reinitializes schema hash heads first, and then deletes objects using a zeroed fake `sqlite3` handle. This avoids recursive stale hash traversal while freeing nested table and trigger resources.

## State and Persistence

The file mutates connection-local state: `db->aCollSeq`, `db->aFunc`, `db->enc`, `db->pDfltColl`, `db->mDbFlags`, and schema hash members. Built-in function registration mutates global `sqlite3BuiltinFunctions`. Schema clearing increments `Schema.iGeneration` when a loaded schema is reset and clears `DB_SchemaLoaded`/`DB_ResetWanted`, which invalidates dependent prepared statements elsewhere. No database pages are written directly here.

## Dependencies and Integration Points

This code depends on SQLite hash APIs, allocator APIs, string comparison helpers, parser error reporting, value conversion, trigger/table deletion, and B-tree schema storage. It is called from parser name resolution, function registration APIs, collation registration APIs, schema reset paths, and date/time or other built-in function registration (`sqlite3InsertBuiltinFuncs()` is used by multiple modules).

## Risks and Edge Cases

Collation fallback intentionally copies function pointers but not destructors; copying `xDel` would double-free external collation state. OOM paths must signal `sqlite3OomFault()` and leave hash tables consistent. `sqlite3FindFunction()` must not return built-in definitions while creating a new function because callers overwrite returned fields. `matchQuality()` has special negative arity rules for built-ins with one-or-more or two-or-more arguments. Schema cleanup order is sensitive because table deletion can refer to trigger/index/fkey structures.

## Test Signals

Useful tests include collation-needed callbacks for UTF-8 and UTF-16 names, missing collation error text and `SQLITE_ERROR_MISSING_COLLSEQ`, fallback across encoding-specific collations, application functions overriding built-ins and `DBFLAG_PreferBuiltin`, vararg and fixed-arity function resolution, OOM during hash insertion, schema reset generation increments, and deletion of schemas containing tables, indexes, triggers, and foreign keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/carray.c -->
# sources/storage-engines/sqlite/src/carray.c

## Purpose

`carray.c` implements the optional `carray` eponymous virtual table/table-valued function, enabled only when virtual tables are present and `SQLITE_ENABLE_CARRAY` is defined. It exposes caller-supplied C arrays to SQL rows, supporting pointer/count/ctype hidden-column constraints and a newer `sqlite3_carray_bind[_v2]()` API for safer single-argument binding.

## Important APIs, Types, and Functions

- `carray_bind` stores bound array metadata: data pointer, element count, type flags, destructor, and destructor argument.
- `carray_cursor` tracks scan state: current one-based rowid, array pointer, count, and element type.
- `carrayConnect()` declares `CREATE TABLE x(value,pointer hidden,count hidden,ctype hidden)`.
- `carrayBestIndex()` chooses among empty scan, single `pointer` bind (`idxNum=1`), pointer+count (`idxNum=2`), and pointer+count+ctype (`idxNum=3`).
- `carrayFilter()` decodes bound parameters into cursor state using pointer types `"carray-bind"` or `"carray"`.
- `carrayColumn()` materializes values as integer, int64, double, text, or blob from `struct iovec`.
- `sqlite3_carray_bind_v2()` and `sqlite3_carray_bind()` bind a `carray_bind` object to a statement parameter.
- `sqlite3CarrayRegister()` registers the module as `"carray"`.

## Control Flow and Behavior

The planner requests constraints on hidden columns. If only `pointer=` is usable, the value must be a pointer bound by `sqlite3_carray_bind_v2()` with type `"carray-bind"`, and count/type come from `carray_bind`. If `pointer=` and `count=` are usable, the pointer must be bound with pointer type `"carray"` and the type defaults to `int32`. A usable `ctype=` switches to typed values after validating against `azCarrayType`.

The cursor starts at rowid 1 and advances by incrementing `iRowid`. EOF occurs when `iRowid > iCnt`. `value` reads `pPtr[iRowid-1]` according to `eType`; hidden columns either return count/type or no pointer value. Invalid or unconstrained inputs yield an empty table instead of dereferencing.

Binding with `SQLITE_TRANSIENT` copies the array into one allocation. Text arrays copy the pointer array plus nul-terminated strings; blob arrays copy `struct iovec` entries plus blob payloads; numeric arrays copy fixed-width bytes. Non-transient binding stores the supplied pointer and destructor metadata. The bound object is attached with `sqlite3_bind_pointer()` and cleaned up by `carrayBindDel()`.

## State and Persistence

The virtual table is stateless except for per-cursor scan state and per-parameter `carray_bind` objects owned by prepared statements. It does not write database storage. Destructor handling is the main state lifecycle: `SQLITE_STATIC` means no caller destructor, `SQLITE_TRANSIENT` means SQLite owns copied memory, and other callbacks are invoked for `pDestroy` or `aData` depending on the API variant.

## Dependencies and Integration Points

This file depends on the virtual table API, pointer binding API, result APIs, SQLite memory allocation, and `struct iovec` availability. On Windows-like targets it defines a local `struct iovec`. SQL integration is via `sqlite3VtabCreateModule()`, allowing `SELECT * FROM carray(...)` syntax through eponymous virtual tables.

## Risks and Edge Cases

The legacy pointer/count form can dereference invalid C pointers if callers bind wrong addresses or lifetimes. `carrayBestIndex()` rejects partial multi-argument usage where `count` or `ctype` constraints are present but unavailable, preventing silently wrong function-call semantics. `sqlite3_carray_bind_v2()` validates `mFlags`, but it does not guard negative `nData` beyond normal size arithmetic expectations; callers must pass sane counts. Large transient text/blob arrays can overflow or OOM if size accumulation exceeds allocator limits. Blob `iov_len` is cast to `int` in `sqlite3_result_blob()`, so extremely large individual blobs are outside practical safe use.

## Test Signals

Tests should cover all five element types, null text entries, transient copy lifetime after caller memory is freed, custom destructors and `pDestroy`, unknown `ctype` error reporting, unconstrained empty scans, partial hidden-column constraint rejection, pointer type mismatches, planner estimates and `omit` flags, and registration when `SQLITE_ENABLE_CARRAY` is disabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/carray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/complete.c -->
# sources/storage-engines/sqlite/src/complete.c

## Purpose

`complete.c` implements `sqlite3_complete()`, `sqlite3_complete16()`, and the internal diagnostic `sqlite3_incomplete()`. It tokenizes enough SQL to decide whether a string ends at a complete statement boundary, including comments, quoted strings/identifiers, parentheses, and the special `CREATE TRIGGER ...; END;` termination rule.

## Important APIs, Types, and Functions

- `sqlite3_incomplete(const char*)` scans UTF-8 SQL and returns 0 for complete input or a packed nonzero diagnostic value for missing terminators.
- `sqlite3_complete()` returns the public boolean completion result.
- `sqlite3_complete16()` converts UTF-16 input to UTF-8 using a transient `sqlite3_value` and then delegates to `sqlite3_incomplete()`.
- Token constants include `tkSEMI`, `tkWS`, `tkOTHER`, and, when triggers are enabled, keyword tokens for `EXPLAIN`, `CREATE`, `TEMP`, `TRIGGER`, and `END`.
- `IdChar` is imported from tokenizer behavior for ASCII or EBCDIC builds.

## Control Flow and Behavior

The scanner is a hand-written state machine. Without triggers, it only needs states for invalid/start/normal and detects a final semicolon outside quotes/comments. With triggers enabled, the eight-state transition table distinguishes beginning-of-statement `EXPLAIN`, `CREATE`, optional `TEMP`/`TEMPORARY`, `TRIGGER`, first semicolon, `END`, and final semicolon. Whitespace never changes state.

The loop skips or validates lexical structures: C comments must close with `*/`, SQL comments run to newline, bracket identifiers must close with `]`, and quote/backtick strings must close with the same delimiter. Parentheses adjust `nParen` even though the public result still treats a semicolon-terminated statement as complete; the richer `sqlite3_incomplete()` return packs unmatched parenthesis count in upper bits. On finish, `statemap[state]` reports whether a semicolon or trigger tail is missing, and `pending` reports an unterminated quote/comment marker.

## State and Persistence

All state is local to the scan: current state, token, pending delimiter, and parenthesis count. `sqlite3_complete16()` may initialize SQLite unless autoinit is omitted and allocates a temporary value for transcoding. The file does not mutate database state or parse schema objects.

## Dependencies and Integration Points

The public API is used by shells and client libraries to decide whether more SQL text is needed. It depends on tokenizer character-class tables, case-insensitive comparison helpers, UTF-16 value conversion, and optional `sqlite3_initialize()`. Compile-time options change behavior for triggers, explain, UTF-16, API armor, ASCII, and EBCDIC.

## Risks and Edge Cases

The scanner is intentionally not a full SQL parser. It handles quote closure by searching the next matching delimiter and does not process doubled SQL quotes as escapes during this completion pass, so behavior must match SQLite's historical API contract and tests. Trigger completion is sensitive to recognizing keywords only at statement start. A trailing SQL comment without newline is considered pending only if the state is not already `START`. NULL input returns `SQLITE_MISUSE_BKPT` only under API armor; otherwise callers must avoid NULL.

## Test Signals

Tests should include empty and whitespace-only strings, simple semicolon completion, unterminated C/SQL comments, single/double/backtick/bracket quoted text, trigger bodies ending with `;END;`, `EXPLAIN CREATE TEMP TRIGGER`, trigger-disabled builds, unmatched parentheses diagnostics through `sqlite3_incomplete()`, UTF-16 inputs, EBCDIC character classes where supported, and NULL input under API armor.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/complete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/date.c -->
# sources/storage-engines/sqlite/src/date.c

## Purpose

`date.c` implements SQLite's date and time SQL functions. The full implementation registers `julianday`, `unixepoch`, `date`, `time`, `datetime`, `strftime`, `timediff`, current-time functions, and debug-only `datedebug`. When `SQLITE_OMIT_DATETIME_FUNCS` is set, it retains minimal `current_time`, `current_date`, and `current_timestamp` support for default column expressions.

## Important APIs, Types, and Functions

- `DateTime` caches a timestamp as Julian-day milliseconds (`iJD`), calendar fields (`Y/M/D`), time fields (`h/m/s`), timezone offset, and validity flags (`validJD`, `validYMD`, `validHMS`, `rawS`, `useSubsec`, `isUtc`, `isLocal`, `isError`).
- Parsing helpers include `getDigits()`, `parseTimezone()`, `parseHhMmSs()`, `parseYyyyMmDd()`, `parseDateOrTime()`, and `setRawDateNumber()`.
- Conversion helpers include `computeJD()`, `computeYMD()`, `computeHMS()`, `computeYMD_HMS()`, `validJulianDay()`, `computeFloor()`, `autoAdjustDate()`, and `clearYMD_HMS_TZ()`.
- Local time helpers `osLocaltime()` and `toLocaltime()` wrap platform `localtime` APIs and test fault injection.
- `parseModifier()` applies modifiers such as `unixepoch`, `julianday`, `auto`, `localtime`, `utc`, `weekday N`, `start of ...`, `floor`, `ceiling`, `subsec`, relative units, and signed date/time offsets.
- Output functions are `juliandayFunc()`, `unixepochFunc()`, `datetimeFunc()`, `timeFunc()`, `dateFunc()`, `strftimeFunc()`, `timediffFunc()`, and current-time wrappers.
- `sqlite3RegisterDateTimeFunctions()` inserts the function definitions into SQLite's built-in function table.

## Control Flow and Behavior

All full date/time functions route through `isDate()`. With no arguments, it uses the statement current time if the function is not being evaluated in a pure context. Numeric inputs become `rawS`, meaning they may later be interpreted as Julian day, Unix epoch seconds, or auto-detected. Text inputs are parsed as ISO-like date/time, time-only, `now`, numeric strings, or `subsec`/`subsecond` current time. Each modifier is then applied in order, and the final value is normalized to a valid Julian day.

`computeJD()` converts YMD/HMS/timezone data to Julian-day milliseconds and clears local calendar fields if timezone adjustment occurs. `computeYMD()` and `computeHMS()` lazily compute reverse views. The validity flags are central: modifiers clear stale representations after changing `iJD` or calendar fields so later functions recompute from the authoritative form.

Relative month/year additions are calendar-aware. They update Y/M, compute day overflow in `nFloor`, and allow `floor` to roll back to the last valid day or `ceiling` to keep default rollover. Numeric unit transforms convert seconds/minutes/hours/days directly in milliseconds, while month/year fractional remainders use fixed 30-day/365-day constants.

`strftimeFunc()` builds output using `sqlite3_str` under the connection length limit and supports SQLite-specific substitutions like `%f`, `%J`, `%G`, `%g`, `%k`, `%l`, `%P`, `%R`, `%T`, `%u`, `%U`, `%V`, and `%W`. Unknown format substitutions abort with NULL. `timediffFunc()` computes a signed calendar interval that can be used as a modifier to transform the second argument into the first.

## State and Persistence

No database pages are persisted. The main persistent-like state is statement-stable current time from `sqlite3StmtCurrentTime()`, ensuring multiple current-time calls in one statement agree. Localtime conversion uses process/OS timezone state and SQLite global fault-injection hooks in test builds. The registered built-ins become global function definitions via `sqlite3InsertBuiltinFuncs()`.

## Dependencies and Integration Points

This file depends on `sqliteInt.h`, C time APIs, SQLite value/result APIs, function purity checks, statement current-time plumbing, string accumulators, connection limits, mutexes around unsafe localtime variants, global test configuration, and the built-in function registration macros (`PURE_DATE`, `DFUNCTION`, `STR_FUNCTION`). It integrates with SQL execution as scalar functions and with default-value handling through the minimal omit build.

## Risks and Edge Cases

Range handling is strict: representable calendar dates are effectively `0000-01-01` through `9999-12-31 23:59:59.999`, and out-of-range `iJD` values return NULL. `rawS` is deliberately ambiguous until a modifier resolves it; wrong modifier order makes results NULL. Localtime outside 1970-2038 maps the year into an equivalent range, which is approximate and platform dependent. Fractional seconds are truncated around sub-millisecond input to avoid rounding surprises. Month/year arithmetic and `floor`/`ceiling` behavior are subtle around leap days and short months. Pure-function contexts must not observe current time or local timezone.

## Test Signals

Tests should cover ISO date/time parsing, timezone offsets and `Z`, negative years, date normalization like `2023-02-31`, Julian-day and Unix-epoch numeric interpretation, `auto` thresholds, modifier-order failures, `floor` and `ceiling` after month/year adds, `weekday`, `start of day/month/year`, `localtime`/`utc` conversions including injected failures, subsecond output for `datetime`, `time`, `unixepoch`, and `strftime('%s')`, week/year format specifiers, `timediff` invariants, length-limit failures in `strftime`, pure-function restrictions on `now`, and omit-datetime fallback current functions.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/date.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/dbpage.c -->
# sources/storage-engines/sqlite/src/dbpage.c

## Purpose

`dbpage.c` implements the optional `sqlite_dbpage` virtual table, available for test builds or `SQLITE_ENABLE_DBPAGE_VTAB` when virtual tables are enabled. It exposes raw database pages through pager APIs so reads see uncommitted and WAL-backed changes, and writes can replace pages or request truncation.

## Important APIs, Types, and Functions

- `DbpageCursor` stores scan state: page number range, pager pointer, page-1 reference, schema index, and page size.
- `DbpageTable` stores the owning `sqlite3` connection plus pending truncate target (`iDbTrunc`, `pgnoTrunc`).
- `dbpageConnect()` declares `pgno INTEGER PRIMARY KEY`, `data BLOB`, and hidden `schema`; configures the module as `SQLITE_VTAB_DIRECTONLY` and all-schema aware.
- `dbpageBestIndex()` plans optional `schema=` and `pgno=` constraints.
- `dbpageFilter()` resolves the schema, pager, page size, last page, optional page number, and pins page 1.
- `dbpageColumn()` returns page number, raw page blob, or schema name; the pending-byte page is returned as a zero blob.
- `dbpageUpdate()` implements replacement/insert-like writes and insert-NULL truncation requests.
- `dbpageBeginTrans()`, `dbpageBegin()`, `dbpageSync()`, and `dbpageRollbackTo()` coordinate write transaction and delayed truncation.
- `sqlite3DbpageRegister()` registers `"sqlite_dbpage"`.

## Control Flow and Behavior

Queries default to the main schema unless a usable hidden `schema=` constraint supplies another database name. Full scans visit page 1 through `sqlite3BtreeLastPage()`, while `pgno=` constrains the scan to one page or no rows if out of range. The cursor keeps a page-1 reference while scanning, likely to stabilize pager state and database header access.

Data reads use `sqlite3PagerGet()` on each requested page and return a transient copy of exactly one page. The page containing `PENDING_BYTE` is treated specially because requesting it from the pager is corrupt; the module returns a zero blob of page size.

Writes are disallowed under defensive mode and delete operations are rejected. Updates require matching old/new page numbers; inserts behave as replacement. The target page must be in `1..4294967294`. Data must be a blob of exact page size, except `INSERT` with NULL data and `pgno > 1`, which records a pending truncation to `pgno-1`. Writes open transactions on all attached B-trees because the module cannot know in advance which schema might be updated. Actual page bytes are copied after `sqlite3PagerWrite()`. Truncation is delayed until xSync via `sqlite3PagerTruncateImage()`.

## State and Persistence

Read scans hold pager references. Successful blob writes mutate database pages within the surrounding SQLite transaction. Truncation state is table-level and pending until sync; rollback-to and new transactions clear it. Defensive mode prevents writes, and normal pager journaling/WAL semantics provide durability or rollback.

## Dependencies and Integration Points

This file depends on virtual table APIs, B-tree and pager internals, schema-name lookup, table-valued function support, transaction hooks, `SQLITE_Defensive`, and the pending-byte constant. It integrates with SQL as the `sqlite_dbpage` eponymous module and is intentionally direct-only to block unsafe use from schema objects such as triggers or views.

## Risks and Edge Cases

The module can corrupt databases if misused, which is why direct-only and defensive checks matter. Truncation uses `INSERT(pgno,NULL)` semantics and is staged; errors after staging must clear `pgnoTrunc`. Opening write transactions on all databases may have locking side effects. The pending-byte page behavior is synthetic. Page-size mismatches, invalid schema names, bad page numbers, attempts to delete, and attempts to change page numbers must report errors through `zErrMsg`.

## Test Signals

Tests should cover full scans and single-page scans, attached schema selection, unknown schema returning no rows or error depending path, reads through WAL/uncommitted pager state, pending-byte zero blob, exact page-size enforcement, defensive-mode read-only errors, update versus insert page-number rules, insert NULL truncation and rollback cancellation, transaction opening failures, and disabled-module registration stubs.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/dbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/dbstat.c -->
# sources/storage-engines/sqlite/src/dbstat.c

## Purpose

`dbstat.c` implements the optional `dbstat` virtual table used by `sqlite3_analyzer` and diagnostics to report B-tree page layout, payload, unused bytes, page paths, overflow chains, offsets, and aggregate space usage by table or index.

## Important APIs, Types, and Functions

- `zDbstatSchema` declares visible columns (`name`, `path`, `pageno`, `pagetype`, `ncell`, `payload`, `unused`, `mx_payload`, `pgoffset`, `pgsize`) plus hidden `schema` and `aggregate`.
- `StatCell` records per-cell local payload, child page, overflow pages, last overflow payload, and overflow iteration state.
- `StatPage` owns a copied page buffer, path string, decoded flags, cells, right-child page, unused bytes, and max payload.
- `StatCursor` owns the root-page statement, traversal stack, aggregate flag, output fields, and running counters.
- `statBestIndex()` recognizes `schema=`, `name=`, `aggregate=`, and ordered output by `(name,path)`.
- `statFilter()` builds a query over `sqlite_schema` plus the schema table root and initializes traversal.
- `statGetPage()` copies pager page data into a padded buffer.
- `statDecodePage()` parses B-tree headers, cells, freeblocks, local payload, and overflow chains.
- `statNext()` performs depth-first traversal and emits either each page/overflow page or one aggregate row per B-tree.
- `sqlite3DbstatRegister()` registers `"dbstat"`.

## Control Flow and Behavior

The module starts from a prepared statement that lists root pages: `sqlite_schema` page 1 plus every schema object with a nonzero rootpage. Optional `name=` filters this list, and optional `schema=` chooses an attached database. The cursor uses `aPage[32]` as a traversal stack. For non-aggregate scans, each B-tree page and overflow page becomes a row with a path string. For aggregate scans, `statNext()` keeps walking until the current B-tree is exhausted, accumulating counts into one row.

`statDecodePage()` copies the page image before decoding and adds 256 bytes of padding to tolerate limited overreads on corrupt data, matching pager/B-tree safety assumptions. It decodes table/index leaf/internal flags, cell pointer arrays, freeblock chains, right-child pointers, varint payload sizes, rowids for table leaves, local payload sizes, and overflow page chains by following pager pages. If page structure is corrupt, it clears cells, sets flags to zero, and later reports `pagetype='corrupted'`.

Overflow rows are emitted before descending into the child page associated with the cell, matching the documented binary path ordering. `statSizeAndOffset()` usually computes offset as `(pageno-1)*page_size`, but asks ZIPVFS via file-control opcode `230440` for compressed page size/offset when available.

## State and Persistence

The module is read-only. It allocates and frees page buffers, cell arrays, overflow arrays, path strings, and a root-page statement per cursor. It reads pager pages and follows B-tree state as of the current connection snapshot. Aggregate counters accumulate page counts, payload, unused bytes, page size, and max payload.

## Dependencies and Integration Points

This file depends on virtual table APIs, SQLite internal pager/B-tree APIs, schema querying, varint decoding, page-size/reserve-byte APIs, OS file-control for ZIPVFS, memory allocation, and SQLite string formatting. It is direct-only because it exposes low-level file layout. It supports the `sqlite3_analyzer` tool and SQL-level inspection.

## Risks and Edge Cases

Corrupt pages can contain invalid flags, freeblock loops, bad cell offsets, impossible payload sizes, or overflow chains pointing to unreadable pages. The decoder attempts to avoid undefined behavior but may return pager errors when following overflow pages. Traversal depth is limited by `aPage[32]`; deeper structures return `SQLITE_CORRUPT_BKPT`. `statResetCsr()` must clear page allocations before resetting the root statement because OOM can reset pager state. `name=` SQL generation lacks an intervening space before `WHERE` in the appended string, so tests should confirm the generated statement is accepted or catch regressions around this path.

## Test Signals

Tests should cover ordinary rowid and WITHOUT ROWID tables, indexes, overflow payloads, aggregate and non-aggregate modes, attached schema selection, `name=` filtering, order-by consumption, ZIPVFS file-control behavior, corrupted page flags/freeblocks/cell offsets, overflow pager failures, deep B-tree corruption, OOM cleanup, schema page row inclusion, and disabled-module registration stubs.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/dbstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/delete.c -->
# sources/storage-engines/sqlite/src/delete.c

## Purpose

`delete.c` generates VDBE bytecode for `DELETE FROM` statements and provides shared helpers used by DELETE, UPDATE, INSERT, triggers, foreign keys, and index maintenance. It handles table lookup, read-only policy, view materialization, optional `ORDER BY/LIMIT` rewriting, truncate optimization, one-pass deletion, virtual tables, row triggers, foreign keys, change counts, and index-entry deletion.

## Important APIs, Types, and Functions

- `sqlite3SrcListLookup()` resolves a single-table `SrcList` and handles `INDEXED BY`.
- `sqlite3CodeChangeCount()` emits row-change result code after `OP_FkCheck`.
- `vtabIsReadOnly()`, `tabIsReadOnly()`, and `sqlite3IsReadOnly()` enforce virtual table, view, system table, shadow table, trusted-schema, and writable-schema restrictions.
- `sqlite3MaterializeView()` evaluates a view into an ephemeral table for INSTEAD OF trigger processing.
- `sqlite3LimitWhere()` rewrites `DELETE/UPDATE ... WHERE ... ORDER BY ... LIMIT ...` into a `rowid IN (SELECT ...)` or primary-key vector `IN` expression.
- `sqlite3DeleteFrom()` is the main code generator for DELETE statements.
- `sqlite3GenerateRowDelete()` emits bytecode to delete one row, including OLD registers, BEFORE/AFTER triggers, foreign-key checks/actions, index deletion, and table deletion.
- `sqlite3GenerateRowIndexDelete()` emits `OP_IdxDelete` for all relevant indexes.
- `sqlite3GenerateIndexKey()` builds index key registers and optionally records partial-index skip labels.
- `sqlite3ResolvePartIdxLabel()` resolves partial-index skip labels.

## Control Flow and Behavior

`sqlite3DeleteFrom()` first resolves the target table, finds triggers, determines whether foreign keys make the statement complex, applies the optional update/delete-limit rewrite, initializes views, checks read-only and authorizer rules, assigns cursors, opens a write operation, materializes views if needed, resolves WHERE expressions, and optionally initializes a row-change counter.

If the statement is a simple full-table delete, the authorizer did not return `SQLITE_IGNORE`, there are no triggers/FKs, the table is not virtual, and preupdate hooks are absent, it emits `OP_Clear` for the table and indexes. Otherwise it builds a WHERE loop to collect rowids or primary keys. Rowid tables use a RowSet for two-pass deletes; WITHOUT ROWID tables use an ephemeral table containing primary-key records. If the query planner supports one-pass deletion, the row key is kept in registers and cursors already positioned by the WHERE loop are reused.

The actual row deletion path handles virtual tables with `OP_VUpdate` and ordinary tables through `sqlite3GenerateRowDelete()`. For ordinary tables, row deletion seeks the row if not already positioned, populates OLD.* registers when triggers or FKs require them, fires BEFORE triggers, re-seeks if triggers may have moved/deleted the row, performs FK checks, deletes secondary index entries, emits `OP_Delete` for the canonical table or primary-key cursor, runs FK actions, and fires AFTER triggers.

`sqlite3GenerateRowIndexDelete()` skips the primary-key index for WITHOUT ROWID tables and can skip a cursor already positioned by one-pass planning. It uses `sqlite3GenerateIndexKey()` to load index columns, evaluate partial-index predicates, reuse registers from the prior index when safe, and generate record keys as needed.

## State and Persistence

The file emits VDBE programs rather than executing deletions immediately. Runtime persistence is through VDBE opcodes that mutate table and index B-trees, virtual tables, autoincrement metadata, foreign-key side effects, and change counters. During code generation it mutates parser state such as cursor numbers, memory register allocation, trigger context, `isMultiWrite`, authorization context, and temporary expression trees. Cleanup always deletes source lists and expressions.

## Dependencies and Integration Points

This code is tightly integrated with the parser, name resolver, WHERE planner, VDBE emitter, B-tree cursor opening, authorization, trigger subsystem, foreign-key subsystem, virtual table subsystem, view expansion, autoincrement handling, update/delete-limit extension, preupdate/update hooks, and schema policy flags. It also shares helpers with UPDATE and integrity-check/index code paths.

## Risks and Edge Cases

DELETE semantics are highly conditional. The truncate optimization must be disabled for authorizer `SQLITE_IGNORE`, triggers, FKs, virtual tables, and preupdate hooks so hooks and constraints observe row-level behavior. BEFORE triggers can move cursors or delete the row, requiring a re-seek and disabling no-seek index optimization. WITHOUT ROWID primary-key vectors must match SELECT outputs in `sqlite3LimitWhere()`. Partial-index predicates can clobber reused registers, so prior-key caching is disabled after evaluating them. Virtual table direct-only/trusted-schema risk checks must reject unsafe trigger or DDL usage. Cleanup must avoid leaking duplicated WHERE/ORDER/LIMIT trees across rewrite paths.

## Test Signals

Tests should include simple rowid deletes, WITHOUT ROWID deletes, full-table truncate optimization and cases that disable it, `ORDER BY/LIMIT/OFFSET` deletes, composite primary-key `IN` rewrites, views with INSTEAD OF triggers, BEFORE triggers that delete or move rows, AFTER triggers, cascading and restricting foreign keys, virtual table deletes and read-only virtual tables, direct-only and innocuous virtual table policy under trusted-schema settings, system/shadow table restrictions, authorizer `SQLITE_DENY` and `SQLITE_IGNORE`, count-changes behavior, preupdate/update hooks, partial indexes, expression indexes, one-pass single and multi-row plans, and OOM cleanup paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/delete.c -->
