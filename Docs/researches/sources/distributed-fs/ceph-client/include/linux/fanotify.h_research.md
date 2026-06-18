# sources/distributed-fs/ceph-client/include/linux/fanotify.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fanotify.h` centralizes kernel fanotify flag masks, permission classes, event groupings, and response validation masks. The source was read as a complete 150-line file for this report.

## Important APIs, Types, and Functions

The file exports macros such as `FAN_GROUP_FLAG`, `FANOTIFY_ADMIN_INIT_FLAGS`, `FANOTIFY_USER_INIT_FLAGS`, `FANOTIFY_MARK_FLAGS`, `FANOTIFY_PATH_EVENTS`, `FANOTIFY_DIRENT_EVENTS`, `FANOTIFY_PERM_EVENTS`, `FANOTIFY_EVENTS`, `FANOTIFY_OUTGOING_EVENTS`, `ALL_FANOTIFY_EVENT_BITS`, and `FANOTIFY_RESPONSE_VALID_MASK`. It also defines internal `FANOTIFY_UNPRIV`.

## Control Flow

There is no local function flow. Fanotify init, mark, event-generation, and permission-response paths use these masks to reject invalid userspace flags, split inode/path/error/mount event classes, and verify permission responses.

## State and Persistence Behavior

The header stores no state. Runtime state lives in fsnotify/fanotify groups, marks, queues, and permission event objects.

## Dependencies and Integration Points

It depends on `linux/sysctl.h` and `uapi/linux/fanotify.h`. It integrates with fsnotify, fanotify syscalls, capability checks for `CAP_SYS_ADMIN`, mount and inode watches, and file-handle/fd/pidfd reporting.

## Risks and Edge Cases

The masks intentionally avoid extending old UAPI aggregate constants. Privilege mistakes can expose file descriptors, pidfds, permission events, or unlimited queues to unprivileged users. Event classification must preserve directory-only and data-type restrictions.

## Test Signals

fanotify syscall selftests for privileged/unprivileged init, mark validation, permission response validation, mount and dirent events, pidfd/file-handle reporting, and queue overflow behavior.
