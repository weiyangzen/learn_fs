# Group Research: group_1111_linux_stable_sources_os_linux_linux_stable_fs_xfs_scrub_xfile_c_sou_26ffcf19a9b4

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfile.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfile.c

This file implements XFS online scrub’s `xfile` abstraction: a private, unlinked shmem-backed temporary file used as pageable scratch storage for online checking and repair. It is designed as “swappable memory” for large indexed data structures that may not fit in RAM, while remaining inaccessible to userspace.

Key operations:
- `xfile_create` allocates `struct xfile`, creates a `shmem_kernel_file_setup` file, assigns a private lockdep class, and forces `GFP_KERNEL` page-cache backing so repair code can access folio memory directly without highmem mapping.
- `xfile_destroy` restores the inode rwsem lockdep class, drops the file reference, and frees the wrapper.
- `xfile_load` and `xfile_store` copy byte ranges directly between caller buffers and shmem folios, wrapping page-cache allocation/lookup with `memalloc_nofs_save` to avoid filesystem reclaim recursion.
- `xfile_seek_data` delegates to `vfs_llseek(..., SEEK_DATA)` to find written ranges.
- `xfile_get_folio` returns a locked folio covering a single-object range, optionally allocating and dirtying it with `XFILE_ALLOC`.
- `xfile_discard` truncates a range from shmem page cache.

Important behavior:
- Missing folios read as zeroes in `xfile_load`, so sparse xfiles behave like zero-filled memory.
- Errors and short I/O are deliberately collapsed to `-ENOMEM`, reflecting the “memory object” abstraction rather than ordinary file I/O semantics.
- Callers are responsible for concurrency; VFS freezer/inode locks are intentionally bypassed.

Dependencies and integration:
- Used by online scrub/repair helpers such as xfarray-like staging structures.
- Relies on tmpfs/shmem folio APIs, VFS seek-data semantics, XFS scrub tracepoints, and nofs allocation contexts.

Risk notes:
- Object ranges passed to `xfile_get_folio` must not cross folio boundaries; the function returns `NULL` if they do.
- `xfile_discard` computes `pos + count - 1`; callers must avoid zero-length discard ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfile.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfile.h

This header declares the scrub `xfile` API and the minimal wrapper structure around a shmem `struct file`.

Exports:
- `struct xfile { struct file *file; }`
- Lifecycle: `xfile_create`, `xfile_destroy`
- Byte I/O: `xfile_load`, `xfile_store`
- Sparse/file-range helpers: `xfile_discard`, `xfile_seek_data`
- Folio helpers: `xfile_get_folio`, `xfile_put_folio`
- `xfile_bytes` returns allocated bytes based on `i_blocks << SECTOR_SHIFT`.

Constants:
- `XFILE_MAX_FOLIO_SIZE` mirrors the maximum page-cache folio size.
- `XFILE_ALLOC` requests allocation of a folio if absent.

Integration:
- Provides the interface consumed by scrub staging structures without exposing shmem internals to callers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfs_scrub.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfs_scrub.h

This header declares the ioctl entry points for XFS online scrub metadata operations.

Behavior:
- If `CONFIG_XFS_ONLINE_SCRUB` is disabled, `xfs_ioc_scrub_metadata` and `xfs_ioc_scrubv_metadata` are macro stubs returning `-ENOTTY`.
- If enabled, the header exposes the real prototypes taking a file and user pointer.

Integration:
- This is the small compile-time gate between the main XFS ioctl layer and the online scrub implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfs_scrub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_acl.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_acl.c

This file implements POSIX ACL conversion, retrieval, update, and cache invalidation for XFS. ACLs are stored as root namespace extended attributes using XFS on-disk ACL records and converted to/from Linux `struct posix_acl`.

