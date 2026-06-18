# subset-b-008745 research

Grouped research for SQLite miscellaneous extensions under `sources/storage-engines/sqlite/ext/misc`. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/closure.c -->
# sources/storage-engines/sqlite/ext/misc/closure.c

## Purpose

`closure.c` implements the `transitive_closure` virtual table module. It computes descendants, ancestors, or other graph walks over an application table that stores integer child/parent relationships. A virtual table instance can define default `tablename`, `idcolumn`, and `parentcolumn` arguments, and queries can override those through hidden-column equality constraints.

## Important APIs, types, and functions

The public integration point is `sqlite3_closure_init()`, which registers module name `transitive_closure` unless virtual tables are omitted. `closureModule` provides create/connect, best-index, cursor open/close, filter, next/eof/column/rowid callbacks. `closure_vtab` stores the database handle, module table name, configured source table/columns, and cursor count. `closure_cursor` stores per-scan overrides plus `pClosure` and `pCurrent`.

The implementation uses `closure_avl` as both the visited set and sorted output tree. `closureAvlInsert()`, `closureAvlSearch()`, rotations, and balancing keep seen ids unique and sorted. `closure_queue` plus `queuePush()` and `queuePull()` drive breadth-first traversal by generation depth. `closureDequote()` and `closureValueOfKey()` parse module arguments such as `tablename='group'`.

## Control flow

`closureConnect()` parses module arguments, stores defaults, and declares `CREATE TABLE x(id,depth,root HIDDEN,tablename HIDDEN,idcolumn HIDDEN,parentcolumn HIDDEN)`. `closureBestIndex()` recognizes usable constraints on `root`, `depth`, `tablename`, `idcolumn`, and `parentcolumn`; if required table and column names or `root=?` are missing, it chooses a plan that returns no rows. It also consumes `ORDER BY id ASC` because AVL iteration is sorted by id.

`closureFilter()` clears the cursor, reads the root and optional max depth/table/column overrides from argv positions encoded in `idxNum`, prepares a child lookup query, inserts the root at generation 0, then repeatedly pulls queued nodes and queries rows whose parent column equals the current id. Integer child ids not already present in the AVL tree are inserted and queued with `generation+1`. When traversal finishes, `pCurrent` is set to the first AVL node. `closureNext()` advances by in-order AVL successor.

## State and persistence

The virtual table itself persists only its configured strings inside the SQLite connection. Query results are transient cursor state; no database writes occur. The source hierarchy table is read through a prepared `SELECT` with quoted identifiers. The traversal state is all in memory, with duplicate suppression by id.

## Dependencies and integration points

The extension depends on SQLite loadable extension APIs, virtual table APIs, `sqlite3_mprintf()` identifier quoting, and the source table having integer ids. The opening comments stress an index on the parent column for performance. The module is read-only and has no `xUpdate`.

## Risks

Runtime table and column names are accepted from SQL constraints, so correct quoting with `%w` is essential. Cycles are handled by the visited AVL tree, but very large closures can consume memory. Only integer child ids are followed; non-integer ids are silently ignored. `depth < N` is implemented by decrementing the max generation, so boundary tests matter. Missing root or metadata constraints intentionally produce empty output, which can hide query mistakes.

## Test signals

Useful tests create a small tree with an index on the parent column and verify root self inclusion, depth equality and inequality behavior, ancestor traversal by swapping id/parent columns, per-query overrides, sorted `ORDER BY id`, cycle suppression, empty output without root, and error propagation for bad table/column names.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/closure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/completion.c -->
# sources/storage-engines/sqlite/ext/misc/completion.c

## Purpose

`completion.c` implements the eponymous virtual table `completion`, used to suggest completions for partial SQL input. It returns candidate keywords and schema identifiers, optionally filtered by hidden `prefix` and informed by hidden `wholeline`.

## Important APIs, types, and functions

`sqlite3_completion_init()` calls `sqlite3CompletionVtabInit()`, which registers `completion`. `completion_vtab` stores the SQLite connection. `completion_cursor` stores prefix/whole-line buffers, current candidate text, an active metadata statement, rowid, current phase, and a phase-local counter.

