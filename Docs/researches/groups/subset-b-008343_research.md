# subset-b-008343 research

This grouped report covers SELinux `checkpolicy` parser, module compiler, queue, and binary-module inspection files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/module_compiler.c -->
# sources/security-integrity/selinux/checkpolicy/module_compiler.c

## Purpose

`module_compiler.c` implements the module-aware scoping layer used by the `checkpolicy` yacc actions. It sits between grammar reductions in `policy_parse.y`/`policy_define.c` and libsepol's `policydb_t` data model. Its main job is to keep the current `avrule_block_t`/`avrule_decl_t` stack coherent, enforce where declarations and `require` statements are legal, create or require symbols in the correct scope, and append parsed rules to the active declaration.

The file is essential for binary policy modules and optional blocks. It distinguishes global/base parsing from module parsing, tracks optional and else branches, records required and declared scope bitmaps, and resolves inherited requirements in pass 2.

## Important APIs, Types, and Functions

The private `scope_stack_t` records stack frame type, active declaration, last appended AV rule, else-branch state, whether a require was seen, and parent frame. Stack type `1` is an avrule block; type `2` is reserved for conditionals but is only lightly used. Global parser state includes `stack_top`, `last_block`, and `next_decl_id`.

`define_policy(pass, module_header_given)` initializes the parse state after the grammar recognizes either a base policy or a module header. It validates `policydbp->policy_type`, consumes the module name/version from `id_queue` on pass 1, drains them on pass 2, resets the stack, pushes the global declaration, and resets declaration numbering.

`declare_symbol()` and `require_symbol()` are wrappers around `create_symbol()`. They call `symtab_insert()` with `SCOPE_DECL` or `SCOPE_REQ`, then set the matching bit in `decl->declared.scope` or `decl->required.scope`; `require_symbol()` also marks `stack_top->require_given`.

`declare_role()`, `declare_type()`, and `declare_user()` allocate libsepol datum objects, insert them via `declare_symbol()`, and maintain local per-declaration symbol tables (`p_roles`, `p_types`, `p_users`). `get_local_type()` and `get_local_role()` materialize local copies for symbols referenced in module declarations.

The `require_*()` family handles require-block grammar entries. `require_class()` is special because it also creates class permission symbols when allowed by module policy and records required class permission bitmaps via `add_perm_to_class()`.

`is_id_in_scope()` and `is_perm_in_scope()` provide semantic validation used by `policy_define.c`. They treat unknown identifiers as in-scope so callers can emit the more specific "unknown" error later.

`append_*()` functions attach parsed AV rules, conditionals, role transitions/allows, filename transitions, and range transitions to the active declaration. Optional block control is managed by `begin_optional()`, `begin_optional_else()`, `end_optional()`, and `end_avrule_block()`.

## Control Flow

Parsing starts with `define_policy()`, which sets up the global stack frame. Grammar actions then call declaration or require helpers while reductions consume names from `id_queue`. `is_creation_allowed()` prevents declarations and requirements inside conditionals and else branches. For optional blocks, pass 1 allocates new `avrule_block_t` and `avrule_decl_t` objects; pass 2 walks the previously built block chain and asserts declaration ids match `next_decl_id`.

At the end of a non-global avrule block, pass 1 enforces that non-else module/optional branches have a require section, except for base-policy nested cases. In pass 2, `end_avrule_block()` calls `copy_requirements()` so a child declaration inherits all parent required symbol and class-permission bitmaps.

## State and Persistence Behavior

All persistent state is in the global `policydbp` object and libsepol data structures attached to it. The file also has parse-session globals (`stack_top`, `last_block`, `next_decl_id`) that are reset by `define_policy()` and, for fuzz builds, `module_compiler_reset()`. It owns and frees queue strings in pass-specific paths and allocates policydb child structures whose lifetime is owned by policydb destroy routines.

## Dependencies and Integration Points

This file depends on libsepol policydb, avrule block, conditional, ebitmap, hashtab, and symtab APIs. It integrates with `policy_define.c` via exported declare/require/scope/append functions and with `policy_parse.y` through optional and require grammar actions. It consumes `id_queue` from `queue.c` and reports through scanner/parser `yyerror()` and `yyerror2()`.

## Risks and Edge Cases

