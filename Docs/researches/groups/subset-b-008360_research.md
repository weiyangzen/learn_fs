# subset-b-008360 research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.h

## Purpose
This header is the public declaration surface for the CIL build-AST unit tests. It does not implement logic itself; it exposes hundreds of `CuTest` entry points used by `CilTest.c` to register parser-list conversion, CIL datum generation, AST traversal, and negative validation tests for `libsepol/cil` internals.

## Important APIs, Types, And Functions
The only external type used directly is `CuTest` from `CuTest.h`. All declarations are `void test_...(CuTest *)` functions. The declared surface groups around `cil_parse_to_list`, `cil_set_to_list`, datum generators such as `cil_gen_block`, `cil_gen_class`, `cil_gen_type`, `cil_gen_context`, `cil_gen_filecon`, `cil_gen_portcon`, `cil_gen_nodecon`, `cil_gen_macro`, `cil_gen_call`, `cil_gen_optional`, and AST helper tests such as `test_cil_build_ast_node_helper_*` and `test_cil_build_ast_last_child_helper`.

## Control Flow
Control flow is indirect. `CilTest.c` includes this header, creates a CuTest suite, and registers selected declarations with `SUITE_ADD_TEST`. At runtime each registered function builds synthetic CIL token/list trees, invokes the corresponding CIL generator or AST helper, and asserts `SEPOL_OK` or `SEPOL_ERR`.

## State And Persistence
The header owns no runtime state and has no persistence behavior. Its state impact is compile-time: it defines which test functions other translation units may call. Because the implementations exercise mutable `cil_db`, AST nodes, symbol tables, and generated CIL datums, stale or missing declarations can break suite wiring even though the header stores nothing itself.

## Dependencies And Integration Points
It depends only on `CuTest.h` but names tests for internals implemented in `test_cil_build_ast.c` and registered mainly in `CilTest.c` under the build suite. It is tightly coupled to private CIL parser/build APIs because the implementation reaches functions such as CIL generators and AST helper paths rather than public libsepol APIs.

## Risks
The header is very broad and manually maintained, so declaration drift is a risk when tests are renamed or removed. Many negative-case declarations encode expected parser arity and shape validation; changing CIL grammar or AST node flavors requires synchronized updates to implementation and suite registration. The size of the declaration list also makes missing registrations easy to overlook.

## Test Signals
Positive signals include broad coverage of grammar constructs, context/range/IP parsing, macro/call/optional constructs, and top-level `cil_build_ast` error handling. Negative signals are especially strong for null arguments, missing operands, sublists where atoms are expected, extra operands, invalid protocols/classes, and duplicate or malformed AST helper cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_copy_ast.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_copy_ast.c

## Purpose
This file unit-tests CIL AST copy behavior. It verifies direct copy helpers for lists and individual CIL datum types, plus the internal `__cil_copy_node_helper` traversal path used to copy generated AST nodes into another destination tree or merge them into the same database.

## Important APIs, Types, And Functions
The file includes `CuTest.h`, `CilTest.h`, `cil_internal.h`, `cil_copy_ast.h`, `cil_build_ast.h`, and `cil_resolve_ast.h`. It forward-declares `__cil_copy_node_helper`, defines `struct cil_args_copy { struct cil_tree_node *dest; struct cil_db *db; }`, and provides `gen_copy_args`. Direct tests cover `cil_copy_list`, `cil_copy_block`, `cil_copy_perm`, `cil_copy_class`, `cil_copy_common`, `cil_copy_classcommon`, `cil_copy_sid`, `cil_copy_sidcontext`, user/role/type/boolean/MLS constructs, context and IP helpers, network/file policy constructs, conditional expressions, boolif, constrain, call, and optional. Helper tests cover many `CIL_*` node flavors, duplicate handling, merge behavior, null origin, and null extra-argument failures.

## Control Flow
Most tests build a small token tree with `gen_test_tree`, initialize a `cil_db` and `cil_tree_node`, call a `cil_gen_*` builder to populate `test_ast_node->data`, initialize a destination object or symbol table, and call the matching `cil_copy_*` function. Assertions check return code and selected field equality. Node-helper tests first run `cil_build_ast`, then call `__cil_copy_node_helper` with a destination root or parent node and assert both `finished` and status.

