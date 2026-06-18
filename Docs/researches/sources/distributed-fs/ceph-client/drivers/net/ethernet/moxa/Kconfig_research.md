# sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/Kconfig

## Purpose
This Kconfig file defines the MOXA ART Ethernet vendor menu and the `ARM_MOXART_ETHER` driver option for the internal Ethernet controller on MOXA ART SoCs.

## Important APIs, Types, And Functions
It declares `NET_VENDOR_MOXART` as a boolean vendor gate, defaulting to `y` only when its dependencies are met, and `ARM_MOXART_ETHER` as a tristate driver option. The driver option depends on `ARM && ARCH_MOXART` and selects `NET_CORE`.

## Control Flow
Kconfig evaluation first exposes the vendor menu when building for ARM MOXART. If enabled, the `ARM_MOXART_ETHER` prompt becomes available and determines whether `moxart_ether.o` can be built into the kernel, built as a module, or omitted.

## State And Persistence
The persistent output is the kernel `.config` symbol selection. No runtime state exists in this file.

## Dependencies And Integration Points
The file integrates with the top-level Ethernet vendor Kconfig hierarchy and the local Makefile, where `CONFIG_ARM_MOXART_ETHER` controls object inclusion. It is tightly scoped to ARM MOXART platforms.

## Risks
The main risk is configuration visibility: non-MOXART builds cannot select this driver. Selecting `NET_CORE` is conservative but the driver also depends on platform, DMA, interrupt, and OF support through normal kernel infrastructure.

## Test Signals
Validate with `oldconfig` or `menuconfig` on an `ARCH_MOXART` ARM configuration, then confirm that `CONFIG_ARM_MOXART_ETHER=m/y` causes `moxart_ether.o` to build and that non-MOXART configs do not expose the prompt.
