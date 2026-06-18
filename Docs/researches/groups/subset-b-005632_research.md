# subset-b-005632 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/addr.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/cache.c -->
# sources/distributed-fs/ceph-client/fs/ceph/cache.c

## Purpose

`cache.c` implements the runtime fscache glue for CephFS. It registers an fscache volume for a mounted Ceph filesystem, acquires per-inode cache cookies for regular files, and wraps cookie use, updates, and invalidation so address-space code can cache remote file data coherently.

## Important APIs and Functions

`ceph_fscache_register_fs` builds a volume name from the cluster fsid plus optional `fscache_uniq` mount option and calls `fscache_acquire_volume`. `ceph_fscache_unregister_fs` relinquishes that volume.

`ceph_fscache_register_inode_cookie` acquires a per-inode cookie keyed by `ceph_vino`, versioned by `ci->i_version`, and sized from `i_size_read`. It only registers cookies when the mount has fscache enabled, the inode is a regular file, and the inode is new. `ceph_fscache_unregister_inode_cookie` relinquishes the cookie.

`ceph_fscache_use_cookie` and `ceph_fscache_unuse_cookie` bracket modifications or read/write activity; the update path passes the current inode version and size back to fscache. `ceph_fscache_update` updates cookie coherency metadata. `ceph_fscache_invalidate` invalidates cached contents and marks direct-I/O invalidations with `FSCACHE_INVAL_DIO_WRITE`.

## Control Flow

Mount setup calls `ceph_fscache_register_fs`; failures are reported through `errorfc` and leave `fsc->fscache` null so later inode registration is skipped. New regular inodes call `ceph_fscache_register_inode_cookie`, which stores the acquired cookie in `ci->netfs.cache` and sets `mapping_set_release_always` so release callbacks run even when pages look otherwise releasable.

Buffered writeback and cache invalidation code in `addr.c` call the cookie wrappers. When `update` is true during unuse, the cookie receives both `i_version` and current size to keep the cache coherent with MDS-observed file changes.

## State and Persistence Behavior

The persistent external state is the local fscache backend’s volume and per-file cached data. In kernel memory, the Ceph filesystem client stores the volume cookie in `fsc->fscache`; each inode stores the netfs/fscache cookie in `ci->netfs.cache`. Cookie coherency depends on `ci->i_version` and `i_size`.

## Dependencies and Integration Points

This file depends on Linux fscache and netfs APIs, `fs_context` for mount error reporting, and Ceph inode/client helpers from `super.h`. `addr.c` uses these wrappers for dirty folios, write-to-cache, resize, invalidation, and cache-enabled checks via `cache.h`.

## Risks and Edge Cases

The code intentionally avoids caching non-regular or non-new inodes. A stale or missing `i_version` update can expose old cached data. Direct I/O invalidation must carry the direct-write flag so fscache does not trust cached pages across external writes. Registration failures degrade to no cache rather than failing the mount in all cases.

## Test Signals

Exercise mounts with and without fscache, unique fscache volume names, regular versus directory/special inode registration, cache invalidation after direct I/O, writes followed by remount/readback, and fscache backend unavailability. Useful signals are non-null `ci->netfs.cache` only for eligible files, no cache use when `fsc->fscache` is null, and correct cache invalidation/update traces under writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/cache.h -->
# sources/distributed-fs/ceph-client/fs/ceph/cache.h

## Purpose

`cache.h` declares the CephFS fscache interface and provides compile-time fallbacks when `CONFIG_CEPH_FSCACHE` is disabled. It keeps the rest of the Ceph client code able to call cache helpers unconditionally while mapping those calls either to real fscache/netfs operations or to no-op/filemap behavior.

## Important APIs and Types

With `CONFIG_CEPH_FSCACHE`, the header declares the implementation functions from `cache.c`: filesystem volume registration, inode cookie registration, cookie use/unuse, cookie update, and invalidation. It also defines `ceph_fscache_cookie`, `ceph_fscache_resize`, `ceph_fscache_unpin_writeback`, `ceph_fscache_dirty_folio`, and `ceph_is_cache_enabled`.

