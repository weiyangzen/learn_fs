# sources/distributed-fs/ceph-client/scripts/genksyms/lex.l

## Purpose
Provides genksyms lexical analysis, converting preprocessed C into parser tokens and token-list fragments suitable for ABI hashing.

## APIs, Control Flow, and State
Flex rule `yylex1()` performs primitive tokenization for identifiers, numbers, strings, chars, preprocessor line markers, operators, and whitespace. The exported `yylex()` is a second-stage state machine. It tracks source file and line markers, populates `cur_filename`, `cur_line`, and `in_source_file`, appends tokens into `struct string_list` nodes, and returns higher-level phrase tokens for attributes, asm blocks, `typeof`, bracket/brace bodies, expressions, and static assertions. It consults `is_reserved_word()` and `find_symbol()` to distinguish typedef names from identifiers, using `dont_want_type_specifier` and internal suppression counters to resolve grammar context.

## Dependencies and Integration
It depends on flex, `genksyms.h`, generated `parse.tab.h`, and textual inclusion of `keywords.c`. The parser consumes token-list splice points via `yylval`.

## Risks and Test Signals
Risks include mis-nesting phrase states, incorrect source-file ownership for included declarations, typedef ambiguity, and token accumulation leaks on parse errors. Test signals are successful parsing of complex preprocessed headers, correct error locations, and unchanged CRC output for declarations with attributes, anonymous structs, arrays, and initializers.
