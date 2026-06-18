# sources/distributed-fs/openafs/src/comerr/et_lex.lex_nt.c

Purpose: checked-in flex 2.5 scanner output for the OpenAFS `compile_et` error-table grammar on NT/Windows-oriented builds. It tokenizes `.et` input for the yacc parser, preserving an old generated C scanner so Windows builds do not need to regenerate it.

Important APIs/types/functions: exports `yylex`, `yyrestart`, `yy_switch_to_buffer`, buffer helpers such as `yy_create_buffer`, `yy_delete_buffer`, `yy_scan_string`, and `yy_scan_bytes`, the globals `yyin`, `yyout`, `yytext`, `yyleng`, and `yylineno`, and a local `yywrap` returning EOF. The semantic actions return parser tokens `ERROR_TABLE`, `ERROR_CODE_ENTRY`, `END`, `QUOTED_STRING`, `STRING`, or a literal character, and store copied strings in `yylval.dynstr`.

Control flow: `yylex` initializes the current input buffer, drives the generated DFA tables, updates line numbers on matched newlines, and dispatches eleven rule actions originally from `et_lex.lex.l`. Keyword spellings for error-table declarations return grammar tokens; whitespace and comments are skipped; quoted strings are duplicated after stripping the closing quote; ordinary identifiers are duplicated as `STRING`; punctuation is returned as its character value; unmatched text is echoed by the flex default action. End of input runs the generated end-of-buffer path and terminates through `yywrap`.

State and persistence: scanner state is entirely process-local: current buffer, start state, line number, hold character, `yytext`, and allocated scan buffers. It persists no disk or registry state, but string tokens allocated with `strdup` become parser-owned memory and generated buffers must be released by callers when alternate scan APIs are used.

Dependencies and integration: integrates with the comerr yacc parser through token constants and `yylval`, and with `compile_et` grammar support through standard flex globals. It depends on libc stdio/stdlib/string handling and the parser headers that define tokens and semantic value layout.

Risks and test signals: because this is old generated scanner code, the main risks are drift from the source `.l` file, non-reentrant global state, fixed `YYLMAX` token length, unescaped quoted-string handling, and unchecked `strdup` allocation. Useful tests are regenerating error tables from `.et` files, quoted and unquoted token cases, malformed punctuation, comments/whitespace, long tokens, and a Windows build that uses this checked-in scanner.
