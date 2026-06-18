# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/shell.c lines 8934-17244

## Chunk Scope

This chunk is a large embedded-extension section of SQLite's command-line shell amalgamation as vendored under WiredTiger tests. It starts at the tail of `../ext/misc/fileio.c`, where the `fsdir` virtual table is registered and `sqlite3_fileio_init()` installs `readfile`, `writefile`, `lsmode`, and `fsdir`. It then contains complete or near-complete embedded implementations for:

- `../ext/misc/completion.c`
- `../ext/misc/appendvfs.c`
- `../ext/misc/zipfile.c`, when `SQLITE_HAVE_ZLIB` is enabled
- `../ext/misc/sqlar.c`, also under the zlib-enabled region
- `../ext/expert/sqlite3expert.h` and most of `../ext/expert/sqlite3expert.c`
- `../ext/intck/sqlite3intck.h` and `../ext/intck/sqlite3intck.c`
- `../ext/misc/stmtrand.c`
- the start of `../ext/misc/vfstrace.c`

The researched span is `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/shell.c:8934-17244`. The chunk begins after most `fileio.c` implementation has already appeared in an earlier chunk and ends inside `vfstraceDlClose()`, before the rest of the `vfstrace` VFS registration code.

## Purpose

The code gives the SQLite shell a bundle of utility extensions without relying on separate shared libraries at runtime. In this vendored WiredTiger test copy, these extensions are mostly test, diagnostics, packaging, and shell-convenience features around the SQLite engine rather than WiredTiger storage-engine code.

The chunk's feature purposes are:

- `fileio` registers file-oriented scalar functions and the `fsdir` eponymous virtual table used by shell commands and SQL scripts to read, write, list, and inspect filesystem content.
- `completion` exposes an eponymous virtual table that returns SQL completion candidates for keywords, attached databases, schema objects, and table columns.
- `appendvfs` registers a VFS shim named `apndvfs` that can expose a database appended to the end of another file, such as an executable or archive-like prefix.
- `zipfile` exposes ZIP archives as a virtual table and a `zipfile()` aggregate constructor, supporting read/write of central-directory records and raw/deflated file data.
- `sqlar` registers `sqlar_compress()` and `sqlar_uncompress()` zlib helpers for SQLite archive blobs.
- `sqlite3expert` implements the shell's index-advisor engine. It compiles target SQL against shadow schemas, records planner constraints through an internal virtual table, creates candidate indexes, optionally populates `sqlite_stat1`, and reports recommended index DDL and query plans.
- `sqlite3intck` implements an incremental integrity-check API that can step through generated consistency queries over tables and indexes and can release/reacquire read transactions between steps.
- `stmtrand` registers a deterministic statement-local pseudo-random SQL function for repeatable testing.
- `vfstrace` begins a VFS tracing shim that logs lower-level VFS calls and allows `PRAGMA vfstrace` to enable or disable tracing by API class.

## Important APIs, Types, and Functions

### Fileio tail

`fsdirRegister(sqlite3 *db)` constructs a `sqlite3_module` whose methods point to `fsdirConnect`, `fsdirBestIndex`, `fsdirDisconnect`, `fsdirOpen`, `fsdirClose`, `fsdirFilter`, `fsdirNext`, `fsdirEof`, `fsdirColumn`, and `fsdirRowid` from earlier in `fileio.c`. It registers the module as `fsdir`.

`sqlite3_fileio_init(sqlite3 *db, char **pzErrMsg, const sqlite3_api_routines *pApi)` is the extension initializer. It calls `SQLITE_EXTENSION_INIT2`, creates `readfile`, `writefile`, and `lsmode`, then registers `fsdir`. If virtual tables are omitted, `fsdirRegister()` compiles to `SQLITE_OK`.

### Completion virtual table

`completion_vtab` stores the owning `sqlite3 *db`. `completion_cursor` stores hidden-argument state (`zPrefix`, `zLine`), the current result row, a prepared statement for schema-driven phases, a rowid counter, and an `ePhase` state-machine value.

