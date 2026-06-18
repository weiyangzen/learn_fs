# sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/perf_regs.h

## Purpose
Defines s390 perf register indexes.

## Important APIs, Types, and Functions
Exports `enum perf_event_s390_regs` for GPRs R0-R15, FP0-FP15, PSW mask, and PC.

## Control Flow, State, and Persistence
No runtime state; perf uses these indexes in sample masks.

## Dependencies and Integration Points
Integrated with s390 perf register sampling.

## Risks and Test Signals
Risk is sample layout mismatch with kernel perf ABI. Test signals are perf register sampling and mask tests.