Without fscache support, the same names are provided as static inline no-ops or simple fallbacks. `ceph_fscache_dirty_folio` becomes `filemap_dirty_folio`, `ceph_fscache_cookie` returns `NULL`, `ceph_fscache_unpin_writeback` returns success, and `ceph_is_cache_enabled` returns false.

## Control Flow

The header’s control flow is entirely compile-time. Code in `addr.c`, mount setup, and inode teardown can call the Ceph fscache API without surrounding every callsite with preprocessor checks. When enabled, dirty folio handling goes through netfs/fscache dirty tracking; when disabled, it uses normal filemap dirtying.

## State and Persistence Behavior

When enabled, the inline helpers expose the fscache cookie stored in `ci->netfs` and allow cache resize operations to be bracketed by cookie use/unuse calls. When disabled, no cache state is stored or persisted and all state-changing helpers are empty.

## Dependencies and Integration Points

The header depends on `<linux/netfs.h>` unconditionally and `<linux/fscache.h>` when enabled. It integrates directly with `struct ceph_inode_info`, `struct ceph_fs_client`, VFS `inode`, `fs_context`, and writeback-control paths. `addr.c` relies on the macro/function compatibility layer to keep writeback and invalidation code simple.

## Risks and Edge Cases

The main risk is semantic divergence between enabled and disabled builds. In enabled builds, dirty-folio behavior uses netfs, private-2 writeback pinning, and cookie coherency; disabled builds bypass all of that. The resize helper must use/unuse the cookie only when a cookie exists. Function signatures in both branches must remain synchronized or build coverage will differ by config.

## Test Signals

Build and boot-test both `CONFIG_CEPH_FSCACHE=y` and disabled configurations. Check that buffered writes mark dirty folios correctly in both modes, cache resize/invalidate callsites compile without ifdefs, and no fscache symbols are referenced in disabled builds. Runtime tests should verify `ceph_is_cache_enabled` follows cookie state only in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/caps.c -->
# sources/distributed-fs/ceph-client/fs/ceph/caps.c

## Purpose

`caps.c` implements CephFS client capability management. Capabilities are the MDS-issued permissions that let a client cache inode metadata, cache or buffer file data, perform directory operations, write file data to OSDs, and delay metadata flushes. This file tracks capability objects, desired/used/dirty/revoking bitmasks, MDS session ownership, cap import/export during MDS migration, cap flush ordering, capsnap metadata for snapshots, and release encoding for outgoing MDS requests.

It is the synchronization core that makes `addr.c` safe: page-cache reads/writes, mmap faults, inline-data conversion, and fsync all depend on the cap state machine here to decide when data or metadata can be cached, dirtied, flushed, revoked, or waited on.

## Important APIs, Types, and Functions

The public lifecycle APIs include `ceph_caps_init`, `ceph_caps_finalize`, `ceph_adjust_caps_max_min`, `ceph_reserve_caps`, `ceph_unreserve_caps`, `ceph_get_cap`, `ceph_put_cap`, and `ceph_reservation_status`. These manage the MDS client’s slab-backed pool of `struct ceph_cap` objects and enforce total/used/reserved/available invariants.

Per-inode lookup and installation are handled by `__get_cap_for_mds`, `ceph_get_cap_for_mds`, `ceph_add_cap`, `__ceph_remove_cap`, `ceph_remove_cap`, and `__ceph_remove_caps`. Cap objects are indexed in `ci->i_caps` by MDS id and also linked into each session’s LRU/list.

Capability query and desire computation are handled by `__ceph_caps_issued`, `__ceph_caps_issued_other`, `__ceph_caps_issued_mask`, `__ceph_caps_issued_mask_metric`, `__ceph_caps_revoking_other`, `__ceph_caps_used`, `__ceph_caps_file_wanted`, `__ceph_caps_wanted`, and `__ceph_caps_mds_wanted`.

