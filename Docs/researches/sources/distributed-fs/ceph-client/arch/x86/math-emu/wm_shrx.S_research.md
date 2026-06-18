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
