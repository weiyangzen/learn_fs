# Group Research: group_964_linux_stable_sources_os_linux_linux_stable_fs_ceph_addr_c_sources_os_dfdf86bee415

Scope: `Docs/research_subset_a.md` only. This grouped report covers the listed CephFS Linux stable client files under `sources/os/linux/linux-stable/fs/ceph/`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/addr.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/addr.c

## Purpose

`addr.c` implements CephFS address-space operations: buffered reads through netfs, buffered and mmap writes, writeback to OSDs, inline-data handling, FS-Cache write-through hooks, and per-pool read/write permission probing. It is the bridge between Linux page-cache/netfs folios and Ceph OSD object I/O.

## Main Responsibilities

- Defines `ceph_aops`, including `netfs_read_folio`, `netfs_readahead`, `ceph_writepages_start`, `ceph_write_begin`, `ceph_write_end`, `ceph_dirty_folio`, and invalidate/release/migrate handlers.
- Tracks dirty folios by attaching a `ceph_snap_context` to folio private data.
- Preserves Ceph snapshot ordering: writeback must flush dirty folios in ascending snap context order before newer head data.
- Issues OSD reads and writes, including sparse reads for encrypted files or `SPARSEREAD`.
- Integrates with `netfs_request_ops` via `ceph_netfs_ops`.
- Handles inline data reads and uninlining file data into OSD objects.
- Provides Ceph-specific mmap fault and page-mkwrite behavior.
- Caches and validates pool read/write permissions using OSD stat/create probes.

## Key Data Flow

Reads:
- `ceph_init_request()` prepares readahead state and acquires cache/read caps when needed.
- `ceph_netfs_prepare_read()` limits each subrequest to object and mount `rsize` boundaries.
- `ceph_netfs_issue_read()` chooses inline data, normal OSD read, or sparse OSD read.
- `finish_netfs_read()` updates metrics, handles `-ENOENT` as zero-fill, decrypts sparse encrypted extents, releases OSD data pages, and terminates the netfs subrequest.

Writes:
- `ceph_write_begin()` delegates preparation to netfs and then waits for deprecated private-2 cache write state.
- `ceph_write_end()` updates inode size, marks the folio dirty, and triggers cap checks if size changed.
- `ceph_dirty_folio()` increments global and inode dirty counters and attaches the current head or pending capsnap snap context.
- `ceph_writepages_start()` selects the oldest writable snap context, batches dirty folios, builds OSD write requests, and submits async writeback.
- `writepages_finish()` cleans folios, detaches snap contexts, updates dirty accounting, handles errors/blocklisting, and releases writeback refs.

## Snapshot and Dirty Accounting

The file’s central invariant is that dirty data is associated with exactly one snap context:
- Head writes increment `ci->i_wrbuffer_ref_head`.
- Writes racing snapshot creation can be charged to the newest pending `ceph_cap_snap`.
- `get_oldest_context()` finds the only snap context eligible for writeback.
- `ceph_find_incompatible()` prevents dirtying a folio under a newer context while it still contains dirty data for an older context.
- `ceph_put_wrbuffer_cap_refs()` in `caps.c` is called after writeback or invalidation to decrement per-head or per-capsnap counters.

This is why full-folio invalidation detaches private snap context and adjusts wrbuffer refs, while partial invalidation refuses to modify dirty accounting.

## Writeback Mechanics

Writeback uses `struct ceph_writeback_ctl` to carry selected snap context, file size/truncation metadata, range scan state, batching state, page arrays, and OSD op layout.

Important behavior:
- `ceph_define_writeback_range()` ignores caller writeback ranges for non-head snap contexts because older snapshot data must flush first.
- `ceph_process_folio_batch()` filters folios by mapping, dirty state, snap context, EOF, strip-unit boundaries, and writeback/private-2 state.
- `ceph_submit_write()` converts batches into one or more OSD write ops, splitting discontiguous page ranges into multiple extents.
- Encrypted writes use fscrypt bounce pages and round lengths to `CEPH_FSCRYPT_BLOCK_SIZE`.
- Writeback congestion is tracked with `fsc->writeback_count` and mount `congestion_kb` thresholds.

