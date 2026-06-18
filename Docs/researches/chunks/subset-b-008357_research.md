# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.c lines 1-10057

## Chunk Scope

This research covers the first chunk of `test_cil_build_ast.c`, from the license/header through line 10057. The chunk begins a very large CuTest unit-test file for libsepol's CIL AST builder and ends in the middle of `test_cil_gen_avrule_targetemptyparen_neg`; later AV-rule cases and AST-dispatch helper tests are outside this chunk.

## Purpose

This chunk validates the low-level CIL parse-tree-to-AST builder functions in `../../src/cil_build_ast.h`. The tests build synthetic CIL parse trees from token arrays with `gen_test_tree`, call individual `cil_gen_*`, `cil_fill_*`, `cil_parse_to_list`, `cil_set_to_list`, and `cil_gen_expr_stack` routines directly, and assert their return codes and selected AST fields.

The primary behavioral target is parser robustness: each grammar production has a success case and many malformed-input cases covering null pointers, missing required tokens, extra tokens, unexpected nested lists, empty lists, duplicate symbols, invalid operators, and wrong expression domains.

## File Setup and Local Helpers

The chunk includes:

- `<sepol/policydb/policydb.h>` for SELinux/libsepol status and policy constants.
- `CuTest.h` and `CilTest.h` for the test framework and helper fixtures.
- `test_cil_build_ast.h` for suite declarations used by the full file.
- Private implementation headers `../../src/cil_build_ast.h` and `../../src/cil_tree.h`, making this a white-box unit test.

The file forward-declares private helpers:

- `__cil_build_ast_node_helper(struct cil_tree_node *, uint32_t *, void *)`
- `__cil_build_ast_last_child_helper(struct cil_tree_node *, void *)`

Only declarations appear in this chunk; the direct tests for these helpers occur after the current line range.

The local `struct cil_args_build` mirrors the argument bundle passed to AST traversal helpers: `ast`, `db`, `macro`, and `tifstack`. `gen_build_args()` heap-allocates this structure with `cil_malloc` and stores those pointers without ownership transfer or cleanup in this chunk.

## Important APIs and Behaviors Covered

### Generic tree/list conversion

The first tests cover `cil_parse_to_list` and `cil_set_to_list`.

- `cil_parse_to_list` is checked with an `allow` rule permission list and `CIL_AST_STR` list item flavor.
- Negative cases assert `SEPOL_ERR` for null parse node and null output list.
- `cil_set_to_list` converts CIL set syntax into `struct cil_list`, including nested sublists.
- Negative cases check null tree node, null `cl_head`, and null output list.

These tests exercise the builder's base assumption that parse tree nodes are linked through `cl_head`, `next`, and child-list nodes.

### Namespace and block forms

The chunk covers:

- `cil_gen_block`
- `cil_destroy_block`
- `cil_gen_blockinherit`
- `cil_gen_in`

`cil_gen_block` creates a `CIL_BLOCK` node, sets `data`, and preserves the `is_abstract` argument. Its failure cases cover missing block name, list-valued name, null database, null current parse node, null AST node, and null AST parent. `cil_destroy_block` is expected to clear the AST node data via the destroy path.

`cil_gen_blockinherit` accepts exactly a scalar inherited block name. Tests reject list names, missing names, extra tokens, null database, null current node, and null AST node.

`cil_gen_in` handles an `in` statement with a block name and nested body. Tests reject missing block name, extra body elements after the nested statement list, null database/current/AST node, and malformed parse nodes.

### Classes, permissions, permission sets, and class maps

The chunk heavily exercises class/permission generation:

- `cil_gen_perm`
- `cil_gen_permset`
- `cil_gen_perm_nodes`
- `cil_fill_permset`
- `cil_gen_class`
- `cil_fill_classpermset`
- `cil_gen_classpermset`
- `cil_gen_classmap_perm`
- `cil_gen_classmap`
- `cil_gen_classmapping`
- `cil_gen_common`

