# subset-b-000908 Research

Grouped research for the subset B source files under `sources/distributed-fs/ceph-client/arch/x86/math-emu` and `sources/distributed-fs/ceph-client/arch/x86/mm`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_compare.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_compare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_constant.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_constant.c

## Purpose
Defines the emulator's internal `FPU_REG` constants and implements the x87 `FLD` constant opcodes. Constants include 1, pi, pi/2, pi/4, log2(10), log2(e), log10(2), ln(2), zero, infinity, and the indefinite quiet NaN.

## Important APIs, Types, And Functions
`MAKE_REG()` constructs extended-format constants. Exported constants include `CONST_1`, `CONST_PI`, `CONST_PI2`, `CONST_PI2extra`, `CONST_PI4`, `CONST_Z`, `CONST_QNaN`, and `CONST_INF`. `fconst()` dispatches by `FPU_rm` through `constants_table[]`; helpers such as `fldpi()` and `fldln2()` adjust the low significand word based on rounding control.

## Control Flow
`fconst()` indexes the constant table using the decoded ModRM register field. `fld_const()` checks stack overflow, pushes a new x87 stack register, copies the selected constant, applies a tiny rounding adjustment, sets the tag, and clears `C1`. Invalid table entries call `FPU_illegal()`.

## State And Persistence
The file owns immutable constant objects and mutates only the emulator stack/status during loads. It pushes stack entries and writes tags with `FPU_settag0()`. There is no persistence beyond FPU state.

## Dependencies And Integration Points
Depends on `fpu_emu.h` for `FPU_REG` layout and stack helpers, `status_w.h` for `clear_C1()`, and `control_w.h` for rounding-control bits. `reg_constant.h` exposes constants to arithmetic and storage code.

## Risks
The constants are stored at fixed extended precision and depend on one-word adjustments for x87 rounding-mode compatibility. Stack overflow must be detected before `push()`. Header declarations for `CONST_PINF` and `CONST_MINF` are not defined here, so users must rely on definitions elsewhere or avoid them.

## Test Signals
Exercise every `FLD1/FLDL2T/FLDL2E/FLDPI/FLDLG2/FLDLN2/FLDZ` encoding under all rounding modes, stack overflow behavior, resulting tags, sign/exponent fields, and illegal `FPU_rm` dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_constant.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_constant.h -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_constant.h

## Purpose
Declares shared `FPU_REG` constants for the math emulator.

## Important APIs, Types, And Functions
The header includes `fpu_emu.h` and declares external constants such as `CONST_1`, `CONST_PI`, `CONST_PI2`, `CONST_PI2extra`, `CONST_PI4`, `CONST_Z`, `CONST_INF`, `CONST_QNaN`, plus positive/negative infinity aliases.

## Control Flow
There is no executable control flow. It is an include-time contract between constant definitions and arithmetic/storage users.

## State And Persistence
The declarations refer to immutable `const` objects. No state is allocated by this header.

## Dependencies And Integration Points
Used by arithmetic files such as multiply/divide and by load/store conversion code to copy canonical zero, infinity, and NaN values. It depends on the exact `FPU_REG` representation from `fpu_emu.h`.

## Risks
Declaration/definition drift is the main risk. Any constant declared but not defined in the linked emulator will cause build failures; any change to `FPU_REG` layout requires all constants to be audited.

## Test Signals
Build/link coverage for all declared constants and runtime checks that arithmetic invalid/overflow/zero paths copy the expected canonical encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_constant.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_convert.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_convert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_divide.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_divide.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_ld_str.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_ld_str.c

## Purpose
Implements all math-emulator transfers between user memory and internal `FPU_REG` values, including load/store of extended, double, single, integer, packed BCD, environment, and full FPU save/restore images.

## Important APIs, Types, And Functions
Loaders include `FPU_load_extended()`, `FPU_load_double()`, `FPU_load_single()`, `FPU_load_int64()`, `FPU_load_int32()`, `FPU_load_int16()`, and `FPU_load_bcd()`. Stores include `FPU_store_extended()`, `FPU_store_double()`, `FPU_store_single()`, integer stores, and `FPU_store_bcd()`. Environment helpers are `fldenv()`, `FPU_frstor()`, `fstenv()`, and `fsave()`. `FPU_round_to_int()` performs integer rounding.

## Control Flow
Load paths wrap user-memory access with reentrancy checks, decode external formats, classify zeros, normals, denormals, infinities, and NaNs, normalize as needed, and set tags. Store paths branch on tag, round to target precision, raise underflow/overflow/precision/invalid exceptions according to the control word, write masked indefinite values where required, and finally copy bytes to user memory. Environment paths decode 14-byte or 28-byte formats depending on address mode, restore or derive tags, and serialize registers in stack order.

