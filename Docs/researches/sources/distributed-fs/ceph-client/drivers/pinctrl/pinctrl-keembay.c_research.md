# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-keembay.c

## Purpose
Implements the Intel Keem Bay SoC pinctrl, pinmux, pin configuration, GPIO, and GPIO IRQ controller. The driver exposes each SoC pin as a one-pin group, builds functions dynamically from the per-pin mux table, programs GPIO mode registers, and bridges up to eight parent interrupt sources into Linux GPIO IRQs.

## Important APIs, Types, and Functions
Key types are `struct keembay_pinctrl`, `struct keembay_mux_desc`, `struct keembay_gpio_irq`, and `struct keembay_pinfunction`. Registration flows through `keembay_pinctrl_probe`, `keembay_pinctrl_reg`, `keembay_build_groups`, `keembay_build_functions`, and `keembay_gpiochip_probe`. Runtime operations are implemented by `keembay_set_mux`, `keembay_request_gpio`, `keembay_pinconf_get`, `keembay_pinconf_set`, `keembay_gpio_get`, `keembay_gpio_set`, direction helpers, `keembay_gpio_irq_handler`, `keembay_gpio_irq_enable`, `keembay_gpio_irq_disable`, and `keembay_gpio_irq_set_type`.

## Control Flow and State
Probe maps two MMIO resources, initializes a raw spinlock, registers pinctrl, derives pin groups and function descriptors from `keembay_pins`, then registers a `gpio_chip` with chained IRQ parents discovered via `platform_get_irq_optional`. Pinmux writes the selected mux mode into `KEEMBAY_GPIO_MODE_SELECT_MASK`; pinconf read-modify-writes pull, drive strength, slew, and Schmitt bits in per-pin mode registers. GPIO values use grouped data registers for input, output, high, and low writes. IRQ state is split between hardware `INT_CFG` slots and software `kpc->irq[]`, `max_gpios_level_type`, and `max_gpios_edge_type`; falling/low trigger support is emulated by input inversion because the IP only supports rising/high semantics directly.

## Dependencies and Integration Points
Depends on Linux pinctrl generic group/function helpers, generic pinconf DT parsing, gpiolib, hierarchical/chained IRQ support, MMIO accessors, OF matching for `intel,keembay-pinctrl`, and platform IRQ/resource discovery. The GPIO range ties GPIO offsets back to the pin controller, and client DT nodes use the generated function/group names from the Keem Bay mux table.

## Risks and Test Signals
Important risks are slot accounting bugs across the eight IRQ sources, mishandling of low/falling emulation through inversion, read-modify-write races outside the raw spinlock, wrong `ngpios` values relative to the static pin table, and dynamic function grouping errors when the same function name appears on many pins. Test signals include pinmux state in debugfs, GPIO direction/value tests across 32-bit register boundaries, pull/drive/slew/Schmitt pinconf reads after writes, IRQ tests for rising/falling/high/low requests, and probe coverage with missing or partial parent IRQ resources.
