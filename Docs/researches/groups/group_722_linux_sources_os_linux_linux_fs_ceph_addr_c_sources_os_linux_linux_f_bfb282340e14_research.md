# Group Research: group_722_linux_sources_os_linux_linux_fs_ceph_addr_c_sources_os_linux_linux_f_bfb282340e14

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/addr.c -->
# File Research: sources/os/linux/linux/fs/ceph/addr.c

## Purpose
Implements CephFS address-space, page-cache, netfs, writeback, mmap fault, inline-data, and OSD pool-permission behavior for regular file data. This is the core bridge between Linux VFS/mm folios, Ceph MDS capabilities/snapshots, and Ceph OSD object I/O.

## Main Responsibilities
- Provides `ceph_aops`, the Ceph address-space operations:
  - `read_folio = netfs_read_folio`
  - `readahead = netfs_readahead`
  - `writepages = ceph_writepages_start`
  - `write_begin = ceph_write_begin`
  - `write_end = ceph_write_end`
  - `dirty_folio = ceph_dirty_folio`
  - `invalidate_folio = ceph_invalidate_folio`
- Provides `ceph_netfs_ops` for netfs read integration and write-begin validation.
- Tracks dirty folio snap contexts through folio private data.
- Enforces Ceph snapshot writeback ordering.
- Submits asynchronous batched OSD writes and synchronous single-folio writes.
- Handles encrypted file block alignment, sparse reads, and fscrypt bounce pages.
- Handles inline data fetch and conversion to normal object-backed file data.
- Handles mmap faults and `page_mkwrite`.
- Caches OSD pool read/write permission probes.

## Key Data and Invariants
- Dirty folios store a `struct ceph_snap_context *` in `folio->private`.
- Dirty page accounting is split between:
  - `ci->i_wrbuffer_ref`
  - `ci->i_wrbuffer_ref_head`
  - per-`ceph_cap_snap->dirty_pages`
  - global `mdsc->dirty_folios`
- Writeback must submit dirty folios in snapshot order. `get_oldest_context()` determines the oldest writable snap context.
- A folio dirty in a newer snap context cannot be modified until the older context is written or known written.
- Encrypted reads/writes are rounded to `CEPH_FSCRYPT_BLOCK_SIZE`; page offsets are normalized through `ceph_fscrypt_page_offset()` and `ceph_fscrypt_pagecache_page()`.

## Read Path
- `ceph_netfs_expand_readahead()` adjusts netfs readahead to Ceph stripe-unit boundaries while respecting file readahead settings and `FMODE_RANDOM`.
- `ceph_init_request()` sets request flags, allocates Ceph netfs private state, and may acquire read/cache caps for readahead callers that do not already hold them.
- `ceph_netfs_prepare_read()` limits subrequest length to the current object mapping and mount `rsize`.
- `ceph_netfs_issue_read()`:
  - rejects shutdown inodes with `-EIO`;
  - uses MDS inline-data fetch when `ceph_has_inline_data(ci)`;
  - adjusts encrypted I/O to crypto block boundaries;
  - allocates OSD read or sparse-read requests;
  - uses page arrays for encrypted reads and iter data for unencrypted reads;
  - pins OSD stopping blockers until completion.
- `finish_netfs_read()`:
  - records metrics;
  - maps `-ENOENT` to a successful hole/tail clear;
  - marks blocklisted clients on `-EBLOCKLISTED`;
  - decodes sparse extents;
  - decrypts encrypted extents through `ceph_fscrypt_decrypt_extents()`;
  - sets netfs transferred/error fields and terminates the subrequest.

## Dirtying and Invalidation
- `ceph_dirty_folio()`:
  - refuses already dirty folios;
  - chooses pending cap-snap context or head snap context;
  - increments Ceph dirty/writebuffer counters;
  - holds an inode reference on transition from zero dirty buffers;
  - attaches snap context to the folio;
  - delegates final dirty marking to fscache/netfs.
- `ceph_invalidate_folio()` only adjusts Ceph dirty accounting for full-folio invalidation. Partial invalidation leaves dirty accounting intact.
- Full invalidation detaches the snap context and calls `ceph_put_wrbuffer_cap_refs()`.