The normal `cil_gen_class` path builds a `CIL_CLASS`, attaches child permission nodes, and validates that `cl_tail` and `data` are set. It also permits a class with no permissions. Negative cases check malformed names, missing `class`, permissions outside a list, multiple permission lists, nested permission lists, and null arguments.

`cil_gen_perm_nodes` inserts generated permissions into a class permission symtab. One important negative case destroys `test_cls->perms` before insertion and expects `SEPOL_ENOMEM`, so this chunk explicitly tests allocation/symtab failure propagation.

`cil_fill_classpermset` and `cil_gen_classpermset` accept both anonymous permission lists like `(char (write))` and named permission-set references like `(char perms)`. They reject empty permission lists, missing class names, nested unexpected lists, extra tokens, and null output structures.

`cil_gen_classmap_perm` tests classmap permission insertion and duplicate detection. The duplicate case calls `cil_gen_classmap` first, then tries to generate the same classmap permission and expects `SEPOL_EEXIST`.

`cil_gen_classmapping` handles both anonymous class/permission-set tuples and named permission-set references. It rejects missing classmap name, missing classmap permission, missing mapped permission sets, empty anonymous permission sets, and null database/current/AST node.

`cil_gen_common` validates common permission blocks and rejects missing names, duplicate permission lists, nested permissions, and empty permission lists.

### SID, type, role, bounds, and alias declarations

This chunk covers declaration generators for:

- `cil_gen_sid`
- `cil_gen_sidcontext`
- `cil_gen_type`
- `cil_gen_typeattribute`
- `cil_gen_typebounds`
- `cil_gen_typepermissive`
- `cil_gen_typealias`
- `cil_gen_typeattributeset`
- `cil_gen_userbounds`
- `cil_gen_role`
- `cil_gen_roletransition`
- `cil_gen_roleallow`
- `cil_gen_rolebounds`

The declaration pattern is consistent: create a small tokenized CIL statement, initialize a DB and AST node, set `test_ast_node->parent = test_db->ast->root` where required, call the generator, and assert `SEPOL_OK` plus expected AST flavor/data for success cases.

`cil_gen_sidcontext` is notable because it accepts both anonymous context syntax and named context references. Negative cases cover half-formed contexts, missing SID name, empty statement, missing context, duplicate context names, null database/current/AST node.

`cil_gen_typeattributeset` accepts scalar type names and expression forms such as `(and test_t test2_t)` and `(not notypes_t)`. It also treats `(not attr)` as a valid exclusion expression. It rejects empty `(not)`, missing attribute name, name in parentheses, empty lists, list-valued members where scalar values are expected, extra tokens, and null inputs.

`cil_gen_roletransition` is a two-argument API in this file, unlike many other generators: `cil_gen_roletransition(parse_current, ast_node)`. Its tests mutate linked-list pointers to simulate missing source, target, and result fields. It does not take `struct cil_db *` in this chunk.

`cil_gen_roleallow` and `cil_gen_rolebounds` validate role relationship statements and include field assertions for `src_str` and `tgt_str`.

### Boolean, tunable, and conditional AST forms

The chunk tests expression parsing and conditional blocks:

- `cil_gen_expr_stack` with `CIL_BOOL`
- `cil_gen_boolif`
- `cil_gen_tunif`
- `cil_gen_condblock`
- `cil_gen_bool` for both `CIL_BOOL` and `CIL_TUNABLE`

Boolean expression tests cover `and`, `or`, `xor`, `not`, `eq`, `neq`, nested expressions, missing operators, empty argument lists, missing operands, extra operands, null current node, and null output stack.

`cil_gen_boolif` and `cil_gen_tunif` validate `true` and `false` branch blocks, multiple branch blocks, nested boolean/tunable expressions, scalar condition references, missing true-list blocks, empty conditions, unknown condition keywords, extra parentheses, bad operators, and null arguments.

