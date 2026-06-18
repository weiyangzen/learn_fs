# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/fd.h

## Purpose
Defines GlusterFS file descriptor objects and fd tables. These objects connect open-file state to inodes, translator-private fd context, anonymous fd handling, and process fd-number allocation.

## APIs, Types, and Functions
`fd_t` stores pid, flags, atomic refcount, inode list membership, inode pointer, context lock, per-xlator `_fd_ctx` array, lock context, translator count, and anonymous status. `fdtable_t` is a refcounted table with rwlock, max size, entries, and free-list head. APIs allocate/destroy fd tables, get/free fd numbers, get fd pointers, copy/get all fds, create/look up/bind/close/ref/unref fds, create anonymous fds, test anonymous/list-empty state, and set/get/delete translator context values.

## Control Flow, State, and Persistence
`fd_t` state is volatile but long-lived for open handles. It is linked into an inode's fd list, referenced by call frames and translators, and eventually closed/unrefed. `fdtable_t` tracks process-visible numeric fd slots with `first_free` and sentinel values `GF_FDTABLE_END` and `GF_FDENTRY_ALLOCATED`.

## Dependencies and Integration
Depends on `list.h`, `glusterfs.h`, `fd-lk.h`, logging, and `xlator.h`. It is central to open/create/read/write/flush/fsync/lock paths and to protocol client/server fd translation.

## Risks and Test Signals
Risks include fdtable expansion/free-list corruption, fd context races, anonymous fd misuse, refcount leaks, and stale inode links. Test signals include fd allocation/free reuse tests, concurrent lookup/ref/unref stress, statedump context inspection, anonymous fd paths, and lock context cleanup on close.