## Writeback Path
- `ceph_writepages_start()` drives asynchronous writeback:
  - skips nonblocking writeback under congestion;
  - rejects forced unmount/shutdown;
  - initializes `ceph_writeback_ctl`;
  - pins OSD stopping blocker;
  - repeatedly selects oldest snap context and walks tagged folios;
  - tags pages for integrity writeback when required;
  - batches contiguous or multi-extent writes up to stripe/object and OSD op limits.
- `ceph_process_folio_batch()` filters candidate folios:
  - waits on existing writeback and fscache private state;
  - locks folios;
  - rejects wrong snap context, beyond-EOF folios, and strip-unit overrun;
  - clears dirty state for I/O;
  - allocates page arrays;
  - encrypts folios into bounce pages for encrypted files.
- `ceph_submit_write()` builds and starts OSD write requests:
  - may split into several OSD requests when op count is too large;
  - attaches pages to each extent op;
  - starts fscache write-through for each extent;
  - sets writeback state;
  - transfers page-array ownership to the OSD request.
- `writepages_finish()`:
  - maps OSD errors to mapping errors and Ceph write-error state;
  - releases bounce pages;
  - detaches snap contexts;
  - ends page writeback;
  - decrements dirty-folio and writeback congestion counters;
  - optionally removes pages when cache/lazy caps were lost;
  - releases writebuffer cap refs and OSD blocker.
- `write_folio_nounlock()` is the synchronous single-folio fallback used when a folio dirty in an older snap context must be written before modification.

## Write-Begin and Write-End
- `ceph_find_incompatible()` detects folios dirty under a conflicting snap context.
- `ceph_netfs_check_write_begin()` unlocks/drops incompatible folios, queues writeback, waits for the conflicting context to become writable or written, and returns `-EAGAIN`.
- `ceph_write_begin()` delegates to `netfs_write_begin()` and waits for fscache private state.
- `ceph_write_end()` marks uptodate, updates i_size, marks dirty, and calls `ceph_check_caps()` when size growth needs cap reporting.

## mmap Integration
- `ceph_filemap_fault()` obtains read/cache/lazy caps before `filemap_fault()`. If inline data is present and cache caps are unavailable, it fetches inline data into page 0.
- `ceph_page_mkwrite()` obtains write/buffer/lazy caps, updates file time and i_version, handles snapshot-context conflicts, marks the folio dirty, and marks `CEPH_CAP_FILE_WR` dirty metadata.

## Inline Data
- `ceph_fill_inline_data()` fills page-cache page 0 from MDS-provided inline bytes.
- `ceph_uninline_data()` converts inline file data to OSD object data:
  - obtains the current inline version;
  - gets a snap context;
  - reads page 0;
  - creates the first object;
  - writes page contents with xattr compare/set operations on `inline_version`;
  - marks inline metadata dirty as `CEPH_INLINE_NONE`.

## Pool Permission Cache
- `__ceph_pool_perm_get()` probes a data pool/namespace by issuing OSD `STAT` and `CREATE` requests against the first object name, then stores read/write permission bits in an rb-tree.
- `ceph_pool_perm_check()` skips non-regular files, snapshots, and `NOPOOLPERM`; otherwise caches permission flags in inode state and returns `-EPERM` when requested caps exceed pool rights.
- `ceph_pool_perm_destroy()` frees the MDS client permission tree.

## External Dependencies
- Linux mm/filemap/netfs/fscache APIs.
- Ceph MDS caps from `caps.c`.
- Ceph OSD client request construction and striper mapping.
- Ceph fscrypt helpers from `crypto.c`/`crypto.h`.
- Ceph metrics and subvolume metrics.

## Risk Notes
- Dirty folio private data and cap dirty counters must stay synchronized; missed detach/ref puts can leak snap contexts or inode refs.
- Snapshot writeback ordering is critical for correctness.
- Encrypted I/O relies on block-aligned OSD requests and correct bounce-page ownership.
- Forced unmount/shutdown paths deliberately convert pending dirty state to mapping errors.
- Pool permission probing writes/creates first-object metadata for head inodes, so snapshots are explicitly skipped.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/addr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/cache.c -->
# File Research: sources/os/linux/linux/fs/ceph/cache.c

