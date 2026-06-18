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
