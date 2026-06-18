# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/realtek/Makefile

## Purpose
This Makefile registers Realtek arm64 DTBs under `CONFIG_ARCH_REALTEK`.

## APIs, Types, And Functions
It contains 12 `dtb-$(CONFIG_ARCH_REALTEK)` entries. These select board DTBs for Realtek SoC families when the architecture option is enabled.

## Control Flow, State, And Persistence
Kbuild conditionally includes all listed DTB targets. No runtime code or mutable state exists. The outputs are built DTB artifacts.

## Dependencies And Integration
The file depends on matching DTS sources in the Realtek DTS directory and on the Realtek architecture Kconfig symbol. It integrates with the global arm64 `dtbs` build.

## Risks And Test Signals
Risks are missing board entries, renamed DTS files, or a DTB entry left behind after source removal. Run `make ARCH=arm64 dtbs` with Realtek support and confirm all listed targets build.
