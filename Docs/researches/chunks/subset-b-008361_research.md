# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_resolve_ast.c lines 1-10745

## Purpose

This chunk is the first large section of the CIL AST resolver unit-test file for SELinux `libsepol`. It exercises the internal resolver layer that turns parser/build-AST string references into concrete `cil_*` datum pointers and validates pass-specific resolver behavior for blocks, macros, MLS declarations, type enforcement constructs, contexts, network/file labels, and early macro call expansion.

The file is test code, not production resolver logic. Each test builds a small tokenized CIL policy snippet with `gen_test_tree`, initializes a fresh `struct cil_db`, calls `cil_build_ast`, invokes one resolver function or a small sequence of resolver passes, and asserts the expected `SEPOL_OK`, `SEPOL_ENOENT`, or `SEPOL_ERR` result with CuTest. The covered range starts with shared test scaffolding and ends in the beginning of the `cil_resolve_call2_*` tests; the remaining call2/helper-dispatch coverage is in the next chunk.

## Important APIs, Types, And Functions

- `gen_resolve_args()` allocates and populates a local copy of the resolver argument struct used by the internal resolver helpers. The struct fields mirror `cil_resolve_ast.c` internals: `db`, `pass`, `changed`, `callstack`, `optstack`, and `macro`.
- The file forward-declares non-public resolver helpers, especially `__cil_resolve_ast_node_helper()` and `__cil_disable_children_helper()`, because this unit suite reaches into private implementation details through included internal headers.
- Core fixture APIs are `gen_test_tree`, `cil_db_init`, and `cil_build_ast`. Tests depend on the built AST layout and navigate nodes through `test_db->ast->root->cl_head`, `next`, and `cl_head` chains rather than using named lookup helpers.
- Name and top-level resolution coverage includes `cil_resolve_name`, `cil_resolve_ast`, `cil_resolve_roleallow`, `cil_resolve_rolebounds`, `cil_resolve_sensalias`, `cil_resolve_catalias`, `cil_resolve_catorder`, and `cil_resolve_dominance`.
- MLS category/sensitivity/level coverage includes `cil_resolve_cat_list`, `cil_resolve_catset`, `cil_resolve_catrange`, `cil_resolve_senscat`, `cil_resolve_level`, and `cil_resolve_levelrange`, with support calls to `__cil_verify_order` and in some cases `cil_tree_walk`.
- Constraint and context coverage includes `cil_resolve_constrain`, `cil_resolve_context`, and context use through `sidcontext`, `filecon`, `portcon`, `genfscon`, `nodecon`, `netifcon`, `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, and `fsuse`.
- Type-enforcement coverage includes `cil_resolve_typeattributeset`, `cil_resolve_typealias`, `cil_resolve_typebounds`, `cil_resolve_typepermissive`, `cil_resolve_nametypetransition`, `cil_resolve_rangetransition`, `cil_resolve_classcommon`, `cil_resolve_classpermset`, `cil_resolve_avrule`, and `cil_resolve_type_rule`.
- Namespacing and macro expansion coverage includes `cil_resolve_blockinherit`, `cil_resolve_in`, `cil_resolve_call1`, and the start of `cil_resolve_call2`.
- The tests exercise many CIL data types by casting AST node `data`: `struct cil_typealias`, `cil_catset`, `cil_catrange`, `cil_level`, `cil_levelrange`, `cil_context`, `cil_classmapping`, `cil_classpermset`, `cil_call`, `cil_macro`, `cil_param`, and `cil_list_item`.

## Control Flow

The dominant test pattern is:

1. Define `char *line[]` as a flat token stream representing a small CIL S-expression program.
2. Build a parse tree with `gen_test_tree(&test_tree, line)`.
3. Initialize `struct cil_db *test_db` with `cil_db_init`.
4. Allocate resolver arguments with the pass needed for the resolver under test, commonly `CIL_PASS_MISC1`, `CIL_PASS_MLS`, `CIL_PASS_MISC2`, `CIL_PASS_MISC3`, `CIL_PASS_CALL1`, or `CIL_PASS_CALL2`.
5. Convert the parse tree to an AST via `cil_build_ast(test_db, test_tree->root, test_db->ast->root)`.
6. Navigate to the specific AST node, often through positional `cl_head->next` chains.
7. Call the target resolver and assert its return code.

Several tests intentionally model multi-pass resolver dependencies. Category and sensitivity ordering tests run `cil_resolve_catorder`, `cil_resolve_dominance`, or `cil_tree_walk(..., __cil_resolve_ast_node_helper, ...)` before resolving category ranges, sensitivity/category declarations, or levels. Context and range tests often resolve `senscat`, named `level`, or named `levelrange` data before resolving objects that reference them. Macro tests run `cil_resolve_call1` to bind call arguments to macro parameters, then `cil_resolve_call2` to copy or instantiate macro bodies, and only then resolve constructs inside the call body with `args->callstack` pointing at the call node.

Negative tests alter one missing or malformed reference at a time. Examples include absent source/target roles for `roleallow`, missing classmap names or classpermissionsets for `classmapping`, out-of-order or unknown categories in ranges, missing sensitivities or categories in MLS expressions, unknown users/roles/types in contexts, missing class/permission/type names in TE rules, invalid IP address strings, IPv4/IPv6 family mismatches, and call argument count/flavor mismatches. Return-code distinctions are significant: unresolved names generally expect `SEPOL_ENOENT`, malformed internal state or semantic ordering failures often expect `SEPOL_ERR`, and valid repeated/idempotent resolutions usually expect `SEPOL_OK`.

## State And Persistence Behavior

The tests create only in-memory parser trees, CIL databases, AST nodes, symbol tables, and resolver lists. There is no durable persistence, filesystem I/O, or external policy store interaction in this chunk. Persistent state in the production sense is represented by mutations inside `struct cil_db` and its AST:

- `cil_build_ast` populates `test_db->ast`, symbols, declarations, and node data from the test token stream.
- Resolver calls mutate AST datum pointers, resolved lists, macro/call fields, and ordered lists such as `test_db->catorder` and `test_db->dominance`.
- `changed` is passed by pointer in the resolver argument bundle but is usually only initialized and not asserted in this chunk.
- Some tests intentionally mutate resolver-owned state to trigger error paths, for example trimming `test_db->catorder`, changing a macro parameter flavor, freeing and nulling a call's `macro_str`, or resolving the same bounds declaration twice.

The tests do not consistently free `test_tree`, `test_db`, or `args`; this is typical short-lived unit-test fixture behavior but means memory-leak checks would need either fixture cleanup elsewhere or suppressions for intentional test lifetime allocations.

## Dependencies And Integration Points

- Depends on SELinux/libsepol public policydb definitions through `<sepol/policydb/policydb.h>`.
- Depends on CuTest through `CuTest.h` and local CIL test utilities through `CilTest.h`.
- Reaches into CIL internals by including `../../src/cil_build_ast.h`, `../../src/cil_resolve_ast.h`, `../../src/cil_verify.h`, and `../../src/cil_internal.h`.
- Integrates with the CIL pass model. Tests explicitly select pass constants and therefore document which resolver routines are expected to run in which compiler phase.
- Integrates with symbol-table lookup behavior through `cil_resolve_name` and CIL symbol spaces such as `CIL_SYM_TYPES` and `CIL_SYM_BLOCKS`.
- Integrates with macro/block expansion semantics through `cil_resolve_blockinherit`, `cil_resolve_in`, `cil_resolve_call1`, `cil_resolve_call2`, `callstack`, and macro parameter/call argument flavor checks.
- Integrates with MLS ordering validation through `__cil_verify_order`, `test_db->catorder`, and `test_db->dominance`.
- The token streams exercise CIL language surface forms: `block`, `macro`, `call`, `in`, `class`, `common`, `classmap`, `classmapping`, `permissionset`, `classpermissionset`, `allow`, `typetransition`, `typechange`, `typemember`, `rangetransition`, `context`, `sidcontext`, and labeling forms.

## Coverage By Area

- Lines 1-142 establish includes, private helper declarations, `struct cil_args_resolve`, `gen_resolve_args`, baseline `cil_resolve_name` success/failure tests, and a null-root `cil_resolve_ast` failure.
- Lines 143-561 cover role and classmapping resolution, including anonymous/named classpermissionsets and macro-contained classmapping arguments.
- Lines 562-1818 cover MLS aliases, category/sensitivity order, category lists/sets/ranges, and sensitivity-category expressions, including named categorysets, nested ranges, order verification, and missing-name failures.
- Lines 1819-2700 cover level and levelrange resolution for named and anonymous levels, including category list/categoryset inputs and missing sensitivity/category/range endpoints.
- Lines 2701-3598 cover constraint expressions, context resolution, macro-supplied levelranges, named ranges, missing user/role/type/range parts, and roletransition lookup.
- Lines 3599-4202 cover typeattributeset expression resolution, type aliases, type bounds, typepermissive declarations, name type transitions, and expected duplicate/unknown-target behavior.
- Lines 4203-5663 cover rangetransition variants, including named ranges, anonymous ranges, macro-supplied levels/ranges, missing type/class/level references, and anonymous low/high level failures.
- Lines 5664-6296 cover class/common binding, named/anonymous classpermissionsets, permission sets, and AV rule resolution with missing source/target types, classes, permissions, and named permission sets.
- Lines 6297-6725 cover `typetransition`, `typechange`, and `typemember` through the shared `cil_resolve_type_rule` path, checking source type, target type, object class, and result type lookups.
- Lines 6726-9070 cover object, filesystem, network, and hardware labeling resolvers: `filecon`, `portcon`, `genfscon`, `nodecon`, `netifcon`, `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, `fsuse`, and `sidcontext`. Tests check named and anonymous contexts, IPv4/IPv6 handling, missing context references, and invalid embedded context fields.
- Lines 9071-9218 cover `blockinherit` and `in` resolution for blocks, macros, and optionals.
- Lines 9219-10745 cover `cil_resolve_call1` for many parameter flavors: no-parameter calls, type, role, user, sensitivity, category, categoryset, level, ipaddr, class, classmap, permissionset, and classpermissionset parameters. It includes anonymous argument forms, malformed anonymous structures, unknown macro names, extra/missing arguments, duplicate copied names, and forced parameter-flavor corruption. The chunk then begins `cil_resolve_call2` success tests for type, role, user, sensitivity, category, categoryset, permissionset, and classpermissionset parameters.

