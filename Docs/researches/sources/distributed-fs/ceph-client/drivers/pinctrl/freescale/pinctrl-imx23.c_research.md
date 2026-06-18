# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx23.c

Purpose: Provides i.MX23 MXS-family pin numbers, pin descriptors, register offsets, and platform-driver registration for the shared MXS pinctrl core.

Important APIs and types: Defines `enum imx23_pin_enum`, `imx23_pins[]`, `imx23_regs` with `muxsel`, `drive`, and `pull` offsets, `imx23_pinctrl_data`, and a probe wrapper around `mxs_pinctrl_probe()`.

Control flow: `postcore_initcall()` registers the platform driver. OF match on `fsl,imx23-pinctrl` calls the probe wrapper, which delegates parsing and register programming to `pinctrl-mxs`.

State and persistence: This file stores immutable SoC data and one static `mxs_pinctrl_soc_data` instance. Runtime state and MMIO writes are owned by the MXS core. Selected mux/drive/pull values persist in MXS registers.

Dependencies and integration points: Depends on `pinctrl-mxs.h`, OF platform matching, and MXS DT bindings. It covers GPMI, LCD, PWM, SSP, I2C, AUART, rotary, and EMI pin banks.

Risks: `PINID(bank,pin)` numbering must match MXS hardware and DT bindings. Register offsets differ from i.MX28, so cross-copy mistakes can program drive or pull registers incorrectly.

Test signals: Build `CONFIG_PINCTRL_IMX23`, boot an i.MX23 board, inspect pin descriptors, select NAND/LCD/SSP/I2C/UART states, and verify drive/pull configuration through hardware behavior or debugfs.
