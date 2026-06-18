# sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-int3496.c

## Purpose
`extcon-intel-int3496.c` supports Intel INT3496 ACPI USB OTG control devices. It reads a USB ID GPIO, controls optional VBUS and USB mux GPIOs or a VBUS regulator, and reports `EXTCON_USB_HOST`.

## Important APIs, types, and functions
`struct int3496_data` stores GPIOs, optional regulator, extcon device, delayed work, IRQ, and VBUS regulator state. `int3496_do_usb_id()` is the role update worker. `int3496_thread_isr()` debounces ID changes. `int3496_set_vbus_boost()` wraps regulator enable/disable. ACPI GPIO mappings describe ID, VBUS, and mux GPIO indexes.

## Control flow
Probe installs ACPI GPIO mappings, allocates state and devm delayed work, gets the ID GPIO non-exclusively, maps it to an IRQ, optionally gets VBUS and mux GPIOs or a VBUS regulator, registers the extcon device, requests a shared threaded both-edge IRQ, queues and flushes initial ID processing, and stores driver data. The worker treats ID low as host, updates mux and VBUS controls accordingly, and synchronizes `EXTCON_USB_HOST`.

## State and persistence behavior
Runtime state is the last regulator enable state and GPIO outputs. No persistent storage is used.

## Dependencies and integration points
It depends on ACPI, GPIO descriptors, regulators, extcon, platform devices, IRQs, and delayed work. AXP288 can use this device's extcon state as its ID source.

## Risks and edge cases
Some ACPI tables incorrectly mark the IRQ GPIO output-only, so the mapping uses `ACPI_GPIO_QUIRK_NO_IO_RESTRICTION`. If neither VBUS GPIO nor regulator is available, VBUS cannot be driven but host state is still reported. Work is debounced by a fixed 50 ms. Shared IRQs require robust filtering by GPIO state.

## Test signals
Exercise ACPI GPIO mapping, host/peripheral ID transitions, mux and VBUS GPIO output levels, optional regulator enable/disable, initial state after probe, probe without optional controls, and IRQ debounce.
