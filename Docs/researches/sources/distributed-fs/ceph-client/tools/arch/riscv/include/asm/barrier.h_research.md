# sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/barrier.h

## Purpose
RISC-V tools barrier header.

## Important APIs, Types, and Functions
Defines full and SMP memory barriers using `RISCV_FENCE()` with appropriate predecessor/successor sets, plus release/acquire helpers using `barrier()` and `WRITE_ONCE`/`READ_ONCE`.

## Control Flow, State, and Persistence
No stored state; macros emit `fence` instructions or compiler barriers.

## Dependencies and Integration Points
Depends on `asm/fence.h` and `linux/compiler.h`. Integrated with tools code that needs Linux barrier primitives on RISC-V.

## Risks and Test Signals
Risk is insufficient ordering if the fence masks do not match caller assumptions, especially I/O versus memory. Test signals are RISC-V tools builds and lock-free/barrier litmus-style tests.