## Purpose
Implements CephFS FS-Cache volume and inode cookie registration helpers when `CONFIG_CEPH_FSCACHE` is enabled.

## Main Responsibilities
- Registers per-inode cache cookies for regular, newly created inodes.
- Registers and unregisters a filesystem-level FS-Cache volume.
- Provides wrappers for cookie use/unuse, update, and invalidation.

## Key Functions
- `ceph_fscache_register_inode_cookie()`:
  - exits when filesystem caching is disabled;
  - only supports regular files;
  - only registers cookies while inode is `I_NEW`;
  - uses `ci->i_vino` as the key and `ci->i_version` as coherency data;
  - sets `mapping_set_release_always()` when a cookie is acquired.
- `ceph_fscache_unregister_inode_cookie()` relinquishes the inode cookie.
- `ceph_fscache_use_cookie()` and `ceph_fscache_unuse_cookie()` wrap fscache pin/unpin. The update path supplies current version and size.
- `ceph_fscache_update()` updates cookie coherency data.
- `ceph_fscache_invalidate()` invalidates the cookie, using `FSCACHE_INVAL_DIO_WRITE` for direct-I/O write invalidations.
- `ceph_fscache_register_fs()` creates a volume name from Ceph fsid and optional `fscache_uniq`, acquires the FS-Cache volume, and reports mount-context errors.
- `ceph_fscache_unregister_fs()` relinquishes the volume.

## Integration
- Used by `addr.c` for dirty folio handling, read/write cache interaction, writeback unpinning, and invalidation during cap revocation.
- Stores the cookie in the embedded `netfs_inode` inside `ceph_inode_info`.

## Risk Notes
- Inode cookies are intentionally only registered for `I_NEW` regular files; late registration is avoided.
- Coherency depends on correct updates of `ci->i_version` and file size.
- Failure to acquire a volume disables caching by clearing `fsc->fscache`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/cache.h -->
# File Research: sources/os/linux/linux/fs/ceph/cache.h

## Purpose
Declares Ceph FS-Cache helpers and provides no-op fallbacks when `CONFIG_CEPH_FSCACHE` is disabled.

## Main Interfaces
When FS-Cache is enabled:
- `ceph_fscache_register_fs()`
- `ceph_fscache_unregister_fs()`
- `ceph_fscache_register_inode_cookie()`
- `ceph_fscache_unregister_inode_cookie()`
- `ceph_fscache_use_cookie()`
- `ceph_fscache_unuse_cookie()`
- `ceph_fscache_update()`
- `ceph_fscache_invalidate()`
- `ceph_fscache_cookie()`
- `ceph_fscache_resize()`
- `ceph_fscache_unpin_writeback()`
- `ceph_is_cache_enabled()`

## Conditional Behavior
- With `CONFIG_CEPH_FSCACHE`, helpers call Linux fscache/netfs APIs and `ceph_fscache_dirty_folio` aliases to `netfs_dirty_folio`.
- Without `CONFIG_CEPH_FSCACHE`, all helpers are no-ops or return false/zero/null, and `ceph_fscache_dirty_folio` aliases to `filemap_dirty_folio`.

## Integration
- Included by Ceph address-space and cap code to keep cache-aware paths buildable with and without FS-Cache.
- Uses `netfs_i_cookie(&ci->netfs)` to access the cookie.

## Risk Notes
- The fallback macros change dirty-folio behavior, so call sites must not assume FS-Cache state exists.
- `ceph_fscache_resize()` temporarily uses the cookie with `will_modify=true`; incorrect use/unuse pairing would affect cache coherency.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/caps.c -->
# File Research: sources/os/linux/linux/fs/ceph/caps.c

## Purpose
Implements CephFS client capability management. Capabilities are MDS-issued permissions that allow cached inode metadata/data access, buffered writes to OSDs, directory caching, metadata mutation, and delayed release. This file owns the cap state machine for reservation, issuance, revocation, dirty metadata flushing, cap snapshots, MDS migration, cap refs, fsync/writeback synchronization, and release encoding.

