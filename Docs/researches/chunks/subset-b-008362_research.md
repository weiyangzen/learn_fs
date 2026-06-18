# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_resolve_ast.c lines 10746-17523

## Scope And Purpose

This chunk is a large unit-test band for libsepol CIL AST resolution. It does not implement resolver behavior directly; it constructs small CIL token streams, builds ASTs from them, drives specific resolver entry points, and asserts the expected `SEPOL_OK`, `SEPOL_ERR`, or `SEPOL_ENOENT` outcomes.

The covered tests exercise these resolver areas:

- macro call second-pass argument binding and call argument lookup;
- boolean and tunable expression resolution and evaluation;
- user/role/type/MLS relationship resolution;
- disabling AST subtrees for optional or inactive declarations;
- the generic `__cil_resolve_ast_node_helper` dispatcher across many CIL statement flavors;
- resolver error behavior for missing symbols, wrong symbol flavors, null inputs, invalid pass/flavor combinations, callstack/optional-stack constraints, and unresolved optional content.

The tests are source-tree-aligned with the CIL resolver internals, especially the multi-pass resolver model where different declarations are resolved in `CIL_PASS_CALL1`, `CIL_PASS_CALL2`, `CIL_PASS_MISC1`, `CIL_PASS_MISC2`, `CIL_PASS_MISC3`, `CIL_PASS_TIF`, and `CIL_PASS_BLKIN`.

## Important APIs, Types, And Functions

The common test setup uses `gen_test_tree` to transform a string-token array into a `struct cil_tree`, `cil_db_init` to create a fresh `struct cil_db`, `cil_build_ast` to populate `test_db->ast->root`, and `gen_resolve_args` to create `struct cil_args_resolve` with a pass, change flag, callstack, optional stack, and extra resolver context.

Macro resolution is tested through `cil_resolve_call1`, `cil_resolve_call2`, and `cil_resolve_name_call_args`. These tests cover formal/actual argument binding for classes, classmaps, levels, IP addresses, anonymous levels/IP addresses, wrong flavors, missing names, missing argument lists, null call pointers, and null names.

Expression resolution and evaluation are tested through `cil_resolve_expr_stack`, `cil_resolve_boolif`, `cil_resolve_tunif`, and `cil_evaluate_expr_stack`. The expression tests cover booleans, tunables, types, roles, users, unary `not`, binary operators `and`, `or`, `xor`, `eq`, `neq`, nested operator placement on either operand side, missing symbols, and malformed conditional nodes with null strings.

Relationship-specific resolver APIs include `cil_resolve_userbounds`, `cil_resolve_roletype`, `cil_resolve_userrole`, `cil_resolve_userlevel`, `cil_resolve_userrange`, and `cil_resolve_senscat`. These verify user/role/type linkage and MLS level/range resolution, including named levels/ranges, anonymous MLS syntax, and macro-substituted level or range arguments.

Subtree state behavior is tested through `__cil_disable_children_helper`, which is invoked on optional blocks, blocks, users, roles, types, aliases, common/class declarations, booleans, sensitivities, categories, category sets, SIDs, macros, contexts, levels, policy capabilities, permissions, category/sensitivity aliases, tunables, and unknown/unhandled flavors.

The generic resolver dispatch path is tested through `__cil_resolve_ast_node_helper`. This section covers call resolution, conditionals, category ordering, dominance, role allow rules, aliases, category sets/ranges, levels/ranges, constraints, contexts, sensitivity-category mappings, role transitions, type attributes and aliases, bounds, permissive types, range transitions, named type transitions, AV rules, type rules, user relationships, context-bearing labeling rules, hardware/resource context statements, block inheritance, class-common links, optional/macro/call stack handling, and negative guard paths.

Key CIL data structures appearing directly in the tests include `struct cil_db`, `struct cil_tree`, `struct cil_tree_node`, `struct cil_args_resolve`, `struct cil_call`, `struct cil_args`, `struct cil_booleanif`, `struct cil_tunableif`, `struct cil_constrain`, `struct cil_conditional`, `struct cil_optional`, and `struct cil_symtab_datum`.

## Control Flow

Most tests follow a fixed pattern:

