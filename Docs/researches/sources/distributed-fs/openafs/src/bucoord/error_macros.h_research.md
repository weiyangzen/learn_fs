# sources/distributed-fs/openafs/src/bucoord/error_macros.h

## Purpose
Defines local structured-error macros for backup coordinator C files. The macros set a function-local `code` variable and jump to a conventional cleanup label.

## Important APIs, Types, And Functions
`ERROR(evalue)` assigns `code = evalue` and jumps to `error_exit`. `ABORT(evalue)` assigns `code = evalue` and jumps to `abort_exit`. Both undefine previous definitions before redefining.

## Control Flow
Files that include this header must declare a compatible `code` variable and provide the corresponding label. The macros centralize early-exit cleanup in functions with many allocation, lock, RPC, or file failure points.

## State And Persistence
The header stores no state. It influences cleanup behavior in callers and therefore affects lock release, stream cleanup, allocated-memory release, and RPC connection teardown.

## Dependencies And Integration Points
It is included by the command, dump schedule, volume set, tape host, dump, restore, and BUDB interface modules. It depends only on C `goto` label conventions.

## Risks And Test Signals
The macro contract is implicit: missing `code`, `error_exit`, or `abort_exit` labels cause compile failures, while using the macro in a scope where `code` has a different type can produce subtle behavior. Early direct `return`s in files using these macros are a risk because they bypass the intended cleanup labels. Compile coverage and fault-injection paths that verify locks/connections are released are the main test signals.
