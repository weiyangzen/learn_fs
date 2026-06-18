# Group Research: group_1059_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_stack_user_c_so_028a9eaae6b7

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/stack_user.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/stack_user.c

Implements the OCFS2 `"user"` cluster stack plugin, bridging OCFS2 cluster operations to kernel `fs/dlm` lockspaces and, for older userspace stacks, the `/dev/ocfs2_control` misc-device protocol.

Key responsibilities:
- Exposes `/dev/ocfs2_control` with a strict text protocol: read supported tag `T01`, write `T01`, then send `SETN`, `SETV`, and later `DOWN` recovery notifications.
- Maintains mounted live connections in `ocfs2_live_connection_list`, protected by `ocfs2_control_lock`, so userspace node-down messages can call each connection’s recovery handler.
- Tracks global control-daemon state through `ocfs2_control_opened`, `ocfs2_control_this_node`, and `running_proto`.
- Registers `ocfs2_user_plugin` and implements `struct ocfs2_stack_operations`.

Important behavior:
- `ocfs2_control_open/read/write/release()` implement per-open handshake state, exact command-size parsing, private configuration, and close cleanup.
- If the last valid control daemon fd closes while controlled live connections remain, `ocfs2_control_release()` logs a fatal condition and calls `emergency_restart()`.
- `user_dlm_lock()` and `user_dlm_unlock()` wrap `dlm_lock()`/`dlm_unlock()`, attach LVB storage, route AST/BAST callbacks to OCFS2, and force `DLM_LKF_NODLCKWT`.
- `user_plock()` dispatches POSIX lock requests to `dlm_posix_cancel/get/unlock/lock`.
- Without old `dlm_controld`, protocol negotiation uses a DLM `version_lock` resource and its LVB: first mounter writes max protocol under EX, then downconverts to PR; later mounters read and validate it.
- DLM lockspace callbacks trigger OCFS2 recovery for failed slots and publish local node/slot identity when recovery completes.
- `user_cluster_connect()` creates an exclusive DLM lockspace, detects old control-daemon behavior via `ops_rv == -EOPNOTSUPP`, attaches the live connection, negotiates protocol, and waits for local node discovery in callback mode.
- `user_cluster_disconnect()` unlocks the version lock, releases the DLM lockspace, and removes/freezes live-connection state.

Integration points:
- Selected by `stackglue.c` for non-classic cluster stacks.
- Uses kernel DLM APIs, DLM plock APIs, lockspace recovery callbacks, OCFS2 locking protocol callbacks, and ocfs2-tools/dlm_controld conventions.

Risk areas:
- Control-daemon lifetime is safety-critical; unexpected daemon loss while mounted forces restart.
- The control text protocol is intentionally strict about command size and ordering.
- Protocol-version LVB negotiation must stay compatible across all nodes.
- Live connection teardown must prevent userspace recovery messages from touching freed mount state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/stack_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/stackglue.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/stackglue.c

Implements the OCFS2 cluster-stack glue layer. It selects one active cluster stack plugin, exposes generic cluster/DLM APIs to filesystem code, manages module references, and provides sysfs/sysctl controls for stack selection and heartbeat helper path.

Key responsibilities:
- Maintains registered stack plugins in `ocfs2_stack_list`, protected by `ocfs2_stack_lock`.
- Tracks the single active plugin in `active_stack`; mixed active stacks are rejected.
- Maps the classic stack label to `"o2cb"` and any non-classic label to `"user"`.
- Auto-loads `ocfs2_stack_<plugin>` modules on demand.
- Registers `/sys/fs/ocfs2` attributes and `/proc/sys/fs/ocfs2/nm/hb_ctl_path`.

