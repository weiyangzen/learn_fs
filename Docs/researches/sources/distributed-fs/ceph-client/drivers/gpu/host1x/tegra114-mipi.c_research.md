# sources/distributed-fs/ceph-client/drivers/gpu/host1x/tegra114-mipi.c

## Purpose
Implements the Tegra MIPI calibration provider used by Tegra DSI/CSI clients to power the MIPI calibration block, program SoC-specific pad calibration values, start calibration, and wait for completion. It is a platform driver named `tegra-mipi` and registers a `tegra_mipi_ops` provider through `devm_tegra_mipi_add_provider()`.

## Important APIs, Types, and Functions
Key local types are `struct tegra_mipi_pad`, which maps data and optional clock-lane calibration registers for each pad group; `struct tegra_mipi_soc`, which captures SoC-specific pad tables and tuning constants; and `struct tegra_mipi`, which stores device state, MMIO base, prepared clock, mutex, and `usage_count`. Exported behavior is indirect through `tegra114_mipi_ops`: `enable`, `disable`, `start_calibration`, and `finish_calibration`. `tegra114_mipi_power_up()` and `tegra114_mipi_power_down()` toggle bias-pad clamp/regulator bits. `tegra114_mipi_start_calibration()` writes drive, clamp, lane, noise-filter, prescale, and start bits. `tegra114_mipi_finish_calibration()` polls `MIPI_CAL_STATUS` until calibration is inactive and done.

## Control Flow
Probe selects a compatible entry (`nvidia,tegra114-mipi`, `tegra124-mipi`, `tegra132-mipi`, or `tegra210-mipi`), maps the register resource, initializes the mutex, obtains a prepared clock, stores driver data, and publishes the provider. Clients call `enable()` before using lanes; the first user powers up shared bias resources. Calibration is a two-step transaction: `start_calibration()` enables the clock, locks the register mutex, programs selected lane registers according to `mipidev->pads`, starts the block, delays at least 72 microseconds, and returns with the mutex and clock still held. The paired `finish_calibration()` polls hardware status, then unlocks and disables the clock. `disable()` decrements `usage_count` and powers down on the last user.

## State and Persistence
Runtime state is held only in memory and hardware registers: `usage_count`, the mutex, SoC data pointer, MMIO state, and clock state. There is no filesystem persistence. Register values survive until hardware reset or later writes. The split start/finish API intentionally preserves lock and clock ownership across the calibration interval.

## Dependencies and Integration Points
Depends on Linux platform, OF matching, clk, MMIO, polling helpers, and the Tegra MIPI calibration framework in `<linux/tegra-mipi-cal.h>`. It is integrated with display/camera clients through the provider API and with host1x display plumbing by the externally visible `tegra_mipi_driver` symbol.

## Risks
The split calibration contract is fragile: every successful `start_calibration()` must be followed by `finish_calibration()` or the mutex remains locked and the clock remains enabled. `tegra114_mipi_disable()` decrements without guarding underflow, so mismatched client enable/disable calls can corrupt shared power state. SoC pad tables encode register aliases, including shared clock registers, and bad compatible data can program wrong lanes. Poll timeout failures propagate but still clean up lock/clock in `finish_calibration()`.

## Test Signals
Useful signals include successful probe for each compatible, balanced enable/disable tests with multiple clients, calibration timeout/error-path coverage, and DSI/CSI link bring-up with selected pads on Tegra114/124/132/210. Dynamic debug around register programming plus clock enable counts would expose mismatched start/finish or usage-count bugs.
