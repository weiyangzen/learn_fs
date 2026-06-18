# sources/distributed-fs/openafs/src/comerr/error_table_nt.h

Purpose: checked-in generated parser header for NT builds of the error table compiler.

Important APIs: defines `YYSTYPE` with `char *dynstr`, token values for `ERROR_TABLE`, `ERROR_CODE_ENTRY`, `END`, `STRING`, and `QUOTED_STRING`, and declares external `yylval`.

Control flow and integration: no executable logic. It is consumed by NT lexer/parser build paths so lexer tokens match the generated parser.

Risks and tests: must stay synchronized with `error_table_nt.c` and `error_table.y` token definitions. Build failures in NT compile_et paths are the main detection mechanism.
