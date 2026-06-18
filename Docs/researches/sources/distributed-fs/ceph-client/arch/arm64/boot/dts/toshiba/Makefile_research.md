# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/toshiba/Makefile

## Purpose
This Makefile registers Toshiba Visconti arm64 board DTBs.

## APIs, Types, And Functions
It contains two `dtb-$(CONFIG_ARCH_VISCONTI)` assignments for `tmpv7708-rm-mbrc.dtb` and `tmpv7708-visrobo-vrb.dtb`.

## Control Flow, State, And Persistence
Kbuild appends the targets when Visconti support is enabled. There is no runtime state.

## Dependencies And Integration
The file depends on matching DTS files and `CONFIG_ARCH_VISCONTI`. It integrates with the global arm64 DTB build.

## Risks And Test Signals
Risks are stale target names or omitted board entries. Test by building arm64 DTBs with Visconti enabled and confirming both outputs are present.