## Main Responsibilities
- Maintains per-MDS-session and per-inode capability state.
- Allocates, reserves, reuses, and trims `struct ceph_cap` objects.
- Tracks issued, implemented, wanted, used, dirty, and flushing cap masks.
- Sends cap update/flush/release messages to MDS.
- Handles MDS cap messages: grant, revoke, import, export, trunc, flush ack, flushsnap ack.
- Coordinates dirty metadata flushing with inode writeback, fsync, snapshots, and MDS journal safety.
- Manages cap references for open files, buffered I/O, mmap, file locks, and cached pages.
- Encodes inode and dentry cap/lease releases into outgoing MDS requests.

## Core Concepts
- `issued`: caps the MDS currently wants the client to hold.
- `implemented`: caps the client still effectively holds, including caps being revoked but not yet returned due to active refs or dirty state.
- `wanted`: caps the client asks the MDS to keep/grant.
- `used`: caps with active local references, derived from ref counters and cache/writeback state.
- `dirty`: metadata caps that need to be flushed to the auth MDS.
- `flushing`: dirty metadata caps already sent but not acknowledged.
- `i_auth_cap`: the auth-MDS cap for the inode; only auth cap handles dirty metadata and max-size negotiation.
- `ceph_cap_snap`: snapshot-time metadata and dirty-page state that must be flushed in snap order.

## Cap Allocation and Reservation
- `ceph_caps_init()` / `ceph_caps_finalize()` initialize and drain the MDS client cap pool.
- `ceph_adjust_caps_max_min()` sets min/max cap cache sizing from mount options.
- `ceph_reserve_caps()` reserves cap objects before operations that may instantiate inodes/caps. It first consumes available caps, then allocates, then tries trimming session caps on allocation pressure.
- `ceph_unreserve_caps()` returns unused reservations and may trigger cap reclaim.
- `ceph_get_cap()` consumes a reservation or allocates/reuses a cap.
- `ceph_put_cap()` returns a cap to the pool or frees it once the pool exceeds the retained minimum.
- `ceph_reservation_status()` reports pool counters.

## Per-Inode Cap Storage
- Caps are stored in `ci->i_caps`, an rb-tree keyed by MDS id.
- `__get_cap_for_mds()` and `ceph_get_cap_for_mds()` look up caps.
- `__insert_cap_node()` inserts a new cap.
- Each cap is also linked into its session LRU list under `session->s_caps`.

## Cap Issuance and Wanted State
- `ceph_cap_string()` formats cap masks for diagnostics.
- `__cap_is_valid()` rejects stale caps based on session generation and TTL.
- `__ceph_caps_issued()` combines valid cap bits, includes snap caps, and excludes non-auth bits that the auth MDS is revoking.
- `__ceph_caps_issued_mask()` tests whether a mask is held, optionally touching cap LRU position.
- `__ceph_caps_file_wanted()` derives wanted caps from open modes and recent read/write activity.
- `__ceph_caps_used()` derives caps that must be retained because local refs/cache/writeback still exist.
- `__ceph_caps_wanted()` combines file-wanted and used caps, adding exclusives for dirty data or directory ops.
- `__ceph_caps_mds_wanted()` reports caps previously advertised to MDS.

## Adding and Removing Caps
- `ceph_add_cap()` creates or updates a cap from MDS grant/import data:
  - links it to inode and session;
  - updates snap realm;
  - updates auth cap selection;
  - records `issued`, `implemented`, seq/mseq, wanted, and generation;
  - queues delayed checks when issued caps exceed local wanted state.
- `__ceph_remove_cap()` removes a cap from inode/session structures, optionally queues release, updates auth cap, and drops snap realm when no real caps remain.
- `ceph_remove_cap()` wraps removal and warns if an auth cap with dirty state is removed unexpectedly.
- `__ceph_remove_caps()` removes all caps on inode teardown.