`completionModule` implements `xConnect`, `xBestIndex`, `xOpen`, `xFilter`, `xNext`, `xColumn`, `xRowid`, and cleanup. The table schema is `candidate TEXT, prefix HIDDEN, wholeline HIDDEN, phase HIDDEN`. The module is marked `SQLITE_VTAB_INNOCUOUS`.

## Control flow

`completionBestIndex()` finds equality constraints on `prefix` and `wholeline`, assigns argv positions, omits the hidden constraints, and lowers estimated cost/rows when arguments are supplied. `completionFilter()` copies the prefix and/or whole line into cursor-owned memory. If only `wholeline` is provided, it derives the prefix from the trailing alphanumeric or underscore token. It starts at `COMPLETION_FIRST_PHASE` and calls `completionNext()`.

`completionNext()` advances through phases. It enumerates `sqlite3_keyword_name()` results, then `PRAGMA database_list`, then table/view/trigger names from each attached database's `sqlite_schema`, then column names from `pragma_table_xinfo()` joined to schema rows. Prepared statements are finalized at phase boundaries. Each candidate is case-insensitively compared to `zPrefix`; nonmatching candidates are skipped.

## State and persistence

The module is read-only and holds no persistent state. Cursor state includes copied input strings and one active prepared statement at a time. It queries SQLite metadata dynamically, so attached databases and schema changes affect later scans.

## Dependencies and integration points

It depends on SQLite keyword APIs, pragma table-valued functions, `sqlite3_str` construction, attached database metadata, and virtual table planning. It is intended for interactive shell completion and may return duplicates; callers are expected to use `DISTINCT` and ordering when needed.

## Risks

`wholeline` is currently used only to derive a trailing prefix, not to restrict suggestions to syntactically valid positions. Metadata SQL spans attached databases, so prepare/finalize errors from one database can abort the scan. Candidate lifetime is mixed: keyword names are static, metadata values are copied out with `SQLITE_TRANSIENT` in `xColumn`. Duplicate names are normal behavior.

## Test signals

Tests should verify prefix filtering for keywords and object names, prefix derivation from `wholeline`, rowid monotonicity, phase visibility, behavior with attached databases, duplicate handling by caller queries, and clean EOF when there are no matching candidates.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/completion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/compress.c -->
# sources/storage-engines/sqlite/ext/misc/compress.c

## Purpose

`compress.c` provides scalar SQL functions `compress(X)` and `uncompress(X)` using zlib. The format is zlib-compressed payload prefixed by a SQLite-extension-specific variable-length integer containing the original uncompressed byte count.

## Important APIs, types, and functions

`sqlite3_compress_init()` registers `compress` as innocuous and `uncompress` as innocuous and deterministic. `compressFunc()` obtains the input blob and byte count from `sqlite3_value_blob()` and `sqlite3_value_bytes()`, encodes the original length in one to five 7-bit chunks, calls zlib `compress()`, and returns a blob allocated with `sqlite3_malloc64()`. `uncompressFunc()` decodes the size prefix, allocates the expected output buffer, calls zlib `uncompress()`, and returns the restored blob.

## Control flow

Compression computes a conservative zlib output bound, allocates `nOut+5`, emits the length prefix with the high bit set on the final prefix byte, then compresses after the prefix. Decompression reads up to five prefix bytes, accumulating seven bits per byte until a byte with bit `0x80` is seen; the remaining bytes are passed to zlib along with the decoded output size.

## State and persistence

The extension is stateless. It does not persist metadata outside the returned blob. The original size is embedded in the compressed value, so decompression does not need an external length.

## Dependencies and integration points

It depends on zlib headers and library symbols. The file notes that SQLAR and ZIP also use deflate variants, but this wrapper is not byte-compatible with ZIP or SQLAR because of its custom size prefix.

## Risks