Key operations:
- `xfs_acl_from_disk` validates ACL blob size and count, converts big-endian on-disk entries to in-core POSIX ACL entries, and maps UID/GID IDs through `init_user_ns`.
- `xfs_acl_to_disk` serializes POSIX ACL entries into the XFS big-endian ACL xattr format.
- `xfs_get_acl` maps `ACL_TYPE_ACCESS` and `ACL_TYPE_DEFAULT` to `SGI_ACL_FILE` / `SGI_ACL_DEFAULT`, reads the root xattr via `xfs_attr_get`, converts it, and returns `NULL` on `-ENOATTR`.
- `__xfs_set_acl` upserts or removes the ACL xattr using `xfs_attr_change`, then updates the VFS ACL cache.
- `xfs_set_acl` enforces max-entry limits, calls `posix_acl_update_mode` for access ACLs, writes the ACL xattr first, and only then updates inode mode in a separate transaction.
- `xfs_forget_acl` drops cached ACLs when callers bypass the ACL API through xattrs.

Important behavior:
- Default ACLs are only allowed on directories; setting one on a non-directory fails with `-EACCES`, while removing one is a no-op.
- Mode update is deliberately ordered after xattr update to avoid changing file permissions if ACL persistence fails due to ENOSPC.
- Corrupt ACL sizes/counts are reported with `XFS_CORRUPTION_ERROR` and return `-EFSCORRUPTED`.

Dependencies:
- XFS attr subsystem, transaction subsystem, inode logging, POSIX ACL helpers, xattr namespace constants.

Risk notes:
- `xfs_forget_acl` trusts callers to provide valid ACL xattr contents and keep `i_mode` consistent when bypassing normal ACL handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_acl.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_acl.h

This header declares XFS POSIX ACL operations and provides no-op or `NULL` fallbacks when ACL support is disabled.

Exports when `CONFIG_XFS_POSIX_ACL` is enabled:
- `xfs_get_acl`
- `xfs_set_acl`
- `__xfs_set_acl`
- `xfs_forget_acl`

Fallbacks:
- `xfs_get_acl` and `xfs_set_acl` become `NULL`.
- `__xfs_set_acl` returns success.
- `xfs_forget_acl` is an empty inline.

Integration:
- Lets inode and xattr code compile cleanly with or without POSIX ACL support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_aops.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_aops.c

This file implements XFS address-space operations for buffered I/O, DAX writeback, writeback completion, read submission, swap activation, and zoned filesystem writeback support.

Major responsibilities:
- File size update: `xfs_setfilesize` logs `i_disk_size` after successful append writeback.
- Write I/O completion: `xfs_end_ioend_write` handles shutdown, I/O errors, COW cleanup, unwritten extent conversion, zoned completion, reflink COW completion, and post-write file size extension.
- Completion queueing: `xfs_end_bio` records zone-append sector results if applicable, queues ioends to `m_unwritten_workqueue`, and `xfs_end_io` sorts/merges ioends before finishing them.
- Writeback mapping: `xfs_map_blocks` validates cached iomaps using fork sequence counters, handles COW fork precedence, converts delalloc extents, trims mappings at COW boundaries, and reports holes.
- Buffered writeback: `xfs_writeback_range` maps ranges and feeds folios into iomap ioends; failures punch stale delalloc blocks with `xfs_discard_folio`.
- Zoned writeback: `xfs_zoned_map_blocks` consumes COW-fork delalloc extents and creates anonymous-write iomaps; `xfs_zoned_writeback_submit` allocates/submits zone writes and generates integrity metadata if needed.
- Read path: chooses default iomap read ops or custom ioend-backed read completion when block device integrity checksums require deferred completion.
- Swap activation: rejects zoned inodes, flushes inodegc to resolve pending reflink removals, sets the correct swap block device, and delegates to `iomap_swapfile_activate`.

Exported address-space operation tables:
- `xfs_address_space_operations`: read folio, readahead, writepages, dirty/release/invalidate folio, bmap, migration, partial uptodate, error removal, swap activation.
- `xfs_dax_aops`: DAX writepages and swap activation.

