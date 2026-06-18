# Research: subset-b-008814

## sources/storage-engines/sqlite/tool/lemon.c

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/lemon.c -->
# sources/storage-engines/sqlite/tool/lemon.c

## Purpose
`lemon.c` is SQLite's bundled Lemon LALR(1) parser generator. It reads a Lemon grammar file, optionally preprocesses `%ifdef`/`%ifndef` regions, builds grammar symbols/rules/states/follow sets/actions, resolves conflicts, compresses and renumbers parser tables, then emits generated parser C, token headers, reports, and optionally an SQL description of grammar tables. It is a single-file amalgamation of Lemon modules (`action`, `acttab`, `build`, `configlist`, `main`, `option`, `parse`, `plink`, `report`, `set`, and generated table helpers).

## Important APIs, Types, and Functions
- Core model types: `struct lemon` holds whole-generator state and output options; `struct symbol` represents terminals, nonterminals, and multiterminals; `struct rule` represents productions and reduce code; `struct config` represents LR configurations and follow sets; `struct state` represents generated automaton states; `struct action` represents shift/reduce/accept/error actions.
- Memory and utility layer: `lemon_malloc`, `lemon_calloc`, `lemon_realloc`, `lemon_free`, and `lemon_free_all` track allocations in `memChunkList`; `lemon_sprintf`/`lemon_vsprintf` implement a narrow formatter used by generated paths and diagnostics.
- Build pipeline: `FindRulePrecedences`, `FindFirstSets`, `FindStates`, `FindLinks`, `FindFollowSets`, and `FindActions` implement parser construction.
- State/config helpers: `Configlist_add`, `Configlist_addbasis`, `Configlist_closure`, `State_insert`, `State_find`, `Configtable_insert`, and `Configtable_find` de-duplicate configurations and states through generated hash-table code.
- Parser for grammar input: `Parse`, `preprocess_input`, `eval_preprocessor_boolean`, and `parseonetoken` scan the grammar file, build rules, process directives such as `%name`, `%type`, `%fallback`, `%wildcard`, `%token_class`, `%destructor`, and capture user code blocks.
- Reporting and output: `ReportOutput`, `ReportTable`, `ReportHeader`, `Reprint`, `CompressTables`, `ResortStates`, `translate_code`, `emit_code`, and `emit_destructor_code` produce `.out`, `.c`, `.h`, and optional `.sql` outputs.
- Table construction: `acttab_alloc`, `acttab_action`, `acttab_insert`, `compute_action`, and `minimum_size_type` generate compact `yy_action`, `yy_lookahead`, offset, and default-action tables.

## Control Flow
1. `main()` parses command-line options with the local option framework. Notable switches include `-b`, `-c`, `-d`, `-D`, `-E`, `-g`, `-m`, `-l`, `-p`, `-q`, `-r`, `-s`, `-S`, `-T`, and `-U`.
2. It initializes string, symbol, and state tables, creates the end marker symbol `$`, and calls `Parse(&lem)`.
3. `Parse()` reads the entire grammar into memory, runs `preprocess_input()`, then tokenizes identifiers, string literals, C code blocks, comments, `::=`, aliases, precedence marks, and one-character operators. Each token feeds `parseonetoken()`.
4. `parseonetoken()` is a state machine that builds `struct rule` objects, attaches rule code blocks, handles aliases and multiterminals, and stores directive payloads into `struct lemon` or `struct symbol` fields.
5. After parsing, `main()` indexes/sorts symbols, assigns rule numbers with action-bearing rules first, and either reprints grammar (`-g`) or runs the generator pipeline.
6. The generator computes first/lambda sets, LR(0) states, propagation links, follow sets, and actions. `resolve_conflict()` handles shift/shift, shift/reduce, and reduce/reduce conflicts using precedence and associativity where possible.
7. Unless disabled, `CompressTables()` chooses frequent reductions as defaults and converts shifts to auto-reduce states into `SHIFTREDUCE`; `ResortStates()` renumbers states to reduce table size.
8. `ReportOutput()` writes the human-readable automaton report; `ReportTable()` opens `lempar.c`, streams template sections separated by `%%`, injects generated tables and code, and emits the parser C file; `ReportHeader()` writes token defines unless makeheaders mode is active.

