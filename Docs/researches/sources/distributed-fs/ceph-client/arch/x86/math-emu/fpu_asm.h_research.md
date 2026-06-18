# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_asm.h

## Purpose
This header provides assembly-side definitions for wm-FPU-emu helper routines, including stack-frame parameter offsets and `FPU_REG` field offsets.

## Important APIs, Types, and Functions
Macros include `EXCEPTION`, `PARAM1` through `PARAM7`, `SIGL_OFFSET`, `EXP(x)`, `SIG(x)`, `SIGL(x)`, and `SIGH(x)`. It includes `linux/linkage.h` for symbol annotations.

## Control Flow
There is no runtime control flow. The macros let assembly helpers access C arguments and `FPU_REG` fields consistently.

## State and Persistence
It stores no state, but its offsets define how assembly reads and writes caller-provided emulator structures.

## Dependencies and Integration Points
It is included by emulator `.S` files through `fpu_emu.h`. It depends on 32-bit frame-pointer calling conventions used by these old helper routines.

## Risks and Test Signals
Risks include offset drift if `FPU_REG` layout or calling convention changes. Test signals include successful emulator assembly builds and correct arithmetic helper behavior under stack/register tests.