## State And Persistence
The tests allocate mutable CIL objects, symbol tables, AST roots, and list nodes in memory only. There is no file persistence. State risk is concentrated in ownership and aliasing: copy helpers duplicate some structures while intentionally preserving string values and symbolic references. Some tests merge into the same DB to exercise duplicate-detection semantics.

## Dependencies And Integration Points
This file is registered by `CilTest.c` in the tree suite. It integrates with CIL parser-test helpers from `CilTest.h`, CIL build functions that turn synthetic parse trees into AST datums, symbol table initialization from libsepol, and internal copy APIs not normally exposed as public application APIs.

## Risks
Several tests only assert `SEPOL_OK` without deeply validating copy independence, allocator ownership, or complete nested graph equality. There are commented-out `test_cil_copy_ast` cases and declarations in the header for copy-data-helper and `netifcon_merge` paths that do not appear implemented here, indicating possible stale coverage intent. The tests also rely on hand-built pointer walks through generated parse trees, which are brittle if parse-tree shape changes.

## Test Signals
Strong signals include coverage of nested lists, anonymous contexts/ranges/IPs, symbol-table duplicate failures, merge-vs-copy behavior, malformed origin and null extra arguments, and representative security policy objects. The suite gives useful regression detection for return-code contracts and basic field preservation across AST copying.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_copy_ast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_copy_ast.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_copy_ast.h

## Purpose
This header declares the CuTest entry points for CIL copy-AST tests. It is the suite-facing contract consumed by `CilTest.c` and implemented primarily by `test_cil_copy_ast.c`.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares `void test_cil_copy_...(CuTest *)` functions for list copying, each major CIL datum copy helper, fill helpers for level/context/IP address, conditional/boolif/constrain copy paths, direct AST copy tests, internal node-helper tests, and copy-data-helper tests.

## Control Flow
The header has no executable control flow. Its declarations allow the test registrar to add copy tests to the CuTest suite. At runtime, registered functions follow the implementation file's pattern of generating a source CIL object, copying it through `cil_copy_*` or `__cil_copy_node_helper`, and asserting return values and selected fields.

## State And Persistence
There is no persistent state. The file influences build state by requiring function signatures to match implementation and suite registration. Mismatches can surface as link failures only when a declared test is actually registered or referenced.

## Dependencies And Integration Points
The only direct dependency is CuTest. The declared functions integrate indirectly with `CilTest.c`, `test_cil_copy_ast.c`, `cil_copy_ast`, `cil_build_ast`, `cil_internal`, and libsepol symbol table behavior.

## Risks
The header declares `test_cil_copy_node_helper_netifcon_merge`, `test_cil_copy_data_helper`, `test_cil_copy_data_helper_getparentsymtab_neg`, and `test_cil_copy_data_helper_duplicatedb_neg`, but the read implementation did not show matching function bodies. It also declares `test_cil_copy_ast` and `test_cil_copy_ast_neg`, whose implementation is commented out and whose registrations are commented in `CilTest.c`. This drift is a maintenance risk and can hide intended coverage.

## Test Signals
The declaration set shows intended coverage across direct copy functions, helper traversal, duplicate negative paths, null argument paths, and nested object fills. It is a useful map of copy-AST coverage expectations even where implementation or registration lags behind the declarations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_copy_ast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_fqn.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_fqn.c

## Purpose
This file tests full qualified-name processing for CIL ASTs. It ensures that `cil_fqn_qualify` succeeds on representative policy fragments after they have been converted from synthetic parse trees into CIL AST nodes.

## Important APIs, Types, And Functions
It includes `policydb.h`, `CuTest.h`, `CilTest.h`, `cil_fqn.h`, and `cil_build_ast.h`. The two test entry points are `test_cil_qualify_name` and `test_cil_qualify_name_cil_flavor`. They use `gen_test_tree`, `cil_db_init`, `cil_build_ast`, and `cil_fqn_qualify`.

## Control Flow
Each test builds an in-memory token array, converts it to a parser tree, initializes a CIL database, builds the AST at `test_db->ast->root`, then calls `cil_fqn_qualify`. The first case includes categories, category order, sensitivity, sensitivitycategory, type, role, user, context, and sid references. The second case checks the CIL-flavor class syntax with `inherits`.

## State And Persistence
All state is in memory: parse tree, CIL database, AST, and symbols. There is no teardown visible in the tests, so the unit runner relies on process lifetime for cleanup. The relevant state behavior under test is name qualification over the AST rather than durable storage.