## State And Persistence
This file reads/writes user memory and heavily mutates emulator state: registers, tags, `control_word`, `partial_status`, `top`, instruction/operand addresses, and FPU stack contents. `fsave()` also calls `finit()`, making it a state-resetting operation.

## Dependencies And Integration Points
Depends on Linux `uaccess` primitives, FPU stack/tag macros, constants from `reg_constant.h`, control/status word definitions, normalization and shift helpers, and exception helpers. It is the bridge between architectural memory formats and emulator internals.

## Risks
User memory access can fault and the comment notes emulator static data may change while swapping, so reentrancy handling matters. Rounding edge cases for denormals, overflow, NaNs, unsupported encodings, and masked/unmasked exceptions are high risk. Integer minimum values and BCD overflow use special indefinite encodings. A notable review point is the `FPU_store_single()` empty-register branch checking `control_word & EX_Invalid`, while neighboring code generally uses `CW_Invalid`.

## Test Signals
Round-trip tests for float/double/extended, all integer widths, BCD, infinities, quiet/signaling NaNs, denormals, zero signs, precision modes, rounding modes, masked and unmasked exceptions, invalid stack stores, `fldenv/fstenv` in 16/32-bit modes, `frstor/fsave` register ordering, and user-copy fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_ld_str.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_mul.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_mul.c

## Purpose
Implements high-level multiplication for two `FPU_REG` operands, handling tags and exceptional values before delegating finite unsigned multiplication to `FPU_u_mul()`.

## Important APIs, Types, And Functions
`FPU_mul(FPU_REG const *b, u_char tagb, int deststnr, int control_w)` multiplies stack destination `st(deststnr)` by an external/register operand and stores the result back into `deststnr`.

## Control Flow
The valid-fast path calls `FPU_u_mul()` with XORed sign and summed exponents. Special handling resolves denormal operands through `FPU_to_exp16()`, zero results for finite/zero combinations, NaN propagation, invalid `zero * infinity`, and infinity propagation with result sign. Failed unsigned multiplication restores the saved destination sign.

## State And Persistence
The destination register and tag are modified. Exceptions update global emulator state. No persistent storage is used.

## Dependencies And Integration Points
Uses `reg_u_mul.S`, `reg_convert.c`, constants, stack/tag helpers, and common arithmetic exception helpers. Called by x87 instruction decode for multiply variants.

## Risks
Destination may alias a source, so helper ordering and saved sign matter. Denormal exceptions can prevent writes. Zero sign behavior follows real 80486/IEEE behavior rather than the text of older manuals.

## Test Signals
Finite products across signs/exponents, source/destination aliasing, denormal operands, zero times finite, zero times infinity invalid, infinity times finite, NaN propagation, overflow/underflow from `FPU_u_mul()`, and masked/unmasked exception returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_mul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_norm.S -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_norm.S

## Purpose
Provides i386 assembly normalization helpers for `FPU_REG` significands.

## Important APIs, Types, And Functions
Exports `FPU_normalize(FPU_REG *n)` and `FPU_normalize_nuo(FPU_REG *n)`. The first normalizes and reports underflow/overflow; the second normalizes without underflow/overflow exception handling.

## Control Flow
Both functions inspect the high and low significand words, shift left until the high bit is set, and adjust the exponent by the shift distance. `FPU_normalize()` then checks `EXP_OVER` and `EXP_UNDER`, calling `arith_overflow()` or `arith_underflow()` as needed before returning a tag. `FPU_normalize_nuo()` returns `TAG_Valid` or `TAG_Zero` without exception calls.

## State And Persistence
The input register is modified in place. Exception paths update global FPU exception state. No persistent storage is allocated.

## Dependencies And Integration Points
Called by conversion, load, and arithmetic code. It relies on `FPU_REG` offset macros and arithmetic exception helpers declared through `fpu_emu.h` and `exception.h`.

## Risks
The assembly assumes exact structure offsets and 32-bit calling conventions. Exponent conversion between internal and 80x87 biased form must happen in the correct order. Underflow during shift adjustment is expected and must flow into arithmetic exception handling.

## Test Signals
Normalize already-normal values, low-word-only values, zero, exponent underflow, exponent overflow, and denormal conversion callers that require no-underflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_norm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_round.S -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_round.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_add.S -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_add.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_div.S -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_div.S

## Purpose
Implements unsigned finite division of two normalized `FPU_REG` significands.