Malformed inputs generally result in a NULL return because zlib errors free the buffer without setting an explicit SQLite error. If the size prefix is absent, `nOut` may be derived from the first bytes anyway and can lead to allocation attempts before zlib rejects the stream. Length handling uses `unsigned int`, so extremely large SQLite values depend on platform limits. The functions do not special-case SQL NULL input beyond SQLite's blob/bytes behavior.

## Test signals

Good coverage round-trips empty, text, binary with embedded NULs, and large blobs; verifies deterministic output for the same input and NULL/error behavior for malformed blobs, truncated prefixes, and non-zlib payloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/csv.c -->
# sources/storage-engines/sqlite/ext/misc/csv.c

## Purpose

`csv.c` implements a read-only virtual table module named `csv` for reading CSV content from either a filesystem file (`filename=`) or inline text (`data=`). It can infer columns, use a header row, accept an explicit schema, or use a fixed `columns=N` count.

## Important APIs, types, and functions

`sqlite3_csv_init()` registers `csv`; under `SQLITE_TEST` it also registers `csv_wr`, a faux writable variant whose `xUpdate` returns `SQLITE_READONLY`. `CsvReader` owns file/input-buffer state, field accumulation memory, current line, terminator, and error text. `CsvTable` stores configured filename/data, starting offset after a header, column count, and test flags. `CsvCursor` owns a `CsvReader`, per-column value buffers, lengths, and rowid.

Core parsing lives in `csv_read_one_field()`, with buffering in `csv_getc()`, `csv_getc_refill()`, `csv_append()`, and `csv_resize_and_append()`. Parameter parsing is handled by `csv_parameter()`, `csv_string_parameter()`, `csv_boolean_parameter()`, `csv_trim_whitespace()`, and `csv_dequote()`.

## Control flow

`csvtabConnect()` parses module arguments, rejects missing or simultaneous `filename=` and `data=`, optionally opens the input to count columns or read header names, builds a default `CREATE TABLE x(...)` declaration when no schema is supplied, records the offset after the header row, and marks the virtual table `SQLITE_VTAB_DIRECTONLY`. `csvtabOpen()` opens a fresh reader for each cursor. `csvtabFilter()` rewinds to `iStart`, preallocates the field buffer, and calls `csvtabNext()`. `csvtabNext()` reads fields until a row terminator, copies up to `nCol` fields into cursor column buffers, pads missing trailing columns with NULL, increments rowid, and sets rowid to -1 at EOF. `csvtabBestIndex()` normally reports a full-scan cost; the `SQLITE_TEST` flag can pretend constraints are useful for planner tests.

## State and persistence

The virtual table stores only configuration strings and header offset. It never writes CSV data. Cursor state owns open file handles and field buffers, which are closed/freed on cursor close. Inline `data=` input is scanned from memory.

## Dependencies and integration points

It depends on SQLite virtual table APIs, standard C file IO, and SQLite memory routines. Because `filename=` reads arbitrary files, the module is direct-only and the comments recommend TEMP virtual tables.

## Risks

CSV parsing is RFC4180-oriented but only comma-separated; there is no runtime separator parameter despite a parser comment mentioning alternative separators. Huge fields grow memory dynamically. Header and schema inference reads only the first row, so malformed later rows surface during scan. Filesystem access is intentionally powerful and must remain direct-only. `csv_trim_whitespace()` uses string length bookkeeping that is sensitive to trailing whitespace cases. `csvtabBestIndex()` test mode intentionally lies to the planner and must not be enabled in production builds.

## Test signals

Tests should cover quoted fields, doubled quotes, CRLF and LF endings, empty fields, empty first field, UTF-8 BOM stripping, header inference, explicit schema, `columns=N` padding/truncation, data-vs-filename validation, unreadable files, rowid progression, EOF, direct-only restrictions, and `csv_wr` read-only errors under `SQLITE_TEST`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/csv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/dbdump.c -->
# sources/storage-engines/sqlite/ext/misc/dbdump.c

## Purpose

`dbdump.c` implements `sqlite3_db_dump()`, a C API that emits UTF-8 SQL text able to recreate a database schema and contents while preserving rowid values when needed. With `DBDUMP_STANDALONE`, it also builds a command-line utility around that API.

