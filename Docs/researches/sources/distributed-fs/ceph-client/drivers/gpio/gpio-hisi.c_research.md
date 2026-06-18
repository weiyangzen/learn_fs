<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-hisi.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-hisi.c

## Purpose
`gpio-hisi.c` registers a HiSilicon/Ascend GPIO controller as a gpiolib chip backed by a memory-mapped register bank. It uses the generic GPIO helper for data, set, clear, and direction operations, then layers debounce and optional cascaded interrupt support on top.

## Important APIs, types, and functions
The main state is `struct hisi_gpio`, which embeds `struct gpio_generic_chip`, the MMIO base, `line_num`, and one parent IRQ. `hisi_gpio_read_reg()`/`hisi_gpio_write_reg()` are the low-level MMIO helpers. `hisi_gpio_set_config()` supports `PIN_CONFIG_INPUT_DEBOUNCE`. IRQ operations are `hisi_gpio_set_ack()`, mask/unmask, type selection, enable/disable, and `hisi_gpio_irq_handler()`. Probe uses `gpio_generic_chip_init()` and `devm_gpiochip_add_data()`.

## Control flow
Probe requires exactly one firmware child node, maps resource 0, reads the child `ngpios`, fetches the matching platform IRQ, initializes a generic chip using the controller's set/clear direction registers, sets dynamic base and line count, installs an irqchip when an IRQ is present, and registers the chip. The chained parent handler reads `INTSTATUS`, iterates active bits, and dispatches child IRQs through the GPIO IRQ domain.

## State and persistence behavior
Driver state is runtime-only and device-managed. Hardware holds output level, direction, debounce, interrupt mask, enable, polarity, type, and dual-edge bits. No software shadow is kept for normal GPIO levels. Firmware `ngpios` bounds the exported lines; the code clamps anything above 32.

## Dependencies and integration points
This integrates with ACPI `HISI0184`, OF compatible `hisilicon,ascend910-gpio`, `gpio-generic`, gpiolib irqchip helpers, chained IRQ handling, and pinconf debounce users. It depends on firmware child nodes for port metadata.

## Risks and edge cases
The probe rejects anything other than one port, so firmware describing multiple ports will fail. Dual-edge configuration has priority over other type registers and must be explicitly cleared when changing to non-both-edge types. `platform_get_irq()` returning 0 or negative disables or skips IRQ setup depending on value, so firmware IRQ numbering bugs can silently remove interrupt support.

## Test signals
Useful signals are probe on ACPI and DT systems, libgpiod line get/set/direction tests, debounce pinconf tests, IRQ type tests for all supported trigger modes including edge-both reconfiguration, and interrupt storm tests verifying EOI/mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-hisi.c -->
