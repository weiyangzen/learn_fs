# sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.c` is the common NVIDIA Tegra SOCTHERM thermal management driver for Tegra114/124/132/210-era SoCs. It calibrates and enables TSENSOR channels, registers thermal zones for CPU/GPU/MEM/PLLX groups, programs hardware thermal shutdown and throttle trips, manages over-current interrupt domains, exposes debugfs register dumps, and handles suspend/resume reinitialization. The source was read as a complete 2292-line file.

## Important APIs, Types, and Functions

The core private types are `struct tegra_soctherm`, `struct tegra_thermctl_zone`, `struct soctherm_throt_cfg`, `struct soctherm_oc_cfg`, and `struct soctherm_oc_irq_chip_data`. Important functions include `tegra_soctherm_probe()`, `soctherm_init()`, `enable_tsensor()`, `tegra_thermctl_get_temp()`, `tegra_thermctl_set_trips()`, `tegra_thermctl_set_trip_temp()`, `thermtrip_program()`, `throttrip_program()`, `tegra_soctherm_set_hwtrips()`, `soctherm_thermal_isr_thread()`, `soctherm_edp_isr_thread()`, `soctherm_oc_int_init()`, `soctherm_init_hw_throt_cdev()`, `tegra_soctherm_throttle()`, `soctherm_clk_enable()`, `soctherm_suspend()`, and `soctherm_resume()`. Its thermal-zone ops are `get_temp`, `set_trip_temp`, and `set_trips`.

## Control Flow

Probe matches a SoC descriptor, allocates `tegra_soctherm`, maps SOCTHERM plus CAR or CCROC registers, gets reset and clocks, computes shared and per-sensor calibration via `soctherm-fuse.c`, enables clocks, parses optional `nvidia,thermtrips` and `throttle-cfgs`, initializes raw sensors, pdiv/hotspot registers, and hardware throttling, then registers one thermal zone per sensor group. For each zone it immediately programs hardware trips from the DT thermtrips property or thermal critical trip fallback and optional hot-trip throttle binding. Interrupt setup creates a nested IRQ domain for over-current alarms and requests threaded thermal/EDP IRQs. Runtime thermal IRQs disable asserted level interrupts in the hard handler, clear expected status bits in the thread, and update the affected thermal zones. Over-current IRQs clear OC status, re-enable configured OC alarms, and dispatch nested IRQs when clients enabled them. Suspend disables clocks; resume reenables clocks, reinitializes hardware, and reprograms trips for each zone.

## State and Persistence Behavior

Driver state is devm-managed except debugfs and global OC IRQ chip data. Calibration words are computed at probe and stored in `tegra->calib[]`; hardware registers are reprogrammed on probe and resume. Thermal zones and cooling devices are registered with the thermal core. The `throt_cfgs` array captures parsed DT throttle configuration and cooling-device handles. Hardware stats registers are enabled and visible through debugfs but are not persisted across reset, suspend, or driver reload.

## Dependencies and Integration Points

The driver depends on MMIO resources named `soctherm-reg`, `car-reg`, or `ccroc-reg`, Tegra reset/clock providers, Tegra fuse reads, thermal core internals through `../thermal_core.h`, Device Tree thermal zone registration, cooling-device binding, IRQ domains, debugfs, and SoC descriptor tables from `tegra114/124/132/210-soctherm.c`. DT properties include `nvidia,thermtrips`, `throttle-cfgs`, `nvidia,priority`, CPU/GPU throttle fields, and OC alarm parameters.

## Risks and Edge Cases

Hardware trip programming is safety-critical: bad threshold grain, sign extension, group masks, or thermtrip parsing can prevent shutdown or cause false shutdown. `tegra_soctherm_set_hwtrips()` uses one `temperature` variable for both thermtrip and throttle programming; if a hot trip differs from the critical/thermtrip value, throttle behavior may not match policy expectations. Missing or invalid throttle DT leaves hardware throttling disabled but probe continues. `soctherm_interrupts_init()` returns success if either platform IRQ lookup fails, so systems without IRQ resources rely on polling/set_trips behavior. Global `soc_irq_cdata` assumes one active SOCTHERM instance. Debugfs register reads depend on live clocks/registers. Race safety around trip programming relies on disabling per-group interrupts and `thermctl_lock`.

## Test Signals

Test with real Tegra114/124/132/210 DTs should verify zone registration, sysfs temperatures, critical trip programming, hot-trip throttle binding, OC nested IRQ mapping, debugfs `soctherm/reg_contents`, suspend/resume reprogramming, and module remove clock cleanup. Fault-injection signals include missing resources, bad throttle-cfg nodes, fuse-read failures, missing IRQs, and thermal zone update events after synthetic register status changes.
