<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/super.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenfs/super.c

## Purpose
`super.c` implements the `xenfs` pseudo-filesystem, a Xen-specific single-superblock filesystem exposing xenbus, capabilities, privcmd, and initial-domain xenstored/hypervisor-symbol helper files.

## Important APIs, types, and functions
Key functions are `xenfs_fill_super`, `xenfs_get_tree`, `xenfs_init_fs_context`, `xenfs_init`, and `xenfs_exit`. It defines `capabilities_read`, `capabilities_file_ops`, and the `xenfs_type` file_system_type.

## Control flow
Module init registers `xenfs` only when running in a Xen domain. Mount uses `get_tree_single`, then `simple_fill_super` creates fixed tree entries. Initial domains get extra `xsd_kva`, `xsd_port`, and optional `xensyms`; other Xen domains get the minimal tree.

## State and persistence
There is no persistent storage. Directory entries and file contents are synthetic and reflect current Xen role. Capabilities reports `control_d` only for the initial domain.

## Dependencies and integration points
The file integrates with VFS fs_context, `simple_fill_super`, Xen domain detection, xenbus file operations, privcmd operations, and optional xenstored/xensyms file operations declared in `xenfs.h`.

## Risks and test signals
Risks include exposing dom0-only files to guests, missing optional object definitions, and registration on non-Xen systems. Test signals include mount/umount in dom0 and guest domains, permissions on `xenbus` and `privcmd`, `capabilities` output, and config matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/super.c -->
