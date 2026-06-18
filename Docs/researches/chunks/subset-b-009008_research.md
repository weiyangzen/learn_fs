# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/shell.c lines 17245-25464

## Scope

This chunk covers a large middle section of SQLite's amalgamated command-line shell source as vendored under WiredTiger tests. The range starts at the tail of the `vfstrace` VFS shim, then includes the recover extension public header, the `sqlite_dbdata`/`sqlite_dbptr` virtual-table implementation, most of `sqlite3recover.c`, and the beginning of the shell's core runtime state and output/SQL execution machinery. It ends partway through the shell help text, after the `.output` entry.

The chunk is conditionally compiled around several features: recovery support requires `!SQLITE_OMIT_VIRTUALTABLE && SQLITE_ENABLE_DBPAGE_VTAB`; session state requires `SQLITE_ENABLE_SESSION`; editor and filesystem features are removed for `SQLITE_NOHAVE_SYSTEM` or `SQLITE_SHELL_FIDDLE`; authorization, scan-status, and deserialize help text depend on their corresponding SQLite build flags. The code is therefore both shell functionality and embedded extension code compiled into the standalone sqlite3 CLI when options allow.

## Purpose

The covered code serves four major purposes:

- Complete the `vfstrace` extension registration path, allowing the shell or tests to wrap a lower VFS and log selected VFS calls.
- Provide the recovery API and implementation used by the CLI `.recover` feature: recover schema, table data, orphan pages, and optional SQL script output from a corrupt database by reading raw pages through `sqlite_dbpage` and interpreting b-tree records directly.
- Define the central `ShellState` structure, shell mode constants, output escaping/formatting helpers, query execution callbacks, auto-EQP/scanstats plumbing, parameter binding, and dump helpers.
- Seed the CLI help table for dot commands visible in this part of the file.

In the larger file, this range bridges low-level SQLite extension internals with high-level CLI behavior. It is not isolated library code: many static helpers here depend on global shell utilities and SQLite APIs declared earlier in `shell.c`, and later dot-command dispatch code calls the APIs and helpers defined here.

## Important APIs, Types, and Functions

### VFS tracing tail

The opening lines finish `vfstrace.c`. `vfstraceRandomness()`, `vfstraceSleep()`, `vfstraceCurrentTime()`, `vfstraceCurrentTimeInt64()`, and `vfstraceGetLastError()` wrap the corresponding root VFS calls, toggle trace categories, and emit formatted diagnostics. `vfstraceSetSystemCall()`, `vfstraceGetSystemCall()`, and `vfstraceNextSystemCall()` forward VFS v3 syscall override APIs. `vfstrace_register()` allocates a new `sqlite3_vfs`, embeds `vfstrace_info`, copies the trace VFS name, installs wrapper methods based on the root VFS version, and registers the shim. `vfstrace_unregister()` unregisters only VFS instances whose `xOpen` matches `vfstraceOpen`, preventing accidental removal of unrelated VFS implementations.

### Recovery public API

When recovery is enabled, the embedded `sqlite3recover.h` declares opaque `sqlite3_recover` handles and these public APIs:

- `sqlite3_recover_init()` creates a recovery job that writes a new output database.
- `sqlite3_recover_init_sql()` creates a job that emits SQL statements through a callback instead of writing a database directly.
- `sqlite3_recover_config()` accepts `SQLITE_RECOVER_LOST_AND_FOUND`, `SQLITE_RECOVER_FREELIST_CORRUPT`, `SQLITE_RECOVER_ROWIDS`, and `SQLITE_RECOVER_SLOWINDEXES`.
- `sqlite3_recover_step()` performs incremental work, `sqlite3_recover_run()` runs to completion, and `sqlite3_recover_finish()` tears down the handle.
- `sqlite3_recover_errcode()` and `sqlite3_recover_errmsg()` expose final or in-progress errors.

### `sqlite_dbdata` and `sqlite_dbptr`

The `DbdataTable`, `DbdataCursor`, and `DbdataBuffer` types implement two eponymous virtual tables:

- `sqlite_dbdata(pgno, cell, field, value, schema HIDDEN)` reads raw b-tree pages and exposes each record field plus rowid pseudo-fields for intkey tables.
- `sqlite_dbptr(pgno, child, schema HIDDEN)` exposes parent-to-child page pointers from b-tree interior pages.

Key methods are the SQLite virtual table callbacks: `dbdataConnect()`, `dbdataDisconnect()`, `dbdataBestIndex()`, `dbdataOpen()`, `dbdataClose()`, `dbdataFilter()`, `dbdataNext()`, `dbdataColumn()`, `dbdataRowid()`, and `dbdataEof()`. `sqlite3DbdataRegister()` registers both module names with the same `sqlite3_module`, using `pAux` to distinguish pointer-table mode.

Parsing helpers include `dbdataLoadPage()` for fetching raw page blobs from `sqlite_dbpage` or a page-provider function, `dbdataGetVarint()`/`dbdataGetVarintU32()`, `dbdataValueBytes()`, and `dbdataValue()`. `dbdataNext()` is the central scanner: it walks pages, classifies b-tree page types, follows overflow chains, copies payloads with padding, parses record headers, and advances through fields while tolerating corruption.

### Recovery implementation state

The recovery implementation defines:

- `RecoverTable` and `RecoverColumn`, which map recovered schema tables and columns to original root pages, record fields, bind indexes, generated-column handling, integer-primary-key handling, and WITHOUT ROWID detection.
- `RecoverBitmap`, used by lost-and-found recovery to track pages already assigned to recovered schema trees or freelist pages.
- `RecoverStateW1`, used while writing rows into recovered schema tables.
- `RecoverStateLAF`, used across the three lost-and-found phases.
- `struct sqlite3_recover`, which holds input/output database handles, callback mode, configuration, page/header repair buffers, error state, state-machine state, prepared statements, and recovered table metadata.
- `RecoverGlobal recover_g`, protected by `SQLITE_MUTEX_STATIC_APP2`, used temporarily while a wrapper `sqlite3_io_methods` intercepts reads of page 1.

Important support helpers include `recoverMalloc()`, `recoverError()`, `recoverDbError()`, `recoverPrepare()`, `recoverPreparePrintf()`, `recoverReset()`, `recoverFinalize()`, `recoverExec()`, `recoverBindValue()`, `recoverMPrintf()`, and `recoverPageCount()`. SQL helper functions registered on the output handle include `recoverReadI32()`, `recoverPageIsUsed()`, `recoverGetPage()`, and `recoverEscapeCrlf()`.

The main public functions are implemented by `recoverInit()`, `sqlite3_recover_init()`, `sqlite3_recover_init_sql()`, `sqlite3_recover_config()`, `sqlite3_recover_step()`, `sqlite3_recover_run()`, and `sqlite3_recover_finish()`. The private `recoverStep()` function drives the state machine.

### Recovery schema/data/lost-and-found functions

Schema and output setup are handled by `recoverOpenOutput()`, `recoverOpenRecovery()`, `recoverTransferSettings()`, `recoverCacheSchema()`, `recoverWriteSchema1()`, and `recoverWriteSchema2()`. `recoverAddTable()` introspects tables created in the output database to build `RecoverTable` metadata, including generated columns, hidden columns, integer primary keys, and WITHOUT ROWID indexes.

Data recovery is handled by `recoverWriteDataInit()`, `recoverWriteDataStep()`, and `recoverWriteDataCleanup()`. These functions iterate recovered root pages through recursive SQL over `sqlite_dbptr('getpage()')`, select cells and fields from `sqlite_dbdata('getpage()')`, accumulate row values, synthesize `INSERT OR IGNORE` statements through `recoverInsertStmt()`, and optionally issue SQL callback output.

