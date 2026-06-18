# sources/distributed-fs/ceph-client/drivers/input/misc/soc_button_array.c

## Purpose
`soc_button_array.c` converts Windows-compatible ACPI SoC tablet button descriptors into one or two `gpio-keys` platform devices. It supports fixed ACPI IDs, dynamic ACPI0011 `_DSD` HID-style descriptors, DMI quirks, and separate autorepeat/non-autorepeat groups.

## Important APIs, Types, and Functions
`struct soc_button_info` describes one button's name, ACPI GPIO index, event type/code, autorepeat, wakeup, and polarity. `struct soc_device_data` binds fixed button tables and optional device checks. `soc_button_lookup_gpio()` resolves ACPI-indexed GPIO and IRQ. `soc_button_device_create()` builds `gpio_keys_platform_data` and registers a `gpio-keys` child. `soc_button_get_button_info()` parses ACPI0011 `_DSD` button descriptors. `soc_device_check_MSHW0040()` filters Microsoft Surface generations via `_DSM`.

## Control Flow
Probe obtains match data, runs an optional check, chooses a fixed button table or parses ACPI0011 `_DSD`, verifies GPIO resources exist, then attempts to create two `gpio-keys` children: one for autorepeat and one for non-autorepeat. Creation counts buttons in the requested class, skips DMI-invalid ACPI indexes, resolves each GPIO/IRQ, applies low-level IRQ quirk handling when requested or DMI-matched, fills `gpio_keys_button` records, and registers a child platform device. Remove unregisters all children.

## State and Persistence Behavior
Persistent state is `struct soc_button_data` holding child platform devices. Child `gpio-keys` devices own input state, debounce, IRQ configuration, and wakeup behavior. Dynamically parsed ACPI button info is devm-allocated and freed after child creation. Module parameter `use_low_level_irq` persists for the module lifetime.

## Dependencies and Integration Points
The driver depends on ACPI, DMI, gpiolib, legacy GPIO numbers, IRQ configuration, `gpio-keys`, platform devices, and input event definitions. ACPI IDs include `PNP0C40`, `INT33D3`, `ID9001`, `ACPI0011`, `MSHW0028`, and `MSHW0040`. It integrates indirectly with userspace through the `gpio-keys` input devices it creates.

## Risks and Edge Cases
The low-level IRQ quirk deliberately bypasses `gpio_keys_button.gpio` and programs IRQ type to work around AML that mutates GPIO controller registers; wrong DMI matching can cause stuck IRQs or nonfunctional buttons. `-EPROBE_DEFER` from GPIO lookup is intentionally ignored for virtual GPIO resources, which can also hide real deferral needs. Dynamic `_DSD` parsing accepts only known HID usage combinations and turns unknowns into reserved keys. The platform data is allocated with devm but passed to a child device by copy size only for the base struct, relying on child registration semantics.

## Test Signals
Test fixed ACPI IDs, ACPI0011 descriptor parsing, Surface MSHW0040 `_DSM` filtering, DMI low-level IRQ systems, invalid ACPI index DMI skip, GPIO lookup failures including defer, autorepeat split into two children, wakeup flags, switch events for tablet/rotation/rfkill, and removal unregistering children.
