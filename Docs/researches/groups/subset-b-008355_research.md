# sources/security-integrity/selinux/libsepol/cil/src subset-b-008355 research

Grouped research for the CIL AST reset, resolve, stack, string pool, symbol table, tree, and verification files. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_reset_ast.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_reset_ast.c

## Purpose

`cil_reset_ast.c` clears resolution-time state from a CIL AST so the same tree can be re-resolved after optional blocks are disabled or declarations are otherwise invalidated. It deliberately preserves parse/build-time strings and structural AST nodes while nulling resolved pointers, destroying derived datum-expression lists, clearing ordering flags, and undoing class/common permission value shifts.

## Important APIs, Types, and Functions

The public API is `cil_reset_ast(struct cil_tree_node *current)`, which walks a subtree with `cil_tree_walk()` and dispatches by `node->flavor` in `__cil_reset_node()`. The file contains many flavor-specific reset helpers: class/common and permission helpers (`cil_reset_class()`, `cil_reset_perm()`, `cil_reset_classperms_list()`), alias/bounds helpers (`cil_reset_alias()`, `cil_reset_user()`, `cil_reset_role()`, `cil_reset_type()`), expression-holder resetters for user/role/type attributes and constraints, MLS helpers (`cil_reset_cats()`, `cil_reset_level()`, `cil_reset_levelrange()`), context-bearing object resetters, SID/order resetters, and default/boolean-if cleanup.

## Control Flow

`cil_reset_ast()` calls `cil_tree_walk(current, __cil_reset_node, NULL, NULL, NULL)`. For each AST node, the dispatcher resets only derived fields for that flavor. Nested objects are handled explicitly: class permission lists are traversed item by item, anonymous `level`, `levelrange`, and `context` objects are recursively reset, while named references are set back to `NULL` for later name resolution.

## State and Persistence Behavior

The reset operation mutates the AST in place. It destroys derived `cil_list` containers but normally passes `CIL_FALSE` so referenced datums are not freed. It clears pointers such as `alias->actual`, `user->bounds`, `role->bounds`, `type->bounds`, resolved contexts, resolved MLS ranges, and resolved class permissions. For class/common relations, it subtracts the common permission offset from class permission values and resets `class->num_perms` to local permissions. This makes the next resolver pass behave as if common association had not yet occurred.

## Dependencies and Integration Points

This file depends on `cil_tree_walk()` from `cil_tree.c`, `cil_list_destroy()` and list iteration macros, symbol-table mapping through `cil_symtab_map()`, logging, and the large CIL data model in `cil_internal.h`. Its main integration point is `cil_resolve_ast()`, which calls `cil_reset_ast()` after optional-block removal containing declarations requires resolution to restart.

## Risks and Edge Cases

The code assumes fields follow ownership conventions: named references are not destroyed, anonymous subobjects are recursively reset, and derived lists can be destroyed without freeing their datum payloads. The manual expression-list cleanup for attributes avoids destroying nested expression stacks, but is easy to get wrong if list ownership changes. Class common reset is subtle because permission values are shifted during resolution and must be shifted back exactly once. A missing flavor in `__cil_reset_node()` can leave stale state across re-resolution.

## Test Signals

Useful tests include policies with disabled optionals containing declarations, repeated classcommon resolution after reset, anonymous and named contexts/ranges through filecon, sidcontext, and userrange, attribute set expressions resolved before and after reset, and classpermission/classmapping constructs using nested sets. Memory-checking tests should ensure list containers are freed while datums remain valid for the next pass.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_reset_ast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_reset_ast.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_reset_ast.h

## Purpose

`cil_reset_ast.h` declares the reset pass used to clear resolution-derived AST state before re-running resolver passes.

## Important APIs, Types, and Functions

The header includes `cil_tree.h` and exports `int cil_reset_ast(struct cil_tree_node *current);`. The parameter is the subtree root to reset; the return value follows libsepol `SEPOL_OK`/`SEPOL_ERR` conventions.