Lost-and-found support is split across `recoverLostAndFound1Init()`/`recoverLostAndFound1Step()`, `recoverLostAndFound2Init()`/`recoverLostAndFound2Step()`, and `recoverLostAndFound3Init()`/`recoverLostAndFound3Step()`. The first phase marks used pages, optionally excluding freelist pages unless `bFreelistCorrupt` is set. The second maps unclaimed pages to likely parent/root pages and computes the maximum recovered field count. The third creates an output lost-and-found table, scans unclaimed pages with `sqlite_dbdata`, and inserts recoverable records through `recoverLostAndFoundOnePage()`.

### Recovery VFS wrapper

`recoverIsValidPage()` validates candidate b-tree pages by checking page type, freeblocks, cell pointer arrays, payload local/overflow sizing, fragment counts, and overlap. `recoverVfsDetectPagesize()` scans the first up-to-four 64 KiB blocks of a file to infer page size and reserved bytes if the header is corrupt.

The `recover_methods` wrapper and functions `recoverVfsRead()`, `recoverVfsWrite()`, `recoverVfsTruncate()`, `recoverVfsSync()`, `recoverVfsFileSize()`, `recoverVfsLock()`, `recoverVfsUnlock()`, `recoverVfsCheckReservedLock()`, `recoverVfsFileControl()`, `recoverVfsSectorSize()`, `recoverVfsDeviceCharacteristics()`, `recoverVfsShmMap()`, `recoverVfsShmLock()`, `recoverVfsShmBarrier()`, `recoverVfsShmUnmap()`, `recoverVfsFetch()`, and `recoverVfsUnfetch()` temporarily forward all methods to the underlying file except page-1 reads. `recoverVfsRead()` can replace the database header with a sane synthesized header while preserving key fields, letting SQLite open/read corrupt files far enough for recovery. `recoverInstallWrapper()` and `recoverUninstallWrapper()` swap the file handle's `pMethods` under the recovery mutex.

### Shell state and output/query execution

`OpenSession`, `ExpertInfo`, `EQPGraphRow`, `EQPGraph`, `ColModeOpts`, and especially `ShellState` define the CLI's runtime state. `ShellState` tracks database connections, output streams, mode and separator settings, explain/EQP/scanstats flags, safe mode, progress callbacks, temp output files, active statement, session state, auxiliary connections, indentation state, nonce state, EQP graph, expert advisor object, and WASM fiddle state when compiled.

Mode and flag constants define `AUTOEQP_*`, `SHELL_OPEN_*`, `SHELL_TRACE_*`, `SHELL_PROGRESS_*`, `SHELL_ESC_*`, `SHFLG_*`, `MODE_*`, separators, and input nesting limits. `shellLog()`, `shellPutsFunc()`, `failIfSafeMode()`, and `editFunc()` provide logging, SQL-visible output, safe-mode enforcement, and the SQL `edit()` helper.

Output helpers include `outputModePush()`, `outputModePop()`, `setCrlfMode()`, `output_hex_blob()`, `output_quoted_string()`, `output_quoted_escaped_string()`, `anyOfInStr()`, `zSkipValidUtf8()`, `output_c_string()`, `output_json_string()`, `escapeOutput()`, `output_html_string()`, `output_csv()`, `printSchemaLine()`, `printSchemaLineN()`, `print_dashes()`, `print_row_separator()`, `print_box_line()`, `print_box_row_separator()`, `translateForDisplayAndDup()`, `needUnistr()`, and `quoted_column()`.

Execution and diagnostics helpers include `shell_callback()`, `callback()`, `captureOutputCallback()`, `createSelftestTable()`, `set_table_name()`, `shell_error_context()`, `run_table_dump_query()`, `save_err_msg()`, `displayLinuxIoStats()`, `displayStatLine()`, `display_stats()`, `scanStatsHeight()`, `display_explain_scanstats()`, `str_in_array()`, `explain_data_prepare()`, `explain_data_delete()`, `display_scanstats()`, `disable_debug_trace_modes()`, `restore_debug_trace_modes()`, `bind_table_init()`, `bind_prepared_stmt()`, `exec_prepared_stmt_columnar()`, `exec_prepared_stmt()`, `expertHandleSQL()`, `expertFinish()`, `expertDotCommand()`, `shell_exec()`, `freeColumnList()`, `tableColumnList()`, `toggleSelectOrder()`, `dump_callback()`, and `run_schema_dump_query()`.

