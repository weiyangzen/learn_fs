# Research Group subset-b-008372

This grouped report covers the sepolgen lexer, reference-policy parser/model, policy generation, matching, output, module-compilation, object-model, i18n, and utility modules under `sources/security-integrity/selinux/python/sepolgen/src/sepolgen`. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/lex.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/lex.py

## Purpose
This file is the bundled PLY lexer implementation used by sepolgen's reference-policy parser. It builds a stateful token scanner from `tokens`, `literals`, `states`, and `t_*` rule definitions supplied by a caller module or object, then exposes the familiar `input()` and `token()` runtime API.

## Important APIs, Types, And Functions
`LexToken` is the mutable token record carrying `type`, `value`, `lineno`, and `lexpos`. `LexError` reports scanner failures. `Lexer` owns compiled regex tables, state stacks, ignored characters, error/eof callbacks, input text, cursor position, and table serialization via `writetab()` / `readtab()`. Its public control surface is `input`, `token`, `begin`, `push_state`, `pop_state`, `skip`, `clone`, and iteration.

`LexerReflect` introspects the caller dictionary, validates `tokens`, `literals`, `states`, rule functions, rule strings, `t_error`, and `t_eof`, and detects duplicate rules from module source. `_form_master_re()` composes named regex alternatives, recursively splitting large patterns when Python cannot compile the combined expression. `lex()` is the builder entry point and installs module globals `lexer`, `token`, and `input`. `TOKEN` / `Token` attach regex strings to rule functions.

## Control Flow
Build flow starts in `lex()`: gather caller symbols, reflect and validate them unless optimized, optionally read a cached lextab, build per-state master regexes, inherit `INITIAL` expressions for inclusive states, install ignore/error/eof tables, and optionally write a lextab. Runtime flow in `Lexer.token()` loops over input, skips ignored characters, tries each state regex, constructs a `LexToken`, dispatches rule functions when present, validates returned token types in non-optimized mode, handles literals, calls error handlers, and emits EOF tokens when configured.

## State And Persistence Behavior
Lexer state is in-memory and mutable: `lexpos`, `lineno`, active state, state stack, and current input change during scanning. Optimized mode may persist generated lexer tables to a Python module under `outputdir` or the caller package; `readtab()` reloads those tables and rebinds functions from a dictionary. `clone()` shallow-copies the lexer and can rebind rule methods to another object, so compiled regexes are shared while state cursors become independent.

## Dependencies And Integration Points
The module depends on Python `re`, `sys`, `types`, `copy`, `os`, and `inspect`. It is imported by `refparser.py`, which defines sepolgen's token rules and calls `lex.lex()` from parser global initialization. The API mirrors upstream PLY, so yacc integration expects `token()` and `input()` semantics and `tok.lexer` callbacks.

## Risks And Edge Cases
Regex rules that match empty strings, duplicate `t_` definitions, unspecified token names, missing `t_error`, invalid state specs, and bad literal specs are detected during validation. Optimized table loading trusts cached modules and bypasses validation, so stale tables can hide rule problems until import/version mismatch. `token()` is performance-sensitive and mutates shared lexer attributes while rule functions can also change `lexpos` or state. Cached table writing imports package modules dynamically and can fail on read-only paths. Some Python 2 compatibility branches remain, increasing maintenance complexity.

## Test Signals
Useful tests build lexers from function and string rules, exercise inclusive/exclusive states, ignored tokens, literals, error callbacks that do and do not advance `lexpos`, EOF callbacks, optimized lextab write/read, object-bound cloning, duplicate-rule diagnostics, and unknown token returns. Parser-level tests in `refparser.py` also validate this module indirectly by scanning real `.if`, `.te`, and `.spt` policy text.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/lex.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/matching.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/matching.py

## Purpose
This module scores requested SELinux access vectors against access vectors provided by reference-policy interfaces. It chooses interface matches that cover a requested access while preferring closer permission/type/object-class and information-flow behavior.

