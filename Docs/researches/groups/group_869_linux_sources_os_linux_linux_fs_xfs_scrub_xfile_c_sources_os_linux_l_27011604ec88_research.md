# Group Research: group_869_linux_sources_os_linux_linux_fs_xfs_scrub_xfile_c_sources_os_linux_l_27011604ec88

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfile.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/xfile.c

Implements XFS scrub “xfile” temporary swappable memory using an unlinked shmem file as a page-cache-backed staging area.

Key elements:
- `xfile_create` allocates an `xfile`, creates a kernel shmem file with `VMA_NORESERVE`, assigns a separate inode lockdep class, and forces non-highmem backing pages via `mapping_set_gfp_mask(..., GFP_KERNEL)`.
- `xfile_destroy` restores the inode lock class, drops the file reference, and frees the wrapper.
- `xfile_load` reads directly from shmem folios, returning zeroes for sparse regions and treating errors/short reads as `-ENOMEM`.
- `xfile_store` grows `i_size` before page allocation, copies caller data into folios, marks them dirty, and treats short writes as allocation failure.
- `xfile_seek_data` delegates to `vfs_llseek(..., SEEK_DATA)`.
- `xfile_get_folio` returns a locked folio for a range that must fit within one folio; optionally allocates with `XFILE_ALLOC`.
- `xfile_put_folio` unlocks and drops the folio.
- `xfile_discard` truncates shmem page cache over a byte range.

Dependencies:
- Uses tmpfs/shmem internals: `shmem_kernel_file_setup`, `shmem_get_folio`, `shmem_truncate_range`.
- Uses scrub allocation flags and tracing from `scrub/scrub.h`, `scrub/xfile.h`, `scrub/trace.h`.
- Uses NOFS scopes around shmem page cache access.

Research notes:
- Caller is responsible for concurrency; VFS inode/freezer locking is intentionally bypassed.
- The file is never exposed to userspace and must be released with `xfile_destroy`.
- Error policy deliberately collapses I/O and allocation failures to `-ENOMEM`, because this abstraction is treated as temporary memory.
- `xfile_store` and `xfile_get_folio(XFILE_ALLOC)` update `i_size` before allocation so shmem will instantiate folios.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfile.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/xfile.h

Declares the xfile abstraction used by online scrub/repair staging structures.

Key elements:
- `struct xfile` wraps a single `struct file *`.
- Declares lifecycle functions `xfile_create` and `xfile_destroy`.
- Declares byte-oriented access functions `xfile_load`, `xfile_store`, `xfile_discard`, and `xfile_seek_data`.
- Defines `XFILE_MAX_FOLIO_SIZE` as the largest page-cache folio size.
- Defines `XFILE_ALLOC` for `xfile_get_folio`.
- Declares folio pin helpers `xfile_get_folio` and `xfile_put_folio`.
- `xfile_bytes` reports allocated bytes from inode `i_blocks`.

Dependencies:
- Requires Linux folio/file/inode types from surrounding kernel headers.
- Implemented by `scrub/xfile.c`.

Research notes:
- `xfile_get_folio` exposes locked folios directly, so users must obey lock/release discipline.
- `xfile_bytes` reports backing allocation, not logical file size.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfs_scrub.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/xfs_scrub.h

Public ioctl-facing declarations for XFS online scrub.

Key elements:
- When `CONFIG_XFS_ONLINE_SCRUB` is disabled, `xfs_ioc_scrub_metadata` and `xfs_ioc_scrubv_metadata` are macros returning `-ENOTTY`.
- When online scrub is enabled, declares both ioctl entry points.

Dependencies:
- Used by XFS ioctl code to gate scrub support at compile time.

Research notes:
- The header provides a hard disabled behavior without requiring callers to add their own `#ifdef` blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfs_scrub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_acl.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_acl.c

Implements XFS POSIX ACL conversion, get/set operations, mode synchronization, and ACL cache invalidation.