## Important APIs, Types, And Functions
Exports `FPU_u_div(FPU_REG *a, FPU_REG *b, FPU_REG *dest, unsigned int control_word, char sign)`. It computes/adjusts the destination exponent and tail-jumps to `fpu_reg_round`.

## Control Flow
The routine computes exponent difference plus bias, clamps extreme underflow, and fast-paths divisors with zero low word using 32-bit division. Full division builds a multiword accumulator, estimates quotient limbs using the divisor high word plus one, corrects overestimates, computes remainder relation to the denominator for rounding information, handles quotient overflow by shifting right and incrementing exponent, then sets up `%eax:%ebx:%edx` for rounding.

## State And Persistence
The destination register is written during rounding. Local accumulator/result storage is stack-resident unless non-reentrant mode uses statics.

## Dependencies And Integration Points
Called by `reg_divide.c` for finite operands. Integrates with `reg_round.S` for precision, sign, and exception handling.

## Risks
The long division correction logic has many carry/borrow invariants. Remainder classification drives exact/half/more-than-half rounding and is a correctness hotspot. Divisor normalization is required; paranoid builds detect broken preconditions.

## Test Signals
Fast divisor path, full divisor path, dividend less/equal/greater than divisor, quotient overflow, exact division, exact half remainder, just-below/above-half remainders, exponent underflow, and all precision/rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_div.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_mul.S -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_mul.S

## Purpose
Implements unsigned finite multiplication for normalized `FPU_REG` significands at approximately 128-bit internal precision.

## Important APIs, Types, And Functions
Exports `FPU_u_mul(FPU_REG *a, FPU_REG *b, FPU_REG *c, unsigned int cw, char sign, int exponent_sum)`, though the exact parameters are consumed by assembly offset macros and the common rounding tail.

## Control Flow
The routine multiplies all 32-bit limbs of the two 64-bit significands, accumulates a 128-bit product, computes the biased destination exponent from the summed exponents, clamps extreme underflow, normalizes by shifting left when the top product bit is clear, converts lower product bits into rounding extension information, and jumps to `fpu_reg_round`.

## State And Persistence
Writes the destination register through `reg_round.S`; local accumulators are stack-resident or static under `NON_REENTRANT_FPU`.

## Dependencies And Integration Points
Called by `reg_mul.c` after tag/special-case handling. It depends on `reg_round.S`, `fpu_emu.h` offsets, and control-word definitions.

## Risks
Product accumulation and carry propagation must preserve enough low-order information for rounding. It does not independently validate exponent overflow/underflow beyond preparing values for the common rounder.

## Test Signals
Products near 1.0 and 4.0, normalization shift/no-shift, carry propagation across limbs, low discarded bits affecting rounding, underflow/overflow through the rounder, denormal-preconverted operands from the C wrapper, and precision controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_mul.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_sub.S -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_sub.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/round_Xsig.S -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/round_Xsig.S

## Purpose
Provides normalization and simple rounding for a 12-byte extended-significand (`Xsig`) helper type.

## Important APIs, Types, And Functions
Exports `round_Xsig(Xsig *n)` and `norm_Xsig(Xsig *n)`. Both return the signed shift count applied to normalize the value.

## Control Flow
Both routines load three 32-bit words, shift left until the most significant bit is set, and store the adjusted value. `round_Xsig()` additionally rounds based on the high bit of the discarded low word and handles carry by setting the normalized top bit and incrementing the shift count. `norm_Xsig()` can shift by up to two 32-bit word positions but does not round.

## State And Persistence
The pointed-to `Xsig` is modified in place. No global state is changed.

## Dependencies And Integration Points
Used by higher precision math-emulator functions that need 96-bit fixed-point normalization. Depends on `fpu_emu.h` for calling-convention macros and `Xsig` layout.

## Risks
The returned shift count is negative for left normalization and is part of caller exponent adjustment. Carry during rounding can renormalize the result by one bit. Zero or very small inputs must be interpreted correctly by callers.

## Test Signals
Already-normal values, one-word and two-word left shifts, rounding no-carry, rounding carry into the high word, and zero/under-normalized inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/round_Xsig.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/shr_Xsig.S -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/shr_Xsig.S

## Purpose
Implements right shifts for 12-byte `Xsig` values.

## Important APIs, Types, And Functions
Exports `shr_Xsig(Xsig *arg, unsigned nr)`.

## Control Flow
The routine branches on shift count ranges: less than 32, 32-63, 64-95, and 96 or more. It uses `shrd` for cross-word shifts and zeroes high words as they shift out. Shifts of 96 or greater clear the full value.

