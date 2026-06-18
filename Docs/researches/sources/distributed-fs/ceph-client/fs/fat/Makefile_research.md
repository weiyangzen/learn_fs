# sources/distributed-fs/ceph-client/fs/fat/Makefile

## Purpose
`Makefile` maps FAT-family Kconfig symbols to kernel objects. It builds the common FAT core, VFAT long-name layer, MSDOS name layer, and optional FAT KUnit test object.

## Important Build Rules
`obj-$(CONFIG_FAT_FS) += fat.o` builds the common FAT module or built-in object. `obj-$(CONFIG_VFAT_FS) += vfat.o` and `obj-$(CONFIG_MSDOS_FS) += msdos.o` build the two front-end filesystem modules. `fat-y` is composed of `cache.o`, `dir.o`, `fatent.o`, `file.o`, `inode.o`, `misc.o`, and `nfs.o`. `vfat-y` contains `namei_vfat.o`, while `msdos-y` contains `namei_msdos.o`. `obj-$(CONFIG_FAT_KUNIT_TEST) += fat_test.o` adds the unit test object.

## Control Flow
This is declarative kbuild logic. The selected Kconfig symbols determine which composite objects are linked. The common core is separate from the VFAT and MSDOS namespace implementations, so both front ends can share allocation, inode, directory, FAT-entry, file, misc, and NFS export code.

## State And Persistence Behavior
There is no runtime state in this file. Its persistent output is the build artifact layout: `fat.o`, `vfat.o`, `msdos.o`, and optionally `fat_test.o` as built-in or module objects depending on Kconfig tristate values.

## Dependencies And Integration Points
The file integrates with `fs/fat/Kconfig` symbols and the kernel kbuild system. It establishes module composition that must match module names described in Kconfig help. Runtime behavior is provided by the listed C objects elsewhere in `fs/fat`.

## Risks
The main risk is build/link drift: adding a new FAT core source without updating `fat-y`, or moving namei code without updating the front-end composite objects, can produce unresolved symbols or missing functionality. KUnit test object selection must remain aligned with `FAT_KUNIT_TEST`.

## Test Signals
Test signals include allmodconfig/allnoconfig build coverage, built-in and modular FAT/VFAT/MSDOS combinations, `modinfo` or module artifact checks for expected object names, and KUnit build/run coverage when `CONFIG_FAT_KUNIT_TEST` is enabled.
