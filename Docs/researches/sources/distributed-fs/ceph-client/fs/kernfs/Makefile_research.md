<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/kernfs/Makefile

## Purpose
This Makefile defines the object list for the kernfs pseudo-filesystem implementation.

## Important APIs, types, and functions
It builds `mount.o`, `inode.o`, `dir.o`, `file.o`, and `symlink.o` into built-in kernel objects through `obj-y`. There are no code-level APIs in this file.

## Control flow
When `CONFIG_KERNFS` is selected and this directory is descended into by kbuild, all listed objects are compiled as built-in components rather than separate modules.

## State and persistence behavior
The Makefile has no runtime state. It determines which translation units provide kernfs mount, inode, directory, regular file, and symlink behavior.

## Dependencies and integration points
The object list must stay aligned with exported kernfs symbols and internal headers. `dir.o` supplies namespace tree operations, `mount.o` handles superblocks/mounts, `inode.o` bridges to VFS inodes/attributes, `file.o` implements file operations, and `symlink.o` implements links.

## Risks and test signals
Risks are missing objects causing unresolved symbols or dead code assumptions about modularity. Test signals are clean kernfs-user builds, link tests for sysfs/cgroup configurations, and dependency changes that add or remove kernfs translation units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/Makefile -->
