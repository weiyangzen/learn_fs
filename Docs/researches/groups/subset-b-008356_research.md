# subset-b-008356 research

Grouped research report for the SELinux CIL AST writer and unit/integration harness files. Each file section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_write_ast.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_write_ast.c

## Purpose
`cil_write_ast.c` serializes CIL parse/build/resolve/post AST trees back to human-readable CIL-like text. It is a diagnostic and introspection layer over the CIL tree and datum structures rather than a policy compiler stage that mutates policy state. Its output is phase-sensitive: parse-phase output preserves parse tree structure and quoting, while later phases emit semantic CIL forms from typed `struct cil_*` payloads.

## Important APIs, Types, And Functions
The public entry points are `cil_write_ast_node(FILE *out, struct cil_tree_node *node)` and `cil_write_ast(FILE *out, enum cil_write_ast_phase phase, struct cil_tree_node *node)`. `cil_write_ast_node` handles a single typed AST node through a large `node->flavor` switch, and `cil_write_ast` drives `cil_tree_walk()` with phase-specific callbacks.

Important local helpers include `datum_or_str()` and `datum_to_str()` for resolved datum names versus saved source strings; `write_expr()` for CIL expression lists; `write_classperms()` and `write_classperms_list()` for class/permission groups and classpermission sets; `write_permx()` for ioctl/nlmsg extended permissions; `write_level()`, `write_range()`, `write_context()`, and `write_ipaddr()` for MLS/security context values; `write_constrain()` for constraint expression bodies; and `write_call_args()` / `write_call_args_tree()` for resolved and parse-tree macro call arguments.

The switch covers policy declaration, conditional, macro, access-vector rule, type/role/user, MLS, labeling, network, hardware, filesystem, and capability node flavors. Examples include `CIL_BLOCK`, `CIL_MACRO`, `CIL_CALL`, `CIL_MLS`, `CIL_DEFAULTUSER`, `CIL_CLASS`, `CIL_CLASSPERMISSIONSET`, `CIL_PERMISSIONX`, `CIL_SIDCONTEXT`, `CIL_BOOL`, `CIL_LEVELRANGE`, `CIL_USERATTRIBUTESET`, `CIL_AVRULE`, `CIL_AVRULEX`, `CIL_TYPE_RULE`, `CIL_NAMETYPETRANSITION`, `CIL_CONSTRAIN`, `CIL_FILECON`, `CIL_PORTCON`, `CIL_NODECON`, `CIL_GENFSCON`, `CIL_FSUSE`, `CIL_POLICYCAP`, and `CIL_IPADDR`.

## Control Flow
For parse phase, `cil_write_ast()` calls `cil_tree_walk()` with parse callbacks. The node callback indents by `depth`, prints `(` or `()` for data-less grouping nodes, quotes parse tokens containing whitespace, and otherwise prints the token as-is. First-child and last-child callbacks adjust indentation and emit closing parentheses.

For build/resolve/post phases, `cil_write_ast()` uses CIL callbacks. The node callback specially handles `CIL_SRC_INFO` by emitting `;;* lms`, `;;* lmx`, and `;;* lme` source mapping markers; other nodes are indented and passed to `cil_write_ast_node()`. The first/last child callbacks increase indentation for nested constructs except root and source-info wrappers, and print closing parens for compound forms. Class/common/map-class nodes set `CIL_TREE_SKIP_HEAD` because their permission children are emitted inline by `write_node_list()`.

`cil_write_ast_node()` mostly prints one balanced CIL form per node, with child-bearing forms leaving the closing parenthesis for the tree-walk last-child callback. Helpers choose between resolved datum pointers and unresolved string fields so the writer can represent partially resolved ASTs as well as post-resolution trees.

## State And Persistence
The file does not own durable state. It reads AST node payloads, list contents, datum names, source-location metadata, and resolved/unresolved string fields, then writes to the caller-provided `FILE *out`. It does not allocate persistent objects or mutate the CIL database. The only state it maintains is traversal indentation in `struct cil_write_ast_args`.

