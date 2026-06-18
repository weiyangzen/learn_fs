# sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-pic64gx-gpio2.c

## Purpose
This driver controls the PIC64GX GPIO2 pinmux register. It exposes package pins and peripheral groups where each group can be selected either as GPIO or as a fixed peripheral function by setting bits in a single MMIO register.

## Important APIs, Types, and Functions
- `PIC64GX_PINMUX_REG` is the single mux register at offset zero.
- `pic64gx_gpio2_regmap_config` defines a little-endian 32-bit MMIO regmap.
- `pic64gx_gpio2_pins` names 29 package pins by ball labels.
- Group arrays cover MDIO0/1, SPI0, CAN0/1, PCIe, QSPI, UART3/4/2.
- `PIC64GX_PINCTRL_GROUP()` generates paired GPIO/peripheral groups for each function, with group-specific masks and settings.
- `pic64gx_gpio2_functions` maps function names to group lists, including a multi-group `gpio` function.
- Pinctrl ops expose group metadata and debug display; pinmux ops expose function metadata and write selected group settings.
- `pic64gx_gpio2_probe()` maps MMIO resource 0, creates a regmap, initializes the descriptor, and registers pinctrl.

## Control Flow
Probe maps the hardware register and registers the pinctrl device. DT pinctrl states select a function/group; `pic64gx_gpio2_pinmux_set_mux()` looks up the selected group and writes its mask/setting using `regmap_assign_bits()`. GPIO groups clear the same bits that peripheral groups set.

## State and Persistence
Software state is `struct pic64gx_gpio2_pinctrl`. Mux selections persist in the single MMIO register. There is no pinconf, GPIO chip, IRQ handling, or suspend/resume state in this file.

## Dependencies and Integration Points
The driver depends on platform MMIO resources, regmap MMIO, Linux pinctrl/pinmux helpers, generic DT map parsing, and the `microchip,pic64gx-pinctrl-gpio2` compatible. It is selected by `CONFIG_PINCTRL_PIC64GX`.

## Risks
The whole driver is table driven around one register, so incorrect bit masks or package-pin group membership will misroute peripherals. There is no GPIO-controller implementation here despite the `gpio_` group names; it only selects mux mode. `regmap_assign_bits()` return values are not checked in `set_mux`.

## Test Signals
Build with `CONFIG_PINCTRL_PIC64GX`, verify the platform resource maps, inspect debugfs pinctrl groups/functions, and test switching each peripheral group to GPIO and peripheral mode while reading back the mux register. Board-level validation should cover QSPI, CAN, UART, MDIO, SPI, and PCIe reset/sideband pins.
