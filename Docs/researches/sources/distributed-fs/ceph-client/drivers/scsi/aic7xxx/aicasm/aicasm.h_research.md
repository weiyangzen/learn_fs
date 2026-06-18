# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm.h

Purpose: shared interface for the `aicasm` assembler program, parser, scanner, macro expander, and symbol code. It exposes global assembly state and allocator/processing functions used across generated and handwritten components.

Important APIs and types: defines `path_entry_t`, `include_type` (`QUOTED_INCLUDE`, `BRACKETED_INCLUDE`, `SOURCE_FILE`), `SLIST_HEAD(path_list, path_entry)`, and extern globals `search_path`, `cs_tailq`, `scope_stack`, `patch_functions`, `includes_search_curdir`, `appname`, `stock_include_file`, `yylineno`, `yyfilename`, `prefix`, `patch_arg_list`, `versions`, `src_mode`, and `dst_mode`. Declared functions include `stop()`, `include_file()`, `expand_macro()`, `seq_alloc()`, `cs_alloc()`, `scope_alloc()`, and `process_scope()`.

Control flow role: generated parsers call these declarations to allocate instructions, scopes, and critical sections; scanners call `include_file()` and macro expansion paths; all components use `stop()` for fatal diagnostics and cleanup. The include type enum lets scanner/parser code distinguish quote includes, bracket includes, and top-level source inclusion.

State and persistence: only declares state. The actual state is owned mostly by `aicasm.c` and parser/scanner modules. Persistent behavior is indirect through output files managed by the main program.

Dependencies and integration: includes local BSD-style `queue.h` and forward-declares `struct symbol` so it can reference symbol APIs without forcing full symbol definitions. It is included by `aicasm.c`, grammars, scanners, and symbol/macro code.

Risks: broad extern global state couples all assembler modules and makes reentrancy impossible. Parser-generated code and handwritten code must agree on global names such as `src_mode`/`dst_mode` and `yyfilename`. `stop()` is noreturn; callers depend on it for control-flow termination after errors.

Test signals: full host build after parser/scanner generation, warnings for missing prototypes or mismatched globals, assemble sources with includes/macros/conditionals, and failure-path tests confirming `stop()` cleanup.
