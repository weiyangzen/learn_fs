# Research: subset-b-008353

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_build_ast.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_build_ast.c

## Purpose

`cil_build_ast.c` converts the parser tree for SELinux CIL policy input into the typed CIL AST used by later libsepol phases. It is the first major semantic pass after parsing: it verifies list shapes, allocates the correct `cil_*` structures, attaches them to `cil_tree_node` objects, inserts declarative objects into the appropriate symbol tables, records source locations, and rejects statements that are syntactically valid but illegal in the current AST context.

The file also owns many destroy routines for AST payload structures created here. Those destructors encode the ownership model: most strings are interned or parser-owned pointers and are not freed, while lists, anonymous embedded contexts/levels, ebitmaps, and symtab datums are destroyed by the matching payload destructor.

## Important APIs, Types, and Functions

`struct cil_args_build` is the walker state passed through `cil_tree_walk`. It tracks the current destination AST node plus contextual ancestors that affect legality: active `tunif`, `in`, `macro`, `optional`, and `boolif` nodes.

Declaration helpers include `cil_gen_declared_string`, `cil_allow_multiple_decls`, `cil_add_decl_to_symtab`, `cil_gen_node`, and `cil_clear_node`. `cil_gen_node` is the central declaration path: it verifies the name, finds the parent namespace symbol table, sets node data/flavor, inserts the datum, and checks macro parameter shadowing. `cil_add_decl_to_symtab` handles duplicate declaration policy, allowing configured multiple declarations for selected flavors and special repeated declarations for optionals and policycaps.

Syntax and list helpers include `cil_fill_list`, `cil_fill_perms`, `cil_fill_classperms`, `cil_fill_classperms_list`, `cil_gen_expr`, `cil_gen_constraint_expr`, `cil_fill_context`, `cil_fill_levelrange`, `cil_fill_level`, `cil_fill_cats`, `cil_fill_integer`, `cil_fill_integer64`, and `cil_fill_ipaddr`. These helpers translate parse-tree list/string forms into CIL list structures and embedded payload objects.

Generator functions cover nearly the full CIL statement surface: blocks, inheritance, macros and calls, classes, commons, permissions, classpermissions, users, roles, types, aliases, attributes, booleans, tunables, conditionals, AV rules, extended permissions, type and range transitions, MLS sensitivities/categories/levels, constraints, contexts, labeling statements, defaults, policycaps, `handleunknown`, `mls`, and source-info records. `parse_statement` is the large keyword dispatcher that maps `CIL_KEY_*` interned strings to those generator functions.

Destroy functions mirror the generator families. Important patterns include `cil_destroy_classperms_list` deep-destroying mixed classperm/classperm-set items, `cil_destroy_*attributeset` destroying string and datum expression lists with different ownership flags, `cil_destroy_context` destroying anonymous level ranges only when `range_str` is absent, and `cil_destroy_block` unlinking blockinherit back-references from `bi_nodes`.

## Control Flow

`cil_build_ast` initializes `cil_args_build` and walks the parse tree with `cil_tree_walk`. `__cil_build_ast_node_helper` processes only list heads, rejects empty non-root lists, runs `check_for_illegal_statement`, calls `parse_statement`, then advances the current AST pointer to the newly created node. For leaf-like statements it sets `CIL_TREE_SKIP_NEXT` so the walker does not descend into data lists that are not policy statement bodies.

`__cil_build_ast_first_child_helper` records context when the current AST node is a tunableif, in-statement, macro, optional, or booleanif. `__cil_build_ast_last_child_helper` pops the AST pointer back to the parent, clears contextual state, restores outer optional state for nested optionals, and destroys converted parse-tree children to reduce peak memory use.

Most `cil_gen_*` functions follow the same pattern: check arguments, verify exact parse syntax through `__cil_verify_syntax`, allocate/init the payload, read interned strings or child lists from the parse tree, perform statement-specific keyword/value checks, assign `ast_node->data` and `ast_node->flavor`, and return `SEPOL_OK`. On failure they log a statement-specific message, destroy partially initialized payloads, and clear declarative AST nodes when needed.

Expression parsing is recursive. Generic set and conditional expressions map interned operator strings to `CIL_AND`, `CIL_OR`, `CIL_NOT`, `CIL_EQ`, `CIL_NEQ`, `CIL_XOR`, `CIL_ALL`, and `CIL_RANGE`, verify the operator grammar for the target flavor, and build nested `cil_list` stacks. Constraint expressions use a separate operator and operand grammar because left/right operands may be constraint slots such as `u1`, `r2`, `t3`, or MLS low/high fields.