## Inline Data

Inline data is handled separately from normal object data:
- Reads can fetch inline data via an MDS `GETATTR` request in `ceph_netfs_issue_op_inline()`.
- `ceph_fill_inline_data()` installs inline bytes into page cache.
- `ceph_uninline_data()` creates object data, writes page-cache content into OSD object 0, guards with the `inline_version` xattr, and marks caps dirty after switching to `CEPH_INLINE_NONE`.

## mmap Behavior

- `ceph_filemap_fault()` acquires cache/lazy caps before calling `filemap_fault()`, or manually loads inline data for inline files.
- `ceph_page_mkwrite()` acquires buffer/write caps, updates times and i_version, resolves incompatible snap contexts, marks the folio dirty, and marks write caps dirty.

Signals are blocked except `SIGKILL` during cap acquisition around faults.

## FS-Cache Integration

When `CONFIG_CEPH_FSCACHE` is enabled:
- Dirty folios call `ceph_fscache_dirty_folio()`.
- Writeback marks pages with private-2 and calls `fscache_write_to_cache()`.
- Failed cache writes invalidate the cache except `-ENOBUFS`.

Without FS-Cache, these helpers compile to no-ops or normal `filemap_dirty_folio`.

## Pool Permission Checks

`ceph_pool_perm_check()` lazily validates read/write permission for regular file data pools:
- Skips snapshots and `NOPOOLPERM`.
- Uses an rb-tree cache keyed by pool id and namespace.
- Probes read with OSD `STAT` and write with exclusive `CREATE`.
- Caches `POOL_READ` and `POOL_WRITE` bits into inode flags if layout is unchanged.

## Important Dependencies

- `caps.c`: cap acquisition/release, dirty cap marking, wrbuffer ref release, writeback queueing.
- `cache.c`/`cache.h`: FS-Cache cookie helpers.
- `crypto.c`/`crypto.h`: encrypted read/write alignment, bounce pages, extent decryption.
- OSD client APIs: `ceph_osdc_new_request()`, `ceph_osdc_start_request()`, OSD op data setup.
- netfs library: request ops, folio read/readahead/write-begin support.

## Edge Cases and Risks

- Dirty folio accounting depends on every private snap context being detached exactly once.
- Non-head snapshot writeback intentionally ignores requested ranges; callers expecting strict range-limited writeback must account for Ceph snapshot ordering.
- Encrypted reads currently use page arrays rather than iter data because decryption infrastructure is page-based here.
- `ceph_netfs_issue_read()` mutates `subreq->io_iter.count` for encrypted reads to satisfy sparse message constraints.
- Forced unmount/shutdown converts operations to `-EIO`/`-ESTALE` and may invalidate or redirty pages.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/addr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/cache.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/cache.c

## Purpose

`cache.c` implements CephFS FS-Cache volume and inode-cookie lifecycle helpers. It is compiled when `CONFIG_CEPH_FSCACHE` is enabled and backs the declarations in `cache.h`.

## Main Responsibilities

- Registers an FS-Cache volume for a mounted Ceph filesystem.
- Registers per-inode cookies for new regular-file inodes.
- Updates, invalidates, uses, unuses, and relinquishes FS-Cache cookies.

## Key Functions

- `ceph_fscache_register_fs()` builds a volume name from Ceph FSID and optional `fscache_uniq`, then calls `fscache_acquire_volume()`.
- `ceph_fscache_unregister_fs()` relinquishes the volume.
- `ceph_fscache_register_inode_cookie()` acquires a cookie for new regular files only, using `i_vino` as key and `i_version` plus file size as coherency data.
- `ceph_fscache_unregister_inode_cookie()` relinquishes an inode cookie.
- `ceph_fscache_use_cookie()` and `ceph_fscache_unuse_cookie()` bracket cache usage, optionally updating coherency metadata.
- `ceph_fscache_update()` updates cookie coherency from inode version and size.
- `ceph_fscache_invalidate()` invalidates cached contents, marking direct-I/O write invalidations when applicable.

