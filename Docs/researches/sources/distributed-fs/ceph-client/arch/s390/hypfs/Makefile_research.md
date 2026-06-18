<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/Makefile

Purpose: Builds the s390 hypervisor filesystem core, debugfs diagnostic files, and optional mounted filesystem view.

Important APIs/types/functions: Adds `hypfs_dbfs.o`, `hypfs_diag.o`, `hypfs_diag0c.o`, `hypfs_sprp.o`, and `hypfs_vm.o` for `CONFIG_S390_HYPFS`; adds `hypfs_diag_fs.o`, `hypfs_vm_fs.o`, and `inode.o` for `CONFIG_S390_HYPFS_FS`.

Control flow: Build-time only. The debugfs and diagnostic collection core can be built independently of the filesystem front end.

State and persistence: No runtime state.

Dependencies and integration points: Coordinates object inclusion for the public declarations in `hypfs.h`, diag-specific helpers, z/VM helpers, SPRP ioctl support, and mounted hypfs inode implementation.

Risks: Missing an object can produce unresolved symbols only for certain config combinations, especially the inline `IS_ENABLED(CONFIG_S390_HYPFS_FS)` wrappers.

Test signals: Build matrix for `CONFIG_S390_HYPFS` and `CONFIG_S390_HYPFS_FS`, including built-in and module-like combinations.

Source read size: 14 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/Makefile -->