## Control Flow

The VFS trace path is mostly straight delegation: public registration allocates and installs a VFS shim, each wrapper logs and forwards to the root VFS, and unregister frees only recognized shims.

The `sqlite_dbdata`/`sqlite_dbptr` virtual table flow starts with `xBestIndex` recognizing hidden `schema=?` and optional `pgno=?` constraints. `xFilter` resets the cursor, decides whether to scan one page or the full database, prepares a page-loading statement or function call, binds the schema, probes page-1 encoding, and advances to the first row. `dbdataNext()` then loops until it finds a row or reaches EOF. For `sqlite_dbptr`, it emits child pointers from interior b-tree pages. For `sqlite_dbdata`, it loads a page, validates enough structure to avoid unsafe reads, walks cells, extracts local and overflow payload bytes, parses the record header, returns rowid field `-1` for intkey pages, and advances field-by-field before moving to the next cell or page.

The recovery state machine in `recoverStep()` proceeds as follows:

- `RECOVER_STATE_INIT`: emit begin pragmas to SQL callback mode, enter the recovery mutex, open output, optionally install the VFS header wrapper, start a transaction on the input, transfer settings, attach the recovery database, cache schema rows, then create the first-stage output schema and move to writing.
- `RECOVER_STATE_WRITING`: initialize table-writing statements if needed, recover table rows one step at a time, then either move to lost-and-found or to schema finalization.
- `RECOVER_STATE_LOSTANDFOUND1`: build the used-page bitmap from schema roots, reachable child pages, and possibly freelist pages.
- `RECOVER_STATE_LOSTANDFOUND2`: build parent/root mapping for unclaimed pages and determine lost-and-found column capacity.
- `RECOVER_STATE_LOSTANDFOUND3`: create and populate the lost-and-found table one page at a time.
- `RECOVER_STATE_SCHEMA2`: create deferred views/triggers/non-unique indexes, commit output, end the input transaction, issue callback commit statements, and clean up.
- `RECOVER_STATE_DONE`: no-op.

`sqlite3_recover_step()` returns `SQLITE_OK` while more work remains, `SQLITE_DONE` only once the state is done without error, and otherwise the stored error. `sqlite3_recover_run()` loops over `sqlite3_recover_step()`. `sqlite3_recover_finish()` performs final cleanup and ends an open input transaction if needed.

The shell execution flow in `shell_exec()` prepares one SQL statement at a time from an input string. If `.expert` is active, SQL is routed into the expert object and finished instead of executed normally. Otherwise each statement may first run auto-EQP and auto-EXPLAIN variants, with debug trace modes temporarily disabled and trigger EQP toggled. The statement is then bound with values from `temp.sqlite_parameters` or special `$int_`/`$text_`/`_NAN`/`_INF` names, executed through `exec_prepared_stmt()`, and followed by EQP rendering, stats, scanstats, finalize/error handling, and advancement to the next statement.

Result output is mode-driven. Simple modes stream each row through `shell_callback()`. Column/table/box/markdown modes call `exec_prepared_stmt_columnar()`, which buffers all result text, splits/wraps display lines, computes widths, then renders the full table. Dump paths use `dump_callback()` and `run_table_dump_query()` to generate SQL text and retry in reverse rowid order if corruption interrupts ordinary traversal.

## State and Persistence Behavior

The recovery code persists state in several layers. The input database is opened under a read transaction and may be read through a temporary file-method wrapper that modifies page-1 bytes only in SQLite's read buffer, not on disk. The output database identified by `zUri` is opened read-write/create and is overwritten by `recoverTransferSettings()` via a backup from an empty temp database before recovered schema/data are written. The auxiliary `recovery` database is attached using `zStateDb` and stores temporary `recovery.schema` and `recovery.map` tables.

