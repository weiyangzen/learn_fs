# Research Group subset-b-008354

This grouped report covers SELinux `libsepol` CIL source files under `sources/security-integrity/selinux/libsepol/cil/src`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_deny.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_deny.c

## Purpose
`cil_deny.c` implements CIL deny-rule semantics. A CIL deny rule behaves like a neverallow match, but instead of reporting an error it removes matching permissions from existing allow rules. The file rewrites the AST by finding matching `allow` rules, deleting them, and inserting replacement allow rules that preserve the portions not denied.

## Important APIs, Types, And Functions
The public entry point is `cil_process_deny_rules_in_ast(struct cil_db *db)`. Public class-permission helpers exported through `cil_deny.h` are `cil_classperms_list_match_any`, `cil_classperms_list_match_all`, `cil_classperms_list_copy`, `cil_classperms_list_and`, and `cil_classperms_list_andnot`.

Internally, the file has two main layers. The permission layer recursively handles plain class permissions, map class permissions, and classpermission sets. The type-set layer uses `ebitmap_t` and `struct cil_symtab_datum` to compute intersections and differences for concrete types and type attributes. Attribute synthesis helpers such as `cil_create_attribute_d1_and_not_d2`, `cil_create_attribute_d1_and_d2`, and `cil_create_attribute_all_and_not_d` create reusable generated attributes when a result is not empty and not a single concrete type.

## Control Flow
`cil_process_deny_rules_in_ast` walks the AST, skips abstract blocks and macros, collects `CIL_DENY_RULE` nodes, and processes them in encounter order. `cil_process_deny_rule` builds a temporary `CIL_AVRULE_ALLOWED` target from the deny rule, calls `cil_find_matching_avrule_in_ast`, and for each matching allow rule calls `cil_remove_permissions_from_rule` before removing the original allow node.

`cil_remove_permissions_from_rule` first emits an allow for permissions in the original allow but not in the deny (`P1 and not P2`). It then computes common permissions (`P1 and P2`), common sources (`S1 and S2`), and non-denied sources (`S1 and not S2`). The remaining logic branches on `self`, `notself`, and `other` target pseudo-types because target matching depends on the source type. `cil_remove_permissions_from_special_rule` covers the most complicated target cases.

## State And Persistence Behavior
The file mutates the in-memory AST and symbol tables only. It inserts generated `CIL_TYPEATTRIBUTE` and `CIL_TYPEATTRIBUTESET` nodes adjacent to existing nodes, increments `db->num_types_and_attrs`, and inserts generated attributes into the local or root type symbol table. It removes original allow and deny nodes after rewriting. There is no direct disk persistence; later binary or policy serialization consumes the transformed AST.

## Dependencies And Integration Points
It depends on `cil_find.c` for matching allow rules, `cil_list` for list ownership, `cil_tree` helpers through internal headers for AST insertion/removal, `cil_symtab` for generated attributes, `cil_copy_ast` and destroy helpers for classperms ownership, `cil_strpool` for generated names, and libsepol `ebitmap` operations for set algebra. It is invoked from `cil_post_process` after initial database expansion and before final verification.

## Risks And Edge Cases
The highest-risk area is semantic equivalence of the AST rewrite, especially combinations of concrete types, attributes, `self`, `notself`, and `other`. Generated attributes must be inserted in the correct scope and must not collide with existing symbols. The code intentionally reuses existing equivalent attributes when possible; failures there can cause symbol-table growth or incorrect scope. Empty class-permission and empty type-set results are represented by NULL or empty lists, so callers must respect `cil_list_is_empty`.

## Test Signals
Useful tests compile policies with deny rules over concrete types, attributes, map classes, classpermission sets, and all special targets. Tests should compare emitted allow rules or final policydb access vectors with and without denies. Failure signals include unresolved generated attributes, duplicate names, allow rules retaining denied permissions, or denial of too broad a source/target set.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_deny.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_deny.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_deny.h

## Purpose
`cil_deny.h` declares the deny-rule processing interface and the class-permission list set operations used by deny handling and related code.

## Important APIs, Types, And Functions
The header exports match predicates `cil_classperms_list_match_any` and `cil_classperms_list_match_all`, structural copier `cil_classperms_list_copy`, set operations `cil_classperms_list_and` and `cil_classperms_list_andnot`, and the AST pass `cil_process_deny_rules_in_ast`.

## Control Flow
The header has no executable control flow. Consumers include it when they need permission-list intersection/difference semantics or the post-processing deny pass.

## State And Persistence Behavior
No state is owned here. Implementations allocate and destroy `struct cil_list` trees and may mutate the AST; callers must follow ownership conventions documented by the implementation.

## Dependencies And Integration Points
The declarations rely on forward-visible CIL types from internal headers, especially `struct cil_list` and `struct cil_db`. `cil_post.c` calls the deny pass, and `cil_deny.c` supplies the implementation.

