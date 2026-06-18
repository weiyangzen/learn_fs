
# sources/distributed-fs/ceph-client/include/uapi/linux/inotify.h

## Purpose

`inotify.h` defines the inotify event record ABI, watch masks, special flags, aggregate event mask, init flags, and the `INOTIFY_IOC_SETNEXTWD` ioctl. The complete 84-line file was read.

## Important APIs, Types, and Functions

`struct inotify_event` contains watch descriptor, mask, cookie, name length, and flexible filename. Constants include all implemented watch events `IN_ACCESS` through `IN_MOVE_SELF`, generated events `IN_UNMOUNT`, `IN_Q_OVERFLOW`, `IN_IGNORED`, helper masks `IN_CLOSE`/`IN_MOVE`, flags `IN_ONLYDIR`, `IN_DONT_FOLLOW`, `IN_EXCL_UNLINK`, `IN_MASK_CREATE`, `IN_MASK_ADD`, `IN_ISDIR`, `IN_ONESHOT`, `IN_ALL_EVENTS`, `IN_CLOEXEC`, `IN_NONBLOCK`, and `INOTIFY_IOC_SETNEXTWD`.

## Control Flow

User space initializes an inotify fd, adds watches with masks, then reads one or more variable-length `inotify_event` records. Kernel fsnotify code queues events, supplies move cookies, marks overflow, and removes one-shot or ignored watches.

## State and Persistence Behavior

Inotify instances keep per-fd watch descriptors, masks, queues, and next watch descriptor state. Events persist in the queue until read or dropped on overflow.

## Dependencies and Integration Points

It includes `linux/fcntl.h` and `linux/types.h`. It integrates with fsnotify, VFS path/inode events, file-descriptor flags, and user-space file watchers.

## Risks and Edge Cases

Variable-length names require careful record iteration using `len`. Event queues can overflow, move cookies must be matched carefully, watch descriptors can be reused, and `IN_MASK_CREATE`/`IN_MASK_ADD` semantics differ.

## Test Signals

Inotify tests should cover all event masks, directory filename payloads, move cookies, queue overflow, one-shot watches, symlink and only-dir flags, nonblocking reads, close-on-exec, and `SETNEXTWD` behavior.
