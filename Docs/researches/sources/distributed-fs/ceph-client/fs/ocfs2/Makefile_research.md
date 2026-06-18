# sources/distributed-fs/ceph-client/fs/ocfs2/Makefile

## Purpose
`fs/ocfs2/Makefile` defines how OCFS2 kernel objects are composed from core filesystem files, stack glue, clustering backends, DLM, and subdirectories.

## Important Build Targets
`obj-$(CONFIG_OCFS2_FS)` builds `ocfs2.o` and `ocfs2_stackglue.o`. `obj-$(CONFIG_OCFS2_FS_O2CB)` builds `ocfs2_stack_o2cb.o`. `obj-$(CONFIG_OCFS2_FS_USERSPACE_CLUSTER)` builds `ocfs2_stack_user.o`. `ocfs2-objs` includes allocation, aops, directory, DLM glue, export, extents, file, heartbeat, inode, ioctl, journal, locks, mmap, namei, refcounting, resize, slot maps, super, symlink, sysfile, quotas, xattr, ACL, and filecheck support.

## Control Flow and Integration
Kbuild consumes this file. `ccflags-y := -I$(src)` supports local includes. Conditional objects provide runtime-selectable clustering stacks. Subdirectories `dlmfs/`, `cluster/`, and `dlm/` are included according to OCFS2 and stack symbols.

## State and Persistence Behavior
No runtime state is stored here, but object inclusion controls persistent feature availability, including ACL/xattr storage, quota metadata, journaling, and clustered coordination.

## Dependencies and Integration Points
The file integrates with `fs/ocfs2/Kconfig`, kbuild composite rules, and subdirectory builds. `acl.c` is part of the main OCFS2 object whenever `CONFIG_OCFS2_FS` is enabled.

## Risks
Omitting an object can remove behavior or produce unresolved symbols. New conditional code must align with Kconfig. The cluster directory is always built with OCFS2 for masklog support.

## Test Signals
Run kbuild for built-in and module configurations across OCFS2, O2CB, userspace cluster, and DLM combinations. Check generated modules and modpost output for expected symbols.
