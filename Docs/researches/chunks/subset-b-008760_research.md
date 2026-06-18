# sources/storage-engines/sqlite/ext/wasm/libcmpp.c lines 7336-16047

## Scope

This chunk covers a large middle section of the amalgamated `libcmpp.c` source. It spans public and internal setup helpers, directive tokenization and dispatch, the SQLite-backed define/include database, built-in directive implementations, argument parsing and expression evaluation, process piping, dynamic module loading, and the opening of SQLite's embedded `generate_series` virtual table implementation. The chunk begins in the tail of define/include-path management and ends after the `seriesColumn()` implementation and integer limit macros for `generate_series`; later virtual-table methods continue beyond this range.

## Purpose

The code in this range is the operational core of the `cmpp` preprocessor. It turns an input string/file/stream into output by scanning for directive delimiters at line starts, parsing directive arguments, resolving or lazily registering directive handlers, executing built-in directives, and maintaining define/include/module state in an internal SQLite database. It also exposes utility APIs used by embedders: output/input callbacks, policy getters/setters, savepoint control, CLI argument processing, buffer recycling, SQL query binding, subprocess piping, and dynamic module loading.

## Important APIs, Types, and Functions

- Include/module/db setup:
  - `cmpp__include_dir_add()`, `cmpp_include_dir_add()`, `cmpp__include_dir_rm_id()` maintain rows in the internal `inclpath` table and update `nIncludeDir`.
  - `cmpp_module_dir_add()` appends module search-path entries, normalizing `CMPP_PATH_SEPARATOR` into the configured module path separator when DLL support is enabled.
  - `cmpp_db_name_set()` selects a persistent SQLite database filename before `cmpp__db_init()` opens the database.
  - `cmpp_path_search()` delegates module/file path lookup to a prepared SQLite statement.

- Directive scanning and processing:
  - `cmpp_next_chunk()`, `cmpp__dx_next_line()`, and `cmpp_dx_delim_search()` scan input, track source line numbers, flush non-directive text, identify directive lines, and handle grouped constructs and escaped newlines.
  - `cmpp_dx_next()` normalizes a directive line, resolves the directive with `cmpp__d_search3()`, validates call-only/no-call flags, and parses raw or list arguments according to directive flags.
  - `cmpp_dx_process()` invokes the directive callback unless the current conditional level is eliding and the directive is not flow-control.
  - `cmpp_dx_consume()` and `cmpp_dx_consume_b()` consume nested directive bodies up to configured closers and optionally process intervening directives.

- Directive registration:
  - `cmpp_d_register()` registers opener and optional closer directive entries in a sorted `CmppDList`, checks safe-mode restrictions, validates directive names, and associates callback state/destructors.
  - `cmpp__d_delayed_load()` lazily registers built-in directives such as `if`, `define`, `include`, `query`, `pipe`, `module`, `delimiter`, `@`, `arg`, `join`, `file`, and policy/debug helpers.
  - `CmppDList_*` helpers own directive-entry allocation, cleanup, sorting, and lookup.

- Policy and savepoint APIs:
  - `cmpp_atpol_*` and `cmpp_unpol_*` map string names to policy enums, expose get/set, and support scoped push/pop stacks via generated POD list helpers.
  - `cmpp_sp_begin()`, `cmpp_sp_rollback()`, `cmpp_sp_commit()` wrap SQLite savepoints; `cmpp__dx_sp_*()` mirror them with per-input-source tracking so script-level savepoints are cleaned up during directive context teardown.

- Processing entry points:
  - `cmpp_process_string()`, `cmpp_process_file()`, and `cmpp_process_stream()` initialize the database, set up a `cmpp_dx`, shadow `__FILE__`, manage input-local include path priority, repeatedly call `cmpp_dx_next()`/`cmpp_dx_process()`, and flush output.
  - `cmpp_call_str()` runs a directive in call context, optionally prepends the current directive delimiter, captures output into a buffer, and applies trimming flags.
  - `cmpp_process_argv()` implements the historical CLI driver for `-D`, `-U`, `-I`, `-L`, `-F`, `-e`, `-o`, delimiter/policy/debug/db flags, SQL tracing, and file processing.

- Buffer, output, and stream helpers:
  - `cmpp_b_*` implements an appendable NUL-terminated byte buffer plus a `cmpp`-owned recycler via `cmpp_b_borrow()` and `cmpp_b_return()`.
  - `cmpp_outputer_*`, `cmpp_stream()`, `cmpp_input_f_FILE()`, `cmpp_output_f_FILE()`, `cmpp_input_f_fd()`, and `cmpp_output_f_fd()` form generic I/O adapters.
  - Optional `cmpp__obuf` support wraps buffered output behind a `cmpp_outputer`.

