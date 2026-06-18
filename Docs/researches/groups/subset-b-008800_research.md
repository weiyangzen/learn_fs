# subset-b-008800 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/update.c -->
# sources/storage-engines/sqlite/src/update.c

## Purpose
`update.c` is SQLite's UPDATE statement code generator. It lowers parsed `UPDATE`, `UPDATE FROM`, limited UPDATE, view-update, virtual-table update, trigger, foreign-key, generated-column, RETURNING-compatible, and UPSERT `DO UPDATE` paths into VDBE bytecode. The file is not a storage engine by itself, but it is one of the central write-path bridges between SQL syntax and persistent table/index btrees.

## Important APIs, Types, And Functions
The exported entry points are `sqlite3Update()` and `sqlite3ColumnDefault()`. `sqlite3Update()` owns normal table UPDATE code generation and is also reused by `upsert.c` for `ON CONFLICT DO UPDATE`. `sqlite3ColumnDefault()` annotates `OP_Column` reads with ALTER TABLE default values and adds `OP_RealAffinity` for REAL columns stored as integers.

Private helpers include `indexColumnIsBeingUpdated()` and `indexWhereClauseMightChange()` for deciding which indexes must be opened and rewritten; `exprRowColumn()` for synthetic `TK_ROW` references used by `UPDATE FROM`; `updateFromSelect()` for staging key plus SET-expression results into an ephemeral table; and `updateVirtualTable()` for the separate virtual-table `OP_VUpdate` path. Key data structures are `Parse`, `SrcList`, `Table`, `Index`, `ExprList`, `Expr`, `WhereInfo`, `Vdbe`, `NameContext`, `AuthContext`, `Trigger`, and `Upsert`.

## Control Flow
`sqlite3Update()` first resolves the target table, triggers, view status, read-only status, cursor allocation, and the `aXRef[]` mapping from table columns to SET-list expressions. It identifies rowid/IPK and WITHOUT ROWID primary-key changes, rejects writes to generated columns, applies the authorizer, propagates generated-column dependencies through `aXRef[]`, and computes whether foreign-key work or REPLACE conflict handling may be needed.

For `UPDATE FROM`, it calls `updateFromSelect()` to build a SELECT that emits target keys plus SET values into an ephemeral table. For ordinary rowid tables without `UPDATE FROM`, it may collect rowids in a RowSet/ephemeral table before mutation. For WITHOUT ROWID tables, views, or `UPDATE FROM`, it stages composite primary-key records or view rows. For eligible ordinary updates it asks `where.c` for a one-pass plan and disables one-pass multi-row updates if the selected scan index is being modified.

The mutation loop loads old row content when triggers, primary-key changes, or foreign keys need it; computes new row registers; computes generated columns; fires BEFORE triggers; reloads unmodified columns after BEFORE triggers; runs constraint checks; reseeks if conflict handling moved the cursor; performs FK checks; deletes old index entries and possibly the old table row; inserts the new row and index entries; runs FK actions; increments row counts; fires AFTER triggers; and advances either the WHERE cursor or the staged ephemeral table.

Virtual tables bypass the btree rewrite path. `updateVirtualTable()` gathers old rowid, new rowid, and every column value into registers or an ephemeral table, preserves unchanged-column markers with `OPFLAG_NOCHNG`, uses a one-pass strategy only when the virtual table guarantees at most one row, and emits `OP_VUpdate` with the selected conflict policy.

## State And Persistence Behavior
This file persists changes only through generated VDBE opcodes. Persistent effects include table row replacement, index entry deletion/insertion, sqlite_sequence finalization for top-level updates, FK cascading actions, trigger side effects, virtual-table `xUpdate` calls, and VACUUM-independent btree writes coordinated by `sqlite3BeginWriteOperation()` and `sqlite3MultiWrite()`. Intermediate state is held in VDBE registers, RowSets, ephemeral tables, cursor arrays, `aXRef[]`, `aRegIdx[]`, `aToOpen[]`, trigger masks, and `WhereInfo`.

Correctness depends on conservative index maintenance. A false positive in `indexColumnIsBeingUpdated()` or `indexWhereClauseMightChange()` only opens or rewrites extra indexes; a false negative can leave persistent indexes corrupt. Generated columns are treated as updated when their expressions depend on updated columns so constraints and indexes see recomputed values. ALTER TABLE-added defaults are attached to column reads so older records missing appended columns still return the declared default.

## Dependencies And Integration Points
`update.c` depends on name resolution (`resolve.c`), expression code generation (`expr.c`), WHERE planning (`where.c`), SELECT code generation (`select.c`) for `UPDATE FROM`, insert/index helpers (`insert.c`), triggers (`trigger.c`), foreign keys (`fkey.c`), generated columns (`build.c`/expression helpers), authorization (`auth.c`), virtual tables (`vtab.c`), rowsets (`rowset.c`), and UPSERT (`upsert.c`). The VDBE opcodes it emits integrate with `vdbe.c`, btree cursors, preupdate/update hooks, and the RETURNING/count-changes machinery.

## Risks And Edge Cases
High-risk areas are one-pass eligibility, index-change detection, BEFORE-trigger reload semantics, REPLACE conflict handling, primary-key rewrites on WITHOUT ROWID tables, `UPDATE FROM` staging order, and virtual-table no-change markers. Mutating a scan index in one-pass multi-row mode can loop or skip rows, so the fallback check is critical. BEFORE triggers can delete or modify the row being updated; this file intentionally skips later work if the row vanished and reloads only unmodified columns if it survived. `UPDATE FROM` must keep SET-expression columns aligned after key columns in the ephemeral table. UPSERT reuse requires cursors already opened by INSERT and skips normal row discovery.

## Test Signals
Relevant SQLite tests include `update.test`, `update2.test`, `update3.test`, `update4.test`, `updatevtab.test`, `wherelimit.test`, `hook.test`, `trigger*.test`, `fkey*.test`, generated-column tests, `upsert*.test`, and `returning*.test`. Strong regressions are EXPLAIN changes around one-pass UPDATE, failures of `PRAGMA integrity_check` after indexed updates, incorrect row counts, preupdate-hook column mismatches, generated-column update errors, virtual-table `sqlite3_vtab_nochange()` behavior, `UPDATE FROM` result mismatches, and FK cascade differences.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/upsert.c -->
# sources/storage-engines/sqlite/src/upsert.c

## Purpose
`upsert.c` implements SQLite's `INSERT ... ON CONFLICT ... DO NOTHING/DO UPDATE` support around the `Upsert` AST object. It owns allocation, duplication, target analysis, conflict-target-to-index matching, duplicate-clause handling, and the code-generation bridge that invokes `sqlite3Update()` for the `DO UPDATE` action.

## Important APIs, Types, And Functions
The public functions are `sqlite3UpsertDelete()`, `sqlite3UpsertDup()`, `sqlite3UpsertNew()`, `sqlite3UpsertAnalyzeTarget()`, `sqlite3UpsertNextIsIPK()`, `sqlite3UpsertOfIndex()`, and `sqlite3UpsertDoUpdate()`. They operate mainly on `Upsert`, `Parse`, `SrcList`, `Table`, `Index`, `ExprList`, `Expr`, `NameContext`, and `Vdbe`.

`sqlite3UpsertNew()` records the conflict target, optional partial-index target WHERE clause, SET list, optional action WHERE clause, and next clause. `sqlite3UpsertAnalyzeTarget()` resolves target expressions and binds each targeted clause to a matching unique index or to the rowid/IPK. `sqlite3UpsertOfIndex()` chooses the clause for a failing unique index. `sqlite3UpsertDoUpdate()` locates the conflicting row and delegates the action to `sqlite3Update()`.

## Control Flow
Parsing builds a linked list of `Upsert` objects. Before insert code generation relies on the list, `sqlite3UpsertAnalyzeTarget()` resolves conflict-target symbols against the single insert target table. For each targeted clause, it first recognizes a rowid conflict target on rowid tables. Otherwise it scans unique indexes, requiring the same number of key columns, matching partial-index WHERE expressions when present, and expression/collation/column equivalence between target terms and index key terms. Successful matches set `pUpsertIdx`; redundant clauses for the same index are marked `isDup` for compatibility rather than rejected.

During insert conflict handling, `sqlite3UpsertOfIndex()` returns the first applicable clause for the failed unique index, stopping at an untargeted final clause if present. `sqlite3UpsertNextIsIPK()` helps determine whether later clauses can catch an integer-primary-key conflict while skipping duplicate clauses. For `DO UPDATE`, `sqlite3UpsertDoUpdate()` ensures the data cursor points at the conflicting row: it converts an index cursor to a rowid seek for rowid tables or reads primary-key columns from the failing index and verifies the WITHOUT ROWID table cursor with `OP_Found`. It then duplicates the UPSERT source list, applies REAL affinity to `excluded.*` registers, and calls `sqlite3Update()` with the SET and WHERE expressions.

## State And Persistence Behavior
The `Upsert` list is parse-time state and is freed through `sqlite3UpsertDelete()`, including target lists, partial-index WHERE clauses, SET lists, action WHERE clauses, auxiliary source-list ownership in `pToFree`, and chained clauses. Persistent writes happen only through the INSERT code path and the delegated UPDATE bytecode. Analysis mutates `Upsert` nodes by setting `pUpsertIdx`, `isDoUpdate`, `isDup`, cursor fields supplied by INSERT, source-list fields, and register fields for `excluded.*`.

Matching a conflict target to the wrong index would route persistent conflict handling incorrectly. For expression and partial indexes, the file depends on structural expression comparison rather than SQL text identity. Duplicate conflict clauses are deliberately tolerated to preserve older application behavior even though later duplicates never fire.

## Dependencies And Integration Points
`upsert.c` is tightly coupled to `insert.c`, which builds conflict-checking bytecode and stores cursor/register/source context in `Upsert`. It uses `resolve.c` for target name resolution, `expr.c` for expression duplication and comparison, schema/index metadata from `build.c`, VDBE opcodes for row lookup, and `update.c` for the DO UPDATE action. It also relies on table/index conventions for rowid tables, WITHOUT ROWID primary keys, expression indexes, collations, and partial indexes.

## Risks And Edge Cases
Conflict-target matching is the main risk. Collation wrappers, expression indexes, partial-index predicates, unordered target terms, duplicate ON CONFLICT clauses, rowid aliases, and WITHOUT ROWID primary-key lookup all need exact behavior. `sqlite3UpsertDoUpdate()` must not take ownership of the outer INSERT source list, so it duplicates it before calling `sqlite3Update()`. If the failing unique cursor is not the table cursor, rowid or PK seeking must land on the correct table row or report corruption. REAL affinity on `excluded.*` matters because UPDATE code expects hard REAL values for REAL columns.

## Test Signals
The main signals are `upsert*.test`, especially tests with multiple ON CONFLICT clauses, redundant clauses, partial unique indexes, expression indexes, collations, rowid conflict targets, DO NOTHING fallthrough, DO UPDATE WHERE filters, and WITHOUT ROWID tables. Good secondary signals are `insert*.test`, `indexexpr*.test`, `where*.test` for unique index matching, and corruption/error-path tests expecting "ON CONFLICT clause does not match any PRIMARY KEY or UNIQUE constraint".
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/upsert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/utf.c -->
# sources/storage-engines/sqlite/src/utf.c

## Purpose
`utf.c` provides SQLite's internal Unicode text encoding primitives. It reads and writes UTF-8 code points, converts VDBE `Mem` strings among UTF-8, UTF-16LE, and UTF-16BE, handles UTF-16 byte-order marks, counts UTF-8/UTF-16 characters or byte lengths, and exposes debug/test helpers for UTF validation. These routines sit underneath SQL text values, API calls, collations, scalar functions, and database encodings.

## Important APIs, Types, And Functions
Important macros are `WRITE_UTF8`, `WRITE_UTF16LE`, `WRITE_UTF16BE`, and `READ_UTF8`. The first-byte lookup table `sqlite3Utf8Trans1[]` accelerates UTF-8 decoding. Public functions include `sqlite3AppendOneUtf8Character()`, `sqlite3Utf8Read()`, `sqlite3Utf8ReadLimited()`, `sqlite3VdbeMemTranslate()`, `sqlite3VdbeMemHandleBom()`, `sqlite3Utf8CharLen()`, `sqlite3Utf8To8()` in debug test builds, `sqlite3Utf16to8()`, `sqlite3Utf16ByteLen()`, and `sqlite3UtfSelfTest()` in test builds. Key data types are `Mem`, `sqlite3`, `u8`, `u32`, and VDBE memory flags such as `MEM_Str`, `MEM_Term`, subtype, affinity, and allocation ownership bits.

## Control Flow
UTF-8 decode starts with a single byte. For multibyte sequences, `sqlite3Utf8Read()` and `READ_UTF8` fold continuation bytes into a code point and replace NUL overlongs, surrogate encodings, and U+FFFE/U+FFFF with U+FFFD. `sqlite3Utf8ReadLimited()` is a bounded variant used when input is not zero-terminated; it reads at most four bytes and does less validation.

`sqlite3VdbeMemTranslate()` is the main conversion path. UTF-16-to-UTF-16 conversion is an in-place byte swap after making the `Mem` writeable. UTF-8-to-UTF-16 allocates a worst-case output buffer and emits little- or big-endian units. UTF-16-to-UTF-8 reads 16-bit units, combines surrogate pairs, optionally replaces invalid surrogates under `SQLITE_REPLACE_INVALID_UTF`, writes UTF-8 bytes, terminates the buffer, releases the old `Mem` payload, and installs the new allocation with updated flags and encoding.

`sqlite3VdbeMemHandleBom()` detects UTF-16 BOMs, makes the memory writeable, removes the first two bytes, terminates the string, and updates `Mem.enc`. `sqlite3Utf16to8()` wraps a transient `Mem` around API input and asks VDBE memory code to convert it. Character-count helpers advance by encoded characters rather than bytes.

## State And Persistence Behavior
The routines mutate transient in-memory values, not database pages directly. `sqlite3VdbeMemTranslate()` can allocate a new buffer, release the old representation, update `pMem->z`, `zMalloc`, `szMalloc`, `n`, `enc`, and flags, and preserve affinity/subtype bits. BOM handling removes bytes in place. These conversions affect persistent behavior indirectly because values are compared, stored, serialized, and returned through the encoding selected by the database and API.

Invalid UTF handling is intentionally SQLite-specific: overlong encodings for values >= 0x80 are accepted, overlong NULs and surrogate/noncharacters are replaced, and standalone continuation bytes are treated as single-byte values by `sqlite3Utf8Read()`. Those choices are externally visible in functions, collations, and APIs.

## Dependencies And Integration Points
`utf.c` depends on `sqliteInt.h` and `vdbeInt.h`, especially `Mem` ownership and allocation helpers from VDBE memory code. It integrates with `vdbemem.c` through `sqlite3VdbeChangeEncoding()`, SQL functions such as `length()`/`substr()`, collation and comparison paths, UTF-16 public APIs (`sqlite3_open16`, `sqlite3_column_text16`, `sqlite3_complete16`), tokenizer/parser input conversion, and test harness support. Compile-time gates include `SQLITE_OMIT_UTF16`, `SQLITE_TEST`, `SQLITE_DEBUG`, byte-order configuration, and `SQLITE_REPLACE_INVALID_UTF`.

## Risks And Edge Cases
Risks concentrate around buffer sizing, termination, odd UTF-16 byte counts, surrogate-pair handling, and preserving `Mem` ownership flags. UTF-16 input length is forced even in some paths; BOM removal must leave a two-byte terminator. Invalid UTF behavior is compatibility-sensitive and cannot simply be replaced with strict Unicode rules. `sqlite3Utf16to8()` returns the owned `Mem` buffer to the caller, so callers must free it with SQLite allocation discipline. In-place UTF-16 endian swapping requires a writeable buffer and correct `pMem->n` masking.

## Test Signals
Relevant tests include `enc*.test`, `utf16align.test`, `func.test` UTF length cases, `func3.test` encoding-specific function registration, `capi3e.test`, `mutex2.test`, `types.test`, and TCL tests using `sqlite3_column_text16`, `sqlite3_open16`, or `sqlite3_complete16`. Useful low-level signals are `translate_selftest` in test builds, malformed UTF sequences, BOM-prefixed strings, odd byte counts, surrogate pairs, invalid surrogates, UTF-16BE/LE round trips, and memory-fault injection in conversion paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/utf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/util.c -->
# sources/storage-engines/sqlite/src/util.c

## Purpose
`util.c` is a dense collection of SQLite core utility routines used across parsing, VDBE execution, btree record handling, numeric conversion, logging, safety checks, overflow-safe arithmetic, query-planner estimates, and bind-parameter name storage. It does not define one subsystem; it provides shared primitives whose behavior is part of SQLite's public compatibility surface.

## Important APIs, Types, And Functions
Error and parser helpers include `sqlite3FaultSim()`, `sqlite3Error()`, `sqlite3ErrorClear()`, `sqlite3SystemError()`, `sqlite3ErrorWithMsg()`, `sqlite3ProgressCheck()`, `sqlite3ErrorMsg()`, and `sqlite3ErrorToParser()`. Token/string helpers include `sqlite3Strlen30()`, `sqlite3ColumnType()`, `sqlite3Dequote()`, `sqlite3DequoteExpr()`, `sqlite3DequoteNumber()`, `sqlite3DequoteToken()`, `sqlite3TokenInit()`, `sqlite3_stricmp()`, `sqlite3StrICmp()`, `sqlite3_strnicmp()`, and `sqlite3StrIHash()`.

Numeric routines include `sqlite3AtoF()`, `sqlite3Int64ToText()`, `sqlite3Atoi64()`, `sqlite3DecOrHexToI64()`, `sqlite3GetInt32()`, `sqlite3Atoi()`, `sqlite3FpDecode()`, and `sqlite3GetUInt32()`, supported by internal 128/160-bit multiplication and powers-of-ten tables. Binary encoding helpers include `sqlite3PutVarint()`, `sqlite3GetVarint()`, `sqlite3GetVarint32()`, `sqlite3VarintLen()`, `sqlite3Get4byte()`, `sqlite3Put4byte()`, `sqlite3HexToInt()`, and `sqlite3HexToBlob()`. Runtime safety and arithmetic helpers include `sqlite3SafetyCheckOk()`, `sqlite3SafetyCheckSickOrOk()`, `sqlite3AddInt64()`, `sqlite3SubInt64()`, `sqlite3MulInt64()`, `sqlite3AbsInt32()`, `sqlite3LogEstAdd()`, `sqlite3LogEst()`, `sqlite3LogEstFromDouble()`, `sqlite3LogEstToInt()`, and `sqlite3VListAdd()`/lookup helpers.

## Control Flow
The error helpers maintain connection and parse error state. Compile-time errors use `sqlite3ErrorMsg()` to allocate formatted UTF-8 text in `Parse.zErrMsg`, increment `nErr`, set parser `rc`, and respect `db->suppressErr`. Runtime errors use `sqlite3Error()` or `sqlite3ErrorWithMsg()` to update `db->errCode`, `db->pErr`, `db->errByteOffset`, and OS errno fields. `sqlite3ProgressCheck()` polls interrupt and progress callbacks during long prepares.

Text/token helpers operate mostly in place: dequoting removes SQL identifier/string quotes; quoted numeric tokens remove digit separators and reclassify as integer or float; token initialization stores pointer plus 30-bit length. Case-insensitive comparison and hashing use SQLite's `sqlite3UpperToLower` table, so behavior matches identifier rules rather than locale rules.

Numeric conversion parses into bounded integer mantissas and decimal exponents, then uses precomputed powers of ten and wide multiplication to convert between decimal text and IEEE754 doubles. Integer parsing separately handles decimal, optional UTF-16 input in `sqlite3Atoi64()`, and hex literals in `sqlite3DecOrHexToI64()`/`sqlite3GetInt32()`. Varint routines implement SQLite's 1-to-9 byte btree record format with fast paths for small values and careful masking for larger values.

## State And Persistence Behavior
Most state is transient but persistence-critical. Varints and big-endian 4-byte helpers read and write on-disk btree record headers and page metadata. Numeric conversion controls how SQL literals become stored INTEGER or REAL values and how REALs render back to text. `sqlite3Error*` changes connection-visible error state. Safety checks may log misuse through `sqlite3_log()`. `sqlite3FileSuffix3()` can alter journal/WAL/shared-memory filenames under 8.3-name builds. `sqlite3VListAdd()` stores bind-parameter name mappings in parser/VDBE state and can freeze reallocability by convention when pointers are exposed.

## Dependencies And Integration Points
`util.c` depends on `sqliteInt.h`, standard `stdarg.h`, optional `math.h`, compiler intrinsics for overflow/multiplication/byte-swap, the VFS for last OS errors, btree/pager access for special WAL system-error handling, SQLite memory allocation wrappers, tokenizer character-class tables, and global configuration. Consumers span nearly every SQLite subsystem: parser, expression code, printf formatting, VDBE record decoding, btree, pager, JSON and SQL functions, URI handling, bind-parameter APIs, query planner LogEst math, and test fault injection.

## Risks And Edge Cases
The highest-risk code is numeric and binary compatibility code. `sqlite3AtoF()` intentionally uses about 19 significant input digits, so rounding is not arbitrary precision; changing it can alter query results and tests. Integer parsing distinguishes no-prefix, trailing text, overflow, and the special positive `9223372036854775808` case. Varint decoding is optimized and mask-heavy; off-by-one errors corrupt record parsing. Endian helpers must handle unaligned memory safely via `memcpy` in optimized branches. Error-state helpers must not overwrite parser errors in suppressed contexts or lose OS errno details. `VList` realloc rules are subtle because exposed name pointers make later enlargement unsafe.

Overflow-safe arithmetic must preserve the original value on failure. `sqlite3SafetyCheckOk()` intentionally only provides misuse protection, not a hard memory-safety proof. `sqlite3HexToInt()` assumes valid input under assert. LogEst conversion is approximate by design; planner changes can cascade from small table-estimate differences.

## Test Signals
Relevant tests include `atof1.test`, `numcast.test`, `cast.test`, `types*.test`, `printf*.test`, `bind*.test`, `capi*.test`, `misc*.test`, `fault*.test`, `malloc*.test`, `pager*.test`, and VDBE record/format tests that exercise varints. Strong targeted checks include boundary integers around `SMALLEST_INT64`/`LARGEST_INT64`, `9223372036854775808`, hex literals, digit separators in quoted numbers, NaN/Inf handling, very long strings for `sqlite3Strlen30()`, malformed bind parameter names, varint lengths 1 through 9, endian round trips, arithmetic overflow preservation, and fault simulation callbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vacuum.c -->
# sources/storage-engines/sqlite/src/vacuum.c

## Purpose
`vacuum.c` implements the SQL `VACUUM` command and the VDBE runtime operation that rebuilds a database into a compact copy, optionally writing to a separate output file for `VACUUM INTO`. It coordinates SQL schema replay, content copy, btree metadata preservation, pager flags, page-size/autovacuum settings, locking, and cleanup of the temporary attached vacuum database.

## Important APIs, Types, And Functions
The parser-facing entry point is `sqlite3Vacuum(Parse *pParse, Token *pNm, Expr *pInto)`, which emits `OP_Vacuum`. The runtime entry point is `sqlite3RunVacuum(char **pzErrMsg, sqlite3 *db, int iDb, sqlite3_value *pOut)`, called by the VDBE. Private helpers `execSql()` and `execSqlF()` prepare and run SQL against the same connection; when a SELECT returns SQL text, `execSql()` recursively executes only schema-copy statements beginning with `CRE` or `INS`.

Important data types are `sqlite3`, `Parse`, `Vdbe`, `Btree`, `Pager`, `Db`, `sqlite3_value`, `sqlite3_stmt`, and btree metadata constants such as `BTREE_SCHEMA_VERSION`, `BTREE_TEXT_ENCODING`, `BTREE_USER_VERSION`, and `BTREE_APPLICATION_ID`.

## Control Flow
`sqlite3Vacuum()` resolves an optional schema name, rejects the temp database, resolves an optional INTO expression into a register, emits `OP_Vacuum`, and marks the target btree as used. The heavy work occurs when VDBE executes the opcode and calls `sqlite3RunVacuum()`.

`sqlite3RunVacuum()` first rejects invocation inside a transaction or while other statements are active. For `VACUUM INTO`, it validates a text filename and temporarily forces create/readwrite open flags. It saves connection flags, change counters, trace state, and open flags; enables writable schema, built-in preference, attach create/write, comments, and vacuum mode; disables foreign keys, defensive mode, reverse order, and count-rows; and chooses a random attached schema name like `vacuum_...`.

It attaches the transient output database, verifies a `VACUUM INTO` target is empty, configures cache/spill/pager flags and reserved bytes, begins an SQL transaction, starts a btree transaction on the main database, sets target page size/autovacuum, replays table and index creation SQL from the source schema into the vacuum database, copies table contents with generated `INSERT INTO vacuum_db.table SELECT * FROM main.table` statements, copies view/trigger/virtual-table schema rows, preserves selected btree meta values while incrementing the schema cookie, copies the compacted file back with `sqlite3BtreeCopyFile()` for ordinary VACUUM, commits the temp btree, adjusts main page size/autovacuum metadata, then restores flags, closes/detaches the temporary btree, resets schemas, and returns the final rc.

## State And Persistence Behavior
Ordinary VACUUM rewrites the target database file through btree copy, requiring an exclusive transaction and enough temporary space for the vacuum copy and rollback journal. `VACUUM INTO` writes a separate output database and does not copy back into the source. The command preserves text encoding, user version, application id, cache-size metadata, and increments the schema version. It may apply pending `nextPagesize` and `nextAutovac` settings when allowed, but suppresses page-size changes for WAL-mode ordinary VACUUM.

Connection state is deliberately distorted during the operation and then restored: schema writes are allowed, checks and foreign keys are ignored while rebuilding, tracing is disabled, change counters are restored, and all schemas are reset at the end. The temporary attached database is closed manually after forcing `autoCommit=1` so its journal disappears with the pager close.

## Dependencies And Integration Points
`vacuum.c` depends on parser/VDBE code generation, `vdbe.c` `OP_Vacuum`, attach/database-name handling, SQL prepare/step/finalize APIs, btree and pager APIs, schema initialization, SQLite random number generation, URI parameter handling for reserve bytes, transaction state, and schema reset. It interacts with `sqlite_schema` content and therefore with `build.c`, `insert.c`, btree metadata, WAL journal mode, auto-vacuum settings, page-size pragmas, and VFS file behavior.

## Risks And Edge Cases
Security-sensitive behavior is concentrated in `execSql()`: schema SQL returned by SELECT is recursively executed only if it begins with `CREATE` or `INSERT`, limiting attacks that corrupt `sqlite_schema.sql` before VACUUM. Other risks include transaction-state enforcement, active statement detection, output-file existence checks for `VACUUM INTO`, WAL page-size restrictions, exact restoration of connection flags on error, random attached-schema naming collisions, reserved-byte URI handling, and correct manual detach cleanup. Failing after the temporary database is attached must still restore flags and reset schemas.

Because VACUUM rebuilds through SQL text from `sqlite_schema`, malformed or legacy schema entries can surface as prepare/runtime errors. The code assumes enough disk space for large temporary copies. `VACUUM INTO` must not overwrite an existing non-empty file. Btree metadata copy must increment the schema cookie so other connections reload the schema.

## Test Signals
Relevant tests include `vacuum*.test`, `interrupt.test` VACUUM cases, `enc2.test` encoding plus vacuum coverage, `autovacuum*.test`, `wal*.test` page-size/journal interactions, crash and corruption tests involving schema SQL, and `tt3_vacuum.c` concurrent writer/vacuum stress. Strong checks include "cannot VACUUM from within a transaction", "cannot VACUUM - SQL statements in progress", non-text INTO filename errors, output file already exists, page-size changes outside WAL, `PRAGMA integrity_check` after VACUUM, schema cookie changes, VACUUM INTO preserving source database, and cleanup after injected prepare/step/btree failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vacuum.c -->
