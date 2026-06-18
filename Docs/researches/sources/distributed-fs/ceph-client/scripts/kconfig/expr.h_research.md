# sources/distributed-fs/ceph-client/scripts/kconfig/expr.h

## Purpose

`expr.h` is the core public data model for kconfig expressions, symbols, properties, and menu nodes. It defines the contracts shared by parser, symbol evaluation, menu finalization, persistence, and frontends.

## Important APIs, Types, and Functions

Key types are `enum tristate`, `enum expr_type`, `union expr_data`, `struct expr`, `struct expr_value`, `struct symbol_value`, `enum symbol_type`, `struct symbol`, `enum prop_type`, `struct property`, `enum menu_type`, `struct menu`, and `struct jump_key`. Important flags include `SYMBOL_CONST`, `SYMBOL_VALID`, `SYMBOL_TRANS`, `SYMBOL_WRITE`, `SYMBOL_WRITTEN`, `SYMBOL_WARNED`, `SYMBOL_DEF_*`, `MENU_CHANGED`, and `MENU_ROOT`. It declares the expression APIs implemented by `expr.c`, global const symbols `symbol_yes`, `symbol_no`, `symbol_mod`, and `modules_sym`.

## Control Flow

This header has no executable control flow beyond `expr_is_yes()` and tristate macros. Its structures drive runtime flow elsewhere: parser creates `struct menu`/`struct property`, symbol code computes `struct symbol.curr`, expression code evaluates `struct expr`, and UI code traverses menu nodes.

## State and Persistence Behavior

The header defines in-memory state layout. `struct symbol` stores current calculated value, external/default values, visibility, menu instances, reverse dependencies, and flags used by reads/writes. `struct menu` stores tree structure, prompt, inherited dependencies, visibility clauses, help text, source location, and frontend scratch data. Persistence is performed by `confdata.c`, but it relies on these fields being stable.

## Dependencies and Integration Points

It includes list and C/C++ compatibility headers and is included by nearly all kconfig sources. The structures are tightly coupled with `parser.y`, `symbol.c`, `menu.c`, `confdata.c`, `expr.c`, `mconf.c`, and `gconf.c`.

## Risks and Edge Cases

This is a central ABI within the tool; changing enum values, flag bits, or struct fields has broad blast radius. Choices are represented as symbols with `name == NULL`, so null-name handling is required throughout. `union expr_data` stores const-typed views plus `_initdata` for interning; unsafe mutation can break hash identity.

## Test Signals

Compile coverage across all kconfig frontends is the first signal. Behavioral signals include choices, multi-definition symbols, `select`/`imply`, visibility inheritance, transitional symbols, and config write/read round trips that exercise the flags declared here.
