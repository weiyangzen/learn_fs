<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/mem_analysis_scanner.l -->
## sources/distributed-fs/orangefs/src/apps/devel/mem_analysis_scanner.l

**Purpose:** This flex scanner tokenizes memory allocation trace input for `mem_analysis_parser.y`, entering the parseable code region after a sentinel line.

**Important APIs, types, and functions:** It includes `mem_analysis.h` and generated `mem_analysis_parser.h`. It defines token-return macros updating global `col`, regexes for hex hints, decimal ints, filenames under `src` or `include`, and `(nil)`. Start conditions `CODE` and `COMMENT` separate ignored preamble, parseable trace, and C comments. `yywrap()` returns 1 at EOF.

**Control flow:** Before seeing `init_glibc_malloc:running\n`, the scanner consumes all text while tracking line/column. In `CODE`, it returns keyword tokens, values, filenames, and EOL. It skips whitespace, consumes C comments, maps `(nil)` to zero, and calls `yyerror` for any unexpected character.

**State and persistence:** It mutates global `line` and `col` and returns `yytext` pointers for filenames. It does not write output itself.

**Dependencies and integration points:** It depends on flex behavior, parser token definitions, and the driver’s `yyerror`. Several flex options/macros are set to avoid interactive handling, unused stack support, generated `main`, and unistd conflicts.

**Risks and edge cases:** The filename regex is restrictive and excludes many valid paths. Returning `yytext` without duplication is unsafe if parser actions store it. Decimal regex allows repeated signs like `--1`, which `strtol` will not parse as intended. Tests should cover preamble skipping, comments, each token type, nil hints, bad characters, Windows/flex-version builds, and filenames outside the accepted pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/mem_analysis_scanner.l -->
