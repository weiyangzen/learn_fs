# sources/distributed-fs/ceph-client/drivers/clk/microchip/Kconfig

Purpose: This Kconfig fragment controls Microchip clock driver build options for legacy PIC32 and PolarFire SoC MPFS support.

Important APIs, types, and functions: It defines `COMMON_CLK_PIC32` as a default boolean when `COMMON_CLK && MACH_PIC32`, and `MCHP_CLK_MPFS` as the user-visible PolarFire SoC clock option. `MCHP_CLK_MPFS` depends on `ARCH_MICROCHIP || COMPILE_TEST`, defaults to `y`, requires `MFD_SYSCON`, and selects `AUXILIARY_BUS` and `REGMAP_MMIO`.

Control flow: Kconfig selection determines which objects in the Microchip clock Makefile are compiled. There is no runtime behavior in this file.

State and persistence behavior: The state is build configuration only. It affects the resulting kernel image or module set, not runtime persistence.

Dependencies and integration points: `COMMON_CLK_PIC32` enables shared PIC32 clock core compilation for PIC32 SoCs. `MCHP_CLK_MPFS` enables both MPFS MSS clock configuration and MPFS CCC drivers and ensures their syscon/regmap infrastructure is present.

Risks and edge cases: The default-yes MPFS option can build in COMPILE_TEST contexts but depends on required headers and dt-bindings being available. `COMMON_CLK_PIC32` is not user-prompted here, so PIC32 platform symbols drive it. Test signals include `allmodconfig`, `allyesconfig`, PIC32 builds, MPFS builds with `MFD_SYSCON`, and COMPILE_TEST builds on non-Microchip architectures.
