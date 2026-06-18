# subset-b-008749 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/qrf/qrf.c -->
# sources/storage-engines/sqlite/ext/qrf/qrf.c

## Purpose

`qrf.c` implements SQLite's Query Result Format utility library. Its public job is to run an already-prepared `sqlite3_stmt` and render its result rows in shell-style output formats such as box, table, markdown, CSV, JSON, SQL insert statements, line mode, list mode, EXPLAIN, EXPLAIN QUERY PLAN, and scanstatus/stat modes. It is designed as a reusable formatter behind `sqlite3_format_query_result()` rather than as a standalone extension entry point.

The implementation is stateful for the lifetime of a single formatting call. It consumes the caller's statement, optionally changes explain mode through `sqlite3_stmt_explain()`, steps the statement to completion or an error, writes formatted output through a `sqlite3_str` buffer and/or caller-supplied writer callback, resets the statement, restores explain mode, and releases all temporary allocations.

## Important APIs, Types, And Functions

The exported API implemented here is `sqlite3_format_query_result(sqlite3_stmt *pStmt, const sqlite3_qrf_spec *pSpec, char **pzErr)`. It returns an SQLite result code, treats `NULL` statements as no-ops, rejects a `NULL` spec with `SQLITE_MISUSE`, and rejects a busy statement with `SQLITE_BUSY`.

`Qrf` is the central private state object. It stores the statement and database handle, the accumulated `sqlite3_str` output, copied and normalized `sqlite3_qrf_spec`, row/column counts, current error state, output width/height limits, optional JSONB translation statement, and a union of mode-specific state for line mode, EQP graphing, EXPLAIN indentation, and multi-row INSERT accumulation.

`qrfInitialize()` copies the caller spec, validates `iVersion`, normalizes out-of-range enum values to auto, chooses defaults, configures style-specific text/blob/null/title behavior, and switches statements into EXPLAIN or EXPLAIN QUERY PLAN mode when needed. `qrfFinalize()` emits style-specific trailers, flushes output, transfers `pzOutput` ownership if requested, frees mode-specific allocations, restores any prior explain mode, finalizes JSONB helper state, and propagates `sqlite3_str` errors.

Rendering helpers include `qrfRenderValue()` for SQLite value-to-text/blob conversion, `qrfEncodeText()` for SQL/CSV/HTML/Tcl/JSON/plain/relaxed text quoting, `qrfEscape()` for control-character escaping, `qrfDisplayWidth()`, `sqlite3_qrf_wcwidth()`, `sqlite3_qrf_wcswidth()`, `sqlite3_qrf_decode_utf8()`, and `qrfIsVt100()` for terminal-display width accounting. The width logic accounts for tabs, newlines, VT100 escapes, zero-width Unicode, and double-width Unicode through the large `aQrfUWidth` span table.

Columnar formatting is organized through `qrfColData`, `qrfColumnar()`, `qrfWrapLine()`, `qrfWidthPrint()`, `qrfPrintAligned()`, `qrfRowSeparator()`, `qrfBoxSeparator()`, `qrfSplitColumn()`, and `qrfRestrictScreenWidth()`. EXPLAIN and planner output use `qrfExplain()`, `qrfScanStatusVm()`, `qrfEqpAppend()`, `qrfEqpRender()`, `qrfEqpRenderLevel()`, and, when `SQLITE_ENABLE_STMT_SCANSTATUS` is available, `qrfEqpStats()` and `qrfStatsHeight()`.

## Control Flow

`sqlite3_format_query_result()` initializes `Qrf`, dispatches by normalized style, resets the statement, finalizes the formatter, and returns `qrf.iErr`. Box, column, markdown, and table styles call `qrfColumnar()` because they need all rows materialized to compute widths before printing. Explain style calls `qrfExplain()`. Stats VM builds a temporary `bytecode(?1)` query and routes it through EXPLAIN formatting. Stats and StatsEst synthesize EQP-like output from scanstatus. All other styles stream row-by-row through `qrfOneSimpleRow()`.

`qrfColumnar()` performs an initial `sqlite3_step()` to detect whether any rows exist. It then materializes optional headers and all cells into `qrfColData`, tracking natural display widths, numeric cells, multi-line cells, and maximum widths per column. After stepping is complete, it computes alignment, applies fixed or natural widths, enforces `nWrap`, optionally splits one-column output into multiple visual columns, optionally squashes wide columns to `nScreenWidth`, then renders headers/body/separators/borders. Multi-line cells are repeatedly passed through `qrfWrapLine()` until exhausted or `nLineLimit` is reached, in which case an ellipsis row is emitted.

