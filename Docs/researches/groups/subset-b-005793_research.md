# Research Report: subset-b-005793

Work item: `subset-b-005793`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.c -->
## sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.c

Purpose: Implements the online scrub "xfile" abstraction, a private unlinked shmem file used as pageable temporary memory for scrub/repair staging data. It lets scrub code store large indexed arrays without requiring all data to remain resident, while avoiding user-visible file descriptors.

Important APIs and functions: `xfile_create` allocates `struct xfile`, creates a shmem kernel file with `VMA_NORESERVE`, assigns a dedicated inode lockdep class, and forces page-cache allocations to use `GFP_KERNEL` to avoid highmem pages. `xfile_destroy` restores the inode lock class and drops the shmem file. `xfile_load` and `xfile_store` copy byte ranges between caller buffers and shmem folios, translating absent folios on reads into zeroes. `xfile_get_folio` exposes a locked folio for a single-folio object, optionally allocating it with `XFILE_ALLOC`; `xfile_put_folio` unlocks and releases it. `xfile_seek_data` delegates to `SEEK_DATA`, and `xfile_discard` truncates a shmem range.

Control flow: Create returns a single handle that callers must serialize. Load/store validate `MAX_RW_COUNT` and superblock maxbytes, enter NOFS allocation context, walk page-sized or folio-sized chunks via `shmem_get_folio`, check mapping writeback errors, copy data, and release folios. Store grows `i_size` before SGP_CACHE allocation and marks written folios dirty. Direct folio access similarly validates bounds, gets a folio in SGP_READ or SGP_CACHE mode, rejects cross-folio spans, checks writeback errors, and marks allocated folios dirty to keep backing memory from disappearing after the last reference.

State and persistence: Data lives in a tmpfs/shmem page cache backing file, not in XFS metadata or user-visible namespace. It can be reclaimed/swapped by the VM and is destroyed by `fput` in `xfile_destroy`. Dirty folios are used to pin memory-object contents in cache semantics, not to persist filesystem state. `xfile_bytes` in the header observes backing blocks through `i_blocks`.

Dependencies and integration: Depends on Linux shmem APIs, folios, VFS file/inode helpers, NOFS context, scrub tracepoints, and scrub GFP policy. It is used by online scrub support such as xfarray-style temporary indexes, where XFS repair must avoid filesystem recursion while allocating memory.

Risks: Callers must provide all synchronization; there are no VFS inode/freezer locks for normal xfile access. Any short read/write, shmem allocation failure, writeback error, or oversize access is collapsed to `-ENOMEM` or `-EIO`, so consumers should treat failures as fatal memory staging failures. `xfile_discard` assumes nonzero count because it subtracts one from `pos + count`.

Test signals: Exercise create/destroy, sparse reads returning zeroes, writes crossing folio boundaries, allocation failure paths, writeback error propagation, single-folio object access, discard plus `seek_data`, and lockdep noise around private shmem inode locking during scrub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.h -->
## sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.h

Purpose: Declares the xfile interface used by online scrub code to treat a hidden shmem file as pageable temporary memory.

Important APIs and types: `struct xfile` contains the backing `struct file *`. Public functions are `xfile_create`, `xfile_destroy`, `xfile_load`, `xfile_store`, `xfile_discard`, `xfile_seek_data`, `xfile_get_folio`, and `xfile_put_folio`. `XFILE_MAX_FOLIO_SIZE` captures the largest page-cache folio size, and `XFILE_ALLOC` requests allocation in `xfile_get_folio`. `xfile_bytes` reports allocated backing bytes from `i_blocks`.

Control flow and integration: This header is the narrow contract between scrub data structures and the implementation in `scrub/xfile.c`. Consumers can either copy data in/out by offset or lock one folio directly when a staged object is guaranteed not to cross a folio boundary.

State and persistence: The only state visible to callers is the opaque handle and page-cache allocation accounting. No on-disk XFS state is represented here.

Dependencies: Requires VFS `struct file`, inode helpers, folio types, page size constants, and sector shift definitions from included kernel/XFS headers.

Risks: The header exposes the raw `file` field, so misuse by consumers could bypass xfile assumptions. Direct folio users must respect the no-cross-folio contract and always call `xfile_put_folio`.

Test signals: Build coverage with and without scrub consumers, direct folio get/put pairing checks, and tests that staged byte accounting changes after store/discard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfs_scrub.h -->
## sources/distributed-fs/ceph-client/fs/xfs/scrub/xfs_scrub.h

