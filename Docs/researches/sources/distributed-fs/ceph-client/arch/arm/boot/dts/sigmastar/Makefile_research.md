# sources/distributed-fs/ceph-client/arch/arm/boot/dts/sigmastar/Makefile

Purpose: this Kbuild fragment lists SigmaStar/MStar ARMv7 DTBs.

Important API surface: `dtb-$(CONFIG_ARCH_MSTARV7)` adds eight board DTBs, including infinity/infinity2m/infinity3 and mercury5 targets such as BreadBee, 100ask DongshanPi One, Miyoo Mini, WirelessTag IDO SBC, SSD201HTV2, UnitV2, and Midrive D08.

Control flow: Kbuild conditionally appends targets for `CONFIG_ARCH_MSTARV7`.

State and persistence: no runtime state. The file persists the list of buildable SigmaStar/MStar device trees.

Dependencies and integration: depends on matching DTS files and the parent ARM DTS build. Generated artifacts integrate with board-specific bootloader DTB selection.

Risks and test signals: target names are long and product-specific, so spelling drift is the primary risk. Test with MStarV7 enabled and verify all eight DTBs compile.