Important exported APIs:
- Plugin lifecycle: `ocfs2_stack_glue_register()`, `ocfs2_stack_glue_unregister()`.
- Protocol setup: `ocfs2_stack_glue_set_max_proto_version()`.
- DLM wrappers: `ocfs2_dlm_lock()`, `ocfs2_dlm_unlock()`, status/LVB helpers, and `ocfs2_dlm_dump_lksb()`.
- Cluster lifecycle: `ocfs2_cluster_connect()`, `ocfs2_cluster_connect_agnostic()`, `ocfs2_cluster_disconnect()`, `ocfs2_cluster_hangup()`, `ocfs2_cluster_this_node()`.
- POSIX locks: `ocfs2_stack_supports_plocks()`, `ocfs2_plock()`.

Important behavior:
- `ocfs2_cluster_connect()` validates group length and locking protocol, allocates `ocfs2_cluster_connection`, pins/selects the stack, then calls plugin `connect`.
- `ocfs2_cluster_disconnect()` calls plugin `disconnect`, frees the connection on success, and drops the stack reference unless heartbeat hangup is pending.
- `ocfs2_cluster_hangup()` runs the configured helper as `-K -u <uuid>` and then drops the pending stack reference.
- Sysfs exposes max locking protocol, loaded plugins, active plugin, selected cluster stack, and DLM recovery callback support.
- `cluster_stack` can be changed only when no active stack is mounted.

Integration points:
- Mount/DLM glue code uses this as the stack-independent cluster interface.
- Stack plugins such as `stack_user.c` and the classic O2CB stack register here.
- `super.c` uses exported `ocfs2_kset` for per-device sysfs directories.

Risk areas:
- Active stack state and module references must stay synchronized across connect/disconnect/hangup.
- The selected stack label is global while active.
- `ocfs2_dlm_dump_lksb()` assumes the active stack provides the debug hook.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/stackglue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/stackglue.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/stackglue.h

Defines the public OCFS2 cluster-stack abstraction shared by filesystem code and stack plugins.

Key contents:
- Defines stack-independent limits `GROUP_NAME_MAX` and `CLUSTER_NAME_MAX`.
- Defines `struct ocfs2_protocol_version`, the inter-node locking protocol version.
- Defines `struct ocfs2_dlm_lksb`, a union large enough for O2DLM and fs/dlm lock status blocks plus LVB storage.
- Defines `struct ocfs2_locking_protocol`, the callback table for lock AST, blocking AST, and unlock AST notifications.
- Defines `struct ocfs2_cluster_connection`, carrying group/cluster names, negotiated version, callbacks, lockspace, and stack-private data.
- Defines `struct ocfs2_stack_operations`, the plugin vtable for connect/disconnect, node identity, DLM operations, optional plocks, and optional lock dumping.
- Defines `struct ocfs2_stack_plugin`, the stack registration object.

Important API contracts:
- `connect()` must not return until node-down notifications and locking requests are ready.
- `disconnect()` must not return while the stack can still reference the connection.
- DLM wrappers pass callbacks indirectly through the connection protocol and `ocfs2_dlm_lksb`.
- `plock` is optional and callers must check support.
- `DLM_LKF_LOCAL` is locally faked because the public DLM constants header lacks it.

Integration points:
- Included by OCFS2 DLM glue, mount logic, stack plugins, and user-stack code.
- Hides stack-specific lock-status layout from most filesystem code.

Risk areas:
- The lock status union must remain large enough for supported stacks.
- Protocol negotiation depends on all stacks seeing the same `sp_max_proto`.
- Callback lifetime semantics are strict; violating them can break cluster recovery or locking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/stackglue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/suballoc.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/suballoc.c

Implements OCFS2 suballocation for metadata blocks, dinodes, and global clusters. It manages chain allocator inodes, group descriptors, bitmap searches, reservation contexts, block group growth, slot stealing, free paths, reclaim, and allocator locking before extent growth.

