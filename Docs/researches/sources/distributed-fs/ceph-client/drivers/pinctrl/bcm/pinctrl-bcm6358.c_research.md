<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6358.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6358.c

## Purpose
This file implements BCM6358-specific pinmux data and control for the shared BCM63xx framework. Unlike the newer BCM63xx variants, BCM6358 uses overlay mode bits in a single mode register and must sometimes drive GPIO direction when assigning non-GPIO functions.

## Important APIs, Types, And Functions
`struct bcm6358_pingroup` wraps a `pingroup`, the mode bit to enable, and a per-pin direction bitmap for that group. `struct bcm6358_priv` stores a `regmap_field *overlays` covering mode bits 0-15. Static pin descriptors put the set of possible overlay bits for each pin in `drv_data`. `bcm6358_pinctrl_set_mux()` computes a mask of the selected group mode and all conflicting overlay bits, updates the regmap field, then asks the registered GPIO chip to set each pin input or output according to group direction.

## Control Flow
Probe allocates private state, calls the common BCM63xx probe with that state, fetches the resulting `struct bcm63xx_pinctrl`, and allocates the overlay regmap field. Standard pinctrl callbacks expose the static group and function tables. GPIO request enable reads the pin's `drv_data` overlay mask and clears all function bits that could own that line.

## State And Persistence
The only private software state is the overlay regmap field pointer. The active function state persists in the BCM6358 mode register. GPIO direction changes made during muxing persist in the common GPIO direction register and are intentionally used as part of the alternate-function setup.

## Dependencies And Integration Points
Depends on `pinctrl-bcm63xx.c` for registration and GPIO, Linux regmap fields, pinctrl-utils generic DT parsing, and gpiolib ranges because mux setup looks up the GPIO chip with `pinctrl_find_gpio_range_from_pin()` and invokes direction callbacks.

## Risks
The function/group arrays contain names such as `spi_cs_2_3` and `clkrst` whose group arrays reference group names; table mismatches would break DT state resolution. In the mux and direction loops, code indexes `bcm6358_pins[pin]` using the loop index rather than the group's pin number, which is a notable maintenance risk because it assumes group pin arrays and descriptor ordering are compatible. Direction side effects can also surprise consumers if a function's output bitmap is wrong.

## Test Signals
Test all overlay functions, especially UART1, EBI CS, SPI CS, UTOPIA, modem, serial/legacy LEDs, PWM sync clock, and system IRQ. Confirm GPIO requests clear overlay bits. Verify alternate functions that require output directions drive expected idle levels and that pinctrl strictness prevents concurrent GPIO use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6358.c -->
