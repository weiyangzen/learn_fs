# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx27.c

Purpose: Supplies i.MX27 pad IDs and pin descriptors for the legacy i.MX1-style pinctrl core, and registers the `fsl,imx27-iomuxc` platform driver.

Important APIs and types: Defines port constants, `PAD_ID()`, `enum imx27_pads`, `imx27_pinctrl_pads[]`, `imx27_pinctrl_info`, OF match table, probe wrapper, and `arch_initcall()` registration.

Control flow: Platform probe calls `imx1_pinctrl_core_probe()`. The common legacy core parses DT functions/groups and programs port-based mux registers.

State and persistence: Static pad data lives here; parsed functions/groups are added to the mutable `imx27_pinctrl_info` by the core. Hardware state persists in legacy IOMUX registers through the core.

Dependencies and integration points: Depends on `pinctrl-imx1.h`, `CONFIG_PINCTRL_IMX1_CORE`, and DT bindings for i.MX27 mux ID/config triples. Covers LCD, SD, CSI, USB, I2C, SSI, ATA, CSPI, UART, NAND, PCMCIA, and clock/reset pads.

Risks: Sparse port-based pad IDs must match the legacy register layout. The shared legacy core has static descriptor/index state, so multiple instances would be risky even though SoC usage is normally single-instance. Mux IDs are opaque and easy to misencode in DT.

Test signals: i.MX27 build/boot, debugfs pin state reads, DT parsing for several functions, UART/USB/SD/FEC-equivalent peripheral pin selection, and pullup config tests.