Key responsibilities:
- Validate and read group descriptors, including ECC, signature, generation, parent dinode, chain index, free counts, bitmap size, and discontiguous extent-list sanity.
- Reserve allocation contexts for metadata blocks, new inodes, local/global cluster allocation, and local allocator refill.
- Grow allocator inodes by creating contiguous or discontiguous block groups.
- Search allocation chains and group bitmaps for clear bits while respecting JBD2 committed-data copies.
- Claim metadata blocks, dinodes, and clusters, updating allocator dinode counts and group bitmaps inside journal transactions.
- Free suballocator bits, dinodes, and clusters, including undo-buffer handling for global bitmap changes.
- Reclaim completely unused non-global suballocator block groups back to the global bitmap.
- Provide helper APIs for inode-bit testing and allocator reservation before extent-tree mutation.

Important behavior:
- `ocfs2_reserve_suballoc_bits()` locks a system allocator inode, ensures enough free bits, and optionally grows it by allocating a new block group.
- `ocfs2_block_group_alloc()` reserves global clusters, formats a group descriptor, links it into the smallest chain, updates allocator inode size/counts, and records the last allocation group.
- Discontiguous block groups store extents in `bg_list`; allocation results are translated back to physical block numbers through `ocfs2_bg_discontig_fix_result()`.
- `ocfs2_test_bg_bit_allocatable()` checks the live bitmap and journal committed copy to avoid reusing blocks freed by an uncommitted transaction.
- `ocfs2_reserve_clusters_with_limit()` prefers local allocation when appropriate, falls back to the global bitmap, and retries after truncate-log freeing once.
- `ocfs2_claim_suballoc_bits()` tries the last-group hint, then the best free chain, then other chains, and can fall back to discontiguous main-bitmap allocation.
- `ocfs2_search_chain()` may relink a reasonably empty group to the chain head to improve future locality.
- `ocfs2_find_new_inode_loc()` supports find-only reservation; `ocfs2_claim_new_inode_at_loc()` later claims the exact location.
- `_ocfs2_free_suballoc_bits()` clears bitmap bits, updates chain/dinode counters, and may call `_ocfs2_reclaim_suballoc_to_main()` for empty non-global groups.
- `ocfs2_lock_allocators()` reserves data and metadata allocators before extent growth so callers avoid taking allocator locks while holding an active journal handle.
- `ocfs2_test_inode_bit()` dirty-reads the target dinode for suballocator location, locks the allocator inode, then checks the relevant bitmap bit.

Important exported APIs:
- Reservation: `ocfs2_reserve_new_metadata_blocks()`, `ocfs2_reserve_new_metadata()`, `ocfs2_reserve_new_inode()`, `ocfs2_reserve_clusters()`, `ocfs2_reserve_cluster_bitmap_bits()`.
- Claiming: `ocfs2_claim_metadata()`, `ocfs2_claim_new_inode()`, `ocfs2_find_new_inode_loc()`, `ocfs2_claim_new_inode_at_loc()`, `ocfs2_claim_clusters()`, `__ocfs2_claim_clusters()`.
- Freeing: `ocfs2_free_suballoc_bits()`, `ocfs2_free_dinode()`, `ocfs2_free_clusters()`, `ocfs2_release_clusters()`.
- Validation/helpers: `ocfs2_check_group_descriptor()`, `ocfs2_read_group_descriptor()`, `ocfs2_find_max_contig_free_bits()`, `ocfs2_which_cluster_group()`, `ocfs2_test_inode_bit()`, `ocfs2_lock_allocators()`.

Integration points:
- Used by extent allocation/truncation, inode creation/deletion, local allocator, resize/recovery paths, quota-aware growth, and system file lookup.
- Depends on journaling, metadata cache, local allocation, DLM inode locks, truncate-log freeing, and blockcheck validation.