Important concurrency and correctness points:
- Writeback mapping relies on locked folios plus fork sequence counters to detect concurrent extent changes.
- COW mappings take precedence over data fork mappings.
- I/O completion uses nofs allocation contexts because completion can run under reclaim.
- Swap files are rejected on reflink/COW and realtime cases that cannot safely expose raw block mappings.

Dependencies:
- iomap writeback/read APIs, XFS bmap/reflink/iomap/zone allocation, block integrity, workqueues, inodegc, DAX.

Risk notes:
- Error paths must remove delalloc mappings from clean pages or later direct I/O can observe stale allocation state.
- Zoned writeback uses different invariants: allocation happens at submit time, not map time.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_aops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_aops.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_aops.h

This header exposes the XFS address-space operation tables and key helpers implemented in `xfs_aops.c`.

Exports:
- `xfs_address_space_operations`
- `xfs_dax_aops`
- `xfs_setfilesize`
- `xfs_end_bio`

Integration:
- Used by inode setup and writeback/read completion code to connect VFS page-cache operations to XFS-specific iomap behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_aops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_attr_inactive.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_attr_inactive.c

This file removes an inode’s entire extended attribute fork during inode inactivation. It invalidates remote attribute value buffers, walks attr leaf/node trees, truncates attr fork extents, and removes the in-core/on-disk attr fork.

Key operations:
- `xfs_attr3_rmt_stale` maps remote attr value extents and marks their incore buffers stale without logging them.
- `xfs_attr3_leaf_inactive` scans leaf entries, finds remote values, invalidates their value blocks, and releases the leaf buffer.
- `xfs_attr3_node_inactive` recursively walks attr btree nodes depth-first, invalidating child subtrees, binvalidating child buffers, removing parent entries, and rolling transactions between removals.
- `xfs_attr3_root_inactive` starts at attr block zero, dispatches to node or leaf invalidation, reinitializes an empty root leaf to make crash recovery safe, and rolls the transaction before truncation.
- `xfs_attr_inactive` coordinates the whole teardown: checks for an attr fork, allocates a transaction, invalidates tree contents, truncates all attr fork extents including root, removes the fork, commits, and always zaps the in-core fork on error.

Important behavior:
- Remote attr value buffers are not logged, so they can be marked stale directly.
- The root leaf is reinitialized before truncation so a crash during truncation cannot leave entries pointing at freed remote value blocks.
- Recursion is bounded by `XFS_DA_NODE_MAXDEPTH`; exceeding it marks the attr fork sick and returns `-EFSCORRUPTED`.

Dependencies:
- XFS attr leaf/node formats, remote attr helpers, dir/attr health marking, transactions, buffer invalidation, extent truncation.

Risk notes:
- The function removes the in-memory attr fork even on error, which is intentional for inode inactivation but important for callers to understand.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_attr_inactive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_attr_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_attr_item.c

This file implements logged extended-attribute deferred operation items: ATTRI intent items and ATTRD done items. These make xattr set/remove/replace operations crash-recoverable, including parent pointer variants.

Core data handling:
- `xfs_attri_log_nameval_alloc/get/put` manages refcounted name/value/new-name/new-value buffers shared between deferred attr state and log items.
- `xfs_attri_item_free/release` and `xfs_attrd_item_free/release` handle log item lifetime, AIL removal, shadow vectors, and shared buffer references.

ATTRI formatting:
- `xfs_attri_item_size` and `xfs_attri_item_format` calculate and emit log vectors for the format item plus required name/value vectors.
- `xfs_attr_log_item` fills inode number, generation for parent pointers, operation flags, name lengths, value length, and attr filter into the log format.
- `xfs_attr_create_intent` builds an ATTRI item for deferred logged attr work if the operation has `XFS_DA_OP_LOGGED`.

Deferred operation flow:
- `xfs_attr_defer_add` translates high-level set/remove/replace operations into ATTRI op flags, initializes the attr state machine, and queues the deferred item.
- `xfs_attr_finish_item` runs `xfs_attr_set_iter`; if more state-machine work remains, it returns `-EAGAIN` to continue after a transaction roll.
- `xfs_attr_create_done` creates an ATTRD tied to a specific ATTRI.
- `xfs_attr_relog_intent` recreates an equivalent intent to move the log tail forward.

