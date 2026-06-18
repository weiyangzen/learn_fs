# sources/distributed-fs/ceph-client/fs/ceph/addr.c

## Purpose

`addr.c` implements CephFS address-space, netfs, writeback, mmap, inline-data, and data-pool permission behavior for regular file I/O. It is the bridge between Linux page-cache/netfs callbacks and Ceph OSD object requests, while preserving Ceph-specific invariants around snapshot contexts, MDS capabilities, fscrypt block alignment, fscache coherency, and forced-unmount shutdown.

The file is not just a VFS operation table. It owns the rules for attaching a `ceph_snap_context` to every dirty folio, writing dirty folios in snapshot order, converting inline data to object data, servicing mmap faults with capability references, and lazily probing read/write permission against the data pool namespace.

## Important APIs, Types, and Functions

The exported operation tables are `ceph_netfs_ops`, `ceph_aops`, and the internal `ceph_vmops`. `ceph_netfs_ops` wires Ceph into netfs via `ceph_init_request`, `ceph_netfs_free_request`, `ceph_netfs_prepare_read`, `ceph_netfs_issue_read`, `ceph_netfs_expand_readahead`, and `ceph_netfs_check_write_begin`. `ceph_aops` provides `read_folio`, `readahead`, `writepages`, `write_begin`, `write_end`, `dirty_folio`, `invalidate_folio`, `release_folio`, `direct_IO`, and `migrate_folio`.

`struct ceph_writeback_ctl` is the central writeback scratch state. It tracks the selected snapshot context, stable size/truncate metadata, page index range, folio batches, OSD op grouping, page arrays, and whether the page array came from the fallback mempool. Helpers such as `ceph_init_writeback_ctl`, `ceph_define_writeback_range`, `ceph_check_page_before_write`, `ceph_process_folio_batch`, `ceph_submit_write`, and `ceph_wait_until_current_writes_complete` form the bulk writeback pipeline.

Read-side functions include `ceph_netfs_expand_readahead`, `finish_netfs_read`, `ceph_netfs_issue_op_inline`, `ceph_netfs_prepare_read`, and `ceph_netfs_issue_read`. Write-side functions include `ceph_dirty_folio`, `ceph_invalidate_folio`, `write_folio_nounlock`, `writepages_finish`, `ceph_writepages_start`, `ceph_write_begin`, `ceph_write_end`, `ceph_page_mkwrite`, and `ceph_uninline_data`. Pool permission support is provided by `ceph_pool_perm_check`, `__ceph_pool_perm_get`, and `ceph_pool_perm_destroy`.

## Control Flow

Buffered reads enter through netfs. `ceph_init_request` sets legacy `PG_private_2` behavior, captures per-file readahead settings for readahead requests, and for readahead without an existing rw context tries to take `CEPH_CAP_FILE_RD` plus `CEPH_CAP_FILE_CACHE`. `ceph_netfs_prepare_read` caps each subrequest to the current object-layout extent and mount `rsize`. `ceph_netfs_issue_read` rejects shutdown inodes, handles inline data through an MDS `GETATTR` fast path, adjusts encrypted reads to full fscrypt blocks, creates either a normal or sparse OSD read, attaches either iter data or page-array data, and completes through `finish_netfs_read`.

`finish_netfs_read` converts OSD results into netfs subrequest status. `-ENOENT` becomes a successful hole with clear-tail semantics, `-EBLOCKLISTED` marks the filesystem client, sparse reads are converted through `ceph_sparse_ext_map_end`, encrypted sparse extents are decrypted by `ceph_fscrypt_decrypt_extents`, OSD page vectors are released, metrics are updated, and the netfs subrequest is terminated.

Dirtying a folio starts in `ceph_dirty_folio`. It increments the MDS client dirty-folio counter, selects either the newest pending capsnap context or the live head snap context, increments inode write-buffer counters, pins the inode on the first dirty page, attaches the snap context to folio private data, and then delegates dirty marking to fscache/netfs. `ceph_invalidate_folio` reverses that accounting for full-folio invalidation by detaching private snap context state and calling `ceph_put_wrbuffer_cap_refs`.

Writeback starts in `ceph_writepages_start`. It refuses opportunistic writeback during client write congestion, aborts on forced unmount, initializes `ceph_writeback_ctl`, acquires an OSD stopping blocker, chooses the oldest writable snap context, tags pages if doing sync writeback, scans folios with the selected writeback tag, locks and filters folios by snap context and EOF, encrypts page-cache pages into bounce pages when needed, groups contiguous and discontinuous ranges into OSD write ops, and submits asynchronous OSD writes. If non-head snap contexts remain, it may loop back to the start of the file and wait for current writes before proceeding to the next snap context.

`writepages_finish` is the async completion path. It sets mapping errors and Ceph write-error state on failure, detects loss of cache/lazyio caps and removes folios when necessary, frees fscrypt bounce pages, clears page private snap-context state, ends writeback, decrements dirty-folio and writeback congestion counters, updates metrics, drops wrbuffer cap refs, frees the request page array, and releases the OSD stopping blocker.