## Dependencies And Integration Points
It depends on CIL internals from `cil_internal.h`, flavor constants from `cil_flavor.h`, list traversal from `cil_list.h`, logging from `cil_log.h`, symbol datum shape from `cil_symtab.h`, tree walking from `cil_tree.h`, and its public declarations in `cil_write_ast.h`. It also relies on policy constants such as `SEPOL_OK`, `SEPOL_ERR`, `SEPOL_ALLOW_UNKNOWN`, `AVRULE_ALLOWED`, and related rule kind values.

Integration is centered on `cil_tree_walk()` and the shape of every `struct cil_*` payload referenced by `node->flavor`. New CIL AST node flavors or new enum values require serializer updates here or they fall into placeholder output such as `<?RULE:...>`, `<?OP>`, `<?DEFAULT>`, `<?PROTOCOL>`, or `<?FILETYPE>`.

## Risks
The main correctness risk is drift between parser/build/resolution structures and the serializer switch. Because the file has many manual format branches, a new node field or enum value can silently produce placeholder text or malformed CIL. Some string fields are printed directly and some are quoted, so caller invariants around stored strings matter for round-trip readability. `write_call_args()` appears to emit an extra trailing space for declared string arguments, which may be harmless but can complicate exact output comparisons. `inet_ntop()` failures degrade to `<?IPADDR>`, which is useful diagnostically but not valid policy syntax.

## Test Signals
This subset does not include direct unit tests for `cil_write_ast.c`. Indirect signals come from the broad CIL build/resolve/copy/integration tests registered in `CilTest.c`, especially tests for macros, constraints, contexts, MLS constructs, labeling rules, IP addresses, and extended permissions. Stronger direct tests would compare parse/build/resolve writer output for representative nodes, unresolved string fallback paths, source-info marker handling, and unsupported enum fallback markers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_write_ast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_write_ast.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_write_ast.h

## Purpose
`cil_write_ast.h` exposes the CIL AST writer interface used by code that needs to dump parse/build/resolve/post AST state to a `FILE *`. It is the small public contract for `cil_write_ast.c`.

## Important APIs, Types, And Functions
The header defines `enum cil_write_ast_phase` with `CIL_WRITE_AST_PHASE_PARSE`, `CIL_WRITE_AST_PHASE_BUILD`, `CIL_WRITE_AST_PHASE_RESOLVE`, and `CIL_WRITE_AST_PHASE_POST`. It declares `void cil_write_ast_node(FILE *out, struct cil_tree_node *node)` for one-node serialization and `int cil_write_ast(FILE *out, enum cil_write_ast_phase phase, struct cil_tree_node *node)` for whole-tree traversal.

## Control Flow
This header contains no executable flow. Its enum values drive the branch in `cil_write_ast()` that selects parse-tree callbacks versus semantic CIL callbacks.

## State And Persistence
No state is stored here. Callers provide the output stream and tree node. The implementation writes to the stream and returns `SEPOL_OK`/`SEPOL_ERR` for whole-tree operations.

## Dependencies And Integration Points
The header includes `<stdio.h>` for `FILE` and `cil_tree.h` for `struct cil_tree_node`. Any caller including this file gets the AST writer phase enum and can request dumps without depending on private serializer helpers.

## Risks
The enum is an ABI/API coordination point with the implementation. Adding a new phase requires corresponding behavior in `cil_write_ast.c`; otherwise it will use the non-parse path. The header does not document ownership, null handling, or output syntax guarantees, so callers must follow implementation conventions.

## Test Signals
Compile-time coverage comes from any CIL component or test harness that includes the header. Functional validation depends on tests that call `cil_write_ast()` and verify emitted text.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_write_ast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/integration_testing/nonmls.conf -->
# sources/security-integrity/selinux/libsepol/cil/test/integration_testing/nonmls.conf

## Purpose
`nonmls.conf` is a compact non-MLS SELinux policy fixture used by integration tests. It exercises baseline declarations and rules without MLS level/range syntax.

