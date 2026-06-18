# sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_ctx.c

Purpose: provides small helpers for temporarily switching the current task filesystem context to an OBD run context and restoring it later. This is used by server-side or storage-facing code paths that need relative filesystem operations to run under a Lustre object device root.

Important APIs/types/functions: `ll_set_fs_pwd()` replaces `fs_struct->pwd` under the fs seqlock while taking and dropping path references; `push_ctxt()` saves the current pwd, mount, and umask into `struct lvfs_run_ctxt`, sets umask to zero, and switches to `new_ctx`; `pop_ctxt()` validates that the task is still in the pushed context, restores the saved pwd and umask, and releases references. Both public functions are exported.

Control flow: callers allocate a save context, call `push_ctxt(save, new_ctx)` before doing filesystem work, and must call `pop_ctxt(save, new_ctx)` afterward. If `new_ctx->dt` is non-NULL, both operations are no-ops because an underlying dt_device path does not need VFS cwd switching.

State/persistence: only per-task transient state is changed: `current->fs->pwd` and `current->fs->umask`. References are acquired with `dget()`/`mntget()` and released with `dput()`/`mntput()`. No persistent data is stored.

Dependencies/integration: depends on kernel VFS path/mount APIs, `fs_write_seqlock()`, Lustre `lvfs_run_ctxt`, OBD context magic checks, and the task's shared `fs_struct`. It is not policy-specific despite living near PTLRPC security code.

Risks/test signals: every successful push must be paired with pop on the same task, otherwise cwd or umask leaks into later work. Assertions catch mismatched context and missing references only in debug/assert-enabled builds. Tests or fault injection should cover push/pop balance, no-op dt path behavior, umask restoration, and error unwinds that occur between push and pop.
