# Research: sources/distributed-fs/ceph-client/fs/notify/dnotify/dnotify.c

## Purpose

This file implements legacy dnotify directory notifications on top of fsnotify. Users register interest with `fcntl()` on a directory file descriptor and receive `SIGIO` notifications when matching child events occur.

## Important APIs, Types, and Functions

Global state includes `dir_notify_enable`, optional sysctl registration, `dnotify_struct_cache`, `dnotify_mark_cache`, and the singleton `dnotify_group`. `struct dnotify_mark` embeds `struct fsnotify_mark` and chains `struct dnotify_struct` registrations. `dnotify_recalc_inode_mask()` recomputes the aggregate mask. `dnotify_handle_event()` sends `SIGIO` and removes one-shot registrations. `dnotify_flush()` removes registrations on file close. `convert_arg()` maps userspace `DN_*` flags to internal `FS_*` masks. `attach_dn()` adds or merges a registration. `fcntl_dirnotify()` is the main registration entry point. `dnotify_init()` allocates caches and the fsnotify group.

## Control Flow

Registration rejects disabled sysctl state, zero masks remove existing watches, and non-directories return `-ENOTDIR`. Valid registrations pass `security_path_notify()`, allocate a dnotify struct and potentially a new mark, lock the fsnotify group, find or add the inode mark, check for an fd-close race with `fget_raw()`, set file ownership for signal delivery, attach or merge the registration, and recalculate masks.

On events, fsnotify calls `dnotify_handle_event()`. It ignores irrelevant non-directory events, locks the mark, scans all registrations, sends `send_sigio()` to matching owners, and frees one-shot registrations before recalculating the mark mask. `dnotify_flush()` performs close-time cleanup and detaches/free marks when the last registration disappears.

## State and Persistence Behavior

Runtime state is held in slab-allocated `dnotify_struct` nodes chained from a per-inode dnotify mark, plus the shared fsnotify group. State persists until one-shot event consumption, explicit zero-mask removal, fd close, or mark teardown. There is no on-disk persistence.

## Dependencies and Integration Points

The implementation depends on fsnotify backend APIs, signal ownership helpers, security hooks, sysctl when enabled, slab caches, spinlocks, and file descriptor lifetime rules. It exports behavior through `fcntl_dirnotify()` and `dnotify_flush()`.

## Risks

Concurrency around fd close and mark insertion is delicate; the group lock and mark spinlock must be preserved. One-shot removal while iterating the chain must update masks correctly. Signal-based delivery is lossy and legacy. `dir_notify_enable` sysctl changes can make registrations fail with `-EINVAL`.

## Test Signals

Test registration on directories and non-directories, zero-mask removal, one-shot and `DN_MULTISHOT` behavior, signal delivery for create/delete/modify/access/attrib/rename, close-time cleanup, concurrent close/register races, sysctl disable behavior, and security hook denial.