## State And Persistence
The `Xsig` object is modified in place. No global state is touched.

## Dependencies And Integration Points
Used by extended precision math routines. Depends on the three-word memory layout expected by `fpu_emu.h`.

## Risks
Boundary counts are the main risk because x86 variable shifts have masked counts and `shrd` only supports useful 0-31 counts. The helper intentionally discards shifted-out bits; callers needing sticky bits must handle them elsewhere.

## Test Signals
Shift counts 0, 1, 31, 32, 33, 63, 64, 65, 95, 96, and larger, preserving expected cross-word bit movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/shr_Xsig.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/status_w.h -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/status_w.h

## Purpose
Defines x87 status-word bit masks and small helpers for manipulating emulator status flags.

## Important APIs, Types, And Functions
Macros define exception bits (`SW_Invalid`, `SW_Denorm_Op`, `SW_Zero_Div`, `SW_Overflow`, `SW_Underflow`, `SW_Precision`), stack fault, summary/backward flags, condition codes, top-of-stack shift, and busy bit. Helpers include `clear_C1()`, `set_C1()`, `setcc(cc)`, `status_word()`, and `status_word_and_BUSY()`.

## Control Flow
Header-only macros update `partial_status` and combine it with `top` to synthesize the architectural status word.

## State And Persistence
All helpers operate on global emulator state such as `partial_status` and `top`; no storage is declared here.

## Dependencies And Integration Points
Included by comparison, constants, load/store, and exception/status paths. It is the shared definition of condition and exception flag layout.

## Risks
Bit definitions must match x87 architectural layout. `setcc()` preserves non-condition bits while replacing `C0/C1/C2/C3`; misuse can unintentionally clear `C1`.

## Test Signals
Instruction-level tests that inspect `fnstsw`, condition codes after compare/classification, stack-top reporting, busy bit synthesis, and exception-summary behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/status_w.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/version.h -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/version.h

## Purpose
Carries the software FPU emulator version string.

## Important APIs, Types, And Functions
Defines `FPU_VERSION` as `"wm-FPU-emu version 2.01"`.

## Control Flow
No executable control flow.

## State And Persistence
No mutable state. The macro is compile-time metadata.

## Dependencies And Integration Points
Used wherever the emulator reports or embeds its version.

## Risks
Version drift is the only meaningful risk; the macro may not reflect local changes unless manually maintained.

## Test Signals
Build coverage and any diagnostic output that includes `FPU_VERSION`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/wm_shrx.S -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/wm_shrx.S

## Purpose
Implements 64-bit right-shift helpers used by integer conversion and rounding code.

## Important APIs, Types, And Functions
Exports `FPU_shrx(void *arg1, unsigned arg2)` and `FPU_shrxs(void *arg1, unsigned arg2)`. Both shift the 64-bit quantity stored at `arg1`; `FPU_shrx()` returns the shifted-out extension in `eax`, while `FPU_shrxs()` returns a compact sticky form optimized for integer rounding.

## Control Flow
`FPU_shrx()` handles shift ranges below 32, 32-63, 64-95, and 96 or more, updating the memory operand and `eax`. `FPU_shrxs()` handles the same conceptual ranges but sets low bits in `eax` to indicate whether discarded bits beyond the primary half-bit were nonzero.

## State And Persistence
The 64-bit memory operand is modified in place. No global state is touched.

## Dependencies And Integration Points
`FPU_round_to_int()` uses `FPU_shrxs()` to detect fractional bits and half-way cases. Other emulator helpers use `FPU_shrx()` when an explicit extension word is needed.

## Risks
Sticky-bit encoding must match callers' rounding macros. Boundary shift counts can easily produce wrong half/more-than-half decisions. The assembly assumes little-endian two-word layout.

## Test Signals
Shift-count boundary tests, exact-half cases, discarded-nonzero sticky cases, zeroing for shifts above 95, and integer rounding behavior for positive/negative values under all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/wm_shrx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/wm_sqrt.S -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/wm_sqrt.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/mm/Makefile

## Purpose
Defines the build composition and instrumentation policy for `arch/x86/mm`.

## Important APIs, Types, And Functions
This is a kbuild file, not C code. It controls object lists such as `init.o`, `fault.o`, `ioremap.o`, `extable.o`, `tlb.o`, `cpu_entry_area.o`, and conditional objects for huge pages, page-table dumps, KASAN/KMSAN, MMIOTRACE, NUMA, pkeys, KASLR, PTI, and memory encryption.

