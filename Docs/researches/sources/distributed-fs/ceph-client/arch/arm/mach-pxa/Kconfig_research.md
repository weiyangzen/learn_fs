<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Kconfig

Purpose: Kconfig menu for Intel/Marvell PXA2xx/PXA3xx ARM platforms. It selects common CPU, GPIO, timer, power, and platform support, and gates DT and legacy ATAGS boards.

Important symbols: `ARCH_PXA` depends on `ARCH_MULTI_V5` and little endian and selects `PLAT_PXA`, `GPIO_PXA`, clocksource, and suspend support. DT machine symbols are `MACH_PXA25X_DT`, `MACH_PXA27X_DT`, and `MACH_PXA3XX_DT`. Legacy board symbols under `ATAGS` include `ARCH_GUMSTIX`, `GUMSTIX_AM200EPD`, `GUMSTIX_AM300EPD`, `PXA_SHARPSL`, and Zaurus variants. Internal SoC symbols include `PXA25x`, `PXA27x`, `PXA3xx`, `CPU_PXA300`, `CPU_PXA310`, and `CPU_PXA320`.

Control flow: this file does not execute; it shapes compilation. The DT options select SoC support and `USE_OF`; legacy board options select board files and dependent subsystems. The CPU symbols are selected by machines rather than usually presented directly.

State and persistence: build configuration persists in `.config`; no runtime state.

Dependencies and integration: consumed by `arch/arm/mach-pxa/Makefile`, SoC init code, and board files. It also selects external subsystems such as I2C, SPI, HWMON, APM emulation, and Sharp-specific platform components.

Risks and test signals: wrong selects can omit required init objects or include incompatible legacy board code. Test with representative defconfigs for DT PXA25x/PXA27x/PXA3xx and legacy Gumstix/Zaurus, checking that expected objects build and machine descriptors are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Kconfig -->
