# sources/distributed-fs/ceph-client/fs/udf/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/Makefile` wires the UDF implementation into kbuild. The source was read as a complete 10-line Makefile.

## Important APIs, Types, and Functions

The kbuild contract is `obj-$(CONFIG_UDF_FS) += udf.o` and `udf-objs := balloc.o dir.o file.o ialloc.o inode.o lowlevel.o namei.o partition.o super.o truncate.o symlink.o directory.o misc.o udftime.o unicode.o`.

## Control Flow

There is no runtime flow. Kbuild links the listed object files into `udf.o` when `CONFIG_UDF_FS` is enabled.

## State and Persistence Behavior

No filesystem state is owned here. The object list determines which implementation units contribute to the UDF module or built-in image.

## Dependencies and Integration Points

The Makefile integrates with `Kconfig` and kbuild. The listed files cover allocation, directory/file/inode operations, low-level device probing, path lookup, partition handling, superblock parsing, truncation, symlink handling, misc descriptor helpers, time conversion, and Unicode/NLS filename conversion.

## Risks and Edge Cases

Omitting an object can cause unresolved symbols or runtime feature loss. Reordering is usually not semantically meaningful for C objects, but adding new files requires keeping this object list aligned with exported prototypes and Kconfig dependencies.

## Test Signals

Compile `CONFIG_UDF_FS=y` and `m`, verify `udf.o` links without unresolved symbols, and run basic mount/read/write/unmount tests that exercise symbols from every listed object.
