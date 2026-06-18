# subset-b-009278 Research

Grouped research for the requested lcov/genhtml test files. Each section is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/demangle.sh -->
# sources/test-tools/lcov/tests/genhtml/demangle.sh

- Purpose: Exercises `genhtml` C++ demangling modes with a synthetic trace containing plain and mangled function names.
- Important APIs/types/functions: Shell functions `die`, `cleanup`, `prepare`, and `run`; `prepare` writes a temporary info/source pair and `run` captures genhtml stdout/stderr.
- Control flow: Runs no-demangle, default `c++filt`, custom demangler, and custom demangler with parameters, then greps generated function HTML for expected transformed names.
- State and persistence behavior: Creates `out_demangle`, stdout/stderr logs, `demangle.info.tmp`, and `file.tmp`; cleanup removes core generated inputs.
- Dependencies and integration points: Depends on `$GENHTML`, optional `c++filt`, local `mycppfilt.sh`, Perl filtering, and genhtml function-view HTML naming.
- Risks: HTML class/name and environment-specific demangler output can vary; the script accepts either of two default conversions.
- Test signals: Passing signals are clean stderr, expected exit code, and generated function names in `${OUTDIR}/genhtml/file.tmp.func.html`.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/demangle.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/Makefile -->
# sources/test-tools/lcov/tests/genhtml/errs/Makefile

- Purpose: Makefile entry for `msgtest.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/MsgContext.pm -->
# sources/test-tools/lcov/tests/genhtml/errs/MsgContext.pm

- Purpose: Perl callback fixture for negative or specialized lcov/genhtml callback-path testing in `sources/test-tools/lcov/tests/genhtml/errs`.
- Important APIs/types/functions: Defines package `MsgContext` with methods: new, test, context.
- Control flow: The harness loads it through lcov/genhtml callback options so selected methods either provide synthetic data or deliberately fail to validate diagnostics.
- State and persistence behavior: State is held in blessed constructor arguments where present; modules write no persistent files themselves.
- Dependencies and integration points: Depends on Perl callback loading and the lcov/genhtml callback protocol; integrated by nearby shell tests.
- Risks: API drift in callback method names or diagnostic formatting can change the targeted failure mode.
- Test signals: Passing signal is the parent shell script observing the expected callback result, warning, or failure message.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/MsgContext.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/genError.pm -->
# sources/test-tools/lcov/tests/genhtml/errs/genError.pm

- Purpose: Perl callback fixture for negative or specialized lcov/genhtml callback-path testing in `sources/test-tools/lcov/tests/genhtml/errs`.
- Important APIs/types/functions: Defines package `genError` with methods: new, select, extract_version, compare_version, annotate, resolve, check_criteria, simplify, exclude.
- Control flow: The harness loads it through lcov/genhtml callback options so selected methods either provide synthetic data or deliberately fail to validate diagnostics.
- State and persistence behavior: State is held in blessed constructor arguments where present; modules write no persistent files themselves.
- Dependencies and integration points: Depends on Perl callback loading and the lcov/genhtml callback protocol; integrated by nearby shell tests.
- Risks: API drift in callback method names or diagnostic formatting can change the targeted failure mode.
- Test signals: Passing signal is the parent shell script observing the expected callback result, warning, or failure message.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/genError.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/missingRestore.pm -->
# sources/test-tools/lcov/tests/genhtml/errs/missingRestore.pm

- Purpose: Perl callback fixture for negative or specialized lcov/genhtml callback-path testing in `sources/test-tools/lcov/tests/genhtml/errs`.
- Important APIs/types/functions: Defines package `missingRestore` with methods: new, simplify, start, save.
- Control flow: The harness loads it through lcov/genhtml callback options so selected methods either provide synthetic data or deliberately fail to validate diagnostics.
- State and persistence behavior: State is held in blessed constructor arguments where present; modules write no persistent files themselves.
- Dependencies and integration points: Depends on Perl callback loading and the lcov/genhtml callback protocol; integrated by nearby shell tests.
- Risks: API drift in callback method names or diagnostic formatting can change the targeted failure mode.
- Test signals: Passing signal is the parent shell script observing the expected callback result, warning, or failure message.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/missingRestore.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/msgtest.sh -->
# sources/test-tools/lcov/tests/genhtml/errs/msgtest.sh

- Purpose: Large genhtml/lcov diagnostic regression harness covering option validation, config includes, callbacks, cache errors, case-insensitive substitutions, deprecated RC options, MC/DC diagnostics, and message-count expectations.
- Important APIs/types/functions: Procedural shell script using `LCOV_BASE`, `DIFFCOV_OPTS`, version/annotate/select/criteria callback paths, compiler gates, and common.tst variables; no reusable shell functions.
- Control flow: Cleans artifacts, builds/captures baseline data, then runs many independent positive and negative `lcov`, `geninfo`, and `genhtml` checks, validating each with exit codes and greps.
- State and persistence behavior: Creates transient `.info`, `.log`, `.rc`, `.json`, cache directories, callback output directories, and report trees; its initial cleanup block defines the persistence boundary.
- Dependencies and integration points: Depends on `common.tst`, local callback fixtures, repository callback scripts, compiler tools, `mcdc_errs.dat`, and lcov/genhtml diagnostic wording.
- Risks: High brittleness from exact message greps, compiler-version coverage variance, permissions, and deliberately corrupt cache/config state; mitigated by targeted `--ignore` paths.
- Test signals: Passing signals are expected failure/success codes and greps for usage, callback, inconsistent, count, deprecated RC, empty diff, cache, context, and MC/DC messages.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/msgtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/parallelFail.pm -->
# sources/test-tools/lcov/tests/genhtml/errs/parallelFail.pm

- Purpose: Perl callback fixture for negative or specialized lcov/genhtml callback-path testing in `sources/test-tools/lcov/tests/genhtml/errs`.
- Important APIs/types/functions: Defines package `parallelFail` with methods: new, simplify, start, save, restore, finalize.
- Control flow: The harness loads it through lcov/genhtml callback options so selected methods either provide synthetic data or deliberately fail to validate diagnostics.
- State and persistence behavior: State is held in blessed constructor arguments where present; modules write no persistent files themselves.
- Dependencies and integration points: Depends on Perl callback loading and the lcov/genhtml callback protocol; integrated by nearby shell tests.
- Risks: API drift in callback method names or diagnostic formatting can change the targeted failure mode.
- Test signals: Passing signal is the parent shell script observing the expected callback result, warning, or failure message.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/parallelFail.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/select.sh -->
# sources/test-tools/lcov/tests/genhtml/errs/select.sh

- Purpose: Shell helper or test driver for `sources/test-tools/lcov/tests/genhtml/errs`.
- Important APIs/types/functions: Executable script interface; local functions are absent or limited to driver helpers parsed by the script itself.
- Control flow: Parses optional test flags, invokes lcov/genhtml/compiler/helper commands, and checks results with exit codes, `grep`, `diff`, or generated file existence.
- State and persistence behavior: Creates transient logs, coverage files, binaries, and output directories named in its cleanup block or parent Makefile.
- Dependencies and integration points: Depends on `common.tst` where sourced, local fixtures, lcov/genhtml tools, compiler tools, and standard shell utilities.
- Risks: Risks are exact diagnostic greps, environment/tool availability, and stale cleanup lists.
- Test signals: Passing signals are successful expected commands and explicit grep/diff/file-existence assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/select.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/Makefile -->
# sources/test-tools/lcov/tests/genhtml/exception/Makefile

- Purpose: Makefile entry for `exception.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/exception.cpp -->
# sources/test-tools/lcov/tests/genhtml/exception/exception.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/exception`. It stresses exception branch capture/filtering.
- Important APIs/types/functions: Important declarations include: struct Throw {Throw () {throw std::exception();}};; struct NoThrow {NoThrow () {}};; static int a;; template<typename T>; bool test(); int main().
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/exception.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/exception.sh -->
# sources/test-tools/lcov/tests/genhtml/exception/exception.sh

- Purpose: Genhtml exception-branch regression harness for throwing and nonthrowing builds, trace merging, exception branch filtering, and differential reports.
- Important APIs/types/functions: Defines shell functions `runClang` and `runGcc`; uses common tool variables, version scripts, compiler selection, and ignore/filter options.
- Control flow: Compiles `exception.cpp` with `DO_THROW` and `NO_THROW`, captures coverage, normalizes compiler quirks, merges traces in both directions, and renders genhtml normal/differential reports.
- State and persistence behavior: Creates executables, `.gcno/.gcda`, `.info`, logs, and report directories; clean removes them.
- Dependencies and integration points: Depends on gcc/clang/llvm-cov availability, lcov/genhtml/geninfo, `common.tst`, and source-control version callbacks.
- Risks: Compiler-specific exception branch layouts are the main risk; old gcc inconsistency is handled with filters/gates.
- Test signals: Passing signals are successful capture/merge/report commands and expected normalized branch/report comparisons.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/exception.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/Makefile -->
# sources/test-tools/lcov/tests/genhtml/filter/Makefile

- Purpose: Makefile entry for `filter.pl` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/brace.c -->
# sources/test-tools/lcov/tests/genhtml/filter/brace.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: void braceExample2() {.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/brace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/expr1.c -->
# sources/test-tools/lcov/tests/genhtml/filter/expr1.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: small parser fixture with no complete exported API.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/expr1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/expr2.c -->
# sources/test-tools/lcov/tests/genhtml/filter/expr2.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: small parser fixture with no complete exported API.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/expr2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/expr3.c -->
# sources/test-tools/lcov/tests/genhtml/filter/expr3.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: small parser fixture with no complete exported API.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/expr3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/expr4.c -->
# sources/test-tools/lcov/tests/genhtml/filter/expr4.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: small parser fixture with no complete exported API.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/expr4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/filter.pl -->
# sources/test-tools/lcov/tests/genhtml/filter/filter.pl

- Purpose: Perl harness for lcov source filtering primitives: conditional detection, trivial-function detection, brace filtering, and compiler-directive filtering.
- Important APIs/types/functions: Uses `lcovutil`, `ReadCurrentSource`, `TraceFile`, `parseOptions`, `parse_ignore_errors`, `containsConditional`, `containsTrivialFunction`, `parse_cov_filters`, `write_info_file`, and `count_totals`.
- Control flow: Initializes options, checks `expr*.c`, mutates lookahead/bitwise globals, checks `*rivial*.c`, then compares vanilla, brace-filtered, and directive-filtered counts for `brace.c`.
- State and persistence behavior: Writes derived `.filtered`, `.orig`, and `.directive` files when matching `.info` inputs exist; global parser settings are reset between scenarios.
- Dependencies and integration points: Depends on repository lcov Perl modules, fixture source/info files, and current-directory glob order.
- Risks: Global settings can leak between checks, and broad globs can include unintended future fixtures.
- Test signals: Passing signal is final `passed` output with no `die`, plus expected count reductions in derived info files.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/filter.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/multilineTrivial.c -->
# sources/test-tools/lcov/tests/genhtml/filter/multilineTrivial.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: void x() {.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/multilineTrivial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/multilineTrivial2.c -->
# sources/test-tools/lcov/tests/genhtml/filter/multilineTrivial2.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: void x() {.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/multilineTrivial2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/notTrivial1.c -->
# sources/test-tools/lcov/tests/genhtml/filter/notTrivial1.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: void skipMe(unsigned, unsigned) { return 1; }.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/notTrivial1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/notTrivial2.c -->
# sources/test-tools/lcov/tests/genhtml/filter/notTrivial2.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: void containsCode() { a;.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/notTrivial2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/notTrivial3.c -->
# sources/test-tools/lcov/tests/genhtml/filter/notTrivial3.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: small parser fixture with no complete exported API.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/notTrivial3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/notTrivial_init.c -->
# sources/test-tools/lcov/tests/genhtml/filter/notTrivial_init.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: Data::Data(int a).
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/notTrivial_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/notTrivial_multiline.c -->
# sources/test-tools/lcov/tests/genhtml/filter/notTrivial_multiline.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: void y(int x, int z) {.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/notTrivial_multiline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/trivial1.c -->
# sources/test-tools/lcov/tests/genhtml/filter/trivial1.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: void trivial() { /* comment */}.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/trivial1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/trivial2.c -->
# sources/test-tools/lcov/tests/genhtml/filter/trivial2.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: int trivial(unsigned abc) {};.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/trivial2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/trivial3.c -->
# sources/test-tools/lcov/tests/genhtml/filter/trivial3.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: }; // simulate end of class decl.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/trivial3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/trivialMethod.c -->
# sources/test-tools/lcov/tests/genhtml/filter/trivialMethod.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/filter`. It is parsed as text by source-filter tests rather than compiled as a standalone program.
- Important APIs/types/functions: Important declarations include: Data::Data(int a) {.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/trivialMethod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/full.sh -->
# sources/test-tools/lcov/tests/genhtml/full.sh

- Purpose: Creates genhtml output for `100% coverage` fixture data and validates summary counts and generated files.
- Important APIs/types/functions: No shell functions; accepts `--coverage` and `--verbose`, and relies on environment variables for input info files and expected counts.
- Control flow: Runs `$GENHTML $FULLINFO`, captures stdout/stderr, validates exit status and clean stderr, calls `check_counts` with `$FULLCOUNTS`, and ensures HTML files exist.
- State and persistence behavior: Creates `out_full` and stdout/stderr logs; source inputs are not modified.
- Dependencies and integration points: Depends on `$GENHTML`, mkinfo-provided trace/count variables, `check_counts`, Perl Devel::Cover filtering, and `find`.
- Risks: Fixture-data or genhtml stdout wording drift can break count checks while rendering still works.
- Test signals: Passing signals are matching counts, empty stderr outside coverage mode, and at least one generated `.html` file.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/full.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/Makefile -->
# sources/test-tools/lcov/tests/genhtml/function/Makefile

- Purpose: Makefile entry for `function.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/current.cpp -->
# sources/test-tools/lcov/tests/genhtml/function/current.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/function`. It provides stable functions whose bodies/call status differ between baseline and current revisions.
- Important APIs/types/functions: Important declarations include: void; void; void; void; void; void; void; void.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/current.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/function.sh -->
# sources/test-tools/lcov/tests/genhtml/function/function.sh

- Purpose: End-to-end genhtml function categorization harness comparing baseline and current C++ revisions across called/not-called combinations, version insertion, aliases, and report generation.
- Important APIs/types/functions: Procedural shell script using `LCOV_BASE`, `VERSION_OPTS`, `LCOV_OPTS`, `DIFFCOV_OPTS`, symlinks to fixture sources, and `common.tst` tool variables.
- Control flow: Captures baseline called/no-call traces, verifies inserting version data into a trace without versions, captures current called/no-call traces, builds a diff, and runs genhtml for matrix combinations against gold output.
- State and persistence behavior: Creates symlinks, binaries, coverage data, `.info/.gz`, `.json`, `.xlsx`, diffs, logs, and output directories; clean removes them.
- Dependencies and integration points: Depends on C++ compiler, lcov/genhtml, Python `xlsxwriter`, diff/sed/perl normalization, common harness, and local gold files.
- Risks: Compiler function end-line metadata, generated static initializer symbols, and xlsxwriter availability can affect results.
- Test signals: Passing signals are matching version-inserted data, expected matrix reports, end-line/proportion handling when supported, and alias suppression behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/function.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/initial.cpp -->
# sources/test-tools/lcov/tests/genhtml/function/initial.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/function`. It provides stable functions whose bodies/call status differ between baseline and current revisions.
- Important APIs/types/functions: Important declarations include: void; void; void; void; void; void; void; void.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/initial.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/template.cpp -->
# sources/test-tools/lcov/tests/genhtml/function/template.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/function`. It provides stable functions whose bodies/call status differ between baseline and current revisions.
- Important APIs/types/functions: Important declarations include: template <typename T, unsigned i=0>; void; int; main(int ac, char **av).
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/template.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/Makefile -->
# sources/test-tools/lcov/tests/genhtml/insensitive/Makefile

- Purpose: Makefile entry for `insensitive.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/annotate.sh -->
# sources/test-tools/lcov/tests/genhtml/insensitive/annotate.sh

- Purpose: Perl case-insensitive annotation callback used by genhtml tests to provide source line metadata and modification timestamps.
- Important APIs/types/functions: Defines `get_modify_time`; uses `POSIX::strftime` and, in the insensitive variant, path case matching helpers/modules.
- Control flow: Resolves the requested file, calculates modification time, reads source lines, normalizes carriage returns, and emits annotation records for genhtml.
- State and persistence behavior: Reads filesystem metadata and file contents; writes no persistent files except caller-controlled logs.
- Dependencies and integration points: Depends on Perl modules, file stat data, and genhtml annotate callback protocol.
- Risks: Timestamp and path-case sensitivity can affect version/annotation consistency checks.
- Test signals: Passing signals are expected annotation/owner/date data in generated reports or expected annotation failure diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/annotate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/insensitive.sh -->
# sources/test-tools/lcov/tests/genhtml/insensitive/insensitive.sh

- Purpose: Shell helper or test driver for `sources/test-tools/lcov/tests/genhtml/insensitive`.
- Important APIs/types/functions: Executable script interface; local functions are absent or limited to driver helpers parsed by the script itself.
- Control flow: Parses optional test flags, invokes lcov/genhtml/compiler/helper commands, and checks results with exit codes, `grep`, `diff`, or generated file existence.
- State and persistence behavior: Creates transient logs, coverage files, binaries, and output directories named in its cleanup block or parent Makefile.
- Dependencies and integration points: Depends on `common.tst` where sourced, local fixtures, lcov/genhtml tools, compiler tools, and standard shell utilities.
- Risks: Risks are exact diagnostic greps, environment/tool availability, and stale cleanup lists.
- Test signals: Passing signals are successful expected commands and explicit grep/diff/file-existence assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/insensitive.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/version.sh -->
# sources/test-tools/lcov/tests/genhtml/insensitive/version.sh

- Purpose: Minimal version callback returning a stable version for case-insensitive path tests.
- Important APIs/types/functions: Executable Perl callback prints `1` and exits 0.
- Control flow: Ignores input and returns a constant version so path-case behavior is isolated from real VCS state.
- State and persistence behavior: No state is read or written.
- Dependencies and integration points: Depends only on Perl and version-script callback invocation.
- Risks: Constant versions can hide path-specific version behavior, intentionally.
- Test signals: Passing signal is stable version comparison across differently cased paths.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/lambda/Makefile -->
# sources/test-tools/lcov/tests/genhtml/lambda/Makefile

- Purpose: Makefile entry for `lambda.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/lambda/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/lambda/lambda.cpp -->
# sources/test-tools/lcov/tests/genhtml/lambda/lambda.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/lambda`.
- Important APIs/types/functions: Important declarations include: void f(int n1, int n2, int n3, const int& n4, int n5); int g(int n1); struct Foo; void print_sum(int n1, int n2); int data = 10;; int main(); int n = 7;; for (int n = 0; n < 10; ++n).
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/lambda/lambda.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/lambda/lambda.sh -->
# sources/test-tools/lcov/tests/genhtml/lambda/lambda.sh

- Purpose: Shell helper or test driver for `sources/test-tools/lcov/tests/genhtml/lambda`.
- Important APIs/types/functions: Executable script interface; local functions are absent or limited to driver helpers parsed by the script itself.
- Control flow: Parses optional test flags, invokes lcov/genhtml/compiler/helper commands, and checks results with exit codes, `grep`, `diff`, or generated file existence.
- State and persistence behavior: Creates transient logs, coverage files, binaries, and output directories named in its cleanup block or parent Makefile.
- Dependencies and integration points: Depends on `common.tst` where sourced, local fixtures, lcov/genhtml tools, compiler tools, and standard shell utilities.
- Risks: Risks are exact diagnostic greps, environment/tool availability, and stale cleanup lists.
- Test signals: Passing signals are successful expected commands and explicit grep/diff/file-existence assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/lambda/lambda.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/mycppfilt.sh -->
# sources/test-tools/lcov/tests/genhtml/mycppfilt.sh

- Purpose: Dummy C++ demangler replacement used to verify custom `genhtml --demangle-cpp` command and parameter passing.
- Important APIs/types/functions: Executable filter: skips leading options, chooses a prefix from remaining args or `aaa`, and rewrites `FN`/`FNDA` records with Perl.
- Control flow: Reads lcov records from stdin and prefixes function-name fields before exiting 0.
- State and persistence behavior: Streams stdin/stdout only; no files are written.
- Dependencies and integration points: Depends on bash regex matching, Perl substitution, and genhtml custom demangler invocation.
- Risks: Only `FN`/`FNDA` formats with commas are transformed, which is intentional for the fixture.
- Test signals: Passing signal is generated HTML containing prefixed function names.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/mycppfilt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/part1.sh -->
# sources/test-tools/lcov/tests/genhtml/part1.sh

- Purpose: Creates genhtml output for `partial coverage part 1` fixture data and validates summary counts and generated files.
- Important APIs/types/functions: No shell functions; accepts `--coverage` and `--verbose`, and relies on environment variables for input info files and expected counts.
- Control flow: Runs `$GENHTML $PART1INFO`, captures stdout/stderr, validates exit status and clean stderr, calls `check_counts` with `$PART1COUNTS`, and ensures HTML files exist.
- State and persistence behavior: Creates `out_part1` and stdout/stderr logs; source inputs are not modified.
- Dependencies and integration points: Depends on `$GENHTML`, mkinfo-provided trace/count variables, `check_counts`, Perl Devel::Cover filtering, and `find`.
- Risks: Fixture-data or genhtml stdout wording drift can break count checks while rendering still works.
- Test signals: Passing signals are matching counts, empty stderr outside coverage mode, and at least one generated `.html` file.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/part1.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/part2.sh -->
# sources/test-tools/lcov/tests/genhtml/part2.sh

- Purpose: Creates genhtml output for `partial coverage part 2` fixture data and validates summary counts and generated files.
- Important APIs/types/functions: No shell functions; accepts `--coverage` and `--verbose`, and relies on environment variables for input info files and expected counts.
- Control flow: Runs `$GENHTML $PART2INFO`, captures stdout/stderr, validates exit status and clean stderr, calls `check_counts` with `$PART2COUNTS`, and ensures HTML files exist.
- State and persistence behavior: Creates `out_part2` and stdout/stderr logs; source inputs are not modified.
- Dependencies and integration points: Depends on `$GENHTML`, mkinfo-provided trace/count variables, `check_counts`, Perl Devel::Cover filtering, and `find`.
- Risks: Fixture-data or genhtml stdout wording drift can break count checks while rendering still works.
- Test signals: Passing signals are matching counts, empty stderr outside coverage mode, and at least one generated `.html` file.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/part2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/relative/Makefile -->
# sources/test-tools/lcov/tests/genhtml/relative/Makefile

- Purpose: Makefile entry for `relative.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/relative/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/relative/relative.sh -->
# sources/test-tools/lcov/tests/genhtml/relative/relative.sh

- Purpose: Shell helper or test driver for `sources/test-tools/lcov/tests/genhtml/relative`.
- Important APIs/types/functions: Executable script interface; local functions are absent or limited to driver helpers parsed by the script itself.
- Control flow: Parses optional test flags, invokes lcov/genhtml/compiler/helper commands, and checks results with exit codes, `grep`, `diff`, or generated file existence.
- State and persistence behavior: Creates transient logs, coverage files, binaries, and output directories named in its cleanup block or parent Makefile.
- Dependencies and integration points: Depends on `common.tst` where sourced, local fixtures, lcov/genhtml tools, compiler tools, and standard shell utilities.
- Risks: Risks are exact diagnostic greps, environment/tool availability, and stale cleanup lists.
- Test signals: Passing signals are successful expected commands and explicit grep/diff/file-existence assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/relative/relative.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/Makefile -->
# sources/test-tools/lcov/tests/genhtml/simple/Makefile

- Purpose: Makefile entry for `script.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/annotate.sh -->
# sources/test-tools/lcov/tests/genhtml/simple/annotate.sh

- Purpose: Perl annotation callback used by genhtml tests to provide source line metadata and modification timestamps.
- Important APIs/types/functions: Defines `get_modify_time`; uses `POSIX::strftime` and, in the insensitive variant, path case matching helpers/modules.
- Control flow: Resolves the requested file, calculates modification time, reads source lines, normalizes carriage returns, and emits annotation records for genhtml.
- State and persistence behavior: Reads filesystem metadata and file contents; writes no persistent files except caller-controlled logs.
- Dependencies and integration points: Depends on Perl modules, file stat data, and genhtml annotate callback protocol.
- Risks: Timestamp and path-case sensitivity can affect version/annotation consistency checks.
- Test signals: Passing signals are expected annotation/owner/date data in generated reports or expected annotation failure diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/annotate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/script.sh -->
# sources/test-tools/lcov/tests/genhtml/simple/script.sh

- Purpose: Primary genhtml integration harness for differential coverage: capture, version mismatch, fail-under, baseline/current/differential reports, owner tables, navigation, filtering, selection, criteria callbacks, path elision, spreadsheets, and unreachable exclusions.
- Important APIs/types/functions: Procedural shell script driven by `common.tst` variables such as `LCOV_OPTS`, `DIFFCOV_OPTS`, annotation/version scripts, criteria/select/unreachable callbacks, compiler flags, and optional MCDC support.
- Control flow: Compiles baseline/current variants, captures and gzips traces, creates diffs, renders many genhtml modes, verifies lcov substitution/exclude/trivial filters, tests callback criteria/selection, and checks expected error/ignore paths.
- State and persistence behavior: Creates many `.info/.gz`, `.json`, `.xlsx`, diff files, logs, annotation outputs, coverage databases, linked-path directories, and report trees; cleanup removes the named artifacts.
- Dependencies and integration points: Depends on C/C++ compilers, lcov/genhtml/geninfo, optional py2lcov/perl2lcov paths, Python modules, local `annotate.sh`, and stable HTML text anchors.
- Risks: Broad environment sensitivity: compiler branch layouts, optional MCDC, path mismatch heuristics, exact HTML strings, and optional tool availability.
- Test signals: Passing signals include expected HTML/source files, owner and truncation text, navigation HIT/MISS counts, criteria diagnostics, fail-under output preservation, spreadsheet generation, and expected malformed-option warnings.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/simple.cpp -->
# sources/test-tools/lcov/tests/genhtml/simple/simple.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/simple`. It maps comments/macros to differential coverage categories.
- Important APIs/types/functions: Important declarations include: int; main(int ac, char ** av); int cond = 0;.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/simple.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/simple2.cpp -->
# sources/test-tools/lcov/tests/genhtml/simple/simple2.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/simple`. It maps comments/macros to differential coverage categories.
- Important APIs/types/functions: Important declarations include: int; main(int ac, char ** av); int cond = 0;.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/simple2.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/unreach.cpp -->
# sources/test-tools/lcov/tests/genhtml/simple/unreach.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/simple`. It maps comments/macros to differential coverage categories.
- Important APIs/types/functions: Important declarations include: int; main(int ac, char ** av); int cond = 0;.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/unreach.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/Makefile -->
# sources/test-tools/lcov/tests/genhtml/synthesize/Makefile

- Purpose: Makefile entry for `synthesize.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/munge.pl -->
# sources/test-tools/lcov/tests/genhtml/synthesize/munge.pl

- Purpose: Trace mutator injecting out-of-range line, function, and branch records to test synthesis of missing source metadata.
- Important APIs/types/functions: No subroutines; executable Perl filter from stdin to stdout over lcov `.info` records.
- Control flow: Line-oriented loop rewrites `LF/LH/FNH/FNF/BRF` counters and injects `DA`, `FN`, `FNDA`, and `BRDA` records.
- State and persistence behavior: No filesystem state directly; the harness redirects output to mutated traces.
- Dependencies and integration points: Depends on lcov info syntax and Perl regex processing; integrated by `synthesize.sh`.
- Risks: Intentional inconsistency can become invalid if parser validation changes.
- Test signals: Passing signal is downstream genhtml synthesis/warning behavior expected by `synthesize.sh`.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/munge.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/munge2.pl -->
# sources/test-tools/lcov/tests/genhtml/synthesize/munge2.pl

- Purpose: Trace mutator removing a line coverpoint for the first branch record to create branch-without-line data.
- Important APIs/types/functions: No subroutines; executable Perl filter from stdin to stdout over lcov `.info` records.
- Control flow: Tracks the first `BRDA` line, decrements `LF`, adjusts hit summaries, suppresses the matching `DA`, and passes other records through.
- State and persistence behavior: No filesystem state directly; the harness redirects output to mutated traces.
- Dependencies and integration points: Depends on lcov info syntax and Perl regex processing; integrated by `synthesize.sh`.
- Risks: Intentional inconsistency can become invalid if parser validation changes.
- Test signals: Passing signal is downstream genhtml synthesis/warning behavior expected by `synthesize.sh`.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/munge2.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/synthesize.sh -->
# sources/test-tools/lcov/tests/genhtml/synthesize/synthesize.sh

- Purpose: Genhtml synthesis regression harness for inconsistent trace data, including out-of-range lines and branches without line coverpoints.
- Important APIs/types/functions: Procedural shell script using common harness variables, local mutators `munge.pl` and `munge2.pl`, compiler tools, lcov, and genhtml.
- Control flow: Compiles/captures data, normalizes compiler differences, mutates traces, runs genhtml with source/filter options, and greps for synthesized labels or their absence.
- State and persistence behavior: Creates mutated `.info` files, logs, executable/coverage files, and report directories; cleanup removes them.
- Dependencies and integration points: Depends on `common.tst`, Perl mutators, gcc/gcov/lcov/genhtml, and stable synthesized-coverpoint wording.
- Risks: Intentional trace inconsistency and compiler-version differences require ignore categories and normalization.
- Test signals: Passing signals are expected generated labels, absence of prohibited labels, and successful branch-without-line handling.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/synthesize.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/target.sh -->
# sources/test-tools/lcov/tests/genhtml/target.sh

- Purpose: Creates genhtml output for `target-threshold coverage` fixture data and validates summary counts and generated files.
- Important APIs/types/functions: No shell functions; accepts `--coverage` and `--verbose`, and relies on environment variables for input info files and expected counts.
- Control flow: Runs `$GENHTML $TARGETINFO`, captures stdout/stderr, validates exit status and clean stderr, calls `check_counts` with `$TARGETCOUNTS`, and ensures HTML files exist.
- State and persistence behavior: Creates `out_target` and stdout/stderr logs; source inputs are not modified.
- Dependencies and integration points: Depends on `$GENHTML`, mkinfo-provided trace/count variables, `check_counts`, Perl Devel::Cover filtering, and `find`.
- Risks: Fixture-data or genhtml stdout wording drift can break count checks while rendering still works.
- Test signals: Passing signals are matching counts, empty stderr outside coverage mode, and at least one generated `.html` file.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/target.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/zero.sh -->
# sources/test-tools/lcov/tests/genhtml/zero.sh

- Purpose: Creates genhtml output for `zero coverage` fixture data and validates summary counts and generated files.
- Important APIs/types/functions: No shell functions; accepts `--coverage` and `--verbose`, and relies on environment variables for input info files and expected counts.
- Control flow: Runs `$GENHTML $ZEROINFO`, captures stdout/stderr, validates exit status and clean stderr, calls `check_counts` with `$ZEROCOUNTS`, and ensures HTML files exist.
- State and persistence behavior: Creates `out_zero` and stdout/stderr logs; source inputs are not modified.
- Dependencies and integration points: Depends on `$GENHTML`, mkinfo-provided trace/count variables, `check_counts`, Perl Devel::Cover filtering, and `find`.
- Risks: Fixture-data or genhtml stdout wording drift can break count checks while rendering still works.
- Test signals: Passing signals are matching counts, empty stderr outside coverage mode, and at least one generated `.html` file.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/zero.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/Makefile -->
# sources/test-tools/lcov/tests/lcov/Makefile

- Purpose: Makefile entry for `add/ misc/ summary/ extract/ demangle/ exception/ gcov-tool/ branch/ merge/ format errs multiple follow initializer lambda mcdc` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/add/Makefile -->
# sources/test-tools/lcov/tests/lcov/add/Makefile

- Purpose: Makefile entry for `prune.sh track.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/add/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/add/prune.sh -->
# sources/test-tools/lcov/tests/lcov/add/prune.sh

- Purpose: Shell helper or test driver for `sources/test-tools/lcov/tests/lcov/add`.
- Important APIs/types/functions: Executable script interface; local functions are absent or limited to driver helpers parsed by the script itself.
- Control flow: Parses optional test flags, invokes lcov/genhtml/compiler/helper commands, and checks results with exit codes, `grep`, `diff`, or generated file existence.
- State and persistence behavior: Creates transient logs, coverage files, binaries, and output directories named in its cleanup block or parent Makefile.
- Dependencies and integration points: Depends on `common.tst` where sourced, local fixtures, lcov/genhtml tools, compiler tools, and standard shell utilities.
- Risks: Risks are exact diagnostic greps, environment/tool availability, and stale cleanup lists.
- Test signals: Passing signals are successful expected commands and explicit grep/diff/file-existence assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/add/prune.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/add/track.sh -->
# sources/test-tools/lcov/tests/lcov/add/track.sh

- Purpose: Shell helper or test driver for `sources/test-tools/lcov/tests/lcov/add`.
- Important APIs/types/functions: Executable script interface; local functions are absent or limited to driver helpers parsed by the script itself.
- Control flow: Parses optional test flags, invokes lcov/genhtml/compiler/helper commands, and checks results with exit codes, `grep`, `diff`, or generated file existence.
- State and persistence behavior: Creates transient logs, coverage files, binaries, and output directories named in its cleanup block or parent Makefile.
- Dependencies and integration points: Depends on `common.tst` where sourced, local fixtures, lcov/genhtml tools, compiler tools, and standard shell utilities.
- Risks: Risks are exact diagnostic greps, environment/tool availability, and stale cleanup lists.
- Test signals: Passing signals are successful expected commands and explicit grep/diff/file-existence assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/add/track.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/branch/Makefile -->
# sources/test-tools/lcov/tests/lcov/branch/Makefile

- Purpose: Makefile entry for `branch.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/branch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/branch/branch.cpp -->
# sources/test-tools/lcov/tests/lcov/branch/branch.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/lcov/branch`. It stresses macro/template branch record layouts.
- Important APIs/types/functions: Important declarations include: template <unsigned v>; void func(bool a, bool b); int; main(int ac, char **av); bool a = ac > 1;; bool b = ac > 2;.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/branch/branch.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/branch/branch.sh -->
# sources/test-tools/lcov/tests/lcov/branch/branch.sh

- Purpose: Shell helper or test driver for `sources/test-tools/lcov/tests/lcov/branch`.
- Important APIs/types/functions: Executable script interface; local functions are absent or limited to driver helpers parsed by the script itself.
- Control flow: Parses optional test flags, invokes lcov/genhtml/compiler/helper commands, and checks results with exit codes, `grep`, `diff`, or generated file existence.
- State and persistence behavior: Creates transient logs, coverage files, binaries, and output directories named in its cleanup block or parent Makefile.
- Dependencies and integration points: Depends on `common.tst` where sourced, local fixtures, lcov/genhtml tools, compiler tools, and standard shell utilities.
- Risks: Risks are exact diagnostic greps, environment/tool availability, and stale cleanup lists.
- Test signals: Passing signals are successful expected commands and explicit grep/diff/file-existence assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/branch/branch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/Makefile -->
# sources/test-tools/lcov/tests/lcov/demangle/Makefile

- Purpose: Makefile entry for `demangle.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/demangle.cpp -->
# sources/test-tools/lcov/tests/lcov/demangle/demangle.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/lcov/demangle`. It stresses C++ symbol demangling and duplicate function records.
- Important APIs/types/functions: Important declarations include: class Animal; class Cat : public Animal; int main().
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/demangle.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/demangle.sh -->
# sources/test-tools/lcov/tests/lcov/demangle/demangle.sh

- Purpose: Lcov demangling regression harness for C++ symbols, duplicate function records, simplification callbacks, and function/branch counts.
- Important APIs/types/functions: Procedural shell script using `demangle.cpp`, `simplify.pl`, lcov/geninfo/genhtml tools, compiler settings, and shared ignore options.
- Control flow: Compiles/runs the fixture, captures traces under demangle and simplify configurations, counts branches/functions, checks demangled names, and compares filtered outputs.
- State and persistence behavior: Creates binaries, `.gcno/.gcda`, `.info`, logs, and genhtml output directories; clean removes them.
- Dependencies and integration points: Depends on C++ compiler mangling, lcov demangle support, optional genhtml rendering, Perl simplification, grep/sed normalization.
- Risks: Compiler variance in inline constructor/destructor records and duplicate function entries can affect counts.
- Test signals: Passing signals are expected counts, demangled names, and replacement names from the simplify callback.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/demangle.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/simplify.pl -->
# sources/test-tools/lcov/tests/lcov/demangle/simplify.pl

- Purpose: Small Perl helper script used by adjacent lcov/genhtml tests.
- Important APIs/types/functions: No reusable package API unless explicitly declared; executable behavior is line/argument oriented.
- Control flow: The parent harness invokes it as a callback/filter/helper and validates transformed output or diagnostics.
- State and persistence behavior: Usually streams stdin/stdout or prints a simple value; no standalone persistence.
- Dependencies and integration points: Depends on Perl and lcov/genhtml helper callback contracts.
- Risks: Regex or argument protocol changes can alter behavior.
- Test signals: Passing signal is the adjacent shell test observing the expected transformed names, records, or helper output.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/simplify.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/errs/Makefile -->
# sources/test-tools/lcov/tests/lcov/errs/Makefile

- Purpose: Makefile entry for `errs.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/errs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/errs/errs.sh -->
# sources/test-tools/lcov/tests/lcov/errs/errs.sh

- Purpose: Shell helper or test driver for `sources/test-tools/lcov/tests/lcov/errs`.
- Important APIs/types/functions: Executable script interface; local functions are absent or limited to driver helpers parsed by the script itself.
- Control flow: Parses optional test flags, invokes lcov/genhtml/compiler/helper commands, and checks results with exit codes, `grep`, `diff`, or generated file existence.
- State and persistence behavior: Creates transient logs, coverage files, binaries, and output directories named in its cleanup block or parent Makefile.
- Dependencies and integration points: Depends on `common.tst` where sourced, local fixtures, lcov/genhtml tools, compiler tools, and standard shell utilities.
- Risks: Risks are exact diagnostic greps, environment/tool availability, and stale cleanup lists.
- Test signals: Passing signals are successful expected commands and explicit grep/diff/file-existence assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/errs/errs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/exception/Makefile -->
# sources/test-tools/lcov/tests/lcov/exception/Makefile

- Purpose: Makefile entry for `exception.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/exception/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/exception/exception.cpp -->
# sources/test-tools/lcov/tests/lcov/exception/exception.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/lcov/exception`. It stresses exception branch capture/filtering.
- Important APIs/types/functions: Important declarations include: int; main(int ac, char **av); int branch(0);.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/exception/exception.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/exception/exception.sh -->
# sources/test-tools/lcov/tests/lcov/exception/exception.sh

- Purpose: Lcov exception branch filtering harness validating marker-based and option-based removal of exception branches, intermediate format needs, strict ordering, and filter combinations.
- Important APIs/types/functions: Procedural shell script using capture command forms, branch/filter options, `ENABLE_MCDC`, compiler gates, and common harness variables.
- Control flow: Compiles/runs `exception.cpp`, captures traces, checks branch counts, applies filters with and without markers, exercises ignore paths and strict ordering, and compares outputs.
- State and persistence behavior: Creates executable, coverage files, `.info`, logs, and filtered traces; clean removes them.
- Dependencies and integration points: Depends on lcov/geninfo branch capture, marker parser support, compiler coverage layout, and checked example data.
- Risks: Old compiler branch inconsistencies and intermediate-format requirements can change expected behavior.
- Test signals: Passing signals are expected branch count changes, marker diagnostics, and strict-ordering behavior matching greps/diffs.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/exception/exception.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/Makefile -->
# sources/test-tools/lcov/tests/lcov/extract/Makefile

- Purpose: Makefile entry for `extract.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/brokenCallback.pm -->
# sources/test-tools/lcov/tests/lcov/extract/brokenCallback.pm

- Purpose: Perl callback fixture for negative or specialized lcov/genhtml callback-path testing in `sources/test-tools/lcov/tests/lcov/extract`.
- Important APIs/types/functions: Defines package `brokenCallback` with methods: new, resolve.
- Control flow: The harness loads it through lcov/genhtml callback options so selected methods either provide synthetic data or deliberately fail to validate diagnostics.
- State and persistence behavior: State is held in blessed constructor arguments where present; modules write no persistent files themselves.
- Dependencies and integration points: Depends on Perl callback loading and the lcov/genhtml callback protocol; integrated by nearby shell tests.
- Risks: API drift in callback method names or diagnostic formatting can change the targeted failure mode.
- Test signals: Passing signal is the parent shell script observing the expected callback result, warning, or failure message.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/brokenCallback.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/extract.cpp -->
# sources/test-tools/lcov/tests/lcov/extract/extract.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/lcov/extract`. It contains many custom marker comments for exclusion, unreachable, region, and omit-line tests.
- Important APIs/types/functions: Important declarations include: int main(int argc, const char *argv[]) // TEST_UNREACH_FUNCTION; bool b = false;.
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/extract.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/extract.sh -->
# sources/test-tools/lcov/tests/lcov/extract/extract.sh

- Purpose: Comprehensive lcov capture/extract harness covering initial/all capture, external/internal files, unreachable tags, criteria/history/context callbacks, marker overrides, omit-lines, checksum validation, GCOV_PREFIX resolution, missing-source filtering, and filenames with spaces.
- Important APIs/types/functions: Procedural shell script using `LCOV_OPTS`, `CAPTURE`, compiler gates, filter variables, and helper scripts `fakeResolve.sh`, `history.sh`, `testContext.sh`, and `brokenCallback.pm`.
- Control flow: Compiles linked and unused sources, performs initial/current/all captures, lists and diffs outputs, validates callbacks/config/env expansion, checks marker errors, checksum mismatch, unreachable removal, separated gcno/gcda paths, and missing-source resolution.
- State and persistence behavior: Creates many `.info`, `.json`, `.log`, `.msg`, config files, executables, separated work directories, coverage data, and temporary files; the top cleanup block is the persistence boundary.
- Dependencies and integration points: Depends on common test harness, compilers, lcov/geninfo, checked gold list files, local helper callbacks, shell utilities, and filesystem permission/path behavior.
- Risks: Risks include compiler coverpoint count changes, unreadable-directory permissions, environment-variable config expansion, paths with spaces, and exact diagnostics.
- Test signals: Passing signals are gold list diffs, context JSON/comment fields, marker messages, omit-line counts, checksum failures, GCOV_PREFIX-equivalent traces, missing-source retain/remove checks, and space-containing filename capture.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/extract.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/fakeResolve.sh -->
# sources/test-tools/lcov/tests/lcov/extract/fakeResolve.sh

- Purpose: Resolve helper for separated gcno/gcda extraction tests; echoes its first argument unchanged.
- Important APIs/types/functions: Executable `/bin/sh` script with `printf '%s\n' "$1"` behavior.
- Control flow: Called by lcov `--resolve-script` to provide a deterministic resolved path.
- State and persistence behavior: No persistent state; stdout only.
- Dependencies and integration points: Depends on `/bin/sh` and lcov resolve-script invocation.
- Risks: Assumes the first argument is the desired path.
- Test signals: Passing signal is `resolve.info` matching the reference trace.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/fakeResolve.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/history.sh -->
# sources/test-tools/lcov/tests/lcov/extract/history.sh

- Purpose: Trivial history callback for option plumbing tests.
- Important APIs/types/functions: Executable `/bin/sh` script prints an empty line.
- Control flow: Provides minimal successful callback output so callers reach the intended validation path.
- State and persistence behavior: No persistent state.
- Dependencies and integration points: Depends only on `/bin/sh` and history callback invocation.
- Risks: Future protocols may require structured output.
- Test signals: Passing signal is callers proceeding beyond helper execution.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/history.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/testContext.sh -->
# sources/test-tools/lcov/tests/lcov/extract/testContext.sh

- Purpose: Shell context callback that emits user and multiline context data or fails deliberately.
- Important APIs/types/functions: If first arg is `die`, prints `dying` and exits 1; otherwise prints `USERNAME` and three `MULTILINE` records.
- Control flow: Used through `--context` to validate shell callback parsing, failure handling, and `--ignore callback`.
- State and persistence behavior: Reads current user via `whoami`; writes context records to stdout.
- Dependencies and integration points: Depends on `/bin/sh`, `whoami`, and lcov context parsing.
- Risks: Username/environment variance can affect exact context content.
- Test signals: Passing signals are context JSON/comment fields and expected failure/ignored-failure behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/testContext.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/unused.c -->
# sources/test-tools/lcov/tests/lcov/extract/unused.c

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/lcov/extract`. It contains many custom marker comments for exclusion, unreachable, region, and omit-line tests.
- Important APIs/types/functions: Important declarations include: void f(int y).
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/unused.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/follow/Makefile -->
# sources/test-tools/lcov/tests/lcov/follow/Makefile

- Purpose: Makefile entry for `follow.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/follow/Makefile -->