## State and Persistence Behavior
- Most generator state is explicit in `struct lemon`, but several module-level static tables persist across one process: `memChunkList`, `x1a` string table, `x2a` symbol table, `x3a` state table, `x4a` config table, configuration/plink/action free lists, option parser globals, and `-D` macro arrays.
- `lemon_free()` only zeroes tracked memory and does not unlink/free individual chunks; bulk cleanup happens through `lemon_free_all()` at process exit.
- `Parse()` loads each grammar file as a single buffer and mutates it in-place while tokenizing. `Strsafe()` interns token strings so the parser can safely release the file buffer after parsing.
- Output persistence is file-based: generated `.c`, `.h`, `.out`, and optional `.sql` names are derived from the grammar filename and `-d` output directory. `ReportHeader()` avoids rewriting an unchanged header.
- `%ifdef` preprocessing comments out excluded regions by replacing non-newline bytes with spaces, preserving line numbering for diagnostics and generated `#line` directives.

## Dependencies and Integration Points
- Depends on the C standard library plus `unistd.h`/`access()` on POSIX or a Windows-compatible `access()` declaration.
- Integrates with `lempar.c` as the parser driver template. `tplt_open()` uses an explicit `-T` template, a grammar-adjacent `.lt` file, local `lempar.c`, or a `PATH`/executable-relative search.
- Generated parsers expose names derived from `%name` or default `Parse`, and support template macros for `%extra_argument`, `%extra_context`, `%token_type`, `%default_type`, `%realloc`, `%free`, stack size, destructors, syntax errors, parse accept/failure, and stack overflow hooks.
- In SQLite builds, Lemon is used by the build system to generate parsers such as SQL grammar output; its generated token header is consumed by scanners unless `-m` delegates header creation to makeheaders.

## Risks and Edge Cases
- `lemon_malloc()` checks `nByte<0` even though `size_t` is unsigned; this is harmless but ineffective for overflow checks. Several allocation-size calculations can still overflow theoretically.
- `lemon_free()` is not a normal free and leaves allocations on `memChunkList`; code expecting immediate reuse or true deallocation would be wrong.
- `Parse()` caps inputs over 100,000,000 bytes but reads the file all at once; extremely large or malformed grammar files still stress memory and scanner paths.
- The scanner handles nested braces and skips C comments/strings, but it is a grammar-specific scanner, not a complete C parser; unusual C constructs in actions can confuse brace matching.
- `ReportTable()` writes SQL text with direct symbol/rule text quoting and is meant for generated diagnostics, not hostile grammar names.
- Conflict resolution depends on symbol order and precedence; unresolved conflicts make process exit fail even if code files were emitted.
- The table compaction and state resort steps affect generated parser table shape, so regression tests should compare behavior rather than relying only on stable table text unless `-r`/`-c` are used.

## Test Signals
- Build `lemon.c`, run it against known SQLite grammar inputs, and verify zero conflicts, generated parser compilation, token header stability, and `.out` reports.
- Exercise option parsing with `-D`, `-U`, `-E`, `-T`, `-d`, `-m`, `-S`, `-c`, and `-r`.
- Use grammars covering precedence resolution, fallback tokens, wildcard tokens, token classes/multiterminals, destructors, default types, extra arguments/context, empty rules, and `NEVER-REDUCE`.
- Verify generated parser behavior through SQLite parser tests, plus `YYCOVERAGE`/`yytestcase` signals in generated parsers.
- Check negative diagnostics: missing start symbol, start symbol on RHS, duplicate labels, unused labels, unterminated strings/C blocks, bad `%if` syntax, and nonterminals with no rules.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/lemon.c -->

## sources/storage-engines/sqlite/tool/lempar.c

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/lempar.c -->
# sources/storage-engines/sqlite/tool/lempar.c

## Purpose
`lempar.c` is the Lemon parser driver template. `lemon.c` copies this file to generated parser output and replaces each `%%` separator with generated includes, token definitions, control macros, parse tables, fallback tables, symbolic names, destructor cases, reduce actions, and user-supplied hooks. Any `Parse` identifier prefix is rewritten to the grammar `%name` value.

