
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-exar.c

Purpose: exposes Exar XR17V35x UART MPIO pins as GPIOs through a platform child of a PCI UART driver.

Important APIs/types/functions: `struct exar_gpio_chip` stores gpiochip, MMIO regmap, IDA index/name, first pin, and optional cascaded-device register offset. Important functions are `exar_offset_to_sel_addr()`, `exar_offset_to_lvl_addr()`, `exar_get_direction()`, `exar_get_value()`, `exar_set_value()`, `exar_direction_output()`, `exar_direction_input()`, and `gpio_exar_probe()`.

Control flow: probe gets the parent PCI device's already-mapped BAR0, reads `exar,first-pin` and `ngpios`, doubles `ngpios` and computes a cascaded register offset for cascaded device IDs, creates an MMIO regmap, allocates a unique gpiochip label using IDA, fills callbacks, and registers the chip. Direction is controlled by MPIOSEL bits; level is read/written through MPIOLVL registers. Output direction writes the requested level before clearing the select bit to output.

State and persistence behavior: hardware registers hold direction and value. The IDA index is freed by a devm action. There is no IRQ support, PM context, or software value cache.

Dependencies and integration points: depends on the Exar UART parent having mapped BAR0 with `pcim_iomap_table()`, platform device properties, regmap MMIO, PCI core, gpiolib, and IDA allocation.

Risks: parent driver ordering is required; without mapped BAR0 probe fails. Cascaded detection interprets PCI device-id bitfields, so new variants may need updates. The driver assumes regmap MMIO operations cannot fail after initialization.

Test signals: platform child probe under Exar PCI UART, first-pin and ngpios property validation, cascaded ID behavior, direction/value operations across low/high and cascaded registers, IDA label allocation/free, and regmap initialization.