1. Define a compact CIL policy fragment as a `char *line[]` token array.
2. Build a parse tree and AST with `gen_test_tree`, `cil_db_init`, and `cil_build_ast`.
3. Create resolver arguments with the appropriate pass.
4. Select an AST node by walking `test_db->ast->root->cl_head`/`next`/`cl_head` links.
5. Invoke a focused resolver function or the generic helper.
6. Assert the resolver return code with `CuAssertIntEquals`.

The macro-call tests model the two-pass call flow explicitly. `cil_resolve_call1` locates and validates the macro call target and records call metadata. The test then switches `args->pass` to `CIL_PASS_CALL2` and invokes `cil_resolve_call2` to bind actual arguments to macro parameters. Later lookup tests call `cil_resolve_name_call_args` after those passes to validate that macro-local names resolve to the correct actual AST nodes and flavors.

Expression tests first resolve symbol names in expression stacks, then evaluate tunable expression stacks where appropriate. Boolean conditionals use `CIL_PASS_MISC1`; tunable conditionals use `CIL_PASS_TIF`; constraint expressions involving user/role/type symbols use `CIL_PASS_MISC3`. Negative cases distinguish missing symbols (`SEPOL_ENOENT`) from malformed resolver inputs (`SEPOL_ERR`).

MLS user-level and user-range tests show the dependency between passes. They resolve `sensitivitycategory` relations in `CIL_PASS_MISC2` using `cil_resolve_senscat`, then switch to `CIL_PASS_MISC3` before resolving `userlevel` or `userrange`. Macro variants add `CIL_PASS_CALL1` and `CIL_PASS_CALL2` before MLS resolution and set `args->callstack` when resolving statements inside expanded macro call content.

`__cil_resolve_ast_node_helper` acts as a dispatcher keyed by `node->flavor` and `args->pass`. The tests confirm that the helper invokes the correct specialized resolver for each pass/flavor pair, leaves `finished` as `0` for these unit paths, and tolerates stack states for calls, optionals, disabled optionals, and macros where expected.

## State And Persistence Behavior

The tests are entirely in-memory. They create transient `struct cil_db` and AST instances and do not persist policy output, write files, update repository state, or create compiled SELinux policy artifacts.

The important state transitions are resolver-internal:

- `cil_build_ast` attaches typed CIL data to AST nodes and populates symbol tables used by later resolution.
- `cil_resolve_call1` and `cil_resolve_call2` mutate call-related structures so macro formal parameters can map to actual arguments and nested macro statements can be resolved against `args->callstack`.
- `cil_resolve_expr_stack` replaces or annotates expression-stack conditionals with resolved symbol references and validates their expected flavors.
- `cil_evaluate_expr_stack` reads resolved tunable values and computes a boolean result.
- `cil_resolve_tunif` can mark branches active/inactive according to evaluated tunable conditions.
- `__cil_disable_children_helper` walks AST subtrees and changes `cil_symtab_datum.state` or related declaration state to disabled where appropriate.
- `__cil_resolve_ast_node_helper` relies on `args->optional`/optional stack and callstack state to decide whether failures should propagate normally, be converted into optional-disable behavior, or be rejected as invalid nesting.

Because each test initializes a new database, there is no cross-test persistence. However, these tests are persistence-relevant for the compiler as a whole: successful resolution determines which declarations and rules survive into later CIL compilation and policy emission.

## Dependencies And Integration Points

The chunk depends on the CUnit/CuTest harness through `CuTest` and `CuAssertIntEquals`. It also depends on local test helpers defined elsewhere in `test_cil_resolve_ast.c`, including `gen_test_tree` and `gen_resolve_args`.

The resolver APIs under test are integration points between the AST builder, symbol tables, macro expansion/call handling, conditional expression logic, MLS model resolution, optional block semantics, and the broader libsepol CIL compilation pipeline.

