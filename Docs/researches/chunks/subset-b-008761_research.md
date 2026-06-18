# sources/storage-engines/sqlite/ext/wasm/libcmpp.c lines 16048-16877

## Scope

This chunk covers the tail of SQLite's `generate_series` virtual-table extension embedded in `libcmpp.c`, followed by the beginning of the c-pp demonstration directive module. The `generate_series` portion includes cursor rowid/EOF helpers, 64-bit step-count and floating bound helpers, `seriesFilter()`, `seriesBestIndex()`, the `sqlite3_module` method table, and `sqlite3_series_init()`. The c-pp portion defines demo directive callbacks, HTML div wrapper helpers, directive autoloading, and `cmpp_module__demo_register()`.

## Purpose

- Implement the scan-time and planner-time logic for SQLite's `generate_series` virtual table.
- Translate hidden-column constraints, `value` constraints, ordering, `LIMIT`, and `OFFSET` into a bounded integer cursor range without signed-overflow undefined behavior.
- Register the `generate_series` virtual table with SQLite when virtual tables are enabled.
- Provide sample c-pp directives that demonstrate argument handling, paired open/close directives, block consumption, autoload registration, per-directive state, and module registration.

## Important APIs, Types, And Functions

- `seriesRowid()` returns the current generated integer as the SQLite rowid.
- `seriesEof()` reports `series_cursor.bDone`, which is set by `seriesFilter()` for empty scans and by `seriesNext()` after the terminal value is emitted.
- `seriesSteps()` computes how many increments separate `iBase` and `iTerm` using `span64()` and unsigned `iStep`, honoring ascending and descending scans.
- `seriesCeil()` and `seriesFloor()` abstract ceil/floor behavior. They use libc math when available, compiler builtins on GCC/Clang when allowed, and local integer-based fallbacks otherwise.
- `seriesFilter()` is the virtual-table `xFilter` implementation. It consumes the `idxNum` bitmask and SQLite values prepared by `seriesBestIndex()`, initializes `series_cursor`, narrows the range, applies ordering, and applies `LIMIT`/`OFFSET`.
- `seriesBestIndex()` is the virtual-table planner hook. It inspects `sqlite3_index_info` constraints, builds the `idxNum` bitmask, assigns argument indexes, marks constraints omittable when safe, estimates cost/rows, consumes compatible `ORDER BY`, and rejects unusable input constraints.
- `seriesModule` wires the virtual-table method table, using `seriesConnect`, `seriesDisconnect`, `seriesOpen`, `seriesClose`, `seriesFilter`, `seriesNext`, `seriesEof`, `seriesColumn`, and `seriesRowid`.
- `sqlite3_series_init()` is the extension entry point. It checks the SQLite version for older runtimes and calls `sqlite3_create_module(db, "generate_series", &seriesModule, 0)`.
- `cmpp_dx_f_demo1()` is a simple c-pp directive callback that emits a greeting and dumps each parsed argument's token type, length, and text.
- `divOpener()` emits an opening HTML `<div>` tag, treating directive arguments as CSS class names.
- `cmpp_dx_f_divOpen()` and `cmpp_dx_f_divClose()` implement a paired directive with stateful nesting count.
- `cmpp_dx_f_divWrapper()` consumes input until the matching closer directive, processes nested directives, chomps trailing whitespace, and wraps the captured content in a div.
- `cmpp_d_autoload_f_demos()` lazily registers demo directives by name, including closer-name aliases where appropriate.
- `cmpp_module__demo_register()` eagerly registers the demo directives with a c-pp instance.

## Control Flow

For `generate_series`, planning starts in `seriesBestIndex()`. It scans `pIdxInfo->aConstraint` and recognizes equality constraints on hidden `start`, `stop`, and `step` columns; equality and range constraints on `value` or rowid; `LIMIT`; and `OFFSET`. It records the selected constraints in `aIdx[]`, sets matching bits in `idxNum`, and assigns `argvIndex` values in the exact order expected by `seriesFilter()`: start, stop, step, limit, offset, lower/equality value constraint, then upper value constraint. Without `ZERO_ARGUMENT_GENERATE_SERIES`, the planner requires either a usable `start=` constraint or a usable value/rowid lower/equality constraint and returns an error message if the first argument is missing or unusable.

At scan time, `seriesFilter()` first rejects any NULL constraint value by jumping to the no-rows path. It loads original `start`, `stop`, and `step` values into `iOBase`, `iOTerm`, and `iOStep`, using defaults of `0`, `0xffffffff`, and `1` for omitted inputs. If only `value` constraints are present, the default generation range is widened to the full signed 64-bit range so the value constraints can define the effective bounds.

