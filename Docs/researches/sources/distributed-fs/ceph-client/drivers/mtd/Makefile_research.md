# sources/distributed-fs/ceph-client/drivers/mtd/Makefile

## Purpose

This `Makefile` maps top-level MTD Kconfig symbols to built objects and subdirectories. It builds the MTD core aggregate, optional user-facing block/translation modules, panic/pstore/swap support, and delegates chip, map, device, NAND, test, LPDDR, SPI NOR, UBI, and HyperBus families to their own subdirectory Makefiles.

## Important Build Targets

`obj-$(CONFIG_MTD) += mtd.o` builds the core aggregate from `mtdcore.o`, `mtdsuper.o`, `mtdconcat.o`, `mtdpart.o`, and `mtdchar.o`, with `mtd_virt_concat.o` added when `CONFIG_MTD_VIRT_CONCAT` is enabled. `obj-y += parsers/` always descends into partition parsers so their own Kconfig selections can build. User-facing modules include `mtd_blkdevs.o`, `mtdblock.o`, `mtdblock_ro.o`, `ftl.o`, `nftl.o`, `inftl.o`, `rfd_ftl.o`, `ssfdc.o`, `sm_ftl.o`, `mtdoops.o`, `mtdpstore.o`, and `mtdswap.o`. `nftl-objs` and `inftl-objs` define multi-object modules.

## Control Flow

Kbuild evaluates each `obj-*` line from the resolved `.config`. Built-in selections are linked into vmlinux; module selections become loadable modules where supported. The unconditional `obj-y += chips/ lpddr/ maps/ devices/ nand/ tests/` causes traversal of those directories, but their contained objects still depend on their local `obj-$(CONFIG_...)` rules. SPI NOR, UBI, and HyperBus subdirectories are only descended when their root symbols are enabled.

## State and Persistence Behavior

This file has no runtime state. Its effect is persistent in build artifacts: it decides which object files and modules exist. The aggregate `mtd.o` shape is important because it controls which core services are always present once `CONFIG_MTD` is enabled.

## Dependencies and Integration Points

The file is the implementation side of `drivers/mtd/Kconfig`. Its names must stay aligned with source files and symbols. The `mtd-y` aggregate integrates MTD core, superblock helpers, concatenation, partitioning, and char device support. Block translation modules depend on `mtd_blkdevs.o` selected by Kconfig. Subdirectory descent integrates chip probing and concrete bus/device families.

## Risks and Edge Cases

Unconditional descent into `tests/` is safe only because the tests subdirectory must guard objects by `CONFIG_MTD_TESTS`; a bad local Makefile could accidentally build destructive tests. Removing or renaming aggregate members would silently drop core APIs. Symbol/object drift between Kconfig and this Makefile can produce selected features that do not build or dead objects that are never reachable.

## Test Signals

Build matrix tests should check `CONFIG_MTD=y`, `CONFIG_MTD=m`, and selected translation layers. `make drivers/mtd/` or equivalent kernel build targets should confirm that aggregate members and subdirectory modules are produced only for selected symbols. Link tests should cover `nftl-objs` and `inftl-objs` composition.
