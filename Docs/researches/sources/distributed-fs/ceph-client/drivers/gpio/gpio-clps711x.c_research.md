
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-clps711x.c

Purpose: implements Cirrus Logic CLPS711X/EP7209 GPIO banks using the generic MMIO GPIO helper.

Important APIs/types/functions: the file is centered on `clps711x_gpio_probe()`, with `struct gpio_generic_chip_config` and `struct gpio_generic_chip` carrying almost all behavior. The OF match table accepts `cirrus,ep7209-gpio`.

Control flow: probe requires an OF node and uses the `gpio` alias id to identify the bank. It maps two resources, one data and one direction register, initializes a one-byte generic GPIO chip, handles Port D's inverted direction semantics by using `dirin`, and sets Port E to three lines. It then assigns dynamic base/owner and registers the chip.

State and persistence behavior: no private runtime state exists after registration. Hardware data and direction registers are accessed through generic-chip callbacks. The only persistent configuration is bank id from OF alias and the generated gpiochip fields.

Dependencies and integration points: depends on OF aliases, platform resources, and `gpio_generic_chip_init()`. The driver assumes platform data/DT describes each port as a separate device with two MMIO resources.

Risks: invalid or missing alias ids reject probe, so DT alias numbering is part of the ABI. Direction polarity differs for Port D, making bank id correctness critical. No IRQ, pinctrl, or PM state is implemented.

Test signals: DT probe for aliases 0-4, Port D direction polarity, Port E exposing exactly three GPIOs, generic get/set/direction behavior, and failure for missing OF node or bad alias id.