`cil_gen_condblock` validates both `CIL_CONDTRUE` and `CIL_CONDFALSE` blocks and rejects missing nested rule lists and extra tokens.

`cil_gen_bool` creates both boolean and tunable AST nodes, checks parsed `true`/`false` values, and rejects missing value, invalid boolean strings, missing names, extra names, and null inputs.

### Range transitions and name transitions

The chunk covers:

- `cil_gen_nametypetransition`
- `cil_gen_rangetransition`

`cil_gen_nametypetransition` expects a string/name, source type, target type, class, and destination type. It has precise negative tests for each missing field and for each field incorrectly represented as a parenthesized sublist.

`cil_gen_rangetransition` accepts named level ranges and anonymous level forms, including anonymous low or high level values. It rejects null database/current/AST node, missing source/target/class/low/high fields, parenthesized scalar fields, invalid anonymous level syntax, and extra tokens.

### Constraint and MLS constraint expressions

The densest section in this chunk targets `cil_gen_expr_stack` with `CIL_MLSCONSTRAIN` and `CIL_CONSTRAIN`. It constructs `struct cil_constrain`, initializes `classpermset`, fills it from the parse tree with `cil_fill_classpermset`, and parses the expression into `cons->expr`.

Operators and domains covered include:

- Equality and inequality: `eq`, `neq`
- Unary negation: `not`
- Binary logical operators: `or`, `and`
- MLS dominance operators: `dom`, `domby`, `incomp`
- Entity keywords: `t1`, `t2`, `r1`, `r2`, `u1`, `u2`
- MLS keywords: `l1`, `l2`, `h1`, `h2`
- Symbol references such as `type_t`, `role_r`, and `user`

The tests enforce domain restrictions. For example, comparing `t1` to `type_t`, `r1` to `role_r`, or `u1` to `user` is accepted, while self comparisons such as `t1` to `t1`, `r1` to `r1`, `u1` to `u1`, or invalid MLS level usage in ordinary `CIL_CONSTRAIN` are rejected. The chunk also checks left-keyword restrictions such as `eq h2 h1`, missing operands, operands in parentheses, extra operands, operators in parentheses, null output stack, null/empty current expression, and calling into a nested expression at the wrong parse node.

### AV rule start

The chunk begins AV-rule testing:

- `cil_gen_avrule` with `CIL_AVRULE_ALLOWED`

Successful cases include anonymous class/permission lists and named permission-set references. The main success case asserts source string, target string, class string, AST flavor `CIL_AVRULE`, and the populated permission list with `CIL_AST_STR` items matching parse-tree permission tokens.

Negative cases in this chunk include extra trailing token after the classperm set, source represented as a list, empty source list, target represented as a list, and the beginning of an empty target-list test. The empty target-list test body is incomplete at line 10057 and continues into the next chunk.

## Control Flow Pattern

Nearly every test follows the same sequence:

1. Declare a null-terminated `char *line[]` token stream representing a CIL form.
2. Call `gen_test_tree(&test_tree, line)` to synthesize a `struct cil_tree`.
3. Allocate a `struct cil_tree_node *test_ast_node` with `cil_tree_node_init`.
4. Allocate a `struct cil_db *test_db` with `cil_db_init` where the target API requires a database.
5. Set AST parent and line metadata when the generator expects a valid insertion context.
6. Navigate the parse tree via `root->cl_head->cl_head`, `next`, and `cl_head` chains.
7. Call the target generator/filler/parser.
8. Assert `SEPOL_OK`, `SEPOL_ERR`, `SEPOL_ENOMEM`, or `SEPOL_EEXIST`; selected success tests also assert AST data fields, flavors, or list contents.

Negative tests often mutate the generated parse tree after construction, e.g. setting `cl_head` or `next` links to `NULL`, to exercise error paths that are hard to express through a simple token array.

## State and Persistence Behavior

