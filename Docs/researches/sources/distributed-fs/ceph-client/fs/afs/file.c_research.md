# sources/distributed-fs/ceph-client/fs/afs/file.c

Purpose: `file.c` provides regular-file VFS operations and netfs integration for AFS data I/O, open/release key management, fscache use, mmap tracking, and asynchronous fetch-data completion.

Important APIs and functions: exported tables are `afs_file_operations`, `afs_file_inode_operations`, `afs_file_aops`, `afs_req_ops`, and `afs_fetch_data_operation`. Main functions include `afs_open()`, `afs_release()`, `afs_cache_wb_key()`, `afs_issue_read()`, `afs_fetch_data_async_rx()`, `afs_file_read_iter()`, `afs_file_splice_read()`, mmap hooks, and netfs callbacks.

Control flow: open requests an AFS key, allocates per-file state, validates the vnode, caches a writeback key for writers, marks new content on truncate, and starts fscache cookie use. Buffered reads validate before filemap reads; direct reads use netfs unbuffered I/O. Netfs read requests allocate an operation and either issue async fileserver reads for readahead/iocb paths or synchronous operations otherwise. Async receive delivers rxrpc data, updates subrequest progress, rotates fileservers on failure, and terminates the netfs subrequest.

State and persistence: `struct afs_file` holds the open key and optional writeback key. Vnodes maintain writeback-key lists, fscache cookies, remote size, mmap counters, and open-mmap list links. Fetch success commits vnode status and byte counters; release fsyncs writers and unuses fscache cookies with auxiliary data.

Dependencies and integration points: VFS file operations, netfs, fscache, rxrpc calls from `fsclient.c`, server rotation, callback invalidation, writeback code, and `flock.c` lock hooks.

Risks: key and writeback-key refcounts must balance. Async read cancellation can race with completion. mmap tracking coordinates with callback work. Cache invalidation must match server data-version changes.

Test signals: read/readahead/direct/splice reads, writer release fsync, fetch cancellation and retry, fscache aux updates, mmap open/close, callback invalidation, and writeback-key reuse.
