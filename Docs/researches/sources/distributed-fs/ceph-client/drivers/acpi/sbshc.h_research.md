# sources/distributed-fs/ceph-client/drivers/acpi/sbshc.h

## Purpose

This header is the small public contract for the ACPI SBS SMBus host-controller driver. It lets smart-battery code refer to SMBus protocol IDs, well-known SBS device addresses, the opaque host-controller object, and the exported read/write/callback functions without depending on the driver's private EC implementation.

## Important APIs, types, and functions

`struct acpi_smb_hc` is forward-declared as an opaque handle. `enum acpi_smb_protocol` defines ACPI SMBus protocol values for quick, byte, word, block, process-call, and block-process-call operations. `enum acpi_sbs_device_addr` defines charger, manager, and battery addresses. `smbus_alarm_callback` is the callback signature. The prototypes are `acpi_smbus_read()`, `acpi_smbus_write()`, `acpi_smbus_register_callback()`, and `acpi_smbus_unregister_callback()`.

## Control flow

The header has no executable control flow. Callers obtain or receive an `acpi_smb_hc *` from the SBS/HC integration path, issue protocol-specific reads or writes, and optionally register an alarm callback that `sbshc.c` dispatches from EC query context.

## State and persistence

No state is defined here beyond compile-time enum values and function types. The opaque pointer deliberately keeps lock, wait queue, EC offset, query bit, and callback storage private to `sbshc.c`.

## Dependencies and integration points

The declarations require ACPI/Linux integer types such as `u8` from included kernel headers in users. This header is included by `sbshc.c` and smart battery clients that need ACPI SBS transport access.

## Risks

Protocol enum values are ABI-like within the driver family and must stay aligned with the ACPI SMBus host-controller protocol register. Address enum values are 7-bit SBS addresses; callers must not pass already-shifted bus addresses because `sbshc.c` shifts the address when writing the EC address register.

## Test signals

Compile users against the header, exercise each protocol value through `acpi_smbus_read()`/`write()`, and verify callback registration/unregistration remains type-correct for smart battery users.
