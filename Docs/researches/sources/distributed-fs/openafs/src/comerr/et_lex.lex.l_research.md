# sources/distributed-fs/openafs/src/comerr/et_lex.lex.l

Purpose: lex scanner for `.et` error table files.

Important tokens: recognizes `error_table`/`et`, `error_code`/`ec`, `end`, quoted strings, alphanumeric/underscore strings, comments starting with `#`, whitespace, and single-character punctuation such as comma and equals.

Control flow and state: quoted strings are duplicated without surrounding quotes into `yylval.dynstr`; identifiers are duplicated as `STRING`; comments and whitespace are skipped; unknown single characters are returned literally. `yywrap` returns 1 to signal end of input.

Dependencies and integration: generated into `et_lex.lex.c` by the comerr Makefile and included by `error_table.y` output or NT parser variants. It depends on yacc token definitions and `yylval`.

Risks and tests: quoted strings do not support escapes and the identifier rule `{AN}*` can match empty input in some lex implementations, though surrounding rules usually consume progress. Build-time parsing of `.et` files is the main test signal.
