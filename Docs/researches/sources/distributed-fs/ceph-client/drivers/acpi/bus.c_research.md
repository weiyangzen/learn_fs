# sources/distributed-fs/ceph-client/drivers/acpi/bus.c

## Purpose
Provides the ACPI core bus implementation and much of ACPI subsystem initialization. It evaluates device status, attaches private data to ACPI handles, negotiates `_OSC` capabilities, dispatches ACPI notifications, matches ACPI devices to drivers, registers the `acpi` bus type, and orders early/late ACPI boot setup.

## Important APIs, Types, And Functions
Global exports include `acpi_root`, `acpi_root_dir`, `acpi_kobj`, `acpi_bus_type`, and capability flags such as `osc_pc_lpi_support_confirmed`, `osc_cpc_flexible_adr_space_confirmed`, `osc_sb_native_usb4_support_confirmed`, and `osc_sb_native_usb4_control`.

Device status helpers are `acpi_bus_get_status_handle()` and `acpi_bus_get_status()`. Private data helpers wrap ACPICA attach/get/detach data with `acpi_bus_private_data_handler()`. `_OSC` support is implemented by `acpi_eval_osc()`, `acpi_osc_error_check()`, exported `acpi_run_osc()`, and `acpi_osc_handshake()`. Platform and USB4 negotiation are driven by `acpi_bus_osc_negotiate_platform_control()` and `acpi_bus_osc_negotiate_usb_control()`.

Notification support includes root `acpi_bus_notify()`, per-driver notify installation/removal, exported `acpi_dev_install_notify_handler()` and `acpi_dev_remove_notify_handler()`, and special `\_SB` shutdown handling through `acpi_sb_notify()`. Matching APIs include `acpi_companion_match()`, `acpi_set_modalias()`, `acpi_match_acpi_device()`, `acpi_match_device()`, `acpi_device_get_match_data()`, `acpi_match_device_ids()`, and `acpi_driver_match_device()`.

Driver/bus glue is `__acpi_bus_register_driver()`, `acpi_bus_unregister_driver()`, `acpi_bus_match()`, `acpi_device_probe()`, `acpi_device_remove()`, and child walkers `acpi_bus_for_each_dev()`, `acpi_dev_for_each_child()`, and `acpi_dev_for_each_child_reverse()`. Initialization entry points are `acpi_early_init()`, `acpi_subsystem_init()`, internal `acpi_bus_init()`, and `acpi_init()` registered with `subsys_initcall`.

## Control Flow
Early boot calls `acpi_early_init()` if ACPI is enabled. It enables ACPICA interpreter slack unless strict mode is set, makes ACPI mappings permanent, applies x86 DSDT copy DMI quirks, reallocates the root table, initializes ACPICA, and adjusts SCI routing on x86. `acpi_subsystem_init()` later enables ACPI mode and tells the regulator core firmware constraints are complete.

`acpi_init()` creates `/sys/firmware/acpi`, initializes PRMT and PCC, calls `acpi_bus_init()`, then runs architecture and feature initializers such as FFH, PCI MCFG, VIOT, HEST/GHES, scan, EC, debugfs, sleep proc, wakeup devices, debugger, `\_SB` notifications, and VIOT. `acpi_bus_init()` loads tables, probes ECDT EC, starts the interpreter, initializes AML objects, negotiates `_OSC`, installs table handlers, initializes sysfs and processor control, probes DSDT EC, initializes sleep and interrupt routing, installs root system notifications, creates `/proc/acpi`, and registers `acpi_bus_type`.

Runtime device binding flows through the generic driver core: `acpi_bus_match()` checks `match_driver` and ACPI IDs; `acpi_device_probe()` calls the ACPI driver's `ops.add`, installs a notify handler if provided, and takes a device reference; `acpi_device_remove()` removes notification handlers, invokes `ops.remove`, clears driver data, and drops the reference.

## State And Persistence
The file maintains global boot and negotiation state, proc/sysfs roots, and exported `_OSC` capability booleans consumed by other subsystems. ACPI devices keep status bits in `struct acpi_device`, private handle data in ACPICA, physical-node relationships protected by `physical_node_lock`, and driver binding state in the device core. There is no runtime persistence across boots.

## Dependencies And Integration Points
This file is the ACPI integration center. It depends on ACPICA table/interpreter/event APIs, Linux device core, procfs, sysfs kobjects, DMI on x86, regulator constraints, workqueues, reboot, PCI, APEI/GHES, PRMT, PCC, VIOT, EC, scan, sleep, debugfs, and architecture hooks. Its exported matching, registration, notification, and `_OSC` symbols are consumed by ACPI drivers and by non-ACPI buses using ACPI companions.

## Risks
Initialization order is delicate: EC, `_OSC`, table handlers, sysfs, scan, IRQ model, and notification setup all have firmware-ordering constraints. `_OSC` error handling must distinguish query failures from masked capabilities or downstream subsystems will assume unsupported features. Matching must avoid binding absent devices and avoid double-matching secondary physical devices sharing one ACPI companion. The graceful shutdown work function intentionally loops while reporting `_OST`, so it must only be scheduled for the specific shutdown notification.

## Test Signals
Boot logs for ACPICA revision, interpreter enablement, `_OSC` support/control masks, interrupt routing model, and absence of ACPI termination are primary signals. Driver binding/unbinding, ACPI modalias uevents, hotplug notifications with `_OST`, USB4/CPPC capability flags, and `/proc/acpi` plus `/sys/firmware/acpi` creation test the major paths. Firmware tables with malformed `_OSC`, missing `_STA`, shared companions, and hotplug events are important regression cases.