## Important APIs, Types, and Functions
- Generated parser state types: `struct yyStackEntry` stores state/action number, major token, and semantic minor value; `struct yyParser` stores the stack, top pointer, optional high-water mark, error recovery counter, `%extra_argument`, and `%extra_context`.
- Public parser API in generated output: `ParseTrace()` in debug builds, `ParseInit()`, `ParseAlloc()`, `ParseFinalize()`, `ParseFree()`, optional `ParseStackPeak()`, optional `ParseCoverage()`, main `Parse()`, and `ParseFallback()`.
- Core runtime helpers: `yyGrowStack`, `yy_destructor`, `yy_pop_parser_stack`, `yy_find_shift_action`, `yy_find_reduce_action`, `yyStackOverflow`, `yyTraceShift`, `yy_shift`, `yy_reduce`, `yy_parse_failed`, `yy_syntax_error`, and `yy_accept`.
- Generated tables/macros: `yy_action`, `yy_lookahead`, `yy_shift_ofst`, `yy_reduce_ofst`, `yy_default`, `yyFallback`, `yyTokenName`, `yyRuleName`, `yyRuleInfoLhs`, `yyRuleInfoNRhs`, `YYCODETYPE`, `YYACTIONTYPE`, `YYMINORTYPE`, `YYSTACKDEPTH`, `YYERRORSYMBOL`, and action-range constants.

## Control Flow
1. A caller allocates or provides a parser, initializes it with state 0 on the stack, then repeatedly calls `Parse(parser, major, minor, extra_arg)` with tokens. Token 0 is end-of-input.
2. `Parse()` starts from the current top stack state and calls `yy_find_shift_action()` for terminal lookahead. That routine consults offset/action/lookahead tables, then fallback and wildcard handling if the direct table entry misses.
3. If the action is reduce, `Parse()` calls `yy_reduce()`, which runs generated reduce code, computes the LHS nonterminal, finds the goto action with `yy_find_reduce_action()`, pops RHS entries, pushes the LHS, and loops for more reductions.
4. If the action is shift or shift-reduce, `yy_shift()` pushes the token and semantic value, grows the stack if configured, translates pending shift-reduce states into reduce action numbers, and returns to the caller.
5. If the action is accept, `Parse()` pops the start marker, calls `yy_accept()`, and returns.
6. If the action is syntax error, behavior depends on generated macros: with `YYERRORSYMBOL`, it calls syntax-error code, pops until the error token can shift, shifts error, and suppresses repeated errors for three successful shifts; with `YYNOERRORRECOVERY`, it reports and discards immediately; otherwise it reports/discards and fails on end-of-input.

## State and Persistence Behavior
- All parser runtime state is in `yyParser`; generated parsers are reentrant as long as callers do not share one parser instance across threads unsafely.
- Debug tracing uses static globals `yyTraceFILE` and `yyTracePrompt`, so trace configuration is process-global for the generated parser.
- With `YYGROWABLESTACK`, the parser starts with inline `yystk0` and can allocate a heap stack using `YYREALLOC`, freeing it in `ParseFinalize()`. With fixed stacks, overflow calls generated `%stack_overflow` code.
- Error recovery state is `yyerrcnt`; it suppresses repeated syntax errors until three successful shifts.
- `ParseFinalize()` and `ParseFree()` run destructors for stack entries still present; error handling and stack pops also call generated destructors for discarded semantic values.
- Optional `YYCOVERAGE` records a static `yycoverage[YYNSTATE][YYNTOKEN]` matrix of observed state/lookahead pairs.

## Dependencies and Integration Points
- Requires generated definitions from `lemon.c`; the template alone is not standalone because most `%%` placeholders must be filled.
- Uses grammar-provided code for `%include`, `%destructor`, `%token_destructor`, `%default_destructor`, `%stack_overflow`, `%parse_failure`, `%syntax_error`, `%parse_accept`, and reduce actions.
- Memory allocation is injected with `YYREALLOC`/`YYFREE` and `YYMALLOCARGTYPE`; context and extra arguments are wired through generated `ParseARG_*` and `ParseCTX_*` macros.
- SQLite-generated parsers can enable `yytestcase()` and `YYCOVERAGE` to link parser table coverage to the surrounding test harness.