The implementation is highly stateful. Queue consumption must match grammar order exactly, declaration ids must stay synchronized across both passes, and assertions in pass 2 assume pass 1 successfully built the same block topology. Memory ownership is subtle: several paths return `1` from symbol creation to signal that the caller must destroy an unused datum. Else branches intentionally disallow declarations and require blocks, and a missed `require_given` update will reject otherwise valid modules. The expression `dest_typdatum->flavor != isattr ? TYPE_ATTRIB : TYPE_TYPE` in local type/role checks is precedence-sensitive and should be reviewed carefully if touched.

## Test Signals

Useful tests include parsing base policies with no module header, modules with name/version headers, optional blocks with and without requires, optional else branches inheriting requirements, duplicate declarations, type/attribute and role/attribute flavor conflicts, class require permissions, and pass-2 reparse consistency. Fuzz builds can use `module_compiler_reset()` to verify clean reuse across parser invocations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/module_compiler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/module_compiler.h -->
# sources/security-integrity/selinux/checkpolicy/module_compiler.h

## Purpose

`module_compiler.h` exposes the module compiler/scoping API used by the parser and semantic action layer. It is the contract for initializing policy/module scope, declaring and requiring symbols, checking whether references are allowed in the current module scope, appending parsed rule objects, and managing optional block lifetime.

## Important APIs and Types

The header includes `sepol/policydb/hashtab.h` because several APIs use `hashtab_key_t` and `hashtab_datum_t`. It relies on libsepol policydb types that are visible through the translation units including it, such as `role_datum_t`, `type_datum_t`, `user_datum_t`, `avrule_t`, `cond_list_t`, and transition rule structs.

`define_policy(int pass, int module_header_given)` begins parser handling for base or module input. `declare_symbol()` and `require_symbol()` are lower-level generic symbol insertion APIs. Typed wrappers (`declare_role()`, `declare_type()`, `declare_user()`, `require_class()`, `require_role()`, `require_type()`, `require_bool()`, and others) hide the datum setup and pass-sensitive behavior.

`is_id_in_scope()` and `is_perm_in_scope()` are semantic checks used before resolving names into policydb indexes. `get_current_cond_list()` deduplicates conditionals by expression within the active declaration. `append_cond_list()`, `append_avrule()`, `append_role_trans()`, `append_role_allow()`, `append_range_trans()`, and `append_filename_trans()` form the output side of parser reductions.

Optional blocks are controlled by `begin_optional()`, `begin_optional_else()`, `end_optional()`, and `end_avrule_block()`.

## Control Flow and Integration

`policy_parse.y` calls these APIs directly from grammar actions, while `policy_define.c` calls declaration, scope-check, local-symbol, and append functions while constructing policydb objects. The interface is pass-aware: many exported helpers receive `pass`, and callers are responsible for draining `id_queue` consistently even when pass 1 only declares skeletons and pass 2 resolves references.

## State and Persistence Behavior

The header does not define state, but all functions operate against global parser state declared in implementation files, especially `policydbp`, `id_queue`, and the module compiler scope stack. Objects appended through this API become part of the persistent `policydb_t` tree.

## Dependencies and Risks

Because this is a C header with no ownership annotations beyond comments, callers must obey return-code conventions. In particular `declare_symbol()` can return `1` to mean the symbol already existed and the caller must free the datum. Misinterpreting `require_symbol()` or `declare_symbol()` return values can leak or double-free datums and can corrupt scope bitmaps. The optional-block APIs must be balanced in grammar actions.

## Test Signals

Compile coverage should ensure all parser users see consistent prototypes. Behavioral tests should exercise each exported require/declaration wrapper, optional block transitions, and scope checks for symbols and permissions.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/module_compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/parse_util.c -->
# sources/security-integrity/selinux/checkpolicy/parse_util.c

## Purpose

`parse_util.c` provides `read_source_policy()`, a shared helper for checkpolicy/checkmodule-style tools to parse a textual SELinux policy source into an already initialized `policydb_t`. It centralizes file opening, parser global setup, two-pass parsing, cleanup of parser resources, and user-facing error reporting.

## Important APIs and Functions

