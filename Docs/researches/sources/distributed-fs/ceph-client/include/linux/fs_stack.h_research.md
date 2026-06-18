# sources/distributed-fs/ceph-client/include/linux/fs_stack.h

Purpose: declares helper functions for stackable filesystems to copy inode attributes from lower filesystems to upper inodes without requiring the caller to hold `i_rwsem`.

Important APIs and functions: `fsstack_copy_attr_all()` and `fsstack_copy_inode_size()` are implemented in `fs/stack.c`. Inline helpers `fsstack_copy_attr_atime()` and `fsstack_copy_attr_times()` copy atime, mtime, and ctime through the modern inode timestamp accessors.

Control flow: overlay/stacking filesystems call these helpers after lower-inode changes or during lookup/revalidation to synchronize visible upper inode metadata. The file intentionally avoids locking requirements because stackable filesystems frequently operate while holding their own ordering constraints.

State and persistence: helpers update in-memory inode attributes; persistence of upper metadata is filesystem-specific. Size copying can affect writeback and stat results, while timestamp copying affects cache coherency and userspace-visible metadata.

Dependencies and integration points: depends on `linux/fs.h` inode timestamp helpers and stackable filesystem code such as overlay-like layers.

Risks and test signals: risks include stale upper attributes, racing lower changes, copying too much metadata, and timestamp granularity mismatches. Tests should cover stat consistency after lower writes, truncation/size updates, timestamp updates, and stacked filesystem behavior under concurrent operations.
