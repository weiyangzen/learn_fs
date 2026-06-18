# sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm8994.c

## Purpose
Exposes GPIO pins on Wolfson WM8994-family audio devices, including variant-specific request restrictions, direction/value operations, drive-mode pin configuration, IRQ mapping, and debugfs alternate-function reporting.

## Important APIs, Types, And Functions
- `struct wm8994_gpio` stores the parent `struct wm8994` and chip template copy.
- `wm8994_gpio_request` rejects unsupported WM8958 GPIO offsets.
- `wm8994_gpio_direction_in`, `wm8994_gpio_direction_out`, `wm8994_gpio_get`, and `wm8994_gpio_set` access per-pin `WM8994_GPIO_1 + offset` registers.
- `wm8994_gpio_set_config` supports open-drain and push-pull output configuration.
- `wm8994_gpio_to_irq` maps GPIO offsets through the parent's regmap IRQ data.
- `wm8994_gpio_dbg_show` decodes direction, pull, polarity, output type, and GPIO alternate function.

## Control Flow
Probe allocates private data, copies the template, sets `ngpio = WM8994_GPIO_MAX`, applies optional platform GPIO base, and registers a sleepable chip. Request checks reject unavailable WM8958 pins before consumers take them. Direction input sets `WM8994_GPN_DIR`; direction output writes direction and level bits together. Set updates only the level bit. Debugfs walks every pin and decodes the current control register.

## State And Persistence
No local GPIO shadow is kept. Per-pin WM8994 registers retain direction, level, pull, polarity, output configuration, and alternate-function state according to parent device lifetime.

## Dependencies And Integration Points
Depends on WM8994 MFD core, pdata, regmap IRQ support, GPIO and register definitions, gpiolib pinconf/debugfs hooks, and the platform driver `wm8994-gpio`.

## Risks And Edge Cases
Variant restrictions are hard-coded in `request`; unsupported WM8958 offsets must stay aligned with silicon capabilities. Debugfs reports alternate functions even for unrequested pins and must handle read failures. `wm8994_gpio_fn` labels `WM8994_GP_FN_FLL2_OUT` as "FLL1 output", which looks like a diagnostic string bug. IRQ mapping assumes parent regmap IRQ data is valid.

## Test Signals
Test WM8958 request rejection offsets, direction/value register bit updates, open-drain/push-pull pinconf, IRQ virq mapping, fixed/dynamic base handling, and debugfs alternate-function output including unsupported register read paths.