Reference acquisition and release are centered on `try_get_cap_refs`, `ceph_try_get_caps`, `__ceph_get_caps`, `ceph_get_caps`, `ceph_take_cap_refs`, `ceph_get_cap_refs`, `ceph_put_cap_refs`, `ceph_put_cap_refs_async`, and `ceph_put_wrbuffer_cap_refs`. File-open mode accounting is handled by `ceph_get_fmode`, `ceph_put_fmode`, and `__ceph_touch_fmode`.

Dirty metadata and flushing are handled by `__ceph_mark_dirty_caps`, `ceph_alloc_cap_flush`, `ceph_free_cap_flush`, `__mark_caps_flushing`, `try_flush_caps`, `caps_are_flushed`, `ceph_fsync`, `ceph_write_inode`, `ceph_check_caps`, `ceph_flush_dirty_caps`, and the kick helpers `ceph_early_kick_flushing_caps`, `ceph_kick_flushing_caps`, and `ceph_kick_flushing_inode_caps`.

MDS message handling is centered on `encode_cap_msg`, `__prep_cap`, `__send_cap`, `__send_flush_snap`, `ceph_flush_snaps`, `handle_cap_grant`, `handle_cap_flush_ack`, `handle_cap_flushsnap_ack`, `handle_cap_trunc`, `handle_cap_export`, `handle_cap_import`, `parse_fscrypt_fields`, and `ceph_handle_caps`. Release encoding uses `ceph_encode_inode_release` and `ceph_encode_dentry_release`.

## Control Flow

A typical cap starts as a reserved or freshly allocated `struct ceph_cap`, then `ceph_add_cap` attaches it to an inode and MDS session. The function updates snap realm association, records auth-cap ownership, stores issued/wanted/sequence state, checks side effects of newly issued caps, and queues delayed cap checking if issued caps exceed actual wants.

Callers acquire usable cap references through `ceph_try_get_caps` or `ceph_get_caps`. The internal `try_get_cap_refs` checks file-lock error state, pending truncates, currently issued and implemented caps, write max-size limits, pending capsnaps, readonly MDS sessions, shutdown state, and MDS wanted state. On success it increments per-inode reference counters through `ceph_take_cap_refs`; on transient failure the blocking path waits on `ci->i_cap_wq`, biases fmode refs to keep wants alive, requests larger max_size, or renews caps after stale sessions.

When writes or metadata changes dirty inode state, `__ceph_mark_dirty_caps` sets `ci->i_dirty_caps`, installs a preallocated cap-flush object, ensures a head snap context exists, links the inode to the auth session’s dirty list, takes an inode reference for writeback, and queues delayed cap flushing. Later, `ceph_check_caps` compares file-wanted, used, dirty, issued, implemented, revoking, and retain masks. It may invalidate page cache, queue writeback, mark dirty caps flushing, send cap update/flush messages, or delay cap release.

`__prep_cap` is the state transition point before sending a cap message. It applies retained caps, moves implemented caps through revocation state, records wanted caps, captures size, max_size, xattrs, timestamps, mode/uid/gid, inline-data status, fscrypt auth, flags, flush tid, and oldest flush tid. `encode_cap_msg` serializes these fields into the current MDS cap message format, including fscrypt rounded size plus real file size when encryption is enabled.

Flush acknowledgements reverse the dirty/flushing state. `handle_cap_flush_ack` removes acknowledged cap-flush records up to the acknowledged tid, clears `i_flushing_caps`, removes the inode from flushing lists when clean, wakes inode and MDS waiters, and drops the inode reference taken when the inode became dirty. Snapshot flush acknowledgements go through `handle_cap_flushsnap_ack`, remove matching `ceph_cap_snap` records by `follows` and tid, drop snap contexts, and wake waiters.