The CIL language constructs used in token streams include `class`, `common`, `classcommon`, `classmap`, `classmapping`, `macro`, `call`, `allow`, `boolean`, `booleanif`, `tunable`, `tunableif`, `category`, `categoryorder`, `sensitivity`, `sensitivitycategory`, `sensitivityalias`, `categoryalias`, `categoryset`, `categoryrange`, `level`, `levelrange`, `context`, `constrain`, `mlsconstrain`, `user`, `role`, `type`, `userbounds`, `rolebounds`, `typebounds`, `roletype`, `userrole`, `userlevel`, `userrange`, `roleallow`, `roletransition`, `typeattributeset`, `typealias`, `typepermissive`, `rangetransition`, `typetransition`, `typechange`, `typemember`, `filecon`, `portcon`, `genfscon`, `nodecon`, `netifcon`, `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, `fsuse`, `sid`, `sidcontext`, `block`, `blockinherit`, and `optional`.

Return-code expectations integrate with libsepol's public error vocabulary. `SEPOL_OK` indicates successful resolution, `SEPOL_ENOENT` indicates a referenced declaration was not found or a dependent symbol failed to resolve, and `SEPOL_ERR` indicates malformed input, invalid resolver context, incompatible flavors, or illegal stack/pass combinations.

## Risks And Edge Cases

The tests rely heavily on positional AST navigation such as `root->cl_head->next->next`. This is concise but fragile: adding declarations to a test token stream or changing AST construction order can point a test at the wrong node while still compiling.

Several negative tests intentionally corrupt internals after AST construction, such as changing a macro argument flavor to `CIL_SYM_UNKNOWN`, nulling a conditional string, using an empty user string in `sidcontext`, or passing null call/name/helper arguments. These are valuable guard tests, but they depend on internal structure layouts and can become stale if the implementation refactors data ownership.

Macro argument tests cover many flavors, but they mainly assert return codes rather than inspecting the exact resolved nodes. A resolver regression that returns `SEPOL_OK` while binding to an incorrect but compatible datum could escape these tests unless later compilation fails.

MLS tests rely on correct pass sequencing. Missing the `CIL_PASS_MISC2` sensitivity-category resolution step before `CIL_PASS_MISC3` userlevel/userrange resolution can turn otherwise valid fragments into `SEPOL_ENOENT`. This mirrors production pass ordering and makes these tests good signals for pass-regression bugs.

Optional behavior is subtle. The helper can treat some failures inside optionals as non-fatal by disabling optional content, but it rejects invalid optional stack combinations for tunables and macro call resolution. Changes around `args->optional`, disabled state, or "failed to resolve" handling have high regression risk.

The generic AST helper tests cover broad flavor dispatch but usually assert only the top-level return code and `finished == 0`. They do not fully validate all side effects, such as final datum pointers, list contents, branch enablement, or disabled child states.

Context-bearing rule tests are security-sensitive because incorrect resolution of contexts, MLS ranges, IP addresses, netmasks, filesystems, ports, devices, or SIDs can produce incorrect SELinux labeling rules. The negative tests catch unresolved references but not every semantic validation rule.

## Test Signals

Direct signals in this chunk include:

- `test_cil_resolve_call2_*` validates macro call second-pass handling for classes, classmaps, levels, anonymous levels, IP addresses, anonymous IP addresses, unknown flavors, and missing argument syntax.
- `test_cil_resolve_name_call_args*` validates successful and failing call-argument name lookup across flavor mismatches, null inputs, absent call args, and unresolved names.
- `test_cil_resolve_expr_stack_*`, `test_cil_resolve_boolif*`, `test_cil_resolve_tunif*`, and `test_cil_evaluate_expr_stack_*` validate expression name resolution, boolean/tunable branch resolution, and operator evaluation.
- `test_cil_resolve_userbounds*`, `test_cil_resolve_roletype*`, `test_cil_resolve_userrole*`, `test_cil_resolve_userlevel*`, and `test_cil_resolve_userrange*` validate user/role/type and MLS relationship resolution, including macro and anonymous MLS forms.
- `test_cil_disable_children_helper_*` validates that the disable helper handles many AST flavors without error and respects already-disabled optionals.
- `test_cil_resolve_ast_node_helper_*` validates dispatch for specialized resolver functions over call, conditional, MLS, access-rule, transition, context, device, filesystem, block, class-common, rolebounds, optional, macro, and invalid-input paths.

Useful follow-up coverage would inspect resolved datum pointers and state transitions after successful calls, add tests for deeply nested macro/optional combinations, and verify complete side effects for context-bearing statements rather than relying only on return codes.