- SQLite database layer:
  - `cmpp__prepare()`, `cmpp__stmt()`, `cmpp__step()`, `cmpp__stmt_reset()`, `cmpp__db_rc()`, and `cmpp__db_errcode()` centralize prepared statement creation, stepping, reset, and error mapping.
  - `cmpp__db_init()` opens `:memory:` or a configured DB file, installs tracing, registers UDFs, creates the schema, initializes SQLite's `series` module, prepares savepoint statements, and performs lazy initialization.
  - `cmpp__define_impl()`, `cmpp__define2()`, `cmpp__define_legacy()`, `cmpp_define_v2()`, `cmpp_define_shadow()`, and `cmpp_define_unshadow()` populate either persistent defines (`def`) or scoped shadow defines (`sdef`).
  - `cmpp__define_from_row()` maps query result columns to defines using SQLite column names and type mapping.

- Built-in directives:
  - `cmpp_dx_f_define()` supports scalar define, grouped `key -> value` define lists, expression/call-derived values, `?` define-if-absent mode, `-append`, heredoc `<<`/`<<<`, and chomp handling.
  - `cmpp_dx_f_undef()`, `cmpp_dx_f_error()`, `cmpp_dx_f_expr()`, `cmpp_dx_f_once()`, `cmpp_dx_f_if()`, `cmpp_dx_f_if_dangler()`, `cmpp_dx_f_pragma()`, `cmpp_dx_f_savepoint()`, `cmpp_dx_f_stderr()`, `cmpp_dx_f_at()`, `cmpp_dx_f_undef_policy()`, and `cmpp_dx_f_delimiter()` implement core preprocessing behavior.
  - Optional unsafe directives include `cmpp_dx_f_include()`, `cmpp_dx_f_pipe()`, `cmpp_dx_f_attach()`, `cmpp_dx_f_detach()`, `cmpp_dx_f_query()`, `cmpp_dx_f_file()`, and `cmpp_dx_f_module()`, guarded by compile-time flags, constructor flags, and safe mode.
  - Utility directives `sum`, `arg`, `join`, and `cmp` expand arguments and emit calculated text.

- Argument parsing and evaluation:
  - `cmpp_args__init()`, `cmpp_args_parse()`, `cmpp_arg_parse()`, `cmpp_args_clone()`, and `cmpp_dx_args_parse()` allocate/reuse parser state and tokenize directive arguments into `cmpp_arg` lists.
  - `cmpp_tt_forWord()` maps symbolic tokens such as `==`, `!=`, `<`, `<=`, `glob`, `not`, `defined`, `->`, `<<`, and `<<<` to token types.
  - `cmpp__args_evalToInt()`, `cmpp__arg_toBool()`, comparison operator helpers, and `cmpp_args__not_simplify()` implement expression evaluation over integers, defines, string truthiness, glob matching, nested groups, calls, and comparison SQL statements.
  - `cmpp_arg_to_b()`, `cmpp__bind_arg()`, `cmpp_kav_each()`, `cmpp_str_each()`, and `cmpp__arg_expand_ats()` convert arguments into output bytes, SQL bind values, or key/value callback inputs.

- External integration:
  - `cmpp_popen()`, `cmpp_popenv()`, `cmpp_popen_args()`, and `cmpp_pclose()` provide Unix process execution used by `#pipe`.
  - DLL helpers `cmpp__dlopen()`, `cmpp__dlsym()`, `cmpp__dlclose()`, `cmpp__module_extract()`, and `cmpp_module_load()` load `cmpp_module` entry points from shared libraries when compiled with DLL support.
  - The chunk begins the embedded `generate_series` virtual table: `series_cursor`, `span64()`, `add64()`, `sub64()`, `seriesConnect()`, `seriesDisconnect()`, `seriesOpen()`, `seriesClose()`, `seriesNext()`, and `seriesColumn()`.

## Control Flow

Input processing starts at `cmpp_process_string()`, which initializes SQLite state, creates a stack-local `cmpp_dx`, shadows `__FILE__`, adds the source directory to the include path with a priority based on nesting depth, then loops over `cmpp_dx_next()` until no directive remains. `cmpp_dx_delim_search()` emits ordinary text as it scans and stops only when the current delimiter is found at beginning-of-line after optional spaces. Once a directive line is identified, `cmpp_dx_next()` normalizes escaped newlines, splits the directive name from the argument text, resolves or lazily registers the directive, and creates either parsed argument lists or a raw-line argument. `cmpp_dx_process()` then calls the directive implementation.

Nested/body directives use `cmpp_dx_consume()`. It repeatedly calls `cmpp_dx_next()` until it sees one of the expected closer directives. Depending on flags, it either rejects intervening directives or processes them. This mechanism is used by heredoc-like `#define`, `#once`, `#if`, `#query`, `#pipe`, delimiter/policy scoped blocks, and dangling-closer diagnostics.