Purpose: Provides the top-level ioctl entry declarations for XFS online metadata scrub, with stubs when scrub support is disabled.

Important APIs: When `CONFIG_XFS_ONLINE_SCRUB` is enabled, declares `xfs_ioc_scrub_metadata(struct file *, void __user *)` and `xfs_ioc_scrubv_metadata(struct file *, void __user *)`. When disabled, both names are preprocessor stubs returning `-ENOTTY`.

Control flow and integration: This is included by ioctl-facing XFS code so callers can invoke scrub operations without scattering configuration checks. It controls whether scrub ioctls are live or report unsupported operation.

State and persistence: No state is stored here; persistence behavior is entirely in the enabled scrub implementation elsewhere.

Dependencies: Depends on kernel `struct file`, user pointer annotation, and the XFS Kconfig option.

Risks: The macro stubs must match function signatures closely enough for callers. Tests must cover disabled builds because no runtime symbol exists in that configuration.

Test signals: Compile matrix with `CONFIG_XFS_ONLINE_SCRUB=y/n`; ioctl tests should expect `ENOTTY` when disabled and dispatch into scrub when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfs_scrub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.c

Purpose: Implements XFS POSIX ACL get/set support by translating between Linux `struct posix_acl` and XFS root-namespace extended attributes (`SGI_ACL_FILE` and `SGI_ACL_DEFAULT`).

Important APIs and functions: `xfs_get_acl` loads an ACL xattr and converts it with `xfs_acl_from_disk`. `__xfs_set_acl` directly upserts or removes the ACL xattr and updates the inode ACL cache. `xfs_set_acl` is the VFS-facing setter that validates ACL size and updates file mode for access ACLs. `xfs_acl_set_mode` logs an inode core mode/ctime update. `xfs_forget_acl` invalidates cached ACLs when raw xattr paths bypass the ACL interface. Internal converters are `xfs_acl_from_disk` and `xfs_acl_to_disk`.

Control flow: Reads select the correct xattr name based on ACL type, call `xfs_attr_get`, convert big-endian disk entries to core tags/perms/uids/gids, and return NULL on `-ENOATTR` so the VFS can negative-cache. Writes reject default ACLs on nondirectories, serialize through the xattr change path, and only update cached ACLs after success. The public setter updates mode only after the ACL xattr succeeds to avoid changing mode when ENOSPC prevents ACL persistence.

State and persistence: ACLs persist as root namespace xattrs. Access ACL updates can also persist inode mode and ctime through a separate transaction. Cached ACL state in the VFS inode is synchronized after successful changes or explicitly forgotten after raw xattr mutation.

Dependencies and integration: Uses XFS attr APIs, transaction logging, inode locking expected by caller `i_mutex`, POSIX ACL helpers, idmapped mount mode update logic, XFS corruption reporting, and namespace constants from xattr headers.

Risks: Disk ACL corruption is detected through length/count/tag validation, but invalid uid/gid mappings are represented through init_user_ns conversions. Mode update happens after xattr update, so failure of the second transaction can leave an ACL change without the intended mode change. Raw xattr writers must call `xfs_forget_acl`.

Test signals: ACL round-trip tests, invalid disk ACL fuzzing, access ACL mode recalculation with idmapped mounts, default ACL rejection on nondirectories, ENOSPC during set, and cache invalidation through raw xattr paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.h

Purpose: Declares the XFS POSIX ACL interface and provides no-op/null substitutes when POSIX ACL support is not compiled.

Important APIs: With `CONFIG_XFS_POSIX_ACL`, exports `xfs_get_acl`, `xfs_set_acl`, `__xfs_set_acl`, and `xfs_forget_acl`. Without it, `xfs_get_acl` and `xfs_set_acl` are `NULL`, `__xfs_set_acl` returns success, and `xfs_forget_acl` is empty.

Control flow and integration: VFS inode operation setup can assign these names directly while remaining configuration-neutral. Internal XFS code can call `__xfs_set_acl` without additional ifdefs.

State and persistence: The enabled implementation persists ACLs as xattrs; the disabled header path intentionally does not persist or cache ACL state.

Dependencies: Forward-declares inode and posix ACL types and relies on VFS ACL integration in the implementation.

Risks: Disabled builds silently succeed for internal `__xfs_set_acl` calls, so callers must rely on VFS feature gating to prevent unsupported user-visible ACL operations.