Key elements:
- `xfs_acl_from_disk` validates the on-disk ACL header/count/size, allocates a VFS `posix_acl`, converts big-endian XFS ACL entries to in-core entries, and maps ids through `init_user_ns`.
- `xfs_acl_to_disk` converts a VFS ACL to the XFS on-disk xattr format.
- `xfs_get_acl` selects `SGI_ACL_FILE` or `SGI_ACL_DEFAULT`, fetches the root namespace xattr, and converts it to a `posix_acl`.
- `__xfs_set_acl` upserts or removes the root namespace ACL xattr and updates the cached ACL on success.
- `xfs_acl_set_mode` logs inode mode changes in a transaction after ACL updates.
- `xfs_set_acl` validates ACL size, uses `posix_acl_update_mode` for access ACLs, applies the xattr update first, and then updates mode.
- `xfs_forget_acl` invalidates cached access/default ACLs when raw xattr paths modify ACL names.

Dependencies:
- Uses xattr/attr machinery: `xfs_attr_get`, `xfs_attr_change`, `XFS_ATTR_ROOT`.
- Uses VFS ACL helpers: `posix_acl_alloc`, `posix_acl_update_mode`, `set_cached_acl`, `forget_cached_acl`.

Research notes:
- Default ACLs are allowed only on directories; removing a nonexistent default ACL on a non-directory returns success.
- ACL xattr update precedes mode update to avoid changing mode if the xattr operation fails with `ENOSPC`.
- Malformed on-disk ACLs return `-EFSCORRUPTED` after logging corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_acl.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_acl.h

Compile-time interface for XFS POSIX ACL support.

Key elements:
- Under `CONFIG_XFS_POSIX_ACL`, declares `xfs_get_acl`, `xfs_set_acl`, `__xfs_set_acl`, and `xfs_forget_acl`.
- Without ACL support, maps `xfs_get_acl` and `xfs_set_acl` to `NULL`, makes `__xfs_set_acl` a no-op success, and makes `xfs_forget_acl` a no-op.

Dependencies:
- Consumed by inode/xattr code that must compile with or without POSIX ACL support.

Research notes:
- The no-op `__xfs_set_acl` behavior allows internal callers to avoid compile-time conditionals.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_aops.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_aops.c

Defines XFS address-space operations and writeback/read I/O integration with iomap, reflink COW, unwritten extent conversion, DAX, zoned storage, and swapfile activation.

Key elements:
- `xfs_setfilesize` transactionally advances `i_disk_size` after successful append writeback.
- `xfs_end_ioend_write` handles write completion: shutdown/error paths, COW cleanup on failure, zoned completion, reflink COW finish, unwritten conversion, and append size update.
- `xfs_end_io` drains inode ioend lists, sorts/merges ioends, and completes reads/writes via workqueue context.
- `xfs_end_bio` records zone append locations when needed and queues ioend completion work.
- `xfs_discard_folio` punches stale delalloc mappings after writeback mapping failure.
- `xfs_map_blocks` validates or refreshes writeback iomaps, handles COW-vs-data fork precedence, converts delalloc extents to real blocks, and trims mappings at COW boundaries.
- `xfs_writeback_range` and `xfs_writeback_submit` connect XFS mapping/conversion rules to `iomap_writepages`.
- Zoned writeback uses `xfs_zoned_map_blocks`, `xfs_zoned_writeback_range`, and `xfs_zoned_writeback_submit` to consume COW-fork delalloc reservations and allocate zones at bio submission time.
- `xfs_vm_writepages` selects normal or zoned writeback; `xfs_dax_writepages` uses DAX writeback.
- `xfs_vm_bmap` refuses swap-style bmap on COW or realtime files and otherwise delegates to iomap.
- Read paths use iomap read ops, with special ioend-backed read completion when the block device has integrity checksums.
- `xfs_vm_swap_activate` rejects zoned inodes, flushes inodegc to settle reflink removals, sets the swap block device, and delegates to `iomap_swapfile_activate`.
- Exports `xfs_address_space_operations` and `xfs_dax_aops`.

Dependencies:
- Heavy use of iomap read/writeback APIs.
- Calls XFS bmap, iomap, reflink, zoned allocation, realtime group, inodegc, and transaction helpers.
- Uses workqueue completion through `m_unwritten_workqueue`.

Research notes:
- Writeback mapping validity is guarded by fork sequence numbers plus page locking assumptions.
- COW writeback always takes precedence over overlapping data-fork mappings.
- Error handling for shared writeback must cancel COW and punch data-fork delalloc to avoid stale accounting.
- Zoned writeback differs substantially: allocation is deferred until bio submission and uses anonymous writes.
- `->bmap` intentionally refuses reflink/realtime files because swap bypasses filesystem I/O paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_aops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_aops.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_aops.h

