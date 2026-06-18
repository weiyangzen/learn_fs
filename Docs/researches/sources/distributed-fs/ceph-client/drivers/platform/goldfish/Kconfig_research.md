<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/goldfish/Kconfig

## Purpose

This Kconfig file defines support for Android Goldfish virtual platform devices and the Goldfish QEMU pipe driver.

## Important APIs, Types, And Functions

`GOLDFISH` is a bool menuconfig depending on `HAS_IOMEM` and `HAS_DMA`, defaulting from `X86_GOLDFISH`. `GOLDFISH_PIPE` is a tristate option under that menu.

## Control Flow

Enabling `GOLDFISH` exposes the pipe option. Enabling `GOLDFISH_PIPE` builds the virtual pipe driver used by Android emulator guests.

## State And Persistence

This file has no runtime state. It controls whether Goldfish platform code is compiled.

## Dependencies And Integration Points

It integrates with architecture Goldfish defaults and the platform driver Makefile.

## Risks

The menu help notes that non-emulator builds generally should not enable these drivers. Missing DMA or IOMEM support correctly hides the menu.

## Test Signals

Check config visibility on Goldfish and non-Goldfish architectures, allmodconfig builds, and disabled behavior when DMA/IOMEM support is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/Kconfig -->
