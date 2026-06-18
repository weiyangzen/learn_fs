# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/microchip/Makefile

## Purpose
This Makefile declares Microchip arm64 DTBs built by the kernel device-tree build. It gates LAN969x and Sparx5 board DTBs behind their architecture Kconfig symbols.

## APIs, Types, And Functions
The file exports no code APIs. Its build interface is `dtb-$(CONFIG_ARCH_LAN969X)` and `dtb-$(CONFIG_ARCH_SPARX5)` assignments. It lists one LAN9696 EVB DTB and five Sparx5 PCB variants, including eMMC variants for PCB134 and PCB135.

## Control Flow, State, And Persistence
Kbuild evaluates the conditional `dtb-y` fragments during `make dtbs` or kernel builds. There is no runtime state. The persistent output is the selected `.dtb` files in the build tree.

## Dependencies And Integration
The Makefile depends on the corresponding DTS files and Kconfig symbols. It integrates with `scripts/Makefile.lib` device-tree rules through the architecture DTS directory hierarchy.

## Risks And Test Signals
Risks include stale board names, missing DTS files, or DTBs not being built because the wrong Kconfig symbol is used. Test by enabling `CONFIG_ARCH_LAN969X` or `CONFIG_ARCH_SPARX5` and running `make dtbs`; missing-source failures or absent output DTBs indicate integration breakage.
