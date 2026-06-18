# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/Makefile

## Purpose
Build mapping for HiSilicon PHY drivers. It links each Kconfig symbol to its driver object file.

## Important APIs, types, and functions
Uses standard Kbuild `obj-$(CONFIG_...) += file.o` rules for seven PHY objects.

## Control flow
When a config symbol is built-in or module, Kbuild compiles the matching `.c` file into the kernel or module set.

## State and persistence
No runtime state. Build decisions persist only through kernel configuration.

## Dependencies and integration points
Depends on the adjacent Kconfig symbols. Object names match the source files in this work item.

## Risks and test signals
Risk is symbol/object drift if a file is renamed or a Kconfig symbol changes. Test by enabling each symbol and running a kernel build or `make drivers/phy/hisilicon/`.
