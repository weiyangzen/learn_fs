# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_arith.c

## Purpose
Implements core arithmetic kernels for the m68k floating-point emulator using the internal unpacked extended format.

## APIs, Flow, And State
Exports constant operands `fp_QNaN` and `fp_Inf`, plus functions declared in `fp_arith.h`: sign operations, add/sub/compare/test, multiply/divide, single-precision multiply/divide variants, modulo/remainder, integer rounding, and scale. The functions mutate `dest` in place, may mutate `src` in some paths, and update emulated FPSR/FPCR state through `FPDATA`. Add/sub align exponents using `fp_denormalize()`, combine mantissas, and handle signed zero and infinities. Mul/div use 128-bit mantissa helpers. `fp_roundint()` implements FPCR rounding modes and sets inexact. `modrem_kernel()` computes quotient, rounds it, subtracts the product, and stores quotient bits.

## Dependencies And Integration
Depends on `fp_emu.h` macros and `multi_arith.h`. Called by opcode dispatch tables in `fp_scan.S`, with final normalization performed by `fp_util.S`.

## Risks And Test Signals
Many operations rely on normalized inputs and exact internal format invariants. `fp_fsub()` and comparison flip `src->sign`, so caller ownership matters. Mod/remainder are marked as potentially inefficient. Test signals are FADD/FSUB/FMUL/FDIV/FCMP/FMOD/FREM/FINT/FSCALE instruction tests across zeros, infinities, NaNs, denormals, rounding modes, overflow, underflow, and divide-by-zero.
