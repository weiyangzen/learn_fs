# sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-common.c

## Purpose
`read-only-common.c` implements shared FOP wrappers that block mutating operations with `EROFS` when either the read-only or WORM translator is globally enabled for normal clients. It also passes through lock operations and safe xattrop cases.

## Important APIs and Functions
- `is_readonly_or_worm_enabled()` reads `read_only_priv_t.readonly_or_worm_enabled` but disables enforcement for internal/trusted frames with `frame->root->pid < GF_CLIENT_PID_MAX`.
- `ro_xattrop()` and `ro_fxattrop()` block xattrop unless all dict values are zero-filled.
- Mutating blockers: `ro_setattr`, `ro_fsetattr`, `ro_truncate`, `ro_ftruncate`, `ro_fallocate`, `ro_mknod`, `ro_mkdir`, `ro_unlink`, `ro_rmdir`, `ro_symlink`, `ro_rename`, `ro_link`, `ro_create`, `ro_open`, `ro_fsetxattr`, `ro_fsyncdir`, `ro_writev`, `ro_setxattr`, `ro_removexattr`.
- Lock pass-through wrappers: `ro_entrylk`, `ro_fentrylk`, `ro_inodelk`, `ro_finodelk`, `ro_lk`.
- `ro_open_cbk()` is a strict unwind callback used by `ro_open()`.

## Control Flow
Each wrapper checks `is_readonly_or_worm_enabled()` and either unwinds the FOP immediately with `-1, EROFS` or tail-winds the same FOP to `FIRST_CHILD(this)`. `ro_open()` blocks only write-capable open modes; read-only opens proceed and unwind through `ro_open_cbk()`. Lock operations always pass through, allowing lock management on read-only volumes.

## State and Persistence
The file reads only `read_only_priv_t` from `this->private`; it writes no state and persists nothing. Xattrop checks inspect request dictionary payloads but do not mutate them.

## Dependencies and Integration Points
It depends on GlusterFS default stack macros, `read-only.h`, and the exact FOP unwind signatures. The same object is compiled into both `read-only.la` and `worm.la`, so WORM uses these wrappers for operations it does not specialize.

## Risks
- The trusted-client bypass depends on PID threshold semantics; misclassification can allow writes or block internal maintenance.
- FOP signatures must match GlusterFS core; unwind argument mistakes can break callers.
- The zero-filled xattrop exception is subtle and should remain aligned with the operations that depend on no-op xattrop behavior.
- `ro_fsetxattr`, `ro_setxattr`, and `ro_removexattr` block all xattrs when enabled, including administrative operations unless issued as trusted/internal.

## Test Signals
Tests should verify every mutating FOP returns `EROFS` when enabled for client frames and passes through when disabled or internal. Specific coverage should include write-only/read-write opens, read-only opens, lock FOP pass-through, zero-filled versus nonzero xattrop dictionaries, and shared behavior when compiled into WORM.