## Important APIs, Types, And Functions
`Match` stores an interface candidate, numeric distance, and whether the candidate changes information-flow direction. It inherits rich comparison behavior from `util.Comparison`, ordering by `(dist, info_dir_change)`. `MatchList` separates acceptable `children` from over-threshold or direction-changing `bastards`, exposes `best()`, `all()`, `append()`, and `sort()`, and records the requested `av`.

`AccessMatcher` owns distance penalties and a `objectmodel.PermMappings` instance. `type_distance()` treats exact matches and access id parameters as zero distance. `perm_distance()` computes missing permissions as negative distance and surplus provided permissions as positive distance using permission weights. `av_distance()` combines source type, target type, object class, and permission distance. `av_set_match()` scores an interface access set against one requested vector and penalizes write-capable interfaces for read-only requests. `search_ifs()` scans enabled interfaces by target type and populates a `MatchList`.

## Control Flow
The normal path is `PolicyGenerator` -> `InterfaceGenerator.match()` -> `AccessMatcher.search_ifs()`. `search_ifs()` considers generic target-type interfaces and target-specific interfaces, skips disabled interfaces, computes aggregate distance, accepts non-negative scores, and sorts results. `av_set_match()` caches `av_set.info_dir` after computing permission-flow direction across its rules.

## State And Persistence Behavior
All state is in-memory. `MatchList` accumulates matches for one requested access. `AccessMatcher` is reusable and keeps only configuration. Interface access sets may be mutated by caching `info_dir`, which is a cross-call performance optimization and an observable state side effect.

## Dependencies And Integration Points
It depends on `access` for id-parameter detection, `objectmodel` for permission weights and flow constants, and `util.Comparison` for ordering. It integrates with `interfaces.InterfaceSet`-like objects that expose `tgt_type_all`, `tgt_type_map`, and interface descriptors with `.enabled`, `.name`, and `.access`.

## Risks And Edge Cases
The distance model is heuristic and comments call out expense. Negative/positive distance combination is subtle and can reorder candidates unexpectedly when type/object mismatch and permission surplus combine. `Match.info_dir_change` is initialized but never set in the shown scorer even though `MatchList` checks it, so direction-changing candidates are penalized numerically but not flagged structurally. Mutating `av_set.info_dir` assumes the access set is stable. Threshold defaults may drop viable but broad interfaces.

## Test Signals
Tests should cover exact matches, id-parameter matches, missing and surplus permissions, object-class mismatches, multi-rule interface access sets, write-flow penalty for read-only requests, disabled interfaces, target-type maps, threshold behavior, and sorted best-match selection.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/matching.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/module.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/module.py

## Purpose
This module validates SELinux module names, creates standard reference-policy module directory trees, and wraps command-line compilation/packaging tools for `.te` policy modules.

## Important APIs, Types, And Functions
`is_valid_name(modname)` accepts names that start alphabetically and contain only letters, digits, underscore, hyphen, and period. `ModuleTree` derives canonical file paths for `.te`, `.fc`, `.if`, `.pp`, and `Makefile`, then `create()` makes a module directory, writes a Makefile include, and creates empty standard policy files. `modname_from_sourcename()` strips directory and extension.

`ModuleCompiler` wraps `/usr/bin/checkmodule`, `/usr/bin/semodule_package`, and `/usr/bin/make`. Important attributes include `mls`, `module`, `checkmodule`, `semodule_package`, `make`, `refpol_makefile`, `output`, and `last_output`. `create_module_package()` dispatches to `refpol_build()` for refpolicy builds or to `compile()` plus `package()` for direct builds. `gen_filenames()` maps a `.te` source to `.mod` and `.pp`.

## Control Flow
Directory creation is simple path derivation followed by `os.mkdir`, Makefile write, and empty file creation. Compilation flow builds shell command strings, runs them via `getstatusoutput`, records command/output through `o()`, and raises `RuntimeError` when commands return nonzero. Non-refpolicy builds delete the intermediate `.mod` after packaging.

