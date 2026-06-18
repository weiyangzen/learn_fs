# sources/distributed-fs/ceph-client/tools/include/nolibc/stackprotector.h

## Purpose
Supplies stack protector support when nolibc is built with compiler stack canaries enabled.

## APIs, Types, and Functions
Defines weak `__stack_chk_fail`, `__stack_chk_fail_local`, weak global `__stack_chk_guard`, and `__stack_chk_init()` when stack protector mode is detected; otherwise `__stack_chk_init()` is an empty stub.

## Control Flow, State, and Persistence
Startup code calls `__stack_chk_init()` before `main`. Failure handlers terminate through nolibc abort/exit paths. Persistent state is the canary guard value, usually initialized from auxiliary-vector randomness when available or a fallback value.

## Dependencies and Integration
Depends on compiler stack-protector macros, `compiler.h` attributes, startup ordering in `crt.h`, and syscall/stdlib termination helpers. It integrates with all nolibc code compiled under stack protector flags.

## Risks and Test Signals
Risks are initializing the guard too late, weak symbol collisions, predictable fallback canaries, and architecture startup code accidentally protected before the guard exists. Test signals are stack-protector-enabled builds, deliberate canary corruption tests, auxv randomness presence/absence, and static checks that `_start` paths are `no_stack_protector`.
