# sources/distributed-fs/openafs/src/comerr/error_table.y

Purpose: yacc grammar and semantic actions for parsing `.et` error table files.

Important APIs and state: grammar accepts `error_table`/`et`, optional table function, table id, one or more `error_code`/`ec` entries, and `end`. Semantic helpers include `add_ec`, `add_ec_val`, `put_ecs`, `set_table_num`, `set_table_fun`, `set_table_1num`, `char_to_num`, and `char_to_1num`. Globals include `table_number`, `current`, `error_codes`, and external output files.

Control flow: parser computes the table base from encoded table name and optional function, writes string entries to C or MSF output as entries are parsed, fills gaps with `NULL` for explicit numeric values, records symbolic names, then writes header `#define`s for each error code.

Persistence and integration: output is streamed into files opened by `compile_et.c`. The lexer is included at the end as generated `et_lex.lex.c` or NT variant. Generated tables later register with `afs_add_to_error_table`.

Risks and tests: parser uses process globals and exits on invalid table names. `add_ec_val` only prints when codes are out of order and returns, which may allow generation to continue in a degraded state. Table-name truncation is intentional legacy behavior but can collide. Build generation is the main test signal.
