<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/math-emu.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/math-emu.h

## Purpose
`math-emu.h` defines the internal ABI for the m68k software FPU emulator, including FPSR/FPCR bit fields, C data structures, debug helpers, and assembler macros.

## Important APIs, Types, and Functions
It defines FPSR accrued/exception/condition-code bits, FPCR rounding and precision constants, debug masks, `union fp_mant64`, `union fp_mant128`, `struct fp_ext`, `struct fp_data`, `FPDATA`, `dprint()`, `uprint()`, assembler offsets, PC access macros, instruction fetch helpers, user-memory access macros with exception-table fixups, and debug printing macros.

## Control Flow, State, and Persistence
For C, emulator state lives in `current->thread.fp` as `struct fp_data`. For assembly, macros advance saved PC, fetch instruction words/longs from user space, and recover faults through fixup sections.

## Dependencies and Integration Points
It depends on `setup.h`, `linkage.h`, scheduler/current task state, printk, pt_regs offsets, and thread FP register offsets. FPU emulator C and assembly files share this layout.

## Risks
The header explicitly requires synchronization with `asm/fpu.h` and assembler offsets. User access macros are fault-sensitive. Big-endian quotient extraction is assumed. Debug printing can perturb emulator timing.

## Test Signals
Signals include FPU emulator instruction suites, rounding/precision tests, exception bit behavior, user fault recovery during instruction operand access, signal/context-switch preservation, and assembler offset validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/math-emu.h -->
