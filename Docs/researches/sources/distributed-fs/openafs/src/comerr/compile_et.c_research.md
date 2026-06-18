# sources/distributed-fs/openafs/src/comerr/compile_et.c

Purpose: command-line compiler for `.et` error table definitions. It generates C source, header, or message catalog output consumed by OpenAFS builds.

Important APIs and state: `main` parses flags (`-debug`, `-language`, `-h`, `-p`, `-v`, `-emit`), derives input/output paths, opens `yyin`, optionally includes a `.p.h` prolog into the header, writes C/MSF prologs, calls `yyparse`, and emits trailer definitions such as `initialize_<table>_error_table`, `ERROR_TABLE_BASE_*`, and compatibility macros. Globals include `hfile`, `cfile`, `msfile`, `table_name`, `version`, `use_msf`, and emit flags. `xmalloc` exits on allocation failure; `yyerror` reports line and token context.

Control flow and persistence: generated files are written in the current working directory; input is resolved as `prefix/filename(.et)`. Parser actions in `error_table.y` write error strings and macro definitions as the grammar is reduced.

Dependencies and integration: depends on yacc/lex globals, `compiler.h`, `internal.h`, roken, opr, and generated component version source. It is invoked by Makefiles such as `src/cmd/Makefile.in`.

Risks and tests: argument parsing is manual and exits on many errors. It writes output files directly rather than atomically. Table names are truncated by parser code for compatibility, which can surprise callers. Test signal comes from generated headers/sources in normal builds.