Risk areas:
- Chain allocator counters, group free counts, and bitmaps must remain consistent across journal rollback/error paths.
- Reusing bits before delete/free transactions commit can corrupt data; committed bitmap-copy checks are central.
- Discontiguous group result translation is subtle because logical bitmap offsets may map to separate physical extents.
- Slot stealing improves availability but complicates allocator locality and lock ownership.
- Reclaiming empty groups rewrites suballocator and global bitmap state in one transaction-sensitive path.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/suballoc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/suballoc.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/suballoc.h

Declares the OCFS2 suballocator API implemented by `suballoc.c`.

Key contents:
- Defines `group_search_t`, the callback signature for searching one group descriptor bitmap.
- Defines `struct ocfs2_alloc_context`, the reservation/claim state object for metadata, inode, local allocator, main bitmap, and discontiguous main bitmap allocations.
- Defines allocation context modes: `OCFS2_AC_USE_LOCAL`, `OCFS2_AC_USE_MAIN`, `OCFS2_AC_USE_INODE`, `OCFS2_AC_USE_META`, and `OCFS2_AC_USE_MAIN_DISCONTIG`.
- Tracks allocator inode and buffer, target slot, requested/given bits, chain search state, last group hint, max block limit, find-location-only state, and optional reservation map.

Declared APIs:
- Context lifetime: `ocfs2_free_alloc_context()`, `ocfs2_free_ac_resource()`, `ocfs2_alloc_context_bits_left()`.
- Reservation: metadata, inode, cluster, and cluster-bitmap reservation helpers.
- Claiming: metadata, inode, exact inode-location, and cluster claim helpers.
- Bitmap mutation/freeing: `ocfs2_block_group_set_bits()`, suballocator/free-dinode/free-cluster/release-cluster helpers.
- Validation/helpers: group descriptor checking/reading, contiguous-free-bit scanning, cluster-group mapping, allocator locking, inode-bit testing, and steal-slot initialization.

Important inline behavior:
- `ocfs2_which_suballoc_group()` derives a contiguous group descriptor block from an allocated block and bit.
- `ocfs2_cluster_from_desc()` maps cluster bitmap group descriptors to cluster offsets, with special handling for the first group.
- `ocfs2_is_cluster_bitmap()` identifies the global bitmap inode by comparing inode block number to `osb->bitmap_blkno`.

Risk areas:
- Callers own high-level locking and must pair reservation contexts with frees.
- `ac_find_loc_only`/`ac_find_loc_priv` are specialized ordering hooks; misuse can claim a different block than expected.
- `ocfs2_which_suballoc_group()` is not sufficient for discontiguous groups when explicit `i_suballoc_loc` exists.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/suballoc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/super.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/super.c

Implements OCFS2 module lifecycle, filesystem registration, mount/remount parsing, superblock probing and initialization, mount/dismount orchestration, system inode loading, quota enable/disable, statfs, inode slab setup, debugfs state reporting, and filesystem error policy.

Key responsibilities:
- Registers the `ocfs2` filesystem type and OCFS2 quota format.
- Initializes OCFS2 inode, dquot, quota-chunk, and uptodate-cache slabs.
- Parses mount options through `fs_context`.
- Probes supported block sizes for OCFS2 superblocks and rejects OCFS1 volumes.
- Builds `struct ocfs2_super`, VFS superblock operations, feature flags, cluster-stack metadata, workqueues, recovery state, journal object, slot info, and system inode caches.
- Mounts clustered volumes by initializing DLM, locking the superblock, selecting a slot, checking/recovering the volume, loading local alloc, and initializing truncate log.
- Completes mount recovery, quota recovery, and orphan scanning after root dentry setup.
- Dismounts in reverse order, stopping sysfs/debugfs, orphan scan, quota recovery, quotas, local alloc, truncate log, recovery, slots, system inodes, journal, DLM, and heartbeat hangup.