`ceph_handle_caps` is the message dispatcher. It decodes versioned MDS cap messages, including snap trace, peer migration fields, inline data, epoch barrier, pool namespace, btime/change_attr, dirstats, and fscrypt fields. It finds the inode, locks the session, dispatches import/export/grant/revoke/flush-ack/trunc operations, updates snap realms on import, and sends cap releases if the MDS references an inode/cap the client no longer has.

Import/export handle MDS authority migration. `handle_cap_export` moves or creates placeholder caps for the target session and transfers auth ownership and flushing-list membership if needed. `handle_cap_import` installs the imported auth cap, removes the peer export cap when appropriate, and then lets `handle_cap_grant` apply the imported grant and wake waiters.

`ceph_fsync` first waits for file data writeback, then for full fsync flushes dirty caps and unsafe MDS requests, and waits for non-file-write metadata caps to be acknowledged. `ceph_write_inode` either flushes caps synchronously for sync writeback or queues immediate cap checking for asynchronous writeback.

## State and Persistence Behavior

Core state lives in `ceph_inode_info`: cap rb-tree, auth cap pointer, dirty/flushing cap masks, cap flush list, delayed cap list membership, cap snap list, wanted max size, requested max size, reported size, head snap context, read-cache generation, file-mode refcounts, cap refs (`i_rd_ref`, `i_rdcache_ref`, `i_wr_ref`, `i_wb_ref`, `i_wrbuffer_ref`, `i_fx_ref`, `i_pin_ref`), inline and fscrypt metadata, xattr blobs, layout, and error flags.

MDS-client/session state includes cap object accounting, session cap lists, delayed release lists, dirty/flushing lists, global cap flush list, last flush tid, wait queues, metrics, and session generation/ttl. Cap flush tids provide ordering for waiters and reconnect replay.

Persistence occurs by sending cap messages to the MDS. Dirty metadata is not durable until the MDS acknowledges cap flushes or unsafe requests complete. Fscrypt auth context and real encrypted file size are included in cap messages; file data itself persists through OSD writes in `addr.c`, while caps record metadata such as size, times, xattrs, mode, uid/gid, inline state, and change attribute.

## Dependencies and Integration Points

This file depends on MDS sessions and requests, messenger sends, snap realm management, xattr/security helpers, fscrypt definitions, fscache invalidation, page-cache invalidation, writeback, file locks, and OSD epoch barriers. It integrates with `addr.c` through cap acquisition/release, dirty cap marking, wrbuffer refs, writeback queueing, mmap page-mkwrite, and fsync/write_inode paths. It integrates with directory/dentry code through dentry lease and inode release encoding, complete-directory invalidation, async dirops, and unlink cap dropping.

## Risks and Edge Cases

The highest-risk area is concurrent cap state transitions under multiple locks (`i_ceph_lock`, session mutex, session cap lock, MDS client mutex, snap rwsem, cap dirty lock, and cap delay lock). Deadlocks are avoided by carefully dropping locks before message sends, target-session opens, or blocking waits. Incorrect ordering can strand dirty caps, lose revocation acks, or race MDS migration.

Dirty/flushing accounting is fragile. Losing a `ceph_cap_flush`, failing to propagate `wake` to earlier flush records, or mishandling `i_head_snapc` can hang fsync or leak inode refs. Revocation while writeback or invalidation is in progress is another risk; code queues writeback/invalidate rather than acknowledging too early. Fscrypt fields add risk because encrypted inodes report rounded cap-message size plus a separate real file size. MDS import/export messages can arrive out of order, so sequence and migrate-sequence comparisons are critical.

Shutdown, reconnect, and blocklist paths intentionally drop dirty state and set mapping/filelock errors. These paths trade data availability for unmount/recovery progress and need focused fault-injection coverage.

## Test Signals

Important tests include cap grant/revoke under buffered reads and writes, mmap writers during revocation, fsync waiting for dirty metadata, snapshot creation with dirty data and capsnaps, MDS failover/reconnect with flushing caps, cap import/export during active writeback, encrypted file size/fscrypt-auth propagation, directory complete-cache invalidation on FILE_SHARED changes, file-lock error behavior after cap purge, unlink/drop-cap release encoding, and memory-pressure cap trimming.