## Risks and Edge Cases
- Generated table constants must be internally consistent; wrong offsets or action ranges become assertion failures in debug builds and undefined parser behavior in release builds.
- Fallback token mappings assert that fallback chains terminate, so grammar fallback cycles are invalid.
- Destructor generation must match semantic value union members; wrong `%type` or alias handling can compile but destroy the wrong union member.
- Error recovery discards input and stack symbols, so grammar destructors must be correct to avoid leaks or double frees.
- Stack growth depends on grammar-provided allocator signatures matching `YYREALLOC`/`YYFREE` and optional `YYSIZELIMIT`.
- `ParseTrace()` globals are not per parser instance.

## Test Signals
- Compile a generated parser with assertions enabled and run grammar tests through successful parses, syntax errors, error recovery, end-of-input, and parser destruction.
- Enable `YYCOVERAGE` and inspect `ParseCoverage()` misses for untested parser states.
- Test `YYFALLBACK`, `YYWILDCARD`, fixed stack overflow, growable stack expansion, `%extra_argument`, `%extra_context`, and destructors.
- Validate memory cleanup with parser finalization after partial parse and after syntax-error discard paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/lempar.c -->

## sources/storage-engines/sqlite/tool/libvers.c

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/libvers.c -->
# sources/storage-engines/sqlite/tool/libvers.c

## Purpose
`libvers.c` is a tiny diagnostic utility for linking against an SQLite library of unknown provenance and printing its runtime version metadata. It helps confirm which SQLite library a build or environment is actually resolving.

## Important APIs, Types, and Functions
- Declares `extern const char *sqlite3_libversion(void);`.
- Declares `extern const char *sqlite3_sourceid(void);`.
- `main()` prints both values with `printf()` and returns success.

## Control Flow
`main()` ignores its arguments, calls `sqlite3_libversion()` and `sqlite3_sourceid()`, prints one line for the version and one line for the source ID, then exits with `0`.

## State and Persistence Behavior
The program has no persistent state, no heap state, no files, and no database handles. Its output is entirely derived from the linked SQLite library.

## Dependencies and Integration Points
- Depends on `stdio.h` and external SQLite symbols supplied by the linked library.
- It intentionally does not include `sqlite3.h`; the two declarations are enough for this probe.
- Useful in build/test environments where `LD_LIBRARY_PATH`, static linking, package manager libraries, or local build artifacts may select different SQLite binaries.

## Risks and Edge Cases
- Link-time failure indicates the selected library does not export the expected symbols.
- Runtime dynamic loader selection can still differ from compile-time expectations; the output is useful precisely because it reports the loaded library.
- The unused `argc`/`argv` may trigger warnings under strict warning policies.

## Test Signals
- Compile and link against a known SQLite build, run the binary, and compare printed version/source ID to the expected build.
- Repeat with dynamic library path changes to confirm it reports the runtime-loaded library.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/libvers.c -->

## sources/storage-engines/sqlite/tool/loadfts.c

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/loadfts.c -->
# sources/storage-engines/sqlite/tool/loadfts.c

## Purpose
`loadfts.c` is a command-line performance-test helper that creates an SQLite FTS3, FTS4, or FTS5 table and recursively loads file contents from a directory tree into a single-column `fts` virtual table. It can also issue special FTS control inserts and optionally batch inserts in transactions.

## Important APIs, Types, and Functions
- `readfileFunc()` implements SQL function `readtext(X)`, reading an entire path into SQLite-allocated memory and returning it as UTF-8 text.
- `showHelp()`, `error_out()`, and `sqlite_error_out()` provide CLI usage and fatal diagnostics.
- `struct VisitContext` carries `nRowPerTrans`, `sqlite3 *db`, and prepared insert statement `pInsert`.
- `visit_file()` binds a file path into `INSERT INTO fts VALUES(readtext(?))`, steps/resets the statement, and commits/begins every configured row interval.
- `traverse()` recursively walks directories with `opendir()`, `readdir()`, `dirent.d_type`, and `sqlite3_mprintf()` path construction.
- `main()` parses switches, opens the database, creates the scalar SQL function, creates the FTS virtual table, applies `-special` commands, prepares insert SQL, traverses files, finalizes, closes, and frees.

