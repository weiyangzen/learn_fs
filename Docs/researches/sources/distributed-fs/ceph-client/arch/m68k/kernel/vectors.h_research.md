# sources/distributed-fs/ceph-client/arch/m68k/kernel/vectors.h

## Purpose

`vectors.h` declares the early vector-table initialization entry used by startup assembly.

## Important APIs, Types, and Functions

It declares `void base_trap_init(void);`.

## Control Flow

The header has no executable control flow. `head.S` calls `base_trap_init()` after switching to the real kernel stack and before `start_kernel()`.

## State and Persistence Behavior

No state is owned here. `vectors.c` sets VBR and fills early vector entries.

## Dependencies and Integration Points

It connects `head.S` to `vectors.c`. The function must be callable before full kernel initialization.

## Risks and Edge Cases

A declaration mismatch could break the assembly-to-C call during the earliest exception setup phase.

## Test Signals

Successful boot past early trap setup and correct handling of early bus/illegal/syscall vectors validate this contract.
