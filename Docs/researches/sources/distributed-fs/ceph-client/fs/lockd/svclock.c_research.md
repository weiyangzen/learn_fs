# sources/distributed-fs/ceph-client/fs/lockd/svclock.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svclock.c` implements the common server-side lock engine for lockd, especially blocked locks, deferred VFS lock callbacks, client grant callbacks, lock-owner lifetime, and retry scheduling. The source was read as a complete 1076-line file for this report.

## Important APIs, Types, and Functions

Important file state includes global `nlm_blocked`, `nlm_blocked_lock`, and `nlmsvc_lock_operations`. Public/common entry points are `nlmsvc_lock`, `nlmsvc_testlock`, `nlmsvc_unlock`, `nlmsvc_cancel_blocked`, `nlmsvc_retry_blocked`, `nlmsvc_grant_reply`, `nlmsvc_traverse_blocks`, `nlmsvc_locks_init_private`, `nlmsvc_release_lockowner`, `nlmsvc_put_lockowner`, and `nlmsvc_release_call` from the paired procedure file. Key helpers include `nlmsvc_create_block`, `nlmsvc_lookup_block`, `nlmsvc_find_block`, `nlmsvc_unlink_block`, `nlmsvc_setgrantargs`, `nlmsvc_defer_lock_rqst`, `nlmsvc_grant_deferred`, `nlmsvc_notify_blocked`, `nlmsvc_grant_blocked`, and `retry_deferred_block`.

## Control Flow

`nlmsvc_lock` checks whether the backing file can lock, creates or finds an `nlm_block`, handles grace/reclaim rules, inserts the block into the retry list, then calls `vfs_lock_file`. Immediate success removes the block and returns granted; `-EAGAIN`, `FILE_LOCK_DEFERRED`, `-EDEADLK`, and other errors become NLM statuses. Filesystem callbacks enter through `nlmsvc_lock_operations.lm_notify` or `.lm_grant`, mark blocks ready, move them toward the head of `nlm_blocked`, and wake the lockd service. `nlmsvc_retry_blocked` scans ready blocks, revisits deferred requests or retries blocked grants. Successful VFS grants send `NLMPROC_GRANTED_MSG` asynchronously, then `nlmsvc_grant_reply` removes or retries the block based on the client's reply.

## State and Persistence Behavior

The file owns transient in-memory blocked lock state. Each `nlm_block` links into the global retry list and the owning `nlm_file` block list, references an `nlm_rqst`, file, host, and daemon, and is released by `kref`. Lock owners are per-host structures refcounted by VFS lock-manager callbacks. No state is persistent across lockd shutdown; remote clients recover through NSM and NLM grace/reclaim mechanisms.

## Dependencies and Integration Points

It integrates with VFS locking through `vfs_lock_file`, `vfs_test_lock`, `vfs_cancel_lock`, `locks_can_async_lock`, `locks_delete_block`, `locks_copy_lock`, and `lock_manager_operations`. It depends on SUNRPC async calls for grant callbacks, `svc_wake_up` and `nlmsvc_retry` scheduling from `svc.c`, host and file management from lockd, and the common NLM status model.

## Risks and Edge Cases

The block lifecycle is race-prone: comments call out GRANT and CANCEL crossing in flight, list traversal while callbacks move entries, and an RPC release callback that may call a path taking a mutex. File mutex and global spinlock ordering must remain correct. Deferred non-blocking locks use request-cache revisit callbacks and timeouts. `vfs_lock_file` can modify lock ranges, so grant messages preserve and restore original ranges. Lock-owner allocation failures must become no-locks statuses. Client refusal of a grant requires unlocking the VFS lock.

## Test Signals

Stress blocking and non-blocking locks with local POSIX locks and a filesystem supporting async locks; race CANCEL, UNLOCK, GRANTED_RES, service shutdown, and VFS grant callbacks; verify deadlock status translation; monitor `/proc/locks` and lockd debug output for leaked blocks; test retry timers and soft RPC callback failures; and run NFS lock recovery tests through server restarts and grace windows.