## Important APIs, types, and functions

The exported API is `sqlite3_db_dump(sqlite3 *db, const char *zSchema, const char *zTable, int (*xCallback)(const char*,void*), void *pArg)`. `DState` tracks the connection, error count, return code, writable-schema state, and output callback. `DText` is a growable string helper used to build SQL fragments.

`tableColumnList()` discovers table columns via `PRAGMA table_info`, detects integer primary key and rowid preservation needs, and avoids inaccessible rowid aliases. `dump_callback()` emits table DDL and `INSERT` statements. `output_quoted_escaped_string()` safely emits SQL string literals, preserving newline and carriage-return bytes using nested `replace()` expressions. `output_sql_from_query()` emits indexes, triggers, and views from schema queries.

## Control flow

`sqlite3_db_dump()` starts a transaction on the source database, emits `PRAGMA foreign_keys=OFF; BEGIN TRANSACTION;`, then either dumps all tables or a single named table. Table rows are selected through generated `SELECT` statements and emitted according to SQLite type: integers, floats, NULLs, quoted text, and hex blobs. Virtual table DDL is recreated by inserting its schema row under `PRAGMA writable_schema=ON` rather than executing `CREATE VIRTUAL TABLE`. After schema objects are emitted, writable-schema mode is disabled if used, and the output ends in `COMMIT` or `ROLLBACK` based on error count.

## State and persistence

The function reads the supplied database and writes only to the callback. It opens and commits a read transaction around the dump to stabilize source reads. It does not modify database contents, except for transaction state on the connection used for dumping. Standalone mode opens a database path and writes to stdout.

## Dependencies and integration points

It depends on core SQLite C APIs, schema tables, pragmas, keyword checks, `sqlite3_table_column_metadata()`, and callback-style streaming output. It is intended to mirror shell `.dump` behavior in embeddable form.

## Risks

Dump correctness is sensitive to rowid alias detection, WITHOUT ROWID handling, quoted identifiers, virtual table handling, and floating-point special values. Callback failures are not strongly propagated because the callback return value is not consistently checked by helper functions. The code emits schema queries against `sqlite_schema` in some places and the requested schema in others, so attached-schema dumping should be tested carefully. Memory allocation failure in `DText` can suppress later output by clearing the buffer.

## Test signals

Coverage should recreate databases containing rowid tables, INTEGER PRIMARY KEY tables, WITHOUT ROWID tables, hidden rowid-name collisions, blobs, embedded quotes/newlines/CR text, infinities, indexes, triggers, views, virtual tables, `sqlite_sequence`, sqlite_stat tables, single-table dumps, attached schemas, and standalone CLI argument errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/dbdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/decimal.c -->
# sources/storage-engines/sqlite/ext/misc/decimal.c

## Purpose

`decimal.c` implements arbitrary-precision decimal math functions, a `decimal_sum` window aggregate, and a `decimal` collation. The implementation favors exactness and simplicity over speed.

## Important APIs, types, and functions

`sqlite3_decimal_init()` registers scalar functions `decimal`, `decimal_exp`, `decimal_cmp`, `decimal_add`, `decimal_sub`, `decimal_mul`, `decimal_pow2`, window function `decimal_sum`, and collation `decimal`. `Decimal` stores sign, OOM/null/init flags, total digit count, fractional digit count, and an array of base-10 digits.

Parsing and conversion are handled by `decimalNewFromText()`, `decimal_new()`, `decimalFromDouble()`, and `decimalPow2()`. Output is produced by `decimal_result()` or `decimal_result_sci()`. Arithmetic and comparison are implemented by `decimal_cmp()`, `decimal_expand()`, `decimal_add()`, `decimalMul()`, and `decimal_round()`. Aggregate state is a `Decimal` in SQLite aggregate context and is updated by `decimalSumStep()` and `decimalSumInverse()`.

## Control flow

