## sources/distributed-fs/openafs/src/afs/NBSD/osi_misc.c

Purpose: miscellaneous NetBSD OSI routines for superuser checks and unsupported inode syscalls.

Important APIs: `afs_osi_suser`, `afs_syscall_icreate`, `afs_syscall_iopen`, and `afs_syscall_iincdec`.

Control flow: `afs_osi_suser` calls NetBSD `kauth_authorize_generic` with `KAUTH_GENERIC_ISSUSER`, passing either `curlwp->l_ru` on NetBSD 5+ or `curlwp->l_acflag` on older builds, and returns boolean success without setting errno. The inode syscall helpers all return `EINVAL`, indicating unsupported functionality on NetBSD.

Dependencies and integration: depends on NetBSD kauth and current LWP fields. `afs_osi_suser` is used by common AFS authorization checks through the `afs_suser` macro in `osi_machdep.h`. The unsupported inode syscalls satisfy common syscall dispatch symbols while refusing operations.

State and persistence: no OpenAFS-owned state; authorization consults live credential/kernel state.

Risks: NetBSD accounting-field differences are handled by preprocessor branches, but future kauth API changes could break superuser checks. Returning `EINVAL` for inode operations must match userspace expectations; callers must not assume those legacy operations work on NetBSD.

Test signals: root vs non-root authorization, NetBSD 5+ and older compile paths, syscall dispatch for unsupported inode operations, and callers handling `EINVAL`.