## Important Conditions

- No inode cookie is registered if the mount has no FS-Cache volume.
- Only regular files are cacheable.
- Only `I_NEW` inodes get cookies here.
- A successfully cached inode mapping is marked `mapping_set_release_always()` so release callbacks happen consistently.

## Dependencies

- `super.h` for Ceph inode/client accessors.
- Linux FS-Cache APIs.
- `cache.h` for exported declarations and inline wrappers.
- Used by `addr.c` writeback and invalidation paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/cache.h -->
# File Research: sources/os/linux/linux-stable/fs/ceph/cache.h

## Purpose

`cache.h` provides the CephFS FS-Cache interface, with real declarations and inline helpers when `CONFIG_CEPH_FSCACHE` is enabled and no-op fallbacks otherwise.

## Main Responsibilities

- Exposes mount-level and inode-level FS-Cache lifecycle functions.
- Provides `ceph_fscache_cookie()` accessor over `netfs_i_cookie()`.
- Provides cache resize, writeback unpin, dirty-folio, and cache-enabled helpers.
- Keeps the rest of CephFS code buildable without FS-Cache support.

## Enabled Build Behavior

When `CONFIG_CEPH_FSCACHE` is set:
- Real functions from `cache.c` are declared.
- `ceph_fscache_resize()` wraps `fscache_resize_cookie()` with use/unuse.
- `ceph_fscache_unpin_writeback()` delegates to `netfs_unpin_writeback()`.
- `ceph_fscache_dirty_folio` maps to `netfs_dirty_folio`.
- `ceph_is_cache_enabled()` checks `fscache_cookie_enabled()`.

## Disabled Build Behavior

When FS-Cache is disabled:
- Register/unregister/use/update/invalidate functions are inline no-ops.
- `ceph_fscache_cookie()` returns `NULL`.
- `ceph_fscache_unpin_writeback()` returns success.
- `ceph_fscache_dirty_folio` maps to `filemap_dirty_folio`.
- `ceph_is_cache_enabled()` returns false.

## Dependencies

- Linux netfs support.
- Linux FS-Cache support when enabled.
- Ceph inode structures through `struct ceph_inode_info`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/caps.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/caps.c

## Purpose

`caps.c` implements CephFS client capability management. Capabilities are MDS-issued permissions that authorize cached inode metadata, cached file data, writes to OSDs, directory operations, and dirty metadata updates. This file owns cap allocation, acquisition, release, revocation, dirty flushing, snap flushing, MDS cap message handling, reconnect/import/export handling, and open-mode wanted-cap tracking.

## Main Responsibilities

- Maintain per-MDS-session `ceph_cap` objects and per-inode cap rb-trees.
- Decide which caps are issued, implemented, wanted, used, dirty, flushing, or revoking.
- Acquire cap references for reads, writes, cache use, lazy I/O, mmap, and sync operations.
- Flush dirty inode metadata and capsnaps to the MDS.
- Respond to MDS `GRANT`, `REVOKE`, `TRUNC`, `EXPORT`, `IMPORT`, `FLUSH_ACK`, and `FLUSHSNAP_ACK` messages.
- Queue delayed cap release and cap dirty work.
- Encode cap and dentry releases into outgoing MDS requests.
- Handle cap purging during shutdown/session loss.

## Capability State Model

Important state categories:
- `issued`: caps currently granted by the MDS.
- `implemented`: caps the client still effectively holds, including revoking caps not yet acknowledged.
- `wanted`: caps the client asks the MDS to keep or grant.
- `used`: caps pinned by active refs such as read, write, cache, buffer, pin, or exclusive refs.
- `dirty`: metadata cap bits modified locally and not yet flushed.
- `flushing`: dirty cap bits sent to MDS but not yet acknowledged.

