# sources/distributed-fs/ceph-client/scripts/genksyms/genksyms.h

## Purpose
Defines shared types and interfaces for the genksyms lexer, parser, and C implementation.

## APIs, Control Flow, and State
The header defines symbol namespaces (`SYM_NORMAL`, `SYM_TYPEDEF`, `SYM_ENUM`, `SYM_STRUCT`, `SYM_UNION`, `SYM_ENUM_CONST`), symbol change statuses, `struct string_list` token nodes, and `struct symbol` entries carrying hash linkage, definition token lists, expansion/visited links, declaration flags, and override metadata. It sets bison `YYSTYPE` to `struct string_list **`, exposing parser semantic values as mutable list splice points. It declares scanner/parser entry points, global source-position state, symbol-table operations, export handling, list memory helpers, and `dont_want_type_specifier`.

## Dependencies and Integration
It depends on `list_types.h` for `hlist_node` and standard C headers. It is the contract joining `genksyms.c`, `lex.l`, `parse.y`, and `keywords.c`.

## Risks and Test Signals
The pointer-to-pointer parser value convention is compact but fragile: lexer and grammar actions must agree on list ownership. Test signals are clean parser generation, valgrind or sanitizer runs for list ownership changes, and unchanged modversion CRCs after parser refactors.
