# sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/perf_regs.h

## Purpose
Defines MIPS perf register indexes.

## Important APIs, Types, and Functions
Exports `enum perf_event_mips_regs` for PC and R1-R31, with `PERF_REG_MIPS_MAX` set after R31.

## Control Flow, State, and Persistence
No state; perf masks and samples use these ordinal values.

## Dependencies and Integration Points
Integrated with MIPS perf register sampling.

## Risks and Test Signals
Risk is numbering mismatch with perf's target register dump order. Test signals are sample decode and register mask tests.