The conditional flow in `cmpp_dx_f_if()` creates a `CmppLvl` stack entry, evaluates the initial expression unless already eliding, and then consumes until `elif`, `else`, or `/if` while toggling the level's elide flag. It deliberately processes nested flow-control directives even in skip mode so nesting stays balanced.

SQL-backed directives follow a separate flow. `#query` clones the directive arguments, resolves SQL and optional bind groups, optionally starts a savepoint, steps rows, defines each result column into the current define view, replays the directive body for each row by restoring `cmpp_dx_pos`, and consumes a `query:no-rows` body if no row matched. `#attach`/`#detach` bind schema/database names into prepared statements.

The CLI driver intentionally walks arguments twice: first for validation/help/version handling and then for execution. This lets flags and files be interleaved, so define/output/include/module state changes affect later file processing in command-line order.

## State and Persistence Behavior

Most preprocessor state is anchored in `cmpp_pimpl`: current error, outputer, directive registry, delimiter and policy stacks, module path/handles, SQLite handles/statements, buffer recyclers, and the active `cmpp_dx`. The input-local `cmpp_dx_pimpl` tracks source span, position/line number, current directive line, parsed args, nested levels, savepoint count, and shadow rows for source-local state.

Defines and include state are persisted in SQLite tables:

- `def` stores ordinary user defines.
- `predef` stores built-ins such as `cmpp::version`.
- `sdef` stores scoped/shadow defines such as per-source `__FILE__`.
- `vdef` merges predefined, scoped, and ordinary defines with ordering that makes predefined and latest scoped values take precedence.
- `incl` tracks files currently being included for recursion detection.
- `inclpath` stores include search paths with priority.
- `modpath` is declared in schema but this chunk primarily uses `pp->pimpl->mod.path` plus `cmpp_path_search()` for module lookup.

`cmpp_db_name_set()` can make the SQLite database file-backed, but `cmpp__db_init()` drops and recreates the cmpp schema for persistent files, so the file is a persistence medium for a run rather than a schema migration target. Savepoints are real SQLite savepoints and are forcibly rolled back during `cmpp_dx_cleanup()` if a directive context exits with active script-local savepoints.

Memory ownership is explicit and mostly local. Directive entries own copied names and optional callback state destructors. `cmpp_b` and `cmpp_args_pimpl` instances are recycled through `cmpp_pimpl->recycler` to reduce allocations. Dynamic module handles may be tracked in `CmppSohList` when closing is enabled; otherwise handles are intentionally left open.

## Dependencies and Integration Points

The chunk depends heavily on SQLite's C API: prepared statements, views, UDF registration, tracing, dynamic SQL strings, `sqlite3_strglob()`, `sqlite3_mprintf()`, virtual table APIs, and the `generate_series` extension initializer. It also uses standard/POSIX APIs including `fopen`/`fread`/`fwrite`, `read`/`write`, `access`, `stat`, `pipe`, `fork`, `dup`, `exec*`, `fdopen`, `waitpid`, signals, and dynamic loader APIs (`dlopen`/`dlsym`/`dlclose` or libltdl).

The public exported surface in this chunk is suitable for embedders: callers can configure policies, process strings/files/streams, register directives, define/undefine keys, set output callbacks, run call-form directives, load modules, inspect/take errors, and manage savepoints. Compile-time flags such as `CMPP_OMIT_D_DB`, `CMPP_OMIT_D_INCLUDE`, `CMPP_OMIT_D_PIPE`, `CMPP_ENABLE_DLLS`, `CMPP_D_MODULE`, `CMPP_MAIN`, and platform macros substantially alter available behavior.

Safe mode is enforced in two places: directive registration rejects `cmpp_d_F_NOT_IN_SAFEMODE` directives, and `cmpp_dx_process()` checks the flag before callback invocation. Unsafe built-ins are also marked or constructor-flag gated. Module loading has its own safe-mode check.

## Risks and Edge Cases

