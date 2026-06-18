# sources/distributed-fs/ceph-client/fs/nfs/filelayout/Makefile

## Purpose
This Makefile builds the pNFS NFSv4.1 files layout driver module when `CONFIG_PNFS_FILE_LAYOUT` is enabled.

## Important APIs, types, and functions
It declares `obj-$(CONFIG_PNFS_FILE_LAYOUT) += nfs_layout_nfsv41_files.o` and composes that object from `filelayout.o` and `filelayoutdev.o`.

## Control flow
During kernel build, Kbuild includes the composite object only for enabled configurations. The resulting module/object contains the layout-driver registration code from `filelayout.c` and deviceid/data-server helpers from `filelayoutdev.c`.

## State and persistence behavior
The Makefile has no runtime state. Its build-time state determines whether the file layout driver can register and handle `LAYOUT_NFSV4_1_FILES`.

## Dependencies and integration points
It integrates with Kbuild and the NFS/pNFS configuration system. The object name becomes the loadable module name for the files layout driver.

## Risks
If source membership is wrong, the module may register without deviceid helpers or fail to link. Configuration tests need to ensure both implementation files are present when pNFS files layout is enabled.

## Test signals
Build with `CONFIG_PNFS_FILE_LAYOUT=m`, `y`, and disabled; verify module link symbols, module alias availability, and successful layout-driver registration.
