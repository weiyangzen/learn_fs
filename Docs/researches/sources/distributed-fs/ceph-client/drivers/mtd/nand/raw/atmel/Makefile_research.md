# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/Makefile

## Purpose
`raw/atmel/Makefile` maps `CONFIG_MTD_NAND_ATMEL` to the Atmel NAND controller and PMECC objects.

## Important APIs, Types, and Functions
This is Kbuild metadata. It adds `atmel-nand-controller.o` and `atmel-pmecc.o` when `CONFIG_MTD_NAND_ATMEL` is enabled. Composite definitions map `atmel-nand-controller-objs` to `nand-controller.o` and `atmel-pmecc-objs` to `pmecc.o`.

## Control Flow
When the parent raw NAND Makefile descends into `atmel/`, Kbuild evaluates this file. If the config is enabled, it builds two composite objects from the local source files.

## State and Persistence
There is no runtime state. The persistent effect is object/module composition in the build directory.

## Dependencies and Integration Points
It depends on the parent `raw/Makefile` entry `obj-$(CONFIG_MTD_NAND_ATMEL) += atmel/` and the Kconfig symbol that selects necessary Atmel SMC/generic allocator dependencies.

## Risks
If object names drift from source filenames, the Atmel driver will fail to build. Because both controller and PMECC are tied to the same config symbol, changes to split functionality would require Kconfig and Makefile updates together.

## Test Signals
Enable `CONFIG_MTD_NAND_ATMEL` as built-in and module and verify both composite objects are produced and linked without missing PMECC/controller symbols.