`qrfOneSimpleRow()` handles streaming formats. JSON and JObject open or separate row objects and delegate to `qrfOneJsonRow()`. HTML emits table rows and optional header rows. INSERT mode batches rows into `INSERT INTO ... VALUES(...)` statements until `nMultiInsert` is reached, quoting identifiers conservatively with `qrf_need_quote()`. Line mode lazily caches column-name labels and prints each value under its label with optional wrapping. EQP mode accumulates graph rows and flushes when special separator rows are encountered. List-like modes optionally print titles, then render cells separated by `zColumnSep` and `zRowSep`.

`qrfExplain()` is explicitly two-pass. The first pass scans opcode rows and computes indentation based on loop and branch opcodes (`Next`, `Prev`, `VNext`, `VPrev`, `SorterNext`, `Return`, `Goto` with matching yield/seek/rewind targets). It resets the statement and performs a second pass to print a fixed-width table, with an alternate column map for scanstatus VM output. This assumes the first columns are equivalent to ordinary EXPLAIN output.

## State And Persistence Behavior

All durable state remains outside this file. The formatter does not write database tables or files itself; persistence is limited to the caller's statement state and caller-provided output target. It always calls `sqlite3_reset()` on the statement after dispatch and attempts to restore any prior explain mode recorded in `expMode`.

Output state is transient. `pOut` accumulates text until `qrfWrite()` flushes to `xWrite`, or until finalize transfers/finishes it. If `pSpec->pzOutput` is set, finalize either stores the finished string there or appends to an existing allocation using `sqlite3_realloc64()`. If `xWrite` is set, blobs in raw text mode can be written directly after flushing pending buffered text.

Some temporary SQLite state is created. JSONB rendering may open an in-memory database and prepare `SELECT json(?1)` into `pJTrans`; it is finalized and the in-memory database is closed in `qrfFinalize()`. Stats VM prepares a temporary query over `bytecode(?1)` and binds the original statement pointer.

## Dependencies And Integration Points

The file depends on `qrf.h`, the SQLite C API, `sqlite3_str`, `sqlite3_stmt_explain()`, `sqlite3_stmt_isexplain()`, `sqlite3_column_*()`, `sqlite3_keyword_check()`, `sqlite3_malloc64()/realloc64()/free()`, and optional scanstatus APIs under `SQLITE_ENABLE_STMT_SCANSTATUS`. It assumes SQLite printf extensions such as `%Q`, `%#Q`, and `%w`.

The primary integration point is clients that prepare a statement and pass a `sqlite3_qrf_spec`. The spec can redirect output through `xWrite`, collect it through `pzOutput`, customize value rendering through `xRender`, specify separators/table names/null text, and tune width, wrapping, title, alignment, JSONB, and blob behavior. The EXPLAIN and scanstatus modes integrate with SQLite VM introspection and the optional `bytecode()` table-valued function.

## Risks And Edge Cases

Columnar modes materialize the complete result set in memory, so very large result sets can consume substantial memory before producing output. This is intentional for width computation but a different risk profile from streaming styles. Width and Unicode calculations are approximate by design; terminals can disagree on zero-width or double-width character display, causing misalignment.

`qrfRenderValue()` relies on the caller's `xRender` returning SQLite-allocated memory that can be released with `sqlite3_free()`. Raw BLOB text output assumes `xWrite` exists in the default BLOB-text path; otherwise a raw text BLOB with no writer would be unsafe if such a spec combination is constructed. JSONB detection is a fast sanity check with possible false positives, though the `json(?1)` step is the real converter. `qrfJsonbToJson()` opens an auxiliary in-memory connection, so builds without JSON support simply fail to translate and fall back to ordinary blob rendering.

The code modifies statement explain mode for Eqp and Explain and restores it in finalize, but errors during initialization still flow through finalize because the public entry point dispatches using normalized state. Statement reset errors after stepping are captured by `qrfResetStmt()` only if no earlier error exists. `qrfColumnar()` returns early for no rows without resetting itself; the public wrapper performs reset afterward.

## Test Signals

High-value tests should cover every style in `qrf.h`, especially Box/Table/Markdown/Column width calculation, one-column split layout, `nScreenWidth`, `nWrap`, `nLineLimit`, title truncation, right/center/vertical alignment, and fixed negative widths. Encoding tests should include SQL, relaxed SQL, CSV separator collisions, HTML metacharacters, JSON/Tcl control characters, alternate escape modes, NULL rendering, raw and quoted blobs, and optional JSONB-as-text behavior.

