# File Research: sources/cow-pools/bcachefs-tools/include/linux/bits.h

Purpose: bit-mask construction macros compatible with Linux headers.

Key contents:
- Defines bit word and bit-per-type helpers.
- Defines `__GENMASK`, typed `GENMASK_TYPE()`, and `GENMASK*` variants for unsigned long, unsigned long long, and fixed-width integer types.
- Performs compile-time input checks for invalid mask ranges where possible.
- Provides assembly-compatible fallbacks without build-bug checks.

Important interactions:
- Used by bitmap/bitops and code that manipulates packed on-disk fields.
- Relies on compiler/overflow helpers for type maximums and build-time checks.
