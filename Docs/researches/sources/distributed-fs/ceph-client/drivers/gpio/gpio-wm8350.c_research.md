# sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm8350.c

## Purpose
Provides basic gpiolib support for the 13 GPIO pins on Wolfson WM8350 PMICs using the parent MFD register accessors.

## Important APIs, Types, And Functions
- `struct wm8350_gpio_data` holds the parent `struct wm8350` and chip template copy.
- `wm8350_gpio_direction_in`, `wm8350_gpio_direction_out`, `wm8350_gpio_get`, and `wm8350_gpio_set` manipulate `WM8350_GPIO_CONFIGURATION_I_O` and `WM8350_GPIO_LEVEL`.
- `wm8350_gpio_to_irq` maps offsets to parent IRQ numbers when `wm8350->irq_base` is available.
- `wm8350_gpio_probe` copies the template chip, sets `ngpio = 13`, applies platform GPIO base if present, and registers the chip.

## Control Flow
Direction input sets the corresponding I/O bit. Direction output clears the I/O bit and then writes the requested level because hardware lacks atomic direction/value setup. Set updates the level bit through set/clear helpers. Get reads the shared GPIO level register and masks the requested offset.

## State And Persistence
There is no software shadow state. Direction and level live in WM8350 PMIC registers. Legacy platform data may set a fixed base; otherwise the chip uses dynamic GPIO numbering.

## Dependencies And Integration Points
Depends on WM8350 MFD core, platform data, WM8350 GPIO register definitions, parent IRQ base allocation, and gpiolib. The platform driver registers as `wm8350-gpio` via `subsys_initcall`.

## Risks And Edge Cases
Direction-output has a window where the pin becomes output before the new value is written. `to_irq` fails when the parent has no IRQ base. The driver has no `get_direction`, pinconf, or debugfs support, so consumers cannot query some hardware state through standard callbacks.

## Test Signals
Verify 13-line registration, fixed and dynamic base behavior, direction bit polarity, value read/write paths, output direction ordering, IRQ mapping with and without parent IRQ base, and error propagation from parent register helpers.
