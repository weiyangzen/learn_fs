# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.c lines 20683-22965

## Chunk Scope

This chunk is the final chunk of `test_cil_build_ast.c`. It starts at the tail of the `typealias` negative test and then covers a large sequence of CUnit tests for `__cil_build_ast_node_helper`, ending with tests for `__cil_build_ast_last_child_helper`. The tested CIL constructs include type attributes, bounds, role statements, AV rules, type transition/change/member rules, booleans/tunables, MLS sensitivities/categories/ranges/levels, constraints, contexts, labeling statements, hardware/resource context statements, macros, calls, optionals, policy capabilities, and IP address declarations.

The chunk does not define production code. It directly exercises static/internal CIL AST-build helpers by declaring local prototypes and by building synthetic parse trees from token arrays.

## Purpose

The tests validate that the AST builder's keyword dispatch path accepts well-formed CIL statements, rejects malformed or context-forbidden statements, and sets the traversal `finished` flag consistently. This is integration-style unit coverage for the internal production flow in `cil_build_ast.c`:

- `__cil_build_ast_node_helper` ignores non-statement parse nodes, checks whether a statement is legal in the current nesting context, dispatches the statement keyword to the matching `cil_gen_*` routine, appends the generated AST node under the current AST parent, and usually asks the tree walker to skip child parsing for leaf statements.
- `__cil_build_ast_last_child_helper` unwinds `struct cil_args_build` state when a subtree is complete, clears context markers such as macro/optional/boolean-if state, and destroys parse-tree children to reduce memory use.

The main value of this chunk is breadth: it provides one positive and one negative signal for many CIL grammar entry points through the common AST-build dispatcher, rather than only testing each `cil_gen_*` routine in isolation.

## Important APIs, Types, And Functions

- `gen_test_tree(&test_tree, line)` converts a NULL-terminated token array into a `struct cil_tree` parse tree. The tests generally call the helper on `test_tree->root->cl_head->cl_head`, meaning the first token inside the first top-level list.
- `cil_db_init(&test_db)` creates a fresh `struct cil_db` with an AST root used as the target parent for generated AST nodes.
- `gen_build_args(test_db->ast->root, test_db, macro, tifstack)` allocates the test-local `struct cil_args_build` wrapper. In this file it contains `ast`, `db`, `macro`, and `tifstack` fields matching the subset needed by these direct helper calls.
- `__cil_build_ast_node_helper(parse_current, &finished, extra_args)` is the central function under test. The tests assert `SEPOL_OK` or `SEPOL_ERR` and check whether `finished` remains `0` or becomes `1` (`CIL_TREE_SKIP_NEXT`).
- `__cil_build_ast_last_child_helper(parse_current, extra_args)` is tested at the end to ensure a normal subtree exit succeeds and a NULL extra-args call is expected by the test to fail.
- `cil_macro_init`, `cil_tree_node_init`, and `cil_destroy_macro` are used by the nested macro negative tests to synthesize a current macro context and verify that statements forbidden inside macros are rejected.
- CUnit assertions are all `CuAssertIntEquals`, so the tests observe return code and traversal state, not detailed AST node contents.

## Control Flow Covered

Each test follows the same pattern: create a tokenized CIL statement, build a parse tree, initialize a database, initialize `finished = 0`, create `extra_args`, call the internal helper, and assert the outcome. Positive tests expect the production dispatcher to route to the appropriate generator:

- `typeattribute`, `typeattributeset`, `userbounds`, `role`, `roletransition`, `roleallow`, `rolebounds`, `roletype`, and `userrole`.
- AV rules: `allow`, `auditallow`, `dontaudit`, and `neverallow`, each using source/target/class/perms syntax.
- Type rules: `typetransition`, `typechange`, and `typemember`.
- Boolean-like statements: `boolean` and `tunable`.
- MLS/MCS primitives: `sensitivity`, `sensitivityalias`, `category`, `categoryset`, `categoryorder`, `categoryalias`, `categoryrange`, `dominance`, `sensitivitycategory`, `level`, and `levelrange`.
- Constraint and context statements: `constrain`, `mlsconstrain`, `context`, `filecon`, `portcon`, `nodecon`, `genfscon`, `netifcon`, `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, and `fsuse`.
- Higher-level structural statements: `macro`, `call`, `optional`, `policycap`, and `ipaddr`.

The negative tests mutate arity or token shape: missing operands, empty lists, extra operands, identifiers wrapped in lists where atoms are expected, or malformed nested expressions. A few tests invoke statements below later top-level siblings, for example dominance, sensitivitycategory, and level tests select a later `cl_head` via chained `next` pointers after setting up prerequisite sensitivity/category/order declarations in the same parse tree.

The expected `finished` behavior is significant. Leaf-like statements generally expect `finished == 1`, because production code sets `CIL_TREE_SKIP_NEXT` for statements that do not contain nested policy statements. Container-like or declaration paths such as `macro`, `optional`, `role`, `typeattribute`, `boolean`, and `ipaddr` commonly expect `finished == 0` in these tests. Negative cases expect `finished == 0` so failed parses do not request traversal skipping.

## State And Persistence Behavior

All state is in memory. There are no files, policy databases on disk, or persistent artifacts written by these tests. The important transient state is:

- The parse tree produced by `gen_test_tree`.
- The AST rooted at `test_db->ast->root`, which receives nodes if `__cil_build_ast_node_helper` succeeds.
- The `finished` traversal flag passed by pointer.
- The synthetic build context in `struct cil_args_build`, especially `ast`, `db`, and optional `macro`.

Most tests do not destroy `test_tree`, `test_db`, or `extra_args`, which keeps the code short but means the unit binary relies on process teardown for many allocations. The nested macro negative tests are exceptions: they explicitly destroy the database and macro object after checking that nested `macro` and `tunableif` statements are rejected inside macro context.

`__cil_build_ast_last_child_helper` has production-side memory behavior that matters to this chunk: it walks the current AST state back to the parent, clears contextual flags, and calls `cil_tree_children_destroy(parse_current->parent)`. The positive last-child test exercises this path with an `ipaddr` parse subtree.

## Dependencies And Integration Points

This chunk depends on the CIL unit-test harness and libsepol CIL internals:

- `CuTest` and `CilTest.c` register these functions into the CIL build-AST test suite.
- `test_cil_build_ast.h` declares every test in this chunk, including the final `extraargsnull` and last-child tests.
- `../../src/cil_build_ast.h` and direct prototypes expose internal helper behavior to the test file.
- `../../src/cil_tree.h` provides tree-node structures and parse-tree traversal fields such as `cl_head`, `cl_tail`, `next`, and `parent`.
- Production generator functions reached through `parse_statement` include many `cil_gen_*` routines such as `cil_gen_typeattribute`, `cil_gen_avrule`, `cil_gen_typetransition`, `cil_gen_catset`, `cil_gen_constrain`, `cil_gen_context`, `cil_gen_macro`, and `cil_gen_ipaddr`.
- Policy-version and CIL keyword constants are indirectly relevant through `cil_db_init` and the `CIL_KEY_*` keyword dispatch in `cil_build_ast.c`.

The tests are registered near the end of `CilTest.c` in the same rough order as the generator-specific tests, so this chunk acts as final dispatcher coverage after lower-level `cil_gen_*` unit tests.

## Risks And Edge Cases

- The chunk asserts only return code and `finished`; it does not inspect the generated AST node flavor, stored strings, or child structure. A dispatcher could route to the wrong generator but still return `SEPOL_OK` in some cases without this chunk detecting it.
- Several tests depend on exact parse-tree navigation such as `root->cl_head->next->next...`. These are brittle if `gen_test_tree` changes tree shape or if fixture setup inserts/removes top-level forms.
- Many allocations are not cleaned up in ordinary tests. That is acceptable for short-lived CUnit processes but weakens leak-detection usefulness unless the broader harness resets or tolerates these allocations.
- The NULL `extra_args` tests are important risk signals. The production helper implementation dereferences `extra_args` through `args` early in both node-helper and last-child-helper flows; if there is no defensive check in the compiled path, these tests may crash rather than cleanly returning `SEPOL_ERR`. This should be reconciled against the actual build configuration and any wrapper behavior.
- Some positive tests use placeholder identifiers such as `con`, `context`, `low`, and `high` without requiring full semantic resolution. They validate AST construction syntax, not later name resolution or policy validity.
- The `roleallow` positive token array lacks a closing `")"` token in this chunk, yet expects success. That suggests this direct helper test cares only about the current statement's immediate parse node and may not detect malformed outer list completion.
- Nested macro negative tests manually fabricate a `CIL_MACRO` node as context. That is effective for `check_for_illegal_statement`, but it does not simulate every field a real macro AST node would carry.

## Test Signals

Strong signals in this chunk:

- Positive/negative coverage pairs for a broad range of CIL keywords through the shared AST-build helper.
- Validation that malformed arity and malformed list/atom shape return `SEPOL_ERR` without setting `finished`.
- Validation that list-valued constructs such as type attribute sets, category sets/orders/ranges, MLS levels, constraints, contexts, and network/interface contexts request child traversal skipping once parsed.
- Validation that context restrictions reject nested `macro` and `tunableif` statements when `extra_args->macro` is active.
- Validation that last-child handling succeeds for a normal AST state and is intended to reject NULL extra-args input.

Gaps to consider when using this chunk as a regression signal:

- It does not verify AST contents after insertion.
- It does not check log messages or error specificity.
- It does not execute a full `cil_build_ast` traversal over the whole parse tree for these statements; most tests call the node helper directly.
- It does not cover later semantic passes such as symbol resolution, MLS range validation, policy capability support checks, or final policydb conversion.