## Control Flow
1. The program expects switch/value pairs followed by the database path; malformed arity or unknown options call `showHelp()`.
2. CLI options select FTS version (`-fts 3|4|5`), mapping-table flag (`-idx 0|1` parsed but not used elsewhere), root directory (`-dir`), transaction interval (`-trans`), and repeated `-special` commands.
3. `sqlite3_open()` opens the target DB and `sqlite3_create_function()` registers `readtext`.
4. It creates `CREATE VIRTUAL TABLE fts USING fts%d(content)`, then executes each special command as `INSERT INTO fts(fts) VALUES(%Q)`.
5. It prepares the insert statement, starts a transaction if requested, recursively traverses the input directory, inserts every non-directory entry, commits periodically based on last rowid, commits at the end, and cleans up.

## State and Persistence Behavior
- Persistent state is the target SQLite database. The program creates and populates a virtual table named `fts`; rerunning against a database that already has that table will fail at creation.
- `readfileFunc()` loads one complete file into memory per SQL call and transfers ownership to SQLite with `sqlite3_free` as destructor on success.
- Transaction behavior is controlled by `nRowPerTrans`; a positive value wraps inserts in `BEGIN`/`COMMIT` and commits every rowid multiple.
- Directory traversal is depth-first recursion and does not persist a file manifest.

## Dependencies and Integration Points
- Depends on SQLite public C API and FTS modules compiled/loaded into the SQLite library.
- Depends on POSIX directory APIs (`dirent.h`, `opendir`, `readdir`, `closedir`) and `dirent.d_type`.
- Integrates with SQLite's FTS control channel through `INSERT INTO fts(fts) VALUES(...)` for `-special`.
- Intended for benchmark/test workloads rather than general-purpose ingestion.

## Risks and Edge Cases
- `-idx` is parsed and validated but never used; users may expect a filename-to-rowid mapping table that this version does not create.
- `readfileFunc()` uses `ftell()` into `long` and `sqlite3_malloc(nIn)` without explicit negative/large-size checks; very large files can fail or stress memory.
- A zero-length file causes `sqlite3_malloc(0)` and `fread(..., 0, 1, ...)`, which may not return the success condition, yielding NULL/no result rather than empty text.
- Traversal relies on `d_type & DT_DIR`; filesystems that return `DT_UNKNOWN` will treat directories as files and skip recursion.
- No filtering is applied for binary files, symlinks, hidden files, or unreadable files; unreadable files become NULL text silently through `readtext`.
- Periodic commit uses `sqlite3_last_insert_rowid() % nRowPerTrans`, which assumes rowids advance with each insert into the FTS table as expected.

## Test Signals
- Build against SQLite with FTS3/4/5 enabled and run with `-fts 3`, `-fts 4`, and `-fts 5`.
- Load a small directory tree and verify `SELECT count(*) FROM fts`.
- Test nested directories, empty files, unreadable files, large files, binary files, and filesystems with unknown `d_type`.
- Test `-trans` boundaries and `-special` commands such as FTS optimize/merge operations supported by the selected FTS version.
- Confirm current `-idx` behavior before relying on any mapping table.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/loadfts.c -->

## sources/storage-engines/sqlite/tool/logest.c

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/logest.c -->
# sources/storage-engines/sqlite/tool/logest.c

## Purpose
`logest.c` is an interactive command-line calculator for SQLite's `LogEst` numeric representation, where values are approximately ten times base-2 logarithms. It converts between integers/floats and `LogEst`, performs multiply/add/reciprocal/log/NlogN operations on a small stack, and prints approximate numeric interpretations.

## Important APIs, Types, and Functions
- `typedef short int LogEst` defines the compact estimate type.
- `logEstMultiply(a,b)` adds two estimates, corresponding to multiplication in normal space.
- `logEstAdd(a,b)` approximates `log2(2^(a/10)+2^(b/10))*10` using a lookup table for deltas.
- `logEstFromInteger(sqlite3_uint64)` converts integer magnitudes to `LogEst`.
- `logEstToInt(LogEst)` converts estimates back to approximate unsigned integers, saturating at 64-bit max for very large estimates.
- `logEstFromDouble(double)` handles positive floating-point input, including subunit values and large values by inspecting IEEE-754 exponent bits.
- `isInteger()`, `isFloat()`, `showHelp()`, and `main()` implement stack-language parsing and output formatting.