Recovery:
- `xfs_attri_validate` validates op flags, namespace filters, feature support, name/value lengths, parent pointer requirements, and inode number.
- `xfs_attri_recover_work` reconstructs `xfs_attr_intent` and `xfs_da_args` from recovered ATTRI data, attaches the inode, reads attr extents when needed, and initializes the correct add/replace/remove state.
- `xfs_attr_recover_work` validates recovered data, allocates a recovery transaction with suitable reservation, finishes the intent, and captures/commits deferred work.
- `xlog_recover_attri_commit_pass2` validates recovered log vector counts and iovec lengths by operation type, validates names and parent pointer values, reconstructs the shared name/value buffer, and registers the recovered intent.
- `xlog_recover_attrd_commit_pass2` releases matching pending ATTRI intents when a done item is found.

Exported operation tables:
- `xfs_attr_defer_type`
- `xlog_attri_item_ops`
- `xlog_attrd_item_ops`

Dependencies:
- XFS deferred ops, log item framework, attr state machine, log recovery, parent pointer feature checks, inode recovery lookup.

Risk notes:
- Recovery validation is strict because malformed ATTRI records can otherwise replay arbitrary xattr changes.
- Parent pointer operations require inode generation checks and fixed-size `struct xfs_parent_rec` values.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_attr_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_attr_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_attr_item.h

This header defines kernel-only structures for XFS logged xattr intent/done items.

Definitions:
- `struct xfs_attri_log_nameval`: refcounted storage for name, optional new name, value, and optional new value vectors.
- `struct xfs_attri_log_item`: ATTRI intent log item containing the log item header, refcount, shared name/value object, and on-disk log format.
- `struct xfs_attrd_log_item`: ATTRD done log item pointing back to its ATTRI.
- `enum xfs_attr_defer_op`: set, remove, replace.

Exports:
- `xfs_attri_cache`
- `xfs_attrd_cache`
- `xfs_attr_defer_add`

Integration:
- Shared between attr operation code, transaction defer code, and log recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_attr_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_attr_list.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_attr_list.c

This file implements listing of extended attributes from shortform, leaf, and node-format attr forks.

Shortform listing:
- `xfs_attr_shortform_list` lists local in-inode attr entries directly when the output buffer is large enough or when using a zero-size search callback.
- If the buffer is too small, it builds a temporary array of sortable entries, computes hashes, sorts by hash and entry number, resumes from the cursor, and emits entries until full.
- It validates namespaces and names, marking the attr fork sick on corruption.

Node/leaf listing:
- `xfs_attr_node_list_lookup` walks the attr btree from root using the cursor hash to find the correct leaf, validating node magic, levels, and leaf headers.
- `xfs_attr_node_list` validates cursor block hints, falls back to root lookup when stale/wrong, then walks forward across leaf blocks until the result buffer is full or leaves end.
- `xfs_attr3_leaf_list_int` emits entries from a leaf, resynchronizes using duplicate hash counts when needed, skips incomplete entries unless allowed, and handles local versus remote values.
- `xfs_attr_leaf_list` reads the single leaf block and delegates to the leaf walker.

Public entry points:
- `xfs_attr_list_ilocked` requires the inode attr lock, chooses shortform/leaf/node listing based on fork format, and ensures extents are read before block-format listing.
- `xfs_attr_list` checks shutdown, takes the shared attr map lock, calls the ilocked helper, and unlocks.

Dependencies:
- XFS attr formats, attr leaf/node verifiers, dir/attr health marking, xfs sort, transaction buffer reads.

Risk notes:
- Cursor validation is defensive because userspace passes cursors across syscalls while the attr tree may change.
- Shortform sorting allocates with `__GFP_NOFAIL`, so callers should avoid unbounded attr counts; XFS format limits normally constrain this.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_attr_list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_bio_io.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_bio_io.c

