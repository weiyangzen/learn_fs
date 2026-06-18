# sources/distributed-fs/ceph-client/drivers/char/hw_random/ingenic-rng.c

## Purpose
This platform driver supports Ingenic JZ4780 and X1000 RNG blocks. It enables the generator, handles version-specific readiness behavior, and returns one 32-bit word per hwrng read.

## Important APIs, Types, and Functions
- `enum ingenic_rng_version` distinguishes `ID_JZ4780` and `ID_X1000`.
- `struct ingenic_rng` stores version, MMIO base, and hwrng.
- `ingenic_rng_init()` enables `ERNG_ENABLE`.
- `ingenic_rng_read()` polls `ERNG_READY` on X1000+ or delays 20 usec on JZ4780, then reads `RNG_REG_RNG_OFFSET`.
- `ingenic_rng_remove()` manually unregisters and disables the device.

## Control Flow
Probe maps MMIO, reads match data, fills callbacks, manually registers hwrng, and stores driver data. Core init enables the generator. Reads apply variant-specific readiness handling and return one word. Remove unregisters and clears the enable register.

## State and Persistence Behavior
Variant selection is fixed at probe. Hardware enable state persists until cleanup/remove. No software buffering exists.

## Dependencies and Integration Points
It depends on OF compatibles `ingenic,jz4780-rng` and `ingenic,x1000-rng`, platform MMIO, hwrng core, and polling helpers.

## Risks
Manual `hwrng_register()` requires remove-time balancing. The JZ4780 delay is empirical to avoid shifted repeat data. The X1000 polling path always waits and does not honor nonblocking `wait`.

## Test Signals
Test both variants, timeout on X1000 readiness, JZ4780 continuous-read delay behavior, register/unregister balancing, and init/cleanup enable writes.
