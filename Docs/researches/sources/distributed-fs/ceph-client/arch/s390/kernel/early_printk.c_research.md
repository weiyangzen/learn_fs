# sources/distributed-fs/ceph-client/arch/s390/kernel/early_printk.c

## Purpose
Registers an early SCLP console for s390 boot diagnostics before the normal console stack is available.

## Important APIs, Types, And Functions
`register_early_console()` installs `sclp_early_console` if SCLP line-mode or VT220 output is available. `setup_early_printk()` handles the `earlyprintk` early parameter. `sclp_early_write()` forwards console writes to `__sclp_early_printk()`.

## Control Flow
The early parameter accepts bare `earlyprintk` or `earlyprintk=sclp`. Registration is skipped if an early console already exists or if SCLP output facilities are absent. Once registered, console writes are routed to SCLP early output.

## State And Persistence
Uses the global `early_console` pointer. The boot console is temporary and marked `CON_BOOT`; normal console registration later replaces it.

## Dependencies And Integration Points
Depends on console core, s390 setup globals, and SCLP early print support. It is used by early exception handling in `early.c`.

## Risks And Edge Cases
Registration before SCLP feature detection will fail if flags are not available yet. Non-sclp parameter values are ignored. Early console output must avoid dependencies on normal memory allocation.

## Test Signals
Signals include boot with `earlyprintk`, early exception output, SCLP line-mode and VT220 environments, and absence of duplicate early consoles.
