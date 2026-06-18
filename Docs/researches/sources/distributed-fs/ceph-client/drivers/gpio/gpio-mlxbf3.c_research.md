# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf3.c

Purpose: supports NVIDIA BlueField-3 GPIO blocks with separate read, set, clear, output-enable, and interrupt-cause register regions, plus pinctrl range registration.

Important APIs/types/functions: `struct mlxbf3_gpio_context` stores one `gpio_generic_chip` and four mapped register windows: main GPIO, cause, set, and clear. GPIO is handled by `gpio_generic_chip_init()`. IRQ functions are `mlxbf3_gpio_irq_enable()`, `mlxbf3_gpio_irq_disable()`, `mlxbf3_gpio_irq_handler()`, `mlxbf3_gpio_irq_set_type()`, and a no-op ack required by `handle_edge_irq()`. `mlxbf3_gpio_add_pin_ranges()` maps block sizes to pinctrl device `MLNXBF34:00`.

Control flow: probe maps four resources, initializes a generic chip with data input from the main region, set/clear output registers, and output-enable set/clear registers for direction. It installs generic request/free and pin-range callbacks, optionally requests a shared IRQ and creates an internal domain-backed IRQ chip, stores drvdata, and registers the gpiochip. IRQ enable clears stale cause and sets event-enable. IRQ disable clears event-enable and pending cause. IRQ type sets rise/fall enable bits and switches the child handler to `handle_edge_irq`.

State and persistence behavior: output value/direction live in the firmware GPIO set/clear regions. Interrupt enable and pending state live in the cause region. No suspend/resume save path is present. Shutdown disables and clears all interrupts in the cause block.

Dependencies and integration points: depends on ACPI HID `MLNXBF33`, soft dependency on `pinctrl-mlxbf3`, generic MMIO GPIO helper, gpiolib IRQ helpers, and a platform IRQ if interrupt support is present. Pin ranges assume either a 32-line block or a 24-line second block.

Risks: `mlxbf3_gpio_add_pin_ranges()` infers block id from `chip->ngpio`; unexpected firmware `ngpios` values fail pin-range registration. IRQ type programming sets requested senses but does not clear unrequested opposite edges, so type changes can leave stale enable bits. There is no PM restore. Probe logs but returns the result from `devm_gpiochip_add_data()` even after `dev_err_probe()`, so error propagation is direct but the branch is terse.

Test signals: resource mapping order, 32-line and 24-line block pin ranges, generic value/direction operations through set/clear windows, IRQ enable/disable cause clearing, edge type programming, shared parent IRQ dispatch, and shutdown interrupt clearing.