## Dirty Metadata and Cap Flush
- `__ceph_mark_dirty_caps()` marks metadata caps dirty, installs a preallocated cap-flush object, creates/holds head snap context if necessary, links the inode into the auth session dirty list, and returns VFS dirty flags.
- `__mark_caps_flushing()` moves dirty caps to flushing state, assigns a monotonically increasing flush tid, links into global and inode flush lists, and records oldest flush tid.
- `__prep_cap()` mutates cap state for an outgoing update/flush message and fills `cap_msg_args` with inode metadata, xattrs, time fields, size, max_size, fscrypt auth, dirty mask, wanted mask, and pending-capsnap flags.
- `encode_cap_msg()` marshals `CEPH_MSG_CLIENT_CAPS` version 12, including inline version, epoch barrier, oldest flush tid, btime/change_attr, advisory flags, dirstats placeholders, and fscrypt fields.
- `__send_cap()` allocates and sends the MDS caps message; on allocation failure it requeues delayed cap work.

## Snapshot Metadata Flushing
- `__ceph_flush_snaps()` walks `ci->i_cap_snaps` in order, waits until dirty pages and sync writes are complete, assigns flush tids, and sends `CEPH_CAP_OP_FLUSHSNAP`.
- `ceph_flush_snaps()` finds the auth session, kicks earlier flushing caps if needed, calls the internal flusher, and removes the inode from the snap flush queue.
- `ceph_try_drop_cap_snap()` removes capsnaps that have no associated snapshot flush work.
- `ceph_put_wrbuffer_cap_refs()` decrements dirty page refs for head or capsnap contexts, completes capsnaps when dirty pages reach zero, and triggers snap flushing or cap checking.

## Cap Checking State Machine
- `ceph_check_caps()` is the central reconciliation function:
  - computes file-wanted, used, issued, implemented, revoking, retain masks;
  - attempts nonblocking page-cache invalidation when cache/lazy caps are revoked and there is no dirty data;
  - decides whether to ack revocation, flush dirty metadata, request more max size, report size, update wanted caps, or release unneeded caps;
  - sends cap update/flush messages outside `i_ceph_lock`;
  - queues writeback for buffer-cap revocation blocked by dirty pages;
  - queues async invalidation when page-cache invalidation cannot complete inline.
- Delayed cap release uses:
  - `__cap_delay_requeue()`
  - `__cap_delay_requeue_front()`
  - `__cap_delay_cancel()`
  - `ceph_check_delayed_caps()`

## Getting and Releasing Cap References
- `try_get_cap_refs()` attempts to take references for needed/wanted caps:
  - handles file-lock error state;
  - resolves pending truncates;
  - validates max-size for writes;
  - waits for pending cap snaps before write refs;
  - avoids reordering buffered and synchronous writes by respecting revoking buffer caps;
  - handles readonly sessions, shutdown inodes, stale wanted state, and snap rwsem acquisition.
- `ceph_try_get_caps()` is a nonblocking read-cap helper.
- `__ceph_get_caps()` blocks until caps are available, handles signals, max-size requests, cap renewal, inline data fetch, and open-file generation checks.
- `ceph_get_caps()` is the file-based wrapper.
- `ceph_take_cap_refs()` increments per-inode cap ref counters and creates head snap context for writes.
- `ceph_put_cap_refs()` / `ceph_put_cap_refs_async()` drop refs synchronously or by queued work.
- `ceph_get_fmode()`, `ceph_put_fmode()`, and `__ceph_touch_fmode()` maintain open-mode counters and recent-use timestamps.

## fsync and write_inode
- `try_flush_caps()` sends dirty cap metadata immediately or marks the latest flushing tid for waiters.
- `caps_are_flushed()` tests whether flush list has advanced beyond a tid.
- `flush_mdlog_and_wait_inode_unsafe_requests()` asks relevant MDS sessions to flush their journals and waits for unsafe directory/inode operations to become safe.
- `ceph_fsync()` waits data writeback, flushes dirty non-file metadata caps, waits unsafe MDS requests, and checks writeback errors.
- `ceph_write_inode()` flushes or queues dirty caps depending on writeback mode and `for_sync`.

## MDS Message Handling
- `ceph_handle_caps()` decodes MDS cap messages, including optional versioned fields:
  - flock payload
  - import/export peer
  - inline data
  - OSD epoch barrier
  - pool namespace
  - btime/change_attr
  - advisory flags and dirstats
  - fscrypt auth/file-size fields
