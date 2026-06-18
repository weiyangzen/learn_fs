<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.c

## Purpose
This is the shared support file for the BCM63xx pinctrl family. It registers the SoC-specific pinctrl descriptor supplied by each BCM63xx variant and creates a GPIO controller through `gpio-regmap` for matching child GPIO nodes.

## Important APIs, Types, And Functions
`bcm63xx_reg_mask_xlate()` translates a GPIO offset into a register offset and bit mask for gpio-regmap. BCM63xx banks are 32 GPIOs wide, and bank register addresses count backwards from the base value using `BCM63XX_BANK_SIZE`. `bcm63xx_gpio_probe()` fills `struct gpio_regmap_config` with data, direction, set, ngpio, and translation settings. `bcm63xx_pinctrl_probe()` allocates `struct bcm63xx_pinctrl`, obtains the parent syscon regmap, fills `pinctrl_desc`, registers pinctrl, and scans sibling child nodes for compatible GPIO controllers.

## Control Flow
Each SoC-specific file calls `bcm63xx_pinctrl_probe(pdev, &soc, driver_data)`. The common function stores optional driver data for the SoC file, registers pinctrl operations from the `soc` descriptor, then iterates children of the parent OF node. If a child matches any BCM63xx GPIO compatible string, the common code registers a gpio-regmap chip using the same regmap.

## State And Persistence
Software state is `struct bcm63xx_pinctrl`: device, parent regmap, pinctrl descriptor/device, and opaque SoC driver data. GPIO data/direction and mux state persist in shared syscon registers rather than in this file. Device-managed allocation and registration control lifetime.

## Dependencies And Integration Points
Depends on `linux/gpio/regmap.h`, MFD syscon regmaps, OF child node scanning, and SoC-specific descriptors from `pinctrl-bcm6318.c`, `pinctrl-bcm6328.c`, `pinctrl-bcm6358.c`, `pinctrl-bcm6362.c`, `pinctrl-bcm6368.c`, and `pinctrl-bcm63268.c`.

## Risks
The register translation uses a negative bank stride from `base - stride * 4`, which must match the hardware register layout for all supported chips. The common GPIO registration assumes the pinctrl device's parent node contains the GPIO child nodes. If board DT hierarchy differs, pinctrl can register but GPIO support will not appear.

## Test Signals
For every BCM63xx SoC, confirm pinctrl registration, GPIO child discovery, gpiochip creation, GPIO data/direction operation across bank 0 and bank 1, and successful mux ownership through the SoC-specific operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.c -->
