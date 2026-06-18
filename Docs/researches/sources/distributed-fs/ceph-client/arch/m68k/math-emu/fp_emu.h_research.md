# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_emu.h

## Purpose
Provides shared C and assembly definitions for the m68k floating-point emulator, including status manipulation, normalization linkage, and core operand helpers.

## APIs, Flow, And State
For C, it defines `IS_INF`, `IS_ZERO`, `fp_set_sr()`, `fp_set_quotient()`, `fp_copy_ext()`, monadic/dyadic normalization checks, `fp_set_nan()`, `fp_set_ovrflw()`, and inline-assembly calls into conversion routines such as `fp_normalize_ext()` and `fp_conv_ext2long()`. For assembly, it defines `fp_set_sr`, `fp_clr_sr`, and `fp_tst_sr` macros that operate on the emulated FPSR in `FPDATA`. It declares external constants `fp_QNaN` and `fp_Inf`.

## Dependencies And Integration
Includes `asm/math-emu.h`, and for assembler includes `asm/asm-offsets.h`. It is included by nearly every math-emulator C and assembly file, making it the glue between `struct fp_ext`, `FPDATA`, and low-level labels in `fp_util.S`.

## Risks And Test Signals
Inline assembly constraints and register assumptions are ABI-sensitive. The `fp_conv_long2ext` macro appears to jump to `fp_conv_ext2long`, so conversion helper naming should be verified against actual behavior. Test signals are compile tests, trap instruction tests, status-register bit tests, and C/assembly interop around `a0/d0` clobbers.
