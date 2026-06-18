# sources/storage-engines/sqlite/ext/wasm/libcmpp.c lines 1-7335

## Scope

This chunk covers the beginning of SQLite's vendored `ext/wasm/libcmpp.c` amalgamation through the first line of the `cmpp_undef()` implementation. It includes the generated public `libcmpp` header, the module/plugin ABI surface, the private implementation declarations, the main `cmpp_pimpl` state layout, and the first concrete core implementation routines for construction, reset/destruction, output, delimiters, `@token@` expansion, file slurping, SQL binding helpers, and define lookup. Later directive implementations, database initialization, argument parsing internals, CLI processing, module loading, and the rest of define management continue after this chunk.

## Purpose

- Provide the public API for `libcmpp`, a configurable C-like preprocessor for arbitrary UTF-8 text rather than only C source.
- Package both header and implementation into one amalgamated C file for SQLite's WASM extension tree, with WASM-aware elision of `FILE *` APIs through `cmpp_FILE`.
- Define the central `cmpp` object, its opaque private state, directive context model, token and argument types, output/input abstractions, buffer helpers, policy stacks, delimiter stacks, and module ABI.
- Use SQLite as the backing engine for define storage, include-path tracking, savepoints, token metadata, comparison helpers, and path search queries.
- Support extension points: custom directives, directive autoloaders, loadable modules, and a versioned API thunk for modules which cannot rely on global symbol visibility.
- Begin implementing the core runtime: instance allocation/reset, output channel handling, file slurping, delimiter management, `@token@` expansion, flow-control elision levels, and SQLite statement binding/define lookup helpers.

## Important APIs, Types, And Functions