Important mount/remount behavior:
- `ocfs2_fill_super()` probes and initializes the superblock, applies options, validates userspace stack and heartbeat mode, handles hard-readonly devices, creates debugfs/sysfs state, mounts the volume, builds root dentry, enables quotas if writable, and starts orphan scanning.
- `ocfs2_mount_volume()` skips cluster setup for hard-readonly mounts; otherwise it initializes DLM, takes the super lock, finds a slot, loads local system inodes, checks/replays the volume, and initializes truncate log.
- `ocfs2_check_volume()` initializes and loads the journal, verifies journal addressability for large volumes, recovers local alloc after dirty mounts, loads local alloc, marks dead nodes, and computes replay slots.
- `ocfs2_reconfigure()` forbids changing heartbeat mode, data mode, and enabling `inode64` on remount; it manages RO/RW transitions and quota suspend/resume.
- `ocfs2_check_set_options()` validates heartbeat exclusivity, quota feature availability, and ACL/xattr compatibility.

Important VFS/module hooks:
- `ocfs2_sops` provides `statfs`, inode allocation/freeing, eviction, sync, put_super, mount-option display, and quota file I/O hooks.
- `ocfs2_fs_type` uses `get_tree_bdev()` and `kill_block_super`.
- `ocfs2_sync_fs()` flushes or schedules truncate-log work and starts/waits for JBD2 commits.
- `ocfs2_statfs()` reads the global bitmap inode under lock and reports block/free/file counts plus UUID-derived fsid.
- `ocfs2_alloc_inode()` and `ocfs2_inode_init_once()` initialize OCFS2 inode state, lock resources, extent map, metadata cache, reservations, and JBD2 inode linkage.

System inode and quota behavior:
- Global system inodes include root, system directory, and online/global system files; local system inodes are loaded after slot assignment.
- `ocfs2_need_system_inode()` skips quota system inodes when quota feature bits are absent.
- `ocfs2_enable_quotas()` loads local quota system inodes with `QFMT_OCFS2`.
- `ocfs2_disable_quotas()` cancels periodic sync work and disables loaded quotas.

Error behavior:
- `__ocfs2_error()` logs corruption and applies `errors=` policy: panic, continue with `-EIO`, or remount read-only.
- `__ocfs2_abort()` is stronger and forces panic behavior for clustered mounts.
- `ocfs2_block_signals()`/`ocfs2_unblock_signals()` provide full signal masking helpers.

Risk areas:
- Mount/unmount failure labels must preserve ordering across DLM, journal, slot, local alloc, truncate log, quotas, sysfs/debugfs, and recovery state.
- Hard-readonly mounts intentionally skip cluster services and recovery; dirty journals require writable access.
- Remount RW must reject unsupported RO-compatible features and prior filesystem errors.
- Quota enablement is delayed until mount recovery can tolerate cluster-lock waits.
- Superblock feature parsing and cluster-stack validation must match on-disk metadata exactly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/super.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/super.h

Declares OCFS2 superblock-level error and signal helper APIs.

Key contents:
- Declares `__ocfs2_error()` and wraps it with `ocfs2_error(sb, fmt, ...)`, passing `__PRETTY_FUNCTION__` for diagnostics.
- Declares `__ocfs2_abort()` and wraps it with `ocfs2_abort(sb, fmt, ...)`.
- Declares `ocfs2_block_signals()` and `ocfs2_unblock_signals()`.

Integration points:
- Metadata validation, allocator, journal, mount, and inode paths call `ocfs2_error()` for on-disk corruption.
- Critical journal/filesystem failures call `ocfs2_abort()` when continuing is unsafe.
- Long critical sections that cannot tolerate signals use the signal helpers.

Risk areas:
- These macros are part of OCFS2’s corruption policy surface; `ocfs2_error()` may remount read-only or panic depending on mount options.
- `ocfs2_abort()` is intentionally drastic for clustered mounts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/super.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/symlink.c

Implements OCFS2 symlink inode operations and fast-symlink page-cache reads.