## Risks And Edge Cases

- The tests use positional AST navigation heavily. Any AST child ordering change in `cil_build_ast` can break tests even if resolver semantics remain correct.
- The local `struct cil_args_resolve` duplicate and private helper declarations make this suite sensitive to internal resolver implementation changes that are not exposed through a stable public header.
- Many fixtures depend on exact pass sequencing. A production pass reorder or a resolver being moved between pass phases could require coordinated updates across many tests.
- Return-code expectations encode subtle distinctions between name-not-found and malformed-state errors. Regressions can be hidden if a resolver returns a generic failure code that still causes policy compilation to fail but no longer preserves diagnostic specificity.
- Macro tests are high-risk because they rely on `callstack`, argument flavor, named-vs-anonymous parameter conversion, and two-stage call resolution. Bugs here can cause references to resolve in the wrong namespace or copied macro bodies to retain stale parameter state.
- MLS tests stress category/sensitivity ordering; incorrect order list mutation can cause later ranges or sensitivity-category expressions to succeed with invalid dominance/category semantics.
- Network label tests cover IPv4/IPv6 family agreement and anonymous IP address parsing. Missing these cases could allow malformed CIL to progress into lower policydb layers.
- Anonymous context tests validate recursive resolution of inline contexts. If anonymous context parsing changes, failures may surface across file, port, genfs, node, hardware, fsuse, and sidcontext resolver paths.
- Some tests deliberately modify internals after partial resolution. These are valuable for error-path coverage but can become brittle when data ownership or initialization changes.

## Test Signals

- A healthy run should compile this file with access to internal CIL headers and execute each `test_cil_resolve_*` CuTest case in the suite registration that appears later in the file.
- Positive resolver tests should return `SEPOL_OK` for valid CIL snippets, including repeated/idempotent cases such as duplicate category/dominance resolution calls and repeated level resolution.
- Missing declaration tests should return `SEPOL_ENOENT`, especially for unresolved users, roles, types, classes, permissions, categories, sensitivities, contexts, macro names, block names, and named ranges.
- Malformed semantic-state tests should return `SEPOL_ERR`, including invalid range ordering, mismatched IP families, malformed anonymous arguments, extra or missing macro call arguments, and manually corrupted parameter flavor data.
- Macro-related tests should be run with both `CIL_PASS_CALL1` and `CIL_PASS_CALL2` paths because call1 validates/binds arguments while call2 begins copying or materializing macro content. Later chunks complete that call2 coverage.
- Changes to `cil_resolve_ast.c`, `cil_build_ast.c`, CIL AST node ordering, CIL pass constants, macro parameter flavors, or MLS ordering helpers should be validated against this suite because this chunk is broad regression coverage for resolver internals.
