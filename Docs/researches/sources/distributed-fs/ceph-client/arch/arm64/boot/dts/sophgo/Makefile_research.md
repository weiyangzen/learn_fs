# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/sophgo/Makefile

## Purpose
This Makefile registers the Sophgo arm64 DTB target.

## APIs, Types, And Functions
It contains one `dtb-$(CONFIG_ARCH_SOPHGO)` assignment for `sg2042-milkv-pioneer.dtb`.

## Control Flow, State, And Persistence
Kbuild conditionally appends the DTB when Sophgo architecture support is enabled. The built DTB is the only artifact.

## Dependencies And Integration
The Makefile depends on the matching DTS source and the Sophgo Kconfig symbol. It integrates the board into `make dtbs`.

## Risks And Test Signals
Risks are limited to stale target naming or missing DTS source. Build `dtbs` with `CONFIG_ARCH_SOPHGO` enabled and verify the output exists.
