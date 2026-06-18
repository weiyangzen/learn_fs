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
