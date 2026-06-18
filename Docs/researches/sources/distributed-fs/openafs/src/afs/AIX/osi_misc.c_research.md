# sources/distributed-fs/openafs/src/afs/AIX/osi_misc.c

Purpose: miscellaneous AIX OS interface helpers for GFS initialization, vnode I/O wrapping, vnode/gnode release, and superuser checks.

Important APIs and functions: `Afs_init` registers AFS VM buffer strategy with `vm_mount`; `gop_rdwr` builds a one-element `uio` and calls `VNOP_RDWR`; `aix_gnode_rele` unlinks an AFS vnode from its vfs list and frees its allocated gnode; `afs_suser` wraps AIX `suser` without setting errno.

Control flow: `gop_rdwr` zeroes `uio`/`iovec`, sets offset, segment flag, residual, and read/write mode, calls the AIX vnode op with `afs_osi_cred`, then reports residual back to the caller. `aix_gnode_rele` patches neighboring vfs-list links before freeing the gnode.

State and persistence: affects VM registration and in-memory vnode/gnode list membership. Does not directly persist data.

Dependencies and integration: used by `osi_file.c`, `osi_vm.c`, AIX vnode operations, and common AFS superuser checks.

Risks and test signals: `gop_rdwr` offset semantics are documented as safe only for regular non-append cases. Incorrect vnode unlinking can corrupt vfs vnode lists. Signals include stable cache I/O and clean vcache reclamation.