`sqlite3_recover` owns all recovery lifetime state: allocated strings, page-size/header repair buffers, error message, output connection, prepared statements, bitmap, value arrays, and recovered table metadata. Error state is sticky: most helper functions no-op once `errCode` is not `SQLITE_OK`. `sqlite3_recover_config()` is valid only before the first step, enforced by `RECOVER_STATE_INIT`.

`dbdata` cursor state is transient but sensitive: it caches the current page buffer, record buffer, field pointers, rowid, page number, cell number, and page count. `DbdataTable` caches one reusable page statement between cursors by moving it between `pTab->pStmt` and `pCsr->pStmt`.

`ShellState` is the long-lived mutable CLI session object. It persists mode settings, separators, output files, open database handles, auxiliary connections, current prepared statement, statistics flags, progress counts, safe-mode nonce, `.expert` state, and optional session objects. Temporary filesystem state is created by `editFunc()` and output redirection code outside this chunk; `editFunc()` writes a temp file, invokes the configured editor through `system()`, reads back content, and unlinks the temp file.

Output behavior can affect external state: `.dump` and shell query output write to `p->out`; `.log` uses `p->pLog`; `edit()` launches an external command unless omitted; `createSelftestTable()` mutates the database by creating/populating `selftest`; `bind_table_init()` creates `temp.sqlite_parameters` while temporarily disabling defensive mode and writable-schema restrictions.

## Dependencies and Integration Points

This chunk depends heavily on SQLite C APIs: VFS registration, virtual table module callbacks, `sqlite3_dbpage`, prepared statements, SQL scalar functions, backup API, file controls, mutexes, memory allocation, `sqlite3_value_dup/free`, `sqlite3_str`, status APIs, authorizer callbacks, scan-status APIs, `sqlite3_stmt_explain()`, parameter binding, and shell-specific formatting wrappers.

Recovery depends on the `sqlite_dbpage` virtual table being available on the input handle and registers `sqlite_dbdata`/`sqlite_dbptr` on the output handle. It also depends on SQLite's b-tree page format, varint format, record serial types, overflow-page layout, schema table layout, `PRAGMA table_xinfo`, and `PRAGMA index_xinfo`. The CLI `.recover` command later in the file is the primary integration point for the public `sqlite3_recover_*` APIs.

The shell runtime code integrates with later dot-command parsing and main-loop code. `ShellState` fields are read and written throughout the rest of `shell.c`; output modes are selected by `.mode`; parameter bindings by `.parameter`; auto-EQP by `.eqp`; stats by `.stats`/`.scanstats`; dump helpers by `.dump`; safe-mode authorizer by safe-mode setup; and `.expert` by `expertDotCommand()` and `shell_exec()`.

Platform dependencies include `_WIN32` console and CRLF handling, Linux `/proc/PID/io` stats, optional `system()` use for `edit()`, optional UTF-16 output handling, optional scan-status bytecode virtual table use, and WASM/fiddle exclusions for host filesystem and process access.

## Risks and Edge Cases