## Control Flow
Kbuild evaluates configuration symbols to choose object files and sanitizer/tracing flags. Several files disable KCOV/KASAN/KMSAN/KCSAN or `-pg` instrumentation because they run in boot, entry, memory-encryption, or sensitive page-table contexts.

## State And Persistence
No runtime state. It persists build policy in the source tree.

## Dependencies And Integration Points
Integrates `arch/x86/mm` with kernel configuration options and compiler instrumentation. Conditional object selection must match symbol definitions and source availability.

## Risks
Incorrect instrumentation can recurse in entry/page-table code or break boot. Missing conditional objects silently remove features; wrong sanitizer exclusions can produce false positives or runtime faults.

## Test Signals
Build matrix across 32/64-bit, KASAN/KMSAN/KCSAN/KCOV, PTDUMP/debugfs, hugetlb, NUMA backends, MMIOTRACE, PTI, KASLR, pkeys, and AMD memory encryption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/amdtopology.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/amdtopology.c

## Purpose
Discovers AMD NUMA topology directly from northbridge PCI configuration registers during early boot and registers memory ranges per node.

## Important APIs, Types, And Functions
`amd_numa_init()` is the exported initialization entry. `find_northbridge()` scans bus 0 devices for supported AMD function IDs. Static `nodeids[8]` records node IDs from DRAM limit registers.

## Control Flow
The code checks early PCI access, finds the northbridge, reads node count from config register `0x60`, then iterates up to eight DRAM base/limit pairs. It skips disabled/excess/empty/interleaved entries, clamps ranges to `[0,max_pfn)`, enforces sorted bases, calls `numa_add_memblk()`, and sets `numa_nodes_parsed`. After valid memory nodes are found, it maps APIC IDs to nodes based on core-domain size.

## State And Persistence
Mutates global NUMA parse state, memory-block descriptors, and APIC-ID-to-node mappings during `__init`. `nodeids` is `__initdata`.

## Dependencies And Integration Points
Depends on direct PCI config access, memblock/numa_memblks, E820-derived PFN limits, topology domain sizing, and APIC mapping helpers. Used when `CONFIG_AMD_NUMA` is enabled.

## Risks
Northbridge register interpretation is hardware-specific. Interleaved memory is rejected. The APIC mapping assumes contiguous APIC IDs by node and core-domain size. Invalid BIOS register order or limits aborts NUMA setup.

## Test Signals
Boot logs on AMD NUMA systems, disabled/interleaved/malformed node register cases, APIC-to-node validation, memblock NUMA ranges, and fallback behavior when early PCI is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/amdtopology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/cpu_entry_area.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/cpu_entry_area.c

## Purpose
Builds per-CPU CPU-entry-area mappings used by x86 entry code for GDT, TSS, entry stacks, exception stacks, and debug-store areas.

## Important APIs, Types, And Functions
Exports `get_cpu_entry_area(int cpu)` and `cea_set_pte()`. Initialization is driven by `setup_cpu_entry_areas()`, with helpers `init_cea_offsets()`, `setup_cpu_entry_area_ptes()`, `setup_cpu_entry_area()`, `percpu_setup_exception_stacks()`, and `percpu_setup_debug_store()`.

## Control Flow
On x86-64, KASLR can randomize each CPU's CEA slot; without KASLR the CPU number is used. Setup populates required PTEs, maps read-only GDT/TSS on 64-bit or writable versions on 32-bit, maps per-CPU entry and exception stacks with guard pages, conditionally maps VC stacks for encrypted guests, maps Intel debug-store data, then syncs the initial page table.

## State And Persistence
Creates permanent kernel mappings in the CPU entry area and initializes per-CPU pointers such as `cea_exception_stacks` and `_cea_offset`. Page tables are modified via `set_pte_vaddr()`.

## Dependencies And Integration Points
Entry assembly, traps, double-fault/NMI/MCE/#VC handling, KASAN shadow population, PTI/shared page tables, fixmap, descriptor tables, and per-CPU storage all depend on these mappings.

## Risks
Incorrect mapping protections can fault in entry code or weaken isolation. TSS layout assertions protect CPU errata around page boundaries. KASLR offset selection is O(n^2) and must avoid duplicate CEA slots. CEA PTEs are global only when present to avoid `PROT_NONE` confusion.

## Test Signals
Boot on 32/64-bit, KASLR and non-KASLR, PTI, AMD encrypted guests with #VC, Intel debug-store support, KASAN, CPU hotplug/possible CPU count variants, and fault injection on exception stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/cpu_entry_area.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/debug_pagetables.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/debug_pagetables.c