## Dependencies And Integration Points
These tests depend on build-AST success before FQN qualification can run. They are registered in `CilTest.c` and integrate the parser helper, CIL AST builder, and FQN qualification pass. They provide a bridge signal between syntax construction and later semantic resolution.

## Risks
The assertions only check `SEPOL_OK`; they do not inspect the qualified names or verify exact namespace transformations. This can miss regressions where qualification succeeds but produces wrong names. Coverage is narrow, with one larger policy fragment and one class-inheritance flavor case.

## Test Signals
The tests signal that the FQN pass must accept normal CIL policy identifiers, MLS-related names, context references, sid references, and the `class ... inherits ...` flavor without rejecting the AST.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_fqn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_fqn.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_fqn.h

## Purpose
This header declares the FQN unit tests for CuTest registration.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares `test_cil_qualify_name(CuTest *)` and `test_cil_qualify_name_cil_flavor(CuTest *tc)`.

## Control Flow
The header has no executable control flow. `CilTest.c` includes it and registers both declarations in the tree suite. The implementation then builds ASTs and runs `cil_fqn_qualify`.

## State And Persistence
No state is stored. It provides compile-time linkage only.

## Dependencies And Integration Points
The declarations integrate `test_cil_fqn.c` with the shared CuTest harness. The implementation depends on CIL AST building and FQN qualification internals.

## Risks
Because only two tests are declared, FQN behavior has a small explicit suite surface. Additions to namespace rules may require new declarations and suite registration to avoid relying on incidental coverage elsewhere.

## Test Signals
The header confirms that both general name qualification and a CIL class-flavor qualification path are intended first-class test cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_fqn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_lexer.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_lexer.c

## Purpose
This file tests basic CIL lexer setup and token iteration. It validates that a small CIL input buffer can be initialized and that lexer output preserves token type, token value, and line number for common syntax.

## Important APIs, Types, And Functions
It includes `policydb.h`, `CuTest.h`, `test_cil_lexer.h`, and `cil_lexer.h`. The test entry points are `test_cil_lexer_setup` and `test_cil_lexer_next`. Important external APIs are `cil_lexer_setup`, `cil_lexer_next`, and `struct token` with token types `OPAREN`, `SYMBOL`, `QSTRING`, `CPAREN`, and `COMMENT`.

## Control Flow
Both tests allocate a mutable buffer with two trailing NUL bytes, copy a CIL string into it, call `cil_lexer_setup`, and assert `SEPOL_OK`. The token iteration test then repeatedly calls `cil_lexer_next` and verifies the sequence `(`, `test`, `"qstring"`, `)`, and `;comment`, all on line 1.

## State And Persistence
The lexer appears to keep input cursor state internally after setup. The tests use heap buffers and free them after token checks. There is no durable persistence. Because the lexer consumes or references the provided buffer, buffer lifetime and NUL padding are important state assumptions.

## Dependencies And Integration Points
The test is registered by `CilTest.c` and targets lexer internals directly. It is upstream of parser tests: parser behavior depends on lexer tokenization being stable for parentheses, symbols, quoted strings, comments, and line accounting.

## Risks
Coverage is minimal: it does not check EOF behavior, multi-line comments or symbols, malformed quoted strings, whitespace variety, error paths, or lexer cleanup. The test assumes comment line remains 1 even with a trailing newline after the comment, so line-number semantics beyond this simple case are not validated.

## Test Signals
Useful signals are correct setup return code, ordered tokenization of basic syntax, retention of raw token text including quotes and semicolon, and stable line number reporting for a single-line input.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_lexer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_lexer.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_lexer.h

## Purpose
This header declares the lexer unit tests for CuTest registration.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares `test_cil_lexer_setup(CuTest *)` and `test_cil_lexer_next(CuTest *)`.

## Control Flow
There is no runtime control flow. The declarations are consumed by `CilTest.c`, which registers the functions into the unit test suite.

## State And Persistence
No state or persistence behavior is present. It only provides function prototypes.

## Dependencies And Integration Points
The header links the lexer implementation tests to the common CIL test harness. The implementation integrates with `cil_lexer_setup`, `cil_lexer_next`, and token definitions from `cil_lexer.h`.

## Risks
The small declaration set mirrors the narrow lexer coverage. Additional lexer edge cases require adding new declarations and suite registration.

## Test Signals
The intended lexer test surface covers setup and sequential next-token behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_lexer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_list.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_list.c

## Purpose
This file tests CIL list initialization plus append and prepend behavior for `struct cil_list` and `struct cil_list_item`. It emphasizes status-code handling for valid insertions and null or malformed arguments.

## Important APIs, Types, And Functions
It includes `CuTest.h`, `CilTest.h`, `cil_internal.h`, and `cil_build_ast.h`. Test targets include `cil_list_init`, `cil_list_item_init`, `cil_list_append_item`, and `cil_list_prepend_item`. The tests use `struct cil_list`, `struct cil_list_item`, `struct cil_avrule`, `struct cil_classpermset`, `struct cil_permset`, `struct cil_tree`, `struct cil_tree_node`, and `struct cil_db`.

## Control Flow
`test_cil_list_init` allocates an AV rule, initializes nested class/permission structures, initializes the permissions list, asserts it is non-null, and destroys the AV rule. Append/prepend tests generate a small `mlsconstrain` parse tree, initialize DB and AST node context, create list items pointing at class tokens in the parse tree, and call append or prepend. Negative tests pass a null list, null item, or a list item that already has `next` set and assert `SEPOL_ERR`.

## State And Persistence
All list state is heap allocated and in memory. The tested state transitions are head/tail insertion and rejection of invalid inputs. The code does not persist data and does not comprehensively free every object in each test, so process lifetime absorbs many allocations.

## Dependencies And Integration Points
The file depends on parser-test helpers to create parse tree data used as list item payloads. It tests utility list functions used broadly by CIL builders, copy logic, expression stacks, and permission/class collections.

## Risks
The tests mostly assert return codes, not exact list ordering, tail links, length, or ownership after operations. `test_cil_list_prepend_item_prepend` only prepends once despite the name. There is no explicit test for append after prepend, empty-list tail consistency, or destroy behavior.

## Test Signals
Good signals include success paths for one and multiple appends, basic prepend success, rejection of null list/item arguments, and rejection of prepending an already-linked item.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_list.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_list.h

## Purpose
This header declares CIL list utility unit tests for the CuTest harness.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares append/prepend test functions and negative cases. It declares `test_cil_list_item_init(CuTest *)`, but the implementation read contains `test_cil_list_init(CuTest *tc)` instead.

## Control Flow
The header itself has no runtime flow. `CilTest.c` registers a subset of list tests; notably it registers append and prepend cases but not the apparent init-name mismatch.

## State And Persistence
No state is stored. It is a compile-time interface for suite registration.

## Dependencies And Integration Points
It integrates with `test_cil_list.c` and `CilTest.c`, and indirectly with the `cil_internal` list utilities.

## Risks
The declaration/implementation mismatch between `test_cil_list_item_init` and `test_cil_list_init` is a drift risk. If someone tries to register the declared init function, linking will fail unless the implementation is renamed or an alias is added. Narrow declarations also omit a direct `test_cil_list_prepend_item` prototype despite the implementation containing that function.

## Test Signals
The header signals intended coverage for append, multiple append, append invalid arguments, prepend, prepend invalid linked item, and prepend null arguments.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_parser.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_parser.c

## Purpose
This file tests that the CIL parser can parse the canned policy buffer supplied by the test helper into a non-null parse tree.

## Important APIs, Types, And Functions
It includes `policydb.h`, `CuTest.h`, `CilTest.h`, `test_cil_parser.h`, `cil_parser.h`, and `cil_internal.h`. The single test entry point is `test_cil_parser`. It uses `cil_tree_init`, `cil_db_init`, `set_cil_file_data`, and `cil_parser`.

## Control Flow
The test initializes an empty `struct cil_tree *test_parse_root`, initializes a CIL database, obtains `struct cil_file_data *data` from `set_cil_file_data`, then calls `cil_parser("policy.cil", data->buffer, data->file_size + 2, &test_parse_root)`. It asserts `SEPOL_OK` and that the returned parse root is non-null.

## State And Persistence
State is in-memory only: a synthetic file buffer, parser output tree, and unused initialized database. The parser is given a filename string for diagnostics but does not persist output. The code comments explicitly note a TODO to rewrite around the generator helper and to add parse-tree checking.

## Dependencies And Integration Points
This is registered by `CilTest.c`. It depends on test fixture data from `CilTest.h` and exercises the parser entry point that sits between lexer tokenization and AST building.

## Risks
The test is shallow. It does not verify parse-tree contents, error handling, line numbers, comments, nested forms, or malformed input. The initialized `cil_db` is not used, which may be historical scaffolding rather than required setup.

## Test Signals
The main signal is smoke coverage that the canonical fixture buffer parses successfully and produces a tree pointer.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_parser.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_parser.h

## Purpose
This header declares the parser smoke test for CuTest registration.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares `test_cil_parser(CuTest *)`.

## Control Flow
There is no executable logic. `CilTest.c` registers the declaration, and the implementation calls `cil_parser` on fixture policy data.

## State And Persistence
No state is stored. It provides a prototype only.

## Dependencies And Integration Points
The header integrates `test_cil_parser.c` with the shared test runner and indirectly with parser internals.

## Risks
Only one parser test is exposed, so parser coverage depends heavily on build-AST tests that construct parse trees manually rather than exercising parser text input.

## Test Signals
The header signals a single parser acceptance test.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_post.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_post.c

## Purpose
This file tests post-processing comparator functions that order CIL context-related policy records. These comparators are important for deterministic output and conflict/ordering semantics after AST resolution.

## Important APIs, Types, And Functions
It includes `policydb.h`, `CuTest.h`, `CilTest.h`, `test_cil_post.h`, `cil_post.h`, and `cil_internal.h`. Tested APIs are `cil_post_filecon_compare`, `cil_post_portcon_compare`, `cil_post_genfscon_compare`, `cil_post_netifcon_compare`, `cil_post_nodecon_compare`, and `cil_post_fsuse_compare`. The tests initialize `struct cil_filecon`, `cil_portcon`, `cil_genfscon`, `cil_netifcon`, `cil_nodecon`, `cil_ipaddr`, and `cil_fsuse`.

## Control Flow
Each test initializes two objects of the same type, sets only the fields relevant to one comparator branch, calls the comparator with addresses of the object pointers, and asserts sign or equality. Filecon tests cover regex/meta-character and stem/type ordering. Portcon tests cover range width and low port. Genfscon and netifcon compare strings. Nodecon tests cover address family, IPv4 address/mask order, and selected IPv6 byte/mask order. Fsuse tests cover type and filesystem string ordering.

## State And Persistence
All state is temporary heap state initialized by CIL init helpers. No persistence occurs. The ordering result is pure with respect to populated fields, so these tests mostly validate deterministic comparison behavior rather than state mutation.

## Dependencies And Integration Points
The file is registered in `CilTest.c`, although portcon tests are declared in the header but not all appear registered in the suite snippet read. The comparators integrate with CIL post-processing sorting of file contexts, port contexts, genfs contexts, network interface contexts, node contexts, and fsuse records.

## Risks
Tests use minimal object initialization and direct field assignment, so they may miss comparator behavior involving unset strings, full IPv6 arrays, protocol fields, or context tie-breakers. Some assertions check only sign, which is appropriate for qsort comparators but does not ensure magnitude stability. Memory is not freed, relying on process lifetime.

## Test Signals
Strong signals include branch-level ordering coverage for less-than, greater-than, and equality cases across major post-processing comparator families. The file is especially useful for detecting accidental reversal of sort order or changed tie-break priority.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_post.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_post.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_post.h

## Purpose
This header declares post-processing comparator tests for CuTest registration.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares tests for filecon, portcon, genfscon, netifcon, nodecon, and fsuse comparator order. Each declaration follows the pattern `void test_cil_post_<object>_compare_<case>(CuTest *tc)`.

## Control Flow
There is no executable control flow. `CilTest.c` includes this header and registers many of the declared comparator tests into the test suite.

## State And Persistence
The header stores no state and performs no persistence. It is a compile-time contract between the comparator test implementation and suite registrar.

## Dependencies And Integration Points
It integrates `test_cil_post.c` with CuTest and the CIL unit suite. The implementation depends on `cil_post.h` and CIL internal object initialization helpers.

## Risks
The header declares portcon tests, but the suite registration excerpt did not show portcon registrations alongside the other post tests. If they are not registered elsewhere, portcon implementation coverage may compile but not run. As with other headers in this directory, declaration drift can hide intended test coverage until link or registration changes expose it.

## Test Signals
The declaration list documents intended comparator coverage for ordering branches and equality cases in post-processing records.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_post.h -->
