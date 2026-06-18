# subset-b-008746 grouped research

This grouped report covers SQLite miscellaneous extensions under `sources/storage-engines/sqlite/ext/misc`. Each section preserves the source path and is wrapped for reconciliation into the mapped source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/fuzzer.c -->
# sources/storage-engines/sqlite/ext/misc/fuzzer.c

Purpose: implements the `fuzzer` read-only virtual table, a demonstration spelling/search expansion engine that emits strings reachable from an input word by applying weighted rewrite rules. A table is created with `CREATE VIRTUAL TABLE f USING fuzzer(rule_table)`; the rule table is loaded into memory and queries constrain `word MATCH`, `distance`, and optional `ruleset`.

Important APIs/types/functions: `fuzzer_rule` stores a rewrite rule, `fuzzer_stem` stores an active generated basis string, `fuzzer_vtab` owns the rule list, and `fuzzer_cursor` owns the priority queues, seen hash, rowid, limits, and temporary render buffer. Rule loading flows through `fuzzerLoadRules()`, `fuzzerLoadOneRule()`, `fuzzerMergeRules()`, and `fuzzerDequote()`. Virtual table methods include `fuzzerConnect()`, `fuzzerBestIndex()`, `fuzzerFilter()`, `fuzzerNext()`, `fuzzerColumn()`, and `fuzzerDisconnect()`, registered by `sqlite3_fuzzer_init()`.

Control flow: connect validates one rule-table argument, runs `SELECT * FROM db.rule_table`, checks four columns, rejects invalid cost/ruleset/length values, and sorts rules by cost. Filtering initializes a cursor from `word MATCH`, a cost limit, and ruleset. `fuzzerNext()` renders the current lowest-cost stem, creates successor stems, advances rewrite positions/rules with duplicate suppression via `apHash`, and maintains a multi-list priority queue so rows appear in nondecreasing edit cost.

State and persistence: rules are cached in `fuzzer_vtab` for the lifetime of the virtual table connection; edits to the backing rule table are not automatically reflected. Cursor state is transient and includes allocated stems, queues, duplicate hash entries, and output buffer. The virtual table is read-only and persists no data.

Dependencies and integration: depends on SQLite extension and virtual table APIs, `sqlite3_malloc64()`, prepared statements, and planner constraint contracts. It marks the vtab innocuous when available and relies on callers to constrain `distance` or use `LIMIT` because expansion is exponential.

Risks and test signals: high-risk areas are unbounded expansion if planner constraints are absent, memory growth in `nStem`/hash queues, byte-length rather than character-length limits, duplicate suppression correctness, and stale cached rules. Tests should cover malformed rule tables, cost/ruleset bounds, empty insert/delete rules, ruleset filtering, `ORDER BY distance`, duplicate paths with different costs, long input/output rejection, and read-only update failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/ieee754.c -->
# sources/storage-engines/sqlite/ext/misc/ieee754.c

Purpose: registers SQL scalar functions for inspecting and constructing IEEE-754 binary64 values. It exposes exact mantissa/exponent forms, raw big-endian blobs, raw 64-bit integer bit patterns, and one-ULP style incrementing.

Important APIs/types/functions: `ieee754func()` implements both `ieee754(X)` and `ieee754(Y,Z)` plus the `ieee754_mantissa()` and `ieee754_exponent()` variants via `sqlite3_user_data()`. `ieee754func_from_blob()`, `ieee754func_to_blob()`, `ieee754func_from_int()`, `ieee754func_to_int()`, and `ieee754inc()` provide blob/int/quantum helpers. `sqlite3_ieee_init()` registers nine innocuous UTF-8 functions.

Control flow: one-argument calls either decode an 8-byte blob as big-endian binary64 or use SQLite numeric conversion, decompose the sign, exponent, and mantissa, normalize trailing powers of two, and return a formatted `ieee754(m,e)` string or one component. Two-argument calls clamp extreme exponents, normalize mantissa width, assemble exponent and mantissa fields, and return a double. Blob/int helpers copy bytes without numeric conversion where documented.

State and persistence: no persistent state. Static registration metadata stores auxiliary mode integers used by the shared callback.

Dependencies and integration: depends on SQLite scalar function APIs, `memcpy()` for type punning, and binary64 layout assumptions. The extension complements the decimal extension for exact decimal rendering.