The exposed schema is:

```sql
CREATE TABLE x(
  candidate TEXT,
  prefix TEXT HIDDEN,
  wholeline TEXT HIDDEN,
  phase INT HIDDEN
)
```

Important callbacks:

- `completionConnect()` declares the schema, marks the vtab innocuous, and allocates the vtab object.
- `completionOpen()`, `completionCursorReset()`, and `completionClose()` own cursor allocation, hidden-argument strings, and any active schema statement.
- `completionFilter()` accepts equality constraints on hidden `prefix` and `wholeline`, derives a prefix from `wholeline` when needed, initializes `ePhase`, and advances to the first candidate.
- `completionNext()` implements the phase machine. It first enumerates `sqlite3_keyword_name()` candidates, then prepares `PRAGMA database_list`, schema-name union queries, and `pragma_table_xinfo()` joins to produce database, table/view/trigger, and column names.
- `completionBestIndex()` sets `idxNum` bits for usable hidden equality constraints and assigns lower estimated cost/rows when hidden arguments are supplied.
- `sqlite3CompletionVtabInit()` and `sqlite3_completion_init()` register the module as `completion`.

Phase constants include `COMPLETION_KEYWORDS`, `COMPLETION_DATABASES`, `COMPLETION_TABLES`, `COMPLETION_COLUMNS`, and `COMPLETION_EOF`. Several other phase constants are declared but not used by this implementation branch.

### Append VFS

`ApndFile` subclasses `sqlite3_file`. It stores:

- `iPgOne`: offset of page 1 within the containing file
- `iMark`: offset of the append marker, or `-1` before the marker is written
- an immediately following base `sqlite3_file` object accessed through `ORIGFILE()`

Constants define the trailer format and limits:

- `APND_MARK_PREFIX` is `Start-Of-SQLite3-`.
- `APND_MARK_SIZE` is 25 bytes: 17 bytes of prefix plus an 8-byte big-endian offset.
- `APND_MAX_SIZE` limits the exposed append database to below 1 GiB to avoid Windows locking complications.
- `APND_ROUNDUP` defaults to 4096 and `APND_START_ROUNDUP()` aligns newly appended databases.

The `apnd_io_methods` table wraps `xClose`, `xRead`, `xWrite`, `xTruncate`, `xSync`, `xFileSize`, locks, shared-memory operations, and mmap fetch/unfetch. Most methods pass through to the base file after adding `iPgOne` to database-relative offsets. `apndWriteMark()` serializes the trailer and updates `iMark` only after the write succeeds. `apndWrite()` writes the marker before a write that would create or overwrite it. `apndTruncate()` writes the marker first, then truncates the underlying file just past the marker.

`apndReadMark()` validates the trailer, decodes the appended-database offset, and rejects impossible offsets or non-512-byte-aligned starts. `apndIsAppendvfsDatabase()` confirms both the trailer and the SQLite header at `iPgOne`. `apndIsOrdinaryDatabaseFile()` detects ordinary SQLite files and avoids wrapping them.

`apndOpen()` is the critical entry point. Main database opens use the shim; non-main or transient opens pass straight through to the base VFS. After opening the base file, it chooses among ordinary pass-through, existing appended database, append-to-existing-file on `SQLITE_OPEN_CREATE`, or `SQLITE_CANTOPEN`.

`sqlite3_appendvfs_init()` discovers the default VFS, copies version/path/file-size metadata into the static `apnd_vfs`, stores the original VFS in `pAppData`, registers `apndvfs`, and returns `SQLITE_OK_LOAD_PERMANENTLY` on success.

### Zipfile virtual table and aggregate

The `zipfile` module is compiled only with `SQLITE_HAVE_ZLIB` and without `SQLITE_OMIT_VIRTUALTABLE`. It uses zlib raw deflate/inflate for ZIP entries and standard zlib format for the later SQLar helpers.

The virtual table schema is:

```sql
CREATE TABLE y(
  name PRIMARY KEY,
  mode,
  mtime,
  sz,
  rawdata,
  data,
  method,
  z HIDDEN
) WITHOUT ROWID
```

Core ZIP structs:

- `ZipfileEOCD`: end-of-central-directory fields.
- `ZipfileCDS`: central-directory record fields plus malloc-owned `zFile`.
- `ZipfileLFH`: local-file-header fields.
- `ZipfileEntry`: one archive entry, including CDS, UNIX mtime, copied extra fields, data offset, optional in-memory compressed data, and linked-list pointer.
- `ZipfileCsr`: vtab cursor, file handle, directory offset, current entry, and cursor list linkage.
- `ZipfileTab`: vtab object, fixed temp buffer, optional bound archive file, cursor list, and write-transaction state (`pFirstEntry`, `pWriteFd`, `szCurrent`, `szOrig`).

Read helpers include `zipfileReadEOCD()`, `zipfileReadCDS()`, `zipfileReadLFH()`, `zipfileGetEntry()`, little-endian getters/setters, `zipfileScanExtra()`, `zipfileMtime()`, and `zipfileMtimeToDos()`. They parse the EOCD by scanning backward in the final 64 KiB, walk central-directory records, read LFH metadata to locate data bytes, and optionally copy compressed data from an in-memory archive blob.

Virtual table methods:

- `zipfileConnect()` validates constructor arguments, stores an optional archive filename, declares the schema, allocates the shared buffer, and marks the table `SQLITE_VTAB_DIRECTONLY`.
- `zipfileOpen()`, `zipfileResetCursor()`, and `zipfileClose()` manage cursors and unlink them from `ZipfileTab.pCsrList`.
- `zipfileFilter()` supports three scan modes: a table-bound filename, a hidden `z` filename argument, or a BLOB containing an entire ZIP image. It opens the file or loads the directory into memory, then positions the cursor.
- `zipfileNext()`, `zipfileColumn()`, and `zipfileEof()` iterate and expose columns. `data` inflates method 8 entries, `rawdata` returns compressed bytes, zero-size directories return SQL NULL for data, and zero-size files return a zero-length blob.
- `zipfileBestIndex()` requires an equality constraint on hidden `z` when the table was not constructed with a filename.
- `zipfileUpdate()` implements insert, update, delete, conflict handling, compression choice, path normalization for directories, duplicate checks, and in-memory central-directory list maintenance.
- `zipfileBegin()`, `zipfileCommit()`, and `zipfileRollback()` own write transactions. `zipfileCommit()` appends all CDS records and EOCD; `zipfileRollback()` delegates to commit, so updates append a new directory rather than restoring `szOrig`.
- `zipfileFindFunction()` overloads `zipfile_cds()` to expose the current cursor's CDS fields as a JSON-like string.

The `zipfile()` aggregate is implemented by `ZipfileCtx`, `ZipfileBuffer`, `zipfileStep()`, and `zipfileFinal()`. `zipfileStep()` accepts `(name,data)`, `(name,mode,mtime,data)`, or `(name,mode,mtime,data,method)`, validates directory/file mode consistency, optionally deflates, appends LFH and content to an in-memory body buffer, appends CDS records to a second buffer, and increments entry count. `zipfileFinal()` concatenates body, central directory, and EOCD into one result BLOB.

`zipfileRegister()` creates the `zipfile` module, overloads `zipfile_cds`, registers the aggregate, and asserts expected integer sizes. `sqlite3_zipfile_init()` is the extension initializer.

### SQLar zlib helpers

`sqlarCompressFunc()` implements `sqlar_compress(X)`. BLOB values are compressed with zlib `compress()` and returned only if the compressed size is smaller; otherwise the original SQL value is returned. Non-BLOB values are passed through.

`sqlarUncompressFunc()` implements `sqlar_uncompress(X,SZ)`. If `SZ <= 0` or equals the current blob byte length, the original value is returned. Otherwise it allocates `SZ` bytes and calls zlib `uncompress()`.