Scalar functions convert inputs to `Decimal`, perform the requested operation, then render text. Text and integer inputs parse directly; floats and 8-byte blobs can be expanded to an exact decimal representation of their IEEE754 binary64 value unless `bTextOnly` forces text interpretation. Addition aligns integer and fractional digit counts, then either adds or subtracts digit arrays depending on signs. Multiplication uses grade-school accumulation into a new digit array and trims some trailing fractional zeros. `decimal_sum` initializes a zero accumulator, adds each non-NULL value, subtracts values for window inverse, and returns the current/final decimal text.

## State and persistence

The extension is stateless except for aggregate/window state owned by SQLite during query execution. All decimal values are heap-allocated and freed after each scalar operation. The collation parses both comparison keys on each comparison and stores no cached state.

## Dependencies and integration points

It depends on SQLite extension APIs, aggregate/window APIs, deterministic/innocuous function flags, and collation registration. It integrates with SQL ordering through `COLLATE decimal` and with window frames through `decimal_sum`.

## Risks

Large inputs can allocate very large digit arrays, bounded by `SQLITE_DECIMAL_MAX_DIGIT`. OOM is propagated through flags in some paths and direct SQLite errors in others. Text parsing is permissive and stops at exponent or unrecognized characters rather than reporting syntax errors. `decimal_cmp()` mutates operands by trimming trailing fractional zeros, which is safe for temporaries but important to know. Float conversion rejects NaN and infinity by returning NULL/OOM-like behavior depending on the caller path. The collation returns equality on parse failure, which can mask invalid numeric text.

## Test signals

Tests should cover signs, leading/trailing zeros, decimal points, exponents, exact binary64 expansion, 8-byte blob conversion, NaN/infinity behavior, addition/subtraction sign combinations, multiplication fractional trimming, significant-digit rounding in `decimal` and `decimal_exp`, `decimal_pow2` bounds, NULL aggregate behavior, window inverse correctness, collation ordering, and digit-limit/OOM paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/decimal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/diskused.c -->
# sources/storage-engines/sqlite/ext/misc/diskused.c

## Purpose

`diskused.c` implements SQL function `diskused(X)`, a textual database storage-utilization report for schema `X`. It replaces the old `sqlite3_analyzer` utility path and is used by the SQLite CLI `.diskused` command.

## Important APIs, types, and functions

`sqlite3_diskused_init()` registers `diskused` as an innocuous one-argument function. `DiskUsed` stores the database handle, SQL function context, output `sqlite3_str`, randomized temp table name, and target schema. `diskusedSql()`, `diskusedSqlInt()`, `diskusedPrepare()`, and `diskusedStmtFinish()` centralize dynamic SQL execution and error reporting. `diskusedTitle()`, `diskusedLine()`, and `diskusedPercent()` format the report. `diskusedSubreport()` aggregates page and payload statistics for selected subsets of objects.

## Control flow

`diskusedFunc()` resolves NULL schema to `main`, rejects `temp`, validates the schema through `pragma_database_list`, creates a random `temp.diskused...` table, then populates it from `dbstat(schema)` joined to schema-derived table/index metadata. It reads `page_count`, `page_size`, `freelist_count`, `auto_vacuum`, table counts, WITHOUT ROWID counts, and index counts. It emits high-level storage totals, page-count rankings, aggregate subreports for all tables/indexes and categories, per-table and per-index subreports, and finally SQL that can recreate the raw `space_used` data used by the report.

## State and persistence

The function creates a temporary table with a 128-bit random suffix and drops it in `diskusedReset()`. Output accumulates in memory until returned as a single text result. It does not modify the target schema, but it requires `dbstat` visibility over that schema.

## Dependencies and integration points

It depends on SQLite `dbstat`, schema tables, pragma table-valued functions, `pragma_table_list`, `pragma_index_list`, `sqlite3_randomness()`, dynamic SQL quoting with `%w` and `%Q`, and math `ceil()` for auto-vacuum overhead. It is closely tied to SQLite page accounting semantics.

## Risks

The function is innocuous but can be expensive on large databases because it scans `dbstat` and builds a full report string. Temporary table cleanup must run on every error path; many helpers call `diskusedReset()` after reporting errors. Division by storage totals assumes nonzero page counts and object storage in subreports. If `dbstat` is unavailable or shadowed, analysis fails. Report text is not machine-stable enough for strict string tests across SQLite storage changes.

