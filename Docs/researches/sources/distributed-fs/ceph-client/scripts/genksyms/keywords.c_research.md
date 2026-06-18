# sources/distributed-fs/ceph-client/scripts/genksyms/keywords.c

## Purpose
Maps C, GNU C, kernel, and architecture-specific reserved words to genksyms parser tokens.

## APIs, Control Flow, and State
The file defines a static `keywords[]` table and `is_reserved_word(str, len)`. The function linearly scans the table, compares length and bytes, and returns the parser token or `-1`. Covered tokens include asm/attribute/typeof forms, qualifiers, integer builtins, C storage/type keywords, `_Static_assert`, x86 segment qualifiers, and the internal `__GENKSYMS_EXPORT_SYMBOL` marker.

## Dependencies and Integration
It is textually included by `lex.l`, so it relies on token macros from `parse.tab.h` already being visible. It stores no mutable state.

## Risks and Test Signals
Risks are missing newly introduced compiler keywords or mapping a common identifier as a keyword, which changes ABI CRC parsing. Test signals are lexer/parser tests with modern compiler output and stable genksyms CRCs across kernel headers using new C syntax.
