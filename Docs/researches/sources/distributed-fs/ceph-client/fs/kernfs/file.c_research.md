# sources/distributed-fs/ceph-client/fs/kernfs/file.c

## Purpose

`sources/distributed-fs/ceph-client/fs/kernfs/file.c` implements regular-file behavior for kernfs nodes. It turns `struct kernfs_ops` callbacks into VFS file operations for sysfs/cgroup-style pseudo files, covering seq-file reads, binary reads and writes, mmap wrapping, open/release lifetime, poll notification, and file node creation. The source was read as a complete 1092-line file.

## Important APIs, Types, and Functions

The central private type is `struct kernfs_open_node`, which stores the shared per-node open-file list, poll event counter, mmap count, and release-drain count. Key helpers are `kernfs_fop_open`, `kernfs_fop_release`, `kernfs_fop_read_iter`, `kernfs_fop_write_iter`, `kernfs_fop_mmap`, `kernfs_fop_poll`, `kernfs_fop_llseek`, `kernfs_notify`, `kernfs_should_drain_open_files`, `kernfs_drain_open_files`, and `__kernfs_create_file`. `kernfs_file_fops` exports these operations to inodes initialized by `inode.c`.

## Control Flow

Open takes an active reference, validates optional extra permission checks, allocates `kernfs_open_file`, initializes seq_file state, attaches it to the node's shared `kernfs_open_node`, and calls `ops->open` if present. Reads use seq_file when `KERNFS_HAS_SEQ_SHOW` is set; otherwise a PAGE_SIZE or preallocated buffer is filled by `ops->read` under the open-file mutex and active reference. Writes copy one bounded user buffer, NUL-terminate it, then call `ops->write`; partial-write semantics are intentionally not supported. Mmap verifies `KERNFS_HAS_MMAP`, delegates setup to `ops->mmap`, rejects close callbacks, and installs wrapper VM ops that reacquire active references before forwarding faults/access/write faults. Notification increments the poll event immediately, wakes waiters, and queues work that emits fsnotify modify events for all mounted superblocks.

## State and Persistence Behavior

State is in memory only. `kn->attr.open` is RCU-published while open files exist and freed via `kfree_rcu`. Per-open buffers may be allocated once when `ops->prealloc` is enabled. `of->event` snapshots `open_node->event` so poll can report changes after reads. Drain state (`nr_mmapped`, `nr_to_release`, `released`) ensures release callbacks and mmap invalidation happen during node deactivation even if user file descriptors remain.

## Dependencies and Integration Points

This file depends on kernfs active-reference machinery from `dir.c`, inode setup from `inode.c`, mount superblock lists from `mount.c`, seq_file, VFS file operations, mm/VMA callbacks, wait queues, fsnotify, RCU, and hashed `kernfs_locks->open_file_mutex` from `kernfs-internal.h`. `__kernfs_create_file` is the construction point used by external kernfs users.

## Risks and Edge Cases

The main risks are active-reference imbalance, release called more than once, mmap close callbacks that cannot be wrapped, lockdep false positives around mmap and writable sysfs files, users expecting partial writes, and notification races across RCU-published open nodes. Custom seq operations returning `ERR_PTR(-ENODEV)` require the special stop path to avoid double put-active or leaks.

## Test Signals

Useful signals include sysfs/kernfs read/write/mmap/poll tests, KASAN/KCSAN/lockdep during concurrent open, remove, notify, and mmap fault workloads, tests for prealloc plus atomic write length, release-drain tests during node deletion, and fsnotify/poll event tests across multiple kernfs mounts.
