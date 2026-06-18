# sources/distributed-fs/openafs/src/comerr/error_table_nt.c

Purpose: checked-in Bison-generated C parser for Windows/NT builds of the `.et` grammar, including copied semantic actions from `error_table.y`.

Important APIs and state: defines token constants, `YYSTYPE`, parser tables, `yyparse`, and the same helper functions as the grammar source: `add_ec`, `add_ec_val`, `put_ecs`, `set_table_num`, `set_table_fun`, `set_table_1num`, `char_to_num`, and `char_to_1num`. It includes `et_lex.lex_nt.c` on NT or `et_lex.lex.c` otherwise.

Control flow: Bison table-driven parser shifts/reduces `.et` syntax into semantic actions that compute table bases and write generated output. Error recovery is the old Bison skeleton behavior.

Persistence and integration: exists to avoid requiring yacc/Bison on some NT build paths. It shares globals and output-file contracts with `compile_et.c`.

Risks and tests: generated code is large, old, non-reentrant, and can drift from `error_table.y` if regenerated inconsistently. Manual edits should target the grammar instead. Build coverage on Windows is the primary signal.
