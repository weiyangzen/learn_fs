# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx91.c

## Purpose
`pinctrl-imx91.c` binds the NXP/Freescale IMX91 IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx91_pinctrl_pads` (108 pins). Pad coverage includes GPIO, UART, I2C, SD/SDHC, Ethernet, SAI/audio.
- SoC info: `imx91_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx91-iomuxc`.
- Platform driver: `imx91-pinctrl` via `imx91_pinctrl_driver`; registered by `arch_initcall(imx91_pinctrl_init)`.
- Notable includes: `linux/init.h`, `linux/mod_devicetable.h`, `linux/module.h`, `linux/pinctrl/pinctrl.h`, `linux/platform_device.h`.
- Pad-table edge samples: `imx91_pinctrl_pads` starts with `IMX91_PAD_DAP_TDI`, `IMX91_PAD_DAP_TMS_SWDIO`, `IMX91_PAD_DAP_TCLK_SWCLK`, `IMX91_PAD_DAP_TDO_TRACESWO` and ends with `IMX91_PAD_SAI1_TXC`, `IMX91_PAD_SAI1_TXD0`, `IMX91_PAD_SAI1_RXD0`, `IMX91_PAD_WDOG_ANY`.

## Control Flow
- `imx91_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx91_pinctrl_info``.
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

## File-Specific Notes
`ZERO_OFFSET_VALID` is present for this controller, so a mux offset of zero is treated as a real register rather than converted to `NO_MUX`; this matters for low-power/SNVS/LPSR or newer IOMUX layouts whose first pad is at offset 0.

The file includes module alias/metadata even though registration uses `arch_initcall`, which helps module autoload metadata when the driver is built as a module in compatible trees.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx91.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx91-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx91` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.