Test signals: Compile coverage for ACL enabled/disabled configurations and inode operation registration checks for NULL operation pointers when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.c

Purpose: Implements XFS address-space operations for buffered and DAX files, including iomap-based read/writeback, write I/O completion, append-size updates, COW/unwritten conversion, zoned writeback, bmap, readahead, and swap activation.

Important APIs and functions: `xfs_setfilesize` transactionally advances on-disk file size after append writeback. `xfs_end_bio` queues iomap ioends to inode work; `xfs_end_io` sorts/merges and completes them. `xfs_end_ioend_write` handles write completion, COW cancellation/conversion, unwritten extent conversion, zoned completion, and page-cache completion. `xfs_map_blocks` validates/rebuilds cached writeback iomaps and converts delalloc extents. Zoned equivalents are `xfs_zoned_map_blocks`, `xfs_zoned_writeback_range`, and `xfs_zoned_writeback_submit`. Exported operation tables are `xfs_address_space_operations` and `xfs_dax_aops`.

Control flow: Writeback starts in `xfs_vm_writepages`, clears truncate state, and dispatches to normal or zoned iomap writepages. Normal mapping checks COW fork precedence, data/cow sequence counters, holes, delalloc conversion, and COW boundaries before adding folios to ioends. Submit can convert COW extents before bio submission and routes transaction-requiring completions to the unwritten workqueue. Completion updates metadata only in workqueue context when appending, COW, unwritten, zoned, or dontcache work is needed. Read paths use iomap read ops, optionally wrapping bios in ioends for integrity checksum completion.

State and persistence: Persists file size, extent state transitions from delayed/unwritten/COW to real data fork mappings, zoned allocation completion state, and page writeback status. It clears stale delalloc mappings on errors to keep block accounting correct. DAX writeback delegates to `dax_writeback_mapping_range`.

Dependencies and integration: Heavily integrates with iomap, XFS bmap, reflink, zone allocation, inodegc, realtime groups, block integrity, page cache, swapfile activation, and XFS trace/error injection. The operation tables plug into the VFS address_space for regular and DAX inodes.

Risks: Races around COW fork changes, truncate, direct I/O, and writeback mapping reuse are mitigated by page locks and fork sequence checks; regressions here can corrupt extents or leave stale delalloc. Error handling must punch delalloc on failed COW writeback. Zoned writeback requires open-zone lifetime pairing and correct append-sector recording. Swap activation must flush inodegc before checking shared extents.

Test signals: Buffered writeback under ENOSPC/EIO, reflink COW writeback and cancellation, unwritten extent conversion, append file-size persistence, DAX writeback, bmap refusal for reflink/realtime swap use, zoned inode writeback, block-integrity reads, and swapfile activation races with inodegc.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.h

Purpose: Declares XFS address-space operation tables and the small set of helper functions used outside `xfs_aops.c`.

Important APIs: Exports `xfs_address_space_operations`, `xfs_dax_aops`, `xfs_setfilesize`, and `xfs_end_bio`.

Control flow and integration: Super/inode setup uses the operation tables to wire regular and DAX mapping behavior into VFS. iomap/block completion paths use `xfs_end_bio` to defer ioend processing to XFS workqueues.

State and persistence: The table declarations indirectly control read/writeback persistence behavior; `xfs_setfilesize` is the explicit on-disk file-size persistence helper.

Dependencies: Requires XFS inode/off_t types and kernel `struct bio`/address_space operation declarations from surrounding includes.

Risks: Any signature drift breaks VFS operation wiring or iomap completion callbacks. DAX and non-DAX operation tables must remain behaviorally consistent where they share swap activation semantics.

Test signals: Build/link coverage, mount regular and DAX filesystems, buffered write append tests invoking `xfs_setfilesize`, and read/write bio completion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_inactive.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_inactive.c

Purpose: Removes an inode's entire attribute fork during inode inactivation, including invalidating remote attribute value buffers and truncating attr fork blocks safely.

Important APIs and functions: Public `xfs_attr_inactive` orchestrates transaction allocation, inode locking, attr tree invalidation, truncation, and fork removal. Helpers `xfs_attr3_rmt_stale`, `xfs_attr3_leaf_inactive`, `xfs_attr3_node_inactive`, and `xfs_attr3_root_inactive` walk leaf/node structures and stale remote value buffers.

