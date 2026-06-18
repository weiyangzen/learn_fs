# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8qxp.c

## Purpose
`pinctrl-imx8qxp.c` binds the NXP/Freescale IMX8QXP IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx8qxp_pinctrl_pads` (174 pins). Pad coverage includes GPIO, UART, I2C, USDHC, SD/SDHC, Ethernet, NAND, CSI/camera, SAI/audio, JTAG, USB, CAN.
- SoC info: `imx8qxp_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx8qxp-iomuxc`.
- Platform driver: `imx8qxp-pinctrl` via `imx8qxp_pinctrl_driver`; registered by `arch_initcall(imx8qxp_pinctrl_init)`.
- Notable includes: `dt-bindings/pinctrl/pads-imx8qxp.h`, `linux/err.h`, `linux/firmware/imx/sci.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/module.h`, `linux/of.h`, `linux/pinctrl/pinctrl.h`, `linux/platform_device.h`.
- Pad-table edge samples: `imx8qxp_pinctrl_pads` starts with `IMX8QXP_PCIE_CTRL0_PERST_B`, `IMX8QXP_PCIE_CTRL0_CLKREQ_B`, `IMX8QXP_PCIE_CTRL0_WAKE_B`, `IMX8QXP_COMP_CTL_GPIO_1V8_3V3_PCIESEP` and ends with `IMX8QXP_QSPI0B_DQS`, `IMX8QXP_QSPI0B_SS0_B`, `IMX8QXP_QSPI0B_SS1_B`, `IMX8QXP_COMP_CTL_GPIO_1V8_3V3_QSPI0B`.

## Control Flow
- `imx8qxp_pinctrl_probe()` initializes SCU IPC, propagates any error, then calls `imx_pinctrl_probe()` with ``imx8qxp_pinctrl_info``.
- During core probe, child pinctrl nodes are parsed into generic pinctrl groups/functions; pin IDs and register offsets are cached in `struct imx_pin_reg`.
- When a consumer selects a pinctrl state, the generic pinmux callback calls the i.MX core `set_mux` path, which programs mux registers for each pin unless the SoC uses SCU.
- Pin configuration maps are then applied through the core pinconf path, writing pad config registers or dispatching to SCU callbacks depending on `.flags`.

## State And Persistence Behavior
- Static state consists of pad descriptor arrays, immutable SoC info, OF match data, and the platform-driver descriptor.
- Runtime state is allocated by `imx_pinctrl_probe()` in the common core: MMIO mappings, pin register caches, parsed groups/functions, and optional input-select/GPR regmap references.
- No filesystem or on-disk persistence exists; applied pin state persists only in hardware registers/SCFW state until reset, suspend/resume, or a later pinctrl state switch.

## Dependencies And Integration Points
- Linux pinctrl core APIs (`pinctrl_pin_desc`, group/function maps, pinconf/pinmux callbacks).
- Platform bus and OF matching through `platform_driver`, `of_device_id`, and device-tree child nodes containing `fsl,pins`.
- Shared Freescale i.MX core declarations in `pinctrl-imx.h` and implementation in `pinctrl-imx.c`.
- NXP System Controller firmware IPC headers and runtime service.
- DT binding pad-id header included directly for SCU pad constants.

## File-Specific Notes
This is an SCU-backed i.MX8 driver: `.flags = IMX_USE_SCU` selects the SCU parse/config callbacks (`imx_pinctrl_parse_pin_scu`, `imx_pinconf_get_scu`, `imx_pinconf_set_scu`) and the probe initializes firmware IPC with `imx_pinctrl_sc_ipc_init()` before registering with the common core. Pinmux and pad config are therefore applied together through SCFW rather than direct IOMUXC writes.

The file includes module alias/metadata even though registration uses `arch_initcall`, which helps module autoload metadata when the driver is built as a module in compatible trees.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.
- SCU probe depends on firmware IPC availability; failures from `imx_pinctrl_sc_ipc_init()` abort registration before any pin states can be applied.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx8qxp.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx8qxp-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx8qxp` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.
- Test firmware-not-ready or unavailable SCU IPC paths because probe should fail cleanly before registering a partially functional pin controller.
