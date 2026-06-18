# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pistachio.c

## Purpose
This driver provides pinctrl, pinmux, pinconf, GPIO, and GPIO IRQ support for the Imagination Pistachio SoC system pin controller. It covers 90 MFIO pins plus special non-GPIO pins, maps multiplexed peripheral/debug/scenario functions, exposes electrical pad controls, and registers six GPIO banks as child gpiochips.

## Important APIs, Types, And Functions
`struct pistachio_pinctrl` stores the system pinctrl MMIO base, pinctrl device, static pin/function/group tables, and GPIO bank table. `struct pistachio_function` describes a function's legal groups and optional scenario selector metadata. `struct pistachio_pin_group` describes one pin, up to three mux options, and the function-select register field. `struct pistachio_gpio_bank` stores per-bank base, pin range, gpiochip, and backpointer.

The pinmux path is `pistachio_pinmux_enable()`, which writes function-select fields and optional scenario fields, then disables GPIO mode for that pin. Pinconf is handled by `pistachio_pinconf_get()` and `pistachio_pinconf_set()` for Schmitt trigger, high-Z, pull-up/down, bus hold, slew rate, and 2/4/8/12 mA drive strength. GPIO helpers include `gpio_mask_writel()`, `gpio_enable()`, `gpio_disable()`, and gpiochip callbacks for direction, get, set, and get_direction. IRQ support is implemented by `pistachio_gpio_irq_set_type()`, ack/mask/unmask/startup callbacks, and `pistachio_gpio_irq_handler()`.

## Control Flow
Probe allocates controller state, maps one MMIO resource, assigns static tables, registers pinctrl, and then calls `pistachio_gpio_register()`. GPIO registration iterates expected child nodes named `gpio0` through `gpio5`, requires each to have `gpio-controller`, obtains its IRQ, initializes the bank base at `GPIO_BANK_BASE(i)`, attaches a fwnode-aware gpiochip and immutable irqchip, adds the gpiochip, and adds a pin range linking bank GPIO offsets back to pinctrl pins. On failure, already-added gpiochips are removed manually.

Pinctrl group and function enumeration directly reflect the static arrays. For muxable MFIO groups, `pistachio_pinmux_enable()` finds which of the group's three mux slots matches the selected function, updates the correct function-select field, and for functions with scenario lists updates `PADS_SCENARIO_SELECT` to the index of the selected group in that scenario list. After muxing, it finds any GPIO range covering the pin and disables GPIO bit-enable for the bank offset so the peripheral function owns the pad.

GPIO registers use a masked write convention: bit `16 + offset` authorizes writing bit `offset`, implemented by `gpio_mask_writel()`. Direction input clears OUTPUT_EN and enables the GPIO bit; output writes the value, sets OUTPUT_EN, and enables the bit. IRQ type programming supports rising, falling, both-edge, level-high, and level-low by configuring polarity, edge/level mode, and single/dual edge registers. The chained handler dispatches enabled interrupt-status bits for up to 16 pins per bank.

## State And Persistence
Runtime software state is stored in the controller object and the static mutable `pistachio_gpio_banks[]` entries initialized during probe. Hardware state includes pad pull/drive/slew/Schmitt registers, mux function-select and scenario registers, GPIO enable/output/direction, and interrupt configuration/status. There is no persistent storage and no remove callback; probe failure after gpiochip registration is cleaned manually, while successful registration relies on platform lifetime.

## Dependencies And Integration Points
The driver depends on platform MMIO, firmware child nodes, OF/property APIs, pinctrl/pinmux/pinconf core, gpiochip and gpio-irqchip APIs, IRQ handling, `pinctrl-utils`, and standard pinconf generic properties. It binds to `img,pistachio-system-pinctrl`. GPIO consumers use child gpio-controller nodes; pinctrl consumers use the parent pinctrl device and named groups/functions.

## Risks And Test Signals
GPIO bank registration is not devm-managed after success, and there is no remove path, which is acceptable for built-in arch-init registration but risky for hot-unbind assumptions. The static GPIO bank array is mutable global state and would not support multiple controller instances cleanly. `gpio_mask_writel()` depends on the hardware masked-write convention; any register that does not follow it would be corrupted. Mux/scenario validation is table-driven, so wrong scenario arrays can program the wrong scenario index. Pinconf read-modify-write paths have no explicit locking.

Useful tests include probe with all six child GPIO nodes, failure cleanup when a child node or IRQ is missing, muxing plain fixed MFIO groups and three-option mux groups, scenario functions such as `spdif_in` and MIPS trace variants, GPIO enable/disable interaction when switching between GPIO and peripheral mux, all supported pinconf properties and drive strengths, GPIO IRQ rising/falling/both/level modes, and bank 5 behavior with only 10 pins.