Control flow: The public function first checks for an attr fork under shared lock, allocates an attr invalidation transaction, upgrades to exclusive inode lock, joins the inode, and if attr blocks exist, invalidates the attr tree while leaving the root. It truncates all but the root, invalidates the root buffer, truncates to zero, removes the attr fork, and commits. On cancellation or even when no persistent removal occurs, it zaps the in-core attr fork before dropping the lock.

State and persistence: Persists deletion of attr fork extents and inode fork metadata through transactions. Remote attr value buffers are never logged, so they are marked stale before block unmapping. The root block is reinitialized before truncation so a crash during removal sees an empty leaf instead of entries pointing at freed remote blocks.

Dependencies and integration: Uses attr leaf/node parsers, bmap read/truncate, buffer invalidation, transaction rolling, quota assumptions, attr geometry, and health marking for corrupt dir/attr forks.

Risks: Recursive node traversal must respect `XFS_DA_NODE_MAXDEPTH`; corrupt magic or empty/invalid structures mark the attr fork sick. Transaction rolling and buffer release ordering avoid holding buffers across log operations. A failure still destroys in-core attr fork state, so callers must tolerate loss of cached fork after errors.

Test signals: Inactivation of shortform, leaf, node, and remote-value attrs; crash-recovery during attr fork removal; corrupt attr tree depth/magic; remote value stale buffer invalidation; and failure paths confirming in-core fork zapping and no buffer lock leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_inactive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.c

Purpose: Implements logged extended-attribute deferred operations using ATTRI intent and ATTRD done log items, including parent pointer variants, name/value buffer lifetime management, recovery validation, replay, and relogging.

Important APIs and functions: `xfs_attr_defer_add` creates deferred attr work and maps high-level set/remove/replace operations to log op flags. `xfs_attr_create_intent`, `xfs_attr_create_done`, `xfs_attr_finish_item`, `xfs_attr_abort_intent`, `xfs_attr_cancel_item`, `xfs_attr_recover_work`, and `xfs_attr_relog_intent` implement `xfs_attr_defer_type`. ATTRI/ATTRD item ops format, size, release, match, and connect done items back to intent items. Recovery entry points are `xlog_recover_attri_commit_pass2` and `xlog_recover_attrd_commit_pass2`.

Control flow: Deferred attr work captures a `struct xfs_da_args` and an operation state machine. For logged operations, the create-intent path allocates a refcounted contiguous name/value object, initializes an ATTRI with an intent id, fills inode/op/filter/length fields, and logs format plus name/new-name/value/new-value iovecs as needed. Finish calls `xfs_attr_set_iter`; if the delayed attr state is not done, it returns `-EAGAIN` so defer processing rolls transactions. Done items release the ATTRI reference. Recovery validates format, op/filter namespace, iovec counts and lengths, parent pointer values, inode numbers, feature flags, and attr names before reconstructing `xfs_attr_intent` and replaying it under a recovery transaction.

State and persistence: ATTRI records describe unfinished xattr mutations in the log; ATTRD records cancel completed intents. The refcounted name/value object is shared by deferred work and log items to avoid repeated allocation/copying. Replay persists attr fork changes and parent pointer updates through normal attr state machines and transactions.

Dependencies and integration: Integrates with XFS defer ops, xlog recovery intent framework, attr state machine, parent pointer validation, inode recovery iget, transaction reservations, attr geometry, log iovec formatting, AIL reference lifetime, and error injection.

Risks: Log validation is security-critical because recovery allocates and replays operations from disk log data. Parent pointer ops require generation checks and exact value sizes. Refcount ordering between committed/unpinned ATTRI and ATTRD release is subtle. Returning `-EAGAIN` incorrectly can livelock or lose multi-transaction attr progress.

Test signals: Logged xattr set/remove/replace, parent pointer set/remove/replace, crash after ATTRI before ATTRD, relogging long-running intents, malformed log iovec counts/lengths/names/filters, inode generation mismatch, LARP error injection, and memory lifetime checks for shared name/value buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.h

Purpose: Defines in-core structures and public entry points for logged extended-attribute intent/done items.

Important APIs and types: `struct xfs_attri_log_nameval` stores name, optional new name, value, optional new value, and a refcount, with payload bytes immediately following the struct. `struct xfs_attri_log_item` wraps an XFS log item, refcount, shared name/value buffer, and on-disk log format. `struct xfs_attrd_log_item` references the matching ATTRI and stores done format. `enum xfs_attr_defer_op` names set/remove/replace, and `xfs_attr_defer_add` queues work.

