# sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_stackcheck.S

## Purpose
Debug `_mcount` hook that detects Alpha kernel stack overflow and forces an oops when the stack pointer is outside the task stack. The source was read as part of `subset-b-000628` and contains 28 lines.

## Important APIs, Types, and Functions
Defines global `_mcount` and uses `TASK_SIZE` from `asm/asm-offsets.h`.

## Control Flow
The hook computes the end of the current task stack from `$8 + TASK_SIZE`, compares it with `$30` stack pointer, returns normally when within bounds, and otherwise stores through address `-8($31)` in a tight loop to force a fault.

## State and Persistence Behavior
Reads current task and stack pointer registers. On failure it intentionally causes a fault; it does not maintain global state.

## Dependencies
Depends on Alpha `_mcount` instrumentation, task stack layout, `TASK_SIZE`, and the oops path triggered by an invalid store.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
A wrong `TASK_SIZE` or unexpected stack context can either miss real overflow or crash a valid path. The failure path is intentionally destructive.

## Test Signals
Build with stack-check debugging, boot a profiling/debug kernel, run deep-call and interrupt workloads, and verify overflow injection reaches the expected oops path while normal calls return.