- It locates the inode, serializes on session mutex, and dispatches:
  - `CEPH_CAP_OP_GRANT` / `REVOKE` to `handle_cap_grant()`
  - `CEPH_CAP_OP_FLUSH_ACK` to `handle_cap_flush_ack()`
  - `CEPH_CAP_OP_FLUSHSNAP_ACK` to `handle_cap_flushsnap_ack()`
  - `CEPH_CAP_OP_TRUNC` to `handle_cap_trunc()`
  - `CEPH_CAP_OP_EXPORT` to `handle_cap_export()`
  - `CEPH_CAP_OP_IMPORT` to `handle_cap_import()` followed by grant handling
- If the inode/cap is missing, it may synthesize and flush a cap release so the MDS can make progress.

## Grant/Revoke/Import/Export Handling
- `handle_cap_grant()`:
  - applies inode metadata updates when shared caps permit;
  - updates xattrs, times, layout, dirstats, file size, max size, inline data, and fscrypt warnings;
  - invalidates page cache on cache-cap revoke when possible;
  - detects revoked buffer caps and queues writeback;
  - updates `issued` and `implemented`;
  - wakes cap waiters and queues truncation/invalidation/writeback as needed.
- `handle_cap_flush_ack()` removes acknowledged flush tids, clears flushing caps, releases inode refs, wakes inode/global waiters, and frees cap-flush objects.
- `handle_cap_flushsnap_ack()` removes acknowledged capsnaps and releases snap context/inode refs.
- `handle_cap_trunc()` applies MDS truncate state and queues vmtruncate when needed.
- `handle_cap_export()` migrates cap authority away from a session, creates target placeholders if needed, moves flushing list ownership, and removes old caps.
- `handle_cap_import()` installs imported auth caps, resolves peer exported caps, and returns the prior issued mask for grant handling.

## Release Encoding
- `ceph_drop_caps_for_unlink()` proactively drops link caps and queues dirty-cap flush work for soon-to-be-unlinked files.
- `ceph_encode_inode_release()` encodes cap release records into outgoing MDS requests, dropping only unused clean caps and respecting `unless` masks.
- `ceph_encode_dentry_release()` additionally drops dentry leases and encrypts dentry names when needed.
- `ceph_flush_dirty_caps()` and `ceph_flush_cap_releases()` iterate sessions to force dirty-cap or release flushing.

## Purge/Error Paths
- `ceph_purge_inode_cap()` removes a cap, and for auth caps:
  - invalidates page cache on shutdown with cached pages;
  - marks mapping error when dirty buffers remain;
  - drops dirty/flushing state;
  - marks file locks errored;
  - frees preallocated cap flushes;
  - removes capsnaps.
- `invalidate_aliases()` prunes/drops dentries when link count reaches zero.

## External Dependencies
- Ceph MDS session/client logic, snap realms, request queues, and reconnect behavior.
- Ceph OSD epoch barrier update.
- Linux VFS inode writeback, wait queues, file locks, dentries, and inode versioning.
- FS-Cache invalidation helpers.
- Ceph fscrypt auth fields and encrypted dentry encoding.

## Risk Notes
- This file is concurrency-heavy: correctness depends on lock ordering among `i_ceph_lock`, session mutexes, `snap_rwsem`, `cap_dirty_lock`, `cap_delay_lock`, and session cap locks.
- `issued` vs `implemented` distinction is essential for safe revocation under active refs.
- Dirty/flushing cap lists carry inode references; missing put paths can leak inodes, while premature puts can lose dirty metadata.
- Cap migration import/export sequence handling must preserve auth-cap and flushing ownership.
- fscrypt file sizes differ from rounded wire sizes, so grant/trunc/cap message encoding must use the right size field.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/caps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/ceph_frag.c -->
# File Research: sources/os/linux/linux/fs/ceph/ceph_frag.c

## Purpose
Provides comparison logic for Ceph fragment identifiers.

## Key Function
- `ceph_frag_compare(__u32 a, __u32 b)`:
  - compares `ceph_frag_value()` first;
  - if equal, compares `ceph_frag_bits()`;
  - returns `-1`, `1`, or `0`.

## Integration
- Used wherever Ceph fragment identifiers need deterministic ordering, likely directory fragment trees or maps.

