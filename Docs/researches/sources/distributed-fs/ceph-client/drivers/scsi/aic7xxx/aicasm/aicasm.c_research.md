# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm.c

Purpose: main program for the AIC7xxx sequencer assembler. It parses command-line options, opens outputs, drives the lexer/parser, tracks generated instructions, conditional patch metadata, critical sections, include paths, and emits generated C/register/listing files.

Important APIs/types/functions: defines `patch_t`, global output/search/scope/program state, and functions `main()`, `usage()`, `back_patch()`, `output_code()`, `dump_scope()`, `emit_patch()`, `output_listing()`, `check_patch()`, `stop()`, `seq_alloc()`, `cs_alloc()`, `scope_alloc()`, and `process_scope()`. Externally visible helpers are declared in `aicasm.h`.

Control flow: `main()` initializes queues/stacks, creates root scope, parses options (`-I`, `-o`, `-r`, `-p`, `-i`, `-l`, debug), opens the symbol table, includes the source file, and runs `yyparse()`. On success it validates scope closure, processes/dumps scopes to build patch entries, backpatches forward branches, emits code/register/listing outputs as requested, and exits through `stop()`. `output_code()` writes `seqprog[]`, patch function wrappers for conditionals, patch table, and critical-section table. `output_listing()` optionally asks for conditional values and prints source with generated instruction bytes after patch filtering.

State and persistence: in-memory state includes `seq_program`, `patches`, `cs_tailq`, `scope_stack`, `patch_functions`, include search paths, mode globals, and output file handles. Persistent outputs are generated C code, register dumps, diagnostic functions, and listings. On error, `stop()` closes and unlinks partially generated output files.

Dependencies and integration: depends on parsers/scanners generated from `aicasm_gram.y` and scanner files, symbol-table functions in `aicasm_symbol.c`, instruction formats from `aicasm_insformat.h`, BSD queue macros, regex and DB support indirectly, and host stdio/unistd.

Risks: listing generation can block for interactive conditional answers. Include-path list insertion is head-first, which affects search order. Error cleanup relies on global filename/file pointers. Patch skip math in `process_scope()` is subtle and directly controls runtime firmware patching.

Test signals: assemble known `.seq` files, compare generated `seqprog[]` and patch tables to shipped outputs, test forward labels and nested if/else scopes, exercise partial-output cleanup on parse errors, generate listings non-interactively, and run with/without optional outputs.
