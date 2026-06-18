# sources/distributed-fs/ceph-client/fs/ocfs2/uptodate.h

Purpose: declares the cluster-aware metadata uptodate cache interface and the callback table that lets generic cache code lock and identify different OCFS2 caching objects.

Important APIs and types: defines `struct ocfs2_caching_operations` with owner, superblock, cache lock/unlock, and I/O lock/unlock callbacks. Declares cache lifecycle, lookup, insertion, removal, readahead, and slab init/exit functions implemented in `uptodate.c`.

Control flow: users initialize an embedded `struct ocfs2_caching_info` with callbacks, wrap disk I/O with `ocfs2_metadata_cache_io_lock/unlock`, test buffers with `ocfs2_buffer_uptodate`, mark successful reads or new metadata with set helpers, and purge or remove cached block numbers when metadata validity changes.

State and persistence behavior: the header defines no storage itself, but its callbacks operate on runtime cache state in OCFS2 inode or metadata objects. No on-disk format changes are made by this layer.

Dependencies and integration points: consumed by inode initialization, buffer-head I/O, allocators, xattrs, journal access, and cluster lock invalidation paths. The callback abstraction avoids hardcoding inode locks into the cache implementation.

Risks: callback implementations must obey locking expectations: cache locks should not sleep, I/O locks may sleep, and owner/super callbacks must remain valid for the cache lifetime. Incorrect locking around set/remove can produce stale metadata reads on clustered mounts.

Test signals: cache users with lockdep enabled, purge under cluster lock invalidation, readahead detection while a buffer is locked, metadata creation with `ocfs2_set_new_buffer_uptodate`, and build-time coverage of all declared functions.
