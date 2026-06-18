# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx50.c

## Purpose
`pinctrl-imx50.c` binds the NXP/Freescale IMX50 IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx50_pinctrl_pads` (179 pins). Pad coverage includes UART, SPI, I2C, SD/SDHC, display, EPDC, PWM.
- SoC info: `imx50_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx50-iomuxc`.
- Platform driver: `imx50-pinctrl` via `imx50_pinctrl_driver`; registered by `arch_initcall(imx50_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx50_pinctrl_pads` starts with `MX50_PAD_RESERVE0`, `MX50_PAD_RESERVE1`, `MX50_PAD_RESERVE2`, `MX50_PAD_RESERVE3` and ends with `MX50_PAD_EIM_OE`, `MX50_PAD_EIM_RW`, `MX50_PAD_EIM_LBA`, `MX50_PAD_EIM_CRE`.

## Control Flow
- `imx50_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx50_pinctrl_info``.
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
- IOMUXC GPR syscon compatible used by select-input quirks.

## File-Specific Notes
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx50-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx50.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx50-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx50` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.
