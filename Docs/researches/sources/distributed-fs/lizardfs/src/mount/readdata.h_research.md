## sources/distributed-fs/lizardfs/src/mount/readdata.h

Purpose: declares the read-data subsystem API used by the client file operations.

Important APIs: timeout/prefetch getters, `read_inode_ops` for invalidation after inode attribute changes, lifecycle `read_data_init`/`read_data_term`, per-open `read_data_new`/`read_data_end`, and `read_data` returning a `ReadCache::Result` for requested aligned ranges.

Integration: includes `chunk_locator` and `readdata_cache`; parameters expose chunkserver RTT/connect/wave/total timeouts, cache expiration, readahead max window, XOR prefetch, and bandwidth overuse tuning.

Risks and tests: `read_data_freebuff` is declared but not defined in the implementation read for this item, suggesting legacy API drift. Callers must provide block-aligned `offset` and `size` because implementation asserts alignment.
