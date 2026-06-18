<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/mem_analysis_parser.y -->
## sources/distributed-fs/orangefs/src/apps/devel/mem_analysis_parser.y

**Purpose:** This yacc grammar parses memory allocation trace entries for the mem-analysis development tool.

**Important APIs, types, and functions:** The `%union` carries ints, strings, `struct clause`, and `struct entry *`. Tokens represent trace keywords such as `LINE`, `ADDR`, `REALADDR`, `SIZE`, `RETURNING`, `ALIGN`, `NEWADDR`, `RETURNED`, and operations `MALLOC`, `MEMALIGN`, `REALLOC`, `FREE`. Grammar actions call `init_entry`, `add_entry`, and `process_entry`.

**Control flow:** The grammar accepts a sequence of entries shaped as `FILENAME line op clause_list EOL`, where clauses can appear recursively. Each clause wraps one parsed key/value pair, clause lists chain entries, and `process_entry` is intended to emit or record a completed allocation trace row.

**State and persistence:** In its current source form, the semantic helper functions are empty and return no values despite non-void signatures. As written, parser actions produce undefined behavior and no useful output.

**Dependencies and integration points:** It depends on scanner tokenization from `mem_analysis_scanner.l`, shared structs in `mem_analysis.h`, and yacc/bison generation into `mem_analysis_parser.c/h`.

**Risks and edge cases:** Empty semantic functions are the central correctness risk. Right-recursive `mem_trace`/`clause_list` can consume stack for large inputs. `FILENAME` values point at scanner `yytext`, so durable storage would require copying. Tests should first assert generated code warnings/failures, then validate each operation form once semantic functions are implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/mem_analysis_parser.y -->