## Control Flow
1. `main()` iterates over arguments and maintains a fixed stack `LogEst a[100]` with count `n`.
2. Numeric integer arguments are converted with `logEstFromInteger()`. Nonnegative floating arguments are converted with `logEstFromDouble()`. Arguments prefixed with `^` are interpreted directly as raw `LogEst`.
3. Operators mutate the stack: `+` combines top two with `logEstAdd`, `x` combines top two with `logEstMultiply`, `dup` duplicates, `inv` negates, `log` maps `N` to `log(N)`, and `nlogn` maps `N` to `N*log(N)`.
4. Unknown arguments call `showHelp()`. At the end, the stack is printed from top to bottom with raw estimate and approximate decimal/integer value.

## State and Persistence Behavior
All state is process-local stack memory. The program does not open databases or persist output; it only uses SQLite integer typedefs from `sqlite3.h`.

## Dependencies and Integration Points
- Depends on `sqlite3.h` for `sqlite3_uint64`.
- Mirrors SQLite planner estimation math used internally, making it useful for validating constants, estimates, and planner-cost intuition outside the main engine.
- Depends on standard C libraries for parsing and formatting.

## Risks and Edge Cases
- The stack has fixed size 100 and `dup`/push paths do not check overflow, so long argument lists can write past the array.
- `isFloat()` accepts broad character combinations and leaves final validation to `atof()` behavior; strings like repeated signs may pass syntactic screening.
- Negative floating-point arguments are rejected by the `z[0] != '-'` condition, while reciprocal values are represented through `inv`.
- `logEstFromDouble()` assumes 8-byte IEEE-754 `double` and 8-byte unsigned integer, enforced only by `assert()`.
- Output format uses `%lld` with `sqlite3_uint64` expressions; platform format mismatches are possible if typedefs differ.

## Test Signals
- Compare conversions for known inputs such as `1`, `2`, `10`, `100`, `123456`, `^123`, and fractional floats.
- Exercise stack operations: `2 3 x`, `100 200 +`, `10 dup x`, `100 log`, `100 nlogn`, and `10 inv`.
- Run with assertions enabled for floating conversions.
- Add overflow tests for more than 100 push operations if hardening this tool.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/logest.c -->

## sources/storage-engines/sqlite/tool/max-limits.c

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/max-limits.c -->
# sources/storage-engines/sqlite/tool/max-limits.c

## Purpose
`max-limits.c` is a diagnostic utility that links against an SQLite library and prints the compile-time maximum values for SQLite runtime limits. It discovers each maximum by temporarily attempting to raise that limit to the largest signed 32-bit value and reading back SQLite's clamped value.

## Important APIs, Types, and Functions
- `aLimit[]` maps `SQLITE_LIMIT_*` categories to their corresponding `SQLITE_MAX_*` compile-time names.
- `maxLimit(sqlite3 *db, int eCode)` saves the current limit, calls `sqlite3_limit(db, eCode, 0x7fffffff)`, then restores the original value and returns the maximum.
- `main()` opens an in-memory database, iterates `aLimit`, prints aligned name/value pairs, and closes the DB.

## Control Flow
`main()` calls `sqlite3_open(":memory:", &db)`. If successful, it loops over `aLimit`, calls `maxLimit()` for each category, prints the result, then closes the database. If open fails, it exits silently without printing an error.

## State and Persistence Behavior
No persistent database state is created because the database is in-memory. Each limit is restored immediately after probing, so the database handle is left with original runtime limits until close.

## Dependencies and Integration Points
- Depends on `sqlite3.h`, `stdio.h`, and a linkable SQLite library.
- Reports limits affected by compile-time macros such as `SQLITE_MAX_LENGTH`, `SQLITE_MAX_COLUMN`, `SQLITE_MAX_VARIABLE_NUMBER`, and others.
- Useful in packaging, support, and test contexts where the effective library's compile options need verification.