`sqlite3_sqlar_init()` registers both functions as UTF-8 and innocuous.

### SQLite expert index advisor

The public expert API is declared in this chunk:

- `sqlite3_expert_new()`
- `sqlite3_expert_config()`
- `sqlite3_expert_sql()`
- `sqlite3_expert_analyze()`
- `sqlite3_expert_count()`
- `sqlite3_expert_report()`
- `sqlite3_expert_destroy()`

Configuration and report constants include `EXPERT_CONFIG_SAMPLE`, `EXPERT_REPORT_SQL`, `EXPERT_REPORT_INDEXES`, `EXPERT_REPORT_PLAN`, and `EXPERT_REPORT_CANDIDATES`.

Main internal types:

- `IdxColumn`, `IdxTable`: table schema extracted from `PRAGMA table_xinfo` and `sqlite3_table_column_metadata()`.
- `IdxConstraint`: equality, range, and order-by constraints captured from virtual-table planning callbacks.
- `IdxScan`: one table scan plus required constraints/order and covering-column mask.
- `IdxWrite`: unique table/write operation detected through an authorizer callback while testing triggers.
- `IdxStatement`: target SQL plus selected index DDL and EQP text.
- `IdxHash`: candidate-index lookup and de-duplication by generated index name.
- `sqlite3expert`: top-level object containing the user DB, two in-memory databases (`dbm` and `dbv`), schema metadata, scan/write/statement lists, sample configuration, candidates, and accumulated errors.

The internal `expert` virtual table is the observation mechanism. `idxCreateVtabSchema()` builds a parallel schema in `dbv`: ordinary user tables become `CREATE VIRTUAL TABLE ... USING expert(...)`, while views and view triggers are copied where possible. The `expertBestIndex()` callback records planner constraints and order-by terms into `IdxScan` objects whenever target SQL is prepared against `dbv`; it assigns decreasing estimated cost as it captures more useful terms.

Candidate generation uses:

- `idxCreateFromWhere()` to group equality constraints and pair them with range or order-by tails.
- `idxFindCompatible()` to avoid proposing indexes already compatible with an existing index in `dbm`.
- `idxAppendColDefn()` and `idxIdentifierRequiresQuotes()` to build column definitions with collations and DESC markers.
- `idxCreateFromCons()` to generate a unique index name, create the candidate in `dbm`, and add it to `hIdx`.
- `idxCreateCandidates()` to process all captured scans.

Analysis and reporting use:

- `idxPopulateStat1()` to optionally produce `sqlite_stat1` data for candidate indexes. Sampling uses `sqlite_expert_sample()` and a temp table; full mode scans the user DB directly.
- `idxPopulateOneStat1()` to build stat strings by comparing adjacent sorted index keys using `sqlite_expert_rem()`.
- `idxFindIndexes()` to run `EXPLAIN QUERY PLAN` for each target statement against `dbm`, parse plan text for candidate index names, and store chosen index DDL and plan details.
- `idxProcessTriggers()` and `idxProcessOneTrigger()` to create temporary trigger environments for detected write operations and collect scans that trigger bodies would perform.
- `registerUDFs()` and dummy UDF/collation callbacks to let analysis prepare SQL that references application-defined functions and collations without executing them.

`sqlite3_expert_new()` creates `dbv` and `dbm`, enables trigger EQP on `dbm`, registers dummy collation callbacks and UDFs when introspection pragmas are available, copies the user schema into `dbm`, builds the virtual-table schema in `dbv`, and installs the authorizer on `dbv`. `sqlite3_expert_sql()` first compiles statements against the real DB, then prepares them against `dbv` to collect scans. `sqlite3_expert_analyze()` processes triggers, creates candidates, populates stats, builds the candidate report, and finds selected indexes. `sqlite3_expert_destroy()` closes in-memory DBs and frees all linked structures.

### Incremental integrity check

The public `sqlite3_intck` API in this chunk is:

- `sqlite3_intck_open(sqlite3 *db, const char *zDb, sqlite3_intck **ppOut)`
- `sqlite3_intck_close(sqlite3_intck *pCk)`
- `sqlite3_intck_step(sqlite3_intck *pCk)`
- `sqlite3_intck_message(sqlite3_intck *pCk)`
- `sqlite3_intck_unlock(sqlite3_intck *pCk)`
- `sqlite3_intck_error(sqlite3_intck *pCk, const char **pzErr)`
- `sqlite3_intck_test_sql(sqlite3_intck *pCk, const char *zObj)`

`struct sqlite3_intck` stores the database handle, target schema name, current object, current generated check statement, restart key, corruption message, persistent error state, and generated test SQL.

Important helpers:

- `intckPrepare()`, `intckPrepareFmt()`, `intckFinalize()`, `intckStep()`, `intckExec()`, and `intckMprintf()` centralize the module's error-state convention.
- `intckFindObject()` orders tables, indexes, and `sqlite_schema` to choose the next object to check, preserving restart state across `unlock`.
- `intckGetToken()`, `intckIsSpace()`, and `intckParseCreateIndex()` parse CREATE INDEX SQL enough to recover indexed expressions and partial-index WHERE clauses.
- `intckCheckObjectSql()` builds the actual SQL used to check one table or index. It uses common CTEs to model primary keys, index columns, wrappers, partial-index predicates, and generated error messages.
- `intckSaveKey()` serializes the current key vector into SQL text so `sqlite3_intck_unlock()` can finalize the statement and later resume after the last checked row or index entry.

`sqlite3_intck_step()` clears any prior message, finds or prepares the next object check, steps one generated query row, reports corruption as a message rather than a hard error when possible, and returns `SQLITE_DONE` only after all objects are exhausted. `sqlite3_intck_unlock()` saves the restart key and finalizes the current statement so a read transaction can be released between steps.

### Stmtrand

`Stmtrand` stores two unsigned integer PRNG states. `stmtrandFunc()` keeps this state in SQLite auxdata under `STMTRAND_KEY`, seeds it from the first invocation's argument in a statement, advances a Galois LFSR-like `x` state and a linear-congruential `y` state, and returns a non-negative 31-bit integer. Because SQLite clears auxdata on statement reset, the sequence is repeatable per statement execution.

`sqlite3_stmtrand_init()` registers both one-argument and zero-argument `stmtrand`.

### Vfstrace start

`vfstrace_info` stores the root VFS, output callback, trace bitmask, enabled flag, output argument, trace VFS name, and back-pointer to the trace VFS. `vfstrace_file` wraps a real `sqlite3_file` and stores the trace info, base filename, and underlying file pointer.

Trace bit constants cover file methods (`VTR_READ`, `VTR_WRITE`, `VTR_LOCK`, etc.), VFS methods (`VTR_OPEN`, `VTR_DELETE`, `VTR_ACCESS`, etc.), dynamic loading, randomness, time, and mmap fetch/unfetch.

The chunk includes wrappers for:

- File methods: close, read, write, truncate, sync, file size, lock/unlock, reserved-lock check, file control, sector size, device characteristics, shared-memory lock/map/barrier/unmap, fetch/unfetch.
- VFS methods through the chunk end: open, delete, access, full pathname, dynamic-library open/error/symbol lookup, and the beginning of dynamic-library close.

`vfstraceFileControl()` is especially important. It names many `SQLITE_FCNTL_*` operations, handles `SQLITE_FCNTL_PRAGMA` for `vfstrace`, updates `mTrace` from either a numeric mask or textual `+`/`-` API names, forwards the operation to the real file, and decorates selected return values such as `VFSNAME`, `MMAP_SIZE`, `HAS_MOVED`, `PERSIST_WAL`, pragma replies, and temp filenames.

`vfstraceOpen()` allocates a fresh `sqlite3_io_methods` table per opened file, copies the underlying method version, installs tracing wrappers for available methods, and leaves unavailable SHM/fetch methods as NULL. The full `vfstrace_register()` function is outside this chunk.

