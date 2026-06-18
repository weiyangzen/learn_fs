# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.c lines 10058-20682

## Scope And Purpose

This chunk is the middle and largest section of `test_cil_build_ast.c`, a CUnit test file for libsepol's CIL AST builder. It exercises the parser-to-AST generator helpers in `cil_build_ast.c` by building synthetic CIL token trees with `gen_test_tree`, attaching fresh AST nodes to a `cil_db`, invoking a specific `cil_gen_*`, `cil_fill_*`, `cil_build_ast`, or `__cil_build_ast_node_helper` entry point, and checking `SEPOL_OK`/`SEPOL_ERR`, AST flavor, and selected generated fields.

The range begins inside `test_cil_gen_avrule_targetemptyparen_neg`, so its first covered lines are the setup and assertion for an `allow` rule with an empty parenthesized target. It ends in the setup of `test_cil_build_ast_node_helper_typealias_notype_neg`, before that test's helper call and assertions. The following chunk must be consulted for the remainder of that test and later dispatcher cases.

The primary purpose is executable grammar and validation coverage for CIL AST construction. It checks that valid CIL forms produce the expected AST node kind and internal strings/lists, and that malformed trees, null inputs, missing operands, list-vs-symbol mismatches, bad protocol/address/numeric values, and extra operands are rejected.

## Important APIs, Types, And Functions

Core test harness and setup helpers:

- `CuTest`, `CuAssertIntEquals`, `CuAssertStrEquals`, `CuAssertPtrNotNull`, `CuAssertPtrEquals`, and related assertions provide the CUnit-style test contract.
- `gen_test_tree(&test_tree, line)` converts a NULL-terminated token vector into a `struct cil_tree` parse tree. Most tests then pass `test_tree->root->cl_head->cl_head` as the current list head.
- `cil_db_init(&test_db)` creates a `struct cil_db` with an AST root used as the parent for generated nodes and as the root symbol-table context for named declarations.
- `cil_tree_node_init(&test_ast_node)` allocates the AST node passed to a generator. Tests usually set `test_ast_node->parent = test_db->ast->root` and `test_ast_node->line = 1` before invoking a generator.
- `gen_build_args(test_db->ast->root, test_db, NULL, NULL)` creates `struct cil_args_build` for direct calls into `__cil_build_ast_node_helper`.

Generator APIs covered in this chunk include:

- `cil_gen_avrule` negative tail coverage for bad access-vector rule inputs.
- `cil_gen_type_rule` for `CIL_TYPE_TRANSITION`, `CIL_TYPE_CHANGE`, and `CIL_TYPE_MEMBER`.
- User and MLS declarations: `cil_gen_user`, `cil_gen_userlevel`, `cil_gen_userrange`, `cil_gen_sensitivity`, `cil_gen_sensalias`, `cil_gen_category`, `cil_gen_catset`, `cil_gen_catalias`, `cil_gen_catrange`, `cil_gen_catorder`, `cil_gen_dominance`, and `cil_gen_senscat`.
- Role/user/type relation helpers: `cil_gen_roletype`, `cil_gen_userrole`, and `cil_gen_classcommon`.
- Level and range helpers: `cil_fill_level`, `cil_gen_level`, and `cil_gen_levelrange`.
- Constraint and context helpers: `cil_gen_constrain`, `cil_fill_context`, and `cil_gen_context`.
- Labeling/context statements: `cil_gen_filecon`, `cil_gen_portcon`, `cil_fill_ipaddr`, `cil_gen_nodecon`, `cil_gen_genfscon`, `cil_gen_netifcon`, `cil_gen_pirqcon`, `cil_gen_iomemcon`, `cil_gen_ioportcon`, `cil_gen_pcidevicecon`, and `cil_gen_fsuse`.
- Higher-level block-like policy objects: `cil_gen_macro`, `cil_gen_call`, `cil_gen_optional`, `cil_gen_policycap`, and `cil_gen_ipaddr`.
- Whole-builder and dispatcher paths: `cil_build_ast` and the internal `__cil_build_ast_node_helper`.

Important data structures and constants under test include `struct cil_tree`, `struct cil_tree_node`, `struct cil_db`, `struct cil_type_rule`, CIL flavor constants such as `CIL_TYPE_RULE`, `CIL_USER`, and dispatcher keywords, plus result constants `SEPOL_OK` and `SEPOL_ERR`.

