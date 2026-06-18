# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/nvidia/Makefile

## Purpose
This Makefile lists NVIDIA Tegra arm64 board DTBs and enables overlay symbol generation for selected boards. It covers Tegra132, Tegra210, Tegra186, Tegra194, Tegra234, and Tegra264 platforms.

## APIs, Types, And Functions
The build-facing API is a series of `DTC_FLAGS_<dtb-base> := -@` assignments and 21 `dtb-$(CONFIG_ARCH_TEGRA_*_SOC)` entries. The `-@` flag causes the device-tree compiler to emit symbols for overlay support on chosen Jetson and reference boards.

## Control Flow, State, And Persistence
Kbuild evaluates config-guarded DTB targets. There is no runtime state. The persistent outputs are `.dtb` files, with symbol sections included for boards covered by `DTC_FLAGS_*`.

## Dependencies And Integration
The file depends on DTS files named after Tegra boards and SOC Kconfig options. It integrates with overlay workflows because symbol-enabled DTBs can accept runtime or bootloader-applied overlays.

## Risks And Test Signals
Risks include missing `-@` on a board that needs overlays, stale board names, and incorrect SoC gating. Test with `make dtbs`, inspect generated DTBs for `__symbols__` when overlays are required, and boot representative Tegra platforms.