## Risks And Edge Cases
Because the header does not include all type declarations itself, include order matters in consumers. The list operations return NULL for empty or invalid combinations in several cases, so callers must tolerate NULL and empty lists.

## Test Signals
Compile-time signals are missing prototypes or include-order regressions. Runtime signals come from deny-rule tests and direct tests of classpermission list copy/intersection/difference over plain classes, map classes, and classpermission sets.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_deny.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_find.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_find.c

## Purpose
`cil_find.c` implements rule-intersection search over the resolved CIL AST. Its main job is finding AV rules that overlap a target AV rule, including SELinux-specific source/target matching involving type attributes and `self`, `notself`, and `other`.

## Important APIs, Types, And Functions
The public functions are `cil_find_matching_avrule_in_ast` and `cil_expand_class`. Important private helpers include `cil_type_match_any`, `cil_type_matches`, `cil_self_match_any`, `cil_notself_match_any`, `cil_other_match_any`, `cil_notself_other_match_any`, classperms match helpers, `cil_permissionx_match_any`, and `cil_find_matching_avrule`.

`struct cil_args_find` carries traversal parameters: requested node flavor, target rule, output list, and whether the target can match itself.

## Control Flow
`cil_find_matching_avrule_in_ast` walks from a caller-supplied AST node. The walker skips abstract blocks and macros, examines only `CIL_AVRULE` or `CIL_AVRULEX` nodes matching the requested flavor, and delegates to `cil_find_matching_avrule`.

Rule matching checks rule kind, extended-rule flag, source type overlap, target type overlap, and permission overlap. Target matching has separate branches for `self`, `notself`, and `other`; some cases are deliberately false because self cannot match notself/other. For ordinary AV rules it recursively compares classperms lists; for extended AV rules it compares permissionx kind, permission bitmap overlap, and expanded object classes.

## State And Persistence Behavior
The module does not mutate persistent state. It allocates temporary lists from `cil_expand_class`, temporary ebitmaps during type matching, appends matching AST nodes to the caller-owned output list, and destroys its own temporaries.

## Dependencies And Integration Points
It depends on libsepol `ebitmap`, `cil_list`, `cil_tree_walk`, `cil_symtab_map`, and CIL internal structs. `cil_deny.c` uses it to find allow rules affected by deny rules. `cil_binary.c` uses it for neverallow-style matching checks during binary policy generation.

## Risks And Edge Cases
Matching semantics are subtle for attributes with multiple concrete types and for pseudo-targets. An error can either miss a real overlap or report a false conflict. Map classes require expansion through map permissions, and extended permissions require both object-class and bitmap overlap. Empty attributes and degenerate `notself`/`other` cases need careful coverage.

## Test Signals
Tests should cover concrete type versus concrete type, attribute versus concrete type, attribute versus attribute, special target combinations, map classes, classpermission sets, and permissionx ranges. Integration signals are deny-rule rewrites and neverallow diagnostics matching expected source locations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_find.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_find.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_find.h

## Purpose
`cil_find.h` exposes the AST AV-rule search helper and class expansion helper used by deny handling, neverallow verification, and policy serialization.

## Important APIs, Types, And Functions
`cil_find_matching_avrule_in_ast` searches an AST subtree for AV or extended AV rules that overlap a target rule. `cil_expand_class` converts a normal class or map class into a list of concrete classes.

## Control Flow
The header has no runtime flow. The implementation performs tree walking and recursive class-permission expansion.

## State And Persistence Behavior
No state is stored in the header. Callers of `cil_expand_class` receive a newly allocated `struct cil_list` and must destroy it without destroying class data.

## Dependencies And Integration Points
It includes `cil_flavor.h`, `cil_tree.h`, and `cil_list.h`, tying the API to AST node flavors and CIL list ownership. `cil_deny.c`, `cil_policy.c`, and `cil_binary.c` are the main consumers.

## Risks And Edge Cases
The API returns matching nodes by appending to a caller-owned list, so callers must initialize and clean that list. The `match_self` flag changes whether the target can match itself, which is important for neverallow checks versus deny rewrites.

## Test Signals
Compile tests catch signature drift. Behavioral tests should verify that callers destroy expanded class lists and that self-matching behavior differs as expected between rule-search contexts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_find.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_flavor.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_flavor.h

## Purpose
`cil_flavor.h` defines the central `enum cil_flavor` used as the runtime tag for parse tree nodes, AST nodes, list items, operators, and declarative CIL objects.

## Important APIs, Types, And Functions
The file defines two offset constants, `CIL_MIN_OP_OPERANDS` and `CIL_MIN_DECLARATIVE`, and a single enum. Early values represent structural nodes and post-parse statement nodes. Operator values include `CIL_ALL`, `CIL_AND`, `CIL_OR`, `CIL_XOR`, `CIL_NOT`, `CIL_EQ`, `CIL_NEQ`, `CIL_RANGE`, constraint relation operators, and constraint operands. Declarative values include blocks, macros, booleans, classes, permissions, users, roles, types, MLS objects, contexts, IP addresses, policy capabilities, and permissionx.

