# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/fpu.c

## Purpose
`fpu.c` saves/restores SH4 FPU context and handles FPU error traps for denormal/subnormal floating-point operations by emulating selected instructions.

## Important APIs, Types, And Functions
Important functions are `save_fpu()`, `restore_fpu()`, `denormal_to_double()`, `ieee_fpe_handler()`, `float_raise()`, `float_rounding_mode()`, and `BUILD_TRAP_HANDLER(fpu_error)`. It calls softfloat helpers such as `float64_mul`, `float32_div`, and `float64_to_float32`.

## Control Flow
Save/restore enables the FPU, moves FPUL/FPSCR and both FR banks through `frchg`, then disables the FPU. On an FPU trap, `fpu_error` unlazies current task FPU state, clears pending emulation flags, asks `ieee_fpe_handler()` to decode the faulting or delay-slot instruction, updates FPSCR cause/flag bits, restores FPU state, and returns unless enabled exceptions require `SIGFPE`.

## State And Persistence
Task FPU state persists in `tsk->thread.xstate->hardfpu`. Global `fpu_exception_flags` accumulates softfloat exception causes during one trap. The code manipulates hardware FPSCR/FPUL/FR registers.

## Dependencies And Integration Points
It integrates with lazy FPU ownership, SH trap handling, signal delivery, instruction decoding helpers, and `softfloat.c`.

## Risks
The file notes big-endian save/restore is untested. Delay-slot instruction decoding is subtle; wrong next-PC handling can skip or repeat instructions. FPSCR PR/FR bank handling must avoid undefined `frchg` behavior.

## Test Signals
FPU context-switch tests, signal-frame FP state tests, denormal add/sub/mul/div conversion tests, enabled-exception `SIGFPE` tests, and endian build coverage are key.
