# sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/perf_regs.h

## Purpose
Defines RISC-V perf register indexes.

## Important APIs, Types, and Functions
Exports `enum perf_event_riscv_regs` for PC, RA, SP, GP, TP, temporaries, saved registers, and argument registers following RISC-V ABI names.

## Control Flow, State, and Persistence
No state; perf uses ordinal indexes in sample masks and payloads.

## Dependencies and Integration Points
Integrated with RISC-V perf register sampling.

## Risks and Test Signals
Risk is ABI name/order mismatch. Test signals are perf sample register decoding and mask validation.