Useful runtime signals are balanced cap object counters, no stuck entries in dirty/flushing lists after flush acks, `ci->i_cap_wq` wakeups for waiters, cap hit/miss metrics, bounded delayed-cap queue progress, correct `oldest_flush_tid` propagation, and successful `file_write_and_wait_range` plus metadata flush completion for fsync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/caps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/ceph_frag.c -->
# sources/distributed-fs/ceph-client/fs/ceph/ceph_frag.c

## Purpose

`ceph_frag.c` implements comparison for Ceph fragment identifiers. Ceph directory fragmentation uses encoded frag values and bit widths; this helper provides a deterministic ordering for two `__u32` frag values.

## Important APIs and Functions

The only function is `ceph_frag_compare(__u32 a, __u32 b)`. It extracts the fragment value with `ceph_frag_value`, compares those values first, and if equal compares the fragment bit width from `ceph_frag_bits`. It returns `-1`, `1`, or `0` in the usual comparator style.

## Control Flow

The function is linear and branch-only: compare values, return if different; compare bit widths, return if different; otherwise return equality. There is no allocation, locking, or external state mutation.

## State and Persistence Behavior

No state is stored or persisted. The function derives ordering entirely from encoded frag arguments.

## Dependencies and Integration Points

It includes `<linux/ceph/types.h>` for the frag encoding helpers and `<linux/module.h>` for kernel compilation context. Callers elsewhere in the Ceph client can use this comparator to maintain sorted fragment structures or compare directory-fragment identifiers consistently with Ceph encoding rules.

## Risks and Edge Cases

Correctness depends on `ceph_frag_value` and `ceph_frag_bits` matching the wire/in-memory encoding. Sorting by value before bit width must match all callers’ expectations; reversing that order would change fragment tree traversal behavior. Equal encoded value and bits compare equal even if higher unused bits differ in a malformed input; validation is expected elsewhere.

## Test Signals

Unit-level tests should compare fragments with lower/higher values, identical values with lower/higher bit counts, and exact equality. Integration signals are stable ordering in directory-fragment maps and no inconsistent fragment comparisons during readdir or MDS frag updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/ceph_frag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/crypto.c -->
# sources/distributed-fs/ceph-client/fs/ceph/crypto.c

## Purpose

`crypto.c` adapts Linux fscrypt to CephFS. It stores and retrieves encryption context through MDS inode metadata, encodes encrypted filenames into Ceph-safe base64 names with hashing for long names, decodes MDS names for user presentation, prepares encrypted readdir, and encrypts/decrypts page arrays used by OSD I/O.

## Important APIs, Types, and Functions

The fscrypt operation hooks are `ceph_crypt_get_context`, `ceph_crypt_set_context`, `ceph_crypt_empty_dir`, `ceph_get_dummy_policy`, and the `ceph_fscrypt_ops` structure installed by `ceph_fscrypt_set_ops`. `ceph_fscrypt_free_dummy_policy` releases dummy-policy state.

Creation-time context flow is handled by `ceph_fscrypt_prepare_context` and `ceph_fscrypt_as_ctx_to_req`. Filename handling is implemented by `parse_longname`, `ceph_encode_encrypted_dname`, and `ceph_fname_to_usr`. Directory unlock handling is in `ceph_fscrypt_prepare_readdir`.

Data crypt helpers are `ceph_fscrypt_decrypt_block_inplace`, `ceph_fscrypt_encrypt_block_inplace`, `ceph_fscrypt_decrypt_pages`, `ceph_fscrypt_decrypt_extents`, and `ceph_fscrypt_encrypt_pages`.

## Control Flow

