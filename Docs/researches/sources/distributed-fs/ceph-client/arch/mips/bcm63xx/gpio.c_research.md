# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/gpio.c

Purpose: implements the BCM63xx GPIO controller as a Linux `gpio_chip`.

Important APIs and functions: `bcm63xx_gpio_init()` initializes CPU-specific direction defaults and registers the chip. `bcm63xx_gpio_set()`, `bcm63xx_gpio_get()`, and direction callbacks update GPIO data/direction registers under a spinlock. `bcm63xx_gpio_out_low_reg_init()` handles CPUs with split output-low registers.

Control flow: platform setup initializes the controller before board devices request LEDs or reset GPIOs. Generic GPIO consumers call the chip callbacks.

State and persistence: GPIO direction and output bits are hardware runtime state only.

Dependencies and integration points: integrates with Linux gpiolib, BCM63xx CPU/register helpers, LED devices, board reset GPIOs, and any platform consumer using GPIO numbers.

Risks and test signals: wrong register split or direction handling affects every GPIO consumer. Test LEDs, reset pins, input buttons where present, and gpiolib debugfs/state inspection.