## Control Flow
There is no executable control flow. The numeric layout lets code distinguish structural, operator, and declarative categories by ranges.

## State And Persistence Behavior
The enum values become in-memory tags for almost every CIL object and list item. They are not directly persisted, but they influence AST destruction, symbol-table routing, verification, and policy generation.

## Dependencies And Integration Points
Nearly every CIL source file includes this header directly or through `cil_internal.h`. `FLAVOR()`-style datum inspection, switch statements, list traversal, symbol-table mapping, parser/build phases, and post-processing all depend on these stable tags.

## Risks And Edge Cases
Changing enum values can break assumptions in switch statements and range checks. Adding a new CIL construct requires updates across parser/build, verification, destruction, policy generation, binary generation, and research helpers. Operator tags are stored through `void *` casts in lists, so pointer-width-safe casts must be used by implementation code.

## Test Signals
Build failures reveal missing switch cases only where compilers warn. Better signals are parsing and compiling policies that exercise every flavor class, plus sanitizer runs through AST destruction and policy generation after adding or changing a flavor.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_flavor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_fqn.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_fqn.c

## Purpose
`cil_fqn.c` manages fully qualified names for CIL symbol-table data. It constructs FQNs from lexical scopes, compares datum names in sorted order, and recursively assigns FQNs through AST scopes.

## Important APIs, Types, And Functions
The public functions are `cil_fqn_qualify_blocks`, `cil_fqn_qualify`, `cil_fqn_qualify_all`, and `cil_fqn_compare`. `cil_fqn_qualify_blocks` joins a datum name with a list of containing block names using dots. `cil_fqn_qualify` builds the containing block list by walking datum node parents. `cil_fqn_qualify_all` walks an AST and qualifies every symbol datum in block, macro, or conditional scopes.

## Control Flow
Qualification starts at a datum node and climbs through parent AST nodes, collecting non-root block names. It then builds a dot-separated string and interns it through the string pool. The AST-wide pass skips no scopes; it checks node flavors that own symbol tables and maps every symtab datum through the qualifier callback.

## State And Persistence Behavior
The module mutates `struct cil_symtab_datum::fqn` pointers. FQNs are interned in the CIL string pool, so lifetime is tied to the process/database string pool rather than the caller. It does not write files.

## Dependencies And Integration Points
It uses `cil_list` for temporary block-name stacks, `cil_symtab_map` to visit scoped symbols, `cil_strpool_add` for stable string storage, and `cil_tree` parent links. Build and verify phases rely on FQNs for logging, sorting, matching, and output.

## Risks And Edge Cases
The code assumes every datum has at least one AST node and meaningful parent links. Scope qualification must avoid root names while preserving block nesting. Name length allocation is computed before formatting; off-by-one or missing separators would corrupt generated FQNs.

## Test Signals
Tests should build nested block/macro policies and assert qualified names, especially same local names in different blocks. Sorting tests for `cil_fqn_compare` and diagnostic tests that include FQNs are useful integration signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_fqn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_fqn.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_fqn.h

## Purpose
`cil_fqn.h` declares helpers for assigning and comparing fully qualified CIL symbol names.

## Important APIs, Types, And Functions
It declares `cil_fqn_qualify_blocks`, `cil_fqn_qualify`, `cil_fqn_qualify_all`, and `cil_fqn_compare`.

## Control Flow
The header has no executable flow. Implementations either qualify one datum using explicit block lists or node ancestry, or qualify all data in an AST.

## State And Persistence Behavior
No state is owned by the header. Implementations update `fqn` fields on existing datums and allocate interned strings.

## Dependencies And Integration Points
It includes `cil_internal.h` for `struct cil_db` and `struct cil_symtab_datum`. It is used by AST build and verification/output code needing stable display and comparison names.

## Risks And Edge Cases
Consumers must call qualification after enough AST parent/symtab information exists and before FQN-dependent sorting or output. Missing qualification can make later pointer comparisons against keyword strings or emitted names incorrect.

## Test Signals
Tests should check qualified names in nested scopes and stable compare ordering after qualification.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_fqn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_internal.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_internal.h

## Purpose
`cil_internal.h` is the primary internal ABI for the CIL frontend in libsepol. It defines database state, keyword globals, symbol-table indices, AST payload structs for CIL declarations and rules, constants, and initializer/destructor/function prototypes shared across implementation files.

## Important APIs, Types, And Functions
Important global structures include `struct cil_db`, `struct cil_root`, `struct cil_sort`, `struct cil_ordered`, and payload structs such as `cil_block`, `cil_class`, `cil_perm`, `cil_type`, `cil_typeattribute`, `cil_role`, `cil_user`, `cil_avrule`, `cil_deny_rule`, `cil_type_rule`, `cil_context`, file/network context structs, constraints, macros, calls, defaults, and source-info records.

