# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pic32.c

## Purpose
This driver supports Microchip PIC32MZ DA pin control and GPIO. It exposes Peripheral Pin Select input/output muxing, analog/digital mode selection, pull-up/down, open-drain, GPIO direction/value, and change-notification GPIO interrupts. Pinctrl and GPIO banks are registered as separate platform drivers that share static bank metadata.

## Important APIs, Types, And Functions
`struct pic32_pinctrl` stores the PPS MMIO base, clock, pinctrl device, pin/function/group tables, and shared GPIO bank table. `struct pic32_gpio_bank` stores one bank's MMIO base, instance number, gpiochip, and clock. `struct pic32_function`, `struct pic32_pin_group`, and `struct pic32_desc_function` describe which named peripheral functions can be muxed onto each remappable pin and what PPS register/value pair must be written.

The pinmux path is `pic32_pinmux_enable()`, which scans the selected group's function descriptors and writes the PPS mux register. GPIO and pinmux integration uses `pic32_gpio_request_enable()` to clear analog mode, `pic32_gpio_set_direction()`, and the gpiochip callbacks. Pinconf is provided by `pic32_pinconf_get()` and `pic32_pinconf_set()`, including custom generic parameters `microchip,digital` and `microchip,analog`. IRQ support is implemented by `pic32_gpio_irq_set_type()`, `pic32_gpio_irq_ack()`, `pic32_gpio_irq_mask()`, `pic32_gpio_irq_unmask()`, `pic32_gpio_get_pending()`, and `pic32_gpio_irq_handler()`.

## Control Flow
`pic32_pinctrl_probe()` maps the PPS register resource, enables the clock, assigns static pin/function/group arrays, fills `pic32_pinctrl_desc` including custom pinconf parameters, and registers pinctrl. `pic32_gpio_probe()` reads the `microchip,gpio-bank` property, selects a static bank, maps that bank's PORT register resource, gets its IRQ and clock, configures the gpiochip parent, attaches an immutable irqchip with a chained parent handler, and registers the gpiochip with devm. Both platform drivers are registered at `arch_initcall`.

When a pinctrl mux state is applied, the driver looks up the selected function name inside the selected group's descriptor list and writes `muxval` to `pctl->reg_base + muxreg`. GPIO requests clear the selected bank's ANSEL bit through PIC32's SET/CLR alias register scheme. GPIO direction uses TRIS set for input and clear for output, while values use PORT set/clear aliases. Pinconf reads and writes manipulate CNPU, CNPD, ANSEL, ODCU, TRIS, and output level through the bank registers.

GPIO IRQ setup only accepts edge rising, falling, or both. It configures CNEN for rising, CNNE for falling, sets the CNCON edge bit, and switches the child handler to `handle_edge_irq`. The chained parent handler reads CNF status, filters it through enabled rising/falling registers, and dispatches pending child IRQs. Masking clears CNCON ON for the whole bank; unmasking sets it again.

## State And Persistence
Software state is mostly static tables and per-device pointers. The `pic32_gpio_banks[]` array is global and shared between the pinctrl and GPIO platform devices; each GPIO probe fills MMIO, clock, parent, and irqchip fields for one bank. Hardware state persists in PPS and PORT registers until reset or later writes. No software cache tracks mux or pinconf values.

## Dependencies And Integration Points
The driver depends on platform MMIO resources, clocks, OF platform devices, pinctrl/pinmux/pinconf core, gpiochip and gpio-irqchip APIs, `pinctrl-utils`, and PIC32 SET/CLR alias macros from `linux/platform_data/pic32.h`. `pinctrl-pic32.h` supplies PPS and PORT register offsets. Device tree compatibles are `microchip,pic32mzda-pinctrl` and `microchip,pic32mzda-gpio`, with GPIO bank identity carried by `microchip,gpio-bank`.

## Risks And Test Signals
The shared static `pic32_gpio_banks[]` means repeated probes, partial probe failures, or multiple SoC instances would reuse mutable bank state. `pic32_gpio_get_pending()` appears to use `(mask && cnne_fall)` instead of `(mask & cnne_fall)`, which can report falling-enabled status incorrectly whenever any CNNE bit is set. `pic32_gpio_irq_ack()` writes zero to CNF rather than a bit mask or clear alias, which should be checked against hardware semantics. IRQ mask/unmask toggles CNCON ON for the whole bank, so masking one child IRQ can affect sibling GPIO interrupts. The driver includes `spinlock.h` but uses no explicit locking around read-modify-write pinconf paths.

Useful tests include PPS muxing for representative input and output functions, GPIO request clearing analog mode, custom `microchip,digital`/`analog` pinconf parsing, pull-up/down/open-drain/direction/value behavior per bank, GPIO IRQ rising/falling/both-edge delivery, sibling IRQ behavior when one child is masked, invalid bank property handling, and build tests that catch descriptor/register-offset drift.