`ceph_cap_string()` formats these bitsets for debug logs.

## Allocation and Reservation

- `ceph_caps_init()` and `ceph_caps_finalize()` manage the global cap free list.
- `ceph_reserve_caps()`, `ceph_unreserve_caps()`, `ceph_get_cap()`, and `ceph_put_cap()` maintain total, used, reserved, and available cap counters.
- Reservation can trigger `ceph_trim_caps()` on sessions before failing allocation.
- The code keeps a minimum cap pool to reduce allocation churn.

## Per-Inode Cap Management

- `__get_cap_for_mds()` looks up a cap by MDS id in the inode rb-tree.
- `ceph_add_cap()` creates or updates a cap, links it into the session list, updates auth cap state, snap realm, wanted bits, and issue sequences.
- `__ceph_remove_cap()` removes a cap from inode/session structures and optionally queues a release to the MDS.
- `change_auth_cap_ses()` moves dirty/flushing inode list entries when the auth MDS changes.

## Cap Wanted and Used Logic

- `__ceph_caps_used()` derives cap bits from active reference counters and page-cache state.
- `__ceph_caps_file_wanted()` derives wanted caps from open file modes and recent read/write access.
- `__ceph_caps_wanted()` combines open-mode wanted caps with used caps, adding exclusive caps when needed.
- `__ceph_caps_mds_wanted()` reports what has already been requested from MDS sessions.

Open-mode counters are maintained by `ceph_get_fmode()`, `ceph_put_fmode()`, and `__ceph_touch_fmode()`.

## Cap Acquisition

The core acquisition path is:
- `ceph_try_get_caps()` for nonblocking read/cache cap attempts.
- `ceph_get_caps()` and `__ceph_get_caps()` for blocking acquisition by file operations.
- `try_get_cap_refs()` checks issued caps, revoking caps, max-size limits, pending capsnaps, file-lock errors, readonly sessions, shutdown state, and wanted-cap consistency.
- `check_max_size()` requests larger write max-size from the MDS when writes exceed current authorization.

Special return conditions:
- `-EAGAIN`: nonblocking path would need to sleep.
- `-EFBIG`: write exceeds current max size and should request expansion.
- `-EUCLEAN`: caps may need renewal after session disruption.

## Dirty Metadata and Flushes

- `__ceph_mark_dirty_caps()` marks inode metadata caps dirty, allocates/prepares a cap flush object, queues inode on session dirty list, and marks the VFS inode dirty as needed.
- `try_flush_caps()` sends immediate dirty cap flushes and returns flush tid.
- `ceph_write_inode()` flushes dirty caps for writeback or queues immediate cap work.
- `ceph_fsync()` waits for file data, dirty metadata cap flushes, and unsafe MDS operations when required.

Flush ordering is tracked with monotonic `last_cap_flush_tid`, global `cap_flush_list`, and per-inode `i_cap_flush_list`.

## Snapshot Cap Handling

Snapshot metadata is represented by `ceph_cap_snap`:
- `__ceph_flush_snaps()` sends eligible capsnap flushes in order after dirty pages and sync writes finish.
- `ceph_flush_snaps()` resolves the auth session and removes the inode from the snap flush queue.
- `ceph_try_drop_cap_snap()` discards capsnaps that do not need MDS flushes.
- `ceph_put_wrbuffer_cap_refs()` decrements dirty page refs for either head snap context or matching capsnap context and triggers snap flush when complete.
- `handle_cap_flushsnap_ack()` removes acknowledged capsnaps.

This cooperates directly with `addr.c` writeback snap-context ordering.

## Cap Reconciliation

`ceph_check_caps()` is the central reconciliation loop. It:
- Computes file-wanted, used, dirty, flushing, issued, implemented, revoking, want, and retain sets.
- Tries nonblocking page-cache invalidation when cache/lazy caps are revoked and no dirty buffers remain.
- Sends cap updates, flushes, revocation acknowledgments, wanted-cap changes, and max-size updates.
- Queues writeback when FILE_BUFFER revocation is blocked by dirty pages.
- Queues async invalidation when immediate invalidation fails.
- Handles pending cap flush and capsnap flush ordering before normal cap messages.

