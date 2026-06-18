# sources/distributed-fs/ceph-client/drivers/bcma/driver_gpio.c

Purpose: this file registers a GPIO controller backed by BCMA ChipCommon GPIO registers and optionally wires it into the IRQ subsystem for SoC-hosted BCMA devices.

Important APIs, types, and functions: GPIO callbacks include `bcma_gpio_get_value`, `bcma_gpio_set_value`, `bcma_gpio_direction_input`, `bcma_gpio_direction_output`, `bcma_gpio_request`, and `bcma_gpio_free`. IRQ support includes `bcma_gpio_irq_unmask`, `bcma_gpio_irq_mask`, `bcma_gpio_irq_chip`, `bcma_gpio_irq_handler`, `bcma_gpio_irq_init`, and `bcma_gpio_irq_exit` when built for relevant SoCs. Exported integration functions are `bcma_gpio_init` and `bcma_gpio_unregister`.

Control flow: initialization fills `struct gpio_chip` callbacks, parent, fwnode, GPIO count based on chip ID, and base number policy. SoC/built-in configurations request the ChipCommon IRQ, clear interrupt masks, enable the ChipCommon GPIO interrupt bit, configure gpiochip IRQ metadata, and then register the gpiochip with `gpiochip_add_data`. GPIO request hands control to software, clears pulldown, and enables pullup. IRQ unmask samples current input and sets polarity so future edge-like changes are detected; handler computes `(input ^ polarity) & mask`, dispatches each set bit through the gpio IRQ domain, and updates polarity.

State and persistence: state is embedded in `cc->gpio` and hardware GPIO output, output-enable, control, pullup, pulldown, IRQ mask, and polarity registers. IRQ registration persists until unregister.

Dependencies and integration points: it integrates with gpiolib, optional gpiolib irqchip helpers, Linux IRQ handling, device firmware nodes, BCMA ChipCommon GPIO helpers, and SoC chip ID tables.

Risks: IRQ support is conditional and only meaningful for SoC hosts. The handler treats GPIO interrupts through polarity flipping; races around input changes and mask/polarity updates can lose or retrigger interrupts if hardware semantics differ. Absolute GPIO bases for SoC/built-in cases preserve legacy user-space expectations but can conflict if multiple controllers are misnumbered.

Test signals: gpiochip registration, line request/free, input/output toggling, pull configuration, and GPIO interrupt delivery validate behavior. Error-path tests should confirm IRQ is freed if gpiochip registration fails.