Risks and test signals: risks include host assumptions around double size, special handling of negative zero, infinities/NaNs, exponent clipping, and `ieee754_inc()` moving through raw bit patterns rather than numeric order for negative values. Tests should cover zero/negative zero, subnormal/min/max finite values, infinities, blob round trips, int bit-pattern round trips, and mantissa/exponent reconstruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/ieee754.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/memstat.c -->
# sources/storage-engines/sqlite/ext/misc/memstat.c

Purpose: implements the eponymous `sqlite_memstat` virtual table, which exposes SQLite process and connection memory/cache status rows from `sqlite3_status64()`/`sqlite3_status()`, `sqlite3_db_status()`, and optional ZIPVFS file-control counters.

Important APIs/types/functions: `memstat_vtab` stores the database handle; `memstat_cursor` stores schema names, row indexes, and current/highwater values. `aMemstatColumn[]` defines exposed counters and nullability. Virtual table methods are `memstatConnect()`, `memstatOpen()`, `memstatFindSchemas()`, `memstatNext()`, `memstatColumn()`, `memstatBestIndex()`, and cleanup helpers. `sqlite3MemstatVtabInit()` and `sqlite3_memstat_init()` register the module.

Control flow: connect declares `CREATE TABLE x(name,schema,value,hiwtr)`. Filtering snapshots schema names from `PRAGMA database_list`, then `memstatNext()` walks each metric and, for schema-specific rows, each schema. It calls the appropriate status API, skips ZIPVFS rows whose file-control call fails, and exposes nulls based on the metric bitmask.

State and persistence: vtab state is only the database handle. Cursor state owns copied schema-name strings and current metric values. The extension reads live SQLite counters and persists nothing.

Dependencies and integration: requires virtual table support. Compile-time guards alter availability under `SQLITE_CORE`, `SQLITE_ENABLE_MEMSTATVTAB`, `SQLITE_OMIT_VIRTUALTABLE`, SQLite version constants, and `SQLITE_ENABLE_ZIPVFS`.

Risks and test signals: risks include schema-list allocation cleanup, metric availability across SQLite versions, and row skipping for file-control failures. Tests should load the extension, query all rows, attach databases, verify schema columns and highwater nullability, exercise builds with older status APIs or omitted virtual tables, and confirm no writes are possible.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/memstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/memtrace.c -->
# sources/storage-engines/sqlite/ext/misc/memtrace.c

Purpose: provides a process-global tracing allocator shim used by the SQLite shell `--memtrace` path. It logs malloc/free/realloc activity while delegating all operations to the original `sqlite3_mem_methods`.

Important APIs/types/functions: globals `memtraceBase` and `memtraceOut` hold the saved allocator and output stream. Wrapper methods `memtraceMalloc()`, `memtraceFree()`, `memtraceRealloc()`, `memtraceSize()`, `memtraceRoundup()`, `memtraceInit()`, and `memtraceShutdown()` populate `ersaztMethods`. Public entry points are `sqlite3MemTraceActivate(FILE*)` and `sqlite3MemTraceDeactivate()`.

Control flow: activation retrieves the current allocator with `SQLITE_CONFIG_GETMALLOC`, installs the wrapper with `SQLITE_CONFIG_MALLOC`, and records the output stream. Each allocation call logs a `MEMTRACE:` line when the stream is non-null, then calls the saved implementation. Deactivation restores the saved methods and clears global state.

State and persistence: state is global to the process and not tied to a database connection. It persists until explicitly deactivated or process exit and writes only diagnostic output.

Dependencies and integration: must be compiled into the application and normally activated before `sqlite3_initialize()`, because SQLite memory methods are configured through `sqlite3_config()`. It depends on `<stdio.h>` and SQLite core configuration APIs rather than loadable-extension registration.

