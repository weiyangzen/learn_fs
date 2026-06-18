# sources/distributed-fs/ceph-client/drivers/char/hw_random/atmel-rng.c

## Purpose
This platform driver registers Atmel/Microchip TRNG hardware with hwrng. It manages the peripheral clock, optional half-rate mode for high clock rates, runtime PM autosuspend, and reads one 32-bit word from `TRNG_ODATA` when data is ready.

## Important APIs, Types, and Functions
- `struct atmel_trng_data` identifies variants needing half-rate configuration.
- `struct atmel_trng` stores clock, MMIO base, hwrng, device, and variant flag.
- `atmel_trng_init()` enables the clock, programs `TRNG_MR` if needed, and enables with `TRNG_KEY`.
- `atmel_trng_read()` uses runtime PM, waits for `TRNG_ISR_DATRDY`, reads output, and re-reads ISR to avoid stale data.
- Runtime PM hooks call init/cleanup.

## Control Flow
Probe maps MMIO, gets the clock and match data, configures hwrng callbacks, enables runtime PM, and registers the provider. Reads resume the device, wait or immediately sample readiness depending on `wait`, read one word, then autosuspend. Remove and runtime suspend disable hardware.

## State and Persistence Behavior
Hardware enable and clock state are tied to runtime PM. The variant half-rate flag is immutable after probe. No software entropy buffer is kept; each read returns at most one word.

## Dependencies and Integration Points
It depends on OF compatibles `atmel,at91sam9g45-trng` and `microchip,sam9x60-trng`, platform MMIO, a clock, PM runtime, and hwrng core.

## Risks
The wait helper ignores the return value of `readl_poll_timeout()` and returns only final ready state. Probe/remove cleanup paths differ under `CONFIG_PM`; remove calls cleanup regardless and expects hardware to be accessible. Re-reading ISR is necessary to avoid duplicate data if altered.

## Test Signals
Test both compatibles, clock rate above/below 100 MHz, runtime suspend/resume, nonblocking no-data reads, data-ready polling timeout, remove cleanup, and repeated `/dev/hwrng` reads after autosuspend.
