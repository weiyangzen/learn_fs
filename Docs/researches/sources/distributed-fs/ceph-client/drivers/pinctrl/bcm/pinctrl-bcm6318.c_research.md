<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6318.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6318.c

## Purpose
This SoC-specific BCM63xx pinctrl file describes BCM6318 pins, functions, groups, and mux register programming. It supports 50 GPIOs, LED mode for GPIOs 0-23, pinmux-select functions for Ethernet LEDs, serial LEDs, USB, DSL, WPS, and other board signals, and GPIO request fallback that disables alternate functions.

## Important APIs, Types, And Functions
`struct bcm6318_function` maps a function to its groups plus a one-bit mode value and two-bit mux value. Static `bcm6318_pins`, one-pin `bcm6318_groups`, function group arrays, and `bcm6318_funcs` define the hardware matrix. `bcm6318_mux_off()` and `bcm6318_pad_off()` calculate register offsets. `bcm6318_rmw_mux()` updates the mode register and mux selector fields; `bcm6318_set_pad()` controls the pad register for pins whose GPIO mode needs a pad value.

## Control Flow
The platform probe simply calls the shared `bcm63xx_pinctrl_probe()` with `bcm6318_soc`. After common registration, pinctrl callbacks expose group and function counts, names, and pins from static tables. `bcm6318_pinctrl_set_mux()` selects the first pin in the requested group and writes the function's mode and mux values. When gpiolib requests a line, `bcm6318_gpio_request_enable()` clears alternate functions; pins 0-12 use mux 0 as GPIO, while pins 13-41 use mux 3 as GPIO and have pad value cleared.

## State And Persistence
Software state is supplied by the shared `struct bcm63xx_pinctrl`; this file persists no private state. Hardware mux state lives in the shared parent regmap registers. The common helper registers GPIO via `gpio-regmap`, so GPIO data and direction are stored through the parent syscon register map.

## Dependencies And Integration Points
Depends on `pinctrl-bcm63xx.h` for shared probe/state, Linux regmap, pinctrl-utils DT parsing, pinmux strict mode, and the parent syscon node that owns the GPIO/pinmux registers. It is built as a builtin platform driver for `brcm,bcm6318-pinctrl`.

## Risks
The main risk is wrong mux value or register offset per pin. GPIO request handling has SoC-specific split rules for pins below 13 and pins 13-41, so off-by-one errors can leave pins in an alternate function. `strict = true` prevents simultaneous GPIO and mux ownership, but only if pinctrl ranges are correct.

## Test Signals
Validate DT states for LED, Ethernet LED, serial LED, USB, DSL, and WPS functions. Request GPIOs across the split ranges 0-12, 13-41, and 42-49 and verify they return to GPIO mode. GPIO data/direction testing should use the common BCM63xx gpio-regmap chip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6318.c -->