`read_source_policy(policydb_t *p, const char *file, const char *progname)` opens `file` as `yyin`, creates the global `id_queue`, sets `mlspol` from `p->mls`, assigns global `policydbp`, initializes `policydbp->name`, and runs the yacc parser twice. It calls `init_parser(1, file)`, `yyparse()`, rewinds the file, calls `init_parser(2, file)`, `yyrestart(yyin)`, and parses again. It treats either a nonzero parser return or nonzero `policydb_errors` as failure.

## Control Flow

The helper is linear and cleanup-oriented. It returns immediately if the source file cannot be opened. Once `id_queue` exists, all failures go through `cleanup`, which destroys the queue, closes `yyin`, and calls `yylex_destroy()`. A successful two-pass parse sets `rc = 0`.

## State and Persistence Behavior

The function mutates global parser variables declared in `policy_define.c` and `policy_scan.l`: `yyin`, `id_queue`, `policydb_errors`, `policydbp`, and `mlspol`. It also writes `policydbp->name = strdup(file)`. The parsed policy contents persist in the caller-provided `policydb_t`; parser temporaries are destroyed before returning.

## Dependencies and Integration Points

This file depends on `parse_util.h`, `queue.h`, generated yacc/flex symbols, and libsepol `policydb_t`. It is used wherever a source policy needs to be read without immediately running higher-level assertion or hierarchy checks. It assumes the caller already created and configured the policydb, including policy type and target settings.

## Risks and Edge Cases

The helper has process-global parser state and is not reentrant. It overwrites `policydbp->name` without freeing any existing name at this layer, so callers should pass a fresh or appropriately managed policydb. If pass 1 partially mutates `policydb_t` and pass 2 fails, the caller receives `-1` with partial state still in `p`. Cleanup always destroys `id_queue`; other globals are left pointing at closed/destroyed resources until the next parse setup.

## Test Signals

Tests should cover unreadable files, allocation failure paths where practical, pass-1 syntax errors, pass-2 semantic errors, MLS and non-MLS policydb setup, and repeated calls in one process to detect stale flex/parser state.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/parse_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/parse_util.h -->
# sources/security-integrity/selinux/checkpolicy/parse_util.h

## Purpose

`parse_util.h` declares the shared source-policy parsing entry point for checkpolicy-related tools. It documents that callers must provide an already created and configured `policydb_t`, and that this helper only parses source into the policydb without running assertion, hierarchy, or other post-parse validation.

## Important API

`int read_source_policy(policydb_t *p, const char *file, const char *progname);`

`p` is the destination policydb, `file` is the source policy path, and `progname` is used in diagnostics. The return contract is `0` for success and `-1` for parse/setup failure.

## Control Flow and Integration

The header is consumed by tools that need the same two-pass parser behavior. It includes `<sepol/policydb/policydb.h>` so callers have `policydb_t`. The implementation wires into flex/yacc globals, `queue.c`, `policy_define.c`, and `policy_scan.l`.

## State, Dependencies, and Risks

The header itself is stateless. Its most important design signal is the comment that the policydb must already be configured. If a caller does not set policy type, target platform, or MLS mode correctly before calling, grammar actions can reject valid constructs or build the wrong object context tables.

## Test Signals

API-level tests should instantiate a policydb, set required policy properties, call `read_source_policy()`, and verify both success output and parser error handling for malformed source.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/parse_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/policy_define.c -->
# sources/security-integrity/selinux/checkpolicy/policy_define.c

## Purpose

`policy_define.c` is the semantic action engine for the SELinux checkpolicy grammar. It consumes identifier segments accumulated in `id_queue` by `policy_parse.y`, validates them against current scope and policy mode, creates libsepol policydb objects, and appends rules, contexts, constraints, booleans, MLS structures, and module declarations. It is the largest bridge between textual policy syntax and the in-memory `policydb_t`.

## Important APIs, Types, and Functions

Global parser state includes `policydb_t *policydbp`, `queue_t id_queue`, `unsigned int pass`, and `int mlspol`. `init_parser()` resets line counters, errors, pass number, source file, and the identifier queue. `insert_id()` and `insert_separator()` are called by grammar productions to enqueue strings and NULL separators.

Symbol and declaration actions include `define_class()`, `define_common_perms()`, `define_av_perms()`, `define_polcap()`, `define_bool_tunable()`, `define_attrib()`, `define_type()`, `define_typealias()`, `define_typeattribute()`, `define_typebounds()`, `define_role_types()`, `define_role_attr()`, `define_roleattribute()`, `define_attrib_role()`, and `define_user()`.

