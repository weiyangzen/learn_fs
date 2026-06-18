# File Research: sources/cow-pools/bcachefs-tools/raid/internal.h

## Purpose
Private central header for the RAID library.

## Key Responsibilities
- Defines feature/config macros for x86, SSE2, SSSE3, and AVX2 based on config or compiler target.
- Defines compatibility helpers: `BUG_ON`, `__always_inline`, `__aligned`, `__align_ptr`.
- Includes public RAID headers and helper declarations.
- Declares internal functions for parity generation, recovery, inversion, delta generation, and self-test.
- Declares function-pointer dispatch tables for selected implementations.
- Declares Galois-field and pshufb tables.
- Provides SSE/AVX begin/end helpers with memory barriers and register clobbers.

## Important Dispatch Globals
- `raid_gen3_ptr`
- `raid_genz_ptr`
- `raid_gen_ptr[RAID_PARITY_MAX]`
- `raid_rec_ptr[RAID_PARITY_MAX]`

## Dependencies
Includes standard C headers and RAID public headers; conditionally uses inline x86 assembly for SIMD cleanup barriers.
