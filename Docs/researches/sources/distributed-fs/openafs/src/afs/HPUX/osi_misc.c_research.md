# sources/distributed-fs/openafs/src/afs/HPUX/osi_misc.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_misc.c

Purpose: provides HP-UX-specific miscellaneous support, currently just a safe superuser check wrapper.

Important APIs/types/functions: `afs_suser(afs_ucred_t *credp)` saves `u.u_error`, calls HP-UX `suser()`, restores `u.u_error`, and returns the privilege result.

Control flow: straight-line error preservation around `suser`.

State/persistence: no persistent state. It deliberately avoids changing process errno while testing privilege.

Dependencies/integration: used by privileged inode/syscall paths that require superuser checks but must not clobber caller-visible error state.

Risks/test signals: semantics depend on HP-UX `suser()` return convention. Test privileged and unprivileged calls to inode syscalls and verify failed privilege checks do not overwrite unrelated `u.u_error`.