Planner formatting tests should cover ordinary `EXPLAIN`, `EXPLAIN QUERY PLAN`, statement mode restoration, Stats/StatsEst with and without `SQLITE_ENABLE_STMT_SCANSTATUS`, and StatsVm/`bytecode(?1)` output where available. Error-path tests should cover busy statements, bad `iVersion`, writer callback failure, renderer callback results, OOM injection, `sqlite3_reset()` errors, large output with `pzOutput` append, and display width behavior for tabs, VT100 sequences, invalid UTF-8-like bytes, and double-width Unicode.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/qrf/qrf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/qrf/qrf.h -->
# sources/storage-engines/sqlite/ext/qrf/qrf.h

## Purpose

`qrf.h` is the public interface for SQLite's Query Result Format utility library. It defines the user-facing format specification structure, the single formatter entry point, constants for all supported output styles and encoding policies, tri-state switches, alignment values, and display-width helper declarations. The header is intentionally small and C/C++ compatible so callers can embed the formatter without depending on private implementation details from `qrf.c`.

## Important APIs, Types, And Constants

The central public type is `sqlite3_qrf_spec`. It is a versioned options structure. Its leading fields select style and encoding behavior: `iVersion`, `eStyle`, `eEsc`, `eText`, `eTitle`, and `eBlob`. Boolean-like fields are tri-state switches using `QRF_SW_Auto`, `QRF_SW_Off`, and `QRF_SW_On`: `bTitles`, `bWordWrap`, `bTextJsonb`, `bSplitColumn`, and `bBorder`.

Layout fields include `eDfltAlign`, `eTitleAlign`, `nWrap`, `nScreenWidth`, `nLineLimit`, `nTitleLimit`, `nCharLimit`, per-column width and alignment counts (`nWidth`, `nAlign`), and arrays (`aWidth`, `aAlign`). Text output customization includes `zColumnSep`, `zRowSep`, `zTableName`, and `zNull`. Extensibility hooks include `xRender` for caller-provided value rendering, `xWrite` for streaming output, `pRenderArg`, `pWriteArg`, and `pzOutput` for returning an allocated output string.

The primary function is `sqlite3_format_query_result(sqlite3_stmt *pStmt, const sqlite3_qrf_spec *pSpec, char **pzErr)`. The caller prepares a statement, fills a spec, and receives either formatted output through the spec's writer/string fields or an error code plus optional message.

Style constants range from automatic choice through table-like, delimiter, structured, planner, and suppress/count modes: `QRF_STYLE_Auto`, `Box`, `Column`, `Count`, `Csv`, `Eqp`, `Explain`, `Html`, `Insert`, `Json`, `JObject`, `Line`, `List`, `Markdown`, `Off`, `Quote`, `Stats`, `StatsEst`, `StatsVm`, and `Table`.

Text constants control text quoting: auto, plain, SQL, CSV, HTML, Tcl, JSON, and relaxed SQL. Blob constants control whether BLOB values are shown as raw text, SQL literal, hex, Tcl string, JSON string, size-only marker, or chosen automatically from text style. Escape constants control whether control characters are left alone, escaped as ASCII caret notation, or escaped as Unicode control pictures.

Alignment constants combine horizontal and vertical bits. `QRF_ALIGN_HMASK` selects left/center/right/auto and `QRF_ALIGN_VMASK` selects top/middle/bottom/auto; compound constants such as `QRF_ALIGN_NW`, `QRF_ALIGN_C`, and `QRF_ALIGN_SE` encode both axes.

The header also declares `sqlite3_qrf_wcwidth(int c)` and `sqlite3_qrf_wcswidth(const char*)` for estimating terminal display width.

## Control Flow Expectations

The header does not implement behavior, but it defines the contract followed by `qrf.c`. Callers provide an idle prepared statement and a spec. The implementation may consume all rows, reset the statement, and, for explain-related styles, temporarily switch statement explain mode. Columnar styles generally require complete result materialization to compute widths; list-like, JSON, HTML, insert, line, count, off, and EQP styles can stream row-by-row internally.

Defaults are mostly selected by the implementation when fields are zero or `QRF_*_Auto`. For example, automatic style chooses a normal table style for ordinary statements and planner-oriented styles for explain statements. Automatic title, text, blob, separator, null, and wrapping behavior is style-sensitive.

## State And Persistence Behavior

