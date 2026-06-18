# sources/distributed-fs/ceph-client/arch/x86/math-emu/mul_Xsig.S

## Purpose
This assembly file implements fixed-point multiplication helpers for 12-byte `Xsig` values used by polynomial approximations.

## Important APIs, Types, and Functions
Exported functions are `mul32_Xsig(Xsig *x, unsigned mult)`, `mul64_Xsig(Xsig *x, const unsigned long long *mult)`, and `mul_Xsig_Xsig(Xsig *dest, const Xsig *mult)`. All operate in place on the destination `Xsig`.

## Control Flow
Each function accumulates partial products with `mull`, `addl`, and `adcl` into stack temporaries, retaining the high 96 bits appropriate for fixed-point multiplication. The 32-bit variant multiplies by one word, the 64-bit variant by two words, and the full variant by the significant words of another `Xsig`.

## State and Persistence
There is no global state. The destination `Xsig` is overwritten with an unrounded, generally unnormalized product.

## Dependencies and Integration Points
It depends on `Xsig` word ordering and i386 frame-based calling conventions. It is called by polynomial files for `2^x-1`, atan, log2, sine/cosine, and tangent approximations.

## Risks and Test Signals
Risks include dropped carries, wrong word ordering, and accumulated low-bit error affecting transcendental accuracy. Test signals include polynomial accuracy checks, PARANOID emulator tests, and comparison to high-precision reference results.