## Control Flow

Most direct generator tests follow a consistent flow: construct a token vector for one CIL form, build a parse tree, allocate a `test_ast_node`, initialize a `cil_db`, attach the AST node under `test_db->ast->root`, then call the target generator with the parse-tree node and AST node. Positive tests assert `SEPOL_OK`, the expected `test_ast_node->flavor`, non-null generated data, and specific internal string/list fields. Negative tests assert `SEPOL_ERR`.

The type-rule tests at lines 10236-10773 are representative. Valid `typetransition`, `typechange`, and `typemember` forms are expected to populate `src_str`, `tgt_str`, `obj_str`, `result_str`, set the matching `rule_kind`, and mark the AST node as `CIL_TYPE_RULE`. Each rule kind then has null-current, null-AST, missing source, missing target, missing object class, missing result, and extra-token tests.

The user and MLS sections progressively cover named declarations, aliases, sets, ranges, orders, dominance, and sensitivity/category relationships. Many negative tests deliberately make an operand a nested list where a scalar name is expected, remove required tokens by truncating `next` pointers, or pass anonymous range/level forms with empty lists. `cil_fill_level` and `cil_fill_context` are lower-level fillers: their tests check correct extraction of sensitivity/categories and user/role/type/low/high-level fields from nested parse nodes before the higher-level named generators are tested.

The labeling and low-level context sections validate grammar-specific branching. File contexts are tested for file-type selectors such as directory, file, char, block, socket, pipe, symlink, and any. Port contexts distinguish `udp` and `tcp`, validate single ports and two-value ranges, and reject unknown protocols, malformed ranges, missing ports, and bad contexts. IP address handling is split between `cil_fill_ipaddr` for inline anonymous address parsing and `cil_gen_ipaddr` for named IPv4/IPv6 declarations. Node, genfs, netif, pirq, iomem, ioport, pcidevice, and fsuse tests cover their required identifiers, numeric parsing, optional anonymous contexts, and extra-token rejection.

The macro, call, and optional sections exercise CIL constructs that contain nested bodies or argument lists. Macro tests cover every accepted parameter kind in this chunk (`type`, `role`, `user`, `sensitivity`, `category`, `catset`, `level`, `class`, `classmap`, and `permset`), duplicate handling, unknown parameter kinds, unnamed or empty macros, missing parameter names, and parameter names containing periods. Call tests cover calls with arguments, no arguments, anonymous/list arguments, missing names, and name-in-parentheses errors. Optional tests cover named optional blocks, empty optionals, missing rule bodies, extra tokens, and name-in-parentheses errors.

`cil_build_ast` itself is tested near lines 19522-19583 for the whole tree build path: a simple parse tree should build successfully, while null `db`, null `ast`, null tree, and a malformed subtree should fail. The subsequent dispatcher tests call `__cil_build_ast_node_helper` directly with `struct cil_args_build`. These tests verify keyword-to-generator routing and the `finished` flag. For example, `class`, `common`, `sid`, `sidcontext`, `userlevel`, `userrange`, `rangetransition`, and conditional blocks set `finished = 1` when the helper consumes the node completely, while declarations or container-like forms such as `user`, `type`, `typeattribute`, `block`, `macro`, `call`, `optional`, and several type relationship helpers leave traversal to continue with `finished = 0`.

## State And Persistence Behavior

This is unit-test code only. It does not perform durable filesystem, policy-store, or kernel state changes. State is in-memory CIL parser and AST state:

- `gen_test_tree` creates transient parse trees from token arrays.
- `cil_db_init` creates a temporary CIL database and AST root for symbol-table insertion and parent context.
- Successful generators allocate and attach node-specific data to `test_ast_node->data`, set `test_ast_node->flavor`, and may add named declarations to the parent/root symbol table.
- Lower-level fill helpers populate preallocated CIL objects such as levels, contexts, and IP address structures.
- Some negative tests manually corrupt parse tree links, such as assigning `next = NULL`, to simulate truncated forms.

The chunk generally does not emphasize cleanup. Several tests allocate databases, AST nodes, lists, and parse trees without local destruction, which is common in narrow CUnit parser tests but means the tests are better at validating return/status contracts than ownership balance. The generated AST data persists only for the life of the test process.

