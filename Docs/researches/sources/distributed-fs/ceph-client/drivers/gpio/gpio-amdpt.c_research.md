# sources/distributed-fs/ceph-client/drivers/gpio/gpio-amdpt.c

## Purpose
This ACPI platform driver supports AMD Promontory GPIO controllers. It wraps a small MMIO register block with `gpio-generic` and adds request/free ownership tracking through a sync register.

## Important APIs, types, and functions
`struct pt_gpio_chip` contains a `gpio_generic_chip` and MMIO base. `pt_gpio_request()` checks and sets `PT_SYNC_REG` bits, while `pt_gpio_free()` clears them. Probe initializes generic GPIO registers for input, output, direction, and read-output behavior. ACPI IDs map to either 8 or 24 GPIOs.

## Control flow
Probe requires an ACPI companion, allocates and maps the resource, initializes `gpio_generic_chip_config`, sets request/free and line count, registers the chip, clears sync state, and initializes clock-rate register to zero.

## State and persistence behavior
GPIO direction/value state is MMIO hardware state. The driver also uses `PT_SYNC_REG` as an ownership bitmap to reject pins already marked in use, clearing it at probe. No persistent storage is used.

## Dependencies and integration points
It depends on ACPI matching, platform MMIO resources, and `gpio-generic`. Supported ACPI IDs are `AMDF030`, `AMDIF030`, and `AMDIF031`.

## Risks and edge cases
Probe refuses non-ACPI devices. Clearing `PT_SYNC_REG` at probe assumes no other live firmware user needs existing ownership state. Request returning `-EINVAL` for an already marked pin protects against reconfiguration but can surprise consumers that do not request explicitly.

## Test signals
Verify ACPI match line counts, MMIO generic get/set/direction behavior, sync register set/clear on request/free, rejection of already-used pins, and initialization writes to sync and clock-rate registers.