## State And Persistence Behavior
`ModuleTree.create()` persists a new module subtree on disk. `ModuleCompiler` persists generated `.mod` and `.pp` files in the current working directory or source-relative command context and deletes only the intermediate `.mod` in direct mode. `last_output` stores the most recent command or command output for diagnostics.

## Dependencies And Integration Points
It depends on `selinux.is_selinux_mls_enabled()`, `defaults.refpolicy_makefile()`, filesystem modules, and external SELinux toolchain executables. Generated module trees are consumed by refpolicy build tooling and output produced by `policygen`/`output`.

## Risks And Edge Cases
Command strings are built by joining unquoted paths and source names, so spaces or shell metacharacters in paths can break or become unsafe if caller input is not trusted. `is_valid_name()` indexes `modname[0]` and fails on empty strings. `ModuleTree.create()` assumes parent directories exist and target module directories do not. `gen_filenames()` raises `RuntimeError` with an unused formatting argument pattern. Refpolicy build ignores `sourcename` and runs make against the configured Makefile only.

## Test Signals
Tests should validate allowed and rejected names, empty-name behavior, path derivation, file creation with custom/default Makefile includes, `.te` filename conversion with multiple periods, command construction for MLS/module flags, failure propagation, and cleanup of non-refpolicy `.mod` intermediates.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/module.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/objectmodel.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/objectmodel.py

## Purpose
This module centralizes SELinux object-class and permission knowledge used by policy generation and interface matching. It models permission information-flow direction and relative bandwidth/weight so generic generation logic does not embed object-model details.

## Important APIs, Types, And Functions
`implicitly_typed_objects` lists classes often labeled with the creating process type. Flow constants are `FLOW_NONE`, `FLOW_READ`, `FLOW_WRITE`, and `FLOW_BOTH`, with `str_to_dir` and `dir_to_str` mappings for permission-map files. `PermMap` stores one permission's name, direction, and weight. `PermMappings` stores `classes[obj_class][perm] = PermMap`, defaulting unknown permissions to both-direction flow with weight `5`.

`PermMappings.from_file(fd)` parses Apol/setools-style permission maps with `class` headers and `perm direction weight` rows. `get()` raises on unknown class/permission, `getdefault()` returns defaults, `getdefault_direction()` ORs flow directions for a permission set, and `getdefault_distance()` sums weights.

## Control Flow
Consumers load a permission map once, then scoring code in `matching.py` repeatedly asks for permission weights and flow directions. Parsing is line-oriented and stateful: a `class` row starts a new current class; subsequent rows populate that class until another class row appears.

## State And Persistence Behavior
All state is in-memory. `PermMappings.classes` persists parsed mappings for the object's lifetime. No files are written. Unknown permissions are not cached; every default lookup creates a new `PermMap`.

## Dependencies And Integration Points
`matching.AccessMatcher` uses this module to calculate permission distance and write-flow penalties. `policygen` imports it for generation context. The permission map format is expected to be shipped with sepolgen rather than edited interactively by users.

## Risks And Edge Cases
`from_file()` is deliberately strict and raises `ValueError` on duplicate class declarations, malformed permission rows, or permissions before any class. It treats `fields[0] == "#"` as comments, so inline comments or leading whitespace before comments rely on split behavior. Unknown permissions default to broad both-direction flow, which keeps generation running but can over-penalize or over-allow interface candidates. The module does not validate that directions exist in `str_to_dir` before indexing.

## Test Signals
Tests should cover parsing valid class blocks, skipping blank/comment/single-field lines, duplicate classes, malformed rows, permission-before-class errors, `get` failures, default fallback behavior, combined direction ORing, and distance summation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/objectmodel.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/output.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/output.py

## Purpose
This module formats a `refpolicy.Module` tree into textual reference-policy or CIL output. It also reorders generated policy statements for readability before writing.

