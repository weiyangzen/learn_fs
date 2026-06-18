# sources/distributed-fs/ceph-client/drivers/mtd/ubi/Makefile

## Purpose
Defines Kbuild composition for UBI core and optional UBI companion modules.

## Important APIs, Types, and Functions
`obj-$(CONFIG_MTD_UBI) += ubi.o` builds the main UBI object from `vtbl.o`, `vmt.o`, `upd.o`, `build.o`, `cdev.o`, `kapi.o`, `eba.o`, `io.o`, `wl.o`, `attach.o`, `misc.o`, and `debug.o`. Conditional objects add `fastmap.o` and `block.o`. Separate modules include `gluebi.o` and `nvmem.o`.

## Control Flow
Kbuild links feature objects into `ubi.o` according to the selected Kconfig symbols. Block support is built into UBI when `CONFIG_MTD_UBI_BLOCK` is enabled, not as a separate module.

## State and Persistence
No runtime state is held here. Build-time object inclusion determines available runtime features.

## Dependencies and Integration Points
This file maps Kconfig options from `Kconfig` to compiled implementation files in the UBI directory.

## Risks
Missing object entries can produce unresolved symbols or silently omit configured features. Because `block.o` is linked into `ubi.o`, init/exit ordering must be coordinated with UBI core build code.

## Test Signals
Kernel builds should be run across combinations of `MTD_UBI`, `MTD_UBI_FASTMAP`, `MTD_UBI_BLOCK`, `MTD_UBI_GLUEBI`, and `MTD_UBI_NVMEM` to confirm expected objects link.
