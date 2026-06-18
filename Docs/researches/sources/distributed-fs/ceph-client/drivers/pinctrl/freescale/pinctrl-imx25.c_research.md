# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx25.c

Purpose: Supplies i.MX25 pad IDs and pin descriptors for the common i.MX MMIO pinctrl driver, and registers the `fsl,imx25-iomuxc` platform driver.

Important APIs and types: Defines `enum imx25_pads`, `imx25_pinctrl_pads[]`, `imx25_pinctrl_info`, OF match table, `imx25_pinctrl_probe()`, and an `arch_initcall()` driver registration.

Control flow: Platform probe delegates directly to `imx_pinctrl_probe()`, which maps IOMUXC registers, parses DT functions/groups, registers the controller, and enables hog states.

State and persistence: The pad table and SoC info are immutable. Runtime parsed group/function data, register offsets, and current state are in the common i.MX driver. Hardware mux/pad values persist in IOMUXC registers.

Dependencies and integration points: Depends on `pinctrl-imx.h`, `CONFIG_PINCTRL_IMX`, OF bindings using i.MX25 register-offset cells, and consumers for external memory, LCD, CSI, I2C, CSPI, UART, SD, keypad, FEC, and boot/control pads.

Risks: The pad enum includes reserved pads and must align with register-offset-derived pin IDs in DT. Since this SoC info sets no special flags, the default six-cell `fsl,pins` MMIO format is expected. Bad DT offsets can select reserved descriptors.

Test signals: i.MX25 build/boot, valid `fsl,imx25-iomuxc` probe, default/sleep state selection, debugfs pad names, and peripheral tests for FEC, UART, SDHC, LCD, and NAND.
