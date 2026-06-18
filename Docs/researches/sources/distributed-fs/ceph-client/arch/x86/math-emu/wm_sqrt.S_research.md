# sources/distributed-fs/ceph-client/arch/x86/math-emu/wm_sqrt.S

## Purpose
Computes square roots for normalized positive `FPU_REG` inputs using fixed-point Newton iteration and the common rounding path.

## Important APIs, Types, And Functions
Exports `wm_sqrt(FPU_REG *n, unsigned int control_word)`. The input must already be checked for sign and tag and be scaled into the expected `[1.0, 4.0)` range.

## Control Flow
The routine normalizes the argument around exponent bias, makes a linear initial estimate, performs several low-precision Newton updates, refines with multiword correction from `n - guess^2`, derives rounding information, handles rare near-exact cases by recomputing/ comparing the square, sets exponent to one, and tail-jumps to `fpu_reg_round`.

## State And Persistence
The input register is overwritten with the rounded square root. Local multiword accumulators are stack-resident unless non-reentrant mode uses static storage.

## Dependencies And Integration Points
Called by high-level x87 square-root instruction logic after exceptional cases. Depends on `reg_round.S`, `FPU_REG` layout macros, and exception helpers for paranoid internal checks.

## Risks
Near-exact rounding is explicitly difficult because the main correction estimate may not have enough precision in rare cases. The caller must precondition the input range and exponent. Multiword square/correction carries are dense and assembly-specific.

## Test Signals
Perfect squares, values just above/below square half-way boundaries, inputs in `[1,2)` and `[2,4)`, maximum significand values, all precision/rounding modes, denormal/exception handling in the caller, and comparison against hardware x87 results.
