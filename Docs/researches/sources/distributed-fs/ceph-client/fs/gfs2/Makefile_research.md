# sources/distributed-fs/ceph-client/fs/gfs2/Makefile

## Purpose
Builds the `gfs2.o` composite object from GFS2 implementation files and conditionally includes DLM locking support.

## Important APIs, Types, And Functions
`ccflags-y := -I$(src)` adds local include search path. `obj-$(CONFIG_GFS2_FS) += gfs2.o` binds the object to the Kconfig symbol. `gfs2-y` enumerates core object files. `gfs2-$(CONFIG_GFS2_FS_LOCKING_DLM) += lock_dlm.o` adds DLM support when enabled.

## Control Flow
Kbuild expands the object lists according to configuration and links all listed `.o` files into the GFS2 module or built-in object.

## State And Persistence
No runtime state. It controls which implementation units are present in the resulting kernel/module.

## Dependencies And Integration Points
Integrates with Kbuild and Kconfig. The file list couples public headers and cross-file symbols among ACL, bmap, dir, glock, log, quota, recovery, rgrp, super, transaction, and utility components.

## Risks
Omitting an object causes unresolved symbols or missing runtime behavior. Adding DLM unconditionally would break non-cluster builds.

## Test Signals
Build GFS2 as module and built-in, with and without `CONFIG_GFS2_FS_LOCKING_DLM`, and run modpost for unresolved symbols.