## Control Flow and Integration

Callers supply a resolved or partially resolved AST node. The implementation performs a depth-first tree walk and mutates nodes in place. The primary caller is the resolver when disabled optional blocks force declaration reset.

## State, Dependencies, and Risks

The API exposes no ownership details, so callers must know it preserves AST structure while clearing derived fields. It depends on `struct cil_tree_node` being visible. The main risk is calling it on a subtree that should retain resolution products; all supported CIL flavors under that subtree may have resolved pointers and derived lists cleared.

## Test Signals

Compile-time coverage should catch signature drift. Behavioral coverage belongs with resolver tests that trigger `cil_reset_ast()` and then successfully complete a second resolution pass.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_reset_ast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_resolve_ast.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_resolve_ast.c

## Purpose

`cil_resolve_ast.c` is the core CIL name-binding and semantic expansion pass. It turns strings and parse-time lists into pointers to `cil_symtab_datum` objects, expands `in`, `blockinherit`, macro calls, and tunable conditionals, merges global ordering statements, resolves aliases, binds policy rules to classes/types/roles/users/MLS objects, and enforces placement restrictions while walking the AST in a defined pass order.

## Important APIs, Types, and Functions

The central public entry point is `cil_resolve_ast(struct cil_db *db, struct cil_tree_node *current)`. Name lookup is exposed through `cil_resolve_name()` and `cil_resolve_name_keep_aliases()`, with macro-argument lookup in `cil_resolve_name_call_args()`. Rule and object APIs include `cil_resolve_avrule()`, `cil_resolve_deny_rule()`, `cil_resolve_type_rule()`, `cil_resolve_nametypetransition()`, `cil_resolve_rangetransition()`, `cil_resolve_context()`, and the file/network/device context resolvers. Expression binding is handled by `cil_resolve_expr()`, `cil_resolve_boolif()`, and tunable-specific evaluation helpers. Class permission APIs include `cil_resolve_classperms()`, `cil_resolve_classperms_list()`, `cil_resolve_classpermissionset()`, `cil_resolve_classcommon()`, and `cil_resolve_classmapping()`. Ordering APIs include `cil_resolve_sidorder()`, `cil_resolve_classorder()`, `cil_resolve_catorder()`, and `cil_resolve_sensitivityorder()`.

`struct cil_args_resolve` carries pass-local state: current `db`, resolver pass, changed flag, delayed-destroy list, active block/macro/optional/booleanif context, lists of order statements, before/after `in` statements, and abstract blocks.

## Control Flow

Resolution is multi-pass. `cil_resolve_ast()` initializes tracking lists, then iterates from `CIL_PASS_TIF` to `CIL_PASS_NUM`, calling `cil_tree_walk()` with node, first-child, and last-child callbacks. `__cil_resolve_ast_node()` dispatches by pass and node flavor. Early passes evaluate tunableifs, collect and resolve `in` statements, link and copy block inheritance, mark abstract blocks, copy macro bodies, then resolve macro arguments. Alias passes bind aliasactual statements and collapse alias chains. Later passes resolve ordering, MLS catsets and senscat links, then all remaining policy declarations and rules.

After specific passes, `cil_resolve_ast()` performs batch work: resolves collected `in` lists, marks abstract block subtrees, checks inheritance explosion and loops, merges order lists into `db->sidorder`, `db->classorder`, `db->catorder`, and `db->sensitivityorder`, sets category values, and verifies all SID/class/category/sensitivity declarations are ordered. If an optional block fails lookup, the helper records the optional as disabled; when leaving that subtree, it marks the tree changed and schedules children for destruction. If destroyed optionals contained declarations after macro-copying, resolution resets derived declarations with `cil_reset_ast()` and restarts after `CIL_PASS_CALL1`.