## Control Flow

Registration functions are the outer integration path. Each extension initializer calls `SQLITE_EXTENSION_INIT2()` and registers SQL functions, virtual tables, or VFS shims with the supplied `sqlite3 *db` or the global VFS registry. In the shell amalgamation, surrounding code can call these initializers directly instead of loading shared libraries.

`completion` flow is a virtual-table scan. Query planning encodes hidden argument availability in `idxNum`; filtering copies the prefix/wholeline inputs and derives a prefix if necessary; `completionNext()` advances across phases, preparing and finalizing schema queries as each phase begins and ends. Prefix filtering is done after each candidate is produced.

`appendvfs` flow sits below the pager. SQLite opens a database through `apndvfs`; `apndOpen()` either passes ordinary databases through, exposes the appended database by offsetting all IO, or starts a new appended database at an aligned offset. Subsequent reads and writes translate offsets through `iPgOne`, while writes/truncates maintain the trailer marker so later opens can rediscover the database.

`zipfile` read flow starts by locating EOCD, then iterating central-directory entries. For file-backed archives, entries are parsed lazily as the cursor advances. For blob-backed archives or write transactions, entries live in memory. Column reads may read compressed data from file, return raw bytes, inflate data, or synthesize NULL/empty blobs for directories and empty files.

`zipfile` write flow opens the archive in append mode and loads the current directory into memory. Insert/update builds a new local header and appends new content immediately, then modifies the in-memory directory list. Delete only removes list entries. Commit appends a fresh central directory and EOCD. This preserves earlier bytes and relies on the final EOCD making the latest directory authoritative.

`sqlite3expert` flow is prepare-time analysis rather than query execution. The user schema is copied into `dbm` and represented as expert virtual tables in `dbv`. Preparing target SQL against `dbv` invokes `expertBestIndex()` and records constraints/order-by requirements. Analysis generates candidate indexes in `dbm`, optionally populates stats, then uses `EXPLAIN QUERY PLAN` to see which candidate indexes the planner chooses. Reports are stored in the expert object and returned by `sqlite3_expert_report()`.

`sqlite3intck` flow is incremental. A step prepares a generated checker query for the next object if needed, executes one step, and exposes any corruption row through `sqlite3_intck_message()`. When the current object scan finishes, the statement is finalized and the next step picks another object. `sqlite3_intck_unlock()` can interrupt a long scan by saving a restart key and finalizing the statement.

`stmtrand` flow is scalar and statement-local. The first invocation in a statement allocates auxdata and seeds state; later invocations reuse it. Resetting the prepared statement resets the sequence.

`vfstrace` flow wraps both file and VFS method calls. Each wrapper toggles output based on its trace bit, prints a call signature, calls the real underlying method, then prints the result. The trace mask can be changed dynamically through `PRAGMA vfstrace(...)` passed via `SQLITE_FCNTL_PRAGMA`.

## State and Persistence Behavior

Most state in this chunk is transient C heap state owned by SQLite connections, virtual-table cursors, or VFS file objects. Some modules intentionally modify persistent external files:

- `fileio` functions from the previous section can read/write filesystem files; this chunk's initializer exposes those functions and `fsdir`.
- `appendvfs` persists an appended database inside a host file by writing database bytes at `iPgOne` and a 25-byte trailer marker at `iMark`.
- `zipfile` writes archive content to disk when a filename-backed zipfile table is mutated. It appends new file data, central-directory records, and EOCD records rather than rewriting the entire file in place.
- `sqlar` does not persist anything by itself; it returns compressed/uncompressed SQL values to callers.
- `sqlite3expert` creates in-memory analysis databases and temporary functions. It does not change the user's schema or create recommended indexes in the user database.
- `sqlite3intck` disables `PRAGMA automatic_index` while building/checking generated SQL and restores it afterward. It does not modify database content, but it creates a temporary scalar function named `parse_create_index` on the inspected connection while the handle is open.
- `stmtrand` stores per-statement auxdata only.
- `vfstrace` registers a VFS shim and emits diagnostics through caller-supplied output; it forwards actual persistence operations to the root VFS.