## Test signals

Tests should include empty databases, invalid schema names, rejected `temp`, rowid and WITHOUT ROWID tables, indexes and autoindexes, freelist pages, auto-vacuum databases, overflow payloads, attached schemas, `dbstat` unavailable/error cases, temp table cleanup after errors, and presence of the raw `space_used` SQL block.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/diskused.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/eval.c -->
# sources/storage-engines/sqlite/ext/misc/eval.c

## Purpose

`eval.c` implements scalar SQL function `eval()`, which executes SQL text recursively on the current database connection and concatenates returned column values into one text result.

## Important APIs, types, and functions

`sqlite3_eval_init()` registers one- and two-argument `eval` functions with `SQLITE_DIRECTONLY`. `EvalResult` owns the accumulated result string, separator string, separator length, allocation size, and used byte count. `sqlEvalFunc()` obtains SQL and optional separator arguments, gets the connection from `sqlite3_context_db_handle()`, and calls `sqlite3_exec()`. `callback()` appends every column value from every returned row, substituting empty strings for SQL NULL values.

## Control flow

`sqlEvalFunc()` defaults the separator to a single space. If either SQL or separator is SQL NULL, the function returns NULL. `sqlite3_exec()` runs the supplied SQL; for each result row, `callback()` grows the buffer when needed, emits the separator before every value after the first, and appends the text value. On execution error, the SQLite error string is returned as a function error. On callback allocation failure, the callback clears state and aborts execution.

## State and persistence

The function has no module-global state, but it can run arbitrary SQL on the current connection, so it may read or mutate database state depending on the input SQL. The accumulated result is heap memory transferred to SQLite as the function result.

## Dependencies and integration points

It depends on `sqlite3_exec()` recursion and direct-only function registration. The direct-only flag prevents use from schema objects such as views and triggers, limiting privilege escalation from attacker-controlled database files.

## Risks

The function executes arbitrary SQL supplied at runtime, so it is intentionally powerful. Recursive use can interact with locks, transactions, user-defined functions, and side effects on the same connection. Results are flattened without column or row structure. Very large result sets can allocate large memory; allocation failure is detected through callback abort behavior.

## Test signals

Tests should verify one- and two-argument separators, NULL SQL/separator behavior, multiple rows and columns flattening, NULL column conversion to empty text, propagation of SQL errors, side-effect statements, direct-only restrictions, and large output allocation failure behavior where test infrastructure permits.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/eval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/explain.c -->
# sources/storage-engines/sqlite/ext/misc/explain.c

## Purpose

`explain.c` implements an eponymous virtual table `explain` that turns `EXPLAIN <sql>` bytecode output into queryable rows. It was written to simplify tests that assert bytecode patterns.

## Important APIs, types, and functions

`sqlite3_explain_init()` calls `sqlite3ExplainVtabInit()`, registering module `explain`. `explain_vtab` stores the connection. `explain_cursor` stores the original SQL text, prepared `EXPLAIN` statement, and last step result. The declared schema is `addr, opcode, p1, p2, p3, p4, p5, comment, sql HIDDEN`.

## Control flow

`explainBestIndex()` requires a usable equality constraint on hidden column `sql`; if only unusable SQL constraints exist it returns `SQLITE_CONSTRAINT`, and if no usable constraint exists the plan remains expensive/unusable. `explainFilter()` copies the SQL text, prefixes it with `EXPLAIN `, prepares it on the same connection, and steps to the first row. `explainNext()` steps the prepared statement. `explainColumn()` returns the hidden SQL text for the hidden column and otherwise forwards the corresponding `sqlite3_column_value()` from the EXPLAIN statement. `explainRowid()` uses the bytecode address column.

## State and persistence

The module is read-only. Each cursor owns one prepared EXPLAIN statement and copied SQL string. No persistent database state is changed, though preparing SQL can resolve schema metadata and fail if referenced objects are invalid.

