# sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s700.c

Purpose: Supplies the Actions Semi S700 pinctrl description for the common OWL core. It is structurally close to S500 but adjusts pin numbering, Ethernet width, extra dummy groups, Bluetooth/SIRQ exposure, and GPIO interrupt register layout for S700 hardware.

Important APIs and types: Defines the S700 register offsets, GPIO numbering macros for ports A-E, `s700_pads`, `enum s700_pinmux_functions`, `s700_groups`, `s700_functions`, `s700_padinfo`, `s700_gpio_ports`, conversion callbacks `s700_pad_pinconf_arg2val()` and `s700_pad_pinconf_val2arg()`, `s700_pinctrl_data`, and the `pinctrl-s700` platform driver. The group table contains 65 mux groups and 31 drive-strength groups.

Control flow: `s700_pinctrl_init()` registers the driver at `arch_initcall`. Matching `actions,s700-pinctrl` devices call `s700_pinctrl_probe()`, which hands `s700_pinctrl_data` to `owl_pinctrl_probe()`. Runtime pinmux and pinconf operations are entirely delegated to the shared OWL implementation. Function mapping covers NOR, RGMII/SGMII-labeled Ethernet functions, SPI0-3, sensors, UART0-6, I2S, PCM, keypad, JTAG, PWM, SD0-2, I2C0-3, DSI, LVDS, USB30, clock output, MIPI CSI, NAND, SPDIF, SIRQ0-2, Bluetooth, and LCD0.

State and persistence: The file stores immutable S700 tables; actual mux, pull, Schmitt, drive, GPIO, and IRQ state persists in hardware after common-driver writes. S700 exposes 136 GPIOs: ports A-D with 32 pins and port E with 8 pins. Pull conversion is the same two-state encoding as S500, while Schmitt enable remains 0/1.

Dependencies and integration points: Uses `pinctrl-owl.h` macros and Linux pinctrl/generic pinconf APIs. Device tree integration is through `actions,s700-pinctrl`. The GPIO interrupt map differs from S500: ports share `intc_ctl` at `0x204`, use per-port pending/mask/type offsets, and port E has a comment noting `INTC_GPIOD_TYPE1` use to fit the generic shared driver model.

Risks: Because many S700 tables were derived from the S500 shape, copy/paste drift is a key risk, especially around names such as `S700_MUX_ETH_RGMII` assigned to `FUNCTION(eth_rmii)` and `S700_MUX_ETH_SGMII` assigned to `FUNCTION(eth_smii)`. Dummy groups for NAND and SIRQ functions are placeholders that expose function names without normal pad lists; consumers need datasheet confirmation. The shared mux-field conflict risk remains for groups that point at the same MFCTL bits. GPIO interrupt register offsets and `shared_ctl_offset` values are subtle and should be validated on hardware.

Test signals: Build with S700 enabled, boot a DT node using `actions,s700-pinctrl`, verify all 136 GPIOs, test Ethernet including the extra TXD2/TXD3/RXD2/RXD3 pads, validate UART/BT and SIRQ pin states, exercise I2C0-3, SD, NAND, display, CSI, and PWM muxes, read back pull and Schmitt settings, test 2/4/8/12 mA drive-strength groups, and trigger GPIO IRQs on each parent line including port E.
