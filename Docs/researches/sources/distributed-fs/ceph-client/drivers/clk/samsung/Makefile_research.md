# sources/distributed-fs/ceph-client/drivers/clk/samsung/Makefile

Purpose: build manifest for Samsung common clock drivers. It maps Kconfig symbols to object files.

Important APIs/types/functions: core Samsung clock helpers `clk.o`, `clk-pll.o`, and `clk-cpu.o` build under `CONFIG_COMMON_CLK`. SoC-specific objects build under their corresponding symbols, including Exynos 3250/4/5250/5260/5410/5420, ARM64 Exynos/Artpec/GS101/Auto variants, audio subsystem, clock output, ACPM, S3C64xx, S5PV210, and Tesla FSD.

Control flow: no runtime logic. Kbuild appends objects to `obj-y`/`obj-m` according to the resolved configuration.

State and persistence: build artifact selection only.

Dependencies and integration: must match symbols from `Kconfig` and source files present in the Samsung clock directory. `CONFIG_EXYNOS_ARM64_COMMON_CLK` fans out to many ARM64-family SoC files, while `CONFIG_EXYNOS_ACPM_CLK` adds `clk-acpm.o`.

Risks: stale symbol/object mappings cause missing drivers or build failures. `CONFIG_COMMON_CLK` always building base Samsung helpers means compile errors there affect all configurations with common clock enabled. Shared objects such as `clk-exynos5-subcmu.o` are included by multiple SoC configs.

Test signals: Kbuild coverage for each symbol, `make drivers/clk/samsung/` under representative configs, and checking that new Kconfig entries update this file.