## Dependencies and integration points

It depends on virtual table APIs and SQLite's EXPLAIN output column layout. It is used as a table-valued helper for tests and introspection, for example filtering rows by opcode.

## Risks

The module assumes EXPLAIN output columns match the declared schema. SQL text is concatenated after `EXPLAIN`, so caller input must be a single statement acceptable to SQLite prepare. Non-text `sql` arguments produce empty output. Errors from prepare or step propagate as virtual table errors. The module is not marked direct-only or innocuous in this file, so embedding context depends on SQLite's module policy at registration.

## Test signals

Tests should query `explain('SELECT ...')`, filter by opcode, verify hidden SQL column echo, rowid equals address, non-text SQL returns EOF, missing SQL constraint is rejected by planning, invalid SQL propagates an error, and bytecode output remains aligned with SQLite EXPLAIN schema.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/explain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/fileio.c -->
# sources/storage-engines/sqlite/ext/misc/fileio.c

## Purpose

`fileio.c` implements filesystem-facing SQL helpers: `readfile()`, `writefile()`, `lsmode()`, `realpath()`, and eponymous virtual table `fsdir`. These functions support CLI import/export and archive workflows that need to read, write, or enumerate files from SQL.

## Important APIs, types, and functions

`sqlite3_fileio_init()` registers direct-only `readfile` and `writefile`, `lsmode`, `realpath`, and the `fsdir` module. `readFileContents()` reads a whole file into a SQLite blob with length-limit checks. `writeFile()` handles regular files, directories, symlinks on Unix, chmod, and optional mtime. `makeDirectory()` creates missing parent directories. `lsModeFunc()` formats POSIX mode bits.

For `fsdir`, `fsdir_cursor` tracks recursion levels, base path, current stat, current path, and rowid. `FsdirLevel` owns an open `DIR*` plus directory path. The virtual table schema is `(name,mode,mtime,data,level,path HIDDEN,dir HIDDEN)`. Platform helpers provide UTF-8 path support and time conversion on Windows. `portable_realpath()` and `realpathFunc()` resolve existing path prefixes and append missing tails.

## Control flow

`readfileFunc()` returns NULL for NULL or unreadable paths, otherwise delegates to `readFileContents()`. `writefileFunc()` parses 2 to 4 arguments, mode, and mtime, calls `writeFile()`, creates parent directories on `ENOENT`, and raises detailed errors when mode was supplied and writing still fails. `writeFile()` chooses symlink, directory, or regular-file behavior from `mode`; regular files return bytes written.

`fsdirBestIndex()` requires `path=` and optionally accepts `dir=` and `level` constraints, rejecting plans with unusable input constraints. `fsdirFilter()` builds the starting path, stats it, and positions the first row. `fsdirNext()` emits the current path first, then descends into directories depth-first, skipping `.` and `..`, statting each child with `lstat` on Unix. `fsdirColumn()` returns names relative to `dir` when supplied, stat metadata, file data blobs, symlink targets, or NULL for directory data.

## State and persistence

`readfile`, `fsdir`, and `realpath` read filesystem state. `writefile` mutates filesystem state by creating or replacing files, directories, symlinks, permissions, and timestamps. The SQLite database is not modified by the module itself. `fsdir` cursor state owns open directory handles and closes them during reset/close.

## Dependencies and integration points

It depends on C stdio, POSIX or Windows filesystem APIs, SQLite direct-only function registration, virtual tables, and optionally `sqlite3_stdio.h` when compiled into the CLI. `fsdir` is marked `SQLITE_VTAB_DIRECTONLY` because it exposes filesystem contents.

## Risks

This is a high-trust extension because it reads and writes arbitrary paths available to the process. Direct-only flags on `readfile`, `writefile`, and `fsdir` are important security boundaries. Whole-file reads can be expensive and are bounded only by SQLite length limit and memory. Recursive `fsdir` can traverse large trees and follows directory structure without cycle detection beyond not descending into symlinked directories on Unix because it uses `lstat`. `realpathFunc()` documents a FIXME where OOM may return NULL instead of an explicit error. Cross-platform differences exist for symlinks, chmod, stat timestamps, and path separators.