The header also declares the pass enum, symbol-table index enums, keyword pointers such as `CIL_KEY_SELF`, `CIL_KEY_NOTSELF`, `CIL_KEY_ALLOW`, `CIL_KEY_DENY_RULE`, constants for AV rule kinds and attribute-use flags, and many `*_init` constructors.

## Control Flow
There is no executable flow, but the structures encode the pipeline. Parse and build phases populate raw and AST trees; post-processing fills counters, value arrays, bitmaps, sort arrays, and default policy options; binary and textual emitters consume the resolved database.

## State And Persistence Behavior
`struct cil_db` owns the main mutable compiler state: parse tree, AST, built-in pseudo-types, ordering lists, sorted context arrays, declared strings, value-to-object maps, counters, policy options, and target settings. Many payload structs store both original strings and resolved pointers. Persistence is indirect: this state is later serialized to policydb or textual policy.

## Dependencies And Integration Points
The header imports sepol policydb/service types, public `cil/cil.h`, CIL flavor/tree/symtab/memory headers, and system networking types. It is included almost everywhere in the CIL implementation, making changes high impact.

## Risks And Edge Cases
Because this header is broad, field changes can break ownership, destruction, post-processing, and emitters. Several fields are overloaded as either concrete objects, aliases, or attributes; consumers must inspect node flavor before casting. Numeric values in `enum cil_default_object`, `enum cil_default_object_range`, and fsuse types are intentionally kept equal to policydb constants.

## Test Signals
Full pipeline tests are the useful signal: parse CIL, build AST, run post-processing, emit binary/text policy, and destroy the database under sanitizers. Tests should include aliases, attributes, MLS, default rules, contexts, macros, conditionals, and target-platform-specific context rules.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_lexer.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_lexer.h

## Purpose
`cil_lexer.h` defines the token interface between the Flex lexer and the hand-written CIL parser.

## Important APIs, Types, And Functions
It defines token constants `OPAREN`, `CPAREN`, `SYMBOL`, `QSTRING`, `COMMENT`, `HLL_LINEMARK`, `NEWLINE`, `END_OF_FILE`, and `UNKNOWN`. `struct token` carries token type, token value pointer, and line number. Public functions are `cil_lexer_setup`, `cil_lexer_destroy`, and `cil_lexer_next`.

## Control Flow
The header has no runtime flow. The parser sets up a buffer, repeatedly requests the next token, and destroys scanner state at exit.

## State And Persistence Behavior
Lexer state is maintained in the generated scanner. Token values point into the scanned buffer/global lexer state, so callers must intern or copy values that need longer lifetime.

## Dependencies And Integration Points
`cil_parser.c` is the direct consumer. Unit tests under the CIL test tree exercise setup and token iteration.

## Risks And Edge Cases
The scanner expects a Flex-compatible scan buffer with required trailing NUL bytes. Callers passing the wrong size can cause scanner setup failure or truncated input.

## Test Signals
Lexer tests should cover parentheses, symbols, quoted strings, comments, line markers, newlines, EOF, and unknown characters, including line-number behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_lexer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_lexer.l -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_lexer.l

## Purpose
`cil_lexer.l` is the Flex scanner for CIL syntax. It tokenizes the CIL input stream into parentheses, symbols, quoted strings, comments, high-level-language line markers, newlines, EOF, and unknown characters.

## Important APIs, Types, And Functions
The generated scanner is wrapped by `cil_lexer_setup`, `cil_lexer_destroy`, and `cil_lexer_next`. Patterns define digits, letters, special symbol characters, whitespace, newlines, quoted strings, `;;*` high-level line markers, and `;` comments. The scanner uses Flex options `nounput`, `noinput`, `noyywrap`, and prefix `cil_yy`.

## Control Flow
`cil_lexer_setup` scans a caller-provided buffer and resets line number to 1. Each scanner action returns one token type or skips whitespace. Newlines increment the global line counter. `cil_lexer_next` calls `yylex`, copies the current token type/value/line into the caller's token, and returns `SEPOL_OK`.

## State And Persistence Behavior
The file uses scanner-global `value` and `line`. It does not allocate token strings; `yytext` points into scanner-managed buffer content. Parser code modifies quoted string buffers in place to strip quotes before interning.

## Dependencies And Integration Points
It includes `cil_internal.h`, `cil_lexer.h`, `cil_log.h`, and `cil_mem.h`, and reports setup errors through `cil_log`. `cil_parser.c` supplies the buffer from the public CIL loader.

## Risks And Edge Cases
The grammar intentionally recognizes comments as a single `;` token and leaves parser code to consume until newline. Quoted strings cannot contain quotes, newlines, or NUL. `value` is not reset for whitespace/newline/EOF paths, but token type controls use. The high-level line marker pattern is anchored and must remain consistent with parser expectations.