Rule actions include `define_te_avtab()`, `define_te_avtab_extended_perms()`, `define_compute_type()`, `define_filename_trans()`, `define_role_trans()`, `define_role_allow()`, `define_range_trans()`, and their conditional variants. Helpers such as `set_types()`, `set_roles()`, `read_classes()`, and extended-permission range builders translate grammar sets into bitmaps and rule nodes.

MLS and constraint actions include `define_sens()`, `define_dominance()`, `define_category()`, `define_level()`, `define_constraint()`, `define_validatetrans()`, `define_cexpr()`, and semantic category parsing helpers.

Object context actions include `define_initial_sid_context()`, Xen-specific `define_pirq_context()`, `define_iomem_context()`, `define_ioport_context()`, `define_pcidevice_context()`, `define_devicetree_context()`, SELinux network/context functions (`define_port_context()`, `define_netif_context()`, IPv4/IPv6 node variants), Infiniband functions, `define_fs_use()`, and `define_genfs_context()`.

## Control Flow

The file is designed around two parser passes. Pass 1 generally declares symbols, builds optional/module skeletons, and drains queue entries for constructs that cannot be fully resolved yet. Pass 2 validates references, expands sets, appends real rules, and fills contexts. Many functions start with a `pass` branch that consumes queued identifiers and returns early.

For TE rules, the grammar queues source types, target types, classes, and permissions separated by NULLs. `define_te_avtab_helper()` builds an `avrule_t`, handles `self`/`-self`, wildcard and complement permission syntax, validates permission scope, and returns a rule appended by `append_avrule()`. Extended permissions add a template rule, parse ioctl or netlink ranges, normalize omitted ranges, split complete/partial drivers, and append one or more `avrule_t` nodes with `av_extended_perms_t`.

For object contexts, functions parse raw numeric or address arguments from grammar semantic values plus queued strings, call `parse_security_context()`, validate platform support, check duplicates/overlap/hiding, and insert into `policydbp->ocontexts` or `policydbp->genfs`.

## State and Persistence Behavior

All successful definitions mutate `policydbp`. Common persistent structures include symbol tables, value-to-name indexes, role/type/user local declarations, `avrule_decl_t` lists, conditional lists, role transition lists, filename transition tables, MLS semantic ranges, `ocontext_t` linked lists, and genfs linked lists. Temporary queue strings are usually freed as they are consumed. Rule and context nodes become owned by policydb destruction once appended.

## Dependencies and Integration Points

This file depends on libsepol policydb, services, conditional, hierarchy, expand, polcaps, and module-compiler APIs. It receives syntax shape from `policy_parse.y`, tokens and source locations from `policy_scan.l`, and queue operations from `queue.c`. The append and scope functions in `module_compiler.c` are critical for module correctness.

## Risks and Edge Cases

The dominant risk is queue discipline: every grammar production must enqueue exactly what the target define function expects. A mismatch can silently shift later fields. Many functions must drain queues on pass 1 to keep pass 2 clean. The file is not reentrant because of global parser state. Memory ownership varies between "free immediately", "insert into policydb", and "destroy on error"; changes need careful error-path review.

Semantic edge cases include policy-version gating for conditional extended permissions, target-platform gating for Xen versus SELinux object contexts, duplicate and overlap checks for ports/nodes/ibpkeys, class permission vector width limits, forbidden dot syntax for MLS identifiers and aliases, `self` handling with complements, and prohibition on mixing booleans and tunables in one conditional expression.

## Test Signals

High-value tests parse policies covering class/common permission declarations, default rules, MLS definitions, type aliases/attributes/bounds, AV rules with `*`, `~`, `self`, and `-self`, extended `ioctl` and `nlmsg` ranges, conditionals, require/optional module blocks, user MLS ranges, all object context families, duplicate detection, platform rejection paths, and policy-version rejection paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/policy_define.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/policy_define.h -->
# sources/security-integrity/selinux/checkpolicy/policy_define.h

## Purpose

`policy_define.h` declares the parser semantic action API implemented by `policy_define.c`. It is included by the yacc grammar and exposes one function per major SELinux policy language construct. The header is the grammar-to-implementation contract.

