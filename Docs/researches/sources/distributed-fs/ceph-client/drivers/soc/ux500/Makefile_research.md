# sources/distributed-fs/ceph-client/drivers/soc/ux500/Makefile

## Purpose
This Makefile connects the ux500 SoC identity driver object to its Kconfig symbol.

## Important APIs, Types, And Functions
The key build rule is `obj-$(CONFIG_UX500_SOC_ID) += ux500-soc-id.o`.

## Control Flow
Kbuild includes `ux500-soc-id.o` only when `CONFIG_UX500_SOC_ID` is enabled.

## State And Persistence
There is no runtime state. The persistent effect is the compiled object list.

## Dependencies And Integration Points
It depends on the local Kconfig symbol and the `ux500-soc-id.c` source file.

## Risks And Test Signals
Risks are limited to symbol/file name drift. Test signals are kernel build inclusion/exclusion matching `CONFIG_UX500_SOC_ID`.
