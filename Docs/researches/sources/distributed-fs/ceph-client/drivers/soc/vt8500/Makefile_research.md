# sources/distributed-fs/ceph-client/drivers/soc/vt8500/Makefile

## Purpose
This Makefile links the WonderMedia SoC info object to its Kconfig symbol.

## Important APIs, Types, And Functions
The build rule is `obj-$(CONFIG_WMT_SOCINFO) += wmt-socinfo.o`.

## Control Flow
Kbuild includes `wmt-socinfo.o` when the symbol is enabled.

## State And Persistence
There is no runtime state; it only affects the build graph.

## Dependencies And Integration Points
It depends on `WMT_SOCINFO` and `wmt-socinfo.c`.

## Risks And Test Signals
Risks are limited to symbol/name drift. Test signals are expected inclusion/exclusion during builds.