Control flow and integration: The header is consumed by attr mutation code to queue deferred logged work and by log infrastructure to allocate ATTRI/ATTRD caches. It exposes only the queuing API; item operation details remain in `xfs_attr_item.c`.

State and persistence: Structures mirror log intent state that survives crashes until canceled by ATTRD. Shared name/value state is in-core but copied from/to log iovecs.

Dependencies: Requires XFS mount/log format definitions, `struct kvec`, refcounting, and attr state definitions from broader XFS headers.

Risks: Layout and length semantics must remain compatible with log recovery. New operation types must update validation, formatting, recovery, and this enum together.

Test signals: Compile/link of cache users, intent format size expectations, and operation coverage through `xfs_attr_defer_add` callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_list.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_list.c

Purpose: Implements listing extended attributes from XFS in shortform, leaf, and node formats with cursor-based continuation and corruption checks.

Important APIs and functions: `xfs_attr_list` is the external entry that locks the attr fork and delegates to `xfs_attr_list_ilocked`. `xfs_attr_list_ilocked` chooses shortform, leaf, or node path. `xfs_attr_shortform_list` handles inline attrs and sorting for partial buffers. `xfs_attr_node_list_lookup` descends the attr btree by hash and validates cursor targets. `xfs_attr_node_list`, `xfs_attr_leaf_list`, and exported `xfs_attr3_leaf_list_int` emit leaf entries through the caller's `put_listent` callback.

Control flow: Shortform listing returns entries directly when the buffer can hold all entries or when scanning with a zero-size/search callback; otherwise it builds a sorted hash/entry-number array to support stable cursor continuation. Leaf/node listing validates the caller cursor, redoes lookup from the btree root when necessary, processes leaf entries in hash order, follows forward leaf links, and updates cursor hash/offset as entries are emitted.

State and persistence: Does not mutate persistent metadata. It reads in-core or on-disk attr fork extents and updates only the caller's listing cursor and context flags such as `seen_enough`, `dupcnt`, and `resynch`.

Dependencies and integration: Uses attr fork locks, extent loading, attr leaf/node verifiers, name validation, hash functions, health marking, tracing, and caller-provided namespace/value emission callbacks.

Risks: Cursor validation is complex; stale or malicious cursor block/hash values must not return wrong entries or trust corrupt blocks. Shortform pointer bounds and namespace/name checks protect against malformed inline attrs. Incomplete attr entries are hidden unless context explicitly allows them.

Test signals: Listing all attrs in one buffer, partial-buffer continuation with duplicate hashes, shortform-to-leaf transitions, corrupted shortform/leaf/node blocks, incomplete attr filtering, and cursor resync after tree changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bio_io.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_bio_io.c

Purpose: Provides a synchronous metadata-oriented block-device read/write helper that can handle both linear and vmalloc-backed buffers.

Important APIs: `xfs_rw_bdev` performs a read or write to a block device at a sector/count/data tuple with `REQ_META | REQ_SYNC`. `bio_max_vecs` computes bio vector demand from byte count.

Control flow: Non-vmalloc buffers are passed to `bdev_rw_virt`. Vmalloc buffers allocate a bio, add vmalloc chunks until full, chain and submit prior bios as needed, then wait for the final bio. After reads, it invalidates the kernel vmap range so CPU mappings see device data.

State and persistence: Writes synchronously persist caller-provided metadata buffer contents to the block device; reads fill the caller buffer. The helper itself stores no long-lived state.

Dependencies and integration: Uses Linux block layer bios, vmalloc helpers, bio chaining, `submit_bio_wait`, and block-device direct virtual I/O helper. It is suitable for XFS metadata paths needing synchronous device access outside the normal buffer cache.

Risks: Correct behavior depends on bio chaining and chunk accounting; a zero `bio_add_vmalloc_chunk` triggers a new chained bio. The final `if (op == REQ_OP_READ)` comparison is fragile because `op` has flags ORed into it, so tests should verify read invalidation behavior or inspect expected semantics.

Test signals: Synchronous read/write with kmalloc and vmalloc buffers, multi-bio vmalloc transfers, error propagation from `submit_bio_wait`, and read-side vmap invalidation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bio_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.c

