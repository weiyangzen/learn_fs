# sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/Makefile

## Purpose
This Makefile builds the pNFS flexfile layout driver module when `CONFIG_PNFS_FLEXFILE_LAYOUT` is enabled.

## Important APIs, types, and functions
It declares `obj-$(CONFIG_PNFS_FLEXFILE_LAYOUT) += nfs_layout_flexfiles.o` and composes that object from `flexfilelayout.o` and `flexfilelayoutdev.o`.

## Control flow
Kbuild includes the composite object only for configurations that enable the flexfile layout driver. The two implementation files are linked together into the module/object that registers the flexfile layout type elsewhere in the directory.

## State and persistence behavior
The file has no runtime state. Its only effect is build-time inclusion of flexfile layout support.

## Dependencies and integration points
It integrates with the kernel NFS/pNFS configuration and module build system. It is parallel to the files-layout Makefile but targets the flexfile driver implementation files.

## Risks
Incorrect object membership would cause link failures or a module missing either layout logic or device/data-server support. Configuration drift between Kconfig and object names would prevent flexfile layout support from loading.

## Test signals
Build with `CONFIG_PNFS_FLEXFILE_LAYOUT=m`, `y`, and disabled; verify the resulting object links, module loads when modular, and the layout driver registers with its implementation objects present.