## Important APIs and Constants

`COND_ERR` is a sentinel `avrule_t *` value used by yacc actions for conditional rule failures, because `NULL` can represent an empty valid conditional rule list. `TRUE` and `FALSE` are local boolean constants.

The declarations cover conditional AV rule construction (`define_cond_*`), conditional expressions (`define_cond_expr()`), class and permission definitions, booleans/tunables, MLS sensitivity/category/level definitions, constraints, type/role/user declarations, all major TE/RBAC rules, object-context declarations, policy capabilities, permissive and neveraudit flags, and queue insertion helpers (`insert_id()`, `insert_separator()`).

## Control Flow and Integration

`policy_parse.y` calls these functions in grammar reductions after tokens have been queued. Some functions return `int` for direct success/failure, some return allocated or sentinel `avrule_t *`/`cond_expr_t *` values used by conditional grammar productions, and `define_cexpr()` uses `uintptr_t` because yacc carries constraint-expression pointers through an integer-compatible union field.

## State and Persistence Behavior

The header itself is stateless. Its functions operate on global parser state (`policydbp`, `id_queue`, `pass`, `mlspol`, line globals) and mutate the policydb. The queue helper APIs define the shared ordering contract: callers insert identifiers either at tail or head and use NULL separators to delimit logical sets.

## Dependencies and Risks

Because the header does not include every libsepol type it mentions, it assumes includers have already pulled in policydb/conditional definitions. Return-value conventions are mixed and parser-specific; incorrect yacc action checks can confuse an empty construct with an error, especially around `COND_ERR`. Any signature change must be coordinated with grammar `%type` declarations in `policy_parse.y`.

## Test Signals

Compilation of the generated parser is the first signal. Behavioral tests should map grammar productions to the correct function calls and verify that sentinel returns abort only when intended.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/policy_define.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/policy_parse.y -->
# sources/security-integrity/selinux/checkpolicy/policy_parse.y

## Purpose

`policy_parse.y` is the Bison grammar for SELinux source policies and loadable modules. It defines the parse shape for base policies, module policies, MLS constructs, TE/RBAC rules, constraints, security contexts, network/device contexts, optional blocks, and require blocks. Semantic actions push lexed identifiers into `id_queue` and call `policy_define.c`/`module_compiler.c` functions to mutate `policydbp`.

## Important Grammar Areas

The top-level `policy` can be `base_policy` or `module_policy`. `base_policy` sequences classes, initial SIDs, access vectors, default rules, optional MLS, TE/RBAC/users/constraints, indexes, initial SID contexts, fs/genfs, network, device, and Infiniband contexts. `module_policy` parses a module header followed by an avrule block, then calls `end_avrule_block()` and indexes symbols.

Class/common permission grammar maps to `define_class()`, `define_common_perms()`, and `define_av_perms()`. TE/RBAC grammar maps to type/attribute/bool/tunable definitions, AV rules, extended permissions, transitions, role rules, policy capabilities, permissive, and neveraudit actions.

Conditional grammar builds `cond_expr_t` and `avrule_t` lists, then `define_conditional()` attaches them. Constraint grammar builds postfix-style `constraint_expr_t` lists through `define_cexpr()`. Require and optional block grammar delegates to module compiler APIs.

Utility nonterminals such as `names`, `names_push`, `id_comma_list`, `mls_level_def`, `mls_range_def`, `security_context_def`, `path`, `filename`, `number`, and IP address productions control queue ordering and semantic values.

## Control Flow

The grammar is reduction-driven. Lexical rules return tokens with text in `yytext`; grammar actions call `insert_id(yytext, 0)` for normal queue order, `insert_id(..., 1)` for pushed reverse-order constraint name sets, and `insert_separator()` to delimit lists. Once a full construct is recognized, the corresponding `define_*()` function drains the queue in the expected order.

Base policies call `define_policy(pass, 0)` before class parsing. Module policies call `define_policy(pass, 1)` after `MODULE identifier version_identifier ';'`. Indexing is embedded at key points: after access-vector definitions, after TE/RBAC/users/constraints, and after module parsing.

## State and Persistence Behavior

