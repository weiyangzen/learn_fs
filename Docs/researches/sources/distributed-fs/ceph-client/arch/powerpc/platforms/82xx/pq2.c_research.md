# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/pq2.c

## Purpose
`pq2.c` provides common PowerQUICC II restart support.

## Important APIs, Types, and Functions
`pq2_restart(char *cmd)` disables local interrupts, sets the checkstop reset-enable bit in the CPM2 reset module, clears MSR machine-check, external-interrupt, instruction-translation, and data-translation bits, reads reset space to trigger the reset path, and panics if restart fails. It is marked `NOKPROBE_SYMBOL`.

## Control Flow, State, and Persistence
The function mutates reset-control hardware and never returns. It relies on globally mapped `cpm2_immr`.

## Dependencies and Integration Points
It is used by EP8248E and KM82xx machine definitions and depends on CPM2 IMMR structures and PowerPC MSR manipulation.

## Risks and Test Signals
Risks include triggering checkstop rather than orderly reset if hardware wiring differs, and lack of fallback after panic. Test signals are board restart/reset behavior and no kprobe instrumentation on the restart path.
