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
