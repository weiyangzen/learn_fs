# sources/distributed-fs/ceph-client/drivers/memory/tegra/Kconfig

Purpose: Kconfig menu for NVIDIA Tegra memory-controller and external-memory-controller support.

Important APIs/types/functions: `TEGRA_MC` is the top-level bool, defaulting on `ARCH_TEGRA` and selecting `INTERCONNECT`. Child options enable EMC drivers for Tegra20, Tegra30, Tegra124, and Tegra210. Tegra124 selects `TEGRA124_CLK_EMC` on Tegra, Tegra20 selects devfreq and DDR helpers, and Tegra30 selects PM OPP and DDR. `TEGRA210_EMC_TABLE` is an internal bool selected by `TEGRA210_EMC`.

Control flow: when `TEGRA_MC` is enabled, users or platform defaults can enable SoC-specific EMC drivers. The Makefile then includes common MC code plus relevant SoC tables and EMC implementations.

State and persistence: no runtime state. This file controls which memory controller, SMMU/interconnect, reset, timing, and EMC code is compiled.

Dependencies and integration: integrates with `drivers/memory/tegra/Makefile`, SoC architecture symbols, common clock, interconnect, devfreq, PM OPP, and DDR helper subsystems.

Risks: incorrect dependencies can break compile-test or omit required clock/OPP/devfreq support. `TEGRA_MC` selecting interconnect affects runtime topology expectations in `mc.c` and `tegra124-emc.c`.

Test signals: compile with `ARCH_TEGRA`, compile-test each EMC option, and verify selected object files and required subsystem symbols are present.