There is no durable persistence, file I/O, or external state in this chunk. All state is in-memory test fixture state:

- `struct cil_db` instances own an AST root and symtabs used by generators.
- `struct cil_tree` instances provide parsed CIL input fixtures.
- `struct cil_tree_node` instances are manually initialized and used as destinations for AST builder output.
- `struct cil_list`, `struct cil_permset`, `struct cil_classpermset`, and `struct cil_constrain` objects are allocated directly for helper-level tests.
- Some objects are explicitly destroyed only where the test target is a destroy function or where failure injection requires it, such as destroying `test_cls->perms` before testing `cil_gen_perm_nodes` error propagation.

The tests intentionally do not exercise final compiled policy output. They validate intermediate AST construction, parse validation, and data attachment only.

## Dependencies and Integration Points

This unit-test chunk integrates tightly with libsepol CIL internals:

- `cil_malloc`, `cil_strdup`, `cil_db_init`, `cil_tree_node_init`, and specific `cil_*_init` routines allocate and initialize fixture state.
- `gen_test_tree` from `CilTest.h` is the parse-tree fixture factory.
- `cil_symtab_insert` is used to seed the class symbol table for permission-node generation.
- Return codes are libsepol constants: `SEPOL_OK`, `SEPOL_ERR`, `SEPOL_ENOMEM`, and `SEPOL_EEXIST`.
- AST flavors such as `CIL_BLOCK`, `CIL_CLASS`, `CIL_COMMON`, `CIL_SIDCONTEXT`, `CIL_TYPE`, `CIL_TYPEATTRIBUTE`, `CIL_TYPEALIAS`, `CIL_ROLE`, `CIL_ROLETRANSITION`, `CIL_BOOL`, `CIL_TUNABLE`, `CIL_ROLEALLOW`, and `CIL_AVRULE` are central assertions.

Because the test includes private headers and forward-declares private helpers, it is coupled to libsepol's internal AST builder contracts rather than only public CIL APIs.

## Risks and Maintenance Notes

- The tests are brittle by design: many assertions depend on exact parse-tree layout through chained `next`/`cl_head` accesses. Changes in `gen_test_tree` or parse-tree shape can break many tests even if high-level CIL semantics remain correct.
- Several success tests only assert `SEPOL_OK` and do not inspect all generated fields. This gives broad grammar coverage but may miss subtle field-assignment regressions.
- Memory management is fixture-oriented. Many initialized trees, databases, lists, and AST nodes are not destroyed in each test, so leak detectors may require test harness-specific suppression or cleanup outside this chunk.
- Some negative cases inject malformed state by mutating linked-list pointers directly. This is useful for defensive-code coverage, but it can produce states a real parser may never create.
- Domain checks in constraint expressions are security-relevant. Regressions here could allow invalid SELinux constraint expressions into later policy compilation phases.
- The chunk boundary cuts through `test_cil_gen_avrule_targetemptyparen_neg`; any merged research must combine this report with the following chunk to avoid treating the AV-rule target-empty case as fully covered here.

## Test Signals

Strong test signals in this chunk:

- Repeated positive/negative pairs for each generator make expected grammar shape explicit.
- Null input tests cover defensive API contracts.
- Extra-token and list-vs-scalar tests cover parser strictness.
- Duplicate permission insertion asserts `SEPOL_EEXIST`.
- Artificial symtab destruction asserts `SEPOL_ENOMEM` propagation.
- Constraint-expression tests cover many valid and invalid SELinux/MLS operator-domain combinations.
- Selected data assertions confirm AST flavor, allocated data presence, boolean values, strings copied from parse nodes, and permission-list item flavors.

Weak or absent signals:

- No end-to-end `cil_build_ast` traversal is covered in this chunk; those tests appear later in the file.
- No compiled binary policy comparison is performed.
- Most tests do not verify cleanup side effects.
- Many generated AST structs are checked only for non-null data and flavor, not full field-by-field equivalence.