## Test Signals
Unit tests should verify token order, line counters, comment consumption by the parser, quoted string stripping, unknown-token diagnostics, and setup failure behavior for malformed scan buffers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_lexer.l -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_list.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_list.c

## Purpose
`cil_list.c` implements a simple singly linked list used throughout CIL for expressions, datum lists, classperms, AST helper collections, and temporary traversal results.

## Important APIs, Types, And Functions
The file implements initialization/destruction (`cil_list_init`, `cil_list_destroy`, `cil_list_item_init`, `cil_list_item_destroy`), mutation (`cil_list_append`, `cil_list_prepend`, `cil_list_insert`, `cil_list_append_item`, `cil_list_prepend_item`, `cil_list_remove`), and predicates (`cil_list_contains`, `cil_list_match_any`). `cil_list_error` logs an error and terminates on impossible misuse.

## Control Flow
Append/prepend allocate a new item and update head/tail. Insert can prepend, append, or link after a supplied current item. Append/prepend item variants accept an existing chain and find its last node before splicing. Destroy recursively destroys nested lists when item flavor is `CIL_LIST`; otherwise it optionally destroys item data through `cil_destroy_data`.

## State And Persistence Behavior
List state is heap memory only. Items carry a `flavor` tag and raw `data` pointer; ownership is controlled by the caller and the `destroy_data` flag. No persistence exists outside objects that reference these lists.

## Dependencies And Integration Points
The implementation depends on `cil_mem` for allocation, `cil_log` for fatal list misuse, `cil_flavor` for tags, and `cil_destroy_data` for optional payload destruction. Almost every CIL subsystem uses these lists.

## Risks And Edge Cases
The API is not defensive for NULL lists in mutators; misuse exits the process. `cil_list_match_any` compares pointer identity and flavor, not semantic equality. Splicing existing chains assumes the chain is well-formed and acyclic. Destroying with the wrong `destroy_data` value can leak memory or double-free shared AST data.

## Test Signals
Tests should cover empty-list append/prepend, tail updates after remove, insertion at front/middle/end, nested-list destruction, pointer-identity matching, and sanitizer runs over AST build/destroy paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_list.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_list.h

## Purpose
`cil_list.h` declares the generic CIL linked-list structure, iteration macros, and list helper APIs.

## Important APIs, Types, And Functions
It defines `struct cil_list` with `head`, `tail`, and list flavor, and `struct cil_list_item` with `next`, item flavor, and data pointer. Macros are `cil_list_is_empty` and `cil_list_for_each`. Functions mirror the implementation in `cil_list.c`.

## Control Flow
The header contributes macro-based iteration. `cil_list_for_each` assumes a non-NULL list pointer; callers must guard NULL lists themselves unless the local contract guarantees presence.

## State And Persistence Behavior
No state is stored here. The structs define heap-owned in-memory list topology used across AST and expression data.

## Dependencies And Integration Points
It includes `cil_flavor.h` and is consumed by parser, AST build, post-processing, deny processing, find logic, and policy emitters.

## Risks And Edge Cases
The iteration macro is unsafe with NULL lists and with mutation of the current item unless the caller stores `next` separately. The list flavor is advisory; many operations do not enforce it.

## Test Signals
Compile and sanitizer tests should exercise list operations through high-level policy parsing plus focused unit tests for insertion/removal and nested destruction.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_log.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_log.c

## Purpose
`cil_log.c` implements the CIL logging shim. It provides a configurable callback and log level used by parser, verification, allocation wrappers, and other CIL subsystems.

## Important APIs, Types, And Functions
Public functions are `cil_set_log_handler`, `cil_vlog`, `cil_log`, `cil_set_log_level`, and `cil_get_log_level`. The default handler writes messages to `stderr`. Messages are formatted into a fixed `MAX_LOG_SIZE` buffer.

## Control Flow
`cil_log` wraps varargs and delegates to `cil_vlog`. `cil_vlog` emits a message only when the current global log level is greater than or equal to the message level. If `vsnprintf` reports truncation, it emits a truncation marker.

## State And Persistence Behavior
The file owns two process-global variables: current log level and current handler function pointer. It persists no data except through the caller-provided handler side effects.

## Dependencies And Integration Points
It includes public `cil/cil.h` for log level enum definitions. All CIL error reporting routes through this module either directly or indirectly.

## Risks And Edge Cases
Global handler and level are not synchronized, so concurrent users could race. The callback receives `cil_log_level` rather than the original message level, which is a behavioral detail consumers may rely on or trip over. Long messages are truncated to 512 bytes plus marker.

## Test Signals
Tests should set custom handlers, vary log levels, check suppression/emission, and verify truncation behavior. Integration tests should assert diagnostics for parse and verification failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_log.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_log.h

## Purpose
`cil_log.h` declares CIL internal logging helpers.

