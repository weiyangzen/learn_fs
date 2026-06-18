# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_round.S

## Purpose
Implements the central rounding, precision-control, denormal, underflow, overflow, and final arithmetic exit logic for basic emulator operations.

## Important APIs, Types, And Functions
Exports `FPU_round(FPU_REG *arg, unsigned int extent, unsigned int control_w)` for C callers and assembly entry labels `fpu_reg_round`, `fpu_reg_round_sqrt`, and `fpu_Arith_exit`. It tracks local flags `FPU_bits_lost` and `FPU_denormal`.

## Control Flow
The routine first handles possible denormal output by shifting right when underflow is masked or preserving an unmasked-underflow state. It then rounds to 24, 53, or 64 bits based on precision control, using rounding mode and sign to decide increment versus truncation. It handles significand carry, re-normalization, precision flags, masked denormal/underflow-to-zero, unmasked underflow exponent biasing, overflow via `arith_overflow()`, sign injection, and register store.

## State And Persistence
The destination `FPU_REG` is written in place. Exception/status state is updated through precision flag helpers and `EXCEPTION()`. Local state is stack-resident unless `NON_REENTRANT_FPU` selects static storage.

## Dependencies And Integration Points
All unsigned arithmetic assembly helpers tail-jump here. It depends on control-word bit definitions, exception helpers, `FPU_REG` layout, and the calling convention that `%eax:%ebx` holds the significand and `%edx` holds round-extension information.

## Risks
This is a high-risk precision core. Rare half-way cases, sign-dependent directed rounding, denormal-to-normal after rounding, and underflow exception ordering must match x87 behavior. Reentrant versus non-reentrant storage changes concurrency assumptions.

## Test Signals
Precision-control tests for 24/53/64 bits, all rounding modes, positive and negative directed rounding, exact half-even cases, extension-less exact results, masked/unmasked underflow, denormal rounded to normal, underflow to zero, overflow, and precision flag direction.