- `cmpp_dx_delim_search()` only recognizes directives at beginning-of-line after optional spaces. Its line-number and flush logic is subtle because it must not prematurely emit indentation before a directive and must handle blank lines, CRLF, escaped newlines, and grouped delimiters.
- `cmpp__find_closing2()` only validates a top-level group. The comment explicitly notes that malformed inner groups may be deferred to argument parsing.
- Many APIs are gated by `ppCode`/`dxppCode`; savepoint rollback and statement preparation sometimes intentionally work during an error state. Misusing that convention can leave statements unprepared or cleanup paths unable to recover.
- `cmpp_b_reserve()` grows by `s->nAlloc + n`, where callers often pass required total size. This overallocates but preserves amortized safety; callers rely on NUL termination after appends.
- `cmpp_b_borrow()` asserts that returned buffers are not written after return. Violations are debug-time only and could cause hard-to-find memory aliasing in release builds.
- Directive list lookup uses binary search only when more than two entries exist, so `CmppDList_sort()` after registration is required. Missing a sort would make delayed directives intermittently unfindable.
- `cmpp_dx_f_cmp()` contains `if( !bL || !!bR ) goto end;`, which appears suspicious because it exits when `bR` is non-NULL rather than when it is NULL. That likely makes `#cmp` a no-op/error-prone path unless masked elsewhere.
- `#query` always rolls back the savepoint it starts when not in `define` mode. This appears intentional so row-defined variables are scoped to each row body, but changes made inside query bodies may also be rolled back depending on directive behavior.
- `#pipe` writes the full captured body to child stdin before reading stdout and the inline comment notes this can deadlock for large bodies.
- `cmpp_pclose()` uses `waitpid(..., WNOHANG)` in a loop that only iterates while `wp > 0`; it may return before a still-running child exits, potentially leaving cleanup behavior dependent on later process reaping.
- Dynamic module search constructs names and loads DLLs from configured paths. Safe mode blocks this, but non-safe builds must consider search-path injection and module lifetime.
- `cmpp__udf_compare()` uses `strncmp()` with the larger byte length of two SQLite text values; this is not a raw `memcmp()` and may read until a NUL within strings. It is adequate for NUL-terminated SQLite text but not a general blob comparator despite accepting text/blob types.
- `cmpp_arg_parse()` does not implement backslash escaping in quoted strings; users must choose the alternate quote character or group syntax for embedded quotes.
- `cmpp_args__not_simplify()` comments that eliminating `not` operators may change coercion behavior from forced boolean conversion to whatever the LHS consumer wants.
- File path handling has explicit TODOs around canonicalization, Windows support, include path normalization, and `getcwd()` behavior. Different spellings of the same include path/file can bypass recursion or uniqueness expectations.
- The `generate_series` virtual table implementation has signed/unsigned integer aliasing helpers (`span64`, `add64`, `sub64`) that rely on reinterpretation through pointer casts; this mirrors upstream SQLite extension style but is sensitive to strict-aliasing/compiler assumptions.

## Test Signals

Useful tests for this chunk should cover:

- Directive delimiter scanning with leading spaces, blank lines, CRLF, escaped newlines, grouped `{}`, `[]`, `()`, and no-directive passthrough output.
- Lazy registration and unknown directive errors, including call-only/no-call directives and safe-mode blocked directives.
- `#define` scalar, grouped `key -> value`, `?`, `-append`, heredoc, chomp, expression, and call-brace forms; `#undef` glob/key removal; `#once` duplicate suppression keyed by `__FILE__` and line number.
- `#if`/`#elif`/`#else`/`#/if` nesting, elided branches containing unknown or delayed directives, and unterminated nested construct diagnostics.
- `@` token policy and delimiter push/pop/set/heredoc behavior, including empty-stack pop errors and call-form introspection.
- Savepoint begin/commit/rollback at both public API and directive level, including cleanup rollback after errors.
- Include path priority for nested files, recursive include detection, raw include streaming, and missing file errors.
- SQL database initialization, persistent DB reset behavior, UDFs (`cmpp_file_exists`, `cmpp_truthy`, `cmpp_compare`), SQL tracing, `#attach`/`#detach`, `#query` bind groups, batch mode, define mode, row body replay, and `query:no-rows`.
- CLI order-dependent processing with interleaved `-D`, `-U`, `-I`, `-L`, `-o`, `-e`, file inputs, policies, and SQL trace flags.
- Argument parser coverage for quote strings, `@"..."`, groups, heredoc tokens, operators, `defined`, `glob`, path-like words, nested expression evaluation, boolean coercion, and key/value iteration.
- `#pipe` with no input, captured body input, `--` command form, `[...]` argv form, chomp flags, direct/path execution, stderr behavior, large-input deadlock risk, and safe-mode blocking.
- Module loading success/failure paths, symbol-name variants, module init errors, missing DLLs, search-path behavior, and safe-mode rejection.
- Embedded `generate_series` queries through the initialized SQLite connection once the rest of the virtual-table implementation is included by the final merge chunk.

## Cross-Chunk Notes

This chunk starts immediately after preceding define/undefine logic and therefore assumes earlier declarations for macros, structs, prepared-statement maps, output helpers, define lookup helpers, delimiter helpers, and low-level SQLite bind helpers. It ends in the middle of the SQLite `generate_series` extension. The final per-file reconciliation should merge this with later chunks to describe the remaining virtual-table methods (`xRowid`, `xEof`, `xFilter`, `xBestIndex`, registration entry point, etc.) and with earlier chunks for constructors, schema statement maps, delimiter stack primitives, and output expansion internals.