## Risk Notes
- Ordering is lexicographic by fragment value, then fragment bit width. Any caller relying on a different hierarchy would get incorrect ordering, but the implementation is small and direct.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/ceph_frag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/crypto.c -->
# File Research: sources/os/linux/linux/fs/ceph/crypto.c

## Purpose
Implements CephFS integration with Linux fscrypt, including encryption context storage via MDS attributes, encrypted filename encoding/decoding, readdir preparation, and block/page encryption helpers for file data.

## Main Responsibilities
- Registers Ceph fscrypt operations.
- Gets/sets Ceph fscrypt auth context.
- Prepares fscrypt context for newly created encrypted inodes.
- Transfers fscrypt auth context into MDS requests.
- Encodes encrypted dentry names for MDS requests.
- Converts MDS filenames back to user-visible names.
- Handles special Ceph snapshot-name longname format.
- Encrypts/decrypts page arrays and sparse extents.

## fscrypt Operations
- `ceph_crypt_get_context()` validates `ci->fscrypt_auth`, checks Ceph fscrypt auth version, and copies the inner fscrypt blob.
- `ceph_crypt_set_context()` wraps a new fscrypt context in `ceph_fscrypt_auth` and sends it through `__ceph_setattr()`, then marks inode `S_ENCRYPTED`.
- `ceph_crypt_empty_dir()` treats a directory as empty when recursive subdir/file counts total one.
- `ceph_get_dummy_policy()` returns the mount dummy encryption policy.
- `ceph_fscrypt_set_ops()` installs `ceph_fscrypt_ops` on the superblock.
- `ceph_fscrypt_free_dummy_policy()` releases dummy policy state.

## New Inode Context
- `ceph_fscrypt_prepare_context()`:
  - calls `fscrypt_prepare_new_inode()`;
  - allocates a `ceph_fscrypt_auth`;
  - fills its fscrypt blob via `fscrypt_context_for_new_inode()`;
  - copies auth data into `ci->fscrypt_auth`;
  - marks the inode encrypted.
- `ceph_fscrypt_as_ctx_to_req()` moves auth context from ACL/security context into an MDS request.

## Filename Handling
- `parse_longname()` handles special snapshot names of form `_<SNAPSHOT-NAME>_<INODE-NUMBER>`, returning the inode for the embedded inode number and updating the clear snapshot-name length.
- `ceph_encode_encrypted_dname()`:
  - handles snapdir longnames;
  - exits unchanged when the relevant directory has no fscrypt key;
  - encrypts cleartext name with `fscrypt_fname_encrypt()`;
  - hashes ciphertext tail when longer than `CEPH_NOHASH_NAME_MAX`;
  - base64-encodes ciphertext with `BASE64_IMAP`;
  - appends `_<inode>` for parsed long snapshot names.
- `ceph_fname_to_usr()`:
  - handles long snapshot names;
  - passes through unencrypted names;
  - calls `ceph_fscrypt_prepare_readdir()` for encrypted dirs;
  - returns raw MDS name when the key is unavailable;
  - base64-decodes MDS names unless binary ciphertext is supplied;
  - calls `fscrypt_fname_disk_to_usr()`;
  - reconstructs long snapshot display names when needed.
- `ceph_fscrypt_prepare_readdir()` wraps `__fscrypt_prepare_readdir()` and clears directory-complete cache state when a key becomes newly available.

## File Data Crypto
- `ceph_fscrypt_decrypt_block_inplace()` and `ceph_fscrypt_encrypt_block_inplace()` are tracing wrappers over fscrypt block helpers.
- `ceph_fscrypt_decrypt_pages()` decrypts complete `CEPH_FSCRYPT_BLOCK_SIZE` blocks across a page array and ignores incomplete trailing blocks.
- `ceph_fscrypt_decrypt_extents()` decrypts sparse read extents, verifying each sparse extent is crypto-block aligned.
- `ceph_fscrypt_encrypt_pages()` encrypts complete blocks across a page array.

## Integration
- `addr.c` uses these helpers for encrypted netfs reads, sparse reads, writeback bounce-page handling, and encrypted page offsets.
- `caps.c` encodes/decodes fscrypt auth and true encrypted file size in cap messages.
- MDS request paths use encrypted dentry-name encoding.

