# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_switch.S

## Purpose

`vm_switch.S` implements Hexagon context switching between tasks. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The key entry is `__switch_to`, which saves/restores callee-saved registers and task `thread.switch_sp` state. Concrete declarations observed in the file: Includes: `asm/asm-offsets.h`. Types referenced or declared: `task_struct`, `size`. Assembly entry labels: `__switch_to`.

## Control Flow, State, And Persistence

Scheduler runtime flow stores the old task switch stack, loads the next task stack, restores saved registers, and returns into the next task's context or `ret_from_fork`.

## Dependencies And Integration Points

It depends on generated `thread_struct`/switch-stack offsets and integrates with `copy_thread` in `process.c`.

## Risks And Test Signals

Risks are task register corruption, wrong stack pointer restore, and fork return failures. Test signals are scheduler stress, fork/exec loops, and context-switch tracing.
 A local static signal for this file is that it has 83 lines and 2389 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
