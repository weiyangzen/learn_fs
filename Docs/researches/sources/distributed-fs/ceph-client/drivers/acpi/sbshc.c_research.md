# sources/distributed-fs/ceph-client/drivers/acpi/sbshc.c

## Purpose

This file implements the ACPI Smart Battery System SMBus host-controller driver for devices matching `ACPI0001` and `ACPI0005`. It exposes small exported SMBus read/write and alarm-callback APIs used by smart battery support while hiding the transport details of the ACPI Embedded Controller query and register window.

## Important APIs, types, and functions

The private `struct acpi_smb_hc` stores the backing `struct acpi_ec`, a transaction mutex, wait queue, EC register offset, EC query bit, alarm callback/context, and a `done` flag. `union acpi_smb_status` decodes the host-controller status byte into status, alarm, and done bits. `enum acpi_smb_status_codes` and `enum acpi_smb_offset` define status values and offsets inside the EC operation region. Exported APIs are `acpi_smbus_read()`, `acpi_smbus_write()`, `acpi_smbus_register_callback()`, and `acpi_smbus_unregister_callback()`. The platform-driver entry points are `acpi_smbus_hc_probe()` and `acpi_smbus_hc_remove()`.

## Control flow

Probe retrieves the ACPI companion, evaluates `_EC`, allocates and initializes `struct acpi_smb_hc`, derives the EC offset from the high byte and the EC query bit from the low byte, and registers `smbus_alarm()` with `acpi_ec_add_query_handler()`. A transaction takes `hc->lock`, verifies the protocol register is idle, writes command/data/address/protocol registers, waits up to one second for `hc->done`, and reads response bytes for read protocols. EC query handling enters `smbus_alarm()`, reads status, completes the wait on successful done status, clears alarm status, filters alarms to SBS charger/manager/battery addresses, and schedules `acpi_smbus_callback()` through `acpi_os_execute()`.

## State and persistence

Runtime state is per platform device and is freed at remove. Transaction serialization is by mutex; completion is via wait queue and `hc->done`. Callback state is mutable under the same mutex and unregister waits for pending ACPI OS callbacks to complete. EC registers hold transient firmware/device state; no persistent kernel configuration is written.

## Dependencies and integration points

The driver depends on the ACPI EC core (`ec_read()`, `ec_write()`, query handlers), ACPI platform-device matching, ACPICA async execution, and the public declarations in `sbshc.h`. It integrates with smart battery code through exported GPL symbols and with the ACPI device model through `module_platform_driver()`.

## Risks

The transaction path ignores individual EC write failures after the initial protocol read, so fault diagnosis can be coarse. Timeout handling depends on firmware delivering the EC query reliably. Callback unregister must remain synchronized with queued ACPI notification work to avoid use-after-free. Misparsing `_EC` would point at the wrong EC register window or query bit.

## Test signals

Useful signals include module build coverage, ACPI platform probing for `ACPI0001`/`ACPI0005`, successful smart-battery SMBus read/write protocols, timeout behavior when no completion query arrives, alarm callback delivery for SBS charger/manager/battery addresses, and remove/unregister tests with pending notify work.