The grammar has no persistent storage of its own beyond Bison semantic values. Its actions mutate global `id_queue`, `policydbp`, and module compiler state. Numeric semantic values are produced for ports, Xen resources, and masks; most identifiers persist only after semantic actions insert copies into policydb structures.

## Dependencies and Integration Points

It includes libsepol policy headers, `queue.h`, `module_compiler.h`, and `policy_define.h`. It depends on `policy_scan.l` for tokens and on the exact function signatures declared in `policy_define.h`. `checkpolicy` build rules generate parser C/header files from this grammar.

## Risks and Edge Cases

Queue ordering is the main fragility. Nested sets, pushed names, MLS ranges, and security contexts rely on NULL separators in precise positions. Conditional filename transitions are explicitly rejected. Extended permissions support nested ranges and omission syntax. The grammar accepts module versions as version identifiers, numbers, or IPv4-like tokens. Numeric conversions abort on `errno` and unsigned overflow.

## Test Signals

Parser tests should cover both top-level policy forms, nested name sets, constraints with all operators, conditional expressions precedence, require lists, optional/else blocks, security contexts with and without MLS ranges, IPv4/IPv6 CIDR node contexts, genfs typed and untyped forms, extended permission nested sets, and module version token variants.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/policy_parse.y -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/policy_scan.l -->
# sources/security-integrity/selinux/checkpolicy/policy_scan.l

## Purpose

`policy_scan.l` is the Flex scanner for SELinux source policy syntax. It recognizes keywords, identifiers, paths, filenames, numbers, IP/CIDR forms, operators, punctuation, comments, whitespace, and `#line` directives. It also owns parser diagnostic location state and warning/error formatting.

## Important APIs and Globals

The scanner defines `source_file`, `source_lineno`, `policydb_lineno`, `policydb_errors`, and `werror`. `yyerror()` prints an error with source file, source line, token, policydb line, and two buffered source lines, then increments `policydb_errors`. `yywarn()` either delegates to `yyerror()` when warnings are fatal or prints a warning. `set_source_file()` and `set_source_line_and_file()` update logical source locations, including preprocessing-style `#line` directives.

For fuzzing builds, `YY_FATAL_ERROR` is redirected to `yyfatal()`, which reports through `yyerror()` and longjmps rather than exiting.

## Control Flow

Lexing is rule ordered. Newline handling captures the next line text into a rotating two-entry `linebuf`, increments policy and source line counters, and uses `yyless(1)` so the newline itself remains available. Keyword rules return named Bison tokens. Generic patterns return `IDENTIFIER`, `NUMBER`, `FILESYSTEM`, `NETIFNAME`, `PATH`, `QPATH`, `FILENAME`, IPv4/IPv6 tokens, and version identifiers. Comments and whitespace are discarded. Operators and punctuation return either named tokens or their character code. Any unrecognized character calls `yyerror()`.

## State and Persistence Behavior

Scanner state is process-global and reset indirectly by `init_parser()` in `policy_define.c`. It does not allocate policy objects. It may mutate `source_file` and line counters during lexing. For quoted paths/filenames, grammar actions later edit `yytext` to strip quotes before queuing.

## Dependencies and Integration Points

The scanner includes the generated parser header (`policy_parse.h` on Android, otherwise `y.tab.h`) so token numbers match the grammar. It integrates with `policy_parse.y` via returned tokens and with `policy_define.c` via `yyerror`, `yywarn`, and source-location globals. It uses standard C library parsing helpers for line directives.

## Risks and Edge Cases

Rule precedence matters. Some token classes overlap, especially identifiers, filesystems, netif names, version identifiers, IPv4 addresses, and numbers. Source line overflow emits warnings. The two-line diagnostic buffer is fixed at 255 bytes per line, so long lines are truncated intentionally. The scanner is not reentrant. Warning-as-error behavior changes control flow by incrementing `policydb_errors`.

## Test Signals

Scanner-focused tests should include every keyword in mixed case where supported, identifiers with underscores/hyphens/dots, invalid characters, quoted paths and filenames, comments, whitespace, long lines, `#line` with and without file names, IPv4/IPv6 and CIDR tokens, version-like strings, and `werror` behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/policy_scan.l -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/queue.c -->
# sources/security-integrity/selinux/checkpolicy/queue.c

## Purpose

