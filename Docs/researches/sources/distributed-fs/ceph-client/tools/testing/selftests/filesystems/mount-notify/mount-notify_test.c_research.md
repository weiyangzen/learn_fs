# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/mount-notify_test.c

## Purpose

`mount-notify_test.c` verifies fanotify mount namespace notifications for mount attach and detach operations in a private chrooted mount namespace.

## Important APIs, Types, and Functions

The `fanotify` fixture tracks three fanotify fds, event parsing buffer state, temporary root path, original root fd, namespace fd, and root mount id. Helpers include `expect_notify`, `expect_notify_n`, `expect_notify_mask`, `verify_mount_ids`, `check_mounted`, and `setup_mount_tree`. APIs include `fanotify_init(FAN_REPORT_MNT)`, `fanotify_mark(... FAN_MARK_MNTNS ...)`, `listmount`, `get_unique_mnt_id`, `mount`, `umount`, `move_mount`, `fsopen`, `fsmount`, and `pivot_root`.

## Control Flow, State, and Persistence

Setup unshares a mount namespace, makes it private, mounts tmpfs as a temporary root, chroots into it, creates `/a` and `/b`, records the root mount id, and creates three fanotify groups. Only the first group keeps a mark; the second removes it and the third flushes it, so reads assert events only on group zero. Tests exercise bind attach/detach, moving a mount, propagation across a shared tree, attaching a new mount from `fsmount`, reparenting across shared/slave propagation, detach caused by rmdir in another namespace, and pivot_root. Each event's `fanotify_event_info_mnt` mount id and mask are compared with `listmount` snapshots.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are fanotify mount reporting, statmount/listmount helpers, namespace and chroot privilege, and new mount API calls. Integration points are VFS mount lifecycle notifications and fanotify mark management. Risks include event ordering assumptions, fixed 256-byte event buffer, chroot cleanup complexity, and mount propagation sensitivity. Passing signals are exact `FAN_MNT_ATTACH`, `FAN_MNT_DETACH`, or combined masks, no duplicate mount ids, and `listmount` membership matching expected mounted sets.
