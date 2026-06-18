# sources/distributed-fs/ceph-client/drivers/thermal/armada_thermal.c

## Purpose
Marvell EBU Armada thermal sensor platform driver. It supports older legacy DT bindings that map individual MMIO regions and newer syscon-based bindings, exposes thermal zones through the Linux thermal framework, handles SoC-specific calibration formulas, and optionally programs an overheat interrupt threshold for Armada AP/CP devices.

## Important APIs, Types, and Functions
- `struct armada_thermal_priv` stores the device, regmap/syscon, thermal zone name, channel-selection lock, SoC data, overheat IRQ bookkeeping, and current threshold/hysteresis.
- `struct armada_thermal_data` is the SoC descriptor: init callback, temperature conversion coefficients, status bit layout, syscon offsets, DFX IRQ fields, and `cpu_nr`.
- `struct armada_thermal_sensor` binds one thermal-zone instance to a channel id.
- SoC init functions (`armadaxp_init()`, `armada370_init()`, `armada375_init()`, `armada380_init()`, `armada_ap80x_init()`, `armada_cp110_init()`) program reset, calibration, OSR, averaging, and errata settings.
- `armada_select_channel()` serializes channel changes, switches internal/external sensor mode, restarts conversion, and waits for validity.
- `armada_read_sensor()` extracts the sample, optionally sign-extends it, and applies `temp = (b - m * reg) / div` or the inverted variant.
- `armada_get_temp_legacy()` serves tripless legacy zones; `armada_get_temp()` serves OF zones with channel selection and reselects the overheat-source channel.
- `armada_configure_overheat_int()`, `armada_set_overheat_thresholds()`, and the threaded IRQ pair implement hardware critical-threshold interrupt support.
- `armada_thermal_probe()` chooses legacy vs syscon path, registers thermal zones, requests optional IRQs, and iterates all channels.

## Control Flow
Probe matches an OF compatible to a descriptor, allocates private state, and probes in one of two modes. If the parent is not a syscon regmap, the driver creates a small regmap around the old register resource, initializes the sensor, waits for validity, registers one tripless thermal zone, and enables it. In syscon mode it obtains the parent regmap, initializes the hardware, optionally requests a threaded IRQ, then registers one OF thermal zone for the internal channel plus `cpu_nr` external CPU channels. Temperature reads take `update_lock`, switch the hardware mux to the requested channel, read and convert the status register sample, then switch back to the configured interrupt-source channel.

Overheat IRQ setup looks for the first registered zone with a critical trip, selects that channel, writes threshold/hysteresis registers, and enables DFX/server/thermal IRQ bits. The hard IRQ disables the line and wakes the thread. The thread notifies the thermal core, polls once per second until the current temperature falls below `current_threshold - current_hysteresis`, clears the DFX cause by reading it, notifies the core again, and re-enables the IRQ.

## State and Persistence
State is volatile driver and hardware state only. `current_channel` mirrors the selected hardware mux, `interrupt_source` is the channel that should remain selected for overheat detection, and `current_threshold/current_hysteresis` mirror programmed register thresholds. The syscon/MMIO registers persist across reads but are reinitialized at probe. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on platform devices, OF matching, syscon/regmap or MMIO-backed regmap, thermal core APIs, optional platform IRQs, and DT thermal-zone definitions. Legacy mode uses `thermal_tripless_zone_device_register()`. Syscon mode uses `devm_thermal_of_zone_register()`. Overheat handling depends on DFX IRQ registers defined per SoC descriptor.

## Risks and Edge Cases
- Legacy resource fix-up subtracts `syscon_status_off` from the mapped base and rejects mappings that would cross a page boundary; incorrect DT resources fail probe.
- Channel switching is global hardware state; every read must hold `update_lock` and reselect the interrupt source or overheat IRQ routing can become inconsistent.
- `armada_configure_overheat_int()` return value is ignored in the loop, so failed threshold setup only results in missing `overheat_sensor` and a warning.
- Hysteresis conversion intentionally rounds toward the smallest supported value, which favors hardware safety but can increase interrupt frequency.
- Signed-sample and inverted-calibration descriptor fields must match the SoC or reported temperatures will be wrong.
- The threaded IRQ can sleep for long periods while temperature remains above the low threshold.

## Test Signals
Useful tests include DT-compatible probe success for each descriptor, regmap offset checks, temperature conversion fixtures for signed/inverted descriptors, concurrent reads from multiple thermal zones verifying channel reselection, critical trip IRQ simulation verifying disable/poll/clear/re-enable behavior, and legacy binding probe tests for page-boundary validation and tripless zone enablement.