- Recovery intentionally operates on corrupt input. Bounds checks, padding, varint limits, page validation, and overflow-chain handling are security-relevant; mistakes can become out-of-bounds reads or unbounded loops on hostile database files.
- The recovery VFS wrapper mutates `sqlite3_file.pMethods` under a global static mutex. Incorrect install/uninstall sequencing could leave the input connection with the wrong methods or race if the same connection/file is used concurrently.
- `recover_g` is global and supports only one wrapped recovery read at a time. The mutex is intended to serialize the first-step setup, but future changes must not widen wrapper use outside the protected region.
- Page-size detection scans raw bytes and tries both reserved-byte and zero-reserve interpretations. False positives can lead to malformed synthesized headers and incorrect page-count calculations.
- `recoverTransferSettings()` overwrites/truncates the output database before recovery proceeds. Callers must treat `zUri` as destructive output, not an append or repair-in-place target.
- SQL callback mode builds SQL text using quoting and `escape_crlf()`. Bugs here can produce scripts that fail to replay, alter newline content, or mishandle blobs/text with control characters.
- Lost-and-found mode may recover deleted records if `SQLITE_RECOVER_FREELIST_CORRUPT` is set and can assign orphan pages to inferred roots. Results are best-effort and may include unrelated or stale data.
- `dbdataNext()` tolerates corruption by skipping bad pages/cells rather than reporting corruption. That is desirable for recovery but unsuitable as an integrity checker.
- Shell output functions handle UTF-8, control characters, CRLF translation, JSON, SQL literals, HTML, CSV, and terminal box drawing. Off-by-one or width mistakes here can corrupt exported output or produce invalid JSON/SQL/CSV.
- `editFunc()` shells out using the configured editor string and a temp filename. It is intentionally blocked by safe-mode authorization, but builds or paths that bypass safe mode expose command execution.
- `bind_prepared_stmt()` falls back to NULL for unbound parameters and supports special parameter-name conventions. This can hide missing parameters during interactive use if the user expected SQLite's default binding errors.
- Auto-EQP temporarily rewrites a prepared statement into explain modes and disables debug trace flags. Cleanup must reset the statement and restore trace/trigger settings even on error paths.
- Columnar output buffers the entire result set before rendering. Large query results can consume substantial memory compared with streaming modes.
- Dump retry on corruption toggles `PRAGMA reverse_unordered_selects`, which changes traversal order globally on the connection while retrying and must be toggled back.

## Test and Validation Signals

Useful validation for this chunk includes:

- Build the shell with recovery enabled (`SQLITE_ENABLE_DBPAGE_VTAB`, virtual tables enabled) and disabled, ensuring all conditional paths compile.
- Exercise `.recover` against a valid database, a database with a damaged header, a database with damaged schema rows, overflow records, WITHOUT ROWID tables, generated columns, virtual tables, indexes, triggers, and views.
- Exercise `.recover --lost-and-found` style behavior with and without freelist corruption configured, checking that orphan pages are mapped and recovered without crashing.
- Run recovery in SQL callback mode and replay the emitted script, including rows containing blobs, quotes, CR, LF, and control characters.
- Query `sqlite_dbdata` and `sqlite_dbptr` directly with `schema=?`, `pgno=?`, and function-style page providers such as `getpage()` to verify planner constraints, page scanning, rowids, field decoding, and pointer output.
- Test corrupt-page inputs with truncated pages, invalid cell pointers, oversized varints, invalid overflow pointers, bad freeblocks, and weird reserved-byte/page-size combinations under ASAN/UBSAN.
- Validate `.mode` output for `list`, `csv`, `quote`, `insert`, `json`, `html`, `tcl`, `line`, `column`, `table`, `box`, `markdown`, `ascii`, `eqp`, and count modes, including NULL, blob, UTF-8, invalid/control bytes, CRLF, very wide text, and multiline text.
- Verify `.eqp`, `.eqp full`, `.eqp trigger`, `.explain`, `.scanstats`, `.stats`, and bytecode scanstats output against representative SELECT/trigger statements.
- Test `.parameter` binding through `temp.sqlite_parameters`, anonymous parameters, named parameters, `$int_*`, `$text_*`, `_NAN`, and `_INF`.
- Test `.dump` on ordinary databases, virtual tables, `sqlite_sequence`, `sqlite_stat?`, rowid preservation, data-only/no-system modes, and intentionally corrupt tables to exercise reverse-order retry.
- Verify safe-mode authorization rejects `edit()`, `load_extension()`, read/write file helpers, zipfile helpers, tokenizer access, and host `ATTACH` where applicable.
- Run platform-specific checks for Windows CRLF/console handling and Linux `/proc/PID/io` stats where those code paths are compiled.

## Chunk Boundaries for Merge

This chunk begins in the middle of `vfstrace.c`; earlier VFS file/open/delete/access methods and trace mask definitions are outside this range. It ends in the middle of the `azHelp[]` table, so later help entries and all subsequent dot-command dispatch are outside this document. The full per-file report should merge this chunk with adjacent `shell.c` chunks to present complete VFS tracing, complete CLI command coverage, and the final `.recover` command integration point.
