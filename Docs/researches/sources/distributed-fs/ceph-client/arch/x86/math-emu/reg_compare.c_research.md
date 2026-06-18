# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_compare.c

## Purpose
Implements x87 floating-point register comparison for the software FPU emulator. It compares `st(0)` against another `FPU_REG` or stack register, converts the result into either x87 condition-code bits (`C0/C2/C3`) or P6-style EFLAGS (`CF/PF/ZF`), and drives the instruction entry points for `fcom`, `fucom`, `fcomi`, and variants that pop stack entries.

## Important APIs, Types, And Functions
The central helper is `compare(FPU_REG const *b, int tagb)`, which classifies valid, zero, denormal, infinity, and NaN operands. Public instruction handlers are `fcom_st()`, `fcompst()`, `fcompp()`, `fucom_()`, `fucomp()`, `fucompp()`, `fcomi_()`, `fcomip()`, `fucomi_()`, and `fucomip()`. `FPU_compare_st_data()` supports memory-loaded operands. The file depends on `FPU_REG`, stack accessors like `st()`, tag helpers, `EXCEPTION()`, `denormal_operand()`, `setcc()`, `control_word`, `partial_status`, and `FPU_EFLAGS`.

## Control Flow
`compare()` first resolves `TAG_Special` into subtype tags, then handles zero, finite, denormal, infinity, and NaN cases before falling back to exponent/significand comparison. Denormals are converted through `FPU_to_exp16()` before comparing exponents. Wrapper helpers check stack emptiness, call `compare()`, translate result flags, raise invalid-operation for signaling/unsupported NaNs where required, and optionally pop stack entries when no unmasked exception blocks completion.

## State And Persistence
No persistent external storage is used. The code mutates emulator-visible CPU/FPU state: `partial_status` condition bits, `FPU_EFLAGS`, exception flags, and the register stack top when pop variants complete. Stack-underflow paths set unordered comparison flags and raise `EX_StackUnder`.

## Dependencies And Integration Points
This is an instruction-dispatch target for the x87 emulator. It integrates with `reg_convert.c` for denormal normalization, `status_w.h` for condition-code macros, `control_w.h` for exception mask checks, and generic exception/NaN helpers from the emulator.

## Risks
NaN classification is subtle: signaling NaNs and unsupported encodings must raise invalid while quiet unordered compares may not. Denormal handling can both set comparison results and trigger denormal exceptions. EFLAGS paths must clear/update only `ZF/PF/CF`. Pop variants must not pop when an unmasked exception is pending.

## Test Signals
Useful tests compare finite positive/negative values, signed zero equality, infinities with equal/opposite signs, quiet versus signaling NaNs, unsupported encodings, denormal operands under masked/unmasked denormal exceptions, empty stack faults, and pop/no-pop behavior after `fcomp`, `fucomp`, `fcomip`, and `fucomip`.