Purpose: Implements BUI/BUD logged intent handling for deferred bmap updates, allowing map/unmap operations to be replayed after crashes.

Important APIs and functions: `xfs_bmap_defer_add` queues a `struct xfs_bmap_intent`. `xfs_bui_log_space` and `xfs_bud_log_space` calculate reservation sizes. The defer type `xfs_bmap_update_defer_type` uses create-intent/done, finish, cancel, recover, and relog callbacks. Recovery entry points are `xlog_recover_bui_commit_pass2` and `xlog_recover_bud_commit_pass2`.

Control flow: Queueing takes a passive AG/RTG intent reference and pre-adjusts `i_delayed_blks` for map intents. Intent creation sorts by inode if requested, records owner/startblock/startoff/length/type/fork/realtime/unwritten flags in one BUI extent slot, and logs the item. Finish calls `xfs_bmap_finish_one`; if an unmap remains partially unfinished, it returns `-EAGAIN` for transaction rolling. Cancel reverses delayed block accounting and drops group intent refs. Recovery validates the logged extent, reconstructs a bmap intent, obtains inode and group state, allocates a transaction, verifies realtime flag consistency, reserves incore extent changes, finishes the recovered intent, and commits captured deferred work.

State and persistence: BUI persists unfinished bmbt map/unmap work in the log; BUD cancels it when complete. In-core state tracks BUI refcounts, next extent index, group intent refs, and temporary delayed-block accounting. Persistent replay updates inode data/attr fork mappings and related rmap/refcount side effects via deferred operations.

Dependencies and integration: Integrates with XFS log item ops, defer framework, AIL, bmap btree updates, inode recovery, AG/RT group intent accounting, transaction reservations, rmap/realtime validation, and corruption reporting.

Risks: Only `XFS_BUI_MAX_FAST_EXTENTS == 1` is supported, so format validation rejects other counts. Delayed block pre-accounting must be undone exactly once. Recovered realtime flags must match the target fork or replay could corrupt the wrong address space. Refcount ordering between BUI unpin/release and BUD commit is subtle.

Test signals: Crash recovery after BUI before BUD, map and unmap intents, partial unmap `-EAGAIN` loops, realtime and attr-fork flags, malformed log records, relogging, and delayed-block accounting under out-of-place writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.h

Purpose: Defines in-core BUI/BUD log item structures and public helpers for deferred bmap update logging.

Important APIs and types: `XFS_BUI_MAX_FAST_EXTENTS` is currently one. `struct xfs_bui_log_item` contains the log item, refcount, next extent counter, and BUI format. `xfs_bui_log_item_sizeof` computes variable-sized allocation needs. `struct xfs_bud_log_item` links a done item to its BUI. Exports the BUI/BUD slab caches, `xfs_bmap_defer_add`, and log space calculators.

Control flow and integration: Higher-level bmap code allocates `struct xfs_bmap_intent` and queues it through `xfs_bmap_defer_add`; the implementation handles log formatting and recovery.

State and persistence: Structures represent redo intent and done records that persist in the journal until replayed or canceled.

Dependencies: Requires XFS log format definitions and transaction/defer users.

Risks: The header comment states the crash contract: intent in the first transaction and done with actual bmbt update. Any caller violating that ordering risks unrecoverable mapping changes.

Test signals: Log reservation sizing, one-extent intent assumptions, and BUI/BUD recovery ordering tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.c

Purpose: Provides higher-level block mapping utilities around XFS extent state: file extent reporting, delayed allocation punching, EOF preallocation cleanup, fallocate/punch/collapse/insert operations, zeroing, extent counting, and legacy swapext support.

Important APIs and functions: `xfs_getbmap` reports extents for getbmapx. `xfs_bmap_punch_delalloc_range` removes delalloc mappings without a transaction. `xfs_can_free_eofblocks` and `xfs_free_eofblocks` decide and execute post-EOF cleanup. `xfs_alloc_file_space`, `xfs_free_file_space`, `xfs_collapse_file_space`, `xfs_insert_file_space`, and `xfs_flush_unmap_range` implement file-space manipulation. `xfs_swap_extents` swaps data extents between a target and temporary inode. Utility helpers include `xfs_fsb_to_db`, `xfs_zero_extent`, `xfs_bmap_count_leaves`, and `xfs_bmap_count_blocks`.