## Purpose
Exposes page-table dump views through debugfs.

## Important APIs, Types, And Functions
Defines seq-file show callbacks for kernel, current kernel, current user under PTI, and EFI page tables. Module init creates `/sys/kernel/debug/page_tables/*`; module exit removes the directory recursively.

## Control Flow
Each show callback checks the relevant `mm->pgd` and calls `ptdump_walk_pgd_level_debugfs()`. Init creates read-only debugfs files conditionally based on `CONFIG_MITIGATION_PAGE_TABLE_ISOLATION`, EFI, and x86-64.

## State And Persistence
Maintains a static debugfs directory dentry while loaded. Does not mutate page tables.

## Dependencies And Integration Points
Wraps `dump_pagetables.c` walker output for debugfs. Integrates with `init_mm`, `current->mm`, `efi_mm`, and module lifecycle.

## Risks
Assumes `current->mm` is valid in current views; kernel threads or unusual debugfs access contexts can be sensitive. Output exposes kernel mapping details and is appropriately mode `0400`.

## Test Signals
Mount debugfs and read `page_tables/kernel`, `current_kernel`, PTI `current_user`, and EFI files under matching configs; unload module and verify cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/debug_pagetables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/dump_pagetables.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/dump_pagetables.c

## Purpose
Walks x86 page tables and formats contiguous ranges with common attributes, optionally checking for writable-and-executable mappings.

## Important APIs, Types, And Functions
Core state is `struct pg_state`; range labels use `struct addr_marker`. Public functions include `ptdump_walk_pgd_level_core()`, `ptdump_walk_pgd_level()`, `ptdump_walk_pgd_level_debugfs()`, `ptdump_walk_user_pgd_level_checkwx()`, and `ptdump_walk_pgd_level_checkwx()`. `pt_dump_init()` fills runtime marker addresses.

## Control Flow
The ptdump walker calls note/effective-protection callbacks for each page-table level. `note_page()` groups ranges until permissions, effective permissions, level, or marker boundaries change, then prints address span, size, attributes, and level. WX checking counts ranges whose effective protection is writable and executable, with a PCI BIOS exception. Debugfs and boot-time callers select init, current, PTI user, or EFI page tables.

## State And Persistence
Most state is per-walk. Static `address_markers[]` is initialized at boot with dynamic address-space boundaries. No page-table entries are modified.

## Dependencies And Integration Points
Uses generic `ptdump_walk_pgd()`, x86 page-table flag definitions, KASAN, EFI, PTI, and architecture virtual-address constants. Debugfs exposure is in `debug_pagetables.c`.

## Risks
Effective permissions across page-table levels are easy to report incorrectly, especially for NX and user/RW inheritance. WX warnings can be noisy or security-sensitive. Marker max-line truncation must not hide important regions unexpectedly.

## Test Signals
Read debugfs dumps, run boot-time WX checks, compare marker ordering on 32/64-bit with KASAN/PTI/EFI/LDT/ESPFIX, verify large-page level labeling, and inject known WX mappings in test kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/dump_pagetables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/extable.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/extable.c

## Purpose
Implements x86 exception-table fixup dispatch for recoverable faults in kernel code.

## Important APIs, Types, And Functions
Public entries are `ex_get_fixup_type()`, `fixup_exception()`, and `early_fixup_exception()`. Handlers include default IP fixup, zeropad loads, fault-code returns, SGX fault tagging, FPU restore reset, user-access warning/fixup, MSR safe/unsafe handling, clear-FS, immediate/register writes, ucopy length accounting, and FRED `ERETU` repair.

## Control Flow
`fixup_exception()` searches exception tables by faulting IP, extracts type/register/immediate fields from `e->data`, and dispatches to the type-specific handler. Most handlers adjust registers and set `regs->ip` to the relative fixup address. Early fixup handles NMIs specially, validates early kernel context, invokes normal fixup when possible, handles early `BUG`, and halts on unrecoverable early exceptions.

## State And Persistence
Mutates `pt_regs` to redirect execution and return error values. Some handlers reset FPU state, update FRED return frames, clear FS, or print warnings. No persistent tables are allocated here; exception tables are linker/build artifacts.

## Dependencies And Integration Points
Called by traps and page-fault handling. Depends on extable encoding, instruction decoding for zeropad, FPU APIs, BPF, SGX, FRED, Xen/PnP BIOS quirks, MSR machine-check handlers, and early boot diagnostics.

## Risks
Incorrect fixup type dispatch can resume at the wrong IP or corrupt registers. Zeropad verifies exact instruction shape to avoid unsafe emulation. FPU restore fixup is security-sensitive because it prevents stale register leakage. FRED frame rewriting relies on stack-frame layout invariants.

