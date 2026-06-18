# subset-b-005050 Research

Grouped research for Freescale/NXP i.MX pinctrl SoC driver files under `sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx50.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx51.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx51.c

## Purpose
`pinctrl-imx51.c` binds the NXP/Freescale IMX51 IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx51_pinctrl_pads` (367 pins). Pad coverage includes GPIO, UART, I2C, SD/SDHC, NAND, CSI/camera, display, audio, USB.
- SoC info: `imx51_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx51-iomuxc`.
- Platform driver: `imx51-pinctrl` via `imx51_pinctrl_driver`; registered by `arch_initcall(imx51_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx51_pinctrl_pads` starts with `MX51_PAD_RESERVE0`, `MX51_PAD_RESERVE1`, `MX51_PAD_RESERVE2`, `MX51_PAD_RESERVE3` and ends with `MX51_PAD_RESERVE120`, `MX51_PAD_RESERVE121`, `MX51_PAD_CSI1_PIXCLK`, `MX51_PAD_CSI1_MCLK`.

## Control Flow
- `imx51_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx51_pinctrl_info``.
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
There are no local register programming functions; all pin parsing and MMIO writes are delegated to the generic i.MX pinctrl core.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx51.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx51-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx51` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx51.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx53.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx53.c

## Purpose
`pinctrl-imx53.c` binds the NXP/Freescale IMX53 IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx53_pinctrl_pads` (210 pins). Pad coverage includes GPIO, SD/SDHC, NAND, CSI/camera, display.
- SoC info: `imx53_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx53-iomuxc`.
- Platform driver: `imx53-pinctrl` via `imx53_pinctrl_driver`; registered by `arch_initcall(imx53_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx53_pinctrl_pads` starts with `MX53_PAD_RESERVE0`, `MX53_PAD_RESERVE1`, `MX53_PAD_RESERVE2`, `MX53_PAD_RESERVE3` and ends with `MX53_PAD_GPIO_8`, `MX53_PAD_GPIO_16`, `MX53_PAD_GPIO_17`, `MX53_PAD_GPIO_18`.

## Control Flow
- `imx53_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx53_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx53-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx53.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx53-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx53` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx53.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6dl.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6dl.c

## Purpose
`pinctrl-imx6dl.c` binds the NXP/Freescale IMX6DL IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx6dl_pinctrl_pads` (216 pins). Pad coverage includes GPIO, SD/SDHC, Ethernet, NAND, CSI/camera, display.
- SoC info: `imx6dl_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx6dl-iomuxc`.
- Platform driver: `imx6dl-pinctrl` via `imx6dl_pinctrl_driver`; registered by `arch_initcall(imx6dl_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx6dl_pinctrl_pads` starts with `MX6DL_PAD_RESERVE0`, `MX6DL_PAD_RESERVE1`, `MX6DL_PAD_RESERVE2`, `MX6DL_PAD_RESERVE3` and ends with `MX6DL_PAD_SD4_DAT4`, `MX6DL_PAD_SD4_DAT5`, `MX6DL_PAD_SD4_DAT6`, `MX6DL_PAD_SD4_DAT7`.

## Control Flow
- `imx6dl_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx6dl_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx6q-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx6dl.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx6dl-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx6dl` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6dl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6q.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6q.c

## Purpose
`pinctrl-imx6q.c` binds the NXP/Freescale IMX6Q IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx6q_pinctrl_pads` (216 pins). Pad coverage includes GPIO, SD/SDHC, Ethernet, NAND, CSI/camera, display.
- SoC info: `imx6q_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx6q-iomuxc`.
- Platform driver: `imx6q-pinctrl` via `imx6q_pinctrl_driver`; registered by `arch_initcall(imx6q_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx6q_pinctrl_pads` starts with `MX6Q_PAD_RESERVE0`, `MX6Q_PAD_RESERVE1`, `MX6Q_PAD_RESERVE2`, `MX6Q_PAD_RESERVE3` and ends with `MX6Q_PAD_SD1_CLK`, `MX6Q_PAD_SD2_CLK`, `MX6Q_PAD_SD2_CMD`, `MX6Q_PAD_SD2_DAT3`.

## Control Flow
- `imx6q_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx6q_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx6q-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx6q.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx6q-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx6q` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6sl.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6sl.c

## Purpose
`pinctrl-imx6sl.c` binds the NXP/Freescale IMX6SL IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx6sl_pinctrl_pads` (169 pins). Pad coverage includes UART, SPI, I2C, SD/SDHC, LCD/display, EPDC, PWM, audio.
- SoC info: `imx6sl_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx6sl-iomuxc`.
- Platform driver: `imx6sl-pinctrl` via `imx6sl_pinctrl_driver`; registered by `arch_initcall(imx6sl_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx6sl_pinctrl_pads` starts with `MX6SL_PAD_RESERVE0`, `MX6SL_PAD_RESERVE1`, `MX6SL_PAD_RESERVE2`, `MX6SL_PAD_RESERVE3` and ends with `MX6SL_PAD_SD3_DAT3`, `MX6SL_PAD_UART1_RXD`, `MX6SL_PAD_UART1_TXD`, `MX6SL_PAD_WDOG_B`.

## Control Flow
- `imx6sl_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx6sl_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx6sl-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx6sl.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx6sl-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx6sl` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6sl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6sll.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6sll.c

## Purpose
`pinctrl-imx6sll.c` binds the NXP/Freescale IMX6SLL IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx6sll_pinctrl_pads` (153 pins). Pad coverage includes GPIO, UART, SPI, I2C, SD/SDHC, LCD/display, EPDC, PWM, audio.
- SoC info: `imx6sll_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx6sll-iomuxc` -> `imx6sll_pinctrl_info`.
- Platform driver: `imx6sll-pinctrl` via `imx6sll_pinctrl_driver`; registered by `arch_initcall(imx6sll_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/module.h`, `linux/mod_devicetable.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx6sll_pinctrl_pads` starts with `MX6SLL_PAD_RESERVE0`, `MX6SLL_PAD_RESERVE1`, `MX6SLL_PAD_RESERVE2`, `MX6SLL_PAD_RESERVE3` and ends with `MX6SLL_PAD_GPIO4_IO17`, `MX6SLL_PAD_GPIO4_IO22`, `MX6SLL_PAD_GPIO4_IO16`, `MX6SLL_PAD_GPIO4_IO26`.

## Control Flow
- `imx6sll_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx6sll_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx6sll-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx6sll.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx6sll-iomuxc` -> `imx6sll_pinctrl_info`; `/sys/kernel/debug/pinctrl/` should show the `imx6sll` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6sll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6sx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6sx.c

## Purpose
`pinctrl-imx6sx.c` binds the NXP/Freescale IMX6SX IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx6sx_pinctrl_pads` (171 pins). Pad coverage includes GPIO, SD/SDHC, Ethernet, NAND, CSI/camera, LCD/display, USB, QSPI.
- SoC info: `imx6sx_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx6sx-iomuxc`.
- Platform driver: `imx6sx-pinctrl` via `imx6sx_pinctrl_driver`; registered by `arch_initcall(imx6sx_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx6sx_pinctrl_pads` starts with `MX6Sx_PAD_RESERVE0`, `MX6Sx_PAD_RESERVE1`, `MX6Sx_PAD_RESERVE2`, `MX6Sx_PAD_RESERVE3` and ends with `MX6SX_PAD_SD4_DATA7`, `MX6SX_PAD_SD4_RESET_B`, `MX6SX_PAD_USB_H_DATA`, `MX6SX_PAD_USB_H_STROBE`.

## Control Flow
- `imx6sx_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx6sx_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx6sx-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx6sx.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx6sx-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx6sx` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6sx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6ul.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6ul.c

## Purpose
`pinctrl-imx6ul.c` binds the NXP/Freescale IMX6UL IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx6ul_pinctrl_pads` (129 pins), `imx6ull_snvs_pinctrl_pads` (12 pins). Pad coverage includes GPIO, UART, SD/SDHC, Ethernet, NAND, CSI/camera, LCD/display, JTAG, SNVS, boot mode, tamper.
- SoC info: `imx6ul_pinctrl_info`, `imx6ull_snvs_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx6ul-iomuxc` -> `imx6ul_pinctrl_info`, `fsl,imx6ull-iomuxc-snvs` -> `imx6ull_snvs_pinctrl_info`.
- Platform driver: `imx6ul-pinctrl` via `imx6ul_pinctrl_driver`; registered by `arch_initcall(imx6ul_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/of.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx6ul_pinctrl_pads` starts with `MX6UL_PAD_RESERVE0`, `MX6UL_PAD_RESERVE1`, `MX6UL_PAD_RESERVE2`, `MX6UL_PAD_RESERVE3` and ends with `MX6UL_PAD_CSI_DATA04`, `MX6UL_PAD_CSI_DATA05`, `MX6UL_PAD_CSI_DATA06`, `MX6UL_PAD_CSI_DATA07`. `imx6ull_snvs_pinctrl_pads` starts with `MX6ULL_PAD_BOOT_MODE0`, `MX6ULL_PAD_BOOT_MODE1`, `MX6ULL_PAD_SNVS_TAMPER0`, `MX6ULL_PAD_SNVS_TAMPER1` and ends with `MX6ULL_PAD_SNVS_TAMPER6`, `MX6ULL_PAD_SNVS_TAMPER7`, `MX6ULL_PAD_SNVS_TAMPER8`, `MX6ULL_PAD_SNVS_TAMPER9`.

## Control Flow
- `imx6ul_pinctrl_probe()` fetches the SoC info from OF match data, returns `-ENODEV` if missing, then calls `imx_pinctrl_probe()`.
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
The probe uses `of_device_get_match_data()` so multiple compatible entries can select different `imx_pinctrl_soc_info` tables from one platform driver.

The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx6ul-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

`ZERO_OFFSET_VALID` is present for this controller, so a mux offset of zero is treated as a real register rather than converted to `NO_MUX`; this matters for low-power/SNVS/LPSR or newer IOMUX layouts whose first pad is at offset 0.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.
- Every OF match entry must carry a valid `.data` pointer; the probe returns `-ENODEV` when match data is missing.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx6ul.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx6ul-iomuxc` -> `imx6ul_pinctrl_info`, `fsl,imx6ull-iomuxc-snvs` -> `imx6ull_snvs_pinctrl_info`; `/sys/kernel/debug/pinctrl/` should show the `imx6ul` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx6ul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx7d.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx7d.c

## Purpose
`pinctrl-imx7d.c` binds the NXP/Freescale IMX7D IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx7d_pinctrl_pads` (155 pins), `imx7d_lpsr_pinctrl_pads` (8 pins). Pad coverage includes GPIO, UART, SPI, I2C, SD/SDHC, Ethernet, LCD/display, EPDC, SAI/audio.
- SoC info: `imx7d_pinctrl_info`, `imx7d_lpsr_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx7d-iomuxc` -> `imx7d_pinctrl_info`, `fsl,imx7d-iomuxc-lpsr` -> `imx7d_lpsr_pinctrl_info`.
- Platform driver: `imx7d-pinctrl` via `imx7d_pinctrl_driver`; registered by `arch_initcall(imx7d_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/of.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx7d_pinctrl_pads` starts with `MX7D_PAD_RESERVE0`, `MX7D_PAD_RESERVE1`, `MX7D_PAD_RESERVE2`, `MX7D_PAD_RESERVE3` and ends with `MX7D_PAD_ENET1_TX_CLK`, `MX7D_PAD_ENET1_RX_CLK`, `MX7D_PAD_ENET1_CRS`, `MX7D_PAD_ENET1_COL`. `imx7d_lpsr_pinctrl_pads` starts with `MX7D_PAD_GPIO1_IO00`, `MX7D_PAD_GPIO1_IO01`, `MX7D_PAD_GPIO1_IO02`, `MX7D_PAD_GPIO1_IO03` and ends with `MX7D_PAD_GPIO1_IO04`, `MX7D_PAD_GPIO1_IO05`, `MX7D_PAD_GPIO1_IO06`, `MX7D_PAD_GPIO1_IO07`.

## Control Flow
- `imx7d_pinctrl_probe()` fetches the SoC info from OF match data, returns `-ENODEV` if missing, then calls `imx_pinctrl_probe()`.
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
The probe uses `of_device_get_match_data()` so multiple compatible entries can select different `imx_pinctrl_soc_info` tables from one platform driver.

The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx7d-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

`ZERO_OFFSET_VALID` is present for this controller, so a mux offset of zero is treated as a real register rather than converted to `NO_MUX`; this matters for low-power/SNVS/LPSR or newer IOMUX layouts whose first pad is at offset 0.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.
- Every OF match entry must carry a valid `.data` pointer; the probe returns `-ENODEV` when match data is missing.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx7d.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx7d-iomuxc` -> `imx7d_pinctrl_info`, `fsl,imx7d-iomuxc-lpsr` -> `imx7d_lpsr_pinctrl_info`; `/sys/kernel/debug/pinctrl/` should show the `imx7d` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx7d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx7ulp.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx7ulp.c

## Purpose
`pinctrl-imx7ulp.c` binds the NXP/Freescale IMX7ULP IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx7ulp_pinctrl_pads` (116 pins). Pad coverage includes PTC bank, PTD bank, PTE bank, PTF bank.
- SoC info: `imx7ulp_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx7ulp-iomuxc1`.
- Platform driver: `imx7ulp-pinctrl` via `imx7ulp_pinctrl_driver`; registered by `arch_initcall(imx7ulp_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/platform_device.h`, `linux/pinctrl/pinctrl.h`.
- Pad-table edge samples: `imx7ulp_pinctrl_pads` starts with `IMX7ULP_PAD_PTC0`, `IMX7ULP_PAD_PTC1`, `IMX7ULP_PAD_PTC2`, `IMX7ULP_PAD_PTC3` and ends with `IMX7ULP_PAD_PTF16`, `IMX7ULP_PAD_PTF17`, `IMX7ULP_PAD_PTF18`, `IMX7ULP_PAD_PTF19`.

## Control Flow
- `imx7ulp_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx7ulp_pinctrl_info``.
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
This ULP-style controller uses shared mux/config registers. `ZERO_OFFSET_VALID | SHARE_MUX_CONF_REG` makes offset zero a valid pad register and tells the common parser that the mux and config offsets are the same cell. The local GPIO direction helper toggles `BM_IBE_ENABLED`/`BM_OBE_ENABLED` while `mux_mask = BM_MUX_MODE` and `mux_shift = BP_MUX_MODE` preserve mux bits during config writes.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.
- Shared mux/config writes must preserve `BM_MUX_MODE`; mistakes in mask or shift values would corrupt mux selection while applying pad config or GPIO direction.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx7ulp.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx7ulp-iomuxc1`; `/sys/kernel/debug/pinctrl/` should show the `imx7ulp` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.
- For GPIO pads, switch directions through gpiolib and verify the IBE/OBE bits change without altering mux mode bits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx7ulp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8dxl.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8dxl.c

## Purpose
`pinctrl-imx8dxl.c` binds the NXP/Freescale IMX8DXL IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx8dxl_pinctrl_pads` (136 pins). Pad coverage includes GPIO, UART, I2C, USDHC, SD/SDHC, Ethernet, NAND, JTAG, USB, CAN, PCIe, QSPI.
- SoC info: `imx8dxl_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx8dxl-iomuxc`.
- Platform driver: `fsl,imx8dxl-iomuxc` via `imx8dxl_pinctrl_driver`; registered by `arch_initcall(imx8dxl_pinctrl_init)`.
- Notable includes: `dt-bindings/pinctrl/pads-imx8dxl.h`, `linux/err.h`, `linux/firmware/imx/sci.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/module.h`, `linux/pinctrl/pinctrl.h`, `linux/platform_device.h`.
- Pad-table edge samples: `imx8dxl_pinctrl_pads` starts with `IMX8DXL_PCIE_CTRL0_PERST_B`, `IMX8DXL_PCIE_CTRL0_CLKREQ_B`, `IMX8DXL_PCIE_CTRL0_WAKE_B`, `IMX8DXL_COMP_CTL_GPIO_1V8_3V3_PCIESEP` and ends with `IMX8DXL_QSPI0B_DATA3`, `IMX8DXL_QSPI0B_DATA2`, `IMX8DXL_QSPI0B_SS0_B`, `IMX8DXL_COMP_CTL_GPIO_1V8_3V3_QSPI0B`.

## Control Flow
- `imx8dxl_pinctrl_probe()` initializes SCU IPC, propagates any error, then calls `imx_pinctrl_probe()` with ``imx8dxl_pinctrl_info``.
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
- Build with the Kconfig option that includes `pinctrl-imx8dxl.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx8dxl-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx8dxl` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.
- Test firmware-not-ready or unavailable SCU IPC paths because probe should fail cleanly before registering a partially functional pin controller.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8dxl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mm.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mm.c

## Purpose
`pinctrl-imx8mm.c` binds the NXP/Freescale IMX8MM IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx8mm_pinctrl_pads` (149 pins). Pad coverage includes GPIO, UART, SPI, I2C, SD/SDHC, Ethernet, NAND, SAI/audio.
- SoC info: `imx8mm_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx8mm-iomuxc` -> `imx8mm_pinctrl_info`.
- Platform driver: `imx8mm-pinctrl` via `imx8mm_pinctrl_driver`; registered by `arch_initcall(imx8mm_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/module.h`, `linux/of.h`, `linux/pinctrl/pinctrl.h`, `linux/platform_device.h`.
- Pad-table edge samples: `imx8mm_pinctrl_pads` starts with `MX8MM_PAD_RESERVE0`, `MX8MM_PAD_RESERVE1`, `MX8MM_PAD_RESERVE2`, `MX8MM_PAD_RESERVE3` and ends with `MX8MM_IOMUXC_UART3_RXD`, `MX8MM_IOMUXC_UART3_TXD`, `MX8MM_IOMUXC_UART4_RXD`, `MX8MM_IOMUXC_UART4_TXD`.

## Control Flow
- `imx8mm_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx8mm_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx8mm-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

The file includes module alias/metadata even though registration uses `arch_initcall`, which helps module autoload metadata when the driver is built as a module in compatible trees.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx8mm.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx8mm-iomuxc` -> `imx8mm_pinctrl_info`; `/sys/kernel/debug/pinctrl/` should show the `imx8mm` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mn.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mn.c

## Purpose
`pinctrl-imx8mn.c` binds the NXP/Freescale IMX8MN IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx8mn_pinctrl_pads` (149 pins). Pad coverage includes GPIO, UART, SPI, I2C, SD/SDHC, Ethernet, NAND, SAI/audio, boot mode.
- SoC info: `imx8mn_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx8mn-iomuxc` -> `imx8mn_pinctrl_info`.
- Platform driver: `imx8mn-pinctrl` via `imx8mn_pinctrl_driver`; registered by `arch_initcall(imx8mn_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/module.h`, `linux/of.h`, `linux/pinctrl/pinctrl.h`, `linux/platform_device.h`.
- Pad-table edge samples: `imx8mn_pinctrl_pads` starts with `MX8MN_PAD_RESERVE0`, `MX8MN_PAD_RESERVE1`, `MX8MN_PAD_RESERVE2`, `MX8MN_PAD_RESERVE3` and ends with `MX8MN_IOMUXC_UART3_RXD`, `MX8MN_IOMUXC_UART3_TXD`, `MX8MN_IOMUXC_UART4_RXD`, `MX8MN_IOMUXC_UART4_TXD`.

## Control Flow
- `imx8mn_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx8mn_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx8mn-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

The file includes module alias/metadata even though registration uses `arch_initcall`, which helps module autoload metadata when the driver is built as a module in compatible trees.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx8mn.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx8mn-iomuxc` -> `imx8mn_pinctrl_info`; `/sys/kernel/debug/pinctrl/` should show the `imx8mn` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mp.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mp.c

## Purpose
`pinctrl-imx8mp.c` binds the NXP/Freescale IMX8MP IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx8mp_pinctrl_pads` (148 pins). Pad coverage includes GPIO, UART, SPI, I2C, SD/SDHC, Ethernet, NAND, SAI/audio.
- SoC info: `imx8mp_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx8mp-iomuxc` -> `imx8mp_pinctrl_info`.
- Platform driver: `imx8mp-pinctrl` via `imx8mp_pinctrl_driver`; registered by `arch_initcall(imx8mp_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/module.h`, `linux/of.h`, `linux/pinctrl/pinctrl.h`, `linux/platform_device.h`.
- Pad-table edge samples: `imx8mp_pinctrl_pads` starts with `MX8MP_IOMUXC_RESERVE0`, `MX8MP_IOMUXC_RESERVE1`, `MX8MP_IOMUXC_RESERVE2`, `MX8MP_IOMUXC_RESERVE3` and ends with `MX8MP_IOMUXC_HDMI_DDC_SCL`, `MX8MP_IOMUXC_HDMI_DDC_SDA`, `MX8MP_IOMUXC_HDMI_CEC`, `MX8MP_IOMUXC_HDMI_HPD`.

## Control Flow
- `imx8mp_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx8mp_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx8mp-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

The file includes module alias/metadata even though registration uses `arch_initcall`, which helps module autoload metadata when the driver is built as a module in compatible trees.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx8mp.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx8mp-iomuxc` -> `imx8mp_pinctrl_info`; `/sys/kernel/debug/pinctrl/` should show the `imx8mp` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mq.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mq.c

## Purpose
`pinctrl-imx8mq.c` binds the NXP/Freescale IMX8MQ IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx8mq_pinctrl_pads` (149 pins). Pad coverage includes GPIO, UART, SPI, I2C, SD/SDHC, Ethernet, NAND, SAI/audio, SNVS.
- SoC info: `imx8mq_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx8mq-iomuxc` -> `imx8mq_pinctrl_info`.
- Platform driver: `imx8mq-pinctrl` via `imx8mq_pinctrl_driver` with `imx_pinctrl_pm_ops`; registered by `arch_initcall(imx8mq_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/module.h`, `linux/pinctrl/pinctrl.h`, `linux/platform_device.h`.
- Pad-table edge samples: `imx8mq_pinctrl_pads` starts with `MX8MQ_PAD_RESERVE0`, `MX8MQ_PAD_RESERVE1`, `MX8MQ_PAD_RESERVE2`, `MX8MQ_PAD_RESERVE3` and ends with `MX8MQ_IOMUXC_UART3_RXD`, `MX8MQ_IOMUXC_UART3_TXD`, `MX8MQ_IOMUXC_UART4_RXD`, `MX8MQ_IOMUXC_UART4_TXD`.

## Control Flow
- `imx8mq_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx8mq_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx8mq-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

The file includes module alias/metadata even though registration uses `arch_initcall`, which helps module autoload metadata when the driver is built as a module in compatible trees.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx8mq.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx8mq-iomuxc` -> `imx8mq_pinctrl_info`; `/sys/kernel/debug/pinctrl/` should show the `imx8mq` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8mq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8qm.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8qm.c

## Purpose
`pinctrl-imx8qm.c` binds the NXP/Freescale IMX8QM IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx8qm_pinctrl_pads` (269 pins). Pad coverage includes GPIO, UART, I2C, USDHC, SD/SDHC, Ethernet, NAND, CSI/camera, SAI/audio, USB, CAN, PCIe.
- SoC info: `imx8qm_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx8qm-iomuxc`.
- Platform driver: `imx8qm-pinctrl` via `imx8qm_pinctrl_driver`; registered by `arch_initcall(imx8qm_pinctrl_init)`.
- Notable includes: `dt-bindings/pinctrl/pads-imx8qm.h`, `linux/err.h`, `linux/firmware/imx/sci.h`, `linux/init.h`, `linux/module.h`, `linux/of.h`, `linux/pinctrl/pinctrl.h`, `linux/platform_device.h`.
- Pad-table edge samples: `imx8qm_pinctrl_pads` starts with `IMX8QM_SIM0_CLK`, `IMX8QM_SIM0_RST`, `IMX8QM_SIM0_IO`, `IMX8QM_SIM0_PD` and ends with `IMX8QM_ENET1_RGMII_RXD1`, `IMX8QM_ENET1_RGMII_RXD2`, `IMX8QM_ENET1_RGMII_RXD3`, `IMX8QM_COMP_CTL_GPIO_1V8_3V3_ENET_ENETA`.

## Control Flow
- `imx8qm_pinctrl_probe()` initializes SCU IPC, propagates any error, then calls `imx_pinctrl_probe()` with ``imx8qm_pinctrl_info``.
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
- Build with the Kconfig option that includes `pinctrl-imx8qm.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx8qm-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx8qm` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.
- Test firmware-not-ready or unavailable SCU IPC paths because probe should fail cleanly before registering a partially functional pin controller.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8qm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8qxp.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8qxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8ulp.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8ulp.c

## Purpose
`pinctrl-imx8ulp.c` binds the NXP/Freescale IMX8ULP IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx8ulp_pinctrl_pads` (96 pins). Pad coverage includes PTD bank, PTE bank, PTF bank.
- SoC info: `imx8ulp_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx8ulp-iomuxc1`.
- Platform driver: `imx8ulp-pinctrl` via `imx8ulp_pinctrl_driver`; registered by `arch_initcall(imx8ulp_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/module.h`, `linux/pinctrl/pinctrl.h`, `linux/platform_device.h`.
- Pad-table edge samples: `imx8ulp_pinctrl_pads` starts with `IMX8ULP_PAD_PTD0`, `IMX8ULP_PAD_PTD1`, `IMX8ULP_PAD_PTD2`, `IMX8ULP_PAD_PTD3` and ends with `IMX8ULP_PAD_PTF28`, `IMX8ULP_PAD_PTF29`, `IMX8ULP_PAD_PTF30`, `IMX8ULP_PAD_PTF31`.

## Control Flow
- `imx8ulp_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx8ulp_pinctrl_info``.
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
This ULP-style controller uses shared mux/config registers. `ZERO_OFFSET_VALID | SHARE_MUX_CONF_REG` makes offset zero a valid pad register and tells the common parser that the mux and config offsets are the same cell. The local GPIO direction helper toggles `BM_IBE_ENABLED`/`BM_OBE_ENABLED` while `mux_mask = BM_MUX_MODE` and `mux_shift = BP_MUX_MODE` preserve mux bits during config writes.

The file includes module alias/metadata even though registration uses `arch_initcall`, which helps module autoload metadata when the driver is built as a module in compatible trees.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.
- Shared mux/config writes must preserve `BM_MUX_MODE`; mistakes in mask or shift values would corrupt mux selection while applying pad config or GPIO direction.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx8ulp.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx8ulp-iomuxc1`; `/sys/kernel/debug/pinctrl/` should show the `imx8ulp` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.
- For GPIO pads, switch directions through gpiolib and verify the IBE/OBE bits change without altering mux mode bits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx8ulp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx91.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx91.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx93.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx93.c

## Purpose
`pinctrl-imx93.c` binds the NXP/Freescale IMX93 IOMUXC device-tree compatible(s) to the generic i.MX pinctrl core. It contributes the SoC-specific pad namespace and registration metadata; the common core converts DTS `fsl,pins` groups into mux and pin configuration operations. These files are Freescale/NXP i.MX pinctrl platform drivers. Each source is intentionally small and data-heavy: it enumerates the pads exported by one SoC family, fills an `imx_pinctrl_soc_info`, exposes an OF compatible table, and registers a `platform_driver` at `arch_initcall` time. Runtime parsing, group/function registration, pinmux writes, pin configuration writes, debugfs display, and optional suspend/resume behavior live in the shared `pinctrl-imx.c` core and `pinctrl-imx.h` types. Device-tree `fsl,pins` entries are the persistent configuration source; the driver applies them to IOMUXC MMIO registers or, for SCU SoCs, through System Controller IPC during pinctrl state selection.

## Important APIs, Types, And Functions
- Pad table(s): `imx93_pinctrl_pads` (108 pins). Pad coverage includes GPIO, UART, I2C, SD/SDHC, Ethernet, SAI/audio.
- SoC info: `imx93_pinctrl_info`; key fields are `.pins`, `.npins`, optional `.flags`, `.gpr_compatible`, `.gpio_set_direction`, mux masks, and SCU callbacks.
- OF compatibles: `fsl,imx93-iomuxc`.
- Platform driver: `imx93-pinctrl` via `imx93_pinctrl_driver`; registered by `arch_initcall(imx93_pinctrl_init)`.
- Notable includes: `linux/err.h`, `linux/init.h`, `linux/io.h`, `linux/mod_devicetable.h`, `linux/module.h`, `linux/pinctrl/pinctrl.h`, `linux/platform_device.h`.
- Pad-table edge samples: `imx93_pinctrl_pads` starts with `IMX93_IOMUXC_DAP_TDI`, `IMX93_IOMUXC_DAP_TMS_SWDIO`, `IMX93_IOMUXC_DAP_TCLK_SWCLK`, `IMX93_IOMUXC_DAP_TDO_TRACESWO` and ends with `IMX93_IOMUXC_SAI1_TXC`, `IMX93_IOMUXC_SAI1_TXD0`, `IMX93_IOMUXC_SAI1_RXD0`, `IMX93_IOMUXC_WDOG_ANY`.

## Control Flow
- `imx93_pinctrl_probe()` directly calls `imx_pinctrl_probe()` with ``imx93_pinctrl_info``.
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
The info advertises the IOMUXC GPR syscon compatible(s) `fsl,imx93-iomuxc-gpr`, which lets the common core handle select-input fields encoded into general-purpose IOMUXC registers.

`ZERO_OFFSET_VALID` is present for this controller, so a mux offset of zero is treated as a real register rather than converted to `NO_MUX`; this matters for low-power/SNVS/LPSR or newer IOMUX layouts whose first pad is at offset 0.

The file includes module alias/metadata even though registration uses `arch_initcall`, which helps module autoload metadata when the driver is built as a module in compatible trees.

## Risks And Edge Cases
- Pad enum order and `IMX_PINCTRL_PIN()` table order are part of the ABI with device-tree pin IDs; inserting, deleting, or reordering entries can silently program the wrong pad.
- Compatible strings must match binding and DTS names exactly; a mismatch prevents the platform driver from probing and leaves consumers without their pin states.
- The shared core derives register offsets and pin IDs from `fsl,pins` cells, so malformed DTS values can produce bad mux/config writes even when this C file compiles cleanly.

## Test Signals
- Build with the Kconfig option that includes `pinctrl-imx93.c` and check for compile coverage of the pad enum/table, OF table, and probe function.
- Boot a DTS containing `fsl,imx93-iomuxc`; `/sys/kernel/debug/pinctrl/` should show the `imx93` controller, groups parsed from child nodes, and pad config values.
- Exercise pinctrl state transitions for UART/I2C/SPI/USDHC/GPIO-style consumers and confirm mux register writes or SCU calls select the expected hardware function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx93.c -->
