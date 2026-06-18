# sources/distributed-fs/ceph-client/include/linux/dnotify.h

## Purpose
This header declares legacy directory notification support. It associates directory notification masks with file descriptors and file owners, and exposes the fcntl setup and flush hooks.

## Important APIs, types, and functions
`struct dnotify_struct` stores a linked-list node, event mask, file descriptor, `struct file *`, and owner. `DNOTIFY_ALL_EVENTS` combines delete, modify, access, attrib, create, rename, and move events. Kernel APIs are `dnotify_flush()` and `fcntl_dirnotify()` when `CONFIG_DNOTIFY` is enabled.

## Control flow, state, and persistence
State persists as per-file dnotify records. `fcntl_dirnotify()` installs or updates notification state for a file descriptor; `dnotify_flush()` removes records for an owner when a file is closed or ownership ends.

## Dependencies and integration points
It depends on `linux/fs.h` for file, owner, and event flags. It integrates with fcntl, VFS file lifetime, and fsnotify-style events. When disabled, `fcntl_dirnotify()` returns `-EINVAL` and flush is a no-op.

## Risks and test signals
Risks include stale owner/file references, event mask mismatch with fsnotify flags, and compatibility behavior for applications still using dnotify. Tests should cover install, event delivery, close/flush cleanup, unsupported-config behavior, and interaction with rename/move child events.