This file provides `xfs_rw_bdev`, a small helper for synchronous metadata-style reads/writes directly to a block device.

Behavior:
- Adds `REQ_META | REQ_SYNC` to the requested operation.
- If the data buffer is not vmalloc-backed, delegates to `bdev_rw_virt`.
- For vmalloc buffers, builds one or more bios with `bio_add_vmalloc_chunk`, chains overflow bios, submits earlier bios as needed, and waits on the final bio with `submit_bio_wait`.
- Invalidates the kernel vmap range after reads.

Important note:
- The final check compares `op == REQ_OP_READ` after `op` has been ORed with flags; this depends on how `enum req_op` and op flags are represented. The intent is clearly to invalidate vmalloc mappings after read operations.

Dependencies:
- Block layer bio allocation/chaining/submission, vmalloc helpers, XFS platform helpers.

Risk notes:
- Callers must pass valid sector/count/data alignment for the target block device.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_bio_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_item.c

This file implements bmap update intent/done log items: BUI and BUD. These provide redo logging for deferred file block mapping and unmapping operations.

Core log item handling:
- `xfs_bui_init`, `xfs_bui_item_size`, `xfs_bui_item_format`, `xfs_bui_item_unpin`, `xfs_bui_item_release`, and `xfs_bui_release` manage BUI lifecycle and formatting.
- `xfs_bud_item_size`, `xfs_bud_item_format`, `xfs_bud_item_release`, and `xfs_bud_item_intent` manage BUD done items tied to a BUI.
- `xfs_bui_log_space` and `xfs_bud_log_space` expose reservation sizing.

Deferred operation flow:
- `xfs_bmap_update_log_item` records owner inode, start block, file offset, length, operation type, unwritten state, attr fork flag, and realtime flag into the BUI extent record.
- `xfs_bmap_update_create_intent` creates a BUI and optionally sorts work by inode.
- `xfs_bmap_update_create_done` creates the matching BUD.
- `xfs_bmap_defer_add` takes a group intent reference, adjusts `i_delayed_blks` for map operations, traces, and queues the deferred item.
- `xfs_bmap_update_finish_item` calls `xfs_bmap_finish_one`; partial unmaps return `-EAGAIN` until complete.
- `xfs_bmap_update_cancel_item` reverses delayed block accounting, drops group intent references, and frees the intent.

Recovery:
- `xfs_bui_validate` verifies one extent, legal flags, operation type, inode number, file offset/length, and filesystem/realtime block range.
- `xfs_bui_recover_work` reconstructs an in-core `xfs_bmap_intent` from the logged extent and attaches it to recovered deferred work.
- `xfs_bmap_recover_work` allocates a recovery transaction, locks/joins the inode, checks realtime consistency, reserves inode extent capacity, finishes the intent, and captures/commits deferred ops.
- `xfs_bmap_relog_intent` recreates a BUI for log-tail movement.
- `xlog_recover_bui_commit_pass2` validates on-disk BUI format length/count, reconstructs the in-core BUI, and registers it.
- `xlog_recover_bud_commit_pass2` releases matching recovered BUIs when a BUD appears.

Exported operation tables:
- `xfs_bmap_update_defer_type`
- `xlog_bui_item_ops`
- `xlog_bud_item_ops`

Dependencies:
- XFS defer framework, bmap operations, log recovery, AG/RT group intent references, inode extent count reservations.

Risk notes:
- BUI currently logs exactly one extent via `XFS_BUI_MAX_FAST_EXTENTS`.
- Correct delayed block accounting around map cancellation/recovery is critical for stat and quota consistency.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_item.h

This header defines kernel-only BUI/BUD bmap redo item structures and exported helpers.

Concept:
- BUI records a bmap update intent in the first transaction of a rolled sequence.
- BUD records completion in the transaction that performs the bmbt update.
- Log recovery replays BUI work if the final BUD was not committed.

