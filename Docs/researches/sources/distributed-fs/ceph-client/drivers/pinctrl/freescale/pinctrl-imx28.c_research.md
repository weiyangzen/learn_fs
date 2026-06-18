# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx28.c

Purpose: Provides i.MX28 MXS-family pin descriptors and register offsets for the shared MXS pinctrl core.

Important APIs and types: Defines `enum imx28_pin_enum`, `imx28_pins[]`, `imx28_regs` with `muxsel = 0x100`, `drive = 0x300`, and `pull = 0x600`, `imx28_pinctrl_data`, probe wrapper, OF match table, and `postcore_initcall()` registration.

Control flow: OF match on `fsl,imx28-pinctrl` calls `mxs_pinctrl_probe()` with the i.MX28 data. The MXS core handles DT mapping, pinmux, pinconf, and MMIO writes.

State and persistence: Static SoC data is held here. Runtime controller state belongs to `pinctrl-mxs`. Mux, drive, and pull settings persist in MXS hardware registers.

Dependencies and integration points: Depends on `pinctrl-mxs.h`, `CONFIG_PINCTRL_MXS`, and i.MX28 DT bindings. It exposes pins for GPMI, LCD, SSP, AUART, PWM, SAIF, I2C, SPDIF, Ethernet, JTAG, and EMI.

Risks: i.MX28 has more banks and different drive/pull offsets than i.MX23, so shared-board assumptions can break. Missing enum entries for unavailable pins are intentional; DT must use valid `PINID()` values.

Test signals: Build `CONFIG_PINCTRL_IMX28`, boot i.MX28 hardware, inspect debugfs, and test NAND, LCD, MMC/SSP, UART, Ethernet, I2C, and drive-strength/pull states.
