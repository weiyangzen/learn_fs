<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_emmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_emmc.c

## Purpose
`pwrseq_emmc.c` is a power-sequence provider for eMMC reset lines. It exposes the `mmc-pwrseq-emmc` compatible and implements hardware reset by toggling a `reset` GPIO.

## Important APIs, Types, And Functions
The provider-private `struct mmc_pwrseq_emmc` embeds `struct mmc_pwrseq`, a `notifier_block` for restart handling, and `reset_gpio`. `mmc_pwrseq_emmc_reset()` is the MMC reset callback. `mmc_pwrseq_emmc_reset_nb()` is a restart handler for emergency reboot when the GPIO can be toggled without sleeping. Probe and remove are handled by `mmc_pwrseq_emmc_probe()` and `mmc_pwrseq_emmc_remove()`.

## Control Flow
Probe allocates provider state, obtains the `reset` GPIO as output-low, optionally registers a high-priority restart handler if the GPIO is non-sleeping, fills `pwrseq.ops/dev/owner`, stores driver data, and registers with `mmc_pwrseq_register()`. Reset asserts the GPIO, waits 1 microsecond, deasserts it, and waits 200 microseconds. Remove unregisters the restart handler and the pwrseq provider.

## State And Persistence
Runtime state is devm-managed provider memory, the reset GPIO descriptor, registered pwrseq list entry, and optional restart handler. Hardware-visible state is the reset GPIO level. The emergency reboot handler exists so the eMMC can be reset even during urgent restart paths where normal sleepable GPIO access is unavailable.

## Dependencies And Integration Points
The file depends on platform-driver binding, OF compatible matching, GPIO consumer APIs, restart handlers, delays, MMC host/pwrseq APIs, and module infrastructure. It integrates with `pwrseq.c` through provider registration and with MMC hardware reset fallback through `.reset`.

## Risks And Edge Cases
If the reset GPIO is sleep-capable, emergency-reboot reset is disabled and a notice is logged. Remove unconditionally calls `unregister_restart_handler()` even when the handler was not registered, relying on notifier semantics to tolerate it. Incorrect GPIO polarity in device tree would invert reset behavior. The timing constants are minimal and may not be enough for all boards if hardware needs a longer reset pulse.

## Test Signals
Tests should verify probe defers or fails cleanly when the GPIO is missing/not ready, host phandle binding succeeds, `mmc_hw_reset()` toggles the GPIO, emergency restart toggles only for non-sleeping GPIOs, and provider unregister removes the pwrseq entry without leaving stale host references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_emmc.c -->
