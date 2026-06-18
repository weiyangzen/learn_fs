# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-nsp-gpio.c

Purpose: Broadcom Northstar Plus chipCommonA GPIO driver with optional GPIO IRQ support and a local pinctrl device for GPIO-only pinconf settings.

Important APIs/types/functions: `struct nsp_gpio` carries MMIO bases, `gpio_chip`, pinctrl descriptor, and `raw_spinlock_t`. GPIO callbacks include `nsp_gpio_direction_input/output`, `nsp_gpio_get_direction`, `nsp_gpio_get`, and `nsp_gpio_set`. IRQ callbacks are bundled in immutable `nsp_gpio_irq_chip`. Pinconf callbacks support bias, drive strength, and slew through `nsp_pin_config_get/set()`.

Control flow: probe requires `ngpios`, maps GPIO and IO-control resources, initializes the gpiochip, optionally enables the shared parent interrupt and installs `nsp_gpio_irq_handler()`, registers the gpiochip, then registers a one-to-one pinctrl device. The IRQ handler checks chipCommonA status, combines level and edge sources, and dispatches set bits through the gpio IRQ domain.

State and persistence: output enable/data, interrupt masks/polarity/events, pull, slew, and drive strength live in MMIO registers. Driver state is devm-managed and protected by raw spinlocks for GPIO/IRQ paths. Drive strength is encoded across three adjacent IO-control registers.

Dependencies/integration: uses gpiolib, irqdomain/generic IRQ handling, platform OF (`brcm,nsp-gpio-a`), generic pinconf parsing, and pinctrl range helpers. It pairs with the NSP mux driver because pins must be muxed to GPIO before GPIO pinconf is meaningful.

Risks: only one GPIO group is exposed, so group pinconf get/set are stubs. Invalid drive strengths outside even 2-16 mA return `-ENOTSUPP`. Edge interrupt ack only clears event IRQs, while level IRQ behavior relies on input level/polarity and masking. Missing `ngpios` fails probe.

Test signals: exercise libgpiod direction/value paths, configure pull and drive strength from DT, trigger rising/falling/high/low IRQs, verify shared IRQ returns `IRQ_NONE` with no pending bits, and confirm pinctrl debugfs shows the local `gpio_grp`.
