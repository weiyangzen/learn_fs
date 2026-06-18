# sources/distributed-fs/ceph-client/fs/ufs/Makefile

## Purpose
`Makefile` defines the UFS filesystem kbuild object composition and debug compiler flag.

## Important APIs, types, and functions
It builds `ufs.o` when `CONFIG_UFS_FS` is enabled and composes it from `balloc.o`, `cylinder.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `namei.o`, `super.o`, and `util.o`. It adds `-DDEBUG` when `CONFIG_UFS_DEBUG` is enabled.

## Control flow
There is no runtime control flow. Kbuild links all listed objects into one filesystem module/builtin, so symbols declared in `ufs.h` and `util.h` resolve across these compilation units.

## State and persistence
No filesystem state is held here. The object list determines which code participates in UFS mount, directory, inode, allocation, and utility behavior.

## Dependencies and integration points
It is driven by `Kconfig` and integrates UFS with the kernel's filesystem build. Missing an object would break symbol resolution or silently drop functionality.

## Risks and test signals
Risks include object-list drift when new UFS files are added, and debug macro behavior changing only under `CONFIG_UFS_DEBUG`. Test signals are allmodconfig/build-only checks, module link verification, and debug/non-debug compilation.