## MDS Message Encoding

- `cap_msg_args` is the in-memory form for outgoing cap messages.
- `encode_cap_msg()` serializes cap update/flush/flushsnap messages, including timestamps, ownership, mode, xattrs, inline-data marker, epoch barrier, oldest flush tid, btime, change attr, advisory flags, dirstats placeholders, and fscrypt fields.
- `__send_cap()` allocates and sends `CEPH_MSG_CLIENT_CAPS`.
- `__send_flush_snap()` sends `CEPH_CAP_OP_FLUSHSNAP`.

## Incoming MDS Cap Messages

`ceph_handle_caps()` decodes `CEPH_MSG_CLIENT_CAPS`, parses versioned payload fields, locates the inode, and dispatches by op:
- `handle_cap_grant()` handles grants and revocations, updates metadata fields, layout, xattrs, dirstats, inline data, max size, truncation state, and queues writeback/invalidation when needed.
- `handle_cap_flush_ack()` clears acknowledged flushing caps and releases flush records.
- `handle_cap_flushsnap_ack()` removes flushed capsnaps.
- `handle_cap_trunc()` applies MDS truncation state.
- `handle_cap_export()` and `handle_cap_import()` migrate caps between MDS sessions.

If the client lacks the inode or cap for a grant/revoke/import, it queues an explicit cap release back to the MDS.

## Reconnect, Session Loss, and Purge Behavior

- `ceph_early_kick_flushing_caps()`, `ceph_kick_flushing_caps()`, and `ceph_kick_flushing_inode_caps()` resend or mark flushing cap messages after revocation/reconnect conditions.
- `ceph_purge_inode_cap()` removes caps during shutdown/session loss, drops dirty/flushing state with mapping errors, marks file locks erroneous, removes capsnaps, and requests page invalidation when needed.
- `remove_capsnaps()` removes all capsnaps and wakes inode/global flush waiters.

## Release Encoding

- `ceph_encode_inode_release()` encodes inode cap release records into outgoing MDS request buffers, dropping only unused clean caps.
- `ceph_encode_dentry_release()` additionally encodes dentry lease release information and encrypts dentry names when needed.
- `ceph_drop_caps_for_unlink()` aggressively drops link caps and queues dirty cap flushes for soon-unlinked files.

## Important Dependencies

- `addr.c`: dirty page writeback, wrbuffer ref release, page-cache invalidation/writeback queues.
- `crypto.c`/`crypto.h`: fscrypt auth fields, encrypted names in dentry release, encrypted file size handling.
- MDS client/session structures and message transport.
- Linux inode writeback, fscrypt, file locking, wait queues, rb-trees, and list APIs.

## Edge Cases and Risks

- The file is concurrency-heavy: most inode cap state is protected by `i_ceph_lock`, while session lists use `s_cap_lock`, dirty/flush lists use `cap_dirty_lock`, and snap state uses `snap_rwsem`.
- Cap revocation cannot be acknowledged until conflicting active refs or dirty page writeback complete.
- Dirty cap flush ordering is maintained by flush tids; wake propagation moves wait responsibility to preceding flush records when removing later records.
- Auth MDS migration requires careful sequence/migrate-sequence checks to avoid dropping valid caps.
- Encrypted files report rounded traditional size in cap messages while carrying real size in fscrypt-specific fields.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/caps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/ceph_frag.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/ceph_frag.c

## Purpose

`ceph_frag.c` implements comparison for Ceph fragment identifiers.

## Main Function

`ceph_frag_compare(__u32 a, __u32 b)`:
- Extracts fragment value with `ceph_frag_value()`.
- Compares fragment values first.
- If values match, compares fragment bit counts with `ceph_frag_bits()`.
- Returns `-1`, `1`, or `0` for ordered comparison.

