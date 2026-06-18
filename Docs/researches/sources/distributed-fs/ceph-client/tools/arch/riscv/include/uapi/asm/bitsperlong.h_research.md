# sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/bitsperlong.h

## Purpose
RISC-V UAPI word-size selector.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` from `__riscv_xlen` when available, otherwise falls back to 64, then includes generic bits-per-long.

## Control Flow, State, and Persistence
No runtime state.

## Dependencies and Integration Points
Used by RISC-V tools UAPI consumers for riscv32/riscv64 layout selection.

## Risks and Test Signals
Risk is host-side preprocessing without `__riscv_xlen` defaulting to 64 unexpectedly. Test signals are riscv32/riscv64 cross builds.
