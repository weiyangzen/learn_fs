# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_sub.S

## Purpose
Implements unsigned subtraction of two valid `FPU_REG` values where the first operand is known to be greater than or equal to the second.

## Important APIs, Types, And Functions
Exports `FPU_u_sub(FPU_REG *arg1, FPU_REG *arg2, FPU_REG *answ, int control_w, ...)` and tail-jumps to `fpu_reg_round` for nonzero results.

## Control Flow
The smaller operand is shifted right based on exponent difference with sticky extension bits, subtracted from the larger significand, then normalized by shifting left across high, low, and extension words. Exact zero is detected and returned as `TAG_Zero`; otherwise the normalized value goes to common rounding.

## State And Persistence
Writes the destination register and, through rounding, exception/status state. No persistent storage is used.

## Dependencies And Integration Points
Used by high-level subtraction/addition sign-resolution code. Depends on `reg_round.S` and FPU layout macros.

## Risks
The caller precondition that operand one is larger is critical. Cancellation can require large left shifts and may underflow. Sticky bits for shifts over 64 bits affect precision and exact-zero detection.

## Test Signals
Equal operands yielding zero, near-cancellation, exponent differences across 0/31/32/63/64/65 bits, borrow invariants, underflow after normalization, and precision/rounding behavior of inexact differences.