## Important APIs, Types, And Functions
`ModuleWriter` holds formatting options: `sort`, `requires`, and `gen_cil`. `write(module, fd)` optionally applies `sort_filter()`, walks the policy tree, propagates CIL mode to each node, and writes each node string on its own line. `set_gen_cil()` toggles output syntax mode.

Comparator helpers include `id_set_cmp()`, `avrule_cmp()`, `ifcall_cmp()`, `rule_cmp()`, and `role_type_cmp()`. `sort_filter(module)` rewrites each node's `children` list into module declarations, blank comments, require blocks, grouped AV/interface rules by source type, role blocks, then leftover children.

## Control Flow
Formatting starts from `ModuleWriter.write()`. Sorting traverses every node from `module.nodes()`, gathers typed child views through `refpolicy.Node` iterators, sorts rules with cmp-style comparators adapted via `util.cmp_to_key`, inserts separator comments like `============= type ==============`, then replaces `node.children`. The final walk emits all nodes depth-first.

## State And Persistence Behavior
The writer mutates the passed module when sorting: child order changes and separator `Comment` nodes are inserted. It writes only to the provided file descriptor and keeps no persistent cache. `node.set_gen_cil()` mutates each node's output mode immediately before string conversion.

## Dependencies And Integration Points
It depends on `refpolicy` AST classes and `util` compatibility helpers. It is the natural downstream consumer of modules generated by `policygen.PolicyGenerator` or parsed by `refparser`.

## Risks And Edge Cases
Sorting is output-specific and destructive; callers that care about original parse order should disable sorting or pass a copy. `id_set_cmp()` assumes non-empty sets when lengths differ and indexes the first sorted value. `rule_cmp()` assumes interface calls have at least one argument and non-interface rule objects expose `src_types`. `ModuleWriter.requires` is defined but not used in the displayed logic. CIL mode depends on each node's `to_string()` correctness.

## Test Signals
Tests should verify stable ordering of module declarations, requires, AV rules, extended AV rules, interface calls, and role types; insertion of source-type separator comments; preservation of miscellaneous children; CIL flag propagation; and behavior with empty modules, empty sets, and interface calls with duplicate comments.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/output.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/policygen.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/policygen.py

## Purpose
This module generates SELinux reference-policy modules from access vectors. It can emit raw allow/dontaudit rules, extended permission rules, require blocks, interface calls, role/type associations, and explanatory comments from audit messages.

## Important APIs, Types, And Functions
Constants `NO_EXPLANATION`, `SHORT_EXPLANATION`, and `LONG_EXPLANATION` control comment detail. `PolicyGenerator` owns the target `refpolicy.Module`, generation flags (`ifgen`, `gen_requires`, `dontaudit`, `xperms`, `gen_cil`), and comment style. Configuration methods enable reference-policy interface generation, require generation, explanations, dontaudit output, xperm generation, and CIL comments. `set_module_name()` creates or updates a `ModuleDeclaration`; `get_module()` optionally calls `gen_requires()`.

Private `__add_av_rule()` converts one access vector to `refpolicy.AVRule`, adds audit explanations and audit2why/setools hints, and appends it. `__add_ext_av_rules()` creates `AVExtRule` children for `av.xperms`. `add_access()` optionally routes vectors through `InterfaceGenerator`. `add_role_types()` appends role-type rules.

`explain_access()` formats short or long audit-message comments and interface alternatives. `call_interface()` maps interface parameter metadata to access-vector fields. `InterfaceGenerator` disables unsupported interfaces, finds matches through `matching.AccessMatcher`, deduplicates generated interface calls, and returns raw vectors plus calls. `gen_requires()` synthesizes `Require` nodes from rules, interface-call args, and role types.

## Control Flow
Generation usually configures a `PolicyGenerator`, sets a module name, calls `add_access()` with an access-vector set, optionally adds role types, then calls `get_module()` and `output.ModuleWriter.write()`. With interface generation enabled, matching runs before raw rule emission; matched accesses become interface calls and unmatched accesses become AV rules.