## Dependencies

- `linux/ceph/types.h` for Ceph fragment encoding helpers.
- Used anywhere Ceph fragment ids need stable ordering, commonly directory-fragment maps or ordered containers.

## Notes

The comparator orders by fragment value before precision/bit count, making it a small utility for deterministic fragment sorting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/ceph_frag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/crypto.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/crypto.c

## Purpose

`crypto.c` integrates CephFS with Linux fscrypt. It handles encryption context get/set, new-inode context preparation, encrypted filename conversion, snapshot-name special cases, readdir preparation, and page/block encryption/decryption helpers used by Ceph OSD I/O.

## fscrypt Operations

- `ceph_crypt_get_context()` reads the fscrypt auth blob from `ci->fscrypt_auth`, validates Ceph auth version, and copies the fscrypt context.
- `ceph_crypt_set_context()` wraps the fscrypt context in `ceph_fscrypt_auth` and persists it through `__ceph_setattr()`.
- `ceph_crypt_empty_dir()` treats a directory as empty when recursive subdirs plus files count is one.
- `ceph_get_dummy_policy()` returns the mount dummy encryption policy.
- `ceph_fscrypt_set_ops()` installs Ceph’s `fscrypt_operations` on the superblock.

## New Inode Encryption Context

`ceph_fscrypt_prepare_context()`:
- Calls `fscrypt_prepare_new_inode()`.
- Allocates and fills `ceph_fscrypt_auth` for encrypted new inodes.
- Stores a copy in `ci->fscrypt_auth`.
- Sets `S_ENCRYPTED` on the inode.

`ceph_fscrypt_as_ctx_to_req()` transfers prepared auth context into an MDS request.

## Encrypted Name Encoding

`ceph_encode_encrypted_dname()`:
- Handles special snapshot names beginning with `_`.
- Encrypts cleartext names with fscrypt when a key is available.
- Caps long ciphertext names by hashing the tail after `CEPH_NOHASH_NAME_MAX`.
- Base64-encodes ciphertext using `BASE64_IMAP`.
- Preserves special snapshot format by appending `_<inode-number>` when needed.

Special helper:
- `parse_longname()` parses synthetic snapshot names of the form `_<SNAPSHOT-NAME>_<INODE-NUMBER>` and resolves the referenced inode.

## User-Facing Name Decoding

`ceph_fname_to_usr()`:
- Validates name sizes.
- Handles special snapshot longnames.
- Returns raw names for unencrypted directories.
- Prepares encrypted readdir state.
- If no encryption key is available, returns the raw MDS-provided name and can mark `is_nokey`.
- Otherwise base64-decodes or uses supplied ciphertext, then calls `fscrypt_fname_disk_to_usr()`.
- Rebuilds special snapshot longname format after decryption when applicable.

## Readdir Preparation

`ceph_fscrypt_prepare_readdir()` wraps `__fscrypt_prepare_readdir()`:
- Returns 0 if directory is unencrypted or still locked.
- If loading a key unlocks the directory, it clears Ceph’s complete-directory cache state and returns 1.
- Returns negative errno on fscrypt errors.

## Block and Page Crypto

- `ceph_fscrypt_decrypt_block_inplace()` and `ceph_fscrypt_encrypt_block_inplace()` log and delegate to fscrypt block helpers.
- `ceph_fscrypt_decrypt_pages()` decrypts complete `CEPH_FSCRYPT_BLOCK_SIZE` blocks across a page array.
- `ceph_fscrypt_decrypt_extents()` decrypts sparse extents received from OSD reads, skipping holes and validating encryption-block alignment.
- `ceph_fscrypt_encrypt_pages()` encrypts complete crypto blocks across a page array.

All page-array helpers ignore partial trailing blocks by masking length to `CEPH_FSCRYPT_BLOCK_MASK`.

## Important Dependencies