Risks and test signals: risks include calling activation after SQLite initialization, unsynchronized global `FILE *` changes in multithreaded applications, recursion if output allocation flows back into SQLite, and losing the original methods if activation/deactivation ordering is wrong. Tests should verify pre-initialization activation, restore behavior, null stream behavior, realloc edge cases, and logging sizes matching `xRoundup()`/`xSize()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/memtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/mmapwarm.c -->
# sources/storage-engines/sqlite/ext/misc/mmapwarm.c

Purpose: implements `sqlite3_mmap_warm(sqlite3 *db, const char *zDb)`, a C helper that warms the OS page cache for a memory-mapped SQLite database by touching mapped pages through the VFS `xFetch()` interface.

Important APIs/types/functions: the only exported function is `sqlite3_mmap_warm()`. It uses `sqlite3_get_autocommit()`, generated `BEGIN; SELECT * FROM schema.sqlite_schema`, `PRAGMA page_size`, `SQLITE_FCNTL_FILE_POINTER`, `sqlite3_file`, `sqlite3_io_methods.xFetch/xUnfetch`, and `sqlite3_log()`.

Control flow: the function rejects calls inside an open transaction with `SQLITE_MISUSE`, starts a read transaction on the selected schema, retrieves page size, obtains the underlying file pointer, and if the VFS supports version 3 methods, walks page offsets from page 1, fetching each page-sized mapping, touching first/last bytes, unfetching, and stopping on error or null mapping. It then ends the transaction.

State and persistence: no database content is changed. It temporarily opens a read transaction and affects OS cache residency. The dummy `nTotal` accumulation prevents compilers from discarding memory touches.

Dependencies and integration: this is a library helper using SQLite C APIs and VFS mmap support; it is not a SQL function. Its effect depends on mmap configuration, VFS support, and sufficient OS memory.

Risks and test signals: risks include leaving a transaction open if an earlier stage fails before `END`, SQL quoting mistakes for attached database names, partial warming when mappings do not cover the whole file, and VFS-specific `xFetch` behavior. Tests should cover main and attached schemas, calls inside a transaction, non-mmap databases, page-size retrieval failure, and VFS implementations with and without `iVersion>=3`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/mmapwarm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/nextchar.c -->
# sources/storage-engines/sqlite/ext/misc/nextchar.c

Purpose: registers `next_char(prefix, table, column[, where[, coll]])`, a helper for autocomplete/keypad UIs that returns the set of distinct next UTF-8 characters found after a prefix in an indexed vocabulary column.

Important APIs/types/functions: `nextCharContext` holds the database handle, prepared statement, prefix, dynamic result array, and error flags. `writeUtf8()` and `readUtf8()` encode/decode code points, `nextCharAppend()` deduplicates characters, `findNextChars()` iteratively queries the next candidate, and `nextCharFunc()` builds SQL and returns the final string. `sqlite3_nextchar_init()` registers 3-, 4-, and 5-argument variants as innocuous functions.

Control flow: the function builds dynamic SQL over the supplied table expression and column name, constraining the column between `prefix || prior_char_plus_one` and `prefix || char(0x10ffff)`, applying optional where and collation clauses, ordering by the target column, and fetching one row per distinct next character. Each iteration binds the prefix and lower-bound suffix, extracts the next code point after the prefix, appends it if new, resets, and continues until no row is found.

State and persistence: all state is per invocation: prepared statement, result array, and temporary SQL strings. It performs no writes.

Dependencies and integration: depends on SQLite dynamic SQL, caller-provided table/column syntax, collation names, and the vocabulary column's index for performance.

Risks and test signals: table, field, and where parameters are inserted into SQL intentionally, so this is powerful and not safe for untrusted identifiers/expressions. UTF-8 handling assumes valid-ish input and returns replacement characters for malformed encodings. Tests should cover quoted identifiers, subquery table inputs, optional where and collation, multibyte characters, duplicate next chars, empty prefix, missing indexes, malformed SQL, and allocation failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/nextchar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/noop.c -->
# sources/storage-engines/sqlite/ext/misc/noop.c

Purpose: registers pass-through scalar functions used to test SQLite function flags, value typing, and planner/security behavior.

Important APIs/types/functions: `noopfunc()` returns its single argument unchanged. `multitypeTextFunc()` forces text materialization with `sqlite3_value_text()` and then returns the original value so numeric values retain numeric representations alongside text. `sqlite3_noop_init()` registers `noop`, `noop_i`, `noop_do`, `noop_nd`, and `multitype_text`.

Control flow: each SQL call asserts one argument and returns the input value via `sqlite3_result_value()`. Registration assigns distinct flags: deterministic only, deterministic+innocuous, deterministic+directonly, no deterministic flag, and the multitype helper.

State and persistence: no state or persistence.

Dependencies and integration: depends only on SQLite extension scalar function APIs. It integrates mainly with tests for `SQLITE_DETERMINISTIC`, `SQLITE_INNOCUOUS`, `SQLITE_DIRECTONLY`, expression indexes, trusted schema behavior, and subtype/multitype handling.

Risks and test signals: risks are minimal, but behavioral expectations depend on SQLite's function flag semantics. Tests should verify exact value preservation for null/blob/text/numeric values, deterministic planner acceptance, direct-only rejection in schema contexts, innocuous allowance under restricted settings, and `multitype_text()` interactions with `typeof()`, numeric comparisons, and text conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/noop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/normalize.c -->
# sources/storage-engines/sqlite/ext/misc/normalize.c

Purpose: implements `sqlite3_normalize(const char *zSql)`, a standalone SQL normalizer that strips sensitive literal values and canonicalizes SQL text for structural comparison. When compiled with `SQLITE_NORMALIZE_CLI`, it also provides a command-line normalizer.

Important APIs/types/functions: tokenizer tables `aiClass`, `sqlite3UpperToLower`, and `sqlite3CtypeMap` mirror SQLite tokenizer logic. `sqlite3GetToken()` classifies SQL tokens. `sqlite3_normalize()` performs token rewriting and an `IN(...)` post-pass. Optional CLI helpers `normalizeFile()` and `main()` split complete statements with `sqlite3_complete()`.

Control flow: the first pass tokenizes the input, drops whitespace/comments, replaces string/blob/numeric/variable literals and most `NULL` constants with `?`, lowercases identifiers/keywords, and inserts required spacing between adjacent identifier characters. It ensures a trailing semicolon. The second pass rewrites non-subquery `in(...)` lists to `in(?,?,?)` regardless of original list length.

State and persistence: returns a newly allocated normalized string owned by the caller and allocated with `sqlite3_malloc64()`. The CLI reads files into memory and prints normalized statements; no persistent database state is touched.

Dependencies and integration: depends on public `sqlite3.h` allocation and completion APIs. It intentionally copies tokenizer code, so integration risk is drift from SQLite core tokenization.

Risks and test signals: risks include tokenizer drift, simplistic `IN` rewriting based on string search, ASCII-only lowercasing, invalid SQL returning null, and privacy gaps if a literal form is missed. Tests should cover comments, quoted identifiers, strings/blobs, numeric variants, variables, `IS NULL`/`NOT NULL`, nested `IN` lists, `IN (SELECT...)`, malformed tokens, non-ASCII identifiers, and CLI multi-statement splitting.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/normalize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/pcachetrace.c -->
# sources/storage-engines/sqlite/ext/misc/pcachetrace.c

Purpose: provides a process-global tracing shim for SQLite's pluggable page-cache API, used by the shell `--pcachetrace` option to log page-cache operations while delegating to the original `sqlite3_pcache_methods2`.

Important APIs/types/functions: globals `pcacheBase` and `pcachetraceOut` store original methods and output stream. Wrappers cover `xInit`, `xShutdown`, `xCreate`, `xCachesize`, `xPagecount`, `xFetch`, `xUnpin`, `xRekey`, `xTruncate`, `xDestroy`, and `xShrink`. `sqlite3PcacheTraceActivate(FILE*)` and `sqlite3PcacheTraceDeactivate()` install/restore `ersaztPcacheMethods`.

Control flow: activation gets current page-cache methods with `SQLITE_CONFIG_GETPCACHE2`, installs wrappers with `SQLITE_CONFIG_PCACHE2`, and stores the log stream. Every page-cache method logs a `PCACHETRACE:` line before and, for returning methods, after delegating. Deactivation restores the saved methods and zeroes the base table.

State and persistence: global process state only; no database content changes. Diagnostic lines are written to the selected `FILE *`.

Dependencies and integration: must be compiled into the process and configured before SQLite initialization. It depends on SQLite global configuration APIs and the page-cache v2 method table.

Risks and test signals: risks mirror other global config shims: activation after initialization can fail, global logging is not connection-scoped, and repeated activation/deactivation must preserve the original methods. Tests should exercise pre-init activation, fetch/unpin/rekey/truncate traces during normal database access, null stream behavior, deactivation restore, and multi-cache lifecycle calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/pcachetrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/percentile.c -->
# sources/storage-engines/sqlite/ext/misc/percentile.c

Purpose: implements `median()`, `percentile()`, `percentile_cont()`, and `percentile_disc()` as SQLite aggregate/window functions. They compute continuous or discrete percentile values over numeric inputs.

Important APIs/types/functions: `Percentile` is the aggregate/window context storing all numeric inputs, sorted-state flags, and the fraction. `PercentileFunc` describes each SQL function. Core callbacks are `percentStep()`, `percentInverse()`, `percentValue()`, `percentFinal()`, `percentCompute()`, `percentSort()`, and `percentBinarySearch()`. `sqlite3_percentile_init()` registers each with `sqlite3_create_window_function()`.

Control flow: each step validates the fraction argument, enforces that it remains effectively constant per group, rejects nonnumeric and infinite Y values, ignores null Y values, and appends or sorted-inserts the numeric Y. Final aggregate evaluation sorts the array if needed and interpolates at `rPct*(nUsed-1)` unless discrete mode selects the lower input. Window inverse removes values from the sorted array and later steps keep it sorted.

State and persistence: all non-null inputs are retained in aggregate/window memory until finalization. No persistent database state is written.

Dependencies and integration: depends on SQLite aggregate/window APIs, aggregate context allocation, and `SQLITE_SELFORDER1` registration. It can compile as a loadable extension, static extension, or against already included `sqlite3.h`.

Risks and test signals: memory is O(N), aggregate sort is O(N log N), and window maintenance is O(N*K). Edge cases include fraction consistency tolerance, infinities, duplicate values in inverse removal, empty groups, discrete vs continuous semantics, and size validation. Tests should cover all function variants, ordered-set builds, window frames with sliding inverse, nulls, invalid fractions/types, large groups, duplicate values, and percentile endpoints 0/100 or 0/1.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/percentile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/prefixes.c -->
# sources/storage-engines/sqlite/ext/misc/prefixes.c

Purpose: implements the eponymous `prefixes()` table-valued function and `prefix_length()` scalar helper. `prefixes('abcdef')` emits all byte prefixes from longest to empty, while `prefix_length(a,b)` returns the shared UTF-8 character prefix length.

Important APIs/types/functions: `prefixes_vtab` is stateless; `prefixes_cursor` stores rowid, copied input string, and byte length. Virtual table methods include `prefixesConnect()`, `prefixesBestIndex()`, `prefixesFilter()`, `prefixesColumn()`, and cleanup. `prefixLengthFunc()` implements the scalar function. `sqlite3_prefixes_init()` registers both.

Control flow: best-index requires or strongly prefers an equality constraint on hidden `original_string`; otherwise it assigns huge cost. Filtering copies the input string and starts rowid at zero. Each row returns `zStr` with length `nStr-rowid`, so output is longest-to-shortest. EOF occurs after `rowid > nStr`.

State and persistence: per-cursor copied input is transient. The module persists nothing.

Dependencies and integration: depends on SQLite eponymous virtual table support, hidden-column constraints, and UTF-8 byte conventions. The vtab is marked innocuous.

Risks and test signals: `prefixes()` truncates by bytes, so multibyte UTF-8 strings can yield invalid intermediate prefixes; `prefix_length()` counts characters but assumes well-formed UTF-8 and has a possible `-1` behavior for malformed continuation mismatches. Tests should cover constrained and unconstrained plans, empty/null input, multibyte strings, malformed UTF-8, rowid ordering, hidden original column output, and `prefix_length()` symmetry.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/prefixes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/qpvtab.c -->
# sources/storage-engines/sqlite/ext/misc/qpvtab.c

Purpose: implements `qpvtab`, a testing/debugging virtual table that exposes what SQLite passed to and accepted from a virtual table `xBestIndex()` call.

Important APIs/types/functions: `qpvtab_cursor` stores row offset into generated CSV-like diagnostic text and flags. `azColname[]` maps columns. `qpvtabBestIndex()` builds the diagnostic `idxStr`, uses `sqlite3_vtab_rhs_value()`, sets constraint usage, `omit`, `orderByConsumed`, and flags. `qpvtabColumn()` parses diagnostic rows for `vn`, `ix`, `cn`, `op`, `ux`, and `rhs`, and emits synthetic `a` through `e` column values.

Control flow: during planning, `xBestIndex` records all constraints, RHS values when available, order-by terms, `sqlite3_vtab_distinct()`, `idxFlags`, `colUsed`, final `idxNum`, and `orderByConsumed`. Constraints on `a` through `e` are assigned argv indexes and often omitted. A usable integer RHS on hidden `flags` controls integer output for `a`-`e`, order consumption, and LIMIT/OFFSET omission. Filtering receives `idxNum` and `idxStr` and scans one newline-delimited diagnostic row at a time.

State and persistence: diagnostic text is allocated by SQLite as `idxStr` and freed because `needToFreeIdxStr` is set. Cursor state is read-only and transient.

Dependencies and integration: depends on virtual table APIs added for planner inspection, especially `sqlite3_vtab_rhs_value()` and `sqlite3_vtab_distinct()`. It is for tests, not production data access.

Risks and test signals: risks include CSV-like parsing if RHS text contains commas/newlines, version-dependent constraint opcodes, and accidental planner behavior changes. Tests should assert reported constraints for equality/range/blob/text/null RHS values, LIMIT/OFFSET flags, order-by consumption, `colUsed`, rowid constraints, and flag-controlled `a`-`e` typing.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/qpvtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/randomjson.c -->
# sources/storage-engines/sqlite/ext/misc/randomjson.c

Purpose: registers deterministic test functions `random_json(seed)` and `random_json5(seed)` that generate pseudo-random JSON or JSON5 text from a numeric seed.

Important APIs/types/functions: `Prng` stores two 32-bit generator states, `prngSeed()` and `prngInt()` produce deterministic pseudo-random values, `azJsonAtoms[]` and `azJsonTemplate[]` provide JSON/JSON5 fragments, `jsonExpand()` recursively substitutes `%` placeholders, and `randJsonFunc()` performs several expansion passes. `sqlite3_randomjson_init()` registers both functions.

Control flow: each call seeds the PRNG, expands an initial `%` into nested templates with high growth probability, expands again, then runs a low-growth and no-growth pass to eliminate placeholders. Template markers `XX` and `DD` are replaced by generated hex/digit pairs. Output is capped by fixed 10 KB buffers.

State and persistence: no persistent state. Output is deterministic for a seed and type because all PRNG state is local.

Dependencies and integration: depends on SQLite scalar functions and is intended to feed JSON/JSON5 parser tests. It can be built as a loadable or static extension.

Risks and test signals: generated JSON is deliberately broad, including infinities/NaN for JSON5 and large exponent values for JSON. Risks are buffer truncation changing syntactic validity, insufficient coverage if templates drift, and deterministic sequence changes breaking tests. Test signals include stable output per seed, valid `json_valid()`/JSON5 acceptance where expected, buffer cap behavior, placeholder exhaustion, and diverse string/number/object/array atoms.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/randomjson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/regexp.c -->
# sources/storage-engines/sqlite/ext/misc/regexp.c

Purpose: implements a compact POSIX-extended-style UTF-8 regular expression engine and registers `regexp(pattern,string)` plus case-insensitive `regexpi()`. Registering `regexp()` also powers SQLite's `X REGEXP Y` operator.

Important APIs/types/functions: `ReCompiled` stores NFA opcode arrays, parser input, complexity limit, and an initial literal prefix optimization. `ReStateSet` and `ReInput` support matching. Compilation uses `re_compile()`, `re_subcompile_re()`, `re_subcompile_string()`, `re_append()`, `re_insert()`, `re_copy()`, and `re_esc_char()`. Matching uses `re_match()` and opcode constants such as `RE_OP_MATCH`, `RE_OP_FORK`, `RE_OP_ANYSTAR`, and character-class opcodes. `re_sql_func()` caches compiled patterns with auxdata.

Control flow: compilation optionally prepends `.*` for unanchored patterns, parses alternation, grouping, quantifiers, ranges/classes, escapes, and anchors into NFA opcodes, rejects unsupported/invalid syntax, and appends accept. Matching walks UTF-8 input one code point at a time, maintaining current and next active NFA state sets, resolving epsilon transitions, classes, boundaries, and accept states. SQL calls enforce `SQLITE_LIMIT_LIKE_PATTERN_LENGTH` and derive an NFA-size cap from it.

State and persistence: compiled regexes are cached per SQL expression via `sqlite3_set_auxdata()` and freed by `re_free_voidptr()`. Otherwise state is transient and no database data is written.

Dependencies and integration: depends on SQLite extension APIs, SQLite limits, and UTF-8 decoding. `SQLITE_DEBUG` builds can register `regexp_bytecode()` for diagnostics.

Risks and test signals: complexity is bounded O(N*M), but `{m,n}` expands patterns and memory grows with NFA size. Risks include parser edge cases, Unicode decoding/replacement behavior, word-boundary ASCII semantics, case-insensitive ASCII-only folding, prefix optimization correctness, and auxdata lifetime. Tests should cover supported operators, malformed patterns, pattern limits, null inputs, REGEXP operator argument order, UTF-8 classes, `regexpi()`, and debug bytecode when enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/regexp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/remember.c -->
# sources/storage-engines/sqlite/ext/misc/remember.c

Purpose: registers `remember(value, ptr)`, a demonstration scalar function that returns an integer value while also storing it through a C pointer supplied as a SQLite pointer value of type `"carray"`.

Important APIs/types/functions: `rememberFunc()` reads `argv[0]` as `sqlite3_int64`, obtains `sqlite3_value_pointer(argv[1], "carray")`, writes through it if non-null, and returns the integer. `sqlite3_remember_init()` registers the two-argument function.

Control flow: each call is a simple pass-through plus side effect. It does not error if the pointer is absent or the type tag does not match; it just returns the integer value.

State and persistence: the only state change is outside SQLite, at the caller-owned memory address. No database content is written by the function itself, though it is intended to be used inside SQL statements such as updates.

Dependencies and integration: depends on `sqlite3_bind_pointer()`/`sqlite3_value_pointer()` conventions and intentionally shares the `"carray"` pointer type with the carray extension.

Risks and test signals: the function is unsafe if untrusted SQL can receive arbitrary pointer bindings; pointer lifetime, alignment, and type correctness are the caller's responsibility. Tests should bind a valid `sqlite3_int64 *`, verify atomic read-and-store behavior in an update, verify null/wrong pointer tags do not write, and ensure integer conversion behavior matches SQLite rules.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/remember.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/rot13.c -->
# sources/storage-engines/sqlite/ext/misc/rot13.c

Purpose: registers a deterministic innocuous `rot13()` SQL function and a `rot13` collation for testing transformed text comparison.

Important APIs/types/functions: `rot13()` maps ASCII A-Z/a-z by 13 positions and leaves all other bytes untouched. `rot13func()` transforms one SQL text argument, using a stack buffer for short strings and heap allocation for longer ones. `rot13CollFunc()` compares two strings after applying `rot13()` byte-by-byte. `sqlite3_rot_init()` registers function and collation.

Control flow: null input returns null. Non-null input is materialized as UTF-8 text, transformed bytewise, returned as transient text, and any heap buffer is freed. Collation applies the same byte transform during comparison and falls back to length difference.

State and persistence: no persistent state.

Dependencies and integration: depends on SQLite scalar and collation registration. The transform is byte/ASCII oriented and not Unicode case aware.

Risks and test signals: risks include text conversion of blobs/numbers before transformation, collation behavior with embedded nul or non-ASCII bytes, and stack/heap boundary behavior. Tests should verify `rot13(rot13(x)) = x`, null handling, mixed-case ASCII, non-ASCII preservation, long inputs, collation ordering equivalence to comparing transformed strings, and deterministic/innocuous function use.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/rot13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/series.c -->
# sources/storage-engines/sqlite/ext/misc/series.c

Purpose: implements the eponymous `generate_series` virtual table compatible with PostgreSQL-style integer series over signed 64-bit values, with hidden `start`, `stop`, and `step` columns and rowid equal to `value`.

Important APIs/types/functions: `series_cursor` stores original hidden-column inputs and the adjusted generation range. Overflow-safe helpers `span64()`, `add64()`, and `sub64()` manipulate signed boundaries through unsigned arithmetic. Virtual table methods include `seriesConnect()`, `seriesBestIndex()`, `seriesFilter()`, `seriesNext()`, `seriesColumn()`, and `seriesRowid()`. `seriesSteps()` computes range length, and portable `seriesCeil()`/`seriesFloor()` support float constraints. `sqlite3_series_init()` registers the module.

Control flow: `xBestIndex` finds equality constraints on hidden inputs, value/rowid equality and inequalities, LIMIT/OFFSET, and order-by on `value`, encoding them into `idxNum` bits and argv ordering. `xFilter` reads arguments, rejects null constraints, applies defaults, derives actual base/term/step, intersects value constraints, aligns endpoints to the step, reverses output if order-by can be consumed, applies offset/limit, and positions the first row. `xNext` advances until the exact terminal value is reached.

State and persistence: all state is per cursor. The virtual table persists nothing and is read-only.

Dependencies and integration: depends on virtual table support and SQLite 3.8.12 or later. Compile-time options affect zero-argument behavior, math helpers, constraint verification, and scan flags.

Risks and test signals: high-risk areas are 64-bit edge cases, `SMALLEST_INT64`, huge unsigned step values, float constraint rounding, LIMIT/OFFSET order, planner errors for missing `start`, and order-by reversal. Tests should cover positive/negative steps, zero step normalization, missing arguments, value-only constraints, rowid constraints, boundary extremes, null constraints, LIMIT/OFFSET, ascending/descending order consumption, and join planning costs.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/series.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/sha1.c -->
# sources/storage-engines/sqlite/ext/misc/sha1.c

Purpose: registers SHA-1 hashing helpers: `sha1(X)` for lowercase hex text, `sha1b(X)` for the 20-byte digest blob, and `sha1_query(SQL)` for hashing the text and result rows of read-only SQL statements.

Important APIs/types/functions: `SHA1Context` stores state, bit count, and block buffer. Hash engine routines are `SHA1Transform()`, `hash_init()`, `hash_step()`, `hash_step_vformat()`, and `hash_finish()`. SQL callbacks are `sha1Func()` and `sha1QueryFunc()`. `sqlite3_sha_init()` registers the functions, marking direct query hashing as `SQLITE_DIRECTONLY`.

Control flow: `sha1Func()` hashes blob bytes as-is and all other non-null values as UTF-8 text, then returns binary or hex depending on user data. `sha1QueryFunc()` prepares each statement in the input SQL string, rejects non-read-only statements, hashes an `S<n>:` prefix plus original SQL text, then for each row hashes row and type-tagged column encodings for null, integer, float, text, and blob values.

State and persistence: hash state is local to each function call. `sha1_query()` executes read-only SQL but writes no database data.

Dependencies and integration: depends on SQLite scalar APIs, statement preparation/stepping, readonly detection, and endian-independent digest rendering. SHA-1 is cryptographically obsolete but useful for deterministic testing.

Risks and test signals: risks include running arbitrary read-only SQL from a direct-only function, precise type encoding compatibility, endian conversions for integer/float values, and older compiler warnings around transform overreads. Tests should use known SHA-1 vectors, blob vs text distinction, null behavior, binary digest length, multi-statement query hashing, non-query rejection, statement error propagation, and stable result hashing across column types.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/sha1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/shathree.c -->
# sources/storage-engines/sqlite/ext/misc/shathree.c

Purpose: registers SHA-3 helpers: `sha3(X[,size])`, `sha3_agg(Y[,size])`, and `sha3_query(SQL[,size])` for 224-, 256-, 384-, and 512-bit SHA-3 digests.

Important APIs/types/functions: `SHA3Context` stores the Keccak state, rate, loaded byte count, endian mask, and digest size. `KeccakF1600Step()` performs the permutation. `SHA3Init()`, `SHA3Update()`, and `SHA3Final()` implement hashing. SQL callbacks are `sha3Func()`, `sha3AggStep()`, `sha3AggFinal()`, `sha3QueryFunc()`, and `sha3UpdateFromValue()`. `sqlite3_shathree_init()` registers scalar, aggregate, and direct-only query functions.

Control flow: scalar hashing validates size, hashes blob input as bytes or other non-null values as UTF-8 text, finalizes with SHA-3 padding, and returns a digest blob. Aggregate hashing initializes once, then hashes every input including nulls using type-tagged encodings. Query hashing prepares read-only statements, hashes SQL text segments, then row and type-tagged column values using the same encoding.

State and persistence: scalar/query state is local; aggregate state lives in SQLite aggregate context. No database writes occur, though `sha3_query()` evaluates read-only SQL.

Dependencies and integration: depends on SQLite function and aggregate APIs, endian handling, and FIPS 202 SHA-3 constants. Query functions are direct-only to reduce schema-triggered execution risk.

Risks and test signals: risks include invalid size handling differences between scalar/query and aggregate defaulting, ordered aggregate determinism requiring explicit `ORDER BY`, endian-sensitive optimized input path, and arbitrary read-only SQL execution. Tests should include NIST vectors, all sizes, blob/text equivalences documented in comments, aggregate null/type encodings, ordered aggregation, query non-write enforcement, and big/little-endian portability.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/shathree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/showauth.c -->
# sources/storage-engines/sqlite/ext/misc/showauth.c

Purpose: installs a debugging authorizer callback that prints every SQLite authorization request to standard output and allows it by returning `SQLITE_OK`.

Important APIs/types/functions: `authCallback()` maps known authorizer operation codes to readable names, normalizes null string arguments to `"NULL"`, prints `AUTH: op,z1,z2,z3,z4`, and returns OK. `sqlite3_showauth_init()` registers it with `sqlite3_set_authorizer()`.

Control flow: loading the extension replaces the connection's current authorizer with `authCallback`. During statement preparation/execution, SQLite invokes the callback for operations such as reads, writes, DDL, functions, transactions, recursive operations, and pragma access; this extension only logs and permits.

State and persistence: authorizer registration is connection-local and persists until replaced or cleared. It writes diagnostics to stdout and changes no database content by itself.

Dependencies and integration: depends on SQLite extension initialization, authorizer APIs, and stdio. It is intended for shell/debug tracing.

Risks and test signals: risks include overwriting an existing security authorizer, stdout side effects, incomplete opcode-name coverage for newer SQLite constants, and thread interleaving of output. Tests should load the extension, prepare representative SELECT/DDL/DML/pragma/function statements, verify logged op names and null argument formatting, confirm all actions still succeed, and confirm replacing/clearing the authorizer restores prior behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/showauth.c -->
