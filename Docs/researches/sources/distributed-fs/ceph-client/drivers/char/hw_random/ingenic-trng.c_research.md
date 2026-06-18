# sources/distributed-fs/ceph-client/drivers/char/hw_random/ingenic-trng.c

## Purpose
This driver supports the Ingenic X1830 DTRNG true random number generator. It enables the generator through a config bit, waits for data-ready status, and returns one 32-bit word.

## Important APIs, Types, and Functions
- `struct ingenic_trng` stores MMIO base and hwrng.
- `ingenic_trng_init()` sets `CFG_GEN_EN`.
- `ingenic_trng_cleanup()` clears `CFG_GEN_EN`.
- `ingenic_trng_read()` polls `STATUS_RANDOM_RDY` and reads `TRNG_REG_RANDOMNUM_OFFSET`.
- `ingenic_trng_probe()` maps registers, enables the clock, and registers devm hwrng.

## Control Flow
Probe maps MMIO, obtains/enables the clock, configures callbacks, and registers. Core init enables generation. Reads wait up to 1 ms for ready status and return one word. Cleanup clears the enable bit.

## State and Persistence Behavior
Hardware generation state persists while enabled; the clock is devm-enabled for device lifetime. No software buffer exists.

## Dependencies and Integration Points
It depends on OF compatible `ingenic,x1830-dtrng`, platform MMIO, a clock, hwrng core, and polling helpers.

## Risks
Read ignores nonblocking `wait` and always polls. The clock remains enabled for the platform device lifetime rather than runtime PM. Timeout returns an error instead of partial data.

## Test Signals
Test clock and MMIO probe failures, init/cleanup toggling, ready timeout, successful reads, and repeated hwrng provider selection.