## Important APIs, Types, And Functions
It defines `MAX_LOG_SIZE` as 512 and declares formatted functions `cil_vlog` and `cil_log`, plus `cil_get_log_level`. The log handler and setter for log level are declared through the public CIL API rather than here.

## Control Flow
No executable control flow exists. GCC format attributes provide compile-time checking for printf-style calls.

## State And Persistence Behavior
No state is owned in the header. The implementation maintains process-global handler and log level.

## Dependencies And Integration Points
It includes `<cil/cil.h>` for `enum cil_log_level`. All CIL sources that need diagnostics include this header.

## Risks And Edge Cases
Changing `MAX_LOG_SIZE` affects truncation and stack buffer size in `cil_vlog`. Missing format attributes would reduce compiler coverage of logging calls.

## Test Signals
Build warnings for format misuse and logging unit tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_mem.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_mem.c

## Purpose
`cil_mem.c` provides fail-fast allocation wrappers used throughout CIL.

## Important APIs, Types, And Functions
The module implements `cil_malloc`, `cil_calloc`, `cil_realloc`, `cil_strdup`, and `cil_asprintf`.

## Control Flow
Each wrapper calls the corresponding libc allocator or formatter. Allocation failure logs `Failed to allocate memory` and terminates with `exit(1)`. `cil_malloc(0)` and `cil_realloc(ptr, 0)` return NULL if libc does. `cil_strdup(NULL)` returns NULL.

## State And Persistence Behavior
The file owns no persistent state. It returns heap allocations to callers, and callers retain normal free/destroy responsibility.

## Dependencies And Integration Points
It depends on `cil_log` for error reporting. Nearly every CIL subsystem uses these wrappers, so allocation failures are treated as fatal process errors rather than recoverable `SEPOL_ERR` returns.

## Risks And Edge Cases
Fail-fast behavior is simple but makes low-memory testing and library embedding more difficult. `cil_asprintf` relies on `vasprintf`, which may require feature macros in some environments. Zero-size allocation behavior follows libc and can return NULL without logging.

## Test Signals
Normal tests mainly check successful allocation behavior indirectly. Fault-injection builds or allocator shims can confirm fatal OOM paths and NULL handling for zero-size and NULL strdup inputs.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_mem.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_mem.h

## Purpose
`cil_mem.h` declares CIL allocation wrappers that centralize allocation failure handling.

## Important APIs, Types, And Functions
Declared functions are `cil_malloc`, `cil_calloc`, `cil_realloc`, `cil_strdup`, and printf-style `cil_asprintf`.

## Control Flow
The header itself has no executable flow. The implementation exits on allocation failure rather than returning errors.

## State And Persistence Behavior
No state is stored here. Callers receive heap memory that must be freed or transferred to CIL object destructors.

## Dependencies And Integration Points
The header is included by list, parser, lexer, logging users, post-processing, and most AST object constructors.

## Risks And Edge Cases
Consumers should not expect recoverable OOM from these APIs. The header relies on standard size and varargs declarations being available through includes in translation units.

## Test Signals
Compiler coverage of the `cil_asprintf` format attribute and allocator fault-injection tests are useful signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_parser.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_parser.c

## Purpose
`cil_parser.c` is a hand-written parser that converts lexer tokens into a raw parenthesized CIL parse tree. It also records source-path and high-level-language line-marker information as synthetic source-info nodes.

## Important APIs, Types, And Functions
The public function is `cil_parser(const char *path, char *buffer, uint32_t size, struct cil_tree **parse_tree)`. Important helpers include `push_hll_info`, `pop_hll_info`, `create_node`, `insert_node`, `add_hll_linemark`, and `add_cil_path`. `CIL_PARSER_MAX_EXPR_DEPTH` limits parenthesis and line-marker nesting.

## Control Flow
The parser initializes the lexer on a caller-provided buffer, adds a source-info node for the CIL path, then loops over tokens. `OPAREN` creates a child parse node and descends. `CPAREN` ascends and checks balance. `SYMBOL` and `QSTRING` create leaf nodes under the current expression, with strings interned through the string pool. Comments are consumed until newline or EOF. HLL line markers create nested source-info expressions and maintain a stack of previous offsets/expansion mode.

## State And Persistence Behavior
The function mutates the caller-provided parse tree by appending nodes. Node data strings are interned through `cil_strpool_add`; quoted strings are stripped in place before interning. HLL state is local stack data, and scanner state is destroyed on both success and error.

## Dependencies And Integration Points
It depends on the lexer, CIL tree, stack, string pool, memory wrappers, and logging. Public loading code in `cil.c` calls it before AST building. Later diagnostics use line and `hll_offset` fields filled here.

## Risks And Edge Cases
The parser performs structural validation only; semantic validation is later. It rejects symbols outside parentheses, unmatched parentheses, unknown tokens, invalid HLL markers, and nesting over 4096. Error exits leave any already appended parse nodes in the tree for the caller/database cleanup path. Quoted string mutation requires mutable input buffers.