Name lookup first searches visible parent scopes through blocks, blockinherit source parents, macros, calls, and macro arguments, then falls back to root symtabs. In non-qualified mode, dotted names are parsed as explicit block paths unless the name starts with a leading dot, which starts at root. `cil_resolve_name()` normally follows type/sensitivity/category aliases to their actual datums after alias passes.

## State and Persistence Behavior

The resolver mutates AST objects by filling resolved pointers and derived datum lists. It appends resolved attribute expressions to the target attribute's `expr_list`, records user default levels and ranges on `struct cil_user`, stores SID contexts on `struct cil_sid`, adds blockinherit users to `block->bi_nodes`, copies AST subtrees for `in`, blockinherit, macro calls, and selected tunableif branches, and updates database-global ordered lists and category counts. Class common resolution shifts permission values and increments class permission counts. Type attributes record usage bits for expansion, constraints, allow rules, and neverallow rules.

The pass keeps temporary lists and destroys them on exit. Optional disabling does not remove the optional node immediately; it destroys its children after the current traversal and may force a reset/re-resolve cycle.

## Dependencies and Integration Points

The resolver is tightly integrated with `cil_tree` traversal/logging, `cil_symtab` lookup and removal/reinsertion, `cil_copy_ast`, `cil_reset_ast`, `cil_build_ast` anonymous object fill helpers, `cil_verify` ordering checks, `cil_list`, `cil_stack`, and `cil_internal` data definitions. It consumes `enum cil_pass` and `enum cil_sym_index` from the broader CIL internals. It is normally followed by pre/post verification and later policydb conversion.

## Risks and Edge Cases

Resolution order is a major risk: changing pass order can break macros, optional handling, inheritance, alias following, and ordered-list validation. Optional-block disablement is deliberately non-fatal for unresolved names but can require reset of already-derived state. Macro argument resolution temporarily removes local datums if an argument accidentally resolves to a declaration copied inside the call. Inheritance checks limit degenerate exponential copying and detect loops. Dotted name resolution has different behavior depending on `db->qualified_names`, leading dots, abstract blocks, and use in `in` statements. Anonymous levels, ranges, catsets, classpermissions, and IP addresses must be resolved inline because they may never appear in a normal symbol table.

## Test Signals

High-value tests include alias chains and alias loops, optionals that fail inside and outside declarations, macro recursion and macro parameter shadowing, `in` before/after ordering, blockinherit loops and explosive nested inheritance, mixed classorder/unordered classorder merges, category value ordering, anonymous and named MLS ranges, booleanif/tunableif branch copying, xperms resolution, and dotted scope lookup with root-qualified and relative names.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_resolve_ast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_resolve_ast.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_resolve_ast.h

## Purpose

`cil_resolve_ast.h` publishes the CIL resolver interface. It exposes both the full AST resolution pass and many flavor-specific helper functions used by other compilation phases or tests.

## Important APIs, Types, and Functions

The primary API is `cil_resolve_ast(struct cil_db *db, struct cil_tree_node *current)`. The header also declares resolver functions for class permissions, rules, aliases, bounds, users, roles, MLS categories/levels/ranges, constraints, contexts, context-bearing statements, ordering statements, block inheritance, `in`, macro calls, expressions, booleanifs, tunableifs, and scoped name lookup. It includes `cil_internal.h` and `cil_tree.h`, so consumers see the CIL database and tree-node types.

## Control Flow and Integration

Most declarations correspond to implementation dispatch cases in the multi-pass resolver. External code can call specific resolvers when constructing or testing individual AST fragments, but normal policy compilation should call `cil_resolve_ast()` so pass ordering, delayed `in` resolution, optional handling, and ordered-list merging are all honored.

## State and Persistence Behavior

The declared functions generally mutate AST nodes and database fields in place, converting string fields to resolved datum pointers or derived lists. Name lookup APIs return borrowed datum pointers owned by the relevant symtab/datums, not newly allocated copies.

