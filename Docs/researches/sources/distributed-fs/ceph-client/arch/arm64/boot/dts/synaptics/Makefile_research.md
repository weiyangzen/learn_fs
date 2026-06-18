# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/synaptics/Makefile

## Purpose
This Makefile registers Synaptics Berlin arm64 board DTBs.

## APIs, Types, And Functions
It has two `dtb-$(CONFIG_ARCH_BERLIN)` entries for AS370 reference boards.

## Control Flow, State, And Persistence
Kbuild evaluates the target list when Berlin architecture support is enabled. There is no runtime state.

## Dependencies And Integration
It depends on the matching DTS files and `CONFIG_ARCH_BERLIN`. It integrates with the global arm64 DTS build.

## Risks And Test Signals
Risks are stale file names and missing build coverage. Test with `make ARCH=arm64 dtbs` under Berlin support.