Control flow: `xfs_getbmap` validates flags, locks I/O and fork state, optionally flushes data fork delalloc, loads extents, emits holes and extents, and splits records around shared/unshared reflink regions. Space allocation loops with transaction reservations and preallocation flags. Free-space punching flushes/invalidate page cache, unmaps full blocks, and zeroes partial blocks without extending EOF. Collapse/insert prepare by freeing EOF blocks, flushing from an aligned boundary, canceling COW, then shifting extents transactionally with defer rolls. Swapext locks both files and page caches, flushes both, validates format/timestamps/realtime/quota compatibility, then either remaps extents with rmapbt or swaps forks and fixes bmbt owners.

State and persistence: Mutates inode extent maps, delayed block counters, preallocation flags, inode block counts, COW forks, and bmbt block owners through transactions. Flush/invalidate paths synchronize page cache with mapping changes. `xfs_getbmap` is read-only except for required writeback flushing.

Dependencies and integration: Integrates with bmap core, iomap zeroing, reflink, realtime and zoned allocation, quota attachment, transaction reservations, inodegc/page cache, rmapbt, bmbt owner changes, VFS locking, and tracepoints.

Risks: Extent shift operations are race-sensitive with COW writeback and require IOLOCK/MMAPLOCK exclusivity plus aligned cache invalidation. Partial block punch must zero correctly without growing i_size. Swapext is deprecated-style and has many invariants; format, owner, quota, timestamp, rmap, and realtime-group restrictions are critical. EOF cleanup avoids updating on-disk size to prevent NULL-file exposure after crash.

Test signals: getbmap with holes/delalloc/shared/unwritten extents and attr/COW forks; fallocate prealloc loops with ENOSR; punch hole partial-block zeroing; collapse/insert under reflink/COW and realtime units; EOF block cleanup for prealloc/append files; swapext with rmapbt, btree forks, reflink flags, timestamp mismatch, and crash recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.h

Purpose: Declares kernel-only higher-level XFS bmap utility interfaces used by file operations, writeback, ioctl, and maintenance paths.

Important APIs and types: Declares realtime allocation hook `xfs_bmap_rtalloc`, delalloc punch, `struct kgetbmap`, `xfs_getbmap`, extent alignment helpers from bmap core, preallocation/hole-punch/collapse/insert interfaces, EOF block cleanup, `xfs_swap_extents`, block address conversion, extent counting, and `xfs_flush_unmap_range`.

Control flow and integration: This header connects many subsystems to bmap utility behavior: address-space error cleanup uses delalloc punching, ioctl paths use getbmap and swapext, file space operations use alloc/free/collapse/insert, and inode cleanup uses EOF block helpers.

State and persistence: Declared functions can mutate persistent extent maps and inode metadata; the header itself stores no state.

Dependencies: Forward-declares bmap, inode, mount, transaction, and zoned allocation types. Provides an inline `xfs_bmap_rtalloc` returning `-EFSCORRUPTED` when realtime support is disabled.

Risks: The disabled realtime inline intentionally treats RT allocation attempts as corruption, so callers must feature-gate RT paths. Function contracts generally assume caller-held locks that are documented in implementation rather than type signatures.

Test signals: Compile matrix with/without `CONFIG_XFS_RT`, call sites meeting locking assumptions, and public file-operation paths invoking each declared mutator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_buf.c

Purpose: Implements the XFS metadata buffer cache and buffer target layer: cached/uncached buffer lookup, backing memory allocation, synchronous/asynchronous metadata I/O, verification, stale handling, delayed-write queues, LRU/shrinker reclaim, and buftarg initialization/destruction.

Important APIs and functions: Buffer acquisition APIs are `xfs_buf_get_map`, `xfs_buf_read_map`, `xfs_buf_readahead_map`, `xfs_buf_get_uncached`, and `xfs_buf_read_uncached`. Lifetime/locking APIs include `xfs_buf_hold`, `xfs_buf_rele`, `xfs_buf_trylock`, `xfs_buf_lock`, `xfs_buf_unlock`, and `xfs_buf_stale`. I/O APIs include `_xfs_buf_read`, `xfs_bwrite`, `xfs_buf_submit`, `xfs_buf_submit_bio`, `xfs_buf_iowait`, and completion helpers. Delayed write APIs include `xfs_buf_delwri_queue`, `xfs_buf_delwri_queue_here`, `xfs_buf_delwri_submit_nowait`, `xfs_buf_delwri_submit`, and `xfs_buf_delwri_cancel`. Buftarg APIs include `xfs_alloc_buftarg`, `xfs_configure_buftarg`, `xfs_init_buftarg`, `xfs_buftarg_wait`, `xfs_buftarg_drain`, and `xfs_free_buftarg`.

