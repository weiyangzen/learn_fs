<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6328.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6328.c

## Purpose
This BCM63xx SoC file describes BCM6328 pin groups and mux programming. It supports 32 GPIOs plus two pseudo pins for `hsspi_cs1` and `usb_port1`, and exposes functions for LEDs, serial LEDs, internet activity LED, PCIe clock request, Ethernet PHY activity LEDs, HSSPI CS1, and USB host/device port mode.

## Important APIs, Types, And Functions
`struct bcm6328_function` carries group lists plus a mode bit and two-bit mux value. `bcm6328_mux[]` maps pin ranges to mux register offsets. `bcm6328_mux_off()` selects the proper mux register, while `bcm6328_rmw_mux()` updates the mode bit for real GPIO pins and the two-bit mux selector for all defined pins, including the pseudo pins. `bcm6328_pinctrl_set_mux()` and `bcm6328_gpio_request_enable()` are the key pinmux callbacks.

## Control Flow
Probe delegates to `bcm63xx_pinctrl_probe()`. Pinctrl callbacks expose static group/function tables. Mux selection takes the first pin in the selected group and writes the function's mode and mux values. GPIO request enable clears mode and mux selection to zero for the requested GPIO line.

## State And Persistence
All mutable state lives in hardware registers behind the shared regmap. The driver itself is table-only after registration. GPIO direction/value state is provided by the common GPIO regmap chip, while pinmux state persists in MODE and MUX registers until changed or reset.

## Dependencies And Integration Points
Uses the BCM63xx shared core, Linux regmap, pinctrl-utils DT mapping, and strict pinmux semantics. It is registered as a builtin platform driver for `brcm,bcm6328-pinctrl` and expects a parent syscon plus a matching GPIO child for GPIO support.

## Risks
The pseudo pins 36 and 38 are explicitly noted as approximate locations based on mux offsets, so consumers must match the binding expectations rather than assume physical GPIO numbering. `bcm6328_mux_off()` indexes `bcm6328_mux[pin / 16]`; only defined pin numbers should reach it. Incorrect DT pin numbers could otherwise select unintended registers.

## Test Signals
Apply DT states for LED, serial LED, Ethernet LEDs, PCIe clock request, HSSPI CS1, and USB host/device port modes. Request GPIOs 0-31 and confirm alternate function bits are cleared. Validate USB port mode and HSSPI chip-select behavior because they use nonstandard pseudo pin numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6328.c -->
