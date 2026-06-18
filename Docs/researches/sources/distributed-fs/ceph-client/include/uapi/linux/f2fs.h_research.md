# sources/distributed-fs/ceph-client/include/uapi/linux/f2fs.h

This UAPI header exposes F2FS-specific ioctl constants and small ABI structures. It covers atomic/volatile writes, garbage collection, range movement, defragmentation, flush and shutdown, feature queries, compression controls, pinned files, and filesystem labels.

Important exports include `F2FS_IOCTL_MAGIC`, atomic write commands `F2FS_IOC_START_ATOMIC_WRITE`, `COMMIT_ATOMIC_WRITE`, `ABORT_ATOMIC_WRITE`, volatile write commands, `F2FS_IOC_GARBAGE_COLLECT`, `WRITE_CHECKPOINT`, `DEFRAGMENT`, `MOVE_RANGE`, `FLUSH_DEVICE`, `GET_FEATURES`, `GET_PIN_FILE`, `SET_PIN_FILE`, `PRECACHE_EXTENTS`, compression commands, and `F2FS_IOC_SHUTDOWN`. Key structures include `struct f2fs_gc_range`, `struct f2fs_defragment`, `struct f2fs_move_range`, and `struct f2fs_flush_device`.

Control flow is ioctl driven on files or directories in an F2FS mount. Commands mutate per-inode atomic/volatile write state, trigger segment cleaning, flush checkpoint/device state, manipulate extents, or query features. State lives in the mounted F2FS superblock, segment cleaner, checkpoint pack, inode flags, compression metadata, and pinned-file accounting. Persistence varies: feature and label state is persistent, compression and pinning are inode metadata, and GC/flush actions affect on-disk placement.

Dependencies are `linux/types.h`, `linux/ioctl.h`, and the F2FS filesystem implementation. Integration points include Android/storage tooling, fsck.f2fs, generic VFS ioctl routing, block discard/flush paths, compression infrastructure, and xfstests.

Risks include data-loss semantics around atomic/volatile write abort/commit, GC latency and wear behavior, alignment and range validation bugs, shutdown mode misuse, and ABI compatibility when adding ioctl structures. Test signals include F2FS xfstests for atomic writes, GC, defrag, compression, shutdown, feature queries, 32-bit compat ioctls, and fsck/mount persistence checks.
