# sources/distributed-fs/ceph-client/drivers/memory/tegra/Makefile

Purpose: kbuild rules for Tegra memory-controller and EMC drivers.

Important APIs/types/functions: builds the composite `tegra-mc.o` from `mc.o` plus SoC description files selected by architecture config. Separate objects are built for Tegra20/30/124/210 EMC drivers and newer Tegra186-family EMC code. `tegra210-emc-y` composes the Tegra210 EMC core and clock-characterization table.

Control flow: `obj-$(CONFIG_TEGRA_MC)` emits `tegra-mc.o`; `tegra-mc-$(CONFIG_ARCH_...)` appends SoC data such as `tegra114.o`. EMC object selection follows `CONFIG_TEGRA*_EMC` and newer architecture symbols.

State and persistence: no runtime state. Build output follows the selected Kconfig and architecture symbols.

Dependencies and integration: paired with Tegra Kconfig and common driver registration in `mc.c`. The SoC files provide `struct tegra_mc_soc` instances referenced by `mc.c` OF match tables.

Risks: missing SoC object selection causes unresolved `tegra*_mc_soc` references when the OF match entry is compiled. Newer architectures deliberately reuse `tegra186-emc.o`, so object sharing must remain compatible.

Test signals: build each Tegra architecture configuration and compile-test EMC options; inspect `tegra-mc-y` expansion for the expected SoC table files.
