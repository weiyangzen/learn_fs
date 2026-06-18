<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-iproc-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-iproc-gpio.c

## Purpose
This file implements Broadcom iProc GPIO controllers with optional GPIO IRQ support and a local pinconf provider for pull-up/down and drive-strength settings. It supports generic iProc, Cygnus CCM/ASIU/CRMU, NSP, and Stingray-compatible GPIO blocks.

## Important APIs, Types, And Functions
`struct iproc_gpio` stores MMIO bases, optional external IO-control base, IO-control type, raw spinlock, gpiochip, bank count, pinmux support flag, disabled pinconf parameters, and local pinctrl descriptor/device. GPIO callbacks are `iproc_gpio_request()`, `iproc_gpio_free()`, direction, get/set, and get-direction. IRQ paths include `iproc_gpio_irq_handler()`, ack, mask/unmask, and `iproc_gpio_irq_set_type()`. Pinconf paths include `iproc_gpio_set_pull()`, `iproc_gpio_get_pull()`, drive-strength get/set helpers, and `iproc_pin_config_get()/set()`.

## Control Flow
The driver is registered by `arch_initcall_sync()`. Probe maps the GPIO MMIO resource and optional IO-control resource, reads `ngpios`, configures the gpiochip, detects whether GPIO pinmux requests are supported through `gpio-ranges`, optionally wires a chained parent IRQ, registers the gpiochip, and unless disabled creates a local pinctrl device with one pin per GPIO for pinconf. NSP disables drive-strength pinconf; Stingray disables pinconf entirely.

## State And Persistence
Software state includes the spinlock-protected chip object, disabled pinconf list, bank count, and optional local pinctrl registration. Hardware persists data in/out, output enable, IRQ type/dual-edge/edge/mask/status registers, pull registers, resistor enable/pad resistance registers, and drive-strength control registers. Interrupt state is not mirrored in software beyond gpiolib irqchip state.

## Dependencies And Integration Points
Depends on gpiolib, GPIO irqchip helpers, pinctrl consumer APIs for `pinctrl_gpio_request/free`, pinconf-generic, OF platform data, and `gpio-ranges` integration with SoC IOMUX drivers such as Cygnus. GPIO consumers use this as a normal `gpio_chip`; pinconf consumers use the local pinctrl provider.

## Risks
IRQ handling iterates all banks and clears each interrupt before dispatch, which is intentional but sensitive for level interrupts. Drive-strength encoding differs for AON, CDRU, and ASIU controllers through `DRV_STRENGTH_OFFSET()`. Pinconf disable masks must match hardware capabilities. Probe removes the gpiochip on pinconf registration failure, so ordering and error paths matter.

## Test Signals
Test GPIO input/output across multiple banks, optional parent IRQ handling for rising/falling/both/high/low, pull-up/down/disable on CDRU and non-CDRU controllers, drive strengths from 2 to 16 mA, NSP drive-strength rejection, Stingray no-pinconf behavior, and `gpio-ranges` pinmux requests into the owning IOMUX controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-iproc-gpio.c -->
