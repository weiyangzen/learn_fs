<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/traps.c

## Purpose
Handles OpenRISC traps and diagnostics: register/stack dumps, fatal kernel exceptions, user signals for fault classes, FPU exception decoding, and emulation of `lwa`/`swa` atomic instructions.

## Important APIs, Types, And Functions
Defines `lwa_flag` and `lwa_addr`; functions include `show_stack()`, `show_registers()`, `die()`, `unhandled_exception()`, `do_fpe_trap()`, `do_trap()`, `do_unaligned_access()`, `do_bus_fault()`, `do_illegal_instruction()`, and helpers for delay-slot PC adjustment and `lwa`/`swa` simulation.

## Control Flow
C exception handlers either force user signals or call `die()` in kernel mode. Illegal instruction handling recognizes `INSN_LWA` and `INSN_SWA`, simulates load/store conditional behavior using usercopy or exception table fixups, adjusts PC for delay slots, and sets SR flag on successful `swa`.

## State And Persistence
Maintains global `lwa_flag`/`lwa_addr` across emulated atomic instruction pairs. Reads and mutates live `pt_regs`, FPU status, and user memory.

## Dependencies And Integration Points
Called from `entry.S` exception stubs. Depends on FPU save/restore, exception tables, usercopy, unwinder, kallsyms, and OpenRISC instruction encodings.

## Risks
`lwa_flag` is global, not per-task/per-CPU, and is cleared in several entry paths; concurrency correctness relies on interrupts/context behavior. Delay-slot simulation is subtle. Kernel-mode bad accesses must find exception table fixups or die.

## Test Signals
Illegal instruction tests, user SIGFPE/SIGTRAP/SIGBUS/SIGILL delivery, atomic `lwa`/`swa` emulation under contention, delay-slot fault tests, and Oops register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/traps.c -->