## Test Signals
Unit tests should cover valid parse-tree shape, comments, quoted strings, top-level symbol rejection, unmatched parentheses, depth limits, HLL start/end/expand behavior, EOF after comments, and source path source-info insertion.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_parser.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_parser.h

## Purpose
`cil_parser.h` declares the CIL parse-tree builder.

## Important APIs, Types, And Functions
It declares `cil_parser`, which takes a source path, mutable input buffer, byte size, and parse tree pointer.

## Control Flow
The header has no runtime flow. The implementation drives lexer tokenization and tree construction.

## State And Persistence Behavior
No state is stored in the header. The function mutates the supplied parse tree and uses interned strings for node data.

## Dependencies And Integration Points
It includes `cil_tree.h`, making the parser API part of the tree-building layer. `cil.c` calls this during file/module loading.

## Risks And Edge Cases
Callers must pass the size expected by the Flex scan buffer setup, including trailing NUL space prepared by the loader. The buffer must be mutable because quoted strings are edited in place.

## Test Signals
Parser unit tests and loader integration tests are the primary signals, especially malformed syntax and source-location reporting.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_policy.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_policy.c

## Purpose
`cil_policy.c` serializes a resolved CIL database to textual SELinux kernel policy language. It is an output/debug path that walks the post-processed AST/database and writes policy statements in kernel-policy order.

## Important APIs, Types, And Functions
The public entry point is `cil_gen_policy(FILE *out, struct cil_db *db)`. Key helpers gather statements (`cil_gather_statements`), format MLS levels and contexts, format conditional and constraint expressions, expand classpermissions and mapped classes, emit TE rules, emit roles/users, and emit context-labeling rules.

Major emitters include `cil_class_decls_to_policy`, `cil_commons_to_policy`, `cil_classes_to_policy`, `cil_defaults_to_policy`, `cil_default_ranges_to_policy`, `cil_sensitivities_to_policy`, `cil_categories_to_policy`, `cil_mlsconstrains_to_policy`, `cil_av_rule_to_policy`, `cil_av_rulex_to_policy`, `cil_type_rule_to_policy`, `cil_te_rules_to_policy`, `cil_roles_to_policy`, `cil_users_to_policy`, and the various `*_cons_to_policy` functions.

## Control Flow
`cil_gen_policy` initializes statement lists, gathers selected declarations while skipping abstract blocks, macros, and booleanif bodies, then emits in a fixed order: classes and SIDs, class details, defaults, MLS pieces if enabled, policy capabilities, attributes, booleans, types and TE rules, roles, users, constraints, validatetrans, SID contexts, and sorted context rules. TE rules are emitted by repeated AST walks in rule-kind order. Conditional blocks emit `if (...) { ... } else { ... }` with their nested TE rules.

## State And Persistence Behavior
The module writes to a caller-provided `FILE *`. It allocates temporary strings/lists for classperms and constraint expressions and frees them after use. It does not mutate the database except through transient allocations; however it assumes post-processing has already resolved expressions, sorted context arrays, and filled role/user/type bitmaps.

## Dependencies And Integration Points
It depends on `cil_find.c` for class expansion, `cil_list`, `cil_tree_walk`, CIL internal structs, string names from keyword globals, and system `inet_ntop` support for nodecon output. `cil.c` calls `cil_gen_policy` in the path that writes textual policy output.

## Risks And Edge Cases
The serializer assumes a valid, post-processed database. Empty classperms are skipped because kernel policy cannot represent empty permission sets. Mapped classes and permission sets are recursively expanded, so missing expression evaluation can produce wrong output. Constraint-expression string sizing is manual and vulnerable to omissions when new operand kinds are added. Text output must remain consistent with kernel policy syntax, including MLS-only statements.

## Test Signals
Golden-output tests for representative CIL policies are the strongest signal: TE rules, conditionals, map classes, permissionx ranges, MLS levels/ranges, defaults, constraints, users/roles, and every context rule type. Fuzz or sanitizer tests should stress long names, large category ranges, and empty permission expressions.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_policy.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_policy.h

## Purpose
`cil_policy.h` declares the textual policy serializer for a resolved CIL database.

## Important APIs, Types, And Functions
It declares `cil_gen_policy(FILE *out, struct cil_db *db)`.

## Control Flow
The header has no executable flow. The implementation traverses the database/AST and writes kernel policy statements to `FILE *`.

## State And Persistence Behavior
No state is owned here. The serializer writes to caller-owned output and reads the post-processed database.

## Dependencies And Integration Points
It includes `cil_internal.h` for `struct cil_db`. Public CIL code calls it when textual policy output is requested.

## Risks And Edge Cases
Callers must invoke it only after successful post-processing; unresolved expressions or unsorted context arrays can produce incorrect output.

## Test Signals
Compile coverage and golden textual-policy output tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_post.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_post.c

