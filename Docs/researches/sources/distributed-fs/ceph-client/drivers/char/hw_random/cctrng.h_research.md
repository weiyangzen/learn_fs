# sources/distributed-fs/ceph-client/drivers/char/hw_random/cctrng.h

## Purpose
This header provides CryptoCell TRNG register offsets, bit shifts, masks, power constants, entropy quality, and EHR sizing used by `cctrng.c`.

## Important APIs, Types, and Functions
- `CC_TRNG_QUALITY` declares 1024 bits of entropy per 1024 bits of input.
- `CC_TRNG_NUM_OF_ROSCS`, `CC_TRNG_EHR_IN_WORDS`, and `CC_TRNG_EHR_IN_BITS` define ring oscillator and EHR geometry.
- `CC_HOST_RNG_IRQ_MASK` and `CC_RNG_INT_MASK` define interrupt routing/masking.
- Register offsets cover RNG, secure host RGF, power-down, and NVM idle status.

## Control Flow
There is no executable control flow. The C driver uses these constants to program TRNG collection, decode ISR fields through generated masks, handle host interrupts, and manage suspend/resume state.

## State and Persistence Behavior
The header creates no state. It describes MMIO layout and constants that govern persistent hardware register state controlled by `cctrng.c`.

## Dependencies and Integration Points
It depends on `linux/bitops.h` and is included only by the CryptoCell TRNG driver in this subset. The constants must match the CryptoCell 703/713 register map and driver field-extraction macros.

## Risks
Wrong offsets or bit positions can mask interrupts incorrectly, miss FIPS health failures, corrupt power state, or read the wrong EHR words. Since the values are compile-time constants, errors are only visible at runtime on hardware.

## Test Signals
Build-test `cctrng.c`, validate register writes against hardware documentation or trace logs, test interrupt mask bits, EHR word count assumptions, and suspend/resume NVM idle polling.