`sqlite3_qrf_spec` is passed by pointer but copied by the implementation before normalization. The strings and arrays referenced by the spec are caller-owned for the duration of the call. `pzOutput`, when non-NULL, is an output ownership channel: the formatter stores or extends a SQLite-allocated string and the caller is expected to release it with `sqlite3_free()`. `xRender` must return a SQLite-allocated string because the implementation releases it with `sqlite3_free()`.

No persistent database state is described by this header. The API formats query results and may use SQLite statement/database metadata, but durable writes are only whatever the caller's original statement performs while being stepped.

## Dependencies And Integration Points

The header depends on `sqlite3.h` and standard `stdlib.h`. It wraps declarations in `extern "C"` for C++ consumers. Integration is through the SQLite C API: callers pass `sqlite3_stmt*`, receive SQLite result codes, and use SQLite memory allocation conventions for returned strings and callbacks.

The spec is deliberately versioned with `iVersion` and a future-extension comment at the end of the struct. This means callers should initialize the structure predictably, normally with zero-filled storage plus explicit fields, so new trailing fields can default to automatic behavior.

## Risks And Edge Cases

Because this is a public ABI-style structure, field ordering and size matter. The implementation currently accepts only supported `iVersion` values, so callers that set a future version against an older library receive an error. Uninitialized specs are risky: many zero values mean auto, but pointer fields and counts must still be coherent. `nWidth` and `nAlign` must not exceed the actual lengths of `aWidth` and `aAlign`; the implementation trusts those counts.

Width limits use narrow integer fields for some options (`short int` for wrap/screen/line/title limits) and `int` for character limits. Very high requested widths should respect `QRF_MAX_WIDTH`/`QRF_MIN_WIDTH` and implementation caps. Display width helpers are estimates, not Unicode-rendering guarantees.

The callback contracts are important. A writer callback returning non-zero becomes a formatter error. A render callback can override all built-in type rendering for a value; if it returns NULL the built-in rendering path is used.

## Test Signals

Tests for this header/API boundary should compile the header from C and C++, zero-initialize specs, use every enum family, pass custom `xWrite` and `xRender` callbacks, and verify `pzOutput` allocation/append semantics. ABI-oriented tests should confirm old-version specs are accepted and unsupported versions are rejected. API misuse tests should cover `NULL` specs, `NULL` statements, busy statements, inconsistent width/alignment counts, and caller strings/separators used by CSV/List/Line/Insert modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/qrf/qrf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rbu/rbu.c -->
# sources/storage-engines/sqlite/ext/rbu/rbu.c

## Purpose

`rbu.c` is a small command-line driver for SQLite's Resumable Bulk Update extension. It applies an RBU update database to a target database, or runs an RBU-backed vacuum, using the public `sqlite3rbu.h` API. It exists as an executable wrapper around the library, with options for bounded stepping, periodic memory/progress reporting, vacuum mode, and optional SQL run against the opened RBU connections before stepping.

## Important APIs And Functions

`usage(const char *zArgv0)` prints command syntax and exits with code 1. The supported options are `-step NSTEP`, `-statstep NSTATSTEP`, `-vacuum`, and `-presql SQL`, followed by `TARGET-DB RBU-DB`.

`report_default_vfs()` reports the process default VFS using `sqlite3_vfs_find(0)`. `report_rbu_vfs(sqlite3rbu *pRbu)` obtains the target database connection from `sqlite3rbu_db(pRbu, 0)`, asks SQLite for `SQLITE_FCNTL_VFSNAME` on schema `main`, prints the VFS name if available, and frees the returned name with `sqlite3_free()`.

`main()` parses options by allowing abbreviated option names through prefix `memcmp()` checks bounded by each option's full length. It opens either `sqlite3rbu_vacuum(zTarget, zRbu)` or `sqlite3rbu_open(zTarget, zRbu, 0)`, optionally executes `zPreSql` on both the main and RBU database handles, steps the RBU handle up to `nStep` calls or until completion/error, closes the handle with `sqlite3rbu_close()`, reports final status, and returns success only for `SQLITE_OK` or `SQLITE_DONE`.

The RBU API calls are `sqlite3rbu_open()`, `sqlite3rbu_vacuum()`, `sqlite3rbu_db()`, `sqlite3rbu_step()`, `sqlite3rbu_progress()`, `sqlite3rbu_bp_progress()`, and `sqlite3rbu_close()`.

## Control Flow

The program requires at least two trailing positional arguments. It treats `argc-2` and `argc-1` as the target and RBU/state database paths. Options before those arguments configure mode and limits. `-step` controls the maximum number of `sqlite3rbu_step()` calls; when less than or equal to zero, stepping is unbounded until the update finishes or an error occurs. `-statstep` prints memory statistics every configured number of loop iterations. `-vacuum` switches from update mode to RBU vacuum mode. `-presql` captures a SQL string to run after opening the RBU handle and before stepping.