Definitions:
- `XFS_BUI_MAX_FAST_EXTENTS` is currently `1`.
- `struct xfs_bui_log_item` contains a log item, refcount, next-extent counter, and BUI log format.
- `struct xfs_bud_log_item` contains a log item, pointer to the BUI, and BUD log format.

Exports:
- `xfs_bmap_defer_add`
- `xfs_bui_log_space`
- `xfs_bud_log_space`
- BUI/BUD kmem caches.

Integration:
- Used by deferred bmap updates and log recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_util.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_util.c

This file provides higher-level block mapping utilities around core XFS bmap code: extent counting, FIEMAP/getbmap reporting, delayed allocation punching, EOF block cleanup, file space allocation/freeing, collapse/insert range, and extent swapping.

Mapping and reporting:
- `xfs_fsb_to_db` converts fsblocks to disk addresses, handling realtime inodes specially.
- `xfs_zero_extent` issues block-device zeroout for an inode extent.
- `xfs_bmap_count_leaves` and `xfs_bmap_count_blocks` count real extent records and btree blocks, excluding delayed allocation extents.
- `xfs_getbmap` validates flags, chooses data/attr/COW fork, flushes delalloc unless requested, reads extents, reports holes, delalloc, unwritten, shared, and last flags into `kgetbmap`.

Delayed allocation and EOF cleanup:
- `xfs_bmap_punch_delalloc_range` removes delalloc extents in a byte range, optionally returning zoned writeback reservations to an allocation context.
- `xfs_can_free_eofblocks` determines whether post-EOF preallocation or delalloc blocks should be freed.
- `xfs_free_eofblocks` removes delayed blocks or truncates post-EOF extents without updating on-disk file size.

Space management:
- `xfs_alloc_file_space` preallocates file space, respecting extent size hints, realtime allocation, transaction reservation limits, and always-cow inodes.
- `xfs_flush_unmap_range` writes and invalidates page cache over allocation-unit-aligned ranges before unmapping/shift operations.
- `xfs_free_file_space` flushes/invalidate, unmaps complete fsblocks, rounds big-RT allocations, zeroes partial block edges, and writes the EOF page when needed.

Range shifting:
- `xfs_prepare_shift` frees EOF blocks, flushes and invalidates the affected suffix, and cancels COW data so extent shifts do not leave COW records at wrong offsets.
- `xfs_collapse_file_space` frees the target range, prepares for shifting, then calls `xfs_bmap_collapse_extents` with transaction rolls until done.
- `xfs_insert_file_space` validates insert feasibility, prepares shifting, splits an extent at the insertion point, and shifts extents right through repeated deferred-finishing cycles.

Extent swapping:
- `xfs_swap_extents_check_format` validates quota IDs, fork formats, extent counts, attr fork layout constraints, and btree root compatibility before swapping.
- `xfs_swap_extent_flush` writes and invalidates page cache and verifies no cached pages remain.
- `xfs_swap_extent_rmap` performs extent exchange by unmapping/remapping ranges when rmapbt is enabled.
- `xfs_swap_extent_forks` swaps data forks directly when rmapbt is not used, fixes `i_nblocks`, delayed block accounting, and inode log flags.
- `xfs_swap_change_owner` fixes bmbt owner fields after fork swaps on v3 inode filesystems, rolling transactions on fallback logging.
- `xfs_swap_extents` orchestrates inode/pagecache locks, quota attachment, flushing, realtime restrictions, transaction allocation, format/mtime checks, rmap/direct swap, reflink/COW fork swapping, owner repair, sync commit, and cleanup.

Dependencies:
- XFS bmap/btree/defer/quota/reflink/rt/zoned subsystems, page cache writeback/invalidation, transaction reservations, block zeroout.

Risk notes:
- Many operations depend on callers holding `IOLOCK_EXCL` and sometimes `MMAPLOCK_EXCL`.
- Extent shift operations carefully cancel COW and flush aligned ranges to avoid races with writeback completion.
- `xfs_swap_extents` is a deprecated whole-file interface with explicit limitations for realtime groups.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_util.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_util.h