## State and Persistence Behavior

The AST build is in-memory only. Persistent effects are mutations to the caller-owned `cil_db`, AST tree, symbol tables, and helper lists. New declarations are inserted into namespace symbol tables found by `cil_get_symtab`; root-level declared strings are added to the root string symtab and `db->declared_strings`. Repeated declarations can cause a node to reuse an existing datum rather than keep the newly allocated payload.

Some generators deliberately mutate the parse tree while building the AST. `cil_gen_boolif` and `cil_gen_tunif` remove the parsed expression subtree after translating it to `str_expr`. `cil_gen_macro` removes the macro parameter list so the walker processes only macro body statements. The last-child walker destroys parse-tree children once converted.

Strings are compared by pointer against `CIL_KEY_*` constants, so this file assumes parser/strpool interning. Numeric and IP address fields are materialized into integer or `inet_pton` binary forms when the grammar permits literal values, while unresolved identifiers remain as `*_str` pointers for later resolution.

## Dependencies and Integration Points

This file integrates with `cil_parser` parse-tree nodes, `cil_verify` syntax/name/expression validators, `cil_symtab` namespace storage, `cil_tree` traversal and destruction, `cil_list`, `cil_mem` allocators, `cil_log`, `cil_strpool`, and libsepol policy constants such as `POLICYDB_VERSION_COND_XPERMS` and unknown-class handling values. It calls `cil_copy_ast` when preserving macro call argument trees.

Later CIL phases depend on its exact flavor assignment, symbol-table insertion, `*_str` fields, anonymous embedded objects, and expression stack shape. The copy/resolve/compiler phases also rely on destructor ownership conventions established here.

## Risks and Edge Cases

The large `parse_statement` dispatch table is a maintenance hotspot: adding a CIL keyword requires coordinated syntax verification, generator/destroy/copy support, legality checks, and later resolver support. Missing one of those can produce parse acceptance followed by later resolution or copy failures.

Duplicate declaration handling is subtle. Some duplicate declarations intentionally reuse existing datums, while others are fatal. The code must destroy abandoned newly allocated payloads on `SEPOL_EEXIST` paths to avoid leaks and must avoid clearing AST nodes that were rebound to existing datums.

The build pass relies heavily on interned pointer equality for keyword checks. Any caller that bypasses the normal parser/string pool would break keyword matching. Context restrictions are also centralized in `check_for_illegal_statement`; new container flavors or conditional-rule allowances must be added there.

Error cleanup has many partial-object paths. Embedded anonymous objects such as contexts, level ranges, category expressions, and permissionx objects are owned only under certain `*_str == NULL` conditions, so regressions can double-free or leak. Range parsers validate shape and integer conversion but generally do not enforce ordering such as low <= high in this file; later validation must cover semantic consistency.

## Test Signals

Good test coverage should compile valid CIL containing every major statement family and assert successful AST build plus later resolution. Negative tests should cover duplicate declarations, illegal statements inside macro/optional/in/booleanif/tunableif contexts, invalid boolean/default/handleunknown/file type keywords, malformed class-permission and constraint expressions, excessive class permission counts, invalid numeric ranges, invalid IP literals, macro parameter shadowing and duplicate parameters, and `preserve_tunables` behavior.

Memory tests should run malformed-policy corpora under ASan/Valgrind because most risk is partial-construction cleanup. Regression tests should specifically exercise block inheritance, macro calls with copied argument trees, named versus anonymous contexts/levels/ranges, declared-string parameters, and policy-version gating for conditional extended permissions.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_build_ast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_build_ast.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_build_ast.h

## Purpose

`cil_build_ast.h` declares the public build-AST interface for CIL parser-tree conversion and exposes many statement-specific generator, filler, and destructor helpers used by neighboring CIL implementation files. It is broader than a minimal interface: besides `cil_build_ast`, it exports construction/destruction routines for most AST payload types, symbol-table declaration helpers, expression/list fillers, integer/IP parsing helpers, and context/MLS helpers.

## Important APIs, Types, and Functions

The main entry point is `cil_build_ast(struct cil_db *db, struct cil_tree_node *parse_tree, struct cil_tree_node *ast)`, which turns a parse tree into a typed AST rooted at `ast`.