## Dependencies and Risks

The broad exported surface creates coupling to CIL internals and makes signature changes expensive. Calling helpers outside the full pass can bypass prerequisites such as alias processing, classcommon resolution, or MLS ordering. Callers must obey resolver state assumptions: valid `db`, built AST symtabs, and correct parse/build-time fields.

## Test Signals

Compile API tests should cover headers for downstream users. Behavioral tests should use both `cil_resolve_ast()` end-to-end and targeted helper tests for name lookup, expression resolution, class permissions, and context resolution.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_resolve_ast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_stack.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_stack.c

## Purpose

`cil_stack.c` implements a small growable stack used by CIL traversals and cycle checks. It stores pairs of `enum cil_flavor` and opaque data pointers.

## Important APIs, Types, and Functions

`cil_stack_init()` allocates a stack with initial capacity 16 and `pos = -1`. `cil_stack_destroy()` frees the backing array and stack object. `cil_stack_empty()`, `cil_stack_is_empty()`, and `cil_stack_number_of_items()` query or clear state. `cil_stack_push()` grows capacity by doubling with `cil_realloc()` and writes the next `cil_stack_item`. `cil_stack_pop()`, `cil_stack_peek()`, and `cil_stack_peek_at()` expose items by stack position.

## Control Flow

Push increments `pos` first, then resizes if the new position equals capacity. Pop returns `NULL` for an empty stack, otherwise decrements `pos` and returns a pointer to the previous top slot. `peek_at(stack, pos)` treats `pos` as an offset down from the current top.

## State and Persistence Behavior

The stack owns only its dynamic backing array, not `item.data`. Returned item pointers point into the internal array and remain valid only until the stack is mutated or destroyed.

## Dependencies and Integration Points

The implementation uses `cil_malloc()` and `cil_realloc()` from `cil_mem.h`. It is used by resolver inheritance-loop checks and verifier self-reference checks, through direct calls and the iteration macros from `cil_stack.h`.

## Risks and Test Signals

The API does not guard against `NULL` stack arguments except in destroy. Consumers must not retain returned item addresses across push operations that may reallocate. Tests should cover empty pop/peek, capacity growth beyond 16, `peek_at()` bounds, and iteration order expected by cycle detection.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_stack.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_stack.h

## Purpose

`cil_stack.h` defines the stack container and iteration macros used by resolver and verifier recursion checks.

## Important APIs, Types, and Functions

`struct cil_stack` contains the backing `stack` array, capacity `size`, and top index `pos`. `struct cil_stack_item` stores a CIL flavor tag plus opaque `data`. The macros `cil_stack_for_each_starting_at()` and `cil_stack_for_each()` iterate from the top downward through `cil_stack_peek_at()`. Function prototypes cover initialization, destruction, emptying, item counting, push, pop, peek, and indexed peek.

## Control Flow and Integration

The iteration macros are designed for stack-based ancestor checks, where offset zero is the current top. They are used by resolver inheritance checks and verifier self-reference checks to scan active recursion frames.

## State, Dependencies, and Risks

The header depends on `enum cil_flavor` being visible through prior includes in consumers. It does not enforce ownership for `data`; callers supply and retain pointee lifetimes. Macro arguments are evaluated multiple times in the `for` expansion through `cil_stack_peek_at()`, so callers should pass simple variables.

## Test Signals

Compile tests should include the header after the usual CIL internal headers. Runtime tests should verify macro traversal order and behavior when starting offsets are beyond stack depth.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_strpool.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_strpool.c

## Purpose

`cil_strpool.c` implements a process-global intern pool for strings. It deduplicates equal strings and returns stable canonical `char *` pointers so much of CIL can compare keywords and identifiers by pointer identity.

## Important APIs, Types, and Functions

