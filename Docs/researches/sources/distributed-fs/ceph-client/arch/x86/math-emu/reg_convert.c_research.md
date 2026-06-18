# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_convert.c

## Purpose
Provides conversion from normal internal `FPU_REG` exponent representation to the emulator's 16-bit exponent working form, mainly for denormal-aware arithmetic and comparisons.

## Important APIs, Types, And Functions
`FPU_to_exp16(FPU_REG const *a, FPU_REG *x)` copies the 64-bit significand, stores the exponent with `setexponent16()`, and normalizes denormal or pseudo-denormal inputs. It returns the source sign.

## Control Flow
The function copies source significand bits, converts exponent format, then checks for `EXP_UNDER`. Pseudo-denormals with the integer bit set are promoted by increasing the exponent. True denormals are exponent-adjusted and passed through `FPU_normalize_nuo()`. A paranoid internal exception is raised if the result is still not normalized.

## State And Persistence
Only the caller-provided destination register is modified. The source register is not mutated. Internal exceptions may update global FPU exception state.

## Dependencies And Integration Points
Called by compare, multiply, and divide paths when denormal operands must be treated with extended exponent range. It relies on assembly normalization from `reg_norm.S` and exception handling from `exception.h`.

## Risks
The code type-puns `sigl/sigh` through `long long` pointers, so structure layout and alignment assumptions matter. Pseudo-denormal behavior is explicitly noted as non-80486 behavior because it loses denormal identity.

## Test Signals
Cover normal valid numbers, true denormals, pseudo-denormals, signed operands, zero-like underflow encodings, and paranoid detection of unnormalized outputs.