Core declaration APIs are `cil_add_decl_to_symtab`, `cil_gen_declared_string`, and `cil_gen_node`. These are important integration points for code that constructs AST nodes outside the main parser walk because they preserve name validation, namespace lookup, duplicate declaration policy, and macro-parameter shadowing checks.

The header groups most CIL statement families as generator/destroy pairs: blocks and inheritance, classes/common/permissions/classpermission sets, SIDs, users, roles, types and aliases, booleans/tunables/conditionals, AV/type rules, MLS sensitivity/category/level constructs, constraints, contexts, labeling statements, macros/calls, optionals, policycaps, IP addresses, bounds, defaults, `handleunknown`, `mls`, and source-info records.

Helper exports include `cil_gen_expr`, `cil_gen_constrain_expr`, `cil_fill_classperms_list`, `cil_destroy_classperms_list`, `cil_fill_levelrange`, `cil_fill_context`, `cil_fill_cats`, `cil_fill_integer`, `cil_fill_integer64`, `cil_fill_ipaddr`, and `cil_fill_level`.

## Control Flow and Integration

This header does not implement control flow, but its declarations define the build contract used by `cil_build_ast.c` and by other CIL phases that need to create or destroy compatible AST payloads. The caller provides a `cil_db` for policy options and symbol tables, parse/AST tree nodes from `cil_tree`, and flavor/symbol-table constants from `cil_flavor` and `cil_symtab`.

Many functions accept `struct cil_tree_node *parse_current` plus `struct cil_tree_node *ast_node`; generators generally read parse-node siblings, fill `ast_node->data`, and set `ast_node->flavor`. Destroy functions accept payload pointers, not tree nodes, reflecting that tree destruction dispatches separately by flavor.

## State and Persistence Behavior

The header exposes routines that mutate caller-owned AST nodes, symbol tables, and `cil_db` auxiliary lists. It does not define any persistent on-disk behavior. The declared APIs assume the same ownership model as the implementation: interned strings and resolved datum references are usually shallow-owned, while expression lists, anonymous nested contexts/levels/ranges, ebitmaps, and symtab datums are owned by the payload destructor that matches the payload flavor.

## Dependencies

The header includes `stdint.h`, `cil_internal.h`, `cil_flavor.h`, `cil_symtab.h`, `cil_tree.h`, and `cil_list.h`. Those dependencies expose internal CIL payload structs and make this a private/internal libsepol header rather than a narrow external API.

## Risks and Maintenance Notes

Because this header exports a very large surface, drift between declarations and implementation is a risk. In this snapshot, some compatibility-style declarations, such as flavor-specific bounds generator names and some list/constrain helpers, are not defined under those exact names in the companion `cil_build_ast.c`; the implementation instead uses generic helpers such as `cil_gen_bounds` in the dispatcher. Consumers should verify exact symbol availability before depending on those names.

The many exported destroy functions make ownership discipline visible but also fragile: a caller can easily use a destructor for a partially initialized object or an object whose nested `*_str` fields determine ownership. Any new AST payload field must be reflected in both the implementation destructor and, if external construction is needed, the header contract.

## Test Signals

Build tests should catch header/source drift by compiling every CIL source file that includes this header with warnings enabled. API-level tests should exercise construction/destruction of payloads through declared helpers, especially anonymous contexts/levels/ranges, expression lists, classpermissions, and duplicate symbol-table declarations. Link tests are useful because stale declarations can compile but fail when an external user references a function not implemented under the advertised name.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_build_ast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_copy_ast.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_copy_ast.c

## Purpose

`cil_copy_ast.c` deep-copies CIL AST subtrees into another AST location while preserving the semantic ownership rules needed by block inheritance, macro calls, in-statements, and cloned policy fragments. It creates new tree nodes and new payload structs, rebuilds symbol-table entries for declarative nodes, shallow-copies interned strings and already-resolved datum references where appropriate, and deep-copies mutable nested structures such as expression lists, anonymous contexts, levels, level ranges, IP addresses, and classpermission lists.

## Important APIs, Types, and Functions

`struct cil_args_copy` carries the original destination (`orig_dest`), current destination parent (`dest`), and `cil_db` through the tree walker. `cil_copy_ast` is the public entry point and treats `dest` as the parent node into which copied children are appended.

Generic copying helpers include `cil_copy_list`, `cil_copy_expr`, `cil_copy_classperms`, `cil_copy_classperms_set`, `cil_copy_classperms_list`, `cil_copy_fill_level`, `cil_copy_fill_levelrange`, `cil_copy_fill_context`, and `cil_copy_fill_ipaddr`. These preserve interned string/datum pointer identity while allocating new list and embedded object containers.

