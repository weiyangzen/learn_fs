<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/core.c

## Purpose

This is the Wilco EC core platform driver. It binds ACPI ID `GOOG000C`, claims IO resources, initializes the MEC mailbox transport, registers core sysfs and keyboard LED support, and creates platform children for RTC, charger, debugfs, and telemetry.

## Important APIs, Types, And Functions

`wilco_get_resource()` requests IO resources from the ACPI platform device. `wilco_ec_probe()` allocates `struct wilco_ec_device`, initializes `mailbox_lock`, allocates the shared data buffer, claims host data/command/MEC IO regions, calls `cros_ec_lpc_mec_init()`, and registers child platform devices. `wilco_ec_remove()` unwinds those children and sysfs.

## Control Flow

Probe requires three IO resources: host data, host command, and MEC EMI. After transport initialization it creates the debugfs child opportunistically, then RTC, keyboard LEDs, sysfs, charger, and telemetry in order. Errors unwind already-created children. Remove unregisters children in reverse logical order and removes sysfs.

## State And Persistence

The core `wilco_ec_device` contains shared mailbox state, a mutex, IO resource pointers, and child platform-device pointers. EC settings manipulated through child drivers persist in EC firmware/hardware according to their command semantics. Kernel state is devm-managed or explicitly unregistered on remove.

## Dependencies And Integration Points

The driver depends on ACPI, platform IO resources, Chrome EC LPC MEC low-level routines, Wilco platform data definitions, the Wilco mailbox module, Wilco sysfs/properties code, LED class support, and optional child drivers.

## Risks

The debugfs child registration failure is ignored, so remove must handle a null or error-like child carefully; the code only unregisters when the pointer is non-null, and `platform_device_register_data()` returns error pointers on failure. Child device ordering is important because optional modules expect parent data and mailbox transport to be ready.

## Test Signals

Test ACPI probe with all three IO resources, resource-request failures, child platform-device creation/unwind, sysfs creation, keyboard LED absence/presence, telemetry child platform data, module unload, and mailbox command use from children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/core.c -->