`cil_strpool_init()` lazily creates a hashtab and increments a reader/reference count. `cil_strpool_add(const char *str)` looks up a string under a mutex, inserts a `cil_strdup()` copy if absent, and returns the canonical stored pointer. `cil_strpool_destroy()` decrements the reader count and destroys the pool when it reaches zero. Internal helpers implement djb-style hashing, `strcmp()` comparison, and entry destruction.

## Control Flow

All public operations lock `cil_strpool_mutex`. Add searches first; on miss it allocates `struct cil_strpool_entry`, duplicates the input string, inserts it using the duplicated string as the key, and exits the process on allocation/insert failure. Destroy maps entries to free both string and entry before destroying the hashtab.

## State and Persistence Behavior

The pool is static global state: `cil_strpool_tab` and `cil_strpool_readers` persist across CIL database instances. Canonical strings remain valid until the final matching destroy call. The reference count allows multiple users to share the pool, but the code assumes balanced init/destroy calls.

## Dependencies and Integration Points

The implementation uses pthread mutexes, libsepol `hashtab_t`, CIL memory helpers, and CIL logging. It underpins keyword and identifier identity comparisons throughout parser, resolver, verifier, and tree logging code.

## Risks and Test Signals

Unbalanced destroy can underflow `cil_strpool_readers` because it is unsigned and not guarded. Calling `cil_strpool_add()` before init would search a null hashtab. The table size is a power of two and the hash masks by `h->size - 1`, so changing size must preserve that assumption. Tests should cover duplicate string interning, concurrent adds of the same string, balanced multi-reader init/destroy, and misuse detection if the broader project has debug assertions.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_strpool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_strpool.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_strpool.h

## Purpose

`cil_strpool.h` declares the global string interning API used by CIL parsing and semantic phases.

## Important APIs, Types, and Functions

It includes libsepol `hashtab.h` and declares `cil_strpool_add()`, `cil_strpool_init()`, and `cil_strpool_destroy()`.

## Control Flow and State

Consumers initialize the pool before interning, call `cil_strpool_add()` for canonical pointers, and destroy when done. Returned strings are pool-owned.

## Dependencies, Risks, and Test Signals

Because much CIL code compares interned keys by pointer, callers must not pass non-interned strings where pointer identity is expected. Tests should verify that equal strings return identical pointers and that lifecycle calls bracket all parser/resolver use.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_strpool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_symtab.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_symtab.c

## Purpose

`cil_symtab.c` wraps libsepol symbol tables for CIL datums and implements a small complex-key symbol table used for duplicate/collision checks over multi-field rule keys.

## Important APIs, Types, and Functions

Basic datum APIs are `cil_symtab_init()`, `cil_symtab_datum_init()`, `cil_symtab_datum_destroy()`, `cil_symtab_insert()`, `cil_symtab_remove_datum()`, `cil_symtab_get_datum()`, `cil_symtab_map()`, and `cil_symtab_destroy()`. Complex-key APIs are `cil_complex_symtab_init()`, `cil_complex_symtab_insert()`, `cil_complex_symtab_search()`, and `cil_complex_symtab_destroy()`.

## Control Flow

Normal insertion delegates to `hashtab_insert()`. On success it sets datum `name`, `fqn`, owner `symtab`, increments `nprim`, and optionally records the AST node in `datum->nodes`. Removal deletes by `datum->name`, decrements `nprim`, and clears owner state. Destroy clears each datum's `symtab` back-pointer before destroying the underlying hashtab. Complex symtab insertion hashes four integer keys, keeps bucket lists sorted by key fields, rejects exact duplicates with `SEPOL_EEXIST`, and otherwise links a new node.

## State and Persistence Behavior

`struct cil_symtab_datum` owns a list of AST nodes referencing the declaration but not the symtab itself. `cil_symtab_datum_remove_node()` removes a node reference and destroys the datum if no nodes remain. Complex symtab nodes own only the wrapper node allocation; keys and datum payloads are external.

## Dependencies and Integration Points

