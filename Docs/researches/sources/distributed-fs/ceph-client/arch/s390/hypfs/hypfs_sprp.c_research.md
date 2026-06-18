<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_sprp.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_sprp.c

Purpose: Provides the hypfs debugfs interface for Set Partition-Resource Parameter operations through DIAG 304.

Important APIs/types/functions: Defines DIAG 304 commands `SET_WEIGHTS`, `QUERY_PRP`, and `SET_CAPPING`; low-level `__hypfs_sprp_diag304()`, counted wrapper `hypfs_sprp_diag304()`, debugfs read callback `hypfs_sprp_create()`, ioctl helper `__hypfs_sprp_ioctl()`, ioctl dispatcher `hypfs_sprp_ioctl()`, `hypfs_sprp_file`, `hypfs_sprp_init()`, and `hypfs_sprp_exit()`.

Control flow: A read allocates one zeroed page, issues DIAG 304 query, and returns the page only when the diagnose return code is 1. The ioctl path requires `CAP_SYS_ADMIN`, copies a `struct hypfs_diag304` from userspace, validates command fields, optionally copies a page of user data for set operations, executes DIAG 304, copies query data back for query commands, and returns the updated control block.

State and persistence: No persistent data except the registered debugfs file. Each read/ioctl uses a temporary page and control block.

Dependencies and integration points: Exposed only when `sclp.has_sprp` is true. Integrated with hypfs debugfs locking, Linux capability checks, debugfs lockdown gating in `hypfs_dbfs.c`, DIAG statistics, SCLP feature discovery, and UAPI `HYPFS_DIAG304`.

Risks: This is a privileged resource-control surface. User command validation, capability checks, and lockdown handling are security-critical. DIAG 304 uses physical addresses, so page allocation and address translation must remain valid.

Test signals: SPRP-capable systems reading `diag_304`, ioctl query/set/capping as root and non-root, lockdown mode blocking ioctl exposure, invalid command validation, and user-copy fault injection.

Source read size: 147 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_sprp.c -->
