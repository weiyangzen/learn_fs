# sources/distributed-fs/ceph-client/fs/nilfs2/Makefile

## Purpose

The NILFS2 `Makefile` wires `CONFIG_NILFS2_FS` to the `nilfs2.o` composite object and lists every object file participating in the filesystem implementation.

## Important APIs, Types, and Functions

`obj-$(CONFIG_NILFS2_FS) += nilfs2.o` attaches NILFS2 to kbuild. `nilfs2-y` includes inode, file, directory, superblock, namei, page, metadata-file, block mapping, btree/direct mapping, DAT, recovery, segment construction, checkpoint/sufile/ifile allocators, garbage collection inode, ioctl, and sysfs objects.

## Control Flow

When `CONFIG_NILFS2_FS` is enabled, kbuild compiles the listed `.o` files and links them into `nilfs2.o`. Module or built-in behavior is controlled by the tristate value from Kconfig.

## State and Persistence Behavior

The Makefile stores no runtime state. Its object list determines which persistence mechanisms are present in the built filesystem: log segments, checkpoints, DAT, ifile, sufile, bmap, and recovery.

## Dependencies and Integration Points

It integrates with kbuild and the local NILFS2 source layout. `alloc.o` and `bmap.o`, covered in this work item, are core metadata components in that composite object.

## Risks and Edge Cases

Forgetting to list a new object causes link failures or missing functionality. Removing or renaming objects without updating this file breaks the build. Object order usually should not encode behavior but can expose unresolved dependencies at link time.

## Test Signals

Build NILFS2 as built-in and module. Confirm all expected symbols link, `nilfs2.ko` is produced in module mode, and metadata-heavy mount/create/delete/gc paths are available.
