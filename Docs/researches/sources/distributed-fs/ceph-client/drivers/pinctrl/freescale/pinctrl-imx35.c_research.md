# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx35.c

Purpose: Supplies the large i.MX35 pad descriptor table and platform-driver wrapper for the common i.MX MMIO pinctrl driver.

Important APIs and types: Defines `enum imx35_pads` with 485 entries including many reserved IDs, `imx35_pinctrl_pads[]`, `imx35_pinctrl_info`, OF match table for `fsl,imx35-iomuxc`, `imx35_pinctrl_probe()`, and `arch_initcall()` registration.

Control flow: Platform probe delegates to `imx_pinctrl_probe()`. All DT parsing, group/function registration, mux writes, pad config writes, and PM state forcing are handled by the common i.MX driver.

State and persistence: Static pad descriptors are immutable; parsed groups/functions and register-offset maps live in common-driver state. Hardware state persists in i.MX35 IOMUXC registers.

Dependencies and integration points: Depends on `pinctrl-imx.h`, `CONFIG_PINCTRL_IMX`, and i.MX35 DT bindings. The pad list spans external memory, CSI, I2C, SSI/ESAI-like audio, CSPI, UART, USB OTG, display, SD, ATA, MLB, FEC, boot/clock/reset, SDRAM, JTAG, and reserved register slots.

Risks: The table is large and reserve-heavy, so off-by-one enum changes can corrupt many DT-visible pin IDs. As with i.MX25, no special flags are set, so DT must use the default common i.MX cell format. Reserved pad descriptors may appear in debugfs but should not be selected by board pin states.

Test signals: i.MX35 build/boot, successful `fsl,imx35-iomuxc` probe, DT state selection for UART, FEC, SD, LCD, and NAND/ATA, debugfs pin count/name inspection, and suspend/resume default/sleep state checks.