The file depends on libsepol `symtab_t`/`hashtab_t`, CIL list/tree structures, memory helpers, string pool conventions, and logging. Resolver name lookup and tree destruction both rely on datum back-pointers and node lists being maintained correctly.

## Risks and Test Signals

Failure paths call `exit(1)` for allocation/symtab creation failures, so callers cannot recover. `cil_symtab_remove_datum()` assumes `datum->symtab` and `datum->name` are coherent. Complex symtab hashing assumes `nslots` is a power of two because `mask = size - 1`. Tests should cover duplicate insert, node-list removal and datum destruction, temporary remove/reinsert during macro argument resolution, map iteration, and complex-key search early-exit ordering.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_symtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_symtab.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_symtab.h

## Purpose

`cil_symtab.h` defines the CIL datum wrapper around libsepol symbol tables and the complex-key table types used by verification logic.

## Important APIs, Types, and Functions

`struct cil_symtab_datum` contains declaration nodes, simple name, fully qualified name, and owner symtab. Convenience macros `DATUM()`, `NODE()`, and `FLAVOR()` cast datums to their primary AST node/flavor. Complex-key types store four `intptr_t` keys, a payload wrapper, bucket nodes, and table metadata. The header declares all normal and complex symtab operations.

## Control Flow and Integration

Resolvers use the normal symtab API for scoped lookup and insertion. Tree destruction uses datum node lists to decide whether declaration payloads can be freed. Verifier code can use the complex symtab for multi-field duplicate detection, though some rule duplicate checks are currently disabled in comments.

## State, Dependencies, and Risks

The macros assume each datum has at least one node and that the first node is representative. That is invalid for partially initialized or already-destroyed datums. Complex-key structures do not own key payloads, so callers must manage key lifetime. The header depends on libsepol symtab/hashtab headers and `cil_tree.h`.

## Test Signals

Tests should cover macro behavior for datums with multiple nodes, compile inclusion order, complex symtab initialization with power-of-two slot counts, and destruction after partial insertion.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_symtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_tree.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_tree.c

## Purpose

`cil_tree.c` implements the CIL AST tree container, tree-node lifecycle, source-location logging, declarative-subtree detection, node removal, and depth-first traversal callbacks.

## Important APIs, Types, and Functions

Source helpers are `cil_tree_get_next_path()`, `cil_tree_get_cil_path()`, and `cil_tree_log()`. Lifecycle APIs include `cil_tree_init()`, `cil_tree_destroy()`, `cil_tree_subtree_destroy()`, `cil_tree_children_destroy()`, `cil_tree_node_init()`, `cil_tree_node_destroy()`, and `cil_tree_node_remove()`. Traversal is provided by `cil_tree_walk()` and internal `cil_tree_walk_core()`. `cil_tree_subtree_has_decl()` detects nodes with declarative flavors.

## Control Flow

Tree destruction recursively destroys children before destroying the node. Node destruction treats declarative datums specially: it removes the node from the datum's node list and destroys payload data only when the datum has no remaining nodes. Non-declarative nodes directly call `cil_destroy_data()`. `cil_tree_walk()` calls an optional `first_child` callback before descending into a child list, processes each child through `process_node`, respects `CIL_TREE_SKIP_NEXT` and `CIL_TREE_SKIP_HEAD`, recursively walks children, and calls `last_child` after a child list completes.

Source logging climbs parent/source metadata paths. It understands parse-tree `CIL_KEY_SRC_INFO` nodes, AST `CIL_SRC_INFO` nodes, and follows `CIL_CALL`/`CIL_BLOCKINHERIT` references back to macro or inherited block nodes to reconstruct user-facing source traces.

## State and Persistence Behavior

Each node stores parent, child head/tail, sibling next, flavor, CIL line, HLL offset, and payload pointer. Parent/child links are mutated by removal and child destruction. Logging does not alter tree state, but may traverse through resolved macro/blockinherit links. Node destruction also mutates symbol datum node lists.

