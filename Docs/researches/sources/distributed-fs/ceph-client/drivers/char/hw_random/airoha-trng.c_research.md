# sources/distributed-fs/ceph-client/drivers/char/hw_random/airoha-trng.c

## Purpose
This platform driver registers the Airoha EN7581 true RNG with the hwrng core. It enables raw data output, uses an interrupt to wait for reset/startup health checks, validates health status, and returns 32-bit raw samples.

## Important APIs, Types, and Functions
- `struct airoha_trng` stores MMIO base, `struct hwrng`, device pointer, and completion.
- `airoha_trng_init()` enables RNG, leaves software reset, waits for health-check completion, validates failure bits, and polls readiness.
- `airoha_trng_read()` polls `RAW_DATA_VALID` and reads `TRNG_RAW_DATA_OUT`.
- `airoha_trng_irq()` masks interrupts and completes startup.
- `airoha_trng_probe()` maps resources, requests IRQ, configures interrupt/raw data/reset state, and calls `devm_hwrng_register()`.

## Control Flow
Probe masks interrupts, installs the IRQ, enables reset-startup interrupts, enables raw output, places hardware in reset, and registers the hwrng. Core init then enables RNG and unresets hardware. The IRQ completion tells init that health testing completed. Reads wait up to a short timeout for raw data validity and return one word.

## State and Persistence Behavior
Driver state is devm-managed. Hardware enable/reset and interrupt mask state persist between init, reads, and cleanup. The completion is one-shot for the startup health event; cleanup disables RNG and reasserts software reset.

## Dependencies and Integration Points
It depends on OF compatible `airoha,en7581-trng`, platform MMIO, a platform IRQ, hwrng core, completions, and `readl_poll_timeout()`.

## Risks
The startup completion is not reinitialized in `init()`, so repeated init/cleanup cycles rely on completion semantics from first startup. Read ignores `wait` and always polls up to the timeout. A health-check interrupt failure leaves interrupts masked and returns `-ENODEV`.

## Test Signals
Test probe without IRQ/MMIO, startup health pass/fail bits, raw-data timeout, cleanup reset, repeated hwrng selection cycles, and entropy reads through `/dev/hwrng`.