There are copy routines for most AST payload families: ordered lists, blocks, blockabstract/blockinherit, policycaps, permissions, class mappings and classpermissions, SID/user/role/type declarations and set statements, aliases, transitions, bool/tunable conditionals, AV and extended-permission rules, deny/type rules, MLS constructs, contexts and labeling statements, constraints, macros/calls, optionals, defaults, bounds, `handleunknown`, `mls`, and source-info records.

`__cil_copy_node_helper` is the dispatch and insertion engine. It maps `orig->flavor` to the correct copy function, locates a destination symbol table for declarative flavors, invokes the copy routine, creates the destination tree node, updates declaration symbol tables with `cil_add_decl_to_symtab`, enforces flavor compatibility, updates blockinherit back-references, appends the new node to the parent, and descends into children when present.

## Control Flow

`cil_copy_ast` initializes walker state and calls `cil_tree_walk(orig, __cil_copy_node_helper, NULL, __cil_copy_last_child_helper, &extra_args)`. The node helper handles a pre-order copy: select copy routine by flavor, copy payload data, allocate a new `cil_tree_node`, attach it to the destination parent, and if the source has children, set `args->dest` to the new node so child copies nest below it. The last-child helper pops `args->dest` back to the parent after a child subtree is complete.

Declarative nodes take an additional path. For flavors at or above `CIL_MIN_DECLARATIVE`, the helper converts flavor to symbol-table index, finds the destination namespace symbol table, and inserts the copied datum using the original datum name. Duplicate block and macro behavior is special for block inheritance: duplicate blocks can append another node to an existing datum, and duplicate macros may be skipped only while inheriting a block. Other incompatible or duplicate named objects generally produce errors.

Some payload copy routines allocate only a fresh initialized declaration object and let `__cil_copy_node_helper` set datum metadata through symbol-table insertion. Nondeclarative payloads copy statement fields directly. `cil_copy_call` recursively copies a call's `args_tree`, preserving macro pointer and copied flag. `cil_copy_avrule` branches between normal classperms lists and inline/named extended permissionx payloads.

## State and Persistence Behavior

The copy is in-memory and mutates the destination AST and its symbol tables. It does not clone all semantic state: many resolved pointers are shallow-copied, including interned strings, existing datums in expression lists, alias actual pointers, block references, class/common references, macro references, and declared-string references. This is intentional for data that is global, interned, or re-resolved later, but it means the copy is not an independent serialization boundary.

Expression and classpermission lists are structurally copied, so the copied tree can own its list containers independently. Anonymous embedded contexts, levels, ranges, category sets, and IP address values are copied into new allocations. Named references remain as strings or datums and are expected to resolve in the destination namespace.

For blockinherit nodes, if the referenced block is already resolved, the copied node is appended to `block->bi_nodes`; otherwise the resolver will handle it later. This allows copying before blockinherit resolution, especially for in-statement handling.

## Dependencies and Integration Points

The file depends on `cil_internal`, `cil_log`, `cil_mem`, `cil_tree`, `cil_list`, `cil_symtab`, `cil_copy_ast.h`, `cil_build_ast.h`, `cil_strpool`, and `cil_verify`. Its most important integration point is `cil_add_decl_to_symtab` from the build-AST layer, which keeps copied declarations consistent with normal declarations. It also relies on flavor-to-symtab mapping, tree walking, node-to-string logging, and datum macros such as `DATUM`, `FLAVOR`, and `NODE`.

`cil_build_ast.c` calls `cil_copy_ast` when preserving macro call argument trees. Resolver and inheritance code depend on this file to clone AST fragments without corrupting namespaces or losing source location metadata.

## Risks and Edge Cases

The dispatch switch must stay synchronized with all AST flavors. Adding a new flavor without a copy case causes subtree copy failures for policies that use the new construct in macros, block inheritance, or other clone paths.

Shallow versus deep copy boundaries are subtle. Resolved pointers copied from the source may be correct for shared global datums but dangerous if a future field points into a namespace-specific or lifetime-limited object. Conversely, deep-copying datum references incorrectly would break identity expectations used by later phases.

Duplicate handling differs by construct. Blocks and macros have special inheritance behavior, while named classpermissions, permissionx, catsets, levels, levelranges, contexts, and IP addresses reject redefinition. This can surface only in clone paths, so normal parser tests may miss it.

