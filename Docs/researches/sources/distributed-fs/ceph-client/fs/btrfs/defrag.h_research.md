# sources/distributed-fs/ceph-client/fs/btrfs/defrag.h

Purpose: declares the Btrfs defragmentation interface for file defrag, automatic inode defrag queueing/running, root metadata defrag, cleanup, and init/exit of the autodefrag slab cache. It is a small private header connecting ioctl/writeback/autodefrag callers to `defrag.c`.

Important APIs/types/functions: `btrfs_defrag_file()` is the public file-range defrag entry point taking a `btrfs_inode`, readahead state, ioctl range args, minimum generation, and optional maximum sectors. `btrfs_add_inode_defrag()` queues an inode for autodefrag with an extent-size threshold. `btrfs_run_defrag_inodes()` drains queued auto-defrag records for a filesystem. `btrfs_cleanup_defrag_inodes()` frees pending records, typically during teardown. `btrfs_defrag_root()` defragments metadata leaves for a root. `btrfs_auto_defrag_init()` and `btrfs_auto_defrag_exit()` manage the inode-defrag cache. `btrfs_defrag_cancelled()` currently maps cancellation to `signal_pending(current)`.

Control flow: higher layers call `btrfs_add_inode_defrag()` when write patterns indicate fragmentation and autodefrag is enabled. Worker or transaction contexts call `btrfs_run_defrag_inodes()` to process the queue. User ioctl paths call `btrfs_defrag_file()` directly with range/compression flags. Metadata maintenance can call `btrfs_defrag_root()` for root leaf reallocation. Long loops periodically call `btrfs_defrag_cancelled()` to stop on pending signals.

State and persistence: this header owns no state. It exposes functions that operate on `fs_info` defrag queues, inode runtime flags, root defrag progress fields, dirty page-cache/delalloc state, and transaction-persisted metadata COW. The cancellation helper does not store cancellation state and currently ignores its `fs_info` argument.

Dependencies and integration: includes Linux types/compiler annotations and forward-declares file readahead, Btrfs inode/root/fs/trans types, and ioctl defrag range args. It is included by code that needs to schedule or execute Btrfs defrag without depending on the full implementation details.

Risks: the cancellation policy is minimal and signal-based only; future filesystem-wide cancellation would require changing `btrfs_defrag_cancelled()` semantics. Callers must provide a valid `file_ra_state` to `btrfs_defrag_file()` and must understand that non-negative returns are sector counts, not just boolean success. Because many structs are forward-declared, compile errors will only appear in C files that dereference fields without including fuller headers.

Test signals: compile all autodefrag/ioctl/root-defrag users, verify init/exit ordering around mount/unmount/module teardown, and run cancellation tests that deliver signals during long file and root defrag loops. API behavior checks should verify `btrfs_defrag_file()` return values, `range->start` updates, and queue cleanup on unmount.
