<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/statecomp.h -->
# sources/distributed-fs/orangefs/src/common/statecomp/statecomp.h

## Purpose
Defines the statecomp AST structures, transition/action enums, global parser/codegen variables, and helper prototypes.

## Important APIs, Types, And Functions
Defines `enum transition_type`, `enum state_action`, `struct task`, `struct transition`, and `struct state`. Declares globals `states`, `terminate_path_flag`, `line`, `out_file`, and `in_file_name`, plus `yyerror`, `emalloc`, `estrdup`, `new_state`, `new_transition`, `new_task`, and `gen_machine`.

## Control Flow
Parser actions allocate and link these AST objects; code generation consumes and frees them machine by machine.

## State And Persistence
The header exposes mutable global state for the translator process. No runtime OrangeFS server state is involved.

## Dependencies And Integration Points
Requires `FILE` to be visible through including translation units. Used by `statecomp.c`, `parser.y`, `scanner.l`, and `codegen.c`.

## Risks And Test Signals
Risks include broad global coupling and lack of namespace isolation. Compile tests across generated parser/scanner/codegen units and parser behavior tests validate the structure contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/statecomp.h -->