This header declares higher-level bmap utility interfaces.

Exports include:
- Realtime allocation hook `xfs_bmap_rtalloc`, returning `-EFSCORRUPTED` when realtime support is compiled out.
- Delalloc punching: `xfs_bmap_punch_delalloc_range`
- Getbmap output structure `struct kgetbmap` and `xfs_getbmap`
- Internal bmap helpers used by `xfs_bmap_util.c`
- File space operations: allocate, free, collapse, insert
- EOF block cleanup: `xfs_can_free_eofblocks`, `xfs_free_eofblocks`
- Extent swap: `xfs_swap_extents`
- Conversion/counting helpers: `xfs_fsb_to_db`, `xfs_bmap_count_leaves`, `xfs_bmap_count_blocks`
- Cache flushing helper: `xfs_flush_unmap_range`

Integration:
- Provides the bridge from ioctl/file-operation layers to core block mapping code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf.c

This file implements the XFS metadata buffer cache: buffer allocation, lookup, memory backing, read/write I/O, verification, delayed-write queues, LRU shrinker integration, and buffer target lifecycle.

Buffer lifetime and cache:
- `xfs_buf_alloc_backing_mem` backs buffers with kmalloc for small aligned sizes, folios for page-sized/power-of-two buffers, vmalloc fallback for larger/non-power-of-two buffers, or in-memory buftarg mappings.
- `xfs_buf_alloc` initializes lockref, semaphore, LRU/list heads, maps, counters, target/mount fields, and backing memory.
- Rhashtable lookup uses `_xfs_buf_obj_cmp`, keyed by starting disk address and total length.
- `xfs_buf_get_map` verifies sector alignment/range, gets a per-AG reference, looks up or inserts buffers, locks them, and clears stale I/O errors for non-read lookups.
- `xfs_buf_stale` marks buffers stale, removes delayed-write state, drops LRU ref, and removes from LRU.
- `xfs_buf_rele`, `xfs_buf_kill`, and `xfs_buf_destroy` manage lockref release, LRU placement, rhashtable removal, perag release, and final freeing.

Read path:
- `xfs_buf_read_map` gets a buffer, performs synchronous read if not done, or re-verifies cached contents when verifier ops are supplied.
- `xfs_buf_reverify` attaches missing verifier ops to already-read buffers and reruns read verification.
- `xfs_buf_readahead_map` attempts nonblocking async readahead, skipping in-memory buftargs.
- `xfs_buf_read_uncached` and `xfs_buf_get_uncached` create buffers outside the cache using `XFS_BUF_DADDR_NULL`.

Locking and pinning:
- `xfs_buf_trylock`, `xfs_buf_lock`, and `xfs_buf_unlock` wrap the buffer semaphore.
- Locking a stale pinned buffer forces the log to help unblock stale buffer reuse.
- `xfs_buf_wait_unpin` waits for pin count to drop before write submission.

I/O completion and error handling:
- `__xfs_buf_ioend` runs read verifiers, write completion callbacks, buffer log item completion, retry-state cleanup, and flag cleanup.
- `xfs_buf_ioend_handle_error` handles async write failures: retries first failures, tracks retry limits/timeouts, marks log items failed for transient failures, and forces shutdown on permanent metadata write failures.
- `xfs_buf_ioend_fail` simulates failed I/O by staling the buffer and completing it with `-EIO`.
- `xfs_bwrite` submits synchronous metadata writes and forces shutdown on error.
- `xfs_buf_submit` handles log shutdown, waits for unpin on writes, clears stale errors, runs write verifier callbacks, handles in-memory targets, and submits bios otherwise.
- `xfs_buf_submit_bio` builds bios for contiguous virtual buffer memory and splits by compound map segment.

