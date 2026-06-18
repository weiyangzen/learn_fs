# sources/distributed-fs/ceph-client/drivers/soc/Makefile

## Purpose
This Makefile aggregates vendor SoC driver subdirectories into the kernel build.

## Important APIs, Types, And Functions
It has no runtime APIs. Its important build variables are `obj-y` and `obj-$(CONFIG_...)` entries that descend into vendor directories such as `apple/`, `aspeed/`, `atmel/`, `bcm/`, `amlogic/`, and `qcom/`.

## Control Flow
Kbuild evaluates the file after configuration. Unconditional `obj-y` directories are visited and their child Makefiles decide object selection. Conditional entries, such as `obj-$(CONFIG_ARCH_AT91) += atmel/`, only recurse when the symbol is enabled.

## State, Persistence, And Dependencies
Build state comes from `.config`. The file depends on matching vendor directories and per-vendor Makefiles.

## Integration Points
This is the build companion to `drivers/soc/Kconfig`. It bridges selected configuration symbols to compiled objects and modules.

## Risks
Mismatch between Kconfig sourcing and Makefile recursion can expose options that never build or build directories that have no relevant options. Unconditional vendor recursion is acceptable when child Makefiles are fully conditional.

## Test Signals
Build `drivers/soc/` for allmodconfig, allyesconfig, and architecture defconfigs covering conditional entries, and check for missing-directory or unused-symbol regressions.
