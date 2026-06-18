# sources/distributed-fs/ceph-client/ipc/mqueue.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/mqueue.c` implements Linux POSIX message queues as a filesystem named `mqueue`. It handles queue inode creation, priority-ordered message storage, blocking send/receive, timed operations, notification, polling, namespace mount setup, per-user accounting, and compat/time32 syscall variants. The source was read as a complete 1680-line file.

## Important APIs, Types, and Functions

Core state is `struct mqueue_inode_info`, which embeds a VFS inode, queue lock, wait queue, priority rb-tree, queue attributes, notification state, accounting `ucounts`, two wait queues for send and receive, and memory-size tracking. `struct posix_msg_tree_node` stores messages for one priority. `struct ext_wait_queue` represents a sleeping sender or receiver and uses `STATE_NONE`/`STATE_READY` with release/acquire barriers.

Important functions include `mqueue_get_inode()`, `mqueue_create_attr()`, `mqueue_evict_inode()`, `do_mq_open()`, `do_mq_timedsend()`, `do_mq_timedreceive()`, `do_mq_notify()`, `do_mq_getsetattr()`, `mq_init_ns()`, `mq_clear_sbinfo()`, and `init_mqueue_fs()`. File operations support read-only queue status text, poll, flush notification cleanup, and normal VFS lookup/create/unlink semantics.

## Control Flow

`init_mqueue_fs()` creates the inode cache, registers init namespace sysctls, registers the filesystem, initializes `mq_lock`, and creates the initial namespace mount. Each IPC namespace gets an internal `mqueue` mount via `mq_init_ns()`. `mq_open` resolves a queue name under that mount, optionally creates an inode with validated attributes and accounting, then opens it as a file descriptor.

Messages are inserted into an rb-tree keyed by priority, with the rightmost node holding the highest priority. Send allocates/copies a `msg_msg`, validates priority, fd type, write access, and message length, then either directly hands the message to a waiting receiver, inserts it into the tree, or sleeps on the send wait list when full. Receive validates fd/read access and buffer size, then either removes the highest-priority message, sleeps on the receive wait list, or returns `-EAGAIN` for nonblocking empty queues. Pipelined send/receive bypasses the tree when a peer is already sleeping.

## State and Persistence Behavior

Queue state persists as long as the mqueue inode exists or open references keep it alive. Messages are kernel memory allocated by `load_msg()` and freed on receive or inode eviction. Queue counts, qsize, attributes, notification owner, and waiters are inode-local. Namespace state tracks mount, queue count, limits, defaults, and sysctls. Per-user `RLIMIT_MSGQUEUE` accounting is charged at queue creation for worst-case queue memory and released in eviction.

## Dependencies and Integration Points

This file integrates VFS, fs_context, namespace mounts, `simple_*` directory helpers, SysV message allocation helpers from `msgutil.c`, audit hooks, signal delivery, netlink notification for `SIGEV_THREAD`, user namespace accounting, `RLIMIT_MSGQUEUE`, poll, hrtimer absolute timeouts, and compat/time32 syscall layers.

## Risks and Edge Cases

Blocking send/receive has intentional lockless return paths; `STATE_READY`, `smp_store_release()`, `smp_acquire__after_ctrl_dep()`, and `wake_q_add_safe()` are critical to avoid stale message pointers or task use-after-free. Queue creation accounting assumes worst-case memory; overflow checks and capability exceptions must remain exact. Notification state must be removed on close/unregister and must not signal after exec-id changes. The rb-tree must stay consistent with `mq_curmsgs` and qsize even when allocation of a new priority node fails.

## Test Signals

Tests should cover queue creation limits, `RLIMIT_MSGQUEUE`, namespace mounts, priority ordering, blocking and nonblocking send/receive, absolute timeout behavior, signal interruption, poll readiness, unlink with open descriptors, notification registration/removal for `SIGEV_NONE`, `SIGEV_SIGNAL`, and `SIGEV_THREAD`, compat attributes, time32 syscalls, and stress with concurrent senders/receivers across many priorities.