Key behavior:
- `ocfs2_fast_symlink_read_folio()` reads the inode dinode block with `ocfs2_read_inode_block()`, copies the inline target from `fe->id2.i_symlink` into the folio, and completes folio read state.
- The copied length is bounded by `ocfs2_fast_symlink_chars(inode->i_sb)` and includes the terminating NUL.
- `ocfs2_fast_symlink_aops` installs `.read_folio` for fast symlink address spaces.
- `ocfs2_symlink_inode_operations` uses `page_get_link` plus OCFS2 getattr, setattr, listxattr, and fiemap hooks.

Integration points:
- Fast symlinks are identified by `symlink.h` as symlink inodes with zero blocks.
- Shared OCFS2 file/xattr/attribute code supplies metadata behavior for symlink inodes.

Risk areas:
- Fast symlink correctness depends on the dinode inline symlink area being valid and shorter than the per-superblock maximum.
- Read errors must end the folio read with failure and release the dinode buffer.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/symlink.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/symlink.h

Declares OCFS2 symlink operation tables and the fast-symlink predicate.

Key contents:
- Exposes `ocfs2_symlink_inode_operations`.
- Exposes `ocfs2_fast_symlink_aops`.
- Defines `ocfs2_inode_is_fast_symlink()`, true for symlink inodes with `i_blocks == 0`.

Integration points:
- Inode setup code uses the predicate to choose fast symlink address-space operations.
- VFS symlink handling uses operation tables implemented in `symlink.c`.

Risk areas:
- The fast-symlink test assumes OCFS2 stores inline symlink targets only for zero-block symlink inodes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/symlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/sysfile.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/sysfile.c

Implements lookup and caching of OCFS2 system file inodes.

Key behavior:
- `ocfs2_get_system_file_inode()` returns an inode reference for a global or slot-local system file.
- Global system inodes are cached in `osb->global_system_inodes[type]`.
- Local system inodes are cached in a lazily allocated `NUM_LOCAL_SYSTEM_INODES * max_slots` array.
- `system_file_mutex` serializes cache lookup/population and protects the extra cached inode reference.
- `_ocfs2_get_system_file_inode()` formats the system inode name, looks it up under `osb->sys_root_inode`, and loads it with `ocfs2_iget(..., OCFS2_FI_FLAG_SYSFILE, type)`.
- Under `CONFIG_DEBUG_LOCK_ALLOC`, lockdep classes are assigned per system inode type, with journal and local quota inodes exempted because their cluster locks are not process-owned in a lockdep-friendly way.

Integration points:
- Mount code loads root/system/global/local system inodes through this file.
- Allocator, quota, journal, truncate log, local alloc, bitmap, and recovery paths retrieve their system files here.

Concurrency and lifetime:
- Cached arrays hold one persistent inode reference; callers receive an additional `igrab()` reference.
- Local system inode array allocation is race-tolerant: if another thread installs the array first, the loser frees its allocation.

Risk areas:
- System inode name formatting and lookup must match on-disk system directory entries.
- Missing system files usually indicate corruption or unsupported feature state.
- Cached references must be released by `ocfs2_release_system_inodes()` during dismount and mount failure cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/sysfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/sysfile.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/sysfile.h

Declares the system-file inode lookup API.

Key contents:
- Declares `ocfs2_get_system_file_inode(struct ocfs2_super *osb, int type, u32 slot)`.

Integration points:
- Used by mount, allocation, quota, journal, local allocator, truncate log, recovery, and other OCFS2 internals needing typed system inodes.
- `type` selects the OCFS2 system inode kind; `slot` selects the node-local instance for local system files.

Risk areas:
- Callers must release the returned inode reference with `iput()`.
- Slot must be meaningful for local system inode types and `OCFS2_INVALID_SLOT` for global ones where appropriate.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/sysfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/uptodate.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/uptodate.c

Implements OCFS2 clustered metadata uptodate tracking. Buffer-head uptodate flags alone are insufficient in a cluster because another node may modify metadata, so this file maintains per-owner hints for which metadata blocks can be trusted locally without reread.

