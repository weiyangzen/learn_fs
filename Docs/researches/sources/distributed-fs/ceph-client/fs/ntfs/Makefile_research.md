# sources/distributed-fs/ceph-client/fs/ntfs/Makefile

## Purpose

The NTFS Makefile assembles the legacy NTFS driver object from its component source files and enables debug compilation flags when requested.

## Important APIs, Types, and Functions

The rule `obj-$(CONFIG_NTFS_FS) += ntfs.o` builds the module or built-in object. `ntfs-y` lists the component objects, including address-space operations, attributes, directory/file/inode logic, MFT handling, runlists, superblock, compression, iomap, quotas, object IDs, and block-device I/O. `ccflags-$(CONFIG_NTFS_DEBUG) += -DDEBUG` enables debug code.

## Control Flow

There is no runtime flow. Kbuild links the listed objects into `ntfs.o` when the config symbol is enabled.

## State and Persistence Behavior

The file owns no runtime state. It controls build composition and debug preprocessor state.

## Dependencies and Integration Points

It depends on Kconfig symbols and integrates all NTFS source modules into one driver. The inclusion of `iomap.o` and `aops.o` reflects the driver's use of iomap for page-cache and writeback operations.

## Risks and Edge Cases

Omitting an object from `ntfs-y` can silently remove a feature or cause missing symbols. The debug flag must remain conditional because `-DDEBUG` changes logging/checking behavior across all compiled NTFS objects.

## Test Signals

Build `CONFIG_NTFS_FS=y` and `m`, with and without `CONFIG_NTFS_DEBUG`, and verify `ntfs.o` links all listed objects. Runtime mount smoke tests catch missing object integration.
