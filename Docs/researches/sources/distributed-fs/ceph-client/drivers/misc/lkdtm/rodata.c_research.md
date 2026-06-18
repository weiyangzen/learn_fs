# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/rodata.c

## Purpose
`rodata.c` supplies a minimal function intended to be placed entirely in `.rodata` by LKDTM build handling so permissions tests can attempt execution from rodata.

## Important APIs, Types, and Functions
The only symbol is `void noinstr lkdtm_rodata_do_nothing(void)`, declared in `lkdtm.h` and consumed by `perms.c`.

## Control Flow
The function returns immediately. Its behavior is intentionally trivial so the relevant signal is whether the memory section is executable, not function logic.

## State and Persistence
No state is used.

## Dependencies and Integration Points
Depends on LKDTM build/linker or objcopy behavior that places this function in rodata. `perms.c` calls `execute_location(dereference_function_descriptor(lkdtm_rodata_do_nothing), CODE_AS_IS)`.

## Risks
If build placement changes, the `EXEC_RODATA` test may validate the wrong memory permission. The `noinstr` annotation reduces instrumentation side effects.

## Test Signals
The key signal is that `EXEC_RODATA` faults when attempting to execute this function from a non-executable rodata mapping.