Control flow: Lookup verifies sector/range bounds, obtains a per-AG reference when relevant, tries an RCU rhashtable cache hit, locks the buffer, clears stale external state if needed, or allocates/inserts a new locked buffer with kmalloc/folio/vmalloc/tmpfs backing. Reads either submit I/O or reverify cached data; read errors stale the buffer and translate bad CRC to corruption. Writes wait for pins, verify metadata, handle log shutdown, and submit bios over one or more maps. Bio completion records errors, defers async completion to the mount buffer workqueue, runs read/write verifiers and buffer log item completion, retries async metadata write failures according to error policy, or forces shutdown for permanent metadata I/O failures.

State and persistence: Persistent effects are metadata reads/writes to buftarg block devices. In-core state includes rhashtable cache entries, lockref references, LRU references, stale/done/write-fail/delwri flags, pin counts, buffer log item associations, verifier ops, per-target readahead counters, and shrinker/LRU state. Stale buffers are removed from cache visibility and freed when references drain. Delayed-write queues hold extra refs until submitted or canceled.

Dependencies and integration: Integrates with block layer bios, DAX device discovery, list_lru/shrinker, rhashtable, XFS log shutdown and AIL/buf items, per-AG references, memory-backed buftargs, error injection/config, metadata verifiers/checksums, block device atomic write geometry, and mount workqueues.

Risks: Lock ordering between buffer semaphores, lockref lock, and LRU locks is delicate. Async I/O transfers reference/lock ownership, so touching buffers after submission without a hold is unsafe. Metadata write error retry policy must not lose dirty metadata silently; permanent failures force shutdown and later drain reports repair guidance. Stale pinned buffers can require log forcing to avoid AIL stalls. Missing verifier ops on CRC filesystems are warnings except for known recovery/repair cases.

Test signals: Cache hit/miss races, stale buffer reuse, read verifier failures and CRC translation, async write retry/permanent failure policies, delwri submit/cancel leaks, LRU shrink/drain, multi-map bio splitting, uncached reads, memory buftarg behavior, log shutdown I/O failure, per-AG ref release, and DAX/atomic write configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_buf.h

Purpose: Defines XFS metadata buffer and buffer target types, flags, verifier contracts, and public buffer cache/I/O APIs.

Important APIs and types: `struct xfs_buftarg` abstracts a block/memory target with device, DAX, sector geometry, atomic write units, LRU, readahead counter, rate limiting, and rhashtable. `struct xfs_buf_map` identifies disk ranges. `struct xfs_buf_ops` provides verifier callbacks and magic values. `struct xfs_buf` stores cache key, length, lockref, semaphore, flags, LRU/list links, target/mount/perag, data address, I/O completion, log item linkage, maps, pin count, errors, retry state, iodone callback, and verifier ops. Public APIs cover get/read/readahead, uncached buffers, hold/release, lock/unlock, writes/errors/corruption, delwri queues, LRU ref control, checksums, buftarg lifecycle/configuration, and magic verification.

Control flow and integration: Inline wrappers create single-map operations for common get/read/readahead/incore calls. Flags distinguish operation intent (`XBF_READ`, `XBF_WRITE`, `XBF_ASYNC`), buffer state (`XBF_DONE`, `XBF_STALE`, `XBF_WRITE_FAIL`), internal ownership (`_XBF_KMEM`, `_XBF_DELWRI_Q`), and lookup modifiers (`XBF_INCORE`, `XBF_TRYLOCK`, `XBF_LIVESCAN`).

State and persistence: The definitions describe all in-core state needed to mediate persistent metadata I/O. Verifier and checksum helpers protect on-disk metadata integrity.

Dependencies: Pulls Linux list, mm, fs, DAX, uio, list_lru, and lockref primitives plus XFS core scalar types.

Risks: Flags used only as arguments must not leak into persistent buffer state. `xfs_buf_islocked` reads semaphore internals, so kernel semaphore semantics matter. Callers must pair lock/release helpers correctly and honor async submission ownership rules documented in implementation.

Test signals: Static/build coverage for flag tracing, struct layout expectations, verifier magic checks, wrapper behavior, and call-site audits for lock/ref pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf.h -->