Header for XFS address-space operation exports and shared writeback helpers.

Key elements:
- Declares `xfs_address_space_operations`.
- Declares `xfs_dax_aops`.
- Declares `xfs_setfilesize`.
- Declares shared bio completion function `xfs_end_bio`.

Dependencies:
- Used by inode setup and I/O code that wires XFS into VFS address-space operations.

Research notes:
- The header exposes only the minimal cross-file surface from `xfs_aops.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_aops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_attr_inactive.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_attr_inactive.c

Removes and invalidates an inode’s entire extended attribute fork during inode inactivation.

Key elements:
- `xfs_attr3_rmt_stale` maps remote attribute value extents and marks their incore buffers stale.
- `xfs_attr3_leaf_inactive` scans a leaf block, finds remote-value entries, and invalidates all remote value buffers.
- `xfs_attr3_node_inactive` recursively walks attribute btree nodes depth-first, invalidates child subtrees, invalidates child buffers, removes parent entries, and rolls transactions between children.
- `xfs_attr3_root_inactive` starts at attr block zero, handles node or leaf roots, reinitializes the root as an empty leaf before truncation, and rolls the transaction.
- `xfs_attr_inactive` allocates an attr-invalidation transaction, joins the inode, invalidates remote data and attr blocks, truncates all attr fork extents, invalidates the root block, removes the attr fork, and commits.

Dependencies:
- Uses attr leaf/node parsing, remote attr invalidation, bmap truncation, dir/attr health marking, and transaction roll helpers.
- Uses `xfs_attr_fork_remove` and `xfs_ifork_zap_attr` to remove on-disk and in-core fork state.

Research notes:
- The in-core attr fork is destroyed even on error.
- Remote attr value buffers are never logged, so stale marking is safe before extent removal.
- Tree recursion is bounded by `XFS_DA_NODE_MAXDEPTH`; excessive depth marks the attr fork sick and returns corruption.
- Reinitializing the root before truncating extents is a crash-safety measure to avoid entries pointing at freed remote blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_attr_inactive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_attr_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_attr_item.c

Implements logged deferred extended attribute intent/done items: ATTRI and ATTRD, including normal transaction logging, relogging, cancellation, and log recovery.

Key elements:
- Defines ATTRI/ATTRD slab caches and log item ops.
- `xfs_attri_log_nameval` stores refcounted shared name/new-name/value/new-value buffers for deferred attr operations.
- ATTRI lifecycle functions allocate, format, size, unpin, release, match, and free intent items.
- ATTRD lifecycle functions allocate, format, release, and link done items to their ATTRI.
- `xfs_attr_log_item` fills `xfs_attri_log_format` from `xfs_attr_intent`, with special fields for parent pointer operations.
- `xfs_attr_create_intent` creates a logged ATTRI only for `XFS_DA_OP_LOGGED` operations and shares the name/value buffer with deferred work.
- `xfs_attr_finish_item` resumes the state-machine attr operation via `xfs_attr_set_iter`, returning `-EAGAIN` until the delayed attr operation reaches `XFS_DAS_DONE`.
- `xfs_attri_validate` validates recovered intent fields against feature flags, namespace bits, name lengths, value sizes, parent pointer requirements, and inode numbers.
- `xfs_attri_recover_work` reconstructs `xfs_attr_intent` and `xfs_da_args` from recovered log data, igets the target inode, reads attr extents when needed, initializes add/replace/remove state, and queues recovered deferred work.
- `xfs_attr_recover_work` validates recovered buffers, creates a recovery transaction, finishes the recovered intent, and captures/commits deferred operations.
- `xfs_attr_relog_intent` copies an intent into a new ATTRI to push the log tail forward.
- `xfs_attr_defer_add` converts high-level set/replace/remove and parent-pointer operations into logged op flags and queues the deferred item.
- `xlog_recover_attri_commit_pass2` parses and validates recovered ATTRI log vectors, reconstructs shared name/value buffers, creates an incore ATTRI, and registers it with intent recovery.
- `xlog_recover_attrd_commit_pass2` releases matching recovered ATTRIs when a done item is found.

Dependencies:
- Uses XFS defer ops framework, xattr state machine, parent pointer validation, log recovery, transaction reservation, and inode recovery iget paths.
- Shares operation definitions with `xfs_log_format.h` and `xfs_attr_item.h`.

Research notes:
- ATTRI supports regular logged xattrs and parent pointer set/remove/replace operations; validation is feature-gated.
- Name/value buffers can exceed 64 KiB, so allocation uses `xlog_kvmalloc`.
- Parent pointer operations record inode generation and validate parent record values during recovery.
- Recovery treats malformed intent vectors as metadata corruption and rejects the entire intent.
- ATTRI reference counting accounts for races between AIL insertion and ATTRD processing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_attr_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_attr_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_attr_item.h

Defines kernel-only structures and APIs for logged deferred attribute intent/done items.

Key elements:
- `struct xfs_attri_log_nameval` stores kvecs for name, optional new name, value, optional new value, and a refcount; payload data follows the structure.
- `struct xfs_attri_log_item` wraps a log item, reference count, shared name/value buffer, and ATTRI log format.
- `struct xfs_attrd_log_item` wraps a done log item, backpointer to ATTRI, and ATTRD log format.
- Declares `xfs_attri_cache` and `xfs_attrd_cache`.
- Defines `enum xfs_attr_defer_op` for set, remove, and replace.
- Declares `xfs_attr_defer_add`.

Dependencies:
- Consumed by deferred xattr code and log item implementation in `xfs_attr_item.c`.

Research notes:
- Comments document that ATTRI records work to be done and ATTRD records completion.
- The trailing-buffer design is central to sharing large names/values across deferred state and log items.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_attr_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_attr_list.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_attr_list.c

Implements listing of XFS extended attributes across shortform, leaf, and node formats with cursor-based continuation.

Key elements:
- `xfs_attr_shortform_compare` sorts shortform entries by hash then entry number.
- `xfs_attr_shortform_list` lists local shortform attrs directly when the output buffer can hold all entries; otherwise builds and sorts a temporary hash array to support stable cursor continuation.
- `xfs_attr_node_list_lookup` descends the attr btree from root to the leaf covering the cursor hash, validating node/leaf magic, levels, headers, and child pointers.
- `xfs_attr_node_list` validates or resynchronizes a cursor block, then walks leaf blocks in forward order until the output callback says enough or leaves run out.
- `xfs_attr3_leaf_list_int` lists entries from one leaf block, handles cursor duplicate counts, skips incomplete entries unless allowed, extracts local or remote names/value lengths, validates names, and calls the output callback.
- `xfs_attr_leaf_list` lists a single root leaf.
- `xfs_attr_list_ilocked` dispatches based on attr fork format: no attrs, shortform, single leaf, or node tree.
- `xfs_attr_list` handles shutdown check, stats, shared attr map locking, and unlock.

Dependencies:
- Uses attr fork formats, shortform parsing, attr leaf/node readers, hash calculation, name validation, and health marking.
- Output is callback-driven via `xfs_attr_list_context::put_listent`.

Research notes:
- Shortform attrs are not stored hash-sorted, so partial listings require a temporary sorted array.
- Cursor validation is defensive; invalid cursor blocks cause lookup from the btree root.
- Corrupt attr names, bad magic, impossible tree levels, or root backreferences mark the attr fork sick and return `-EFSCORRUPTED`.
- `bufsize == 0` is treated as a search-callback mode and avoids unnecessary sorting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_attr_list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_bio_io.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_bio_io.c

Provides a small block-device read/write helper for XFS metadata buffers that may be virtually contiguous vmalloc memory.

Key elements:
- `bio_max_vecs` computes a segment count from a byte count.
- `xfs_rw_bdev` applies `REQ_META | REQ_SYNC`, uses `bdev_rw_virt` for non-vmalloc buffers, and builds/chains bios with `bio_add_vmalloc_chunk` for vmalloc buffers.
- On vmalloc input, allocates additional chained bios when the current bio cannot accept more chunks.
- Uses `submit_bio_wait` on the final bio and releases it.

Dependencies:
- Uses block layer bio helpers and `bdev_rw_virt`.
- Intended for synchronous metadata-oriented I/O.

Research notes:
- The code attempts to invalidate vmalloc mappings after reads, but compares `op == REQ_OP_READ` after OR-ing request flags into `op`; as written, that condition is unlikely to be true for read operations with flags attached.
- Bio chaining means only the final bio is waited on directly; earlier bios are chained to it.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_bio_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_bmap_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_bmap_item.c

Implements logged deferred bmap update intent/done items: BUI and BUD, used to redo mapping and unmapping of inode bmbt extents across transaction rolls and log recovery.

Key elements:
- Defines BUI/BUD slab caches and log item ops.
- BUI lifecycle handles allocation, formatting, sizing, unpin, release, match, relogging, and recovery copy-in.
- BUD lifecycle handles formatting, sizing, release, and linking to the originating BUI.
- `xfs_bmap_update_log_item` records owner inode, start block, file offset, length, map/unmap type, unwritten state, attr fork, and realtime flags into the BUI extent slot.
- `xfs_bmap_update_create_intent` optionally sorts bmap intents by owner inode and logs them into a BUI.
- `xfs_bmap_defer_add` takes a group intent reference, precharges `i_delayed_blks` for map operations, traces, and queues deferred bmap work.
- `xfs_bmap_update_cancel_item` reverses map precharge, drops group intent, and frees the intent.
- `xfs_bmap_update_finish_item` calls `xfs_bmap_finish_one`; unfinished unmaps return `-EAGAIN` for continuation.
- `xfs_bui_validate` checks recovered BUI format, flags, operation type, owner inode, file extent range, and data/realtime physical extent range.
- `xfs_bui_recover_work` reconstructs `xfs_bmap_intent`, igets the owner inode, restores fork/type/extent state, takes group intent, and queues recovered work.
- `xfs_bmap_recover_work` allocates a recovery transaction, locks/joins the inode, verifies realtime consistency, reserves extent-count growth, finishes the intent, and captures/commits defer ops.
- Recovery pass2 creates incore BUIs from logged BUI formats and releases BUIs when matching BUDs are found.

Dependencies:
- Uses XFS defer ops, log item/recovery framework, bmap finish helpers, group intent references, inode recovery iget, and transaction reservations.

Research notes:
- `XFS_BUI_MAX_FAST_EXTENTS` is one, so each BUI carries one mapping update.
- `i_delayed_blks` precharge prevents transient `stat` under-reporting during out-of-place remap operations.
- Group intent references bridge bmap work that can enqueue rmap/refcount work across transaction rolls.
- Recovery rejects BUI records with unsupported flags or invalid extents before touching metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_bmap_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_bmap_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_bmap_item.h

Defines kernel-only BUI/BUD structures and APIs for deferred bmap btree redo logging.

Key elements:
- Documents BUI as bmap update intent and BUD as bmap update done.
- Defines `XFS_BUI_MAX_FAST_EXTENTS` as one.
- `struct xfs_bui_log_item` contains log item, refcount, next extent counter, and BUI format.
- `xfs_bui_log_item_sizeof` computes variable-size item allocation size.
- `struct xfs_bud_log_item` contains done log item, pointer to BUI, and BUD format.
- Declares BUI/BUD caches, `xfs_bmap_defer_add`, and log-space calculators.

Dependencies:
- Implemented by `xfs_bmap_item.c`.
- Uses format definitions from XFS log format headers.

Research notes:
- Comments explicitly describe crash recovery semantics: intent in the first transaction, done item in the transaction that performs the bmbt update.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_bmap_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_bmap_util.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_bmap_util.c

Provides higher-level bmap utilities for block mapping reports, preallocation, hole punching, EOF block trimming, collapse/insert range, and legacy extent swapping.

Key elements:
- `xfs_fsb_to_db` maps filesystem blocks to disk addresses, with realtime handling.
- `xfs_zero_extent` issues block zeroing for an inode extent.
- `xfs_bmap_count_leaves` and `xfs_bmap_count_blocks` count real extents and btree blocks, excluding delayed allocation.
- `xfs_getbmap` implements getbmapx reporting for data/attr/debug COW forks, flushing delalloc when needed, reporting holes, delalloc, unwritten/prealloc, and shared extent state.
- `xfs_bmap_punch_delalloc_range` removes delayed allocation extents from a byte range, with special zoned allocation-context accounting.
- `xfs_can_free_eofblocks` decides whether post-EOF real/delalloc blocks can be freed.
- `xfs_free_eofblocks` attaches quotas, waits for DIO, punches prealloc/delalloc or truncates post-EOF data extents transactionally.
- `xfs_alloc_file_space` implements preallocation, including extsize rounding, realtime/data reservations, repeated `xfs_bmapi_write`, and `XFS_DIFLAG_PREALLOC`.
- `xfs_flush_unmap_range` writes back and invalidates the page cache around extent-aligned modification ranges.
- `xfs_free_file_space` punches complete blocks, handles big realtime allocation-unit alignment, and zeroes partial block edges without extending EOF.
- `xfs_prepare_shift` frees EOF blocks, flushes/invalidate ranges, and cancels COW data before extent shifts.
- `xfs_collapse_file_space` frees a range then shifts later extents left.
- `xfs_insert_file_space` verifies insertability, splits at the insertion point, and shifts extents right.
- `xfs_swap_extents_check_format` validates data fork formats and quota identity before swap.
- `xfs_swap_extent_flush` flushes and invalidates page cache for swap participants.
- `xfs_swap_extent_rmap` remaps extents one piece at a time when rmapbt is enabled.
- `xfs_swap_extent_forks` swaps data forks directly when rmapbt is absent, adjusts block counts/delalloc accounting, and sets inode log flags.
- `xfs_swap_change_owner` fixes bmbt block owner fields after fork swaps on v3 inode filesystems.
- `xfs_swap_extents` performs the legacy full-file swap operation with locking, quota attach, format checks, timestamp validation, reflink/COW handling, rmap or fork-swap logic, and transaction commit.

Dependencies:
- Uses XFS bmap core, transactions, quotas, reflink, iomap-adjacent flushing, realtime allocation geometry, zoned allocation context, and rmap/refcount-aware remap logic.

Research notes:
- getbmap reports shared/unshared subranges separately by trimming around reflink sharing.
- Collapse/insert range must stabilize page cache and COW fork state to avoid extent-shift races.
- `xfs_swap_extents` is full-file only and rejects realtime-group files because the deprecated interface cannot recover such swaps after crash.
- Fork swapping without rmapbt requires careful bmbt owner relogging for crash recovery.
- Preallocated files keep speculative real preallocations during EOF cleanup unless delayed allocations must be removed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_bmap_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_bmap_util.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_bmap_util.h

Declares kernel-only bmap utility interfaces used outside `xfs_bmap_util.c`.

Key elements:
- Declares realtime allocation helper `xfs_bmap_rtalloc`, with a non-RT stub returning `-EFSCORRUPTED`.
- Declares delayed allocation punching and getbmap support.
- Defines `struct kgetbmap`, the in-kernel getbmap output record.
- Declares selected `xfs_bmap.c` helpers needed by bmap utility code.
- Declares preallocation, hole punching, collapse range, insert range, EOF block cleanup, swap extents, block conversion, extent counting, and unmap-range flushing APIs.

Dependencies:
- Shared with ioctl, inode, writeback, and bmap code paths.

Research notes:
- The non-RT `xfs_bmap_rtalloc` stub treats attempts to allocate RT extents without RT support as corruption.
- Header keeps the higher-level bmap operations separate from lower-level bmap implementation internals.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_bmap_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_buf.c

Implements the XFS metadata buffer cache: allocation, lookup, backing memory, I/O submission, verification, lifecycle, LRU shrinking, delayed write queues, and buffer target setup.

Key elements:
- `xfs_buf_stale` marks a locked buffer stale, clears delwri state, removes it from LRU, and prevents stale buildup.
- Backing memory allocation supports xmbuf/tmpfs mapping for memory targets, aligned kmalloc for sub-page power-of-two buffers, single folio/high-order folio buffers, and vmalloc fallback.
- `xfs_buf_alloc` initializes buffer state, maps, lock/refcount, LRU ref, pin waiters, target/mount, and backing memory.
- Buffer lookup uses an rhashtable keyed by starting daddr and total length; stale length mismatches are tolerated for busy reallocation cases.
- `xfs_buf_get_map` verifies range/sector alignment, takes per-AG references, looks up or inserts a buffer, handles incore-only lookup, clears stale errors for non-read callers, and returns a locked buffer.
- `xfs_buf_read_map` reads and verifies buffers, re-verifies cached buffers missing ops, marks failed reads stale, maps bad CRC to `-EFSCORRUPTED`, and reports metadata I/O errors.
- `xfs_buf_readahead_map` performs trylock async read-ahead except for memory targets.
- Uncached buffer helpers allocate buffers outside the hash by using `XFS_BUF_DADDR_NULL`.
- Reference lifecycle uses `lockref`, rhashtable removal, LRU insertion, RCU freeing, per-AG ref release, and immediate destruction for uncached or non-LRU buffers.
- Buffer locking uses a semaphore; stale pinned buffers force the log before blocking.
- I/O completion verifies reads, verifies writes before submission, handles vmalloc cache invalidation, updates `XBF_DONE`, processes buffer log items, calls optional iodone, and releases async refs.
- Async write error handling retries transient metadata write errors, marks log items failed for retry, escalates permanent failures to filesystem shutdown, and stales failed buffers.
- Bio submission builds one bio over contiguous virtual memory and splits/chains bios for compound buffer maps.
- Buftarg lifecycle initializes hash/LRU/shrinker/readahead counters, configures sector sizes and atomic write unit geometry, opens DAX holders, syncs blockdev pagecache, drains outstanding buffers, and frees targets.
- Delayed write helpers queue, cancel, synchronously submit, or nowait-submit sorted buffer lists; stale/synchronously written buffers are lazily removed from delwri lists.
- `xfs_verify_magic` and `xfs_verify_magic16` compare on-disk magic values against buffer verifier tables.

Dependencies:
- Uses Linux rhashtable, list_lru, shrinker, lockref, bio, folio/vmalloc, blockdev, DAX, and workqueue APIs.
- Integrates with XFS log, transaction buffer items, error injection/configuration, per-AG lifetime, and in-memory buffer target code.

Research notes:
- Lock ordering is documented for stale, release, buftarg drain, and shrinker isolation paths.
- New cached buffers are locked and held before insertion so RCU lookups racing insertion cannot use unlocked uninitialized buffers.
- Read errors clear `XBF_DONE` and stale the buffer so future cache lookups reread from disk.
- Write verification failure forces shutdown with `SHUTDOWN_CORRUPT_INCORE`.
- Async I/O completion is punted to `m_buf_workqueue` to process buffer/log-item completion outside bio completion context.
- Delwri nowait submission intentionally skips locked or pinned buffers and leaves them on the caller’s list for later retry/cancel.
- Draining a buftarg warns if buffers with permanent write failure are freed, because dirty metadata was discarded after shutdown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_buf.h

Defines XFS metadata buffer and buffer target structures, flags, verifier interfaces, and public buffer-cache APIs.

Key elements:
- Defines buffer daddr constants `XFS_BUF_DADDR_MAX` and `XFS_BUF_DADDR_NULL`.
- Defines buffer state flags: read, write, read-ahead, async, done, stale, write-fail, log-recovery, kmem-backed, delayed-write queued, livescan, incore, and trylock.
- `struct xfs_buftarg` represents a buffer target/block device with DAX state, sector geometry, LRU/shrinker state, readahead counters, I/O ratelimiting, atomic write unit bounds, and hash table.
- `struct xfs_buf_map` describes one physical I/O segment.
- `struct xfs_buf_ops` provides verifier name, v4/v5 magic values, read/write verify callbacks, and optional structural verifier.
- `struct xfs_buf` stores hash node/key, length, lock/ref state, LRU state, perag/mount/target pointers, backing address, I/O work/completion, log item links, maps, pin count, error/retry state, verifier ops, and RCU head.
- Declares buffer lookup/read/readahead/uncached APIs and inline single-map wrappers.
- Declares hold/release, lock/unlock, synchronous write, I/O error reporting, corrupt marking, stale marking, delayed-write queue/submit helpers, checksum helpers, buftarg allocation/free/drain/configuration, and magic verification.
- Defines inline helpers for incore lookup, get/read/readahead, `xfs_buf_relse`, buffer offsets, zeroing, daddr access, oneshot caching, pin checks, and checksum update/verify.

Dependencies:
- Consumed across XFS metadata code for all block-buffer access and verification.
- Implemented primarily by `xfs_buf.c`.

Research notes:
- `xfs_buftarg` distinguishes metadata sector size from device logical sector size.
- `XBF_LIVESCAN` exists for online fsck cache scanning and changes lookup behavior around stale/nonmatching buffers.
- `xfs_buf_oneshot` marks a buffer disposable after release unless it is already strongly LRU-referenced.
- `xfs_buf_islocked` checks semaphore count directly, matching the buffer lock implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf.h -->