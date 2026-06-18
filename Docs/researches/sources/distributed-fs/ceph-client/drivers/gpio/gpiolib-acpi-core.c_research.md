# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi-core.c

## Purpose
`gpiolib-acpi-core.c` is the ACPI integration layer for the GPIO subsystem. It translates ACPI `GpioIo` and `GpioInt` resources into Linux GPIO descriptors, installs ACPI GPIO operation-region handlers, maps ACPI GPIO interrupts to Linux IRQs, manages ACPI event methods (`_Exx`, `_Lxx`, `_EVT`), and exposes ACPI-specific helpers to consumer drivers.

## Important APIs, Types, And Functions
`struct acpi_gpio_event` stores one ACPI event GPIO, including ACPI method handle, pin, IRQ, IRQ flags, wake capability, request state, and the owned descriptor. `struct acpi_gpio_connection` caches descriptors used by GPIO OpRegions. `struct acpi_gpio_chip` is attached to the ACPI controller handle and owns event and OpRegion state. `struct acpi_gpio_info` carries parsed resource metadata back to descriptor lookup callers.

Public/exported entry points include `acpi_gpio_get_irq_resource()`, `acpi_gpio_get_io_resource()`, `acpi_gpiochip_request_interrupts()`, `acpi_gpiochip_free_interrupts()`, `acpi_dev_add_driver_gpios()`, `acpi_dev_remove_driver_gpios()`, `devm_acpi_dev_add_driver_gpios()`, `acpi_find_gpio()`, `acpi_dev_gpio_irq_wake_get_by()`, `acpi_gpiochip_add()`, `acpi_gpiochip_remove()`, and `acpi_gpio_count()`.

Key internal functions are `acpi_get_gpiod()`, `acpi_gpiochip_alloc_event()`, `acpi_gpio_adr_space_handler()`, `acpi_get_gpiod_by_index()`, `acpi_get_gpiod_from_data()`, `acpi_gpio_property_lookup()`, `acpi_gpio_resource_lookup()`, `acpi_gpio_to_gpiod_flags()`, and `acpi_request_own_gpiod()`.

## Control Flow
GPIO chip registration calls `acpi_gpiochip_add()`, which allocates `struct acpi_gpio_chip`, attaches it to the ACPI handle with `acpi_attach_data()`, installs the `ACPI_ADR_SPACE_GPIO` handler, and clears ACPI dependencies. Removal reverses this via `acpi_gpiochip_free_regions()`, `acpi_detach_data()`, and `kfree()`.

Consumer lookup starts in `acpi_find_gpio()`. It tries named `_DSD` GPIO properties using `for_each_gpio_property_name()`, falls back to driver-provided ACPI GPIO mappings if present, then optionally falls back to raw `_CRS` GPIO resources only when the device has no properties and the lookup has no connection ID. Resource walking fills `acpi_gpio_info`, resolves the controller path through `acpi_get_gpiod()`, converts ACPI polarity/pull/direction into gpiod and lookup flags, and applies debounce.

`acpi_gpiochip_request_interrupts()` walks `_AEI` resources. For each `GpioInt`, `acpi_gpiochip_alloc_event()` looks for `_Exx` or `_Lxx` event methods, or `_EVT`, applies interrupt/wake ignore quirks, requests an owned descriptor, locks it as IRQ, resolves `gpiod_to_irq()`, derives IRQ trigger flags, and appends it to the chip event list. Actual `request_threaded_irq()` may be deferred through the ACPI quirks deferred list.

`acpi_gpio_adr_space_handler()` services ACPI OpRegion reads and writes by decoding the connection resource, looking up or caching descriptors per pin under `conn_lock`, borrowing shared event descriptors for read-only shared pins, and using raw GPIO value access to update the ACPI value words.

## State And Persistence
State is kernel-resident and tied to GPIO chip lifetime. `struct acpi_gpio_chip` is attached as ACPI handle data. Event descriptors and OpRegion cached connections live in lists under that object. IRQ wake enablement and requested state are explicit so cleanup can disable wake, free IRQs, unlock IRQ ownership, free owned descriptors, and free event nodes. Driver GPIO mappings are stored on `adev->driver_gpios` until removed or devres cleanup runs.

## Dependencies And Integration Points
This file depends on ACPICA resource walking and address-space handlers, gpiolib descriptor APIs, GPIO chip registration, Linux IRQ APIs, pinctrl-related GPIO configuration, DMI/quirk helpers from `gpiolib-acpi-quirks.c`, and firmware-node property naming helpers. It integrates with consumer APIs through `acpi_find_gpio()` and `acpi_gpio_count()`, with ACPI interrupt users through `acpi_dev_gpio_irq_wake_get_by()`, and with gpiochip lifecycle through `acpi_gpiochip_add/remove()` plus interrupt request/free hooks.

## Risks
Firmware description errors are the main risk: wrong polarity, wake flags, debounce units, resource indices, or missing controller registration can lead to incorrect direction, deferred probe, or unusable interrupts. Event handlers intentionally execute ACPI methods from IRQ thread context, so ordering with OpRegion registration matters. OpRegion descriptor caching must be cleaned exactly once. The code has explicit FIXME comments about descriptor lifetime after putting GPIO device references, which is a long-standing reference model concern.

## Test Signals
Useful tests include ACPI `_DSD` and `_CRS` GPIO lookup on named and unnamed consumers, deferred GPIO controller probe returning `-EPROBE_DEFER`, `GpioInt` IRQ translation and trigger type setup, wake-capable IRQ handling under low-power S0, boot-time `_AEI` event execution toggled by quirks, OpRegion read/write AML tests, debounce conversion from ACPI units, and cleanup paths during gpiochip unregister.
