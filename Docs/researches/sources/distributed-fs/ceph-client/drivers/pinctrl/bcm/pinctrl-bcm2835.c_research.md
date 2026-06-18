<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm2835.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm2835.c

## Purpose
This file implements the combined pinctrl, pinmux, pinconf, GPIO, and GPIO interrupt controller driver for Broadcom BCM2835-family GPIO blocks, including BCM2835, BCM2711, and BCM7211-compatible variants. It exposes every GPIO as a one-pin pinctrl group, maps the hardware function-select values to pinmux functions, handles legacy Raspberry Pi `brcm,pins`/`brcm,function`/`brcm,pull` device-tree bindings as well as generic pinconf bindings, and registers a `gpio_chip` with an irqchip for edge and level GPIO interrupts.

## Important APIs, Types, And Functions
`struct bcm2835_pinctrl` is the central state object. It stores the MMIO base, copied `gpio_chip`, copied `pinctrl_desc`, GPIO range, pinctrl device, optional BCM7211 wake IRQ array, enabled IRQ bitmaps, per-pin IRQ type state, raw IRQ bank locks, and a function-select spinlock.

The hardware accessors are `bcm2835_gpio_rd()`, `bcm2835_gpio_wr()`, `bcm2835_gpio_get_bit()`, `bcm2835_gpio_set_bit()`, `bcm2835_pinctrl_fsel_get()`, and `bcm2835_pinctrl_fsel_set()`. GPIO callbacks include direction, get/set, and get-direction helpers. IRQ callbacks include `bcm2835_gpio_irq_handler()`, `bcm2835_gpio_irq_handle_bank()`, mask/unmask, ack, set-type, and set-wake. Pinctrl and pinmux callbacks are `bcm2835_pctl_*` and `bcm2835_pmx_*`; pinconf callbacks are split between legacy BCM2835 pull programming and BCM2711 pull register programming.

## Control Flow
Probe maps MMIO, selects platform data by OF compatible, initializes locks, clears all event detection enables and latched event bits, registers pinctrl, adds the GPIO range, wires a three-parent hierarchical GPIO irqchip, optionally requests BCM7211 wake IRQs, and finally registers the GPIO chip. Pin requests and DT states then flow through pinctrl: device-tree nodes are translated into mux and config maps, `set_mux` writes the function-select field, pinconf writes pull or level settings, and GPIO requests use generic gpiochip request/free.

For GPIO interrupts, each parent IRQ is chained to the same handler. The handler identifies which parent fired, splits it into hardware GPIO ranges, filters GPEDS status by `enabled_irq_map`, and dispatches each pending line through `generic_handle_domain_irq()`. Type changes update the per-pin `irq_type` array and enable/disable the corresponding rising, falling, high, or low detect register bits.

## State And Persistence
The driver persists software IRQ enable and type state in memory; the hardware persists function-select, output level, pull configuration, and event-detect bits until changed or reset. Probe intentionally clears interrupt detection and pending events. `persist_gpio_outputs` is a module parameter that prevents pinmux free from reverting GPIO outputs to inputs, preserving output drive across pin release. BCM2711 pull settings are readable and stored in dedicated pull registers; BCM2835 pull state cannot be read back.

## Dependencies And Integration Points
The file integrates with Linux pinctrl, pinmux, pinconf-generic, gpiolib, gpio irqchip helpers, OF address/IRQ parsing, and DT binding constants from `dt-bindings/pinctrl/bcm2835.h`. GPIO consumers use the registered `gpio_chip`; peripheral drivers consume pinctrl states through generic or legacy Raspberry Pi bindings.

## Risks
Function-select writes are register-wide read/modify/write operations, so `fsel_lock` is critical. Interrupt type changes are sensitive because edge-both reconfiguration intentionally toggles one detect source at a time. BCM2835 pull programming uses timing delays and a clock-strobe sequence; incorrect ordering can silently misconfigure pulls. The IRQ parent grouping is hard-coded for GPIO ranges 0-27, 28-45, and 46-57, so SoC-compatible data and `ngpio` must stay aligned. Legacy DT parser allocation/unwind must free per-pin config arrays correctly.

## Test Signals
Useful checks are pinctrl state application for generic and legacy DT nodes, GPIO input/output reads and writes, pin release with and without `persist_gpio_outputs`, BCM2711 pull readback, GPIO IRQ rising/falling/both/level behavior across all three parent ranges, wake IRQ enable on BCM7211, and boot logs showing successful pinctrl and GPIO chip registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm2835.c -->
