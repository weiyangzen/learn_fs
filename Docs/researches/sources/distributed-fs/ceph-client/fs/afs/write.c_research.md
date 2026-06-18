# sources/distributed-fs/ceph-client/fs/afs/write.c

Purpose: Connects kAFS regular-file writeback to the netfs writeback framework and AFS/YFS StoreData RPC operations.

Important APIs and functions: `afs_prepare_write()` sets stream write size limits. `afs_issue_write()` queues write subrequests to `system_dfl_wq`; `afs_issue_write_worker()` builds and executes the store operation. `afs_begin_writeback()` selects a valid cached writeback key. `afs_retry_request()` rotates keys after authorization failures. `afs_writepages()`, `afs_fsync()`, and `afs_page_mkwrite()` provide VFS writeback, fsync, and mmap write validation hooks. `afs_prune_wb_keys()` removes unused cached write keys.

Control flow: Netfs writeback calls `afs_begin_writeback()` to place a key in `wreq->netfs_priv`. Each subrequest worker allocates an AFS operation for the vnode, fills store offset/length/i_size/mtime, selects the AFS or YFS RPC through `afs_store_data_operation`, waits synchronously, and reports completion to netfs. Authorization errors mark the subrequest for retry when another writeback key exists.

State and persistence: Vnode writeback keys live on `vnode->wb_keys` under `wb_lock` with usage refcounts. Successful StoreData commits vnode status, increments store counters and byte stats, and prunes keys once dirty/writeback tags are gone. `validate_lock` serializes writeback against truncation.

Dependencies and integration points: Depends on Linux netfs writeback, keyrings, AFS operation framework, vnode validation/status commit, address-space dirty/writeback tags, and YFS/AFS StoreData clients.

Risks: Key rotation depends on correct `netfs_priv2` bookkeeping and refcount drops. Large `sreq_max_len` can stress server or network behavior. Worker submission must terminate every subrequest exactly once, including allocation failures.

Test signals: Writeback with expired/revoked keys, multiple author keys, truncation racing WB_SYNC_ALL and opportunistic writeback, mmap page faults after validation failure, fsync validation errors, and pruning after all dirty/writeback pages are clear.
