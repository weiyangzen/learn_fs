# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra30-tsensor.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra30-tsensor.c` is the dedicated Tegra30 thermal sensor driver. It reads Tegra fuse calibration, enables two TSENSOR channels, registers thermal zones, converts hardware counters to temperatures, and programs interrupt/emergency shutdown thresholds. The source was read as a complete 678-line file.

## Important APIs, Types, and Functions

Key types are `struct tegra_tsensor`, `struct tegra_tsensor_channel`, `struct tegra_tsensor_calibration_data`, and `struct trip_temps`. Important functions include `tegra_tsensor_probe()`, `tegra_tsensor_nvmem_setup()`, `tegra_tsensor_hw_enable()`, `tegra_tsensor_hw_disable()`, `tegra_tsensor_register_channel()`, `tegra_tsensor_get_temp()`, `tegra_tsensor_temp_to_counter()`, `tegra_tsensor_set_trips()`, `tegra_tsensor_enable_hw_channel()`, `tegra_tsensor_disable_hw_channel()`, `tegra_tsensor_isr()`, and suspend/resume handlers.

## Control Flow

Probe allocates state, gets IRQ/MMIO/clock/reset, reads fuse calibration and ATE version, enables hardware, registers two thermal zones if DT provides them, programs channel thresholds, enables channels, and finally requests the threaded IRQ to avoid a race with threshold setup. Temperature reads poll `CURRENT_VALID`, read the current counter, reject overflow, and apply linear plus quadratic calibration. `set_trips` programs the high threshold into TH1 because low breaches are unsupported. Channel enable programs hot and critical thresholds from thermal trips or defaults, enables DVFS and emergency thermal reset interrupts, then enables the thermal zone. The ISR clears per-channel status and updates zones when interrupt bits are set. Suspend disables zones/channels then hardware; resume re-enables hardware and channels.

## State and Persistence Behavior

Calibration coefficients are computed once from fuses and stored in `ts->calib`. `swap_channels` is set for older ATE versions. Channel threshold registers and enable bits are volatile and reprogrammed on resume. Thermal-zone state is maintained by the core.

## Dependencies and Integration Points

The driver depends on Tegra fuse APIs, `tegra_sku_info.revision`, clock/reset frameworks, MMIO polling, threaded IRQs, Device Tree thermal zone registration, and hwmon thermal sysfs. It matches `nvidia,tegra30-tsensor`.

## Risks and Edge Cases

Invalid or old fuse data can disable probe (`ATE < 8`) or trigger channel remapping (`ATE <= 21`). Counter-valid polling can return errors if hardware is not ready. Quadratic conversion and inverse counter calculation must avoid invalid square-root inputs. The emergency shutdown trip is intentionally programmed 5 C above the critical thermal-zone trip, so policy changes should preserve that safety margin.

## Test Signals

Useful tests include fuse vectors for ATE versions, temperature plausibility on both channels, DTs with zero/one/two thermal zones, interrupt-triggered updates, TH1/TH2/TH3 register programming, suspend/resume, and missing/invalid calibration error paths.
