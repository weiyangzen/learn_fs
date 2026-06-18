<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/parser.y -->
# sources/distributed-fs/orangefs/src/common/statecomp/parser.y

## Purpose
Defines the yacc/bison grammar for statecomp's `.sm` machine-description language.

## Important APIs, Types, And Functions
Tokens include `machine`, `nested`, `state`, `run`, `pjmp`, `jump`, `return`, `terminate`, `success`, `default`, braces, semicolons, arrows, and identifiers. Grammar actions call `new_state`, `new_transition`, `new_task`, and `gen_machine`.

## Control Flow
The parser accepts one or more machines. Each machine contains state definitions. Each state has one action (`run`, `jump`, or `pjmp`) plus transitions. `success` becomes return code `0`, `default` becomes `-1`, and identifiers are copied with `estrdup`. PJMP actions collect task return-code-to-machine mappings before normal transitions.

## State And Persistence
Parser actions mutate static current pointers and the global state list declared in `statecomp.h`. Generated C output is produced when a complete machine is reduced.

## Dependencies And Integration Points
Depends on scanner tokens from `scanner.l`, allocation and AST helpers from `statecomp.c`, and code generation in `codegen.c`.

## Risks And Test Signals
Risks include no declared precedence needs but limited syntax diagnostics, no semantic target-state validation, and memory ownership split between parser strings and codegen cleanup. Tests should parse valid multi-machine files, nested machines, PJMP task lists, default/success transitions, duplicate states/transitions, and malformed syntax with correct line numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/parser.y -->