## State And Persistence Behavior
The generator mutates a `refpolicy.Module` in memory by appending child nodes and inserting requires at node starts. `InterfaceGenerator.calls` accumulates matches across `gen()` calls, so reuse can carry previous matches unless a new generator is created. `PolicyGenerator.domains` lazily caches `setools.seinfo()` results for write diagnostics. No files are written directly.

## Dependencies And Integration Points
It depends on `selinux.audit2why`, optional `setools` symbols (`seinfo`, `sesearch`, constants), `refpolicy`, `objectmodel`, `access`, `interfaces`, `matching`, and `util`. It sits between audit/access parsing and final formatting by `output.py`.

## Risks And Edge Cases
The optional `setools` import silently fails, and broad `except` blocks suppress diagnostics. Interface support is intentionally limited to positional source, target, and object-class parameters; roles and more complex signatures are disabled. `gen_requires()` is noted as untested with nesting and may add duplicate or empty requires. Explanations assume audit messages expose specific fields. Comment generation differs for CIL and policy syntax. Reusing `InterfaceGenerator` may duplicate old call matches.

## Test Signals
Tests should cover raw allow and dontaudit generation, xperm emission, CIL comment prefixes, module declaration style with and without interfaces, short/long explanations, audit2why ALLOW/DONTAUDIT/BOOLEAN/CONSTRAINT comments, interface matching and deduplication, unsupported interface disabling, require synthesis, and behavior when setools is absent.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/policygen.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/refparser.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/refparser.py

## Purpose
This file implements the PLY lexer and yacc grammar for SELinux reference-policy language: core policy statements plus refpolicy/M4 constructs such as `interface`, `template`, `optional_policy`, `tunable_policy`, `ifdef`, `ifelse`, `define`, and `gen_require`. It produces the AST classes from `refpolicy.py`.

## Important APIs, Types, And Functions
The lexer defines punctuation, identifiers, paths, filenames, IPv6 addresses, numbers, and reserved words for modules, object contexts, types, roles, AV rules, type rules, booleans, and refpolicy macros. It ignores whitespace, comments, `dnl`, and `refpolicywarn`.

Parser globals are `m`, `error`, `parse_file`, `spt`, `success`, `parser`, and `lexer`. `collect()` attaches parsed children to parent nodes, optionally tagging conditional branch values. `expand()` expands permission macros through `SupportMacros`. Grammar functions create `ModuleDeclaration`, `Interface`, `Template`, `OptionalPolicy`, `TunablePolicy`, `IfDef`, `IfElse`, `InterfaceCall`, `ObjPermSet`, `SecurityContext`, filesystem/network context nodes, `Type`, `Role`, `AVRule`, `TypeRule`, `TypeBound`, booleans, attributes, and other refpolicy nodes.

Public functions are `create_globals()`, `parse(text, module=None, support=None, debug=False)`, `list_headers(root)`, and `parse_headers(root, output=None, expand=True, debug=False)`.

## Control Flow
`parse()` initializes or reuses global lexer/parser objects, resets line/success state, parses text into a provided or new module, and rebuilds parser globals after failures. `parse_headers()` discovers `.if`, selected `.spt`, and pattern files, parses support macros first, injects a synthetic `can_exec` interface, then parses each module file into `Headers.children`, optionally showing a progress bar.

## State And Persistence Behavior
Parser state is global and reused across calls until failure. The AST is in-memory; parse functions append children to caller-provided modules or a fresh module. Header parsing reads policy files but writes no files. Support macro expansion depends on global `spt`.

## Dependencies And Integration Points
It depends on bundled `lex.py`, bundled `yacc`, `access.AccessVector`, `defaults.headers()`, and `refpolicy` AST classes. Its output feeds `interfaces`, `matching`, `policygen`, and `output`.

## Risks And Edge Cases
The grammar intentionally ignores `require`, permissive, range transition, and role transition semantics. Several productions appear bug-prone: `p_devicetreecon` references `refpolicy.DevicetTeeCon()` instead of `DeviceTreeCon`; some range concatenations use the wrong token index; `p_names()` has an `expand([p[1]])` call missing the destination set. `p_error()` assumes `tok` is not `None`, so EOF syntax errors may fail differently. Global parser state is not thread-safe. Path, filename, IPv6, and context regexes are narrow and may reject valid policy text.