## Test Signals
Kernel uaccess fault recovery, `load_unaligned_zeropad()` page-crossing faults, safe RDMSR/WRMSR error returns, FPU restore fault injection, SGX ENCLS faults, BPF extable handling, early boot fixups, and FRED `ERETU` fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/fault.c

## Purpose
Implements the x86 page-fault handler, from low-level IDT entry through kernel/user address classification, recoverable kernel faults, VMA lookup, `handle_mm_fault()`, signal delivery, and fatal oops reporting.

## Important APIs, Types, And Functions
The IDT entry is `exc_page_fault()`. Core helpers include `handle_page_fault()`, `do_kern_addr_fault()`, `do_user_addr_fault()`, `kernelmode_fixup_or_oops()`, `bad_area_nosemaphore()`, `bad_area_access_error()`, `do_sigbus()`, `spurious_kernel_fault()`, `fault_in_kernel_space()`, `show_fault_oops()`, and 32-bit vmalloc synchronization helpers. Global `show_unhandled_signals` controls fatal segfault logging.

## Control Flow
The entry obtains CR2 or FRED event data, lets KVM async page faults consume synthetic events, enters irq context, traces the fault, checks mmiotrace, and dispatches by address space. Kernel faults attempt 32-bit vmalloc sync, CPU errata workarounds, spurious TLB-fault handling, kprobe handling, exception-table fixup, prefetch erratum handling, then oops. User faults reject reserved-bit faults, SMAP violations, disabled fault handlers, and missing `mm`; otherwise they enable IRQs, set fault flags, emulate vsyscall faults, try RCU VMA locking, fall back to mmap locking, call `handle_mm_fault()`, retry when needed, and translate failures to OOM, SIGBUS, SIGSEGV, or kernel fixups.

## State And Persistence
Updates task thread fault metadata (`trap_nr`, `error_code`, `cr2`), emits perf software fault events and tracepoints, may acquire/release VMA or mmap locks, may alter `pt_regs` through fixups, and can terminate tasks or oops the kernel. 32-bit code synchronizes process page tables with init mappings.

## Dependencies And Integration Points
Integrates with core MM fault handling, VMA locking, pkeys, shadow stacks, SMAP/SMEP/NX, KASAN/KFENCE, KVM async PF, mmiotrace, kprobes, VDSO/vsyscall emulation, exception tables, EFI crash handling, SNP RMP diagnostics, and architecture entry code.

## Risks
This is security and stability critical. User/kernel access classification, sanitized error codes, SMAP and pkey enforcement, shadow-stack rules, and vsyscall emulation must be exact. Locking paths must avoid sleeping in disabled-fault or interrupt contexts. Spurious-fault acceptance must not mask real permission bugs. Signal and oops paths must preserve useful diagnostics without leaking layout to userspace.

## Test Signals
Page-fault selftests for demand faults, COW, protection faults, pkeys, shadow stacks, vsyscall, SMAP, NX/SMEP, user versus kernel faults, disabled pagefaults, exception-table recovery, OOM/SIGBUS/HWPOISON paths, KVM async PF, 32-bit vmalloc races, and boot-time/kprobe/mmiotrace interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/hugetlbpage.c

## Purpose
Provides x86 architecture hooks for HugeTLB page-size validation and CMA order selection.

## Important APIs, Types, And Functions
On x86-64, `arch_hugetlb_valid_size()` accepts PMD-sized huge pages and PUD-sized huge pages when `X86_FEATURE_GBPAGES` is present. With contiguous allocation, `gigantic_pages_init()` registers the PUD-sized hstate. `arch_hugetlb_cma_order()` returns the gigantic-page order when supported.

## Control Flow
Feature checks gate 1 GiB huge-page support. The initcall adds the gigantic hstate at arch init time when runtime allocation is possible.

## State And Persistence
Mutates HugeTLB global hstate registration during init. No per-page state is directly managed here.

## Dependencies And Integration Points
Integrates HugeTLB core with x86 page-table levels and CPU feature discovery. Depends on `hugetlb_add_hstate()` and `boot_cpu_has()`.

## Risks
Incorrect size validation could expose unsupported mappings. 1 GiB support must follow hardware capability and allocation configuration.

## Test Signals
Boot and HugeTLB tests with/without `X86_FEATURE_GBPAGES`, PMD and PUD huge-page reservation/allocation, CMA order selection, and 32-bit build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/ident_map.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/ident_map.c