## Dependencies and Integration Points

The tree layer depends on CIL internals, flavor names, list handling, parser/string conversion, string pool keys, and logging. It is the traversal backbone for reset, resolve, verification, build/copy, and cleanup passes.

## Risks and Test Signals

Destroy semantics are tied to declarative datum sharing; freeing too early would break aliases, inherited/copy nodes, or duplicate declarations, while failing to remove nodes leaks. `cil_tree_node_remove()` handles head/tail updates but assumes sibling links are valid. Traversal callbacks can mutate the tree, so pass code must be careful with delayed destruction. Tests should cover traversal skip flags, source trace generation through macros and blockinherit, node removal at head/tail/middle, declarative datum with multiple nodes, and recursive subtree destruction.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_tree.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_tree.h

## Purpose

`cil_tree.h` defines the AST node shape and traversal API used by the CIL compiler.

## Important APIs, Types, and Functions

`struct cil_tree` stores the root node. `struct cil_tree_node` stores parent, child head/tail, next sibling, `enum cil_flavor`, line, HLL offset, and payload data. The header declares source-path helpers, logging, declaration detection, tree/node lifecycle, node removal, and `cil_tree_walk()`. It defines traversal skip flags: `CIL_TREE_SKIP_NOTHING`, `CIL_TREE_SKIP_NEXT`, `CIL_TREE_SKIP_HEAD`, and `CIL_TREE_SKIP_ALL`.

## Control Flow and Integration

`cil_tree_walk()` is the shared depth-first traversal primitive for resolver, resetter, and verifier passes. Callbacks can process nodes, observe entering/leaving child lists, and request branch skipping through the `finished` mask.

## State, Dependencies, and Risks

The header depends on `cil_flavor.h` and `cil_list.h`. It exposes raw tree structure, so callers can mutate links directly; that is powerful but risks parent/tail inconsistencies if not done carefully. Traversal skip constants are bit flags and must remain compatible with all walkers.

## Test Signals

Tests should compile users of the public struct layout, validate skip behavior, and verify lifecycle functions leave destroyed pointers null.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_verify.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_verify.c

## Purpose

`cil_verify.c` performs syntax and semantic checks that complement AST building and resolution. It validates identifier names, expression syntax, constraint expression legality, conditional blocks, macro parameter shadowing, self-referential attributes, ordered-list completeness, MLS ranges, users/roles/types/bounds, contexts, booleanif contents, extended permissions, class/common permission collisions, map-class classpermissions, and selected policy-global uniqueness.

## Important APIs, Types, and Functions

Public helpers include `cil_verify_name()`, `__cil_verify_syntax()`, `cil_verify_expr_syntax()`, `cil_verify_constraint_leaf_expr_syntax()`, `cil_verify_constraint_expr_syntax()`, `cil_verify_conditional_blocks()`, `cil_verify_decl_does_not_shadow_macro_parameter()`, `__cil_verify_ranges()`, `cil_verify_completed_ordered_list()`, `__cil_verify_ordered()`, `__cil_verify_initsids()`, `__cil_verify_senscat()`, `__cil_verify_helper()`, and `__cil_pre_verify_helper()`. Internal helpers cover reserved names, no-self-reference recursion, MLS/category checks, pre/post user validation, role/type circular bounds, context validity, booleanif subtree validation, per-context statement checks, permissionx verification, class verification, policycap lookup, and classpermission/map-class recursion.

## Control Flow

Name verification checks null, length, first character, allowed characters depending on `db->qualified_names`, and flavor-specific reserved words. Syntax verification walks parse sibling nodes against `enum cil_syntax` masks, including variadic list/string tails. Constraint and expression syntax layer operator-specific shape rules on top.

