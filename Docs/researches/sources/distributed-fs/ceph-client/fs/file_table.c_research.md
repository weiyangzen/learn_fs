# sources/distributed-fs/ceph-client/fs/file_table.c

## Purpose

`sources/distributed-fs/ceph-client/fs/file_table.c` allocates, initializes, accounts, and releases `struct file` objects. It owns global file count sysctls, `filp` slab caches, backing-file containers, pseudo-file allocation helpers, and the deferred `fput()` destruction pipeline. The complete 665-line file was read for this report.

## Important APIs, Types, and Functions

Key APIs include `backing_file_user_path()`, `backing_file_set_user_path()`, security accessors for backing files, `get_max_files()`, `alloc_empty_file()`, `alloc_empty_file_noaccount()`, `alloc_empty_backing_file()`, `alloc_file_pseudo()`, `alloc_file_pseudo_noaccount()`, `alloc_file_clone()`, `flush_delayed_fput()`, `fput()`, `__fput_sync()`, `fput_close_sync()`, `fput_close()`, `files_init()`, and `files_maxfiles_init()`. Internal work centers on `init_file()`, `file_init_path()`, `__fput()`, `__fput_deferred()`, and the `backing_file` wrapper.

## Control Flow

Allocation checks global file limits unless the caller chooses a no-account path, allocates from SLAB_TYPESAFE_BY_RCU caches, initializes credentials, security blobs, locks, mode/flag state, fsnotify mode, error cursors, and finally the reference counter. Path-based allocation fills inode, mapping, file operations, access mode, readcount, and open mode. Final `fput()` drops the last reference, schedules task work where possible, or falls back to delayed work. `__fput()` runs close notifications, eventpoll cleanup, locks removal, LSM release, fasync shutdown, `->release`, cdev release, path and mount puts, and cache free.

## State and Persistence Behavior

Persistent storage is not modified directly, but close and release callbacks may flush filesystem/device state. Runtime state includes global `files_stat`, a percpu `nr_files` counter, sysctl-exposed limits, two slab caches, delayed fput lists, task-work callbacks, and per-file credentials, fsnotify, position, mapping, and error cursor state.

## Dependencies and Integration Points

This file integrates with LSM allocation/release hooks, fsnotify, file locks, eventpoll, task_work, mount/dentry lifetime management, character device refs, percpu counters, sysctl registration, kmemleak annotations, and pseudo-file users such as anon inodes and kernel-internal backing files.

## Risks and Edge Cases

Risks include global file limit enforcement under inaccurate percpu counters, freeing SLAB_TYPESAFE_BY_RCU objects before RCU users are safe, using synchronous fput in contexts that can deadlock unmount, mount writer count imbalance when callers attach writable paths incorrectly, and backing-file security/user-path cleanup.

## Test Signals

Signals include file-max and nr_open sysctl tests, open/close stress under file limit pressure, LSM allocation failure injection, delayed fput/task_work coverage, unmount with delayed file references, eventpoll and fasync close tests, and KASAN/KCSAN/RCU debug for file object reuse.