- Version/configuration macros define the amalgamation provenance: package `libcmpp`, version `2.0.x`, hash `c02f3e3e2d3f3573a9a33c1474c2e52fc48e52c70730404a90d0ae51517e7d37`, timestamp `2026-03-08 14:50:35.123 UTC`, default module path, and platform DLL extension.
- `cmpp_rc_e` is the public result-code enum. It distinguishes ordinary success from OOM, misuse, range, I/O, syntax, DB, undefined-key, assertion, help, no-directive, and unsupported-operation results.
- `cmpp_size_t` and `cmpp_ssize_t` are 32-bit by default via `CMPP_BITNESS`, so string/input sizes and offsets are intentionally bounded to 32-bit ranges unless the library is rebuilt incompatibly with 64-bit counters.
- `cmpp_input_f`, `cmpp_output_f`, and `cmpp_flush_f` are the stream callback contracts. `cmpp_outputer` wraps an output callback, flush callback, cleanup callback, stable state pointer, and optional channel name.
- `cmpp_ctor_cfg` configures a new preprocessor with flags such as no-include, no-pipe, no-db, no-module, and safe mode. It can also name a persistent SQLite database file for defines and runtime state.
- `cmpp_ctor()`, `cmpp_reset()`, and `cmpp_dtor()` allocate the object and private state in one block, initialize policy and delimiter stacks lazily, preserve constructor config across resets, and clean up output, SQL statements, DB handles, directives, modules, buffers, policy stacks, delimiters, and recycled argument state.
- `cmpp_mrealloc()`, `cmpp_malloc()`, and `cmpp_mfree()` are explicit wrappers around SQLite allocation APIs. All buffers returned by this library must be freed with the matching wrapper.
- Define APIs include `cmpp_define_legacy()`, `cmpp_define_v2()`, `cmpp_undef()`, `cmpp_define_shadow()`, and `cmpp_define_unshadow()`. In this chunk the public declarations and lookup helpers are present, and the `cmpp_undef()` implementation begins just after the chunk boundary.
- Processing APIs include `cmpp_process_string()`, `cmpp_process_file()`, `cmpp_process_stream()`, and `cmpp_process_argv()`. Their declarations document the main execution model, CLI flags, include/output behavior, `-D/-U/-F/-I`, inline script execution, delimiter and at-policy options, SQL tracing, and define dumping.
- Error APIs include `cmpp_err_get()`, `cmpp_err_set()`, `cmpp_err_set1()`, `cmpp_err_has()`, and `cmpp_dx_err_set()`. Errors are persistent on the `cmpp` object and most APIs become no-ops while an error is set.
- Savepoint APIs `cmpp_sp_begin()`, `cmpp_sp_commit()`, and `cmpp_sp_rollback()` expose DB transaction nesting for directives; internal declarations add `cmpp__dx_sp_*()` wrappers for directive contexts.
- `cmpp_b` is the owned dynamic byte buffer used for captured output and temporary strings. It tracks `z`, bytes in use, allocation size, and a sticky buffer-local error code.
- `cmpp_tt`, `cmpp_arg`, and `cmpp_args` define directive argument tokenization. Tokens include raw lines, words, integers, strings, at-strings, grouping tokens, comparison operators, arrows, arithmetic operators, boolean operators, glob operators, directives, and EOF.
- `cmpp_d`, `cmpp_d_reg`, `cmpp_dx`, and `cmpp_dx_f` define the directive system. Directives have names, flags, optional closers, callback state, and optional finalizers. `cmpp_dx` owns per-input traversal state and exposes current directive arguments to callbacks.
- Directive flags control raw/list parsing, safe-mode disallowance, call-only behavior, no-call behavior, and internal flow-control/argument simplification semantics.
- `cmpp_dx_next()`, `cmpp_dx_process()`, `cmpp_dx_consume()`, `cmpp_dx_consume_b()`, `cmpp_dx_out_raw()`, and `cmpp_dx_out_expand()` form the directive scanning and block-consumption API used by built-in and custom directive callbacks.
- `cmpp_arg_parse()`, `cmpp_arg_to_b()`, `cmpp_call_str()`, `cmpp_kav_each()`, and `cmpp_str_each()` support token parsing, define expansion, bracket-call expansion, and key/value list traversal for directive implementations.
- Policy APIs `cmpp_atpol_*()` and `cmpp_unpol_*()` manage stacks for undefined `@token@` behavior and undefined define behavior. At policies are off, retain, elide, error, or current; undefined policies are null or error.
- Delimiter APIs `cmpp_delimiter_*()` manage the directive delimiter stack, defaulting to `##`; `cmpp_atdelim_*()` manages paired opening/closing delimiters for `@token@`, defaulting to `@...@`.
- `cmpp_popen()`, `cmpp_popenv()`, `cmpp_pclose()`, and `cmpp_popen_args()` declare Unix child-process integration for directives such as pipe. They are unavailable on WASM and non-Unix builds.
- Module APIs `cmpp_module_load()`, `cmpp_module_dir_add()`, `cmpp_module`, and the `CMPP_MODULE_*` macros define loadable module registration, standalone symbols, and optional dynamic-library discovery.
- `cmpp_api_thunk` and `cmpp_api_thunk_map()` expose a versioned table of public functions and exported objects for loadable modules. The chunk includes generated `CMPP_API_THUNK` macros that rewrite `cmpp_*` calls through the thunk in module builds.
- Internal declarations define `CmppDLine`, `CmppSnippet`, `CmppLvl`, list macros, `CmppArgList`, `cmpp_args_pimpl`, `cmpp_dx_pimpl`, `CmppDList`, `CmppSohList`, `CmppKvp`, POD policy stack macros, `cmpp__delim`, and `cmpp_pimpl`.
- `CmppStmt_map()` enumerates cached SQLite statements for define insertion/deletion/lookup, include tracking, include-path search, comparisons, DB attach/detach, savepoints, token type insertion, and a recursive CTE path search.
- Implemented helpers in this chunk include `cmpp_rc_cstr()`, `cmpp_tt_cstr()`, `cmpp_isspace()`, `cmpp_skip_space()`, `cmpp_skip_snl()`, trailing trim variants, `cmpp_fopen()`, `cmpp_fclose()`, `cmpp_slurp()`, `cmpp_chomp()`, output helpers, delimiter helpers, `cmpp__is_int()`, `cmpp__is_int64()`, `cmpp__set_file()`, `cmpp_has()`, `cmpp__get_bool()`, `cmpp__get_int()`, `cmpp__get_b()`, and `cmpp__get()`.

## Control Flow

