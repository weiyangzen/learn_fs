# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_add.S

## Purpose
Implements unsigned addition of two valid, same-sign `FPU_REG` values.

## Important APIs, Types, And Functions
Exports `FPU_u_add(FPU_REG *arg1, FPU_REG *arg2, FPU_REG *answ, int control_w, ...)` using exponent parameters passed by the C/assembly calling convention. It tail-jumps to `fpu_reg_round`.

## Control Flow
The routine chooses the operand with the larger exponent, right-shifts the smaller operand into a 96-bit working value with sticky extension bits, copies the larger exponent to the destination, adds significands, handles carry by shifting right and incrementing the exponent, and delegates rounding/final exception handling.

## State And Persistence
Only the destination register and global exception/status state through the rounding tail are modified.

## Dependencies And Integration Points
Depends on `reg_round.S`, `fpu_emu.h` offset macros, and control-word definitions. Used by higher-level addition/subtraction instruction implementations.

## Risks
Correct sticky-bit formation is essential for later rounding. The caller must provide valid normalized inputs of the same sign and correct exponents. Paranoid checks raise internal exceptions if normalization assumptions fail.

## Test Signals
Equal and unequal exponent additions, shifts below/above 32/64 bits, carry-out normalization, exact versus inexact sticky-extension results, precision-mode rounding, and paranoid invalid normalized-bit cases.
