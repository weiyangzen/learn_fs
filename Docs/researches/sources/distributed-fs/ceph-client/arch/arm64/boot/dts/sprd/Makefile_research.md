# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/sprd/Makefile

## Purpose
This Makefile registers Spreadtrum/Unisoc arm64 board DTBs.

## APIs, Types, And Functions
It has one `dtb-$(CONFIG_ARCH_SPRD)` assignment containing five DTB targets.

## Control Flow, State, And Persistence
Kbuild includes the target list when `CONFIG_ARCH_SPRD` is enabled. No runtime state exists; outputs are DTBs.

## Dependencies And Integration
It depends on the named DTS sources and the architecture Kconfig symbol. It is consumed by the arm64 DTS Kbuild hierarchy.

## Risks And Test Signals
Risks are missing or renamed DTS files and incomplete board coverage. `make ARCH=arm64 dtbs` with Spreadtrum support is the primary test signal.
