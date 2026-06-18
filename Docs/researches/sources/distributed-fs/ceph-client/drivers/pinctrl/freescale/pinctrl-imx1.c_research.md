# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1.c

Purpose: Supplies the i.MX1 pad enumeration and pin descriptor table, then registers a built-in platform driver for `fsl,imx1-iomuxc` using the legacy i.MX1 core.

Important APIs and types: Defines `PAD_ID()`, port constants, `enum imx1_pads`, `imx1_pinctrl_pads[]`, `imx1_pinctrl_info`, and `imx1_pinctrl_probe()`. Driver registration uses `builtin_platform_driver_probe()`.

Control flow: The platform bus matches `fsl,imx1-iomuxc`; the built-in probe passes static pad data to `imx1_pinctrl_core_probe()`, which handles DT parsing and hardware operations.

State and persistence: This file is immutable SoC data except for the `imx1_pinctrl_info` object that the core fills with parsed groups/functions. Hardware state is managed by `pinctrl-imx1-core.c`.

Dependencies and integration points: Depends on `pinctrl-imx1.h`, the legacy core object, OF matching, and board DT nodes using i.MX1 pad IDs.

Risks: Pad IDs are sparse by port, and the descriptor array must match valid hardware pads. Built-in-only registration affects init ordering. Since the common core mutates the SoC info, this table is not purely const.

Test signals: i.MX1 defconfig build, boot with `fsl,imx1-iomuxc`, DT group parsing, debugfs pin list matching expected pads, and peripheral bring-up for LCD, UART, SPI, SD, USB, and CSI pins.
