# sources/distributed-fs/ceph-client/drivers/char/hw_random/meson-rng.c

## Purpose
This driver supports Amlogic Meson RNG blocks, including the older direct-data register variant and the S4 variant that requires seed/run status polling.

## Important APIs, Types, and Functions
- `struct meson_rng_priv` supplies a variant read callback.
- `struct meson_rng_data` stores MMIO base, hwrng, and device.
- `meson_rng_read()` reads one word from `RNG_DATA`.
- `meson_s4_rng_read()` clears seed-ready status, waits for seed and run bits to clear, then reads `RNG_S4_DATA`.
- `meson_rng_probe()` maps MMIO, enables optional `core` clock, selects variant data, and registers hwrng.

## Control Flow
Probe gets match data and resources, sets the hwrng read callback, and registers. Old Meson reads return one word immediately. S4 reads perform two atomic poll loops around the config register before reading data.

## State and Persistence Behavior
The selected read callback is fixed at probe. Optional clock is devm-enabled for device lifetime. Hardware status bits are manipulated per S4 read.

## Dependencies and Integration Points
It depends on OF compatibles `amlogic,meson-rng` and `amlogic,meson-s4-rng`, optional `core` clock, platform MMIO, and hwrng core.

## Risks
The older variant has no readiness or health check. S4 polling ignores the `wait` argument and returns `-EBUSY` on timeout. Only one word is returned regardless of larger buffer requests.

## Test Signals
Test both compatibles, missing match data, optional clock failure, S4 seed/run timeout, and repeated reads through `/dev/hwrng`.
