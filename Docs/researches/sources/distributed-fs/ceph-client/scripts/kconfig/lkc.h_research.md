# sources/distributed-fs/ceph-client/scripts/kconfig/lkc.h

## Purpose

`lkc.h` is the main internal public header for kconfig C sources. It ties together `expr.h`, generated prototypes, lexer/parser entry points, string-buffer utilities, menu APIs, and symbol APIs.

## Important APIs, Types, and Functions

It defines `SRCTREE`, the runtime `CONFIG_` prefix via `CONFIG_prefix()`, `xfwrite()`, and `struct gstr`. It declares parser/lexer hooks (`zconfdump()`, `zconf_starthelp()`, `zconf_fopen()`, `zconf_initscan()`, `zconf_nextfile()`, `yylex()`), file lookup, string builder functions, menu traversal/finalization/help functions, root menu state, and symbol helper functions such as `sym_clear_all_valid()`, `sym_choice_default()`, `sym_calc_choice()`, `sym_get_range_prop()`, and inline choice/value predicates.

## Control Flow

This header supplies inline helpers and macros rather than full algorithms. `menu_for_each_entry()` expands into depth-first traversal using `menu_next()`. `xfwrite()` centralizes fwrite error reporting for expression/config printing.

## State and Persistence Behavior

It declares shared state such as `rootmenu`, `autoconf_cmd`, and parser line globals. It does not persist data directly, but its APIs are used by config persistence and UI frontends.

## Dependencies and Integration Points

Every major kconfig source includes this header. It bridges `confdata.c`, `expr.c`, `menu.c`, `symbol.c`, parser/lexer code, and `mconf`/`gconf` frontends. `CONFIG_` may be overridden by the environment, and code using the macro must tolerate a function-like runtime prefix.

## Risks and Edge Cases

The `CONFIG_` macro is redefined to call `CONFIG_prefix()`, so it is not a string literal in all contexts. `xfwrite()` asserts nonzero element length but only prints on error. Inline choice checks rely on the null-name convention from `expr.h`.

## Test Signals

Compile all tools with default and overridden `CONFIG_`, run menu traversal/help generation, and exercise frontends that include this shared header from C and C++ compilation units.