Memory ownership is manual and local. Cursors free prepared statements and copied strings on reset/close. `zipfile` maintains linked entry lists that are freed on cursor reset, close, disconnect, commit, or cleanup. The expert object owns linked scan, table, statement, write, and hash allocations until `sqlite3_expert_destroy()`. The intck object owns generated SQL, current object names, restart keys, and error messages until close.

## Dependencies and Integration Points

The chunk depends heavily on SQLite extension and virtual-table APIs: `sqlite3_create_function`, `sqlite3_create_module`, `sqlite3_declare_vtab`, `sqlite3_vtab_config`, `sqlite3_prepare_v2`, `sqlite3_step`, `sqlite3_finalize`, `sqlite3_mprintf`, `sqlite3_malloc`, VFS registration, `sqlite3_io_methods`, and many `SQLITE_FCNTL_*` and `SQLITE_OPEN_*` constants.

It also depends on standard C library functionality: `stdio` file IO for ZIP archives, string/memory helpers, varargs, assertions, and ctype parsing. `zipfile` and `sqlar` require zlib (`inflate`, `deflate`, `compress`, `uncompress`, `crc32`) under `SQLITE_HAVE_ZLIB`.

Shell integration points visible or implied by this chunk include:

- Shell file commands and archive commands that use `readfile`, `writefile`, `lsmode`, `fsdir`, `zipfile`, and `sqlar`.
- Shell tab completion or line-editing support that queries `completion(...)`.
- Shell `.expert` support that calls the `sqlite3expert` public API.
- Shell integrity-check commands or tests that can use `sqlite3_intck`.
- Shell diagnostic flags that register/use `vfstrace`.
- SQLite's extension loader, when these modules are built as loadable extensions rather than compiled into the shell.

For WiredTiger, the integration is indirect: this copy lives under `test/3rdparty/sqlite3` as a third-party SQLite shell source. It is likely used by tests, fixtures, or tooling that need a SQLite CLI with bundled features.

## Risks and Maintenance Notes

- Several modules are conditionally compiled. `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_HAVE_ZLIB`, `SQLITE_OMIT_SCHEMA_PRAGMAS`, and introspection pragma options materially change available APIs and behavior.
- `appendvfs` relies on exact trailer validation, 512-byte alignment, and offset translation. Any mistake can make a host file appear as a different database, hide an appended database, or corrupt the trailer. Its maximum-size guard is part of the locking safety story.
- `appendvfs` ordinary-database pass-through uses `memmove()` to copy the base file object over the wrapper. That path depends on `szOsFile` layout assumptions and on having allocated enough space for the base file after `ApndFile`.
- `zipfile` intentionally excludes encryption, multi-disk archives, ZIP64, and methods other than store/deflate. Large archives, large files, or ZIP64 metadata are unsupported and may fail or misparse.
- `zipfileRollback()` calls commit, so virtual-table transaction semantics are append-only rather than true rollback of already appended bytes. Consumers should not expect old archive bytes to be truncated on SQL rollback.
- `zipfileReadData()` uses `fseek()`/`ftell()` with casts to `long`, which is sensitive to platform large-file support.
- `zipfileScanExtra()` assumes well-formed extra-field lengths. Malformed archives are handled mostly through parse errors, but bounds validation is limited to the buffers loaded according to central-directory metadata.
- `sqlar_uncompress()` trusts the declared uncompressed size enough to allocate it. Bad or hostile `SZ` values can cause large allocations before zlib rejects data.
- `sqlite3expert` parses `EXPLAIN QUERY PLAN` detail text for substrings such as `USING INDEX`. This is coupled to SQLite planner output wording.
- `sqlite3expert` uses a generated index-name hash with a bounded collision loop. If no unique name is found after the loop, it returns `SQLITE_BUSY_TIMEOUT`.
- `sqlite3expert` prepares SQL with dummy UDFs and collations but asserts those callbacks should never execute. Any path that accidentally runs analysis statements rather than only preparing/explaining them would hit assertions in debug builds.
- `idxNewConstraint()` appears to allocate `sizeof(IdxConstraint) * nColl + 1` rather than `sizeof(IdxConstraint) + nColl + 1`; this over-allocates for non-empty collation names and is inefficient but not an under-allocation for ordinary inputs.
- `sqlite3intck` generates complex SQL using schema text and parsed index expressions. It is intentionally less thorough than `PRAGMA integrity_check` and can miss corruption classes documented in its header.
- `sqlite3intck` temporarily registers `parse_create_index`; close unregisters it with arity 1 while open registered arity 2. This is worth checking against surrounding SQLite extension behavior because a mismatched unregister arity may leave the function installed.
- `vfstrace` output formatting can leak file paths, VFS names, flags, and errors to the configured output stream. It should be considered diagnostic-only.
- This chunk ends in the middle of `vfstrace.c`. Final per-file research must merge later chunks to cover VFS registration, default selection, allocation of `vfstrace_info`, and the remaining pass-through VFS methods.