## Purpose
Builds and frees identity-mapping page tables for the compressed and regular x86 kernel.

## Important APIs, Types, And Functions
Public functions are `kernel_ident_mapping_init()` and `kernel_ident_mapping_free()`. Internal helpers allocate/populate/free P4D, PUD, PMD, and PTE levels using callbacks in `struct x86_mapping_info`.

## Control Flow
Mapping initialization adds `info->offset` to the requested physical range, defaults and masks page-table flags, walks PGD/P4D/PUD/PMD levels, allocates missing tables through `info->alloc_pgt_page()`, optionally uses 1 GiB PUD leaf mappings when allowed and range-aligned, and otherwise creates PMD leaf mappings. Freeing recurses through present non-leaf entries and calls `info->free_pgt_page()`.

## State And Persistence
Mutates caller-provided page-table pages. Allocation/free ownership is delegated to `x86_mapping_info` callbacks and context.

## Dependencies And Integration Points
Used during early boot, decompression, kexec, or other identity-map setup paths. Depends on page-table folding, `__pa()`, page-table flags, 5-level paging detection, and PTI shadow suppression via `_PAGE_NOPTISHADOW`.

## Risks
Leaf mapping selection must never overwrite existing mappings or map beyond requested boundaries. Offset arithmetic and folded P4D/PGD behavior are subtle. Allocation failure must stop cleanly without leaking partially allocated tables to callers that free them.

## Test Signals
Identity-map creation for aligned/unaligned ranges, overlapping existing mappings, 4-level and 5-level paging, direct 1 GiB mappings, PMD mappings, allocation failure injection, and free of mixed leaf/non-leaf trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/ident_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/init.c

## Purpose
Initializes core x86 memory-management state: PAT cache-mode translation tables, early page-table allocation, direct physical mappings, CR4 paging features, PCID gating, memory-map strategy, text-poke address space, `/dev/mem` restrictions, freeing init memory, zone limits, TLB state, swap limits, and executable-memory ranges.

## Important APIs, Types, And Functions
Key functions include `cachemode2protval()`, `pgprot2cachemode()`, `x86_has_pat_wp()`, `alloc_low_pages()`, `early_alloc_pgt_buf()`, `init_memory_mapping()`, `init_mem_mapping()`, `poking_init()`, `devmem_is_allowed()`, `free_init_pages()`, `free_kernel_image_pages()`, `free_initmem()`, `arch_zone_limits_init()`, `update_cache_mode_entry()`, `arch_max_swapfile_size()`, and `execmem_arch_setup()`.

## Control Flow
Boot initializes early page-table buffers, probes large-page/PGE/GB-page support, disables or enables PCID based on CPU/microcode constraints, maps ISA memory, initializes the trampoline, maps RAM ranges top-down or bottom-up using memblock and E820 RAM ranges, loads `swapper_pg_dir`, flushes TLBs, invokes hypervisor hooks, and runs early memtest. Helper paths split ranges by large-page alignment, allocate low page tables from BRK/memblock/free pages, track mapped PFN ranges, and later free init/initrd memory with NX/RW or not-present protections.

## State And Persistence
Mutates global PAT translation tables, PFN mapped ranges, `max_pfn_mapped`, `max_low_pfn_mapped`, `min_pfn_mapped`, CR4 feature masks, page tables, memblock allocations, TLB state, `text_poke_mm`, and executable memory policy. Many variables are `__initdata`, while PAT/TLB/execmem state persists.

## Dependencies And Integration Points
Integrates with E820, memblock, PAT, MTRR/cache attributes, PTI, KASLR, hypervisors, text patching, TLB flushing, debug pagealloc, kmemleak, memory encryption cleanup, `/dev/mem`, L1TF mitigation, module/kprobe/ftrace/BPF executable allocators, and architecture page-table constructors.

## Risks
Boot-time ordering is critical: page tables must be allocated from mapped memory and direct mappings must avoid holes that MTRRs cannot mark UC. Large-page selection affects performance and correctness with debug pagealloc and memory holes. PCID is disabled for specific microcode errata. Freeing init memory must avoid leaving freed secrets mapped in PTI user-visible aliases. `/dev/mem` policy must not expose system RAM.

## Test Signals
Boot across 32/64-bit, 4/5-level paging, KASLR, PTI, PSE/PGE/GB pages, PCID microcode errata, top-down and bottom-up memblock, sparse E820 holes, Xen/hypervisor hooks, debug pagealloc, strict devmem, initrd freeing, L1TF swap-size limiting, and execmem allocation for modules/kprobes/ftrace/BPF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/init.c -->