When fscrypt asks for an inode context, `ceph_crypt_get_context` validates `ci->fscrypt_auth`, checks the Ceph fscrypt auth version, verifies the output length, and copies the fscrypt blob. Setting a context builds a `ceph_fscrypt_auth` wrapper and sends it through `__ceph_setattr`; on success it marks the inode encrypted.

For a new inode, `ceph_fscrypt_prepare_context` calls `fscrypt_prepare_new_inode`. If encryption is required, it allocates `as->fscrypt_auth`, asks fscrypt for the new context blob, fills the Ceph auth wrapper, mirrors it into `ci->fscrypt_auth`, sets `ci->fscrypt_auth_len`, and marks the inode encrypted. `ceph_fscrypt_as_ctx_to_req` transfers that auth object into the MDS request by swapping pointers.

Filename encryption starts in `ceph_encode_encrypted_dname`. Snapshot names under the snapdir that begin with `_` are parsed by `parse_longname`, which extracts the original snapshot name and target inode number from `_<name>_<ino>`, finding or instantiating that inode so the correct directory key is used. If the directory key is available, fscrypt encrypts the cleartext name, long ciphertext tails are SHA-256 hashed after `CEPH_NOHASH_NAME_MAX`, and the result is base64 encoded with the IMAP alphabet. Snapshot longnames append the inode number again after encryption.

`ceph_fname_to_usr` performs the reverse presentation path for names received from the MDS. Non-encrypted directories pass through unchanged. Encrypted directories first call `ceph_fscrypt_prepare_readdir`; if no key is available, Ceph returns the raw MDS name rather than synthesizing a generic fscrypt nokey name. With a key, it uses either supplied ciphertext or base64-decodes the MDS name, calls `fscrypt_fname_disk_to_usr`, and reconstructs long snapshot names if needed.

For data I/O, block helpers wrap fscrypt in-place encrypt/decrypt with Ceph debug logging. `ceph_fscrypt_decrypt_pages` and `ceph_fscrypt_encrypt_pages` compute 4 KiB crypto-block counts from the file offset and length rounded down to complete blocks, then process each block at the right page index and page offset. `ceph_fscrypt_decrypt_extents` walks sparse OSD extents, validates encrypted extent offset/length alignment, maps object offsets back into the page array, and decrypts only non-hole extents.

## State and Persistence Behavior

Encryption context is stored in `ci->fscrypt_auth` and persisted to the MDS as `struct ceph_fscrypt_auth`. Encrypted cap messages also carry fscrypt auth and real encrypted-file size through `caps.c`. Filenames are persisted to the MDS as base64-encoded ciphertext, with long-name tail hashing and alternate-name support expected for full ciphertext preservation. Data sent to OSDs is encrypted in page/bounce buffers; decrypted data is placed back into page-cache pages for the VFS.

## Dependencies and Integration Points

The file depends on Linux fscrypt, base64, SHA-256, xattrs, Ceph setattr/MDS request code, Ceph inode lookup, and the striper for object mapping in sparse extent decryption. `addr.c` calls the data helpers for encrypted OSD reads/writes, and `caps.c` includes fscrypt auth and real file size in cap messages. Directory and dentry code uses filename helpers for lookup/readdir/release encoding.

## Risks and Edge Cases

Encrypted I/O must only process complete fscrypt blocks; partial tail handling is deliberately left to callers to zero or ignore. Sparse extents with unaligned encrypted offsets or lengths are rejected with `-EIO`. Long filename hashing must stay consistent with `crypto.h` limits or MDS-visible names can exceed `NAME_MAX`. Snapshot longname parsing is sensitive to underscore placement and inode lookup failures. In `ceph_fscrypt_prepare_context`, allocation of `ci->fscrypt_auth` after creating `as->fscrypt_auth` can fail and must be handled by caller cleanup.

## Test Signals