## Test Signals
Tests should parse representative `.if`, `.spt`, and `.te` snippets for every emitted AST type; verify support macro expansion; cover optional/tunable true/false branches; confirm parser rebuild after syntax failure; exercise comments/refpolicywarn handling; and include regression tests for devicetreecon, type/role transitions, ranges, EOF errors, quoted filenames, IPv6 nodecon, and names with complements.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/refparser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/refpolicy.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/refpolicy.py

## Purpose
This module defines sepolgen's reference-policy AST and string emitters. It represents unprocessed refpolicy/M4 constructs, policy statements, contexts, classes, rules, declarations, comments, support macros, and CIL/policy output variants.

## Important APIs, Types, And Functions
`PolicyBase`, `Node`, and `Leaf` provide parent/comment/CIL fields, child traversal, and string conversion. `walktree()` and `walknode()` traverse ASTs. `IdSet`, `list_to_space_str()`, and `list_to_comma_str()` format SELinux identifier sets. `SecurityContext` parses and emits SELinux contexts, using libselinux translation and MLS defaults.

Core declaration/rule classes include `Type`, `TypeAlias`, `Attribute`, `Attribute_Role`, `TypeAttribute`, `RoleAttribute`, `Role`, `AVRule`, `AVExtRule`, `TypeRule`, `TypeBound`, `RoleAllow`, `RoleType`, `ModuleDeclaration`, and `Bool`. Context classes include `InitialSid`, `GenfsCon`, `FilesystemUse`, `PortCon`, `NodeCon`, `NetifCon`, `PirqCon`, `IomemCon`, `IoportCon`, `PciDeviceCon`, and `DeviceTreeCon`. Refpolicy containers include `Headers`, `Module`, `Interface`, `TunablePolicy`, `Template`, `IfDef`, `IfElse`, `OptionalPolicy`, and `SupportMacros`. `Require`, `ObjPermSet`, `ClassMap`, and `Comment` support generated output and macro expansion. `XpermSet` stores extended permission ranges and complements.

## Control Flow
Parsers and generators instantiate leaf/node classes, populate string fields and `IdSet`s, append them to `children`, then output code through `to_string()` or `output.ModuleWriter`. `walktree()` enables type-filtered views such as `node.avrules()` and `node.interfaces()`. `SupportMacros.by_name()` lazily builds a recursively expanded permission map from child `ObjPermSet`s.

## State And Persistence Behavior
The AST is mutable in memory. `children`, comments, CIL mode, require sets, support-macro maps, xperm ranges, and identifier sets can all change after creation. No persistence occurs directly, but `to_string()` is the serialization boundary used by `output.py`.

## Dependencies And Integration Points
It depends on `selinux` for context translation and MLS checks. It is the central integration point for `refparser` (producer), `policygen` (producer/mutator), `matching` and `interfaces` (consumers of rules and parameters), and `output` (serializer).

## Risks And Edge Cases
Validation is intentionally light: invalid identifiers, mismatched permissions, and M4 `$1` placeholders can live in rules. Several implementation issues are visible: `PolicyBase.__init__` ignores the `parent` argument; `RoleAttribute.to_string()` references `self.type` in CIL mode though the class defines `role`; `Attribute.to_string()` appears to swap CIL/non-CIL strings; `Bool.to_string()` checks `s.state` instead of `self.state`; `InitialSid` defines `__init` rather than `__init__`; some CIL emitters may omit separators/newlines. `walktree(type=...)` filters children before descending, so it can skip descendants under non-matching intermediate nodes.

