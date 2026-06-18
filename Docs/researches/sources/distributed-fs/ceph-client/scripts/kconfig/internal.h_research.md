# sources/distributed-fs/ceph-client/scripts/kconfig/internal.h

## Purpose

`internal.h` declares non-public shared state for the kconfig implementation: symbol and expression hash tables, iteration helpers, expression cache invalidation, current parser/menu pointers, and current source location.

## Important APIs, Types, and Functions

Key definitions are `SYMBOL_HASHSIZE`, `EXPR_HASHSIZE`, `HASHTABLE_DECLARE(sym_hashtable, ...)`, `HASHTABLE_DECLARE(expr_hashtable, ...)`, `for_all_symbols(sym)`, `expr_invalidate_all()`, `current_menu`, `current_entry`, `cur_filename`, and `cur_lineno`.

## Control Flow

No runtime flow is implemented. The header enables global traversal and coordination between parser, menu construction, expression interning, symbol evaluation, and config persistence.

## State and Persistence Behavior

It declares process-global in-memory state only. The hash tables are the authoritative registries for symbols and expressions; parser globals identify where new menu entries/properties are being attached.

## Dependencies and Integration Points

It includes `hashtable.h` and is used by `confdata.c`, `expr.c`, `menu.c`, symbol code, and parser/lexer components that need implementation internals not exposed through `lkc.h`.

## Risks and Edge Cases

The globals make kconfig effectively single-context and not thread-safe. Changing hash sizes or traversal macro semantics affects all symbols/expressions. Parser location globals must be kept accurate by the lexer or diagnostics and property locations become misleading.

## Test Signals

Compile all kconfig tools and run parser tests involving nested includes, warnings, symbol traversal, and expression cache invalidation.
