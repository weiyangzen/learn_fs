# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_mul.c

Purpose: implements single-precision multiplication for the MIPS FPU emulator.

Important APIs/functions: `ieee754sp_mul(union ieee754sp x, union ieee754sp y)` handles all special classes, performs a 24x24-bit mantissa multiply using 16-bit partial products, and formats the rounded result.

Control flow: after class handling, finite operands are denormal-normalized, sign is XORed, exponent is summed, mantissas are shifted to the top of words, partial products are accumulated into high/low 32-bit words, sticky information is preserved from the low product, and the result is shifted into single GRS format.

State and persistence: exception flags are updated through invalid special cases and final formatting.

Dependencies and integration: used by MUL.S and fused helpers for non-fused multiply-like behavior. Depends on single internal header macros.

Risks and test signals: test `0*inf` invalid, qNaN/sNaN precedence, product normalization carry, low-word sticky propagation, overflow/underflow, signed zero, and all rounding modes.