## Important Declarations
The fixture declares `class testing` and `class fooclass`, `sid test_sid` and `sid security`, permission sets for both classes, one attribute `attrs`, types `foo_t`, `typea_t`, `typeb_t`, and `typec_t`, booleans `foo_b` and `baz_b`, roles `foo_r`, `rolea_r`, and `roleb_r`, allow rules, a `type_transition`, a role allow, user `foo_u`, and a final SID context `foo_u:foo_r:foo_t`.

## Control Flow
This is declarative policy input, not procedural code. The integration test flow parses this file, translates declarations and rules into CIL/policy structures, and checks that a minimal non-MLS policy can be accepted.

## State And Persistence
The file is static test data. Its state is the policy text persisted in the repository. The test harness reads it as input and does not update it.

## Dependencies And Integration Points
It depends on the legacy policy syntax expected by the integration pipeline. It integrates with the CIL integration test fixtures under `test/integration_testing` and with test registrations from `CilTestFullCil()`.

## Risks
Because this fixture intentionally omits MLS details, it cannot catch MLS serializer/resolver regressions. It also contains commented-out examples and section markers such as `#end`, so tests must treat comments as comments and not assume every visible line is active policy. Any parser syntax change affecting non-MLS policy declarations, allow rules, role rules, or SID contexts may break this fixture.

## Test Signals
A passing integration run using this fixture signals that basic class, SID, type, attribute, bool, role, allow, type transition, user, and SID context handling still works for non-MLS input.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/integration_testing/nonmls.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/AllTests.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/AllTests.c

## Purpose
`AllTests.c` is the executable entry point for the CIL unit and integration test binary. It creates CuTest suites, imports suite factories from `CilTest.c`, runs them, and prints combined details and summaries.

## Important APIs, Types, And Functions
The file declares suite factories `CilTreeGetSuite()`, `CilTreeGetResolveSuite()`, `CilTreeGetBuildSuite()`, and `CilTestFullCil()`. `RunAllTests()` disables CIL log output with `cil_set_log_level(0)`, creates a shared `CuString` output buffer, creates four `CuSuite` objects, adds generated suites into those objects with `CuSuiteAddSuite()`, runs each suite, appends details and summary, and prints the result. `main()` simply calls `RunAllTests()` and exits with `0`.

## Control Flow
The test binary always runs the base suite, resolve suite, build suite, and integration suite in sequence. For each suite it calls `CuSuiteRun()`, `CuSuiteDetails()`, and `CuSuiteSummary()`, appending into one output string. The process return code does not reflect failures because `main()` always returns `0`.

## State And Persistence
Runtime state is limited to in-memory CuTest suites and one `CuString` buffer. The file suppresses CIL logging globally for the process. It does not persist test results except to stdout.

## Dependencies And Integration Points
It depends on `CuTest.h` for the test framework and `../../src/cil_log.h` for log-level control. It integrates all suite registration functions from `CilTest.c` into one binary.

## Risks
Always returning `0` can hide failures from build systems that rely only on process status rather than parsing stdout. The suites allocated by `CuSuiteNew()` and `CuStringNew()` are not deleted before process exit, which is acceptable for a short-lived test binary but noisy under leak checkers. Log suppression may hide useful diagnostics when investigating failing tests.

## Test Signals
The output contains CuTest details and dot/F summaries for base, resolve, build, and integration suites. Any failure is visible in stdout details, not in the exit status.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/AllTests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/CilTest.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/CilTest.c

## Purpose
`CilTest.c` is the central CIL test-suite registry and shared fixture helper file. It collects tests from many `test_cil_*` modules into CuTest suites for base utilities, AST build behavior, AST resolve behavior, copy/post behavior, and full integration.

## Important APIs, Types, And Functions
Shared helpers include `set_cil_file_data()` and `gen_test_tree()`. `set_cil_file_data()` reads `test/policy.cil` into a newly allocated `struct cil_file_data` buffer with two trailing NUL bytes. `gen_test_tree()` builds a simple `struct cil_tree` from a NULL-terminated token array, interpreting `"("` as descent into a new parse node, `")"` as ascent, and other tokens as parse-node data strings.