The public API starts with `cmpp_ctor()`. It allocates enough memory for both `cmpp` and `cmpp_pimpl`, installs the singleton API thunk pointer, initializes the private state from `cmpp_pimpl_empty`, copies constructor flags and optional database filename, initializes policy stacks, and runs lazy initialization. Lazy initialization pushes the default directive delimiter and `@token@` delimiter levels and optionally calls `CMPP_CTOR_INSTANCE_INIT()` for embedding projects that install custom directives at construction time.

Most public APIs first check `ppCode`, the persistent error code stored in `pp->pimpl->err.code`. If it is nonzero, they return that code or become a no-op. This sticky-error style is intentional: clients can chain calls, and a failure prevents follow-on operations from mutating partially invalid state.

`cmpp_reset()` is the heavy recovery path. It flushes and cleans up SQL trace output, destroys directive autoload state, clears module path bytes, unwinds active savepoints when prepared savepoint statements exist, closes output, frees runtime directive registrations, finalizes prepared statements, commits any open write transaction before closing SQLite, closes the DB handle, clears delimiter stacks, clears errors, and then reinitializes `cmpp_pimpl` while preserving the DB filename, recycler pools, policy storage, delimiter storage, module handle list, allocation stamp, constructor flags, and lazy-init marker.

Output flows through `cmpp_outputer` callbacks. `cmpp_outputer_set()` replaces the default channel, `cmpp__out_fopen()` opens a FILE-backed channel, `cmpp__out_close()` flushes and calls cleanup, `cmpp__out2()` writes bytes and records write errors, and `cmpp_dx_out_raw()` suppresses output when the current directive context is in elide mode. Formatted output uses SQLite's `sqlite3_vmprintf()` before writing.

`cmpp__out_expand()` is the key implemented filter in this chunk. It walks a byte range looking for the current at-token opening delimiter. Raw spans before tokens are flushed to the selected output. A `@[directive ...]@` form is treated as an inline call: the bracket content is located with `cmpp__find_closing2()`, processed via `cmpp_call_str()`, and emitted. A normal token extracts the key between opening and closing delimiters, looks up the define with `cmpp__get_b()`, emits the value when found, and otherwise applies the active policy: elide, retain, or error. It borrows temporary buffers from the `cmpp` buffer recycler and returns them before exit.

Delimiter control is stack based. `cmpp_delimiter_push()` appends a delimiter slot, then delegates to `cmpp_delimiter_set()`. On failure, it pops the newly added slot. `cmpp_delimiter_pop()` restores the previous delimiter by cleaning up the top slot. The at-token delimiter APIs do the same, except `cmpp_atdelim_set()` stores opening and closing delimiters in a single owned buffer.

Flow-control elision is represented by `CmppLvl` entries in `cmpp_dx_pimpl::dxLvl`. `CmppLvl_push()` inherits the parent elide bit and records the directive line number. `cmpp_dx_is_eliding()` reads the top level, and output functions use it to suppress text from falsy branches.

Define lookup uses cached SQLite statements. `cmpp_has()` binds a key and checks for a row in `vdef`. `cmpp__get_bool()` reads `cmpp_truthy(v)`, `cmpp__get_int()` casts the selected value to integer, `cmpp__get_b()` appends the value to a `cmpp_b`, and `cmpp__get()` returns a newly allocated copy. Missing entries optionally enforce the undefined-key policy through `cmpp__affirm_undef_policy()`.

File input in this chunk is eager rather than streaming. `cmpp_slurp()` repeatedly calls a `cmpp_input_f`, reallocates a destination buffer, copies all bytes, and NUL-terminates the result. `FileWrapper` builds on that for named files and underlies `cmpp__set_file()`, the implementation helper for `-Fkey=file`, which reads file content, optionally chomps one trailing newline, and inserts the bytes into the define table.

## State And Persistence Behavior

`cmpp_pimpl` is the core mutable state. It owns the SQLite handle and optional database filename, current directive context pointer, output channel, directive and at-token delimiter stacks, cached SQLite statements, sticky error state, SQL trace channel, constructor/runtime flags, policy stacks, runtime directive list and autoloader, module/shared-object state, and recycler pools for buffers and argument pimpls.

