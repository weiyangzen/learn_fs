# sources/distributed-fs/ceph-client/drivers/thermal/uniphier_thermal.c

## Purpose
`uniphier_thermal.c` is a Socionext UniPhier platform thermal driver using a parent syscon regmap to configure PVT temperature monitoring, alert channels, and thermal-zone reporting.

## Important APIs, Types, and Functions
Important types are `uniphier_tm_soc_data` for per-SoC offsets and `uniphier_tm_dev` for runtime state. Key functions initialize calibration and monitor mode, set alerts, enable/disable sensor, read signed temperature, clear IRQs, handle threaded alarm updates, walk trips, probe, and remove.

## Control Flow
Probe allocates state, gets match data and IRQ, obtains the parent syscon regmap, initializes the sensor and calibration, requests a threaded IRQ, registers a DT thermal zone, walks all trips to program up to three alert channels, validates that a critical trip exists at or below 120 C, and enables monitoring. Hard IRQ disables the interrupt and clears alert bits, then the thread updates the thermal zone.

## State and Persistence Behavior
Runtime state tracks regmap, alert enable flags, thermal zone, and SoC offsets. Hardware monitor and alert registers persist while the device is active; remove disables alerts and stops PVT. There is no PM implementation in this file.

## Dependencies and Integration Points
It depends on syscon/regmap, OF match data, platform IRQs, `devm_thermal_of_zone_register`, and thermal trip iteration.

## Risks and Edge Cases
Only three alert channels are available; DT with more trips can overrun expectations unless thermal trip count is constrained externally. The hard IRQ disables the IRQ but the thread does not re-enable it in this file, so IRQ flow should be audited against irq-core semantics and hardware behavior.

## Test Signals
Probe on each compatible, calibration fallback property tests, signed temperature reads, alert programming for trips, critical-trip limit failure, IRQ-triggered thermal updates, and remove disabling sensor registers.