Local tests `test_symtab_init()` and `test_symtab_init_no_table_neg()` directly exercise `symtab_init()` using `cil_sym_sizes`. Suite factories are `CilTreeGetResolveSuite()`, `CilTreeGetBuildSuite()`, `CilTreeGetSuite()`, and `CilTestFullCil()`. The file contains 1,583 `SUITE_ADD_TEST` registrations, making it the authoritative map from test functions in included headers to executable CuTest suites.

## Control Flow
Each suite factory creates a `CuSuite` with `CuSuiteNew()`, registers test functions with `SUITE_ADD_TEST`, and returns the suite. `CilTreeGetResolveSuite()` focuses on name resolution, expression evaluation, optional/macro/call handling, conditionals, constraints, MLS structures, contexts, labeling, networking, hardware contexts, filesystem use, and symbol resolution negative paths. `CilTreeGetBuildSuite()` focuses on parsing/building AST nodes from syntax, including malformed input cases. `CilTreeGetSuite()` focuses on lower-level utilities, copy helpers, post-sort comparators, lexer/parser/FQN/list/tree/symtab behavior, and common copy regressions. `CilTestFullCil()` registers `test_min_policy` and `test_integration`.

## State And Persistence
The file allocates memory for helper structures and suites but does not persist test data. `set_cil_file_data()` depends on the current working directory containing `test/policy.cil`. `gen_test_tree()` allocates tree nodes and duplicated strings for tests to consume.

## Dependencies And Integration Points
The file includes CuTest, CIL internals, libsepol policydb headers, and a broad set of local test headers such as `test_cil_tree.h`, `test_cil_list.h`, `test_cil_symtab.h`, `test_cil_parser.h`, `test_cil_lexer.h`, `test_cil_build_ast.h`, `test_cil_resolve_ast.h`, `test_cil_fqn.h`, `test_cil_copy_ast.h`, `test_cil_post.h`, and `test_integration.h`. It is consumed by `AllTests.c`.

## Risks
The registry is manually maintained. A test function can exist but never run if it is omitted, commented out, or hidden behind a stale include. The high number of registrations makes merge conflicts and accidental duplicate/missing tests likely. `set_cil_file_data()` exits the process on file/stat/read errors, which is direct but prevents normal CuTest failure reporting. Several tests are commented out, documenting known gaps in negative/error-path coverage.

## Test Signals
The file itself is the primary test signal for CIL coverage breadth. It includes positive and negative cases for AST construction, resolution, macro expansion, conditionals, constraints, contexts, access-vector rules, MLS categories and levels, network and filesystem contexts, copy behavior, and post-processing comparators. Coverage is broad but depends on `AllTests.c` running the suites and on consumers checking stdout failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/CilTest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/CilTest.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/CilTest.h

## Purpose
`CilTest.h` declares shared fixtures used by CIL unit tests. It keeps helper data and tree-construction APIs available across individual `test_cil_*` modules.

## Important APIs, Types, And Functions
The header defines `struct cil_file_data` with `char *buffer` and `uint32_t file_size`, matching the buffer returned by `set_cil_file_data()`. It declares `set_cil_file_data(struct cil_file_data **)` and `gen_test_tree(struct cil_tree **, char **)`.

## Control Flow
There is no executable flow in the header. Tests include it to call helper functions implemented in `CilTest.c`.

## State And Persistence
The declared `struct cil_file_data` describes in-memory file contents. Ownership rules are not documented in the header; callers need to know that the implementation allocates both the struct and its buffer.

## Dependencies And Integration Points
It includes `../../src/cil_tree.h` for `struct cil_tree`. It integrates with the unit-test helper implementation in `CilTest.c` and any test module needing synthetic parse trees or policy file buffers.

## Risks
The header uses `uint32_t` without directly including `<stdint.h>`, relying on included CIL headers to provide it. The helper prototypes omit parameter names and ownership documentation, increasing the chance of leaks or misuse in tests.

## Test Signals
Use of this header signals tests that need shared CIL tree/file fixtures rather than isolated assertions.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/CilTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/CuTest.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/CuTest.c

