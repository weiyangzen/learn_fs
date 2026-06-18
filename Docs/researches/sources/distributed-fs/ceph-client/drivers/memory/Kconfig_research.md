# sources/distributed-fs/ceph-client/drivers/memory/Kconfig

## Purpose
This Kconfig file defines the Linux memory-controller driver menu and configuration symbols for embedded DRAM, SRAM, external bus, static memory controller, memory fabric, and SoC-specific memory-controller support.

## Important APIs, Types, And Functions
The top-level `menuconfig MEMORY` gates the menu. Symbols include generic `DDR`, platform drivers such as `ATMEL_EBI`, `BRCMSTB_DPFE`, `BRCMSTB_MEMC`, `TI_AEMIF`, `TI_EMIF`, `OMAP_GPMC`, `FSL_CORENET_CF`, `FSL_IFC`, `MVEBU_DEVBUS`, `JZ4780_NEMC`, `MTK_SMI`, `DA8XX_DDRCTL`, `PL353_SMC`, `RENESAS_RPCIF`, `STM32_FMC2_EBI`, `STM32_OMM`, plus `TI_EMIF_SRAM` and `FPGA_DFL_EMIF`. It sources Samsung and Tegra submenus.

## Control Flow
Kconfig evaluation first exposes the memory controller menu, then conditionally offers drivers according to architecture, OF, AMBA, SRAM, FPGA, HAS_IOMEM, and COMPILE_TEST dependencies. Several symbols select helper subsystems: `ATMEL_EBI` selects syscon and Atmel SMC MFD support; `TI_EMIF` selects `DDR`; `OMAP_GPMC` selects `GPIOLIB`; `RENESAS_RPCIF` selects regmap MMIO and reset controller.

## State And Persistence
The persistent output is kernel configuration state. These symbols determine which objects the Makefile compiles and which dependencies must be enabled. There is no runtime state in the file.

## Dependencies And Integration Points
It integrates with the kernel Kconfig system, architecture symbols, driver submenus, and the sibling Makefile. Help text describes user-visible purpose for each driver and constrains build coverage through `COMPILE_TEST`.

## Risks And Test Signals
Risks include missing dependencies causing randconfig build failures, over-restrictive dependencies hiding valid drivers, incorrect default selections, and stale help text. Test signals include `allyesconfig`, `allmodconfig`, architecture defconfigs, and randconfig builds across ARM, ARM64, MIPS, and COMPILE_TEST configurations.
# sources/distributed-fs/ceph-client/drivers/memory/Kconfig

## Purpose
This Kconfig file defines the Linux memory-controller driver menu and configuration symbols for embedded DRAM, SRAM, external bus, static memory controller, memory fabric, and SoC-specific memory-controller support.

## Important APIs, Types, And Functions
The top-level `menuconfig MEMORY` gates the menu. Symbols include generic `DDR`, platform drivers such as `ATMEL_EBI`, `BRCMSTB_DPFE`, `BRCMSTB_MEMC`, `TI_AEMIF`, `TI_EMIF`, `OMAP_GPMC`, `FSL_CORENET_CF`, `FSL_IFC`, `MVEBU_DEVBUS`, `JZ4780_NEMC`, `MTK_SMI`, `DA8XX_DDRCTL`, `PL353_SMC`, `RENESAS_RPCIF`, `STM32_FMC2_EBI`, `STM32_OMM`, plus `TI_EMIF_SRAM` and `FPGA_DFL_EMIF`. It sources Samsung and Tegra submenus.

## Control Flow
Kconfig evaluation first exposes the memory controller menu, then conditionally offers drivers according to architecture, OF, AMBA, SRAM, FPGA, HAS_IOMEM, and COMPILE_TEST dependencies. Several symbols select helper subsystems: `ATMEL_EBI` selects syscon and Atmel SMC MFD support; `TI_EMIF` selects `DDR`; `OMAP_GPMC` selects `GPIOLIB`; `RENESAS_RPCIF` selects regmap MMIO and reset controller.

## State And Persistence
The persistent output is kernel configuration state. These symbols determine which objects the Makefile compiles and which dependencies must be enabled. There is no runtime state in the file.

## Dependencies And Integration Points
It integrates with the kernel Kconfig system, architecture symbols, driver submenus, and the sibling Makefile. Help text describes user-visible purpose for each driver and constrains build coverage through `COMPILE_TEST`.

## Risks And Test Signals
Risks include missing dependencies causing randconfig build failures, over-restrictive dependencies hiding valid drivers, incorrect default selections, and stale help text. Test signals include `allyesconfig`, `allmodconfig`, architecture defconfigs, and randconfig builds across ARM, ARM64, MIPS, and COMPILE_TEST configurations.
