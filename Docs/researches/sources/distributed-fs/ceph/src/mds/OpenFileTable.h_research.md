# sources/distributed-fs/ceph/src/mds/OpenFileTable.h

Purpose: declares the `OpenFileTable` class and its public contract for tracking open inodes/dirfrags, persisting their anchors, loading/prefetching state after failover, and coordinating journal-log sequence durability.

Important APIs and types: callers use `add_inode()`, `remove_inode()`, `add_dirfrag()`, `remove_dirfrag()`, `notify_link()`, `notify_unlink()`, `commit()`, `load()`, `prefetch_inodes()`, `should_log_open()`, `wait_for_load()`, `wait_for_prefetch()`, and `wait_for_commit()`. Protected helpers expose object naming, header encoding, omap read/load/recover, ancestor reconstruction, and reference accounting. Constants include dynamic `MAX_ITEMS_PER_OBJ`, fixed `MAX_OBJECTS`, dirty sentinels, and prefetch/journal state enums.

State and persistence: the header shows the full persistent model: `omap_version`, `omap_num_objs`, `omap_num_items`, `anchor_map`, `dirty_items`, and `loaded_anchor_map`. It also declares transient coordination state for pending commits, committed/committing log sequences, loaded journals, load/prefetch waiters, destroyed inode tracking, perf counters, and commit waiters.

Dependencies and integration: includes CephFS inode/object/frag types, `mdstypes.h`, config access for the omap threshold, and forward declarations for MDS cache objects. Friend context classes in the `.cc` complete asynchronous objecter reads/writes on the MDS finisher.

Risks and test signals: consumers must not call `wait_for_load()` or `wait_for_prefetch()` after the corresponding state is done because the methods assert the opposite. The API assumes callers serialize through normal MDS locking and only call `commit()` when no other commit is pending. The most useful tests exercise load-before-prefetch, wait-for-commit ordering, and the `should_log_open()` suppression rules.
