# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_divide.c

## Purpose
Implements high-level x87 `FPU_REG` division, including operand selection, destination selection, sign computation, tag handling, special values, and exception routing before delegating finite unsigned division to `FPU_u_div()`.

## Important APIs, Types, And Functions
`FPU_div(int flags, int rm, int control_w)` supports normal and reversed operands, register or memory-loaded operands, and destination-in-`st(0)` or destination-in-`st(rm)` behavior via flags such as `REV`, `LOADED`, and `DEST_RM`.

## Control Flow
The function resolves operand pointers/tags according to flags, computes result sign, and fast-paths two valid operands through `FPU_u_div()`. It then handles denormals via `denormal_operand()` and `FPU_to_exp16()`, zero numerator/denominator cases, NaN propagation through `real_2op_NaN()`, infinity/infinity invalid operations, infinity divided by finite/zero, and finite/zero divide-by-zero.

## State And Persistence
The destination stack register and its tag are modified on successful or masked-exception results. Exceptions update emulator status. The original destination sign is saved only for consistency with helper behavior; most paths overwrite the destination.

## Dependencies And Integration Points
Integrates with `reg_u_div.S`, `reg_convert.c`, `reg_constant.c`, NaN/invalid/divide-by-zero helpers, and stack/tag helpers from `fpu_emu.h`.

## Risks
Flag combinations are easy to mis-handle because memory-loaded operands reuse `rm` as a pointer. NaN propagation must target the architectural destination. Denormal operands can abort when unmasked. Divide-by-zero and `0/0` must diverge into different exception classes.

## Test Signals
Exercise all flag combinations, `a/b` and `b/a`, destination `st(0)` vs `st(i)`, valid finite divisions, denormal operands, signed zero results, finite/zero, zero/zero, infinity cases, NaN propagation, and unmasked exception return values.
