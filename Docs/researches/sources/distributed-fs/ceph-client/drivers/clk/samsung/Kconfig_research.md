# sources/distributed-fs/ceph-client/drivers/clk/samsung/Kconfig

Purpose: Kconfig menu for Samsung clock-controller support. It defines umbrella and SoC-specific symbols for Exynos, S3C64xx, S5PV210, Tesla FSD, audio subsystem, clock output, and ACPM firmware-controlled clocks.

Important APIs/types/functions: configuration symbols include `COMMON_CLK_SAMSUNG`, `S3C64XX_COMMON_CLK`, `S5PV210_COMMON_CLK`, `EXYNOS_3250_COMMON_CLK`, `EXYNOS_4_COMMON_CLK`, `EXYNOS_5250_COMMON_CLK`, `EXYNOS_5260_COMMON_CLK`, `EXYNOS_5410_COMMON_CLK`, `EXYNOS_5420_COMMON_CLK`, `EXYNOS_ARM64_COMMON_CLK`, `EXYNOS_AUDSS_CLK_CON`, `EXYNOS_CLKOUT`, `EXYNOS_ACPM_CLK`, and `TESLA_FSD_COMMON_CLK`.

Control flow: no runtime flow. Kconfig dependency and select logic controls which clock driver objects compile. `COMMON_CLK_SAMSUNG` depends on OF and selects the right SoC clocks based on architecture symbols.

State and persistence: build-time configuration only; no runtime state.

Dependencies and integration: architecture symbols such as `ARCH_EXYNOS`, `SOC_EXYNOS*`, `ARCH_S3C64XX`, `ARCH_S5PV210`, `ARCH_TESLA_FSD`, `ARM`, `ARM64`, `COMPILE_TEST`, and ACPM protocol availability.

Risks: `select` can force lower-level symbols, so dependency mistakes may compile drivers on unsupported architectures. `EXYNOS_ACPM_CLK` allows compile testing without `EXYNOS_ACPM_PROTOCOL`, so runtime users still need the firmware protocol. Help text contains minor typos but no behavior.

Test signals: `allyesconfig`/`allmodconfig`/`COMPILE_TEST` builds, Exynos platform defconfig builds, and ensuring `CONFIG_EXYNOS_ACPM_CLK=m/y` pulls `clk-acpm.o` only when intended.