Pre-verification (`__cil_pre_verify_helper`) skips macros and abstract blocks, checks users before evaluation, validates map classes and classpermissions, and uses `cil_stack` to detect self-reference in user/role/type attributes and catsets. Main verification (`__cil_verify_helper`) runs in two pass values: pass 0 validates post-evaluation users, roles, types, singleton `handleunknown`/`mls`, booleanifs, named ranges, classes, and policycaps; pass 1 validates contexts and context-bearing statements plus extended permissions. Booleanif validation recursively walks condblocks and rejects neverallow, deny rules, and disallowed statement flavors.

Classpermission verification recursively follows classpermissionsets and map permissions, using a tortoise-style step/limit cycle detection to catch circular class permission definitions. MLS verification ensures sensitivity dominance, low categories are a subset of high categories, and categories are allowed for their sensitivities.

## State and Persistence Behavior

Most verification is read-only, but it writes output counters through `cil_args_verify`: `handleunknown`, `mls`, and `nseuserdflt`. It also uses temporary stacks and lists. Some checks inspect resolved bitmaps (`user->roles`, `role->types`), ordered lists on `db`, resolved class/common permission symtabs, and `datum_expr` lists produced by the resolver.

## Dependencies and Integration Points

The verifier depends on libsepol policy capability lookup, ebitmap access through CIL internals, CIL tree/list/stack utilities, resolver-produced datums and ordered lists, `cil_find`/class expansion for permissionx checks, and logging. It is run after resolution phases and before policy database emission.

## Risks and Edge Cases

Several checks rely on pointer identity for interned keywords and resolved datums. Context validation assumes users have ranges and roles, roles have types, and ranges are resolved. The commented-out duplicate rule verification shows a known gap for type/role rule duplicate checking. Booleanif validation has policy-version-specific allowance for extended avrules. `__cil_verify_levelrange_cats()` has a redundant condition but effectively accepts a null low category set. Classpermission recursion must handle `all`, nested lists, map permissions, empty lists, and cycles.

## Test Signals

Tests should cover invalid names and reserved words by flavor, expression arity/operator errors, constraint operand restrictions, duplicate true/false conditional blocks, macro parameter shadowing, attribute self-reference cycles, incomplete ordered declarations, circular user/role/type bounds, invalid context user-role-type-range combinations, named and anonymous range validation, invalid netif/file/node/device contexts, permissionx classes without ioctl/nlmsg permissions, class/common duplicate permissions, circular classpermissionsets, and booleanif disallowed statements.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_verify.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_verify.h

## Purpose

`cil_verify.h` declares the parser/resolver verification helpers and the argument structure used by verify tree walks.

## Important APIs, Types, and Functions

`enum cil_syntax` defines parse-node shape masks for strings, lists, empty lists, variadic lists/strings, and end-of-list. `struct cil_args_verify` carries `db`, an optional complex symtab, singleton-output pointers for `handleunknown` and `mls`, a `nseuserdflt` count pointer, and the active pass pointer. The header declares name, syntax, expression, constraint, conditional, macro-shadowing, range, ordering, SID, senscat, full verify helper, and pre-verify helper functions.

## Control Flow and Integration

Build/parsing code can use syntax helpers early, while compiler verification walks pass `cil_args_verify` to `cil_tree_walk()` with `__cil_pre_verify_helper()` or `__cil_verify_helper()`. Resolver code also calls `__cil_verify_ordered()` after ordered-list merging.

## State, Dependencies, and Risks

The header includes CIL internal, flavor, tree, and list definitions, binding it to internal compiler structures. The double-underscore function names are still externally declared, so they form a de facto internal API. Callers must initialize all pointer fields in `cil_args_verify` before walking.

## Test Signals

Tests should compile downstream users of the header and run tree-walk verification with both pass values. Syntax mask tests should confirm `CIL_SYN_N_LISTS` and `CIL_SYN_N_STRINGS` only accept homogeneous tails before `CIL_SYN_END`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_verify.h -->
