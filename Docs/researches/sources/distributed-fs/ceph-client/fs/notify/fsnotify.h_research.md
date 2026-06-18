# sources/distributed-fs/ceph-client/fs/notify/fsnotify.h

## Purpose

`fsnotify.h` is the private core header for fsnotify connector access and teardown helpers. It defines the RCU connector pointer type, object-specific connector accessors, superblock lookup helpers, mark clearing wrappers, and declarations shared by `fsnotify.c`, `mark.c`, `group.c`, and notifier backends.

## Important APIs, Types, and Functions

The key type is `fsnotify_connp_t`, an RCU pointer to `struct fsnotify_mark_connector`. Inline accessors map a connector to an inode, mount, superblock, or mount namespace: `fsnotify_conn_inode()`, `fsnotify_conn_mount()`, `fsnotify_conn_sb()`, and `fsnotify_conn_mntns()`. Other helpers include `fsnotify_object_sb()`, `fsnotify_connector_sb()`, `fsnotify_sb_marks()`, `fsnotify_clear_marks_by_inode()`, `fsnotify_clear_marks_by_mount()`, `fsnotify_clear_marks_by_sb()`, and `fsnotify_clear_marks_by_mntns()`. Declarations cover queue flushing, SRCU, group comparison, inode unmount scanning, connector destruction, dentry flag updates, and connector cache init.

## Control Flow

There is no independent runtime flow. The inline helpers are used on hot paths to translate generic connector state into object-specific fields and to route teardown calls to `fsnotify_destroy_marks()`.

## State and Persistence Behavior

The header does not own storage. It documents how connectors are embedded into watched objects and how mark lists are reached through object fields. The clear helpers initiate destruction of all marks attached to an object but the actual lifetime is handled asynchronously in `mark.c`.

## Dependencies and Integration Points

It depends on `linux/fsnotify.h`, `linux/srcu.h`, list types, and local mount internals. It is included by generic fsnotify implementation files and backend fdinfo/user code that need connector object access.

## Risks and Edge Cases

The main risks are invalid object-type assumptions and missing `NULL` checks for superblocks without fsnotify info. Mount connectors require `real_mount()` conversion. The mount-namespace connector path does not map to a superblock, so callers using `fsnotify_object_sb()` must handle `NULL`.

## Test Signals

Build coverage across all fsnotify users is important because most behavior is inline. Runtime tests that clear marks by inode, mount, superblock, and mount namespace validate the wrapper paths indirectly.