## Risk Notes
- Long encrypted names are truncated by hashing ciphertext tail; full encrypted names must be preserved elsewhere when needed.
- Snapshot longname parsing depends on underscore delimiters and decimal inode suffixes.
- For encrypted files, wire I/O must be crypto-block aligned; sparse extent misalignment is treated as `-EIO`.
- `ceph_fscrypt_prepare_context()` allocates auth state before `fscrypt_context_for_new_inode()`; error callers must handle cleanup of `as->fscrypt_auth`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/crypto.h -->
# File Research: sources/os/linux/linux/fs/ceph/crypto.h

## Purpose
Declares CephFS fscrypt types, constants, and helpers, with full implementations when `CONFIG_FS_ENCRYPTION` is enabled and no-op/pass-through fallbacks otherwise.

## Key Types and Constants
- `CEPH_FSCRYPT_BLOCK_SHIFT = 12`
- `CEPH_FSCRYPT_BLOCK_SIZE = 4096`
- `CEPH_FSCRYPT_BLOCK_MASK`
- `struct ceph_fname`: carries MDS filename data, optional binary ciphertext, parent dir, lengths, and no-copy flag.
- `struct ceph_fscrypt_truncate_size_header`: metadata sent to MDS for encrypted truncate handling.
- `struct ceph_fscrypt_auth`: Ceph wrapper around fscrypt context blob.
- `CEPH_FSCRYPT_AUTH_VERSION = 1`
- `CEPH_NOHASH_NAME_MAX`: maximum ciphertext prefix kept before hashing long encrypted names.

## Main Interfaces With Encryption Enabled
- fscrypt setup:
  - `ceph_fscrypt_set_ops()`
  - `ceph_fscrypt_free_dummy_policy()`
  - `ceph_fscrypt_prepare_context()`
  - `ceph_fscrypt_as_ctx_to_req()`
- name handling:
  - `ceph_encode_encrypted_dname()`
  - `ceph_fname_alloc_buffer()`
  - `ceph_fname_free_buffer()`
  - `ceph_fname_to_usr()`
  - `ceph_fscrypt_prepare_readdir()`
- I/O alignment and crypto:
  - `ceph_fscrypt_blocks()`
  - `ceph_fscrypt_adjust_off_and_len()`
  - `ceph_fscrypt_decrypt_block_inplace()`
  - `ceph_fscrypt_encrypt_block_inplace()`
  - `ceph_fscrypt_decrypt_pages()`
  - `ceph_fscrypt_decrypt_extents()`
  - `ceph_fscrypt_encrypt_pages()`
  - `ceph_fscrypt_pagecache_page()`
  - `ceph_fscrypt_page_offset()`

## Fallback Behavior Without Encryption
- `ceph_fscrypt_prepare_context()` rejects encrypted parent dirs with `-EOPNOTSUPP`.
- Name conversion passes MDS names through unchanged.
- offset/length adjustment is a no-op.
- encrypt/decrypt helpers return success without transformation.
- `ceph_fscrypt_pagecache_page()` returns the original page.

## Important Inline Logic
- `ceph_fscrypt_auth_len()` returns wrapper header plus fscrypt blob length.
- `ceph_fscrypt_blocks()` computes the number of 4 KiB crypto blocks touched by an offset/length pair and asserts crypto blocks do not exceed page size.
- `ceph_fscrypt_adjust_off_and_len()` rounds encrypted reads down/up to full crypto blocks.
- `ceph_fscrypt_page_offset()` always resolves bounce pages back to their page-cache page before computing offset.

## Integration
- Used by address-space read/write code for block alignment and bounce-page handling.
- Used by cap message encoding/decoding for fscrypt auth and true file size.
- Used by dentry release and MDS request paths for encrypted names.

## Risk Notes
- The enabled and disabled configurations intentionally expose identical call sites but very different semantics.
- Correctness for encrypted I/O depends on all callers using adjusted offsets/lengths before OSD I/O.
- `ceph_fscrypt_page_offset()` is important for writeback code that may see fscrypt bounce pages.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/crypto.h -->