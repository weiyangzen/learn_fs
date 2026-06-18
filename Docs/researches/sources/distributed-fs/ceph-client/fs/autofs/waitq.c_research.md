# sources/distributed-fs/ceph-client/fs/autofs/waitq.c

Purpose: implements autofs kernel-to-daemon wait queues, notification packet creation, pipe writes, catatonic teardown, and daemon release of pending mount/expire requests.

Important APIs/types/functions: `autofs_catatonic_mode`, `autofs_wait`, `autofs_wait_release`, `autofs_notify_daemon`, `autofs_write`, `autofs_find_wait`, and `validate_request`. `struct autofs_wait_queue` stores token, name, uid/gid, pid/tgid, dev/ino, status, and waiter count.

Control flow: `autofs_wait()` validates catatonic and pid namespace visibility, builds a request name, locks `wq_mutex`, reuses an existing wait or allocates a new token, selects protocol v4/v5 packet type based on notify kind and mount type, sends a packet to the daemon pipe, then sleeps until release clears `wq->name.name`. The daemon calls `autofs_wait_release()` with `READY` or `FAIL` token status. Pipe errors either fail one waiter or force catatonic mode.

State and persistence: pending waits are in `sbi->queues`, serialized by `wq_mutex`; pipe writes are serialized by `pipe_mutex`; request names are separately allocated with an offset for path strings. Successful mount waits cache requester uid/gid in `autofs_info` for daemon restart and macro substitution.

Dependencies and integration: uses UAPI autofs packet layouts, `__kernel_write()`, wait queues, signal state, pid namespace translation, autofs dentry helpers, and root ioctl release handling.

Risks: error handling must not leak the allocated name or queue object across interruption, catatonic teardown, and daemon release. SIGPIPE suppression is intentional and easy to regress. Namespace pid translation failure returns `-ENOENT`, which affects containers and daemon restarts.

Test signals: parallel callers waiting on the same missing mount; daemon releases with success/failure; pipe close and EPIPE catatonic transition; pid namespace mismatch; interrupted wait; v4 and v5 packet format coverage.
