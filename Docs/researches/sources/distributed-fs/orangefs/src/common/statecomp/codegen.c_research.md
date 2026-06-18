<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/codegen.c -->
# sources/distributed-fs/orangefs/src/common/statecomp/codegen.c

## Purpose
Generates C declarations and state-machine tables from the parsed statecomp abstract syntax tree.

## Important APIs, Types, And Functions
Exports `gen_machine`. Internal generators emit state declarations, unique run-function prototypes, state starts, action fields, transition tables, parallel-jump tables, return-code rows, next-state/return/terminate targets, and state endings. A qhash table de-duplicates run function declarations.

## Control Flow
`gen_machine` checks that states exist, emits forward declarations and the machine object, then for each state emits the action, optional PJMP table entries, transition table entries, and closing syntax. It sets `terminate_path_flag` when return or terminate transitions are generated. After generation it frees tasks, transitions, and states and resets the global state list for the next machine.

## State And Persistence
Uses global parser state `states`, `out_file`, and `terminate_path_flag`; static `runfunc_table` persists across machines to avoid duplicate declarations. Output is written to the generated C file.

## Dependencies And Integration Points
Depends on `statecomp.h`, `quickhash`, `quicklist`, and `pvfs2-internal.h` with malloc redefinition disabled. It is built into the compile-time `statecomp` translator.

## Risks And Test Signals
Risks include leaked `runfunc_table`, generated C syntax differences between Windows and designated-initializer builds, no semantic validation that transition target states exist, and abrupt asserts on allocation failures. Tests should run statecomp on `.sm` files with run/jump/pjmp, duplicate run functions, missing terminate paths, duplicate transition codes, and Windows-compatible output mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/codegen.c -->
