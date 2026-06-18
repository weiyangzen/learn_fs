# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/st/Makefile

## Purpose
This Makefile registers STMicroelectronics STM32 arm64 board DTBs.

## APIs, Types, And Functions
It contains one `dtb-$(CONFIG_ARCH_STM32)` assignment with four STM32MP257 board DTBs.

## Control Flow, State, And Persistence
Kbuild conditionally includes the targets when STM32 support is enabled. It has no runtime behavior or mutable state.

## Dependencies And Integration
The file depends on corresponding DTS files and `CONFIG_ARCH_STM32`. It integrates STM32 board descriptions with the arm64 DTB build.

## Risks And Test Signals
Risks are stale target references and incomplete board build coverage. Run `make ARCH=arm64 dtbs` with STM32 enabled and verify all four outputs build.