Defines, shadow defines, include records, include paths, token metadata, and some lookup/comparison behavior are persisted in SQLite tables or views managed by later database-initialization code. This chunk shows the statement map and the lookup/binding side of that design. If `cmpp_ctor_cfg::dbFile` is non-null, that SQLite state can be backed by a named database file; otherwise the implementation uses an unspecified temporary or in-memory DB once initialized.

Persistent error state gates almost every operation. The code treats most errors as unrecoverable without `cmpp_reset()`, because a mid-processing failure can leave savepoints, directives, or output state imbalanced. Some API docs call specific errors recoverable, but the dominant runtime model is fail-stop until reset.

The output channel is owned or borrowed depending on the `cmpp_outputer` supplied by the caller. `cmpp_outputer_set()` bitwise-copies callback state and later cleanup may close or mutate the copied outputer's `state`, so ownership rules are part of the caller contract.

Delimiter and policy state is stack-based. Push operations allocate or reserve state and require a matching pop on success. `cmpp_reset()` clears active delimiter entries but keeps the underlying delimiter-list storage for reuse, then marks the object for lazy reinitialization.

Module state includes a DLL/shared-object handle list and module search path. This chunk sets up cleanup rules and state but leaves actual module loading to later code. The comments intentionally note that DLLs are normally unsafe to close, but this build defaults `CMPP_CLOSE_DLLS` to true for valgrind-style cleanup.

Buffer and argument recyclers are retained across reset and cleaned only in `cmpp_dtor()`. That improves reuse during repeated processing but means a reset is not a full memory release.

## Dependencies And Integration Points

- SQLite is the central dependency: allocation (`sqlite3_malloc64`, `sqlite3_realloc64`, `sqlite3_free`), formatting (`sqlite3_mprintf`, `sqlite3_vmprintf`, `sqlite3_str`), database handles, prepared statements, bindings, savepoints, transactions, CTE path search, and runtime scalar functions such as `cmpp_truthy`, `cmpp_compare`, and `cmpp_file_exists`.
- Platform I/O integrates with `stdio.h`, `unistd.h`, `sys/wait.h`, or Windows `_access`/I/O headers depending on build macros. WASM builds typedef `cmpp_FILE` to `void` and mark many file/process APIs unavailable or inoperative.
- SQLite's WASM extension tree consumes this file as a vendored amalgamation under `ext/wasm`; the header also points to SQLite's lighter `c-pp-lite.c` as a related deployment.
- Loadable modules integrate through `cmpp_module_init_f`, `cmpp_d_register()`, `CMPP_MODULE_*` registration macros, dynamic-library search path state, and `cmpp_api_thunk`.
- Custom directives integrate through `cmpp_d_register()`, directive flags, `cmpp_dx_f` callbacks, `cmpp_dx` traversal/output/argument APIs, and directive autoloaders.
- The CLI integration is declared through `cmpp_process_argv()` and usage output. This connects public options such as `-D`, `-U`, `-F`, `-I`, `-e`, `--delimiter`, `--@policy`, SQL tracing, and define dumping to the library runtime.
- External process integration is declared through `cmpp_popen*()` and is intended for directives such as pipe. Safe mode and constructor flags can disable unsafe filesystem/process/module behaviors.

## Risks And Edge Cases

