# sources/distributed-fs/glusterfs/xlators/features/locks/src/posix.c

## Purpose
`posix.c` is the main entry point for the GlusterFS `features/locks` translator. It implements the translator lifecycle, fop/cbk tables, POSIX byte-range locks, mandatory-lock enforcement for I/O paths, lock migration support, lock-count xdata responses, meta-locks used by rebalance, lock state dumps, and cleanup on fd, inode, and client lifetime events.

## Important APIs, Types, And Functions
The file is built around `pl_inode_t`, `posix_lock_t`, `pl_local_t`, `pl_fdctx_t`, `pl_ctx_t`, `pl_meta_lock_t`, and `posix_locks_private_t` from the locks headers. Exported translator operations are installed in `struct xlator_fops fops`, `struct xlator_cbks cbks`, `struct xlator_dumpops dumpops`, and `xlator_api`.

Important lock APIs include `pl_lk`, `pl_is_fop_allowed`, `__rw_allowable`, `do_blocked_rw`, `pl_flush`, `pl_release`, `pl_forget`, `pl_getactivelk`, and `pl_setactivelk`. Xdata/count handling is centralized in `PL_LOCAL_GET_REQUESTS`, `pl_has_xdata_requests`, `pl_get_xdata_requests`, `pl_set_xdata_response`, and count fillers for entry, inode, and POSIX locks. Mandatory-lock control uses `PL_CHECK_LOCK_ENFORCE_KEY`, `pl_track_io_fop_count`, and the set/removexattr callbacks. Lock migration and rebalance coordination use `GF_META_LOCK_KEY`, `GF_META_UNLOCK_KEY`, `pl_metalk`, `pl_metaunlock`, `pl_fill_active_locks`, `gf_lkmig_info_to_posix_lock`, and `pl_write_active_locks`.

## Control Flow
Normal FOPs either pass through while adding xdata bookkeeping, or first validate lock state. `readv`, `writev`, `truncate`, `ftruncate`, `discard`, and `zerofill` build a `posix_lock_t` region and call `pl_is_fop_allowed` when mandatory locking is active. If the operation can proceed, it winds to the child translator; if it conflicts and the fd permits blocking, a call stub is queued on `pl_inode->rw_list`; otherwise it unwinds with `EAGAIN` or `EBUSY`. `do_blocked_rw` later scans queued read/write requests after lock release and resumes stubs whose regions are now allowable.

`pl_lk` validates flock ranges, normalizes negative `l_len`, creates a `posix_lock_t`, handles reserve-lock commands, fd lock enumeration, `F_GETLK`, `F_SETLK`, and `F_SETLKW`, and integrates with reserve locks before calling `pl_setlk`. Blocking locks remain queued by lower helper logic; nonblocking conflicts return `EAGAIN`. Unlocks can alter the returned flock type so NLM can detect whether an fd still has locks.

Most metadata FOPs use the `PL_STACK_UNWIND` family so requested lock-count xdata can be attached on unwind. The compatibility macro suppresses extra xdata for clients older than op-version 3.10. Inode removal paths use `PL_INODE_REMOVE` to coordinate pending remove state with lock cleanup before rename, unlink, or rmdir proceeds.

## State And Persistence Behavior
Primary runtime state is in inode and fd contexts, not in this file's own globals. `pl_inode_t` stores active POSIX locks (`ext_list`), blocked read/write stubs (`rw_list`), reserve locks, inode/entry lock domains, meta-locks, mandatory-lock flags, migration state, and counters. `pl_fdctx_t` stores copied locks for `F_GETLK_FD` iteration. `pl_ctx_t` is per-client state used to clean inode, entry, and meta locks on disconnect or destroy.

Persistent or cross-translator state is represented through xattrs and dictionaries. The file reads pathinfo and lockinfo xattrs, serializes lockinfo dictionaries for lock migration across fd reopen, handles `GF_XATTR_CLRLK_CMD`/`GF_XATTR_INTRLK_CMD`, and sets or removes `GF_ENFORCE_MANDATORY_LOCK`. Meta-lock and active-lock migration state is passed through FOPs rather than stored on disk here.

## Dependencies And Integration Points
The file depends on GlusterFS translator infrastructure (`STACK_WIND`, unwind macros, `xlator_api_t`), inode/fd/client context APIs, dict/xdata helpers, syncops, statedump, lock helpers from `common.c`, `clear.c`, `inodelk.c`, `entrylk.c`, and reserve-lock helpers from `reservelk.c`. It must sit over exactly one child and eventually over a `storage/` translator. Its options expose mandatory locking, tracing, revocation, contention notification, and enforced mandatory lock behavior.

## Risks And Edge Cases
Risk concentrates around lock lifetime and concurrency: mutex ordering between client ctx and inode ctx, waking blocked stubs after deletion or migration, stale frame/local ownership on forced cleanup, and keeping fd/inode refs balanced. Mandatory-lock enforcement has subtle behavior differences between `forced`, `file`, and `optimal` modes; wrong flag handling can either reject valid I/O or let fenced writes through. Lock migration has explicit TODOs around partial failure and meta-lock cleanup. Compatibility code for older clients can hide xdata responses, so changes to xdata behavior need op-version awareness.

## Test Signals
Direct unit coverage in this subset is only for entry lock name semantics, not `posix.c`. Strong test signals would include mandatory-lock read/write/truncate blocking, nonblocking fd `EAGAIN`, lock-count xdata requests on lookup/stat/readdirp, clear-lock xattrs, client disconnect cleanup, fd lock migration using `GF_XATTR_LOCKINFO_KEY`, meta-lock migration, and statedump lock lists.
