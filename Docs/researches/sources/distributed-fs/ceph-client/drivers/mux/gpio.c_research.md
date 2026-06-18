# sources/distributed-fs/ceph-client/drivers/mux/gpio.c

Purpose: platform driver for muxes controlled by an array of GPIO lines. It exposes one mux controller whose state value is driven as a binary value across the GPIO array.

Important APIs and functions: `struct mux_gpio` stores `struct gpio_descs *gpios`. `mux_gpio_set()` converts the integer state into a bitmap with `bitmap_from_arr32()` and writes all GPIOs through `gpiod_multi_set_value_cansleep()`. `mux_gpio_probe()` counts `"mux"` GPIOs, allocates a `mux_chip`, retrieves the GPIO array as outputs initially low, sets `states = BIT(pins)`, validates optional `idle-state`, optionally enables a `"mux"` regulator, and registers the mux chip. OF compatible is `gpio-mux`.

Control flow: probe constructs the controller from firmware-described GPIOs; runtime selection is a pure GPIO write path invoked by mux-core. Regulator enable happens before registration so consumers do not see an unpowered mux. Idle restoration is performed by mux-core when configured.

State and dependencies: persistent runtime state is held by mux-core and GPIO descriptor ownership; hardware state is GPIO output level. Dependencies are GPIOLIB, platform bus, firmware properties, optional regulator framework, and mux-core. Risks include `BIT(pins)` overflow for large GPIO arrays, ambiguous GPIO bit ordering if firmware authors do not match hardware wiring, and no explicit handling of `MUX_IDLE_DISCONNECT` because GPIO muxes support only numeric states or `AS_IS`. Test signals include DT GPIO count/order, idle-state boundary checks, regulator probe deferral, state-to-line mapping, and suspend/resume behavior inherited from GPIO providers.