## Test Signals
Tests should cover string output for every leaf in both policy and CIL modes, `SecurityContext` parsing/default MLS behavior, xperm range normalization and complements, support macro recursive expansion, traversal helpers, require generation strings, comments and comment merging, `InterfaceCall.matches()`, and regression tests for the typo/field issues noted above.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/refpolicy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/sepolgeni18n.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/sepolgeni18n.py

## Purpose
This tiny module provides the `_()` translation function used by sepolgen callers. It centralizes gettext setup for the `selinux-python` message catalog.

## Important APIs, Types, And Functions
The only exported behavior is `_`. On success, `_` is bound to `gettext.translation("selinux-python", localedir="/usr/share/locale", fallback=True).gettext`. On any import/setup failure, `_` falls back to an identity function returning the original string.

## Control Flow
Import-time code tries to import `gettext`, construct a translation object with fallback enabled, and bind `_`. The fallback `except` handles all errors and defines a local identity function.

## State And Persistence Behavior
State is import-time only. No files are written. Runtime translation depends on system locale and installed `.mo` files under `/usr/share/locale`, but `fallback=True` avoids hard failure when catalogs are absent.

## Dependencies And Integration Points
It depends only on Python `gettext` and the system locale catalog path. Other sepolgen modules can import `_` for translatable messages without carrying gettext setup.

## Risks And Edge Cases
The broad bare `except` hides all setup problems, including coding errors. The fallback function shadows built-in-style `_` naming and uses parameter name `str`, which shadows the type but is harmless here. The localedir is hard-coded, so relocatable installs may silently run untranslated.

## Test Signals
Tests should cover import with gettext available, missing catalog fallback, forced gettext import/setup failure, and identity behavior for untranslated strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/sepolgeni18n.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/util.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/util.py

## Purpose
This module contains small compatibility and utility helpers used across sepolgen: progress display, set helpers, locale-aware byte/string conversion, rich-comparison scaffolding, and `cmp` compatibility.

## Important APIs, Types, And Functions
`PY3`, `bytes_type`, and `string_type` abstract Python version differences. `ConsoleProgressBar` writes a fixed 0-100 scale and advances in 50 two-percent blocks through `start()` and `step()`. `set_to_list()` copies set-like containers into lists. `first(s, sorted=False)` returns one element, optionally sorted deterministically. `encode_input()` and `decode_input()` use `locale.getpreferredencoding()` with UTF-8 fallback on `UnicodeError`. `Comparison` implements rich comparison methods in terms of subclass `_compare()`. `cmp_to_key` is imported from `functools` on modern Python or locally implemented for Python 2.6. `cmp(first, second)` returns -1/0/1-style ordering.

## Control Flow
Callers use these helpers directly. `ConsoleProgressBar.step()` updates current progress, computes displayed blocks, caps at 50, writes new indicator characters, flushes, and terminates with a newline once complete. `Comparison` subclasses implement only `_compare`; Python operators delegate to it.

## State And Persistence Behavior
Only `ConsoleProgressBar` holds mutable state: current steps, displayed blocks, output handle, and done flag. Encoding helpers and comparison helpers are stateless. The module writes to the supplied output stream only.

## Dependencies And Integration Points
`matching.Match` inherits from `Comparison`; `output.sort_filter()` uses `cmp_to_key`, `cmp`, `set_to_list`, and `first`; `refparser.parse_headers()` uses `ConsoleProgressBar`; encoding helpers are available for CLI-facing modules.

## Risks And Edge Cases
`first()` is nondeterministic unless `sorted=True` and raises `IndexError` on empty input. Encoding helpers assume the input type has `.encode()` or `.decode()` as appropriate; passing bytes to `encode_input()` on Python 3 or str to `decode_input()` can fail differently. `ConsoleProgressBar` can overrun semantics if `steps` is zero and does not clamp `current`. `Comparison` leaves hashing behavior to subclasses.

## Test Signals
Tests should cover deterministic and nondeterministic first-element paths, empty containers, progress output at start/mid/completion, locale encoding fallback, decode fallback, comparison delegation for all operators, `cmp` ordering, and `cmp_to_key` sorting behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/util.py -->