- `crypto.h` for constants, structures, declarations, and inline helpers.
- `addr.c` for encrypted OSD read/write alignment, sparse extent decryption, and fscrypt bounce-page handling.
- `caps.c` for fscrypt auth encoding in cap messages and encrypted dentry release names.
- Linux fscrypt, base64, SHA-256, and Ceph striper/object mapping helpers.

## Edge Cases and Risks

- Snapshot longname parsing depends on the final underscore separating snapshot name and inode number.
- Very long encrypted filenames are lossy in the visible MDS name because the tail is SHA-256-hashed; full encrypted name preservation is handled elsewhere through dentry alternate names.
- Encrypted sparse extents must be block-aligned; misaligned extents return `-EIO`.
- Without a loaded key, user-facing conversion intentionally returns raw encoded MDS names rather than fscrypt nokey names.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/crypto.h -->
# File Research: sources/os/linux/linux-stable/fs/ceph/crypto.h

## Purpose

`crypto.h` declares CephFS fscrypt structures, constants, helpers, and disabled-build stubs. It is the shared interface between CephFS metadata/cap code, directory code, and address-space I/O for encrypted files.

## Main Definitions

- `CEPH_FSCRYPT_BLOCK_SHIFT`: 12.
- `CEPH_FSCRYPT_BLOCK_SIZE`: 4096-byte encryption block.
- `CEPH_FSCRYPT_BLOCK_MASK`: alignment mask for encryption-block boundaries.
- `struct ceph_fname`: MDS/raw/encrypted filename wrapper for user conversion.
- `struct ceph_fscrypt_truncate_size_header`: payload used when truncating encrypted files, including change attr, file offset, and block size.
- `struct ceph_fscrypt_auth`: Ceph wrapper around fscrypt context blob.
- `CEPH_FSCRYPT_AUTH_VERSION`: current auth wrapper version.
- `ceph_fscrypt_auth_len()`: computes encoded auth length.

## Enabled Build API

When `CONFIG_FS_ENCRYPTION` is enabled, the header declares:
- Superblock ops setup and dummy policy cleanup.
- New-inode context preparation and request transfer.
- Encrypted dentry-name encoding.
- Filename buffer allocation/free helpers.
- MDS-to-user filename conversion.
- Readdir preparation.
- Encryption-block counting and read alignment helpers.
- In-place block encrypt/decrypt wrappers.
- Page-array encrypt/decrypt helpers.
- Sparse extent decryption.
- Bounce-page to page-cache-page conversion.

Important inline helpers:
- `ceph_fscrypt_blocks(off, len)` counts 4096-byte crypto blocks covered by a range.
- `ceph_fscrypt_adjust_off_and_len()` expands encrypted reads to full crypto-block boundaries.
- `ceph_fscrypt_pagecache_page()` unwraps fscrypt bounce pages.
- `ceph_fscrypt_page_offset()` returns page-cache offset even for bounce pages.

## Disabled Build Behavior

When `CONFIG_FS_ENCRYPTION` is disabled:
- Most functions become no-ops or pass-through stubs.
- Preparing context under an encrypted directory returns `-EOPNOTSUPP`.
- Filename conversion returns the raw name.
- Crypto read/write alignment does nothing.
- Page encrypt/decrypt helpers return success without processing.
- Page-cache page helper returns the original page.

## Filename Length Design

The header documents Ceph’s encrypted filename strategy:
- Encrypted bytes are base64-encoded to avoid illegal filename characters.
- Base64 expansion can exceed `NAME_MAX`.
- Ceph limits the unhashed encrypted prefix to `CEPH_NOHASH_NAME_MAX`, then stores a SHA-256 tail hash.
- The 240-byte encoded target leaves space for synthetic snapshot names of the form `_<SNAPSHOT-NAME>_<INODE-NUMBER>`.

## Dependencies

- Linux fscrypt.
- Linux base64.
- SHA-256 definitions.
- Ceph MDS request, ACL/security context, and sparse extent types.
- Used by `crypto.c`, `addr.c`, and `caps.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/crypto.h -->