## Dependencies And Integration Points

The file includes `CuTest.h`, `CilTest.h`, `test_cil_build_ast.h`, and the production CIL headers `../../src/cil_build_ast.h` and `../../src/cil_tree.h`; it also includes `<sepol/policydb/policydb.h>`. The direct declaration of `__cil_build_ast_node_helper` exposes an internal helper to the test suite, so this chunk is tightly coupled to non-public builder internals and not just the public libsepol CIL API.

The tests integrate with the CIL parser representation through `struct cil_tree_node` sibling/child links (`next`, `cl_head`) and with the AST representation through node flavors, parent pointers, line numbers, and generated datum fields. Dispatcher tests integrate with the AST traversal protocol through `struct cil_args_build`, including the current AST parent, current database, optional macro context, and optional tunable-if stack.

Semantically, this chunk is tied to the CIL language grammar accepted by `cil_build_ast.c`. Changes to syntax for access rules, MLS declarations, contexts, network labels, device labels, macro parameter kinds, optional blocks, or conditional blocks should be reflected here; conversely, failing tests in this chunk usually indicate a parser/builder contract change rather than a runtime policy enforcement issue.

## Risks And Edge Cases

The chunk boundary is itself a review risk. It starts inside one avrule negative test and ends inside a typealias dispatcher negative test, so neither boundary test is fully represented here. The merge/reconciliation lane needs neighboring chunks to avoid treating this range as a complete per-file report.

The tests rely heavily on synthetic parse trees and direct pointer manipulation. That is useful for precise failure paths, but it can differ from real parser output, especially for malformed syntax the lexer/parser might reject before `cil_build_ast.c` sees it. Directly nulling `next` pointers also bypasses normal parse-tree ownership and structural invariants.

Many positive tests validate only selected fields. For example, they often assert flavor and key strings but not complete list contents, symbol-table state, destructor behavior, duplicate handling beyond a targeted case, or later resolver behavior. A generator can pass these tests while still producing an AST that fails in resolution or binary policy emission.

Input validation is broad but grammar-specific. Missing operands, extra operands, scalar-vs-list mismatches, invalid protocol names, malformed IP addresses, and numeric parsing failures are well represented. More semantic conflicts, such as unresolved names, duplicate declarations in broader scopes, MLS ordering consistency, or policy capability validity beyond syntax, are generally handled later in the CIL pipeline and are not fully proven by these tests.

Because the test suite invokes internal helpers and checks implementation-specific flavors and data fields, refactors that preserve public behavior but change internal AST construction may require coordinated test updates. The dispatcher tests in particular are sensitive to the exact `finished` traversal protocol.

## Test Signals

Strong signals from this chunk include:

- Access-vector and type-rule parsers reject null inputs, truncated operands, malformed nested lists, and extra tokens.
- Type transition/change/member rules populate source, target, object, result, rule kind, and `CIL_TYPE_RULE` flavor for valid forms.
- User, user-level, user-range, sensitivity, category, alias, set, and range generators accept valid named and anonymous forms and reject missing names, empty ranges/sets, unexpected lists, and extra tokens.
- Role/type and user/role relation generators reject malformed left/right operands and nested sublists in places that require scalar identifiers.
- Class/common and class-common parsing validates required class/common names and permission lists.
- MLS ordering, dominance, sensitivity/category mapping, level, level-range, and context helpers validate nested low/high level structure.
- Constraint parsing handles direct class/perm forms, class sets, perm sets, and invalid expressions.
- File, port, node, genfs, netif, pirq, iomem, ioport, pcidevice, and fsuse context generators validate object selectors, numeric ranges, contexts, anonymous contexts, and extra-token rejection.
- Macro and call parsing validates parameter kinds, duplicate and malformed parameter declarations, argument lists, and missing names.
- Optional blocks, policy capabilities, and named IP address declarations receive direct positive and negative syntax coverage.
- `cil_build_ast` and `__cil_build_ast_node_helper` tests verify top-level build error propagation and dispatcher routing for many CIL keywords, including expected `finished` behavior.

Useful follow-up coverage would include leak/ownership checks under ASan or valgrind, parser-to-builder integration tests using actual CIL source text rather than synthetic trees, and end-to-end checks that ASTs built by these helpers resolve and emit expected policy structures.
