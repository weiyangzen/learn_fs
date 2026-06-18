# sources/distributed-fs/ceph-client/scripts/genksyms/parse.y

## Purpose
Defines the genksyms grammar for ABI-relevant C global declarations and export markers.

## APIs, Control Flow, and State
The bison grammar tracks `is_typedef`, `is_extern`, `current_name`, and reusable `decl_spec`. Helper actions remove or splice `struct string_list` nodes, and `record_compound()` records struct/union/enum definitions unless the tag originates from the primary source file, where a tagged reference is kept instead. Grammar rules handle simple declarations, typedefs, function definitions, storage classes, type specifiers, qualifiers, declarators, nested declarators, parameter lists, class bodies, enum bodies, asm definitions, static assertions, and `EXPORT_SYMBOL` markers. On export markers, it calls `export_symbol()`.

## Dependencies and Integration
It depends on tokenization from `lex.l`, symbol and list APIs from `genksyms.c`, and bison-generated parser code. It is integrated into the kbuild modversion path.

## Risks and Test Signals
The grammar intentionally ignores many expression and initializer details while preserving ABI-affecting declaration shape. Risks include rejecting new C syntax, mishandling typedef-vs-identifier context, or over-recording included compound definitions. Test signals include parser generation with no unexpected conflicts, module export CRC stability, and regression cases for enums, bitfields, attributes, function pointers, and static assertions.