Key responsibilities:
- Initialize, purge, and destroy `struct ocfs2_caching_info` metadata caches.
- Store cached block numbers in a small inline array, then expand to an rb-tree of `ocfs2_meta_cache_item`.
- Check whether a buffer is locally uptodate and trusted for the owner.
- Mark existing or newly allocated metadata buffers as uptodate in the owner cache.
- Remove single blocks or xattr cluster ranges from the cache.
- Dispatch owner, superblock, spinlock, and I/O-lock operations through `struct ocfs2_caching_operations`.
- Maintain the global slab `ocfs2_uptodate_cachep`.

Important behavior:
- `ocfs2_buffer_uptodate()` returns false if the buffer is not marked uptodate, returns true for journaled buffers on this node, otherwise checks the owner metadata cache.
- `ocfs2_buffer_read_ahead()` reports locked cached buffers as active readahead, assuming caller serialization with the I/O lock.
- `ocfs2_set_buffer_uptodate()` avoids duplicate work, appends to the inline array when possible, and expands to an rb-tree when inline capacity is exceeded.
- Expansion preallocates tree items outside the cache spinlock and handles races where purge/removal happened during allocation.
- `ocfs2_set_new_buffer_uptodate()` sets the buffer flag and inserts it while holding the owner I/O lock.
- `ocfs2_metadata_cache_purge()` snapshots the rb-tree root under lock, resets the cache, and frees tree items outside the lock.
- Removal erases tree entries under the cache lock, then frees items after unlocking.

Integration points:
- Used by metadata I/O, inode/dinode reads, allocator group descriptor reads, journal access, xattr cache removal, and lock downconversion paths.
- `ocfs2_inode_init_once()` initializes inode metadata caches with inode caching operations.

Risk areas:
- The cache is a strong hint, not a pinned buffer list; callers still rely on `buffer_uptodate()` and journal state.
- Insertions are serialized by owner I/O lock; removals/purges can race with slow allocation and are explicitly handled.
- Count mismatches during purge indicate cache accounting bugs.
- Not converting tree caches back to arrays after removals is intentional.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/uptodate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/uptodate.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/uptodate.h

Declares OCFS2 metadata-cache operations for clustered uptodate tracking.

Key contents:
- Defines `struct ocfs2_caching_operations`, the callback table used by generic metadata-cache code to get owner id, superblock, non-sleeping cache locks, and sleeping I/O locks.
- Declares slab lifecycle: `init_ocfs2_uptodate_cache()` and `exit_ocfs2_uptodate_cache()`.
- Declares cache lifecycle: `ocfs2_metadata_cache_init()`, `ocfs2_metadata_cache_purge()`, and `ocfs2_metadata_cache_exit()`.
- Declares owner/I/O helpers: `ocfs2_metadata_cache_owner()`, `ocfs2_metadata_cache_io_lock()`, and `ocfs2_metadata_cache_io_unlock()`.
- Declares buffer-state APIs: `ocfs2_buffer_uptodate()`, `ocfs2_set_buffer_uptodate()`, `ocfs2_set_new_buffer_uptodate()`, `ocfs2_remove_from_cache()`, `ocfs2_remove_xattr_clusters_from_cache()`, and `ocfs2_buffer_read_ahead()`.

Integration points:
- Included by inode initialization, buffer-head I/O, allocator, xattr, and metadata validation paths.
- Caching operation implementations connect this generic cache to inode or other metadata owners.

Risk areas:
- Callers must provide non-sleeping cache locks and sleeping I/O locks with the expected semantics.
- `ocfs2_buffer_uptodate()` is a cluster-coherency check, not just a wrapper around `buffer_uptodate()`.
- Removal APIs must be called when metadata blocks are freed or xattr clusters are removed to avoid trusting stale local buffers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/uptodate.h -->