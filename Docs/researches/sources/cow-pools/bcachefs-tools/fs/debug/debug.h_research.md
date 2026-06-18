# File Research: sources/cow-pools/bcachefs-tools/fs/debug/debug.h

## Role

Declares core debugfs helpers and the shared dump iterator structure.

## Public API

`bch2_btree_node_ondisk_to_text()` is always declared and formats a btree node as read from disk.

When `CONFIG_DEBUG_FS` is enabled, the header declares:

- `struct dump_iter`
- `bch2_debugfs_flush_buf()`
- `bch2_dump_release()`
- Filesystem/global debug init and exit helpers.

When debugfs is disabled, filesystem and global debug init/exit functions are inline no-ops returning success where applicable.

## `struct dump_iter`

Carries the state common to debugfs streaming readers: filesystem pointer, optional async object list, btree id and level, current position, previous node, generic iterator cursor, print buffer, userspace destination buffer, requested size, and copied-byte count.