## Purpose
`CuTest.c` implements the lightweight CuTest 1.5 unit test framework vendored for the CIL tests. It supplies dynamic strings, test case execution, assertion failure reporting, and suite aggregation.

## Important APIs, Types, And Functions
String helpers include `CuStrAlloc()`, `CuStrCopy()`, `CuStringInit()`, `CuStringNew()`, `CuStringDelete()`, `CuStringResize()`, `CuStringAppend()`, `CuStringAppendChar()`, `CuStringAppendFormat()`, and `CuStringInsert()`.

Test-case helpers include `CuTestInit()`, `CuTestNew()`, `CuTestDelete()`, `CuTestRun()`, `CuFailInternal()`, `CuFail_Line()`, and assertion implementations for boolean, string, int, double, and pointer comparisons. Suite helpers include `CuSuiteInit()`, `CuSuiteNew()`, `CuSuiteDelete()`, `CuSuiteAdd()`, `CuSuiteAddSuite()`, `CuSuiteRun()`, `CuSuiteSummary()`, and `CuSuiteDetails()`.

## Control Flow
`CuTestRun()` installs a `jmp_buf`, marks a test as run, and invokes the test function. Assertion failures call `CuFailInternal()`, which prefixes file/line information, stores the message, marks the test failed, and uses `longjmp()` to stop the test. `CuSuiteRun()` iterates suite entries and increments `failCount` for failed tests. Summary output emits one `.` or `F` per test; details output either reports `OK` or lists numbered failures with messages and run/pass/fail totals.

## State And Persistence
All state is in allocated `CuString`, `CuTest`, and `CuSuite` structures. Failure messages point into allocated `CuString` buffers that are intentionally retained for reporting. No persistent files are written.

## Dependencies And Integration Points
The implementation uses `assert`, `setjmp`, `stdlib`, `stdio`, `string`, and `math`, and exposes its API through `CuTest.h`. It is used by `AllTests.c`, `CilTest.c`, and individual CIL test files.

## Risks
`CuStringAppendFormat()` uses `vsprintf()` into a fixed `HUGE_STRING_LEN` buffer, which is a classic overflow risk if a very long formatted message is produced. `CuSuiteAdd()` enforces `MAX_TEST_CASES` with `assert()`, so release builds with `NDEBUG` could write past the fixed suite array. `CuSuiteAddSuite()` transfers test pointers without freeing the container suite, so ownership is simple but can leak containers in short-lived binaries. Failure control flow relies on `setjmp`/`longjmp`, so test code with cleanup requirements can leak unless structured carefully.

## Test Signals
The framework reports visible stdout summaries and failure details. It has no self-tests in this subset; confidence comes from its small stable implementation and use by the broader CIL test harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/CuTest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/CuTest.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/CuTest.h

## Purpose
`CuTest.h` is the public header for the vendored CuTest framework. It defines test, suite, and assertion APIs used by all CIL unit tests.

## Important APIs, Types, And Functions
The header defines `CUTEST_VERSION`, allocation/string constants, `CuString`, `CuTest`, `TestFunction`, and `CuSuite`. It declares string helpers, test lifecycle functions, assertion backends, and suite lifecycle/run/report functions. Public assertion macros wrap backend functions with `__FILE__` and `__LINE__`. `SUITE_ADD_TEST(SUITE, TEST)` creates a named test case from the function symbol and adds it to a suite.

## Control Flow
There is no executable flow in the header, but macros shape test execution. Assertion macros capture file/line at the call site. `SUITE_ADD_TEST` stringizes the test function name and passes the function pointer to `CuTestNew()`.

## State And Persistence
The declared structures hold in-memory string buffers, test function pointers, failure flags, failure messages, jump buffers, suite arrays, and failure counts. `MAX_TEST_CASES` fixes suite capacity at 1024 entries per suite.

## Dependencies And Integration Points
It includes `<setjmp.h>` and `<stdarg.h>`. It relies on consumers or `CuTest.c` including allocation declarations for `malloc` when using `CU_ALLOC`. CIL test files include this header directly to define tests and assertions.