`queue.c` implements a small singly linked, double-ended queue used by the checkpolicy parser to shuttle token text and NULL separators from grammar productions to semantic action functions. Although generic in type (`void *` elements), its primary role here is managing dynamically allocated identifier strings.

## Important APIs and Functions

`queue_create()` allocates an empty queue. `queue_insert()` appends an element to the tail. `queue_push()` prepends an element to the head. `queue_remove()` pops and returns the head element. `queue_head()` returns the head element without removing it. `queue_clear()` frees all nodes and their elements but keeps the queue object. `queue_destroy()` frees all nodes/elements and the queue itself.

`queue_map()` applies a callback to each element and stops on nonzero callback status. `queue_map_remove_on_error()` applies a callback and removes elements for which the callback returns nonzero, invoking a second callback on removed elements.

## Control Flow

All mutation functions first handle NULL queue pointers. Insert/push allocate a node and update head/tail consistently. Remove frees only the node, not the returned element. Clear and destroy free both node and element, assuming element ownership belongs to the queue at that time.

## State and Persistence Behavior

The queue persists until `queue_destroy()`. Elements inserted into the parser queue are usually heap-allocated strings from `insert_id()` or NULL separators. Ownership transfers out on `queue_remove()`; callers must free non-NULL returned elements or insert them into policydb-owned structures.

## Dependencies and Integration Points

The implementation depends only on `<stdlib.h>` and `queue.h`. It is used by `policy_define.c`, `parse_util.c`, and `module_compiler.c` as the parser's identifier transport.

## Risks and Edge Cases

Because `queue_clear()` and `queue_destroy()` blindly call `free(p->element)`, the queue is safe only for heap pointers or NULL when those functions are used. It is not thread-safe. `queue_map_remove_on_error()` does not free elements itself; it delegates element cleanup to `g`, then frees the node. Parser correctness depends on preserving insertion order and allowing NULL separators.

## Test Signals

Tests should cover empty operations, append order, push order, mixed push/insert behavior, remove head/tail transitions, clear/destroy with NULL elements, map early-stop behavior, and map-remove tail/head updates.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/queue.h -->
# sources/security-integrity/selinux/checkpolicy/queue.h

## Purpose

`queue.h` declares the generic queue abstraction used by the SELinux checkpolicy parser. It defines the node and queue structures and the operations implemented in `queue.c`.

## Important Types and APIs

`queue_element_t` is `void *`, allowing the parser to store strings and NULL list separators. `queue_node_t` stores one element plus the next pointer. `queue_info_t` stores head and tail pointers, and `queue_t` is a pointer to that structure.

The API supports creation, tail insertion, head insertion, removal, peeking, clearing, destruction, mapping, and conditional removal during mapping.

## Control Flow and Integration

The parser calls `queue_insert()` for normal token order and `queue_push()` for grammar productions that need reverse-order name construction. Semantic functions consume with `queue_remove()` and occasionally inspect the next item with `queue_head()`.

## State and Persistence Behavior

The header exposes the internal structure rather than making `queue_t` opaque, so callers could inspect or mutate internals directly. In practice the parser uses the functions. The implementation treats stored elements as owned by the queue when clearing/destroying.

## Dependencies and Risks

There are no external dependencies. The main risk is ownership ambiguity caused by a generic `void *` queue and public structs. Callers must not put stack pointers or string literals into a queue that may be cleared or destroyed.

## Test Signals

Compile and unit tests should confirm API consistency with `queue.c`, especially head/tail updates and NULL element support.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/test/Makefile -->
# sources/security-integrity/selinux/checkpolicy/test/Makefile

## Purpose

This Makefile builds the checkpolicy test utilities `dispol` and `dismod`. In this subset, `dismod.c` is the relevant companion source. The Makefile is intentionally small and assumes libsepol is available either as an explicit archive dependency or through linker search paths.

## Important Targets and Variables

`CFLAGS ?= -g -Wall -W -Werror -O2` supplies default strict compilation flags while allowing the environment to override them. `LIBSEPOLA` can name a specific `libsepol.a`; if unset, `LDLIBS_LIBSEPOLA := -l:libsepol.a` asks the linker to find the static archive by name.

`all` builds both `dispol` and `dismod`. Each executable links its object file, optional `$(LIBSEPOLA)`, normal `CPPFLAGS`, `CFLAGS`, `LDFLAGS`, and `$(LDLIBS_LIBSEPOLA)`. `clean` removes the two binaries and object files.

