# sources/distributed-fs/ceph-client/fs/coda/Makefile

## Purpose
The Coda `Makefile` declares how the kernel builds the Coda filesystem client module/object set.

## Important APIs, Types, And Functions
It builds `coda.o` when `CONFIG_CODA_FS` is enabled. Core objects are `psdev.o`, `cache.o`, `cnode.o`, `inode.o`, `dir.o`, `file.o`, `upcall.o`, `coda_linux.o`, `symlink.o`, and `pioctl.o`; `sysctl.o` is included when `CONFIG_SYSCTL` is enabled.

## Control Flow
Kbuild combines the listed objects into the built-in filesystem or loadable `coda` module depending on the tristate configuration. Optional debug `ccflags-y` are left commented out.

## State, Persistence, And Dependencies
There is no runtime state. Dependencies are Kbuild variables and the configuration symbols `CONFIG_CODA_FS` and `CONFIG_SYSCTL`.

## Integration Points
This file links the VFS operations, Venus upcall/downcall device, cache, inode, directory, file, symlink, pioctl, and sysctl pieces into one filesystem implementation.

## Risks
Missing an object breaks link-time symbols or runtime feature coverage. Optional sysctl compilation must stay aligned with declarations in `coda_int.h`.

## Test Signals
Build Coda as built-in and module with/without `CONFIG_SYSCTL`, run modpost/link checks, and verify exported module metadata comes from the compiled object set.