## Risks
The fixed `MAX_TEST_CASES` limit can be exceeded by large suites, and the enforcement is in the C implementation assertion rather than in the macro. `CU_ALLOC` expands to `malloc` without including `<stdlib.h>` in the header. The header declares `CuStringRead()` but this subset's `CuTest.c` does not implement it, so using that declaration would create a link failure.

## Test Signals
Tests using this header produce CuTest-compatible assertion failures with file and line context. The broad use of `SUITE_ADD_TEST` in `CilTest.c` is the main integration signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/CuTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil.c

## Purpose
`test_cil.c` contains focused unit tests for core CIL database and symbol-table selection behavior. It validates initialization and `cil_get_symtab()` routing for several AST parent flavors and negative inputs.

## Important APIs, Types, And Functions
The tests call `cil_symtab_array_init()`, `cil_db_init()`, `cil_tree_node_init()`, and `cil_get_symtab()`. Test functions include `test_cil_symtab_array_init()`, `test_cil_db_init()`, `test_cil_get_symtab_block()`, `test_cil_get_symtab_class()`, `test_cil_get_symtab_root()`, `test_cil_get_symtab_flavor_neg()`, `test_cil_get_symtab_null_neg()`, `test_cil_get_symtab_node_null_neg()`, and `test_cil_get_symtab_parent_null_neg()`.

## Control Flow
Each test allocates or initializes a minimal `struct cil_db` and/or `struct cil_tree_node`, configures parent flavor and line fields, calls the target API, and asserts `SEPOL_OK` or `SEPOL_ERR` plus expected pointer state. Positive `cil_get_symtab()` cases cover block, class, and root parent flavors. Negative cases cover invalid flavor, null parent, null node, and parent-null paths.

## State And Persistence
The tests allocate in-memory CIL database and tree-node objects. They do not write files or persistent state. Some tests free manually allocated `struct cil_db` memory, while `test_cil_db_init()` does not clean up the created database before returning.

## Dependencies And Integration Points
The file includes libsepol policydb headers, `CuTest.h`, its own `test_cil.h`, and CIL internal/tree headers. `CilTest.c` registers these functions in `CilTreeGetSuite()`.

## Risks
The tests are useful smoke coverage but not exhaustive. A TODO notes that the `SEPOL_ERR` path in `cil_db_init()` is not reached. Some initialized databases and nodes are not destroyed, which is acceptable for short unit runs but limits leak-check cleanliness. The positive class case requests `CIL_SYM_BLOCKS`, so it validates current routing behavior but may be surprising if symbol routing is refactored.

## Test Signals
Passing tests signal that basic CIL database initialization creates AST/symtab structures and that `cil_get_symtab()` handles common parent flavors and null/error paths consistently.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil.h

## Purpose
`test_cil.h` declares the core CIL unit test functions implemented in `test_cil.c` so the suite registry can add them.

## Important APIs, Types, And Functions
The header declares CuTest-style functions for symbol table array initialization, database initialization, positive `cil_get_symtab()` lookup paths, and negative `cil_get_symtab()` inputs. It also declares `test_cil_symtab_array_init_null_symtab_neg(CuTest *)`, which is not implemented in the paired `test_cil.c` in this subset and is not registered in `CilTest.c`.

## Control Flow
There is no executable flow. The prototypes are consumed by `CilTest.c` at compile time for suite registration and by the compiler for function type checking.

## State And Persistence
No state is stored in this header. Test state is owned by the implementations.

## Dependencies And Integration Points
It includes `CuTest.h` for the `CuTest` type. It integrates `test_cil.c` with the central suite factory in `CilTest.c`.

## Risks
The stale-looking declaration for `test_cil_symtab_array_init_null_symtab_neg()` can mislead maintainers or cause link errors if registered without an implementation. The header has no include of CIL internals because all test functions expose only the CuTest signature.

## Test Signals
Presence of these prototypes indicates that core CIL initialization and symbol-table lookup tests are intended to be part of the base suite.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil.h -->