Delayed write queues:
- `xfs_buf_delwri_queue` adds locked buffers to caller-managed delayed-write lists and takes a reference.
- `xfs_buf_delwri_queue_here` waits for buffers to leave any other delwri list before queuing locally for data-integrity work.
- `xfs_buf_delwri_submit_nowait` sorts by disk address, skips locked/pinned buffers, submits async writes, and leaves skipped buffers on the list.
- `xfs_buf_delwri_submit` synchronously submits all buffers and waits for completion.
- `xfs_buf_delwri_cancel` removes queued buffers and drops references.

Buftarg and reclaim:
- `xfs_init_buftarg` initializes rhashtable, LRU, readahead counter, I/O rate limit, and shrinker.
- `xfs_configure_buftarg` validates device block size, records filesystem sector geometry, capacity, and atomic write unit support.
- `xfs_alloc_buftarg` attaches a block device and optional DAX device, syncs blockdev pagecache, sets provisional sector sizes, and initializes the target.
- `xfs_buftarg_wait` waits for readahead and completion work.
- `xfs_buftarg_drain` frees all LRU buffers at teardown and warns if permanent write failures caused dirty metadata loss.
- Shrinker callbacks reclaim buffers by LRU reference aging while avoiding lock-order inversions through trylocks.

Verification helpers:
- `__xfs_buf_mark_corrupt` reports relationship-level corruption and stales the buffer.
- `xfs_verify_magic` and `xfs_verify_magic16` compare on-disk magic values against v4/v5 verifier tables.

Dependencies:
- Linux block bio APIs, rhashtable, list_lru/shrinker, folio/vmalloc memory, XFS log and buffer log item code, DAX, error injection and shutdown handling.

Risk notes:
- Async submission transfers buffer lock/reference ownership to I/O; callers need an extra reference to touch the buffer afterwards.
- Delayed-write lists are caller-synchronized, not internally synchronized.
- Metadata write error retry policy is central to preventing silent metadata loss; permanent failures force filesystem shutdown.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf.h

This header defines the XFS metadata buffer cache interface and core data structures.

Important definitions:
- Buffer flags: read/write/readahead/async/done/stale/write-fail, internal log-recovery/kmem/delwri flags, and lookup-only flags such as `XBF_INCORE`, `XBF_TRYLOCK`, and `XBF_LIVESCAN`.
- `struct xfs_buftarg`: abstracts a backing block device or in-memory target, including sector geometry, DAX handle, LRU/shrinker state, readahead counter, rate limit, atomic write units, and buffer hash table.
- `struct xfs_buf_map`: disk address, length, and lookup flags for one map segment.
- `struct xfs_buf_ops`: verifier callbacks and magic values.
- `struct xfs_buf`: cached metadata buffer with rhash key, lockref, LRU ref, semaphore, target/mount, backing address, completion, log item links, maps, pin count, error/retry state, verifier ops, and RCU freeing.

API surface:
- Buffer lookup/read/readahead: `xfs_buf_get_map`, `xfs_buf_read_map`, `xfs_buf_readahead_map`, inline single-map helpers.
- Uncached buffers: `xfs_buf_get_uncached`, `xfs_buf_read_uncached`.
- Reference/locking: `xfs_buf_hold`, `xfs_buf_rele`, `xfs_buf_trylock`, `xfs_buf_lock`, `xfs_buf_unlock`, `xfs_buf_relse`.
- I/O and error handling: `xfs_bwrite`, `xfs_buf_ioerror`, `xfs_buf_ioerror_alert`, `xfs_buf_ioend_fail`, `xfs_buf_mark_corrupt`.
- Utilities: `xfs_buf_offset`, `xfs_buf_zero`, `xfs_buf_stale`, `xfs_buf_daddr`, `xfs_buf_set_ref`, checksum helpers.
- Delayed write queues: queue, cancel, submit sync/async.
- Buftarg lifecycle/config: allocate, free, wait, drain, configure, init/destroy.
- Verification helpers: `xfs_buf_reverify`, `xfs_verify_magic`, `xfs_verify_magic16`.

Integration:
- This is the public internal interface for almost all XFS metadata I/O and verifier-aware buffer cache access.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf.h -->