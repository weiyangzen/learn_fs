# subset-b-008747 Research

Grouped research report for SQLite misc extensions in `sources/storage-engines/sqlite/ext/misc`. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/spellfix.c -->
# sources/storage-engines/sqlite/ext/misc/spellfix.c

## Purpose
Implements SQLite's `spellfix1` extension: scalar helper functions for transliteration, phonetic hashing, script detection, fixed-cost edit distance, configurable Unicode edit distance, and a writable `spellfix1` virtual table for fuzzy vocabulary lookup.

## Important APIs, Types, And Functions
The extension registers `spellfix1_translit`, `spellfix1_editdist`, `spellfix1_phonehash`, `spellfix1_scriptcode`, `editdist3`, and module `spellfix1`. Core types include `EditDist3Config`, `EditDist3Lang`, `EditDist3Cost`, `EditDist3FromString`, `spellfix1_vtab`, `spellfix1_cursor`, and `MatchQuery`. Important functions are `phoneticHash`, `editdist1`, `editDist3ConfigLoad`, `editDist3Core`, `transliterate`, `scriptCodeSqlFunc`, `spellfix1Init`, `spellfix1BestIndex`, `spellfix1FilterForMatch`, `spellfix1RunQuery`, `spellfix1FilterForFullScan`, `spellfix1Column`, `spellfix1Update`, and `spellfix1Register`.

## Control Flow
On load, `sqlite3_spellfix_init()` calls `spellfix1Register()`. `xCreate` creates a shadow table named `<vtab>_vocab` with `id`, `rank`, `langid`, `word`, `k1`, and `k2`, plus an index on `(langid,k2)`. `xBestIndex` recognizes `word MATCH`, optional `langid`, `top`, `scope`, distance bounds, and rowid equality. MATCH scans transliterate the query, optionally precompile the Unicode edit-distance source, build a phonetic-hash range, scan the shadow table by `langid` and `k2`, compute edit distance, keep the best ranked rows, then sort by score. Full scans and rowid lookups prepare direct shadow-table SELECTs.

## State And Persistence Behavior
Persistent state is in the shadow vocabulary table and its index. Inserts and updates compute `k1` from a transliterated word or `soundslike`, lower-case it, compute `k2` with `phoneticHash`, and write shadow rows. Deletes remove by `id`. `command='reset'` clears cached edit costs, and `command='edit_cost_table=...'` changes the cost table reference. Virtual-table instances cache database/table names and loaded edit-cost configuration; cursors own result arrays, prepared statements, and pattern strings.

## Dependencies And Integration Points
Depends on SQLite extension, virtual table, scalar function, memory, statement, and SQL formatting APIs. It integrates with SQLite's virtual-table planner, shadow-table storage, `sqlite3_vtab_on_conflict()`, `sqlite3_declare_vtab()`, `sqlite3_create_module()`, and application-provided edit-cost tables.

## Risks And Edge Cases
`editdist1` only accepts ASCII and rejects very large inputs; `editdist3` caps input sizes and treats costs >=10000 as infinite. Transliteration uses a fixed sorted table and maps unknown non-ASCII to `?`. MATCH quality depends heavily on the phonetic hash prefix scope and shadow-table `k2` index. Shadow SQL is dynamically generated but uses `%w`/`%Q` quoting for identifiers and values. Cursor result resizing can drop accumulated rows on allocation failure. `xUpdate` allows control commands through hidden columns, so tests should cover invalid commands and cost-table reloads.

## Test Signals
Useful tests include scalar transliteration/phonehash/edit-distance fixtures, `editdist3` custom cost tables, script-code cases for Latin/Cyrillic/Greek/Hebrew/Arabic/mixed/none, virtual-table insert/update/delete/rename/drop behavior, MATCH with `top`, `scope`, `langid`, distance bounds, prefix `*`, rowid lookup, conflict modes, and OOM/error propagation from shadow SQL.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/spellfix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/sqlar.c -->
# sources/storage-engines/sqlite/ext/misc/sqlar.c

## Purpose
Provides `sqlar_compress(X)` and `sqlar_uncompress(X,SZ)`, helper SQL functions used by SQLite's SQL archive support to store and restore zlib-compressed file payloads.

## Important APIs, Types, And Functions
`sqlarCompressFunc()` uses zlib `compressBound()` and `compress()` against BLOB input. `sqlarUncompressFunc()` uses zlib `uncompress()` with caller-supplied uncompressed size. `sqlite3_sqlar_init()` registers both functions as UTF-8 innocuous scalar functions.

## Control Flow
Compression only attempts zlib compression for BLOB values. If allocation fails it reports `SQLITE_NOMEM`; if zlib fails it reports an SQL error; if compressed output is not smaller than the original, it returns the original value. Uncompression returns the original value when `SZ<=0` or `SZ` equals the input byte length, otherwise it allocates `SZ` bytes and calls `uncompress()`.

## State And Persistence Behavior
The extension keeps no durable state. It transforms values for SQL statements. Persistence happens only when callers store returned blobs in an SQLar table.

## Dependencies And Integration Points
Depends on `sqlite3ext.h`, SQLite result/value/memory APIs, and zlib. It is integrated by the shell and any application that loads the extension and calls the functions.

## Risks And Edge Cases
`SZ` is trusted as the expected uncompressed size and is cast to zlib's `uLongf`; extremely large values can fail allocation or be problematic on platforms where zlib length types are narrower. Corrupt compressed data returns an SQL error. Non-BLOB compression inputs pass through unchanged, which preserves SQL type but may surprise callers expecting BLOB-only output.

## Test Signals
Tests should cover round trips, incompressible data pass-through, non-BLOB values, `SZ<=0`, `SZ==input size`, corrupt compressed blobs, very large size requests, and builds without zlib linkage.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/sqlar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/sqlite3_stdio.c -->
# sources/storage-engines/sqlite/ext/misc/sqlite3_stdio.c

## Purpose
Implements Windows-only UTF-8 aware stdio wrappers declared by `sqlite3_stdio.h`. On non-Windows platforms the file compiles to a no-op.

## Important APIs, Types, And Functions
Exports `sqlite3_fopen`, `sqlite3_popen`, `sqlite3_fgets`, `sqlite3_fputs`, `sqlite3_fprintf`, `sqlite3_vfprintf`, and `sqlite3_fsetmode`. Internal helpers include `UseBinaryWText()` and `piecemealOutput()`. Compile-time options include `SQLITE_U8TEXT_ONLY`, `SQLITE_U8TEXT_STDIO`, and `SQLITE_USE_W32_FOR_CONSOLE_IO`.

## Control Flow
File and process open wrappers convert UTF-8 paths/commands and modes to UTF-16 and call `_wfopen()` or `_wpopen()`. Input from console-like streams reads UTF-16 with either `ReadConsoleW()` or `_O_WTEXT`/`fgetws()`, then converts to UTF-8. Output to console-like streams converts UTF-8 to UTF-16 and writes through `WriteConsoleW()` or `_O_U8TEXT`; simulated binary mode emits ASCII bytes in binary/text mode and switches for non-ASCII segments. Non-console streams use ordinary C stdio.

## State And Persistence Behavior
No persistent data is stored. Two process-global flags, `simBinaryStdout` and `simBinaryOther`, remember simulated binary mode for output streams after `sqlite3_fsetmode()`.

## Dependencies And Integration Points
Depends on Windows APIs, Microsoft CRT mode functions, SQLite memory/formatting APIs, and stdio. It supports CLI and utility code that wants UTF-8 behavior without sprinkling Windows-specific code throughout callers.

## Risks And Edge Cases
The implementation is Windows-specific and relies on CRT mode changes that are process/file-descriptor state. Return values for the wide-output path are approximations rather than exact C stdio semantics. Console detection differs under `SQLITE_U8TEXT_ONLY`, `SQLITE_U8TEXT_STDIO`, and default modes. Allocation or conversion failures generally return null/zero rather than rich diagnostics.

## Test Signals
Windows tests should cover UTF-8 filenames, popen commands, console and redirected input/output, ASCII-only binary output without CRLF translation, non-ASCII rendering, `sqlite3_fsetmode()` transitions, and both Win32 console API and CRT paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/sqlite3_stdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/sqlite3_stdio.h -->
# sources/storage-engines/sqlite/ext/misc/sqlite3_stdio.h

## Purpose
Defines portable UTF-8 stdio interfaces. On Windows it declares wrapper functions implemented in `sqlite3_stdio.c`; elsewhere it aliases them directly to standard C library functions.

## Important APIs, Types, And Functions
The header exposes `sqlite3_fopen`, `sqlite3_popen`, `sqlite3_fgets`, `sqlite3_fputs`, `sqlite3_fprintf`, `sqlite3_vfprintf`, and `sqlite3_fsetmode`. On non-Windows systems these are macros for `fopen`, `popen`, `fgets`, `fputs`, `fprintf`, `vfprintf`, and a no-op mode setter.

## Control Flow
There is no runtime control flow outside macro expansion. Include-time `_WIN32` selection chooses declarations for Windows or macro definitions for other platforms.

## State And Persistence Behavior
The header owns no state. Windows state lives in the companion `.c` file; non-Windows users receive stateless stdio calls.

## Dependencies And Integration Points
Includes `<stdio.h>` everywhere, plus `<stdarg.h>` and `<windows.h>` for Windows declarations. It is meant to be included by SQLite tools or extensions that need consistent UTF-8 file and console behavior.

## Risks And Edge Cases
Callers must link `sqlite3_stdio.c` on Windows or they will get unresolved symbols. `sqlite3_fsetmode()` is intentionally a no-op on non-Windows, so code relying on binary/text mode changes remains platform-specific.

## Test Signals
Build tests should verify Windows declarations link against `sqlite3_stdio.c`, non-Windows macro substitution compiles without the `.c` file, and code can use the wrapper names uniformly.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/sqlite3_stdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/stmt.c -->
# sources/storage-engines/sqlite/ext/misc/stmt.c

## Purpose
Implements the `sqlite_stmt` eponymous virtual table, exposing all prepared statements on the current database connection along with statement status counters and metadata.

## Important APIs, Types, And Functions
Important types are `StmtRow`, `stmt_vtab`, and `stmt_cursor`. Module methods include `stmtConnect`, `stmtOpen`, `stmtFilter`, `stmtNext`, `stmtColumn`, `stmtRowid`, `stmtEof`, `stmtClose`, and `stmtBestIndex`. Public initialization is through `sqlite3StmtVtabInit()` and, when built as an extension, `sqlite3_stmt_init()`.

## Control Flow
`stmtConnect()` declares columns `sql,ncol,ro,busy,nscan,nsort,naidx,nstep,reprep,run,mem` and stores the connection handle. `stmtFilter()` resets cursor-owned rows, walks `sqlite3_next_stmt()`, copies SQL text and status counters into a linked list of `StmtRow` objects, and assigns rowids. Cursor advancement frees the current row and moves to `pNext`; columns read from the snapshot row.

## State And Persistence Behavior
No persistent database state is changed. Cursor state is a snapshot linked list allocated during `xFilter`; the virtual table object stores only the database handle. Statement counters are read without reset by passing `0` to `sqlite3_stmt_status()`.

## Dependencies And Integration Points
Depends on SQLite virtual table support and introspection APIs: `sqlite3_next_stmt`, `sqlite3_sql`, `sqlite3_column_count`, `sqlite3_stmt_readonly`, `sqlite3_stmt_busy`, and `sqlite3_stmt_status`. It is conditionally compiled for core builds with `SQLITE_ENABLE_STMTVTAB` and omitted if virtual tables are disabled.

## Risks And Edge Cases
The snapshot may include the statement currently running the query. Memory use scales with the number and SQL text size of prepared statements. The table is read-only and planner estimates are fixed. If prepared statements are finalized after snapshot creation, copied SQL text and counters remain safe because rows are independent copies.

## Test Signals
Tests should prepare several statements, run some to change counters, query `sqlite_stmt`, verify SQL text, busy/read-only flags, rowid sequence, status counters, no-reset behavior, and clean operation when no other statements exist.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/stmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/stmtrand.c -->
# sources/storage-engines/sqlite/ext/misc/stmtrand.c

## Purpose
Defines `stmtrand([SEED])`, a deterministic pseudo-random SQL function whose sequence is stable for each invocation of a prepared statement and resets with `sqlite3_reset()`.

## Important APIs, Types, And Functions
The `Stmtrand` struct stores two 32-bit generator states. `stmtrandFunc()` implements the generator and statement-local state. `sqlite3_stmtrand_init()` registers arity-one and arity-zero forms.

## Control Flow
On first call within a statement, `stmtrandFunc()` obtains auxdata using a fixed negative key. If absent, it allocates `Stmtrand`, seeds `x` with `seed|1` and `y` with `seed`, and installs it using `sqlite3_set_auxdata()` with `sqlite3_free` as destructor. Each call advances an LFSR-like `x`, advances `y` with a linear congruential step, XORs them, masks to non-negative 31-bit range, and returns an integer.

## State And Persistence Behavior
State is per prepared statement invocation through SQLite auxdata. It is not persisted in the database and is reset when the statement is reset or finalized. Later arguments in the same statement execution are ignored because the first call's auxdata owns the sequence.

## Dependencies And Integration Points
Depends on SQLite scalar function and auxdata APIs. It is intended for repeatable tests that need pseudo-random values inside SQL queries.

## Risks And Edge Cases
The generator is deterministic but not cryptographic. Because auxdata is keyed independently of argument index, the seed is effectively first-use per statement execution. OOM is reported if auxdata allocation or retrieval fails after set.

## Test Signals
Tests should verify identical sequences across resets for the same seed, different seeds produce different sequences, zero-argument behavior, multiple calls within one row/statement advance the sequence, and OOM paths if fault injection is available.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/stmtrand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/templatevtab.c -->
# sources/storage-engines/sqlite/ext/misc/templatevtab.c

## Purpose
Provides a minimal eponymous-only read-only virtual table template for extension authors. The concrete sample table returns 10 rows with columns `a` and `b`.

## Important APIs, Types, And Functions
Types are `templatevtab_vtab` and `templatevtab_cursor`. Module methods include `templatevtabConnect`, `templatevtabDisconnect`, `templatevtabOpen`, `templatevtabClose`, `templatevtabFilter`, `templatevtabNext`, `templatevtabEof`, `templatevtabColumn`, `templatevtabRowid`, and `templatevtabBestIndex`. `sqlite3_templatevtab_init()` registers module `templatevtab`.

## Control Flow
`xConnect` declares `CREATE TABLE x(a,b)` and allocates the table object. `xOpen` allocates a cursor. `xFilter` initializes rowid to 1, `xNext` increments rowid, `xEof` stops at rowid >= 10, and `xColumn` returns `1000+rowid` for `a` and `2000+rowid` for `b`. `xBestIndex` reports fixed cost and row estimate.

## State And Persistence Behavior
There is no persistent state. The only cursor state is `iRowid`; the table object has no additional fields beyond the base object.

## Dependencies And Integration Points
Depends on SQLite extension and virtual table APIs. It intentionally implements only required methods and leaves write, transaction, rename, shadow-name, and integrity hooks null.

## Risks And Edge Cases
As a template, it is intentionally incomplete for real applications. It ignores constraints and arguments, is read-only, eponymous-only, and returns fixed estimates. Authors copying it must add validation, constraints, storage, and error handling appropriate to their domain.

## Test Signals
The basic test is loading the module and verifying `SELECT rowid,a,b FROM templatevtab` returns 9 visible rows with rowids 1 through 9 under the current `iRowid>=10` EOF rule, plus clean open/close under repeated scans.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/templatevtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/tmstmpvfs.c -->
# sources/storage-engines/sqlite/ext/misc/tmstmpvfs.c

## Purpose
Implements `tmstmpvfs`, a VFS shim that records page timestamps in the 16-byte reserved region of database pages and optionally emits per-connection binary event logs.

## Important APIs, Types, And Functions
Primary types are `TmstmpFile` and `TmstmpLog`. VFS methods include `tmstmpOpen` and pass-through wrappers for delete/access/path/dlopen/randomness/time/system-call APIs. I/O methods include `tmstmpRead`, `tmstmpWrite`, `tmstmpFileControl`, shared-memory wrappers, fetch/unfetch wrappers, and `tmstmpClose`. Registration is through `tmstmpRegisterVfs()`, `sqlite3_tmstmpvfs_init()`, and static-link helpers `sqlite3_register_tmstmpvfs()`/`sqlite3_unregister_tmstmpvfs()`.

## Control Flow
Loading registers `tmstmpvfs` as the default VFS above the previous default. `xOpen` wraps main database and WAL files; other files bypass the shim. Database opens allocate a `TmstmpLog` and log filename under `<database>-tmstmp/`; WAL opens find the partner DB file through `sqlite3_database_file_object()`. `xRead` of the database header discovers page size and whether reserved bytes equal 16. `xWrite` observes WAL frame headers, WAL resets, checkpoint writes, and rollback-mode DB writes. It timestamps database page reserved bytes only when reserve size is exactly 16 and logs open/write/checkpoint/close events when a log can be opened.

## State And Persistence Behavior
The VFS persists timestamp metadata in each database page's reserved bytes. WAL frames are not modified, preserving WAL checksums; timestamps are applied when frames are checkpointed into the database or when rollback-mode writes update the database file. Logs are external binary files created lazily only if the `<database>-tmstmp` directory exists and a write event needs flushing. Runtime state tracks page size, WAL salt, frame number, checkpoint mode, partner DB/WAL handles, and buffered log records.

## Dependencies And Integration Points
Depends on SQLite VFS and I/O method contracts, file-control operations `SQLITE_FCNTL_VFSNAME`, `SQLITE_FCNTL_CKPT_START`, and `SQLITE_FCNTL_CKPT_DONE`, process ID APIs, stdio logging, `sqlite3_randomness()`, and `sqlite3_database_file_object()`.

## Risks And Edge Cases
`tmstmpWrite()` casts SQLite's write buffer to mutable bytes to fill reserved space before forwarding to the underlying VFS. The shim assumes page writes include the reserved tail and that checkpoint file-control calls bracket checkpoint writes. Logging silently disables itself if the log file cannot be opened. Partner linkage only works for WAL opens associated with a wrapped DB handle. Device characteristics clear `SQLITE_IOCAP_SUBPAGE_READ`, which can affect upper-layer assumptions.

## Test Signals
Tests should create a database with `SQLITE_FCNTL_RESERVE_BYTES=16`, perform rollback and WAL writes, checkpoint WAL frames, inspect reserved bytes for timestamp/frame/salt/flag fields, verify VFS name includes `tmstmp`, verify log records when `<db>-tmstmp` exists, and confirm ordinary reserve=0 databases remain functionally unchanged.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/tmstmpvfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/totype.c -->
# sources/storage-engines/sqlite/ext/misc/totype.c

## Purpose
Implements `tointeger(X)` and `toreal(X)`, strict conversion helpers that return a converted value only when the input can be represented losslessly according to this extension's rules.

## Important APIs, Types, And Functions
Important helpers are `totypeAtoi64`, `totypeAtoF`, `totypeDoubleToInt`, endian macros, and constants for 64-bit integer bounds. SQL functions are `tointegerFunc` and `torealFunc`; `sqlite3_totype_init()` registers both as deterministic innocuous functions.

## Control Flow
`tointeger` accepts existing integers, floats exactly equal to their int64 cast, 8-byte little-endian integer blobs, and text parsed as an int64 with no extra characters. `toreal` accepts existing floats, integers that round-trip through double to int64, 8-byte big-endian IEEE754 blobs, and text parsed by the local floating-point parser with no leading/trailing whitespace or junk. Non-lossless cases return SQL NULL.

## State And Persistence Behavior
No state is stored. The functions only inspect input values and return converted values or NULL.

## Dependencies And Integration Points
Depends on SQLite scalar function APIs and local numeric parsing copied/adapted from SQLite internals. It is useful in tests or SQL that needs stricter conversion than SQLite's normal affinity rules.

## Risks And Edge Cases
Text parsing is intentionally strict and not identical to SQLite affinity conversion. Blob integer and real byte orders differ by design: little-endian for integer, big-endian for real. Floating-point edge handling includes infinities/underflow behavior from C doubles. Integer bounds around `9223372036854775808` require careful testing.

## Test Signals
Tests should cover every SQLite type, exact and inexact float-to-int cases, int-to-real precision loss, boundary int64 strings, invalid strings with whitespace/junk, zero and signed zero, exponent extremes, and endian-sensitive blob conversions.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/totype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/uint.c -->
# sources/storage-engines/sqlite/ext/misc/uint.c

## Purpose
Registers the `uint` collation, which compares text lexicographically except that embedded digit runs compare by unsigned numeric magnitude.

## Important APIs, Types, And Functions
`uintCollFunc()` implements the collation. `sqlite3_uint_init()` registers it with `sqlite3_create_collation()`.

## Control Flow
The comparator walks both byte strings. When both current bytes are digits, it skips leading zeros, compares digit-run length to determine magnitude, then falls back to `memcmp()` for equal-length runs. Non-digit bytes compare by ordinary byte difference, and exhausted input compares by remaining length.

## State And Persistence Behavior
The collation keeps no state and writes no data. Persistent impact occurs when schemas or indexes use `COLLATE uint`; index ordering then depends on this comparator.

## Dependencies And Integration Points
Depends on SQLite collation registration and C `isdigit()`/`memcmp()`. It integrates with ORDER BY, comparisons, and indexes that select this collation.

## Risks And Edge Cases
Only ASCII digit bytes are numeric. Signs, decimal points, and exponent notation are treated as normal text. Leading zeros do not affect numeric magnitude, so distinct strings may compare equal across a numeric run until later bytes differ. Passing signed non-ASCII bytes to `isdigit()` can be locale/undefined-behavior sensitive because the code does not cast to unsigned char.

## Test Signals
Tests should compare natural-sort examples, leading-zero equivalence, arbitrary-length digit runs beyond 64 bits, mixed text and digits, signs/decimals, empty strings, and indexed ORDER BY behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/uint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/unionvtab.c -->
# sources/storage-engines/sqlite/ext/misc/unionvtab.c

## Purpose
Implements read-only `unionvtab` and `swarmvtab` virtual tables that expose multiple rowid tables with compatible schemas and non-overlapping rowid ranges as one virtual table.

## Important APIs, Types, And Functions
Key structs are `UnionSrc`, `UnionTab`, and `UnionCsr`. Important functions include `unionConnect`, `unionSourceCheck`, `unionSourceToStr`, `unionOpenDatabase`, `unionOpenDatabaseInner`, `unionConfigureVtab`, `unionFilter`, `unionNext`, `doUnionNext`, `unionBestIndex`, `unionFinalizeCsrStmt`, `unionIncrRefcount`, and `createUnionVtab`.

## Control Flow
`unionConnect()` requires TEMP schema, prepares the source SQL sorted by minimum rowid, builds `aSrc`, rejects empty sources and overlapping ranges, validates schemas, declares a virtual schema from the first source, and records the integer primary key column if present. `unionvtab` sources must already be in the main connection or attached databases. `swarmvtab` treats the first source column as a filename/URI, opens source databases lazily, optionally invokes `missing` and `openclose` UDFs, and enforces a maximum open-source cache. `xBestIndex` consumes rowid or integer-primary-key equality/range constraints. `xFilter` builds a UNION ALL query for `unionvtab` or scans one swarm source at a time.

## State And Persistence Behavior
The virtual tables are read-only. Runtime state includes source metadata, optional callback statements, open swarm database handles, a closable LRU-like list, per-source user counts, and cursor statements. No source data is modified.

## Dependencies And Integration Points
Depends on SQLite virtual table APIs, `pragma_table_info`, `sqlite3_table_column_metadata`, `sqlite3_open_v2()` with `SQLITE_OPEN_READONLY|SQLITE_OPEN_URI`, prepared statements, and application UDFs for swarm file materialization and open/close notification.

## Risks And Edge Cases
Correctness depends on truthful, non-overlapping rowid bounds from the configuration query. `unionvtab` validates all source schemas at connect time, while `swarmvtab` validates each database as opened and compares to the first schema string. Dynamic SQL quotes identifiers, but source SQL and callback names remain user-provided configuration. `maxopen` is best effort because active cursors pin sources. The read-only module does not prevent underlying source tables from changing row ranges after connection.

## Test Signals
Tests should cover TEMP-only enforcement, wrong argument counts, empty source SQL, overlapping ranges, schema mismatch, rowid and integer-primary-key constraints, range boundary off-by-one cases, read-only update rejection, swarm missing/openclose callbacks, maxopen closure behavior, context columns, SQL parameter binding options, and concurrent cursors.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/unionvtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/urifuncs.c -->
# sources/storage-engines/sqlite/ext/misc/urifuncs.c

## Purpose
Exposes selected SQLite filename and URI C APIs as SQL functions for testing and demonstration.

## Important APIs, Types, And Functions
Functions include `sqlite3_db_filename`, `sqlite3_uri_parameter`, `sqlite3_uri_boolean`, `sqlite3_uri_int64`, `sqlite3_uri_key`, `sqlite3_filename_database`, `sqlite3_filename_journal`, and `sqlite3_filename_wal`. Each has a small `func_*` wrapper, and `sqlite3_urifuncs_init()` registers them.

## Control Flow
Each wrapper reads schema/name/default arguments, obtains the current database handle with `sqlite3_context_db_handle()`, resolves the schema filename with `sqlite3_db_filename()`, calls the corresponding SQLite URI/filename API, and returns text, int, or int64. Registration loops through a static table of function names, arities, and callbacks.

## State And Persistence Behavior
No state is stored or modified. Results reflect the connection's current database filenames and URI metadata.

## Dependencies And Integration Points
Depends on SQLite filename URI APIs and scalar function registration. It is useful in tests for URI parameters, WAL/journal filename derivation, and attached database filename introspection.

## Risks And Edge Cases
Functions generally trust schema names and pass through NULL results as SQL NULL via `sqlite3_result_text()`. URI parameter visibility depends on how the database was opened. These functions are not marked deterministic or innocuous, reflecting their connection-dependent behavior.

## Test Signals
Tests should open URI filenames with parameters, attach databases, query all wrappers for valid and invalid schemas, verify default handling for boolean/int64 URI functions, enumerate keys, and compare derived database/journal/WAL filenames.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/urifuncs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/uuid.c -->
# sources/storage-engines/sqlite/ext/misc/uuid.c

## Purpose
Implements UUID helper functions: `uuid()` generates RFC-4122 version-4 text UUIDs, `uuid_str(X)` canonicalizes UUID input to text, and `uuid_blob(X)` converts UUID input to a 16-byte blob.

## Important APIs, Types, And Functions
Helpers include `sqlite3UuidHexToInt`, `sqlite3UuidBlobToStr`, `sqlite3UuidStrToBlob`, and `sqlite3UuidInputToBlob`. SQL functions are `sqlite3UuidFunc`, `sqlite3UuidStrFunc`, and `sqlite3UuidBlobFunc`; `sqlite3_uuid_init()` registers them.

## Control Flow
`uuid()` obtains 16 random bytes, sets version nibble 4 and RFC variant bits, renders canonical lower-case text with hyphens. `uuid_str` and `uuid_blob` accept either 16-byte blobs or text with 32 hex digits, optional braces, and optional hyphens before byte pairs. Invalid input returns NULL. Blob rendering always uses network byte order.

## State And Persistence Behavior
There is no stored state. Generated UUID randomness comes from SQLite's randomness provider; persistence occurs only if callers store results.

## Dependencies And Integration Points
Depends on SQLite randomness and scalar function APIs plus C character classification. The conversion functions are deterministic and innocuous; `uuid()` is innocuous but not deterministic.

## Risks And Edge Cases
Input parsing validates hex shape but does not require version or variant bits for caller-supplied UUIDs. Optional hyphens are more permissive than only canonical placement. `isxdigit()` is called on input bytes from SQLite text; tests should stay mindful of locale/unsigned-char behavior.

## Test Signals
Tests should verify generated UUID shape/version/variant, canonicalization from upper/lower/braced/hyphen-flexible strings, blob-to-string and string-to-blob round trips, invalid length or stray characters returning NULL, and deterministic flags for conversion functions.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/uuid.c -->
