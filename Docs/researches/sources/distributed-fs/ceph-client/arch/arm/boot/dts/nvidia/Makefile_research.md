# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nvidia/Makefile

Purpose: Kbuild manifest for NVIDIA Tegra ARM DTBs. It lists board DTBs for Tegra20, Tegra30, Tegra114, and Tegra124 families under their respective architecture config symbols.

Important APIs/types/functions: standard `dtb-$(CONFIG_ARCH_TEGRA_*_SOC) +=` blocks enumerate about 45 DTBs. Covered boards include Transformer/Slate devices, Harmony, Colibri, TrimSlice, Ventana, Beaver, Cardhu, Nexus 7 variants, Ouya, Jetson TK1, Nyan variants, Venice2, Xiaomi Mocha, and several evaluation boards.

Control flow: no executable flow. Kbuild resolves enabled Tegra SoC configs and builds only the associated DTB targets.

State and persistence: no runtime state. Persistent output is the set of generated board DTBs.

Dependencies and integration: depends on Tegra Kconfig symbols, matching DTS files, and parent ARM DTS Kbuild. It integrates a broad set of consumer and development boards into the kernel build.

Risks: because many targets are product variants with similar names, rename mistakes or target omissions can remove board support from `make dtbs`. There are no overlay-specific flags here, so any future overlay target would need explicit Kbuild treatment. Test with Tegra-enabled `make ARCH=arm dtbs`, targeted board builds, and CI that checks every listed `.dtb` maps to a source `.dts`.
