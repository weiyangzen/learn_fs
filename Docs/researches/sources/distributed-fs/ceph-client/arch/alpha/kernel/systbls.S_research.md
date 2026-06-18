# sources/distributed-fs/ceph-client/arch/alpha/kernel/systbls.S

## Purpose
Defines the Alpha kernel system call dispatch table as assembly data generated from `asm/syscall_table.h`. The source was read as part of `subset-b-000628` and contains 15 lines.

## Important APIs, Types, and Functions
Exports global `sys_call_table`. Defines `__SYSCALL(nr, entry)` as a `.quad entry` expansion before including the generated syscall table header.

## Control Flow
At assembly time, `asm/unistd.h` and generated `asm/syscall_table.h` are included. Each generated `__SYSCALL` line emits one 64-bit function pointer into the aligned `.data` table. The low-level syscall entry path indexes this table by syscall number.

## State and Persistence Behavior
The table is static kernel data in the final image. Its contents persist for the running kernel and are derived from generated headers, not modified by this file at runtime.

## Dependencies
Depends on the syscall header generation Makefile, `syscall.tbl`, low-level syscall entry code, and all syscall implementation symbols referenced by the generated table.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Any mismatch between syscall numbers, table order, and entry code ABI is catastrophic. Missing generated headers or missing syscall symbols fail the build; wrong entries misdispatch user syscalls.

## Test Signals
Build `arch/alpha/kernel/systbls.o`, inspect generated `syscall_table.h`, boot userspace smoke tests for basic syscalls, and compare `__NR_*` values with table indexes.
