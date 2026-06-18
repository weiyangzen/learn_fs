# sources/distributed-fs/ceph-client/drivers/soc/vt8500/Kconfig

## Purpose
This Kconfig file defines the VIA/WonderMedia SoC information driver option.

## Important APIs, Types, And Functions
It gates a menu under `ARCH_VT8500 || COMPILE_TEST` and defines `WMT_SOCINFO`, defaulting to `ARCH_VT8500` and selecting `SOC_BUS`.

## Control Flow
When `WMT_SOCINFO` is enabled, the Makefile builds `wmt-socinfo.o`. There is no runtime flow in this file.

## State And Persistence
The selected symbol persists in kernel configuration and controls compile-time inclusion.

## Dependencies And Integration Points
It integrates the VT8500/WonderMedia SoC info C driver with SoC bus support.

## Risks And Test Signals
Risks are mostly dependency drift. Test signals are menu visibility under VT8500 or COMPILE_TEST and successful object build with `CONFIG_WMT_SOCINFO=y`.