## Risks and Edge Cases
- Failed `sqlite3_open()` is ignored, so diagnostics are absent on failure.
- The list only covers the hardcoded `SQLITE_LIMIT_*` categories present in this source; new SQLite limit categories require source changes.
- The method relies on `sqlite3_limit()` returning the old/current effective maximum when asked for a huge value, which is the intended SQLite API behavior.

## Test Signals
- Compile against a default SQLite build and compare printed values to documented defaults for that version.
- Compile against custom `SQLITE_MAX_*` settings and verify the tool reflects the custom maxima.
- Include a link/runtime library mismatch test to verify it reports the loaded library's limits, not just headers.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/max-limits.c -->

## sources/storage-engines/sqlite/tool/mkautoconfamal.sh

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/mkautoconfamal.sh -->
# sources/storage-engines/sqlite/tool/mkautoconfamal.sh

## Purpose
`mkautoconfamal.sh` builds SQLite's amalgamation autoconf distribution tarball from already-generated amalgamation inputs and the full SQLite source tree. It stages files into a temporary package directory, adds Tcl extension glue, cleans build/editor remnants, runs configure/dist, renames the produced package to the autoconf artifact name, and places the final `.tar.gz` in the caller's working directory.

## Important APIs, Types, and Functions
- Shell variables: `TMPSPACE=./mkpkg_tmp_dir`, `VERSION`, `HASH`, `DATETIME`, and `TARBALLNAME`.
- Inputs from current directory: `sqlite3.c`, `sqlite3.h`, `sqlite3ext.h`, `sqlite3rc.h`, and `shell.c`.
- Inputs from `$TOP`: `VERSION`, `manifest.uuid`, `manifest`, `autoconf`, `autosetup`, `configure`, `sqlite3.1`, `sqlite3.pc.in`, `src/sqlite3.rc`, `tool/Replace.cs`, `main.mk`, `make.bat`, and `src/tclsqlite.c`.
- Generated file: `tea/generic/tclsqlite3.c`, beginning with a `USE_SYSTEM_SQLITE` conditional and then appending SQLite's Tcl binding source.

## Control Flow
1. The script enables `set -e` and `set -u`.
2. It reads version and manifest metadata from `$TOP`.
3. It chooses `TARBALLNAME`: for normal release-style invocation, it converts `3.x.y[.z]` into `sqlite-autoconf-3xxyyzz`; for `--snapshot` or no matching non-snapshot branch, it uses `sqlite-snapshot-$DATETIME`.
4. It removes and recreates the staging area by copying autoconf infrastructure and amalgamation/source files into `./mkpkg_tmp_dir`.
5. It prints the staging tree, changes into the staging directory, creates Tcl wrapper source, deletes editor/build artifacts, runs `./configure && ${MAKE-make} dist`, unpacks the produced `sqlite-$VERSION.tar.gz`, renames it to `$TARBALLNAME`, repacks it, moves the final tarball to the parent directory, and lists it.

## State and Persistence Behavior
- Destructively removes `./mkpkg_tmp_dir` on every run.
- Produces `$TARBALLNAME.tar.gz` one directory above the staging directory, normally the original current working directory.
- Reads source-tree metadata but does not modify `$TOP`.
- Uses `${MAKE-make}` so the environment can select a make implementation.

## Dependencies and Integration Points
- Requires a POSIX-ish `/bin/sh`, `cat`, `cut`, `grep`, `tr`, `sed`, `printf`, `rm`, `cp`, `tree`, `mkdir`, `find`, `configure`, `make`, `tar`, and `ls`.
- Integrates with SQLite release/build artifacts; it assumes the amalgamation files already exist in the current directory and `$TOP` points to the source root.
- The generated autoconf tarball is a release/distribution artifact rather than a normal build output.

## Risks and Edge Cases
- `rm -rf $TMPSPACE` is intentionally destructive; running from the wrong directory can delete a local directory with the same name.
- Variables are unquoted in many commands, so spaces or shell metacharacters in `$TOP`, `$VERSION`, or paths can break the script.
- The argument condition appears inverted relative to the comment: the normal autoconf naming branch is taken when at least one argument exists and `$1` is not `--snapshot`; otherwise snapshot naming is used.
- The script assumes `tree` is installed, which may not hold on minimal builders.
- `HASH` is computed but unused.
- Build output depends on the host toolchain and configure behavior.

