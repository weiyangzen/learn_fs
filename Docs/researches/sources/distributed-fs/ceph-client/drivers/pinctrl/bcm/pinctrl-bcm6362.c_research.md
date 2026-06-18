<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6362.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6362.c

## Purpose
This BCM63xx SoC file describes and programs BCM6362 pinmux state. It supports 48 GPIOs, LED mode, normal mode bits, Wi-Fi control via the CTRL register, and a NAND base mode spanning a multi-pin group.

## Important APIs, Types, And Functions
`enum bcm6362_pinctrl_reg` identifies LED, MODE, CTRL, and BASEMODE targets. `struct bcm6362_function` maps function names to groups and register type, with optional base-mode mask. `BCM6362_PIN()` annotates NAND-owned pins via descriptor `drv_data`. `bcm6362_set_gpio()` clears NAND base mode, per-pin mode/LED bits, or Wi-Fi CTRL ownership for a pin. `bcm6362_pinctrl_set_mux()` clears all pins in the selected group, then sets the function-specific register bit or base-mode mask.

## Control Flow
Probe delegates to the shared BCM63xx core. Group/function callbacks return static table data. Applying a pinctrl state calls `set_mux`, which first normalizes all group pins to GPIO, then chooses the register and mask based on `bcm6362_funcs[selector].reg`. GPIO request enable also uses `bcm6362_set_gpio()` to reclaim the line.

## State And Persistence
No dynamic private state is kept. Hardware state persists in LED, MODE, CTRL, and BASEMODE registers. The shared common layer supplies `struct bcm63xx_pinctrl`, the regmap, and GPIO state through gpio-regmap.

## Dependencies And Integration Points
Depends on the common BCM63xx core, parent syscon regmap, pinctrl-utils, and Linux pinmux strict ownership. Consumers use `brcm,bcm6362-pinctrl` states for board functions such as LEDs, UART1, ADSL SPI, Ethernet PHY LEDs, external IRQs, Wi-Fi, and NAND.

## Risks
The code computes `mask = bcm63xx_bank_pin(pin)` in `bcm6362_set_gpio()` and then passes that value to `regmap_update_bits()` where other paths use `BIT(...)`; this is a risk area to review against hardware expectations. Base-mode pins need careful table metadata because failing to clear NAND mode can block GPIO or other mode bits. CTRL semantics are inverted for Wi-Fi versus GPIO, so value polarity mistakes are easy.

## Test Signals
Exercise LED, serial LED, RoboSwitch LEDs, internet LED, SPI CS, UART1, ADSL SPI, EPHY LEDs, external IRQs, Wi-Fi pins 32-47, NAND group, and GPIO fallback. Read back regmap traces or hardware pins to confirm NAND base mode clears when individual pins become GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6362.c -->
