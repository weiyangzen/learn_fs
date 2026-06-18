# sources/distributed-fs/ceph-client/drivers/mtd/Kconfig

## Purpose

This `Kconfig` file defines the top-level Memory Technology Device menu and the main user/translation-layer options under `drivers/mtd`. It gates all lower MTD driver families and controls whether MTD core support, block views, translation layers, panic/oops storage, swap, partitioned master retention, virtual concatenation, chip drivers, map drivers, device drivers, NAND, LPDDR, SPI NOR, UBI, and HyperBus are visible to kernel configuration.

## Important Symbols and Structure

`menuconfig MTD` is the root tristate and implies `NVMEM`. Inside `if MTD`, the file defines `MTD_TESTS`, includes the partition parser submenu, and then declares user modules and translation layers. `MTD_BLKDEVS` is an internal tristate selected by block-style users. Visible block users include `MTD_BLOCK`, `MTD_BLOCK_RO`, `FTL`, `NFTL`, `INFTL`, `RFD_FTL`, `SSFDC`, `SM_FTL`, `MTD_OOPS`, `MTD_PSTORE`, and `MTD_SWAP`. Partition behavior is controlled by `MTD_PARTITIONED_MASTER`, and `MTD_VIRT_CONCAT` depends on it.

The bottom of the file sources submenus for `chips`, `maps`, `devices`, `nand`, `lpddr`, `spi-nor`, `ubi`, and `hyperbus`.

## Control Flow

Kconfig processing starts at `MTD`. When disabled, none of the nested menus or sourced child Kconfigs apply. When enabled as built-in or module, child symbols become available subject to their own dependencies. Several options select `MTD_BLKDEVS` to ensure `mtd_blkdevs.o` is built when a block or translation-layer facade needs it. Child Kconfigs extend the menu in place, so this file is the routing point from generic MTD support to physical chip and bus-specific drivers.

## State and Persistence Behavior

The file does not persist runtime state; it persists build-time configuration in the kernel `.config`. The selected symbols determine which objects are compiled and which MTD APIs are available at runtime. Dangerous test modules are explicitly gated by `depends on m`, encouraging modular use rather than built-in destructive tests.

## Dependencies and Integration Points

The symbols connect to `drivers/mtd/Makefile` object selection. Block-oriented options depend on `BLOCK`; `MTD_PSTORE` depends on `PSTORE_BLK`; `MTD_SWAP` depends on `SWAP`; `SM_FTL` selects NAND core and software Hamming ECC. The sourced child Kconfigs define chip probing, map drivers, raw NAND, SPI NOR, UBI, and other physical/backend integrations.

## Risks and Edge Cases

Several translation layers carry historical patent and data-loss warnings. `MTD_TESTS` can erase whole devices. `MTD_BLOCK` is documented as unsafe for general flash write emulation because erase sizes are larger than block sizes. `MTD_PARTITIONED_MASTER` changes device hierarchy and can expose master and partitions concurrently, which is useful but can be dangerous if users write overlapping regions.

## Test Signals

Configuration tests should verify that expected object files appear for each symbol combination and that dependency constraints prevent invalid builds. Runtime validation should cover MTD core registration, partition parser availability, block facade creation only when selected, UBI preference warnings remaining visible, and destructive tests only being built as modules.