## Control Flow and Integration

The Makefile delegates compilation of `.c` to make's built-in suffix rules and defines only link commands. It is part of the checkpolicy test area and links directly against libsepol internals used by the utilities.

## State and Persistence Behavior

Build outputs are local binaries and `.o` files in the test directory. No generated source or persistent test data is managed here.

## Dependencies and Risks

The Makefile assumes a compiler, make built-in compile rules, and a linkable static libsepol archive. The indentation before `LDLIBS_LIBSEPOLA :=` is spaces in the conditional body; GNU make accepts it for variable assignment, but recipe lines still require tabs. `-Werror` can make builds sensitive to compiler-version warnings.

## Test Signals

Running `make` should produce `dispol` and `dismod`; `make clean` should remove them. A useful CI signal is building once with explicit `LIBSEPOLA=/path/to/libsepol.a` and once with only linker search paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/test/dismod.c -->
# sources/security-integrity/selinux/checkpolicy/test/dismod.c

## Purpose

`dismod.c` is an interactive and scriptable diagnostic utility for displaying the contents of a binary SELinux base policy or loadable module in a textual, module-oriented form. It can show unconditional and conditional AV rules, users, booleans, roles, types/attributes/aliases, role transitions/allows, initial SIDs, requirements, declarations, policy capabilities, unknown handling, filename transitions, version info, and can link an additional module into a loaded base policy.

## Important APIs, Types, and Functions

The file owns a static `policydb_t policydb` and a command table mapping single-character commands to descriptions and flags. `usage()` prints command help, including noninteractive `--actions` mode.

Rendering helpers include `render_access_mask()`, `render_access_bitmap()`, `display_id()`, `display_type_set()`, `display_mod_role_set()`, `display_avrule()`, `display_class_set()`, `display_role_trans()`, `display_role_allow()`, `display_filename_trans()`, and `display_scope_index()`. These convert libsepol values and bitmaps back into readable identifiers and policy-like rule syntax.

Policy loading is handled by `read_policy()`, which peeks at the first 32-bit little-endian word. If it matches `SEPOL_MODULE_PACKAGE_MAGIC`, it reads a module package through `sepol_module_package_read()` after wiring the package policy pointer to the caller's `policydb_t`; otherwise it calls `policydb_read()`.

`link_module()` prompts for a module filename, reads it into a temporary `policydb_t`, indexes it, and calls `link_modules()` against the base. The main loop dispatches commands either from `--actions ACTIONS` or stdin.

## Control Flow

`main()` parses options, initializes and reads the policy, verifies policy type, indexes classes and other symbols, optionally prints version/menu, then repeatedly reads a command. Noninteractive mode consumes one character per loop from the actions string and exits when it reaches implicit `q`. Most commands call display helpers over the loaded `policydb`. The `f` command switches output to a user-selected file; `l` performs module linking; `q` destroys the policydb and exits.

## State and Persistence Behavior

The loaded policydb persists globally until quit. Output state is the current `FILE *out_fp`, initially stdout and optionally changed by command `f`. `link_module()` mutates the loaded base policy by linking in an additional module. The utility does not save the modified policy; it only changes the in-memory model for subsequent display commands.

## Dependencies and Integration Points

It depends on libsepol policydb, services, conditional, link, module, util, and polcaps APIs. It uses endian conversion to detect module package magic. It is built by the local test Makefile and is useful for inspecting outputs produced by checkpolicy/checkmodule.

## Risks and Edge Cases

This is a diagnostic tool, not hardened input-processing code. Many failures call `exit(1)`. Interactive filename handling strips the final byte as a newline and assumes `fgets()` returned a line with length. Some formatting assumes indexed value-to-name arrays are populated. `display_id()` asserts the scope datum exists. Changing output files does not close prior non-stdout handles. Module linking requires the initially loaded policy to be base policy and warns that restart may be needed after failure.

## Test Signals

Build tests should compile with `-Werror`. Runtime tests should load both base and module binaries, exercise `--actions` for every command, verify package and raw policy reading, inspect requirements/declarations for modules, switch output files, test invalid options, and link a valid/invalid module into a base policy.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/test/dismod.c -->
