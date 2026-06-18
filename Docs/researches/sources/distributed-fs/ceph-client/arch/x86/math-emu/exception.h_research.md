# sources/distributed-fs/ceph-client/arch/x86/math-emu/exception.h

## Purpose
This header defines emulator exception and status-summary constants shared by C and assembly code.

## Important APIs, Types, and Functions
Macros include `FPU_BUSY`, `EX_ErrorSummary`, `EX_INTERNAL`, `EX_StackOver`, `EX_StackUnder`, `EX_Precision`, `EX_Underflow`, `EX_Overflow`, `EX_ZeroDiv`, `EX_Denormal`, `EX_Invalid`, `PRECISION_LOST_UP`, `PRECISION_LOST_DOWN`, and the `EXCEPTION(x)` wrapper that optionally logs file/line before calling `FPU_exception()`.

## Control Flow
The header has no runtime control flow beyond the `EXCEPTION()` macro expansion. It standardizes the exception code values consumed by the rest of the emulator.

## State and Persistence
It does not store state, but its bit definitions map directly onto persistent `partial_status` and control-word mask behavior.

## Dependencies and Integration Points
It includes `fpu_emu.h` when needed for status bit definitions, and is included by C and assembly arithmetic, polynomial, and decode files.

## Risks and Test Signals
Risks include bit-value drift from x87 status/control words and macro differences between assembler and C. Test signals are correct exception status bits after emulator operations and successful assembly preprocessing.
