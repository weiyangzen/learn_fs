<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-nomadik.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-nomadik.c

## Purpose
GPIO and IRQ driver for Nomadik/STA2X11 GPIO banks and the reduced Mobileye EyeQ5 variant. It manages up to 32 lines per bank, alternate-function sharing with pinctrl, edge IRQs, wake masks, sleep-mode policy, and debug output.

## Important APIs, types, and functions
State is `struct nmk_gpio_chip` from `gpio-nomadik.h`, populated by `nmk_gpio_populate_chip()`. GPIO callbacks include `nmk_gpio_get_dir()`, `nmk_gpio_make_input()`, `nmk_gpio_get_input()`, `nmk_gpio_make_output()`, and `nmk_gpio_set_output()`. IRQ paths include `nmk_gpio_irq_ack()`, `nmk_gpio_irq_maskunmask()`, `nmk_gpio_irq_set_type()`, `nmk_gpio_irq_set_wake()`, startup/shutdown, and `nmk_gpio_irq_handler()`.

## Control flow
Population finds the platform device by fwnode, reads `gpio-bank` and `ngpios`, maps registers, prepares the optional clock, and deasserts reset. Probe wires GPIO and IRQ callbacks, requests the shared parent IRQ, and registers the chip. GPIO operations enable the clock around register access. IRQ type changes temporarily disable normal/wake masks, update cached rising/falling edge bits, then reapply masks.

## State and persistence behavior
Cached state includes rising/falling edge masks, normal and wake masks, real wake requests, low-EMI value, bank id, sleepmode support, and Mobileye compatibility. Mobileye skips sleep, wake, and alternate-function registers. There is no normal remove path.

## Dependencies and integration points
Uses platform/fwnode lookup, clocks, reset controls, gpiolib, IRQ domains, and optionally `pinctrl-nomadik`. Registered at subsystem init for early consumers.

## Risks and edge cases
Shared sleep-mode locking must coordinate with pinctrl. Clock enable failures are not checked. Mobileye paths rely on WARN guards to avoid unsupported register writes. The resource ownership model is unusual because GPIO and pinctrl may both populate the shared chip.

## Test signals
Probe for both compatibles, direction/value operations, rising/falling/both IRQ delivery, wake behavior, Mobileye unsupported-register avoidance, and debugfs output with pinctrl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-nomadik.c -->
