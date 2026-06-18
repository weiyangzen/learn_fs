# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_macro_gram.y

Purpose: secondary Bison parser for macro invocations in the AIC7xxx assembler. It parses a single macro call, validates argument count, and records replacement text for each formal macro argument.

Important APIs and functions: token inputs are `T_SYMBOL` for the macro symbol and `T_ARG` for raw argument text. Grammar nonterminals are `macrocall` and `macro_arglist`. Helpers are `add_macro_arg()`, `mmlex()`, and `mmerror()`, with parser prefix `mm` from the Makefile.

Control flow: the scanner returns a macro symbol followed by `(`, argument tokens, commas, and `)`. The parser stores the macro in `macro_symbol`, accumulates argument count, calls `add_macro_arg()` for each argument position, checks the count against `macro_symbol->info.macroinfo->narg`, clears state, and accepts. `add_macro_arg()` walks the macro's formal argument queue to the requested position and stores duplicated replacement text.

State and persistence: transient `macro_symbol` points at the macro being invoked. Persistent mutation is per-argument `replacement_text` inside the macro symbol's `macroinfo` argument list, consumed by macro expansion code outside this file.

Dependencies and integration: includes assembler globals, symbol definitions, instruction format header, and queue macros. It depends on `aicasm_macro_scan.l` for raw argument tokenization and on macro definitions created by the primary grammar.

Risks: replacement text is stored on the macro symbol itself, so nested or concurrent macro expansion would be unsafe. Argument count errors distinguish too few after parse and too many inside `add_macro_arg()`. Diagnostics use `stop()`, so no parser recovery is attempted.

Test signals: macro calls with zero, one, and multiple arguments; too many/few arguments; arguments containing nested parentheses; invalid non-macro symbol invocation; repeated macro expansion verifying replacement text refresh.
