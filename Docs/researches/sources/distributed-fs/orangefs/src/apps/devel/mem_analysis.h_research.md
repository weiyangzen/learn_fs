<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/mem_analysis.h -->
## sources/distributed-fs/orangefs/src/apps/devel/mem_analysis.h

**Purpose:** `mem_analysis.h` shares scanner/parser/driver declarations and data structures for the memory analysis tool.

**Important APIs, types, and functions:** It declares `yyerror(char *s)`, defines `PVFS_MALLOC_REDEF_OVERRIDE` to avoid OrangeFS malloc macro replacement, defines `struct clause` with token type/value, defines `struct entry` with allocation-operation fields, and declares global `line` and `col`.

**Control flow:** The header has no control flow, but its structs are meant to be filled by grammar actions and scanner tokens.

**State and persistence:** It exposes parser position globals and output-error behavior indirectly. No persistent state is created by the header itself.

**Dependencies and integration points:** It is included by `mem_analysis.c`, `mem_analysis_parser.y`, and `mem_analysis_scanner.l`. The malloc override is important because the analysis tool itself must not be instrumented by the allocation wrappers it may analyze.

**Risks and edge cases:** There are no include guards, so repeated inclusion relies on build context. `struct entry` fields are plain `int`, which may truncate pointer-sized addresses from traces on 64-bit systems. Tests should ensure generated scanner/parser compile with this header and that pointer/address values in traces are representable or intentionally truncated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/mem_analysis.h -->