After parsing, the program prints the default VFS, opens the RBU handle, and reports the VFS used by the target connection. If pre-SQL is requested and the handle exists, it runs the SQL first against the main connection (`sqlite3rbu_db(pRbu, 0)`) and then against the RBU/state connection (`sqlite3rbu_db(pRbu, 1)`) only if the first execution succeeds.

The stepping loop calls `sqlite3rbu_step(pRbu)` in the loop condition. Each successful `SQLITE_OK` step increments `i`. If stat reporting is enabled and `i % nStatStep == 0`, the program prints memory usage/highwater via `sqlite3_status64()`. In non-vacuum mode it also prints backfill progress from `sqlite3rbu_bp_progress()`.

When the loop exits, the program reads `sqlite3rbu_progress(pRbu)`, closes the handle, and lets `sqlite3rbu_close()` determine whether the operation is incomplete (`SQLITE_OK`), complete (`SQLITE_DONE`), or failed. It prints a final message, optional final memory stats, frees any close error message, and exits 0 for incomplete-or-complete success and 1 for failures.

## State And Persistence Behavior

Durable state is managed by the RBU library and the databases named on the command line. If `nStep` limits work before completion, `sqlite3rbu_close()` saves resumable state in the RBU database for update mode or the state database for vacuum mode. A later invocation can resume through the same library APIs. The driver itself has no separate state file.

The program may mutate both target and RBU/state databases. Normal update mode applies changes from the RBU database into the target. Vacuum mode uses RBU to vacuum the target using the second database as the state store. `-presql` is especially powerful because it executes arbitrary SQL against both opened connections before stepping.

In-process state includes counters, progress totals, an optional error string from `sqlite3rbu_close()`, and transient VFS-name strings returned by file control.

## Dependencies And Integration Points

The file depends on `sqlite3rbu.h` plus C standard headers `stdio.h`, `stdlib.h`, and `string.h`. It also indirectly uses SQLite APIs exposed by the RBU header, including VFS discovery, file-control, status counters, and memory cleanup.

The integration point is a compiled CLI linked with the RBU extension implementation. It is useful in test scripts and manual update/vacuum workflows where bounded calls demonstrate resumability. The surrounding `ext/rbu` directory contains many Tcl tests for RBU behavior, including crash/resume, vacuum, fault injection, and progress cases; this driver is the simple executable interface to the same library.

## Risks And Edge Cases

Option parsing allows prefixes such as `-s` for `-step` and `-v` for `-vacuum` as long as they satisfy the length guard. This is convenient but can make ambiguous future option additions risky. Numeric options use `atoi()`, so invalid strings silently become zero and negative values mean unbounded stepping.

The code does not explicitly check for a failed `sqlite3rbu_open()` or `sqlite3rbu_vacuum()` before the stepping block. If `pRbu` is NULL and `rc` remains `SQLITE_OK`, the later `sqlite3rbu_step(pRbu)`, `sqlite3rbu_progress(pRbu)`, or `sqlite3rbu_close(pRbu, ...)` behavior depends on the RBU API's NULL handling. The VFS report function itself tolerates a NULL or unusable handle only through `sqlite3rbu_db()` returning NULL.

`zPreSql` errors prevent stepping and also skip `sqlite3rbu_close()`, because close is only called inside the `rc==SQLITE_OK` stepping block. If a handle was opened and pre-SQL fails, this path risks not closing the RBU handle before exit. This matters for resource cleanup and possibly for any open transaction state controlled by the RBU handle.

Progress reporting prints at `i==0` after the first successful step because `i` is incremented after the loop body. That is observable but likely harmless. Format strings use `%lld` with `sqlite3_int64`; SQLite's supported platforms generally make this acceptable, but strictly portable code often casts to `long long`.

## Test Signals

CLI tests should cover update and vacuum modes, unbounded stepping, small positive `-step` followed by resume, `-statstep`, and `-presql` success/failure against both handles. Error tests should include missing arguments, malformed numeric arguments, invalid RBU database, invalid target path, VFS reporting without available VFS name, RBU open failure, and close-time error messages.

RBU integration tests should verify that `SQLITE_OK` means incomplete resumable success, `SQLITE_DONE` means complete success, and all other result codes exit non-zero. Crash/resume and bounded-step tests from the `ext/rbu` suite are the strongest behavioral signals because this program relies almost entirely on the library for persistence and correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rbu/rbu.c -->
