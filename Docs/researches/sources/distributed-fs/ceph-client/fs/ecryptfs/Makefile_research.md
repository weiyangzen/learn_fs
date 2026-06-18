# sources/distributed-fs/ceph-client/fs/ecryptfs/Makefile

## Purpose
The eCryptfs Makefile maps Kconfig symbols to compiled object lists for the eCryptfs filesystem.

## Important APIs, Types, And Functions
It builds `ecryptfs.o` when `CONFIG_ECRYPT_FS` is enabled. The composite object includes `dentry.o`, `file.o`, `inode.o`, `main.o`, `super.o`, `mmap.o`, `read_write.o`, `crypto.o`, `keystore.o`, `kthread.o`, and `debug.o`. With `CONFIG_ECRYPT_FS_MESSAGING`, it also includes `messaging.o` and `miscdev.o`.

## Control Flow
Kernel kbuild uses `obj-$(CONFIG_ECRYPT_FS)` to decide whether to build the filesystem and `ecryptfs-y`/`ecryptfs-$(CONFIG_ECRYPT_FS_MESSAGING)` to assemble the module or built-in composite.

## State And Persistence
The file has no runtime state. It controls build artifacts based on the kernel configuration.

## Dependencies And Integration Points
It is paired with the eCryptfs Kconfig and the source files in `fs/ecryptfs`. Messaging object inclusion must match the optional Kconfig symbol.

## Risks
Omitting an object from `ecryptfs-y` can create unresolved symbols or missing functionality. Adding optional code without guarding it by the correct config symbol can break disabled-message builds.

## Test Signals
Build eCryptfs as built-in and module, with and without messaging, and verify no missing symbols and expected module contents.