`ceph_write_begin` uses `netfs_write_begin` and waits for any fscache private-2 write. The netfs `check_write_begin` callback calls `ceph_find_incompatible`; if the target folio is dirty under a newer/unwritable snapshot context, it queues writeback and waits until that context is writeable or already written, then returns `-EAGAIN`. `ceph_write_end` marks the folio uptodate, updates inode size if needed, marks it dirty, and triggers an auth-only cap check if size changed.

`ceph_filemap_fault` takes read/cache/lazyio caps before letting `filemap_fault` populate mmap reads. If inline data is still present and cache caps are not available, it fetches inline data into page 0. `ceph_page_mkwrite` takes write/buffer/lazyio caps, updates timestamps and i_version, resolves snapshot-context conflicts, marks the folio dirty, marks write caps dirty with a preallocated cap flush, and drops cap refs asynchronously.

`ceph_uninline_data` migrates inline file contents into object storage. It captures the inline version, obtains the correct snap context, reads page 0, creates the first object, writes inline content guarded by `inline_version` xattrs, and then marks `i_inline_version` as `CEPH_INLINE_NONE` through dirty capability metadata.

Pool permission checking is lazy and cached. `ceph_pool_perm_check` skips non-regular files, snapshots, and `NOPOOLPERM` mounts. Otherwise it checks inode flags and, if unknown, calls `__ceph_pool_perm_get`, which uses an MDS-client rb-tree cache keyed by pool and namespace. On a miss it issues an OSD `STAT` request and an exclusive `CREATE` request against the first object name to infer read/write permission, caches the result, and stores inode-level permission flags if the layout is unchanged.

## State and Persistence Behavior

The most important persistent state is not on disk but in kernel inode and request structures. Dirty folios carry `ceph_snap_context` references in folio private data. `ceph_inode_info` maintains `i_wrbuffer_ref`, `i_wrbuffer_ref_head`, capsnap dirty-page counts, `i_head_snapc`, truncate metadata, inline-data version, cached layout, and pool permission flags. The MDS client tracks global dirty-folio and writeback counts, pool permission cache, metrics, and shutdown/blocklist state.

OSD writes persist data objects and update object xattrs for inline-data migration. MDS capability dirtying persists metadata later through `caps.c`; this file marks dirty caps and depends on cap flushes for metadata durability. Fscache volume/cookie state is updated or invalidated when buffered data is written, truncated, invalidated, or read-cache caps are revoked.

## Dependencies and Integration Points

This file depends heavily on Linux netfs, page-cache, writeback, mmap, fscrypt, fscache, and VFS helpers. Ceph integrations include MDS capability functions from `caps.c`, inode/session helpers from `super.h` and `mds_client.h`, OSD request helpers from `osd_client` and `striper`, metrics from `metric.h` and `subvolume_metrics.h`, fscache wrappers from `cache.h`, and fscrypt wrappers from `crypto.h`.

The implementation assumes `caps.c` correctly arbitrates `CEPH_CAP_FILE_RD`, `CEPH_CAP_FILE_CACHE`, `CEPH_CAP_FILE_WR`, `CEPH_CAP_FILE_BUFFER`, `CEPH_CAP_FILE_LAZYIO`, and snapshot-cap flushing. It also assumes `crypto.c` can decrypt sparse extents and encrypt page-cache pages using full 4 KiB fscrypt blocks.

## Risks and Edge Cases

High-risk areas are snapshot-ordered writeback, dirty folio accounting, fscrypt alignment, and capability revocation. A missed `ceph_put_wrbuffer_cap_refs` or snap-context put can leak inode references or prevent capsnap completion. Writing a folio under the wrong snap context breaks snapshot consistency. Encrypted reads/writes must be rounded to fscrypt blocks without confusing netfs or sparse-read lengths. Forced unmount and blocklisting paths must set mapping errors and stop future I/O cleanly.

The OSD pool permission probe intentionally creates or stats object names; snapshots skip it to avoid orphan objects. Race handling around layout changes rechecks pool id and namespace before setting inode flags. Inline-data migration has concurrency risk around `inline_version`; the OSD write uses compare/set xattrs and treats `-ECANCELED` as a benign race.

## Test Signals

Useful tests include buffered read/write with and without fscache, encrypted file reads/writes crossing block and object boundaries, sparse reads over encrypted holes, mmap read and write faults, forced unmount during dirty writeback, blocklist error injection, snapshot creation while pages are dirty, writeback under memory reclaim, inline-file reads and uninline conversion, fadvise random readahead disabling, and pool-permission checks with read-only/write-denied pools and pool namespaces. Kernel signals include mapping writeback errors, dirty-folio counter balance, cap wait wakeups, OSD request metrics, absence of leaked writeback pages, and correct cache invalidation on cap revoke.