## Test Signals
- Run from a clean amalgamation directory with valid `$TOP` and verify the tarball name, contents, and included Tcl wrapper.
- Test `--snapshot` and release-version naming explicitly.
- Run with missing required files to confirm `set -e` stops early.
- Inspect the tarball for absence of `*~`, `#*#`, `*.o`, and `*.so` remnants.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/mkautoconfamal.sh -->

## sources/storage-engines/sqlite/tool/mkfptab.c

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/mkfptab.c -->
# sources/storage-engines/sqlite/tool/mkfptab.c

## Purpose
`mkfptab.c` generates C table initializers used by SQLite's floating-point power-of-ten conversion code. It constructs high-precision 256-bit approximations for powers of 10 from `1.0e-351` through `1.0e+347`, then emits compact `aBase[]`, `aScale[]`, and `aScaleLo[]` tables that let runtime code reconstruct the significant high bits of decimal powers using smaller lookup tables. With `--truth`, it also emits a full 128-bit reference table.

## Important APIs, Types, and Functions
- `typedef unsigned __int128 u128` and `typedef unsigned long long int u64` provide arithmetic building blocks.
- `struct u256 { u64 a[4]; }` represents a synthesized big-endian 256-bit unsigned integer.
- `u256_times_10`, `u256_times_2`, `u256_div_10`, and `u256_div_2` implement in-place scaled arithmetic with carries/remainders.
- Constants `SCALE_FIRST`, `SCALE_LAST`, `SCALE_COUNT`, and `SCALE_ZERO` define the exponent range and index of `1.0e+0`.
- `main()` parses `--round` and `--truth`, fills `aHi`, `aLo`, and `aE`, then prints C initializers.

## Control Flow
1. CLI parsing accepts `-round`/`--round` and `-truth`/`--truth`, otherwise exits with an unknown-option error.
2. For nonpositive decimal exponents, it initializes a normalized `u256` at the high bit, records high/low words and binary exponent, divides by 10, and renormalizes by multiplying by 2.
3. For positive decimal exponents, it initializes a shifted value, repeatedly multiplies by 10, renormalizes by dividing by 2 while carry appears in the top word, and records high/low words and exponent.
4. If `--truth` is set, it prints `aTruth[]` entries with 128 bits for every supported decimal power.
5. It prints `aBase[]` for powers 0 through 26.
6. It prints `aScale[]` and `aScaleLo[]` at 27-exponent intervals, with a special entry for exponent -1 replacing the zero slot. `--round` rounds `aScaleLo[]` high 32-bit values when bit 31 is set, except for the special case.

## State and Persistence Behavior
The program has no persistent state. It computes all arrays in stack-local `aHi`, `aLo`, and `aE` buffers and writes generated C text to standard output.

## Dependencies and Integration Points
- Requires compiler support for `__uint128_t`/`unsigned __int128`, available in GCC/Clang but not portable to all C compilers.
- Includes standard headers only.
- Its output is intended to be copied or generated into SQLite floating-point utility code, specifically the tables used by `powerOfTen()` in `util.c`.

## Risks and Edge Cases
- Portability is limited by `unsigned __int128`.
- The comments mention approximates accurate to "96 bytes" and "next 32 bites"; those are comment typos and should be interpreted as bits.
- Format strings use `%llx` and assume `u64` is compatible with `unsigned long long`.
- Arithmetic correctness depends on normalization loops preserving the intended significant bits across the full exponent range; changes need numerical validation, not just compile tests.
- The program writes code to stdout, so build scripts must redirect output deliberately.

## Test Signals
- Compile with GCC or Clang and run with no arguments, `--round`, `--truth`, and combined flags.
- Diff generated tables against checked-in SQLite table constants.
- Validate selected powers against high-precision decimal/binary calculations, especially boundaries `-351`, `-348`, `0`, `26`, `27`, and `+347`.
- Confirm unknown options exit nonzero with a diagnostic.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/mkfptab.c -->
