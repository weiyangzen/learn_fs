# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_scan.l

Purpose: flex lexer for the host-side aic7xxx/aic79xx sequencer assembler. It tokenizes register definition files, sequencer assembly, C-style conditional expressions, include directives, string literals, and assembler-local `#define` macros before handing tokens to `aicasm_gram.y`.

Important APIs/types/functions: scanner start conditions include `COMMENT`, `CEXPR`, `INCLUDE`, `STRING`, `MACRODEF`, `MACROARGLIST`, `MACROCALLARGS`, and `MACROBODY`. `include_file()` opens source or include files, pushes scanner buffers on an `SLIST` include stack, and resets `yylineno`/`yyfilename`. `expand_macro()` expands macro bodies by `unput()`ing replacement text backwards. `next_substitution()` uses compiled regexes from macro arguments to locate argument substitutions. `yywrap()` unwinds include buffers and closes input files.

Control flow: top-level rules discard comments and whitespace, return parser tokens for assembler keywords/opcodes/register-definition keywords, parse octal/decimal/hex numbers, capture strings, and create or look up symbols through `symtable_get()`. Include rules switch into include parsing until `>` or the closing quote. Macro definitions capture either simple or argument macros; macro invocations temporarily run the macro-argument parser, then expand the stored macro body back into the scanner input stream.

State and persistence: scanner state is process-local: `string_buf`, `parren_count`, `quote_count`, include-stack entries, current file name, and flex buffers. No persistent state is written directly; it populates parser values and symbol-table references used by later generated outputs.

Dependencies and integration: depends on flex, the generated grammar header, `aicasm_symbol` symbol table, `queue.h` list macros, `search_path`, `includes_search_curdir`, and fatal `stop()` handling from `aicasm.c`.

Risks and test signals: fixed `MAX_STR_CONST` and unchecked `string_buf_ptr++` writes can overflow on very long strings, macro bodies, or expressions. Macro expansion depends on reverse `unput()` ordering and regex substitutions, so nested/argument macros are high-risk. Include behavior should be tested for quoted versus bracket includes, missing files, nested includes, comments, escaped macro newlines, numeric formats, and invalid-character diagnostics.