There are implementation details worth watching: `cil_copy_condblock` initializes through a local `new = *copy` even though callers pass an uninitialized `data` pointer variable; it then overwrites `*copy` after init, so behavior depends on the init routine not reading the incoming pointer value. Header/source drift also exists for several exact copy-helper names exposed in the header but implemented through generic or static helpers in this file.

## Test Signals

Tests should copy AST fragments containing every supported flavor through macro call arguments, block inheritance, and nested blocks. Assertions should verify destination tree shape, source line/hll offset preservation, symbol-table insertion, duplicate declaration behavior, and that inherited duplicate blocks/macros behave differently from ordinary redefinitions.

Memory and lifetime tests should stress copying of anonymous contexts, levels, ranges, category sets, expression lists, permissionx expressions, call argument trees, and blockinherit back-reference lists under ASan/Valgrind. Negative tests should include incompatible duplicate declarations in a destination namespace, duplicate named anonymous-capable objects, unknown flavor handling, and copy failures inside recursive call-argument trees.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_copy_ast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_copy_ast.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_copy_ast.h

## Purpose

`cil_copy_ast.h` declares the internal API for copying CIL AST payloads and whole AST subtrees. It is used by code that needs to clone policy fragments while preserving CIL tree, symbol-table, and payload ownership conventions, especially macro argument preservation and block/inheritance expansion.

## Important APIs, Types, and Functions

The main entry point is `cil_copy_ast(struct cil_db *db, struct cil_tree_node *orig, struct cil_tree_node *dest)`. `dest` is the parent node receiving copied children; for macro calls it may be the call node itself, as noted by the companion source comment.

General helpers include `cil_copy_list` for generic CIL lists, `cil_copy_expr` for expression stacks, `cil_copy_classperms`, `cil_copy_classperms_set`, `cil_copy_classperms_list`, `cil_copy_fill_level`, `cil_copy_fill_levelrange`, `cil_copy_fill_context`, and `cil_copy_fill_ipaddr`.

The header declares copy routines for declaration and statement payload families: blocks, classes, permissions, classpermissions, SIDs, users, roles, types, bounds, aliases, transitions, booleans, AV/type rules, MLS sensitivity/category/level structures, contexts, labeling statements, constraints, calls, optionals, IP addresses, and boolean conditionals.

## Control Flow and Integration

The header itself has no control flow, but it defines the function-pointer-compatible copy routine shape used by the implementation: most payload copy functions accept `struct cil_db *db`, source `void *data`, destination `void **copy`, and destination `symtab_t *symtab`. This uniform signature lets the implementation dispatch by `enum cil_flavor` during `cil_tree_walk`.

Consumers include build-AST and later CIL transformation code. The header includes `cil_internal.h`, `cil_tree.h`, and `cil_symtab.h`, so it is coupled to internal payload definitions and namespace types.

## State and Persistence Behavior

Copy routines declared here mutate caller-owned destination AST nodes and symbol tables. They do not persist data to disk. The interface implies a mixed ownership model: callers receive newly allocated payload/list containers where appropriate, but many strings and resolved datum pointers are shallow-copied because CIL strings are interned and datums often represent shared semantic declarations.

## Dependencies

This header depends directly on internal CIL structures, tree nodes, and symbol tables. Its declarations are intended to match `cil_copy_ast.c`, `cil_build_ast.c` destructors, and flavor definitions from `cil_flavor`.

## Risks and Maintenance Notes

The exported surface is broad and includes some names not defined under the same exact names in the companion source snapshot, such as `cil_copy_permset`, `cil_copy_common`, flavor-specific bounds aliases, exact alias helper names, and `cil_copy_exrp`. The source dispatch uses generic/static routines for several of these roles. Direct external references to stale declarations would be caught only at link time.

Because many helpers expose partially deep-copying semantics, callers must understand which fields are newly allocated and which are shared. Misusing these helpers as if they produced a fully independent clone can create dangling references or namespace confusion when copied fragments outlive their original semantic context.

## Test Signals

Compile/link tests should include code paths that reference exported copy helpers to detect declaration drift. Behavioral tests should call `cil_copy_ast` over representative AST fragments and verify copied payload ownership by destroying both original and copy under sanitizers. Tests should cover list/expression copying, classpermissions, anonymous contexts/levels/ranges, IP address values, duplicate destination declarations, and blockinherit/macro-specific copy behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_copy_ast.h -->