## Test signals

Tests should cover file reads, unreadable/missing files returning NULL, blob length limit errors, writing regular files, parent directory creation, chmod and mtime, directory and symlink modes, write errors with and without mode arguments, `lsmode` formatting, `fsdir` recursion, level limits, relative `dir` behavior, symlink data, direct-only restrictions, Windows UTF-8 path behavior where available, and `realpath` for existing and not-yet-existing paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/fileio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/fossildelta.c -->
# sources/storage-engines/sqlite/ext/misc/fossildelta.c

## Purpose

`fossildelta.c` implements Fossil delta creation, application, output-size inspection, and delta parsing for SQL. It is provided mainly for developers inspecting RBU files that contain Fossil-format deltas.

## Important APIs, types, and functions

`sqlite3_fossildelta_init()` registers scalar functions `delta_create(X,Y)`, `delta_apply(X,D)`, `delta_output_size(D)`, and virtual table `delta_parse`. The delta engine uses `hash` for a 16-byte rolling checksum window (`NHASH`), `putInt()` and `deltaGetInt()` for Fossil base-64 integers, `checksum()` for the 32-bit big-endian output checksum, `delta_create()`, `delta_output_size()`, and `delta_apply()`.

The parser virtual table uses `deltaparsevtab_cursor`, which stores a copy of the delta blob, cursor offsets, current operator, and operator arguments. It exposes columns `op`, `a1`, `a2`, and hidden `delta`.

## Control flow

`delta_create()` writes the target size line, builds a hash table over 16-byte source landmarks, scans the target with a rolling hash, chooses copy commands when they are smaller than literal text, emits insert commands for unmatched bytes, and finishes with a checksum record. Copy records have `N@O,`, inserts have `N:<bytes>`, and checksum has `N;`.

`delta_apply()` reads the expected output size, then processes copy, insert, and checksum operators while enforcing output-size and source-bound limits. It returns -1 for malformed deltas. Checksum verification is compiled only when `FOSSIL_ENABLE_DELTA_CKSUM_TEST` is defined, but size and bounds checks always run. SQL wrappers allocate output buffers based on `delta_output_size()` and report `"corrupt fossil delta"` on parse/apply mismatch.

`delta_parse` requires an equality constraint on hidden `delta`. `deltaparsevtabFilter()` copies the delta blob and emits the initial `SIZE` row. `deltaparsevtabNext()` advances through operators and emits `COPY`, `INSERT`, `CHECKSUM`, `ERROR`, or `EOF`. Insert payloads are returned as blobs; malformed insert lengths return a zeroblob in `a2`.

## State and persistence

The scalar functions are stateless and operate on input blobs. The parser virtual table stores only cursor-local copies of delta blobs. No database writes occur.

## Dependencies and integration points

It depends on SQLite loadable extension APIs, virtual table APIs, SQLite integer typedefs, and the Fossil delta format also used by SQLite RBU artifacts. Functions are registered as UTF-8 innocuous.

## Risks

Delta data is binary and can contain embedded NULs, so all paths must use explicit byte lengths. `delta_create()` allocates hash arrays proportional to source length and a caller-provided output buffer sized by the SQL wrapper as `target+70`. `checksum()` assumes four-byte alignment in an assert and has endian-specific fast paths. `delta_apply()` protects against output overflow, source overread, missing terminators, and oversized inserts, but checksum validation is optional at compile time. The parser is diagnostic and may expose partial/error rows rather than rejecting all malformed input at filter time.

## Test signals

Tests should round-trip small and large text and binary blobs, source shorter than `NHASH`, insert-only deltas, copy-heavy deltas, embedded NUL data, malformed size headers, bad copy terminators, source-overrun copy commands, output-size mismatch, truncated inserts, checksum rows, `delta_output_size()` errors, `delta_parse` row sequences, hidden-delta planning constraints, and optional checksum-failure behavior when compiled with checksum testing.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/fossildelta.c -->
