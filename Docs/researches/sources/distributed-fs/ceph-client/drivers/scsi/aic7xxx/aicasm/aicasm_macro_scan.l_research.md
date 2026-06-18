# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_macro_scan.l

Purpose: flex scanner for the macro-invocation sub-parser. It tokenizes macro call text, preserving raw argument strings while respecting nested parentheses.

Important APIs and state: defines `MAX_STR_CONST`, `string_buf`, `string_buf_ptr`, `parren_count`, `buf`, and `mmlineno`. Lexical state `ARGLIST` handles tokens inside macro parentheses. It returns `T_SYMBOL`, `T_ARG`, punctuation tokens, and reports fatal errors through `stop()`. `mmwrap()` treats EOF in a macro call as an error.

Control flow: initial state recognizes `WORD(`, looks up the symbol, verifies it is a `MACRO`, pushes back `(`, resets parenthesis count, enters `ARGLIST`, and returns `T_SYMBOL`. In `ARGLIST`, whitespace is skipped, the first `(` starts argument collection, nested parentheses are copied into the current argument, `)` either returns a pending `T_ARG` by pushing the paren back or closes the call, comma similarly returns pending argument text or the comma token, and `MCARG` appends raw non-delimiter text to `string_buf`.

State and persistence: scanner state is transient per macro call. It writes argument text into a fixed buffer and exposes it via `mmlval.str`; persistence happens later when the parser duplicates the text into macro metadata.

Dependencies and integration: includes `aicasm.h`, `aicasm_symbol.h`, generated `aicasm_macro_gram.h`, queue macros, and C regex/stdio headers. It is generated with the `mm` prefix so it can coexist with the primary scanner/parser.

Risks: fixed `MAX_STR_CONST` and no explicit bounds checks while appending argument text can overflow on very long macro arguments. The argument token pattern excludes spaces and delimiters, so formatting-sensitive macro arguments may not survive. EOF is fatal by design. Replacement parsing is not reentrant.

Test signals: macro invocations with nested parentheses, empty argument list, comma handling, invalid characters, non-macro symbols, EOF/truncated call, and long argument fuzzing to expose buffer limits.