`seriesFilter()` stores the absolute step magnitude in unsigned `iStep`, including the `SMALLEST_INT64` negative-step case that requires a magnitude of `9223372036854775808`. It rejects directionally impossible ranges before processing output-value constraints. Equality, lower-bound, and upper-bound constraints on `value` are converted into integer `iMin` and `iMax` bounds, with floating-point inputs accepted only when they can be rounded according to SQL comparison semantics without falling outside signed 64-bit range. The cursor range is then advanced or contracted to the first reachable value within those bounds.

After value-constraint narrowing, `seriesFilter()` snaps `iTerm` to the last value actually reachable from `iBase` by a whole number of steps. If the planner consumed an `ORDER BY` request that is opposite to the natural step direction, it swaps `iBase` and `iTerm` and flips `bDesc`. Finally, it applies `OFFSET` by advancing `iBase` and applies non-negative `LIMIT` by shortening `iTerm`. Success initializes `iValue = iBase` and clears `bDone`; all empty or invalid cases reset the cursor to a benign one-row-shape state with `bDone = 1`.

The module table exposes the generate-series cursor as a read-only, innocuous virtual table. `sqlite3_series_init()` installs that module unless virtual tables are omitted.

The c-pp demo module starts with build-mode preprocessor selection: when compiled as part of the main c-pp app, `CMPP_D_DEMO` keeps the code inline; when built as a standalone module and the module-registration helper is absent, it defines `CMPP_MODULE_STANDALONE`/`CMPP_API_THUNK` and includes `libcmpp.h`. Directive execution then flows through callbacks registered by `cmpp_d_autoload_f_demos()` or `cmpp_module__demo_register()`. The wrapper directive calls `cmpp_dx_consume_b()` with its closer descriptor and `cmpp_dx_consume_F_PROCESS_OTHER_D`, so nested directives are processed while the block is consumed.

## State And Persistence Behavior

The `generate_series` implementation has no persistent storage of its own. Its state is a transient `series_cursor` allocated by `seriesOpen()` and freed by `seriesClose()`. The cursor preserves original hidden-column inputs for `seriesColumn()` output while separately tracking the optimized generation range in `iBase`, `iTerm`, `iStep`, `iValue`, `bDesc`, and `bDone`. `seriesBestIndex()` only mutates the transient `sqlite3_index_info` plan object and, on missing required input, `pVTab->zErrMsg`.

The c-pp demo directives also do not write durable state. `demo-div` allocates an `int` counter as directive state through `cmpp_malloc()` and registers `cmpp_mfree` as its destructor. That counter tracks currently open `demo-div` blocks for the registered directive instance. `cmpp_dx_f_divWrapper()` owns a temporary `cmpp_b` buffer for consumed content and always clears it before returning.

Output effects are immediate: the demo callbacks write to the c-pp output stream through `cmpp_dx_outf()` and `cmpp_dx_out_raw()`, and errors are stored in the processor/directive execution context through `cmpp_dx_err_set()` or the broader `cmpp_err_get()` path.

## Dependencies And Integration Points

- SQLite virtual table APIs: `sqlite3_vtab_cursor`, `sqlite3_index_info`, `sqlite3_module`, `sqlite3_declare_vtab()`, `sqlite3_create_module()`, constraint op constants, `sqlite3_value_*()`, `sqlite3_result_int64()`, `sqlite3_malloc()`, `sqlite3_free()`, and `sqlite3_mprintf()`.
- Earlier `generate_series` helpers and types in the same file: `series_cursor`, `span64()`, `add64()`, `sub64()`, `seriesConnect()`, `seriesDisconnect()`, `seriesOpen()`, `seriesClose()`, `seriesNext()`, and `seriesColumn()`.
- Compile-time gates: `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_SERIES_CONSTRAINT_VERIFY`, `ZERO_ARGUMENT_GENERATE_SERIES`, `SQLITE_ENABLE_MATH_FUNCTIONS`, `_WIN32`, `__GNUC__`, `SQLITE_DISABLE_INTRINSIC`, and optional `SQLITE_INDEX_SCAN_HEX`.
- c-pp public/internal APIs: `cmpp`, `cmpp_dx`, `cmpp_d_reg`, `cmpp_arg`, `cmpp_b`, `cmpp_api_init()`, `cmpp_dx_delim()`, `cmpp_tt_cstr()`, `cmpp_dx_err_check()`, `cmpp_dx_outf()`, `cmpp_dx_out_raw()`, `cmpp_dx_consume_b()`, `cmpp_b_chomp()`, `cmpp_b_clear()`, `cmpp_d_register()`, `cmpp_malloc()`, `cmpp_mfree()`, `cmpp_err_get()`, and `CMPP_MODULE_REGISTER1(demo)`.
- Standard C dependencies in the demo region: `stdlib.h`, `assert.h`, and `string.h`.

