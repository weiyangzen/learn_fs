# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-bandgap.c

## Purpose
`ti-bandgap.c` is the hardware driver for TI OMAP/DRA bandgap temperature sensors. It handles MMIO access, conversion, alert/shutdown interrupts, clocks, OF matching, thermal sensor exposure, and PM context save/restore.

## Important APIs, Types, and Functions
Key public APIs are `ti_bandgap_read_update_interval`, `ti_bandgap_write_update_interval`, `ti_bandgap_read_temperature`, `ti_bandgap_set_sensor_data`, `ti_bandgap_get_sensor_data`, and `ti_bandgap_get_trend`. Major internals include register RMW helpers, `ti_bandgap_power`, errata 814 temperature read, TALERT/TSHUT IRQ handlers, ADC conversion, single-read forcing, continuous-mode setup, TSHUT/TALERT init, `ti_bandgap_build`, probe/remove, and PM notifier/suspend/resume logic.

## Control Flow
Probe builds `ti_bandgap` from DT match data, maps MMIO, obtains optional TSHUT GPIO, checks efuses, configures clocks, powers sensors, programs counters and default thresholds, sets continuous mode when supported, registers cooling/exposes each sensor through callbacks, enables TALERT IRQs after setup, and registers a CPU PM notifier except on excluded OMAP4430 systems. Temperature reads validate sensor id, optionally force a single conversion, read/freezes DTEMP, apply errata workaround if needed, and convert ADC code to millidegrees. TALERT toggles hot/cold masks to wait for the opposite edge and reports temperatures; TSHUT calls `orderly_poweroff(true)`.

## State and Persistence Behavior
Runtime state is held in `struct ti_bandgap`: base address, clocks, lock, IRQ/GPIO, `regval` shadows, thermal private data, and suspend flag. PM save/restore preserves mode, counters, thresholds, masks, and TSHUT registers across suspend and CPU cluster idle. No nonvolatile persistence exists.

## Dependencies and Integration Points
It depends on clk, GPIO, IRQ, OF platform matching, sys_soc quirks, CPU PM, thermal/cpufreq bridge callbacks, and per-SoC `ti_bandgap_data` tables.

## Risks and Edge Cases
Clock-rate validation uses sensor 0 limits for the device. IRQ setup and error unwinding are complex. Wrong feature bits can cause unsupported register accesses. ADC out-of-range maps to `-EIO`. TSHUT shutdown behavior is intentionally severe and must be tested carefully.

## Test Signals
Per-compatible probe/remove, clock failure and IRQ failure unwinding, temperature conversion bounds, TALERT mask toggling, TSHUT interrupt handling in controlled tests, suspend/resume context restore, CPU PM notifier paths, and errata 814 triple-read coverage.
