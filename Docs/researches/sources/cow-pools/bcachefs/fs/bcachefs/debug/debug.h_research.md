# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/debug.h

Public debug/debugfs interface for bcachefs.

Key contents:
- Declares `bch2_btree_node_ondisk_to_text()`.
- Under `CONFIG_DEBUG_FS`, defines `struct dump_iter` shared by debugfs readers.
- Declares buffer flushing, dump release, per-filesystem debug init/exit, and global debug init/exit.
- Without `CONFIG_DEBUG_FS`, provides no-op stubs and success return for `bch2_debug_init()`.

Important invariants:
- `dump_iter` carries filesystem/list/btree selection, cursor positions, print buffer, userspace destination, request size, and accumulated return count.
- Async object debugfs reuses `dump_iter`, `bch2_debugfs_flush_buf()`, and `bch2_dump_release()`.
