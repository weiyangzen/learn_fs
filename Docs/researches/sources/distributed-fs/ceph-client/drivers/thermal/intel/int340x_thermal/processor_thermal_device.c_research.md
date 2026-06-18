# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device.c

## Purpose

`processor_thermal_device.c` is the common Processor Thermal Reporting Device core. It registers ACPI-backed thermal zones, exposes PPCC power-limit metadata, controls TCC offset, and dispatches optional MMIO feature setup for RAPL, RFIM, PTC, workload, power-floor, and SoC slider support.

## Important APIs, Types, and Functions

Exports include `proc_thermal_add()`, `proc_thermal_remove()`, `proc_thermal_suspend()`, `proc_thermal_resume()`, `proc_thermal_mmio_add()`, and `proc_thermal_mmio_remove()`. `proc_thermal_read_ppcc()` parses ACPI `PPCC` packages into two `power_config` entries. `proc_thermal_get_zone_temp()` computes max core temperature using `intel_tcc_get_temp()`. Sysfs attributes expose power limits, power-floor status/enable, and `tcc_offset_degree_celsius`.

## Control Flow

`proc_thermal_add()` binds ACPI state, parses PPCC, chooses `_TMP` or TCC fallback temperature source, registers an INT340x zone, installs ACPI notification, and creates sysfs files/groups. ACPI event `0x83` refreshes PPCC and emits a thermal power capability change. MMIO add maps BAR0 only when needed, then creates feature interfaces in dependency order with error unwinding. Suspend saves TCC offset and slider state; resume refreshes PPCC and restores saved hardware state.

## State and Persistence Behavior

Per-device state lives in `struct proc_thermal_device`; TCC offset save is a static global. Power-limit values mirror firmware PPCC and are refreshed on notify/resume. MMIO features manipulate persistent hardware registers but store minimal driver-side policy.

## Dependencies and Integration Points

Dependencies include ACPI, Intel TCC library, INT340x zone helper, PCI MMIO, sysfs, and feature-specific processor thermal modules. PCI frontends call this file from legacy and newer probe paths.

## Risks and Test Signals

Risks include malformed PPCC packages, partial sysfs creation unwind order, global TCC save across devices, optional feature cleanup asymmetry, and fallback temperature availability on CPU hotplug. Test signals include PPCC parsing, `_TMP` and TCC fallback zones, ACPI event `0x83`, TCC offset permission checks, suspend/resume restore, and MMIO feature-add failure injection.
