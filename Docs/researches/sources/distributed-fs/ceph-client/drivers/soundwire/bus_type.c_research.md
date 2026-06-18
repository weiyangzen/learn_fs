# sources/distributed-fs/ceph-client/drivers/soundwire/bus_type.c

## Purpose
Implements the Linux device-model bus type for SoundWire slave devices. It matches slave devices to `sdw_driver` ID tables, probes/removes/shuts down slave drivers, emits modalias uevents, registers the SoundWire bus at init, and exposes driver registration helpers.

## Important APIs, Types, and Functions
The exported bus object is `sdw_bus_type`. Exported functions are `__sdw_register_driver()` and `sdw_unregister_driver()`, plus `sdw_slave_modalias()` used elsewhere. Local functions include `sdw_get_device_id()`, `sdw_bus_match()`, `sdw_slave_uevent()`, `sdw_bus_probe()`, `sdw_bus_remove()`, `sdw_bus_shutdown()`, `sdw_bus_init()`, and `sdw_bus_exit()`.

## Control Flow
Driver matching compares a slave's manufacturer ID, part ID, optional SoundWire version, and optional class ID against the driver's ID table. Probe requires firmware description, validates the ID again, attaches a power domain without powering up, allocates a per-bus slave index, calls the driver probe, reads slave properties, creates IRQ-domain mapping if requested, initializes dynamic DPN sysfs attributes, normalizes clock-stop timeout, marks the slave probed, and notifies the driver of current status if the bus was already active. Remove clears `probed`, calls driver remove, and frees the index. Module init creates debugfs root and registers the bus through `postcore_initcall`.

## State and Persistence Behavior
The bus type is global. Per-slave persistent state changed here includes `index`, `probed`, `prop`, `clk_stop_timeout`, and IRQ/sysfs setup. `slave_ida` on the bus allocates a stable index for the slave during its bound lifetime. Power-domain attachment persists until device teardown, although explicit detach is not present in this file.

## Dependencies and Integration Points
Depends on Linux device model, module driver registration, power domains, SoundWire public type helpers, IRQ mapping, sysfs attribute groups, and debugfs initialization. Slave codec/function drivers use `module_sdw_driver()`-style wrappers that eventually call `__sdw_register_driver()`. The core bus add path creates devices that bind through this bus type.

## Risks
If `dev_pm_domain_attach()` succeeds and a later IDA allocation or driver probe fails, this file returns without an explicit power-domain detach. Probe failure after IDA allocation frees the ID but does not undo any partial side effects inside driver probe beyond the driver's own error handling. Firmware node checks intentionally reject devices without ACPI/OF descriptions unless ACPI is disabled and OF node exists, which affects synthetic devices. Late status notification errors are warnings, so codec initialization may be deferred or incomplete without failing probe.

## Test Signals
Test driver matching for version/class wildcard and exact cases, modalias uevent strings, driver registration without probe callback, probe/remove failure injection around power-domain attach and IDA allocation, late probe after bus already reports attached, dynamic sysfs DPN creation, domain IRQ mapping, shutdown callback dispatch, and bus init/exit with debugfs enabled.
