# sources/distributed-fs/ceph-client/scripts/kconfig/parser.y

## Purpose
`parser.y` is the Bison grammar and parse driver for Kconfig files. It recognizes Kconfig statements, creates the menu/symbol/property tree, handles variable assignment syntax used by the preprocessor, validates structural constraints, and exposes `conf_parse()` and `zconfdump()`.

## Important APIs, Types, and Functions
The grammar defines tokens for Kconfig keywords, expression operators, words, quoted words, help text, and assignment values. Semantic types cover strings, symbols, expressions, menus, symbol types, and variable flavors.

Important parser actions call shared APIs such as `menu_add_entry()`, `menu_add_prompt()`, `menu_set_type()`, `menu_add_expr()`, `menu_add_symbol()`, `menu_add_dep()`, `menu_add_visibility()`, `menu_add_menu()`, `menu_end_menu()`, `sym_lookup()`, and expression constructors. Post-parse validation is implemented by `transitional_check_sanity()`, `choice_check_sanity()`, and dependency checks through `sym_check_deps()`. `zconf_endtoken()`, `zconf_error()`, and `yyerror()` handle diagnostics. `zconfdump()` emits a normalized view of the parsed tree.

## Control Flow
Parsing starts in `conf_parse(name)`: initialize autoconf dependency text, initialize scanning, initialize the root menu, run `yyparse()`, append autoconf dependency rules and environment-variable dependency rules, delete preprocessor variables, check errors, ensure `modules_sym`, install a default root prompt if needed, finalize menus, then walk each menu entry for recursive dependencies, transitional sanity, and choice-member sanity.

The grammar supports `mainmenu`, `config`, `menuconfig`, `choice`, `if`, `menu`, `source`, `comment`, help blocks, `depends on`, `visible if`, prompts, defaults, `select`, `imply`, `range`, `modules`, `transitional`, boolean/tristate/int/hex/string types, expressions, and `=`, `:=`, `+=` assignments.

## State and Persistence
Global parser state includes `current_menu`, `current_entry`, `current_choice`, `cdebug`, and Bison error count `yynerrs`. Parse results persist in the process-global Kconfig menu/symbol graph. `autoconf_cmd` records dependency rules for generated config outputs. Variable definitions persist only for parse time and are freed after parsing.

## Dependencies and Integration Points
The grammar integrates with scanner functions such as `zconf_initscan()`, `zconf_nextfile()`, and `zconf_starthelp()`, the preprocessor API in `preprocess.h`, shared Kconfig internals, and expression/menu/symbol modules. It feeds every Kconfig frontend and noninteractive config mode.

## Risks and Edge Cases
Because this is the grammar root, parse errors abort configuration. The source contains duplicated statements, including duplicate `menu_add_symbol(P_SELECT, ...)` and duplicate `return 0` in `transitional_check_sanity()`, which should be checked against intended behavior. Transitional symbols are constrained to help-only plus no non-yes dependencies/visibility; this is validated only after `menu_finalize()`. Source/end blocks must be in the same file, and recursive or repeated includes depend on scanner-side detection.

## Test Signals
The requested tests cover auto submenu construction, choices, randomized choice dependencies, conditional dependencies, recursive dependency errors, include recursion/repetition errors, transitional validation, and preprocessing syntax. Parser-specific validation should also include malformed end tokens, blank help text, duplicate help text, invalid choice defaults, and menuconfig without prompts.
