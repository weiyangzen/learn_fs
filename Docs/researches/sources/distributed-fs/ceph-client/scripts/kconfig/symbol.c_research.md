# sources/distributed-fs/ceph-client/scripts/kconfig/symbol.c

## Purpose
`symbol.c` is the core Kconfig symbol engine. It stores symbols, calculates visibility and values, handles bool/tristate/string/int/hex validation, implements choice resolution, applies defaults/selects/implies/ranges/transitional behavior, performs regex symbol search, and detects recursive dependency cycles.

## Important APIs, Types, and Functions
Global constant symbols are `symbol_yes`, `symbol_mod`, and `symbol_no`; `modules_sym` tracks the symbol that enables module support. Public APIs include `sym_get_type()`, `sym_type_name()`, `sym_get_prompt_menu()`, `sym_get_choice_menu()`, `sym_get_range_prop()`, `sym_choice_default()`, `sym_calc_choice()`, `sym_dep_errors()`, `sym_calc_value()`, `sym_clear_all_valid()`, `sym_tristate_within_range()`, `sym_set_tristate_value()`, `choice_set_value()`, `sym_toggle_tristate_value()`, `sym_string_valid()`, `sym_string_within_range()`, `sym_set_string_value()`, `sym_get_string_default()`, `sym_get_string_value()`, `sym_is_changeable()`, `sym_is_choice_value()`, `sym_lookup()`, `sym_find()`, `sym_re_search()`, `sym_check_deps()`, `prop_get_symbol()`, and `prop_get_type_name()`.

Internal dependency-cycle state uses `struct dep_stack`. Search sorting uses `struct sym_match` and `sym_rel_comp()`.

## Control Flow
Symbol calculation starts by checking `SYMBOL_VALID`, initializing a default `newval`, calculating visibility, then applying user values, choice state, defaults, reverse dependencies from `select`, `imply`, direct dependencies, range validation, and module restrictions. Changes mark associated menus as changed and can invalidate all symbols when module support changes.

Choice resolution prioritizes visible user-selected `y`, then visible default, then first visible user-unspecified symbol, then a reverse-order fallback. Dependency checking recursively traverses direct dependencies, reverse dependencies, implied dependencies, property visibility, defaults, and choice members while maintaining a stack for diagnostic output.

## State and Persistence
Symbols are stored in `sym_hashtable`; individual symbols hold current values, user/default values, flags, property lists, menu links, and dependency expressions. Validity and changed flags cache calculations until invalidated. `modules_val` mirrors `modules_sym` and influences tristate-to-bool coercion. Warnings accumulate in `sym_warnings`.

## Dependencies and Integration Points
The file depends on `hash.h`, `xalloc.h`, Kconfig expression/menu/property definitions, and list helpers. It is used by parsers, frontends, config readers/writers, search dialogs, and test harnesses.

## Risks and Edge Cases
This file is highly stateful; missed invalidation can produce stale UI/config output. Transitional symbols are treated as always visible and not writable, and defaults from a single user-set transitional symbol can mark the new symbol as user-valued to avoid prompting. The source contains duplicated lines in several places, including duplicated `if (sym->implied.tri != tri)`, duplicated `if (menu->sym->curr.tri != val)`, and duplicated `continue`; these should be compile- and behavior-tested. Recursive dependency diagnostics are complex and can be sensitive to choice relationships.

## Test Signals
The requested tests exercise choices, randomized choice dependency recalculation, conditional dependencies, no-write behavior for unmet choice dependencies, transitional migration, invalid transitional properties, and recursive dependency errors. Additional tests should cover range validation, `KCONFIG_WERROR`, regex search order, modules disabled behavior, `select` unmet dependency warnings, and `imply`.
