# sources/distributed-fs/ceph-client/drivers/char/hw_random/mtk-rng.c

## Purpose
This driver supports Mediatek hardware RNG blocks. It controls the `rng` clock, enables/disables the generator, waits for readiness, returns 32-bit words, and uses runtime PM autosuspend when available.

## Important APIs, Types, and Functions
- `struct mtk_rng` stores MMIO base, clock, hwrng, and device.
- `mtk_rng_init()` enables the clock and sets `RNG_EN`.
- `mtk_rng_cleanup()` clears `RNG_EN` and disables the clock.
- `mtk_rng_wait_ready()` checks/polls `RNG_READY`.
- `mtk_rng_read()` resumes runtime PM, loops over ready words, and autosuspends.
- Runtime PM hooks call init/cleanup under `CONFIG_PM`.

## Control Flow
Probe allocates state, gets clock and MMIO, registers hwrng, stores driver data, and enables runtime PM. Reads resume the device, read available words while ready, and schedule autosuspend. Without PM, hwrng init/cleanup directly manage hardware.

## State and Persistence Behavior
Hardware enable and clock state are runtime-PM controlled. Quality is set to 900. No software buffer is kept.

## Dependencies and Integration Points
It depends on OF compatibles `mediatek,mt7986-rng` and `mediatek,mt7623-rng`, clock named `rng`, platform MMIO, runtime PM, and hwrng core.

## Risks
`pm_runtime_get_sync()` return value is ignored in read, which can lead to MMIO access after resume failure. Atomic polling always happens when requested by `wait`; timeout returns `-EIO` only if no data was read and wait was true.

## Test Signals
Test clock/MMIO failures, runtime PM resume failure, ready timeout, partial reads, PM autosuspend/resume, non-PM builds, and quality-based provider selection.