## Test Signals

Useful test signals for this chunk include:

- Loading or statically initializing `fileio` should make `readfile`, `writefile`, `lsmode`, and `fsdir` available; when virtual tables are omitted, the scalar functions should still register.
- `SELECT candidate FROM completion('sel')` should include keyword-like completions; `completion(NULL, 'main.tab')` style calls should derive the current prefix from `wholeline`.
- Opening an existing ordinary SQLite database through `apndvfs` should behave like the base VFS, while opening a non-database host file with create flags should append a database and write a valid `Start-Of-SQLite3-` trailer.
- Reopening an appended host file through `apndvfs` should expose the database at `iPgOne` and report database-relative file size as `iMark - iPgOne`.
- `zipfile()` aggregate calls should produce readable archive blobs for stored files, deflated files, directories, and explicit mode/mtime combinations.
- `SELECT name, data, rawdata, method FROM zipfile(?)` should read both filename-backed archives and BLOB archives. Deflated entries should inflate on the `data` column and remain compressed on `rawdata`.
- `INSERT`, `UPDATE`, `DELETE`, `OR IGNORE`, and `OR REPLACE` against filename-backed `zipfile` virtual tables should update the final central directory consistently.
- `sqlar_compress()` should return the original blob when compression is not smaller and a smaller zlib-format blob otherwise; `sqlar_uncompress()` should round-trip when given the correct uncompressed size.
- Expert tests should verify schema copy, target SQL loading, sample configuration boundaries (`0`, partial, `100`), candidate report text, selected index report text, and plan text for representative WHERE, range, ORDER BY, trigger, custom collation, and custom UDF cases.
- Incremental integrity tests should step through clean databases to `SQLITE_DONE`, report messages for induced table/index corruption, release and resume with `sqlite3_intck_unlock()`, and expose generated checker SQL through `sqlite3_intck_test_sql()`.
- `stmtrand()` should produce the same sequence after `sqlite3_reset()` for the same statement and seed, while multiple calls within one statement advance the sequence.
- `vfstrace` tests should register the tracing VFS in later code, exercise open/read/write/lock/file-control paths, and verify `PRAGMA vfstrace('-all,+read,+write')` changes the mask and output volume.

## Cross-Chunk Notes

- Lines before 8934 define most of `fileio.c`, including `readfileFunc`, `writefileFunc`, `lsModeFunc`, and the actual `fsdir` implementation. This chunk only covers registration.
- Lines after 17244 finish `vfstrace.c`; the complete VFS registration lifecycle and remaining VFS pass-through methods are outside this report.
- The final merged report for `shell.c` should describe how these extension initializers are invoked by the shell's startup and command handlers, which are mostly outside this chunk.