Test encrypted creates, context get/set, dummy encryption policy, readdir before and after key addition, long encrypted filenames, snapshot names in snapdir, lookup/release paths that re-encode names, sparse encrypted reads with holes, unaligned extent rejection, reads/writes across page and object boundaries, and no-key presentation. Signals include correct `S_ENCRYPTED` state, stable base64 names within Ceph limits, successful directory invalidation when a key becomes available, and clean fscrypt bounce-page handling in writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/crypto.h -->
# sources/distributed-fs/ceph-client/fs/ceph/crypto.h

## Purpose

`crypto.h` defines the CephFS fscrypt interface, wire/storage helper structures, constants for Ceph’s 4 KiB encryption block handling, encrypted filename buffers, and no-op fallbacks for builds without `CONFIG_FS_ENCRYPTION`.

## Important APIs and Types

`CEPH_FSCRYPT_BLOCK_SHIFT`, `CEPH_FSCRYPT_BLOCK_SIZE`, and `CEPH_FSCRYPT_BLOCK_MASK` define the crypto block size used by Ceph OSD I/O alignment. `struct ceph_fname` carries a directory inode, MDS/base64 name, optional raw ciphertext, lengths, and a no-copy marker. `struct ceph_fscrypt_truncate_size_header` describes encrypted truncate metadata sent to the MDS. `struct ceph_fscrypt_auth` wraps a versioned fscrypt context blob, and `ceph_fscrypt_auth_len` computes its serialized length.

When encryption is enabled, the header declares context, filename, readdir, and page crypt helpers implemented in `crypto.c`. It also defines `CEPH_NOHASH_NAME_MAX`, `ceph_fname_alloc_buffer`, `ceph_fname_free_buffer`, `ceph_fscrypt_blocks`, `ceph_fscrypt_adjust_off_and_len`, `ceph_fscrypt_pagecache_page`, and `ceph_fscrypt_page_offset`.

When encryption is disabled, static inline fallbacks reject encrypted parents with `-EOPNOTSUPP` where necessary, pass filenames through unchanged, leave offsets untouched, return success for crypt operations, and map page helpers to the original page.

## Control Flow

The compile-time branch keeps callsites simple. Enabled builds route operations to fscrypt-aware helpers. Disabled builds still allow unencrypted CephFS to compile and run, but attempts to create children under encrypted directories fail early from `ceph_fscrypt_prepare_context`.

The key runtime inline is `ceph_fscrypt_adjust_off_and_len`: encrypted reads expand the requested OSD range to full Ceph fscrypt blocks and align the offset downward. `ceph_fscrypt_blocks` computes how many encryption blocks overlap a byte range. `ceph_fscrypt_pagecache_page` and `ceph_fscrypt_page_offset` normalize fscrypt bounce pages back to their original page-cache page for accounting and writeback completion.

## State and Persistence Behavior

The header itself stores no state. It defines the serialized auth and truncate structures that are persisted through MDS requests/cap messages and the helpers that decide how much encrypted object data must be read or written. In disabled builds, no fscrypt state is persisted by these helpers.

## Dependencies and Integration Points

It depends on kernel fscrypt, base64, SHA-256, inode/page types, and Ceph forward declarations. `addr.c` uses the block alignment and page normalization helpers. `crypto.c` implements the declared operations. `caps.c` uses `struct ceph_fscrypt_auth` and `CEPH_FSCRYPT_BLOCK_SIZE` when encoding cap messages for encrypted inodes.

## Risks and Edge Cases

The block size must not exceed `PAGE_SIZE`, enforced by `BUILD_BUG_ON` in `ceph_fscrypt_blocks`. Enabled and disabled branches must keep matching signatures. Offset expansion changes OSD I/O lengths, so callers must later copy only the originally requested bytes and handle tails. Filename buffer allocation only occurs for encrypted parents, so callers must pair allocation/free with the same parent encryption state.

## Test Signals

Build coverage should include encryption enabled and disabled. Runtime tests should check encrypted read alignment, page/bounce-page offset accounting, fallback `-EOPNOTSUPP` for encrypted directories without fscrypt support, long filename allocation/free, and cap-message auth length calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/crypto.h -->
