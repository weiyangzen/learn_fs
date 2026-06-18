# sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/fence.h

## Purpose
Small RISC-V fence macro helper.

## Important APIs, Types, and Functions
Defines `RISCV_FENCE_ASM(p, s)` and `RISCV_FENCE(p, s)` to stringify predecessor/successor sets into `fence` instructions for assembly or C inline assembly.

## Control Flow, State, and Persistence
No state. Callers choose fence masks and the macro emits the instruction with a memory clobber in C mode.

## Dependencies and Integration Points
Used by `asm/barrier.h` and any tools code needing explicit RISC-V fences.

## Risks and Test Signals
Risk is misuse with incomplete predecessor/successor sets. Test signals are assembly output checks for `iorw,iorw`, `r,r`, `w,w`, and build coverage.
