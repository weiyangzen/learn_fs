<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63268.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63268.c

## Purpose
This file provides the BCM63268 pinctrl description and mux programming for the shared BCM63xx pinctrl core. It covers 52 GPIOs, LED control, per-pin mode bits, Wi-Fi control bits, NAND and VDSL/DECT base modes, and GPIO fallback for pins that overlap those base modes.

## Important APIs, Types, And Functions
`enum bcm63268_pinctrl_reg` classifies functions by the register they program: LED, MODE, CTRL, or BASEMODE. `struct bcm63268_function` records the function name, groups, register type, and base-mode mask. `BCM63268_PIN()` stores base-mode ownership masks in pin descriptor `drv_data`. `bcm63268_set_gpio()` clears all function ownership for a pin, including base-mode bits, LED bits, mode bits, or CTRL Wi-Fi bits. `bcm63268_pinctrl_set_mux()` first returns every pin in a group to GPIO, then enables the requested function register bit or base-mode mask.

## Control Flow
Probe calls `bcm63xx_pinctrl_probe()` with the BCM63268 SoC table. DT parsing uses generic pin config-to-pin mapping via `pinctrl_utils_free_map` and `pinconf_generic_dt_node_to_map_pin`. On mux selection, the driver sanitizes each pin in the target group with `bcm63268_set_gpio()`, chooses the hardware register and value from the function descriptor, then updates the register through regmap.

## State And Persistence
No private state is stored in this file. Hardware state persists in LED, MODE, CTRL, and BASEMODE registers. `drv_data` embedded in the static pin descriptors is used as immutable metadata to know which base-mode bits must be cleared when reclaiming a pin as GPIO.

## Dependencies And Integration Points
It integrates with the common BCM63xx probe/gpio-regmap implementation, pinctrl-utils generic DT mapping, and the parent regmap obtained from the syscon node. It is the platform driver for `brcm,bcm63268-pinctrl`, while the shared common file also detects the corresponding `brcm,bcm63268-gpio` child for GPIO registration.

## Risks
The file coordinates overlapping function domains. A pin can be controlled by base mode, LED mode, normal mode, or Wi-Fi CTRL behavior, and failure to clear old ownership before setting a new function can leave mixed hardware state. For pins 24-27, multiple base-mode masks overlap NAND and VDSL functions, making table accuracy especially important.

## Test Signals
Exercise NAND, DECT, VDSL override, Wi-Fi, LED, UART1, HSSPI chip-select, NTR, ADSL SPI, switch LED, and GPIO fallback states. Verify GPIO requests clear base-mode conflicts and that Wi-Fi pins 32-51 switch through CTRL semantics correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63268.c -->
