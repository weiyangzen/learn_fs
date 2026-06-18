# sources/distributed-fs/ceph-client/drivers/char/hw_random/exynos-trng.c

## Purpose
This driver supports Samsung Exynos TRNG hardware through either direct MMIO registers or a secure monitor call interface. It manages clocks, runtime PM, suspend/resume behavior, and registers an hwrng provider.

## Important APIs, Types, and Functions
- `struct exynos_trng_dev` stores device, MMIO, clocks, hwrng, and feature flags.
- `exynos_trng_do_read_reg()` requests FIFO generation, polls completion, and copies FIFO registers.
- `exynos_trng_do_read_smc()` reads pairs of 32-bit words via `SMC_CMD_RANDOM`.
- `exynos_trng_init_reg()` programs clock divider, enables RNG, and disables post-processing.
- `exynos_trng_init_smc()` initializes firmware TRNG access.
- PM hooks call SMC exit/resume/init and runtime PM transitions.

## Control Flow
Probe selects MMIO or SMC callbacks from OF match data, enables runtime PM, obtains clocks, and registers hwrng. MMIO init configures the generator. SMC init asks firmware to initialize. Reads either trigger/poll the FIFO and copy up to eight words, or loop SMC calls with retry handling. Remove and suspend notify firmware for SMC variants and release runtime PM.

## State and Persistence Behavior
Clocks and runtime PM state persist while the device is active. SMC firmware owns secure TRNG state. MMIO registers hold divider, enable, post-processing, and FIFO request state.

## Dependencies and Integration Points
It depends on OF compatibles `samsung,exynos5250-trng` and `samsung,exynos850-trng`, Arm SMCCC for SMC variants, clocks `secss` and optional `pclk`, runtime PM, and hwrng core.

## Risks
`exynos_trng_do_read_smc()` writes two words per success and assumes caller `max` is sized suitably by the hwrng core. Resume error paths after acquiring runtime PM may leave usage counts elevated on SMC failures. Secure firmware availability is mandatory for Exynos850 mode.

## Test Signals
Test both compatibles, missing clocks, MMIO poll timeout, SMC retry/error statuses, suspend/resume, remove SMC exit, and `/dev/hwrng` reads with small and large sizes.
