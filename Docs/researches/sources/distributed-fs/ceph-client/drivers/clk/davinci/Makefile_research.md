# sources/distributed-fs/ceph-client/drivers/clk/davinci/Makefile

Purpose: builds TI DaVinci clock-controller objects only when the common clock framework is enabled.

Important APIs/types/functions: make variables add `da8xx-cfgchip.o`, `pll.o`, `pll-da850.o`, `psc.o`, and `psc-da850.o` according to `CONFIG_COMMON_CLK`, `CONFIG_ARCH_DAVINCI_DA8XX`, and `CONFIG_ARCH_DAVINCI_DA850`.

Control flow: when `CONFIG_COMMON_CLK=y`, generic PLL and PSC support are always built in this subdirectory, while DA8xx/DA850 platform descriptors are conditional. If common clk is disabled, no objects from this Makefile are selected.

State and persistence: no runtime state; it controls build composition.

Dependencies and integration points: couples SoC Kconfig selections to the DaVinci CFGCHIP, PLL, and PSC providers. PSC registration depends on PLL and async clock providers being available early, matching the `postcore_initcall()` ordering in the C files.

Risks: because `pll.o` and `psc.o` are unconditional under `CONFIG_COMMON_CLK`, missing platform descriptors can still compile generic code without registering useful SoC clocks. DA850-specific objects require `CONFIG_ARCH_DAVINCI_DA850`, so defconfig mistakes produce missing platform init data.

Test signals: build tests should confirm the DA8xx and DA850 configurations link all referenced init data and that non-DA850 DaVinci/common-clk builds do not pull unresolved descriptors.
