# sources/distributed-fs/ceph-client/scripts/kconfig/menu.c

## Purpose

`menu.c` builds, finalizes, validates, traverses, and describes the shared kconfig menu tree. It is the bridge between parser-created raw entries and frontend-ready menu structures with inherited dependencies, visibility, selects/implies, automatic submenus, and help/search text.

## Important APIs, Types, and Functions

Public APIs include `menu_next()`, `menu_warn()`, `_menu_init()`, `menu_add_entry()`, `menu_add_menu()`, `menu_end_menu()`, `menu_add_dep()`, `menu_set_type()`, `menu_add_prompt()`, `menu_add_visibility()`, `menu_add_expr()`, `menu_add_symbol()`, `menu_finalize()`, `menu_has_prompt()`, `menu_is_empty()`, `menu_is_visible()`, `menu_get_prompt()`, `menu_get_parent_menu()`, `menu_get_menu_or_parent_menu()`, `get_jump_key_char()`, `get_relations_str()`, `menu_get_ext_help()`, and `menu_dump()`. Internal helpers validate properties and format symbol/location/dependency strings.

## Control Flow

During parsing, `_menu_init()` sets the root insertion point, and `menu_add_*()` functions append entries and properties under `current_menu`. `menu_finalize()` recursively propagates parent dependencies, rewrites literal `m` to depend on `MODULES`, simplifies expressions, records reverse dependencies for `select`/`imply`, creates automatic submenus for consecutive dependents, flattens promptless/if nodes, and warns about invalid types/properties. Runtime frontends then use `menu_is_visible()`, traversal helpers, and help-generation functions.

## State and Persistence Behavior

The file owns `rootmenu` and parser build pointers (`current_menu`, `current_entry` are declared in `internal.h`). It mutates symbol dependency fields (`dir_dep`, `rev_dep`, `implied`), menu parent/list/next links, prompt visibility, flags, and frontend jump-key records. It does not write files.

## Dependencies and Integration Points

It depends on `expr.c` for dependency transformations, `symbol.c` for symbol typing/value/default helpers, parser globals from the lexer, list helpers, and `gstr` string utilities. `mconf` and `gconf` depend on its visibility, help, search relation, and parent-menu APIs.

## Risks and Edge Cases

Automatic submenu creation is subtle and can change frontend structure without explicit `menu` blocks. Flattening promptless nodes rewrites tree links, so stale parent/list assumptions are dangerous during finalization. Select/imply expressions must include the selecting symbol and condition or dependency diagnostics become wrong. `menu_is_visible()` has side effects through symbol calculation and prompt visibility caching.

## Test Signals

Parser tests for auto submenu, conditional dependencies, visible-if, select/imply, invalid ranges/defaults, unknown types, choice defaults, prompt redefinition warnings, help/search relation text, and tree dump shape are strong signals.