- The chunk is an amalgamation. Public header, private declarations, generated thunk macros, and implementation coexist in one file, so symbol visibility and macro state are unusually sensitive to compile-time defines.
- Many APIs become silent no-ops when persistent error state is set. This simplifies call chains but can hide the exact operation that stopped doing work unless callers check `cmpp_err_get()`.
- `cmpp_reset()` is intentionally broad and closes the database, removes custom directives/autoloaders, clears paths, finalizes statements, and resets delimiters. Clients expecting partial recovery must preserve and reinstall custom state.
- Output ownership is easy to misuse because outputers are bitwise copied. A cleanup callback may close a state pointer that the caller still considers live unless the caller follows the documented copy-with-null-cleanup pattern.
- `cmpp_slurp()` reallocates by assigning directly to `pDest`; if `cmpp_mrealloc()` returns NULL, the old pointer is lost and the subsequent `memcpy()` would be unsafe. The code does not check allocation failure inside the loop before copying.
- `cmpp_slurp()` uses `unsigned` counters for allocation and offsets even though the public size type is `cmpp_size_t`; very large inputs can overflow these local counters in 32-bit builds.
- `cmpp_skip_snl_trailing()` tests `*z` while moving backward from a one-past-end pointer, which is suspicious relative to `cmpp_skip_space_trailing()` using `z[-1]`; the comment already calls out CRNL handling as incomplete.
- `cmpp__out_expand()` deliberately does not error on an unterminated at-token at EOF because the error block is compiled out. That can retain or flush partially parsed token text rather than reporting syntax failure.
- The at-token call path around `@[...]@` has subtle pointer math involving delimiter lengths and bracket positions; delimiter lengths greater than one increase the need for tests.
- `cmpp__out_expand()` borrows two buffers and immediately returns on the second borrow failing without returning the first buffer if only the second allocation failed.
- `cmpp__set_file()` appears to bind NULL to column 2 in the empty-file branch after binding the key to column 2 earlier; for `defIns(t,k,v)` this is likely a key/value column mix-up unless later code compensates before the chunk boundary.
- `cmpp__is_int()` and `cmpp__is_int64()` rely on `sscanf()` with width macros and do not prove that the full token is numeric; prefixes may parse as integers if not validated elsewhere.
- Safe mode depends on directive registration and processing honoring `cmpp_d_F_NOT_IN_SAFEMODE`. Client-defined directives must set that flag correctly for filesystem, network, process, and similar effects.
- WASM builds define `cmpp_FILE` as `void`, but the comments admit FILE dependencies are not fully compiled out. Any accidental use of `FILE`-oriented APIs in WASM builds can become unsupported or inoperative.
- `cmpp_dtor()` only frees the outer allocation if `allocStamp` matches the canonical empty pimpl marker. Stack/static or manually embedded instances would need compatible initialization discipline.

## Test Signals

- Constructor/destructor tests should cover default construction, construction with `dbFile`, safe-mode flags, lazy delimiter/policy initialization, repeated `cmpp_reset()`, and final `cmpp_dtor()` cleanup.
- Error-state tests should set an error, verify subsequent APIs no-op, verify `cmpp_reset()` is needed for full recovery, and verify `cmpp_check_oom()` behavior with both NULL and non-NULL `cmpp`.
- Output tests should cover no-op outputers, FILE outputers including `"-"` for stdin/stdout selection, buffer outputers, flush failures, cleanup ownership patterns, formatted output, and elide-mode suppression.
- Slurp/file tests should cover empty input, large input, read errors, allocation failure injection, `cmpp_chomp()` for LF and CRLF, `-Fkey=file` behavior, and empty-file define insertion.
- Delimiter tests should cover default directive delimiter, custom delimiter, too-long delimiter, empty/control-character delimiters, push/pop balance, popping an empty stack, and multi-character at-token open/close pairs.
- At-token expansion tests should cover policies off/retain/elide/error, defined and undefined keys, empty keys, custom delimiters, tokens spanning line boundaries, unterminated tokens, and `@[directive ...]@` call expansion.
- Policy-stack tests should cover push/pop balancing for at policies and undefined-key policies and confirm undefined-key error policy affects `cmpp__get_bool()`, `cmpp__get_int()`, `cmpp__get_b()`, and `cmpp__get()`.
- SQLite-backed define tests should cover define existence, truthiness, integer extraction, NULL/empty values, shadow precedence via `vdef`, glob deletes once `cmpp_undef()` implementation is included, and statement reset after each lookup.
- Flow-control tests should confirm nested `CmppLvl` inheritance, elision toggling, and suppression of raw and expanded output in inactive `#if` branches.
- Module/thunk tests should compile a small directive module with `CMPP_API_THUNK`, verify API version compatibility, register directives through `cmpp_api_init()`, and ensure module path defaults and explicit directory additions behave when module support is enabled or omitted.
- WASM configuration tests should build with WASM macros and verify unsupported FILE/process/module paths report `CMPP_RC_UNSUPPORTED` or no-op consistently without depending on Emscripten POSIX I/O proxies.
