<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/statecomp.c -->
# sources/distributed-fs/orangefs/src/common/statecomp/statecomp.c

## Purpose
Provides the `statecomp` executable entry point, argument handling, output-file setup, parser invocation, final validation, diagnostics, and AST construction helpers.

## Important APIs, Types, And Functions
Defines globals `states`, `terminate_path_flag`, `line`, `out_file`, and `in_file_name`. Implements `main`, `parse_args`, `finalize`, `yyerror`, `emalloc`, `estrdup`, `new_state`, `new_transition`, and `new_task`.

## Control Flow
`main` parses arguments, opens input and output, writes a generated-file banner, calls `yyparse`, reports parser return class, and finalizes. Argument parsing requires an `.sm` input and optional output; absent output changes the extension to `.c`. Finalize deletes the output and exits if no generated transition set `terminate_path_flag`. AST helpers append unique states and unique transition return codes, while PJMP tasks are appended in order.

## State And Persistence
State is process-global while compiling one input file. Persistent output is the generated C file; error paths unlink it. Memory is mostly freed by `gen_machine` after each machine.

## Dependencies And Integration Points
Depends on `statecomp.h`, generated parser/scanner functions, standard I/O, Unix `unlink` or Windows `_unlink`, and `pvfs2-internal.h` with malloc redefinition disabled.

## Risks And Test Signals
Risks include process exit from helper functions, only extension-based input validation, output deletion on errors, and target-state validation deferred or absent. Tests should cover default output naming, explicit output naming, non-`.sm` rejection, syntax errors unlinking output, no-terminate validation, duplicate states/transitions, and multi-machine files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/statecomp.c -->