## Risks And Edge Cases

- `seriesFilter()` relies on the `idxNum` bitmask and argument ordering produced by `seriesBestIndex()`. Any future change to one side must preserve the exact bit meanings and `argv` order.
- Floating-point value constraints are subtle. Equality only returns rows for integral finite values in signed 64-bit range, while `>`/`<` with exact integer floats must move one integer past the bound. The local ceil/floor fallback must continue matching libc behavior for relevant finite values.
- Signed 64-bit overflow is intentionally avoided through unsigned helper operations. Replacing `span64()`, `add64()`, or `sub64()` with ordinary signed arithmetic would risk undefined behavior at `SMALLEST_INT64`/`LARGEST_INT64`.
- `iLimit` and `iOffset` are signed SQLite integers. Negative `OFFSET` has no effect because only `iOffset > 0` is applied; negative `LIMIT` behaves as unlimited because shortening only occurs for `iLimit >= 0`.
- In the `LIMIT` path, `seriesSteps(pCur) > (sqlite3_uint64)iLimit` followed by `(iLimit - 1) * pCur->iStep` assumes the zero-limit case has been handled safely. This is an important boundary for tests because `iLimit == 0` can produce arithmetic that is easy to mishandle.
- The `seriesBestIndex()` check `if( aIdx[3]==0 )` appears intended to ignore `OFFSET` without `LIMIT`, but `aIdx[3]` is initialized to `-1`. That condition only fires if the chosen LIMIT constraint is at index 0, so reviewers should verify whether this is inherited SQLite behavior, a transcription issue, or an actual bug in this combined source.
- `seriesBestIndex()` marks constraints omittable for `i>=3`, so `LIMIT`, `OFFSET`, and value constraints may be enforced by the virtual table instead of the core. Incorrect range math would therefore be directly visible as wrong query results.
- The c-pp `divOpener()` writes argument text directly into a single-quoted HTML class attribute without escaping. This is acceptable for a demonstration directive only if callers treat arguments as trusted class names.
- `cmpp_dx_f_divClose()` reports misuse if a closer appears without a matching opener in the shared directive state, but the state is per registered directive, not per nested parser stack beyond the integer counter.
- `cmpp_dx_f_divWrapper()` depends on `dx->d->closer` being correctly registered. A mismatched closer descriptor would make block consumption stop at the wrong directive or fail to stop.

## Test Signals

- `SELECT value FROM generate_series(1,5,2)` should yield `1,3,5`, and hidden columns should report the original `start`, `stop`, and `step`.
- Descending scans such as `generate_series(5,1,-2)` and ascending `ORDER BY` over a descending input should verify base/term swapping and `bDesc` handling.
- Queries with `WHERE value BETWEEN ...`, `value = ...`, `value > ...`, and `value < ...` should confirm that the first generated value is aligned to the step and that terminal values are snapped to reachable values.
- Floating-bound tests should cover integral floats, non-integral floats, values beyond signed 64-bit range, and strict comparison at exact integers.
- Boundary tests should include `SMALLEST_INT64`, `LARGEST_INT64`, negative `SMALLEST_INT64` step magnitude, zero step normalization to one, empty directionally impossible ranges, NULL constraints, `LIMIT 0`, positive `LIMIT`, positive `OFFSET`, and `OFFSET` without `LIMIT`.
- Planner tests should verify missing-start errors when `ZERO_ARGUMENT_GENERATE_SERIES` is not defined, acceptance of usable rowid/value constraints as a substitute, rejection of unusable hidden-column constraints, and `ORDER BY value ASC/DESC` consumption.
- Extension tests should confirm `sqlite3_series_init()` registers `generate_series` on modern SQLite builds and returns the documented version error for runtimes older than 3.8.12.
- c-pp demo tests should exercise `demo1` argument dumping, `demo-div` open/close balance, misuse of a dangling closer, `demo-div-wrapper` with nested directives, autoload lookup for opener and closer names, and destructor cleanup for allocated directive state.