## Purpose
`cil_post.c` performs post-AST processing for CIL. It verifies early invariants, computes database counts and lookup arrays, evaluates attribute and expression bitmaps, builds role/user associations, evaluates classpermission and category expressions, sorts and deduplicates context rules, processes deny rules, and runs final verification.

## Important APIs, Types, And Functions
The public entry point is `cil_post_process(struct cil_db *db)`. Public sort comparators include `cil_post_filecon_compare`, `cil_post_ibpkeycon_compare`, `cil_post_portcon_compare`, `cil_post_genfscon_compare`, `cil_post_netifcon_compare`, `cil_post_ibendportcon_compare`, `cil_post_nodecon_compare`, and `cil_post_fsuse_compare`.

Key internal helpers include expression evaluation functions (`__cil_expr_to_bitmap`, `__cil_expr_list_to_bitmap`, `__evaluate_type_expression`, `__evaluate_role_expression`, `__evaluate_user_expression`, `__evaluate_permissionx_expression`, `__evaluate_cat_expression`), database walkers (`__cil_post_db_count_helper`, `__cil_post_db_array_helper`, `__cil_post_db_attr_helper`, `__cil_post_db_roletype_helper`, `__cil_post_db_userrole_helper`, `__cil_post_db_classperms_helper`, `__cil_post_db_cat_helper`), and conflict handler `__cil_post_process_context_rules`.

## Control Flow
`cil_post_process` runs `cil_pre_verify`, then `cil_post_db`, then `cil_process_deny_rules_in_ast`, then `cil_post_verify`. `cil_post_db` walks the AST multiple times. First it counts unique classes/types/attributes/roles/users and context rules. Then it fills value-to-type/role/user arrays and sort arrays. It marks neverallow-related generated attributes, evaluates attribute bitmaps and permissionx expressions, builds role-to-type and user-to-role bitmaps, evaluates classpermission and map-class expressions, evaluates MLS category expressions, and finally sorts/deduplicates each context-rule array while detecting conflicting duplicate rules.

## State And Persistence Behavior
This pass mutates `struct cil_db` and many AST payloads. It assigns numeric values to types, roles, users, categories elsewhere consumed by bitmaps; allocates `val_to_type`, `val_to_role`, `val_to_user`; allocates sorted context arrays; fills `types`, `roles`, `users`, `perms`, and category expression lists; and sets attribute `keep` flags. It performs no direct disk writes. Later binary/text emitters consume this persistent in-memory state.

## Dependencies And Integration Points
It depends on libsepol `ebitmap`, CIL verification helpers, deny processing, policy/context comparators, tree walkers, list helpers, symbol tables, and logging. It is called from `cil.c` after AST construction and before binary policy generation or textual policy output.

## Risks And Edge Cases
This is a high-blast-radius pass. Expression evaluation must correctly implement `all`, `range`, `not`, `and`, `or`, and `xor` for types, roles, users, permissions, categories, and permissionx values. Context duplicate handling depends on stable sort comparators and `db->multiple_decls`; wrong comparisons can either reject valid duplicates or silently keep conflicting labels. Attribute expansion policy is subtle: generated require/typeattr names and neverallow-only attributes are treated specially. The pass also assumes abstract blocks and macros should be skipped by most walkers.

## Test Signals
Strong tests compile full CIL policies covering type/user/role attributes, aliases, class maps, permission expressions, category ranges, MLS contexts, duplicate context rules with same and conflicting contexts, role/user associations through attributes, permissionx ranges, deny rules, and final neverallow verification. Sanitizers should watch for leaks or double frees after expression-list replacement and context-array compaction.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_post.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_post.h -->
# sources/security-integrity/selinux/libsepol/cil/src/cil_post.h

## Purpose
`cil_post.h` declares post-processing and context-rule comparator APIs used after CIL AST construction.

## Important APIs, Types, And Functions
It declares comparators for filecon, ibpkeycon, portcon, genfscon, netifcon, ibendportcon, nodecon, and fsuse records, plus `cil_post_process`.

## Control Flow
The header has no executable flow. The implementation sorts/deduplicates context arrays and orchestrates the complete post-processing pipeline.

## State And Persistence Behavior
No state is stored here. `cil_post_process` mutates the supplied `struct cil_db` by resolving expressions, filling arrays, processing deny rules, and setting policy defaults.

## Dependencies And Integration Points
It includes `cil_internal.h` and is consumed by `cil.c`, policy generation, tests, and any code that needs the canonical sort order for context records.

## Risks And Edge Cases
Comparator behavior must stay synchronized with kernel/libsepol expectations for context ordering. Calling `cil_post_process` more than once on the same database can be risky because many fields are allocated or transformed in place.

## Test Signals
Comparator unit tests should assert ordering for regex filecons, wildcard netifcons, ranges, IPv4/IPv6 nodecons, and duplicate handling. Full post-process integration tests should assert successful compilation and expected diagnostics for conflicts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil_post.h -->
