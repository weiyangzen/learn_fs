# sources/distributed-fs/ceph-client/scripts/dtc/srcpos.h

Purpose: Declares dtc source file and source position structures plus parser-location helpers.

Important APIs/types: `struct srcfile_state` stores `FILE *`, full name, directory, line/column, and previous include frame. `struct srcpos` stores first/last line and column, source file pointer, and optional chained positions. `YYLTYPE` aliases `struct srcpos`. `YYLLOC_DEFAULT` merges parser rule locations. The header exports source-file stack, include search, source position formatting, error reporting, and line reset functions.

Control flow: Generated Bison parser uses `YYLLOC_DEFAULT` to form a current location from child rule locations, setting `next` to `NULL`. Lexer/parser code calls exported functions implemented in `srcpos.c`.

State/persistence: Exposes global `depfile` and `current_srcfile`, so parser and lexer code directly share source state. `srcpos` objects may reference copied or leaked `srcfile_state` records.

Dependencies/integration: Includes `util.h` for attributes and allocation/error helpers. Integrated with dtc parser grammar, lexer, and tree annotation output.

Risks: The public globals make state coupling implicit. The `YYLLOC_DEFAULT` macro sets `file` from the last RHS symbol for non-empty rules, which can matter for mixed include-origin constructs. Header users must free strings returned by formatting functions.

Test signals: Parser location tests should verify empty and non-empty grammar rule locations, chained positions, and correct file attribution across includes.
