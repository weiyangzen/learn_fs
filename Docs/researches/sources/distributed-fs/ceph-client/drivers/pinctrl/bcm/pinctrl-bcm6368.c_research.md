<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6368.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6368.c

## Purpose
This file provides BCM6368 pinmux tables and register programming for the BCM63xx common pinctrl core. It covers 38 GPIOs, many one-pin overlay functions, and a UART1 base mode on GPIOs 30-33.

## Important APIs, Types, And Functions
`struct bcm6368_function` maps a function to its groups, output-direction bitmap, and optional base-mode value. `struct bcm6368_priv` stores a regmap field for the BASEMODE register. `BCM6368_BASEMODE_PIN()` marks pins whose function depends on base-mode selection. `bcm6368_pinctrl_set_mux()` handles two paths: base-mode functions clear per-pin mode bits and write the base-mode field, while ordinary functions force base mode back to GPIO if needed and set the per-pin mode bit. It then programs GPIO direction for pins in the selected group.

## Control Flow
Probe allocates private state, invokes `bcm63xx_pinctrl_probe()`, retrieves the common state, and allocates the base-mode regmap field. Mux selection resolves the static group/function entry, updates MODE and BASEMODE registers as needed, and uses the pinctrl GPIO range to call GPIO direction callbacks. GPIO request enable clears per-pin mode bits and restores base-mode GPIO for marked pins.

## State And Persistence
Private state is limited to the base-mode regmap field. Hardware state persists in the MODE register, BASEMODE field, and GPIO direction registers. The common BCM63xx core owns pinctrl registration and GPIO regmap state.

## Dependencies And Integration Points
Depends on the shared BCM63xx helper, regmap fields, pinctrl-utils, gpiolib direction callbacks, and strict pinmux ownership. It binds to `brcm,bcm6368-pinctrl`.

## Risks
As with BCM6358, the mux code loops over group pin count but indexes `bcm6368_pins[pin]` by loop index in direction handling, which is risky for groups whose pin numbers differ from descriptor indexes. Base-mode restoration must be paired with any function on pins 30-33. The direction bitmap is part of function semantics; an incorrect bit can configure a peripheral pin as input when hardware expects output.

## Test Signals
Validate analog AFE, system IRQ, serial LED, internet LED, EPHY/RoboSwitch LEDs, USB LED, PCI/PCMCIA, EBI, SPI CS, UART1, and GPIO fallback. Confirm UART1 base mode switches all four pins and that GPIO requests on pins 30-33 restore base mode to GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6368.c -->
