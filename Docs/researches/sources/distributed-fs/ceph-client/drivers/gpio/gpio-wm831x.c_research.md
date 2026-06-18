# sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm831x.c

## Purpose
Exposes Wolfson WM831x PMIC GPIO pins through gpiolib, including direction/value operations, IRQ mapping, drive-mode pin configuration, debounce selection, and debugfs register reporting.

## Important APIs, Types, And Functions
- `struct wm831x_gpio` stores the parent `struct wm831x` and chip template copy.
- `wm831x_gpio_direction_in`, `wm831x_gpio_direction_out`, `wm831x_gpio_get`, and `wm831x_gpio_set` operate on `WM831X_GPIO1_CONTROL + offset` and `WM831X_GPIO_LEVEL`.
- `wm831x_gpio_to_irq` maps GPIO offsets through the parent IRQ domain.
- `wm831x_gpio_set_debounce` maps requested debounce intervals to GPIO function bits after checking the pin is in GPIO-capable mode.
- `wm831x_set_config` supports open-drain, push-pull, and input debounce pinconf.
- `wm831x_gpio_dbg_show` decodes pull, power-domain, polarity, drive, tristate, and level information.

## Control Flow
Probe inherits the parent fwnode, allocates private state, copies a static chip template, fills `ngpio` and base from parent data/platform data, and registers a sleepable chip. Direction input and output set direction, tristate, and function mask bits according to WM831x semantics; output direction then writes the requested level. Pinconf calls update either open-drain bits or debounce/function selection.

## State And Persistence
The driver keeps no shadowed GPIO state. Parent PMIC registers store levels, control mode, pull configuration, function selection, and IRQ domain mappings. Platform data can persist a legacy fixed GPIO base choice into chip registration.

## Dependencies And Integration Points
Depends on WM831x MFD core, WM831x GPIO/IRQ register definitions, parent IRQ domain, optional platform data, and gpiolib pinconf/debugfs hooks. Registered by `subsys_initcall` as `wm831x-gpio`.

## Risks And Edge Cases
Debounce support is encoded through function bits and only accepts broad 32-64 us or 4-8 ms ranges; other values fail. Pins not in GPIO-capable function modes return `-EBUSY` for debounce. `has_gpio_ena` inverts tristate interpretation, so direction handling differs by chip variant. Debugfs reads all pins including unrequested lines and can emit partial output on register errors.

## Test Signals
Check direction/value operations for multiple offsets, IRQ mapping from `WM831X_IRQ_GPIO_1`, fixed vs dynamic base, open-drain/push-pull pinconf, accepted and rejected debounce values, `has_gpio_ena` variants, and debugfs decoding of pull/power-domain/function fields.
