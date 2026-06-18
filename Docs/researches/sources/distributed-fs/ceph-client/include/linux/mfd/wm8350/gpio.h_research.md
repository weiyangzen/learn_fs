<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/gpio.h

## Purpose
`gpio.h` defines the WM8350 GPIO register map, alternate-function encodings for GPIO0 through GPIO12, electrical configuration constants, interrupt/status bits, the GPIO configuration helper, and GPIO child state.

## Important APIs, types, and functions
The public function is `wm8350_gpio_config(struct wm8350 *wm8350, int gpio, int dir, int func, int pol, int pull, int invert, int debounce)`. `struct wm8350_gpio` stores the platform device. Macros define debounce, pull-up/down, interrupt mode, direction, polarity/type, function-select, level registers, per-pin alternate functions, direction/polarity/pull/invert/debounce values, and `WM8350_IRQ_GPIO(x)` mapping GPIO pins to IRQ numbers starting at 50.

## Control flow
Platform init or a GPIO driver calls `wm8350_gpio_config()` to program pin direction, function select nibble, polarity/type, pull resistor, inversion, and debounce. Runtime GPIO reads use the level register, and IRQ handling maps pin events through the core IRQ domain.

## State and persistence behavior
Pin mux and electrical state are hardware register state. `struct wm8350_gpio` only tracks the child platform device; board policy must be re-applied after reset or resume if registers are not retained.

## Dependencies and integration points
The header depends on `platform_device` and `struct wm8350`. It integrates with core IRQ/status definitions, board `wm8350_platform_data.init`, gpiolib-facing implementation code, and alternate functions used by audio, power, RTC, charger, and reset signals.

## Risks and test signals
Risks include selecting an alternate function invalid for a pin, mixing active-low with invert semantics, enabling pulls on outputs, off-by-one GPIO IRQ mapping, and clobbering neighboring 4-bit function fields. Test signals include per-pin mux tests, direction/readback tests, interrupt edge tests, suspend/resume retention, and invalid argument validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/gpio.h -->
