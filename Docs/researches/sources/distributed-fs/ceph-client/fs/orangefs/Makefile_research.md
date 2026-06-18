## sources/distributed-fs/ceph-client/fs/orangefs/Makefile

### Purpose
This Makefile assembles the OrangeFS filesystem module or built-in object.

### Important APIs, types, and functions
- `obj-$(CONFIG_ORANGEFS_FS) += orangefs.o` gates the filesystem on the Kconfig option.
- `orangefs-objs` lists ACL, file, cache, utility, xattr, dcache, inode, sysfs, module, superblock, device request, namei, symlink, directory, bufmap, debugfs, and waitqueue implementation objects.

### Control flow
Kbuild links all listed objects into a single `orangefs.o`. Module entry/exit comes from `orangefs-mod.c`; filesystem registration and superblock code come from `super.o`.

### State and persistence behavior
No runtime state is stored here. The object list defines which subsystems are compiled into the module.

### Dependencies and integration points
The object list is the integration map for the OrangeFS kernel client: VFS operations, upcall/downcall transport, shared memory buffers, xattrs/ACLs, sysfs/debugfs controls, and operation wait queues.

### Risks
Because the module is split across many interdependent objects, missing one object from `orangefs-objs` would produce unresolved symbols or a runtime feature gap. The Makefile must track any future split of protocol, waitqueue, or cache code.

### Test signals
Build with `CONFIG_ORANGEFS_FS=m` and `y`; verify all symbols resolve and the produced module registers filesystem `pvfs2`.
