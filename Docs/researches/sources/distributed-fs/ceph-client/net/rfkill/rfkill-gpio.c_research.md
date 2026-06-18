# sources/distributed-fs/ceph-client/net/rfkill/rfkill-gpio.c

## Purpose
Implements a generic platform rfkill driver that controls radio power using reset/shutdown GPIOs and an optional clock, with ACPI/OF property support.

## Important APIs, Types, and Functions
Defines `struct rfkill_gpio_data`, `rfkill_gpio_set_power()` as the rfkill `set_block` callback, `rfkill_gpio_probe()`, and `rfkill_gpio_remove()`. ACPI support uses GPIO mappings for `reset-gpios` and `shutdown-gpios`; match tables cover ACPI IDs `BCM4752` and `LNV4752`, OF compatible `rfkill-gpio`, and a DMI deny table.

## Control Flow
Probe rejects denied systems, reads name/type properties, maps ACPI type when present, obtains optional clock and reset/shutdown GPIOs, requires at least one GPIO, drives GPIOs initially active, allocates an rfkill device, optionally initializes default-blocked state, registers it, and stores driver data. `rfkill_gpio_set_power()` enables the clock before unblocking, drives GPIOs to match power state, and disables the clock when blocking. Remove unregisters and destroys the rfkill object.

## State and Persistence
State is devm-managed driver data plus an rfkill object pointer, optional clock pointer, GPIO descriptors, type/name, and `clk_enabled`. No persistent storage is used; platform firmware properties define configuration.

## Dependencies and Integration
Depends on platform device core, GPIO consumer API, optional clocks, rfkill core API, ACPI device properties, OF matching, DMI matching, and firmware properties such as `label`/`radio-type` or `name`/`type`.

## Risks and Test Signals
Risks include optional GPIO NULL handling with direction/value calls, clock enable/disable imbalance if `clk_enabled` desynchronizes, firmware with bogus ACPI devices, and active-high assumptions from initial GPIO output values. Test signals are probe with reset-only, shutdown-only, and both GPIOs; `default-blocked`; ACPI and OF property parsing; blocked/unblocked GPIO and clock transitions; DMI-denied platform rejection; and remove while unblocked.
