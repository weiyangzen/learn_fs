# Group Research: group_814_linux_sources_os_linux_linux_fs_ocfs2_inode_c_sources_os_linux_linux_f60ddd1491c0

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`, OCFS2 inode/ioctl/journal/localalloc/locking/mmap/move-extents files. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/inode.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/inode.c

`inode.c` is OCFS2’s core inode lifecycle implementation. It bridges VFS inode objects to on-disk `ocfs2_dinode` records, initializes per-inode lock resources, manages inode cache identity, validates dinode metadata, updates dirty inode state through JBD2 transactions, and owns eviction/delete behavior.

Main responsibilities:
- Maps OCFS2 on-disk inode flags to VFS inode flags with `ocfs2_set_inode_flags()` and back with `ocfs2_get_inode_flags()`.
- Implements `ocfs2_iget()`/`ocfs2_ilookup()` using `iget5_locked()`, custom find/init actors, and block-number based inode identity.
- Populates VFS inode fields from `ocfs2_dinode` in `ocfs2_populate_inode()`, including mode-specific `i_op`, `i_fop`, address-space ops, timestamps, link count, size, sector count, system-file flags, bitmap/quota flags, and lock resource initialization.
- Reads locked inodes with optional cluster locking. It avoids metadata locks for system files, orphan recovery, and local mounts, and supports filecheck check/fix modes through specialized dinode validation/repair.
- Deletes and wipes orphaned inodes. The delete path coordinates inode meta locks, open locks, orphan directory locks, NFS sync lock, truncate, directory index removal, xattr removal, refcount-tree removal, quota release, dinode freeing, and inode allocation bitmap updates.
- Coordinates with orphan recovery by tracking `osb_recovering_orphan_dirs` and `osb_orphan_wipes` so delete_inode and recovery do not deadlock or double-wipe the same inode.
- Maintains eviction behavior through `ocfs2_evict_inode()`, `ocfs2_delete_inode()`, and `ocfs2_clear_inode()`, including checkpointing metadata before lock resources and caches are destroyed.
- Provides `ocfs2_inode_revalidate()` for getattr-style coherency by taking and dropping the inode metadata lock.
- Writes VFS inode state back into dinode buffers via `ocfs2_mark_inode_dirty()`, including size, uid/gid, mode, link count, timestamps, cluster count, dynamic features, and fsync transaction tracking.
- Refreshes in-memory inodes from disk with `ocfs2_refresh_inode()`.
- Validates dinode blocks in `ocfs2_validate_inode_block()`, checking ECC, valid signature, block number, `OCFS2_VALID_FL`, filesystem generation, suballocator slot range, inline-data consistency, chain-list consistency, and refcount-location consistency.
- Implements filecheck-specific validation/repair helpers that return OCFS2 filecheck error classes and can repair limited fields such as `i_blkno`, filesystem generation, extent-list `l_next_free_rec`, and metadata ECC.
- Exposes inode-backed metadata cache operations through `ocfs2_inode_caching_ops`.

Important dependencies:
- Cluster locking: `dlmglue.h` functions such as `ocfs2_inode_lock()`, `ocfs2_open_lock()`, `ocfs2_try_open_lock()`, and lock resource init/free helpers.
- Journaling: `ocfs2_start_trans()`, `ocfs2_journal_access_di()`, `ocfs2_journal_dirty()`, `ocfs2_commit_trans()`, `ocfs2_checkpoint_inode()`.
- Allocation/suballocation: inode allocator system files, `ocfs2_free_dinode()`, truncate log, orphan dirs, quota credits.
- Data/metadata cleanup: xattrs, refcount tree, directory index truncation, extent map truncation, metadata cache shutdown.

Key invariants:
- Inode cache identity is the dinode block number, not just VFS inode number.
- OCFS2 does not trust inode metadata without appropriate cluster locking except in controlled system-file/recovery/read-only paths.
- System files are never deleted through normal inode eviction.
- A zero-link inode is only wiped if the cluster-wide open-lock trylock proves no node still has it live.
- Successfully wiped inodes set `OCFS2_INODE_DELETED`, allowing clear-inode to skip checkpointing metadata that now belongs back to allocator structures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/inode.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/inode.h

`inode.h` defines OCFS2’s private inode structure, inode state flags, inode-cache helpers, and public inode lifecycle APIs.

Main contents:
- Defines `struct ocfs2_inode_info`, embedding the VFS inode and adding OCFS2 state:
  - On-disk block identity `ip_blkno`.
  - Cluster lock resources for metadata, open, and rw locks.
  - Allocation and xattr semaphores.
  - Spinlock-protected open count, cluster count, flags, attributes, I/O marker lists, and unwritten extent list.
  - Metadata cache, extent map, JBD2 inode, directory lookup hints, local allocation reservation, quota pointers, and fsync transaction IDs.
- Defines `ip_flags` values for system files, journal inodes, bitmap inodes, deleted inodes, maybe-orphaned remote unlinks, direct-I/O open state, orphan-dir skipping, and DIO orphan entries.
- Provides `OCFS2_I()` and `INODE_CACHE()` conversion helpers.
- Declares `ocfs2_evict_inode()`, `ocfs2_iget()`, `ocfs2_ilookup()`, inode revalidation, inode population/refresh, dirty marking, inode flag sync helpers, dinode validation, and inode block read helpers.
- Defines iget flags for system-file lookup, orphan recovery, and filecheck check/fix modes.
- Provides `ocfs2_inode_sector_count()` and `ocfs2_is_refcount_inode()` helpers.

This header is the contract shared by nearly all OCFS2 subsystems that need inode state, cluster locking, extent maps, journaling state, or metadata caching.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ioctl.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/ioctl.c

`ioctl.c` implements OCFS2’s file attribute operations and user ioctl dispatch. It handles allocation-space ioctls, volume resize/group changes, reflink, aggregated filesystem info requests, trim, and move-extents dispatch.

Main responsibilities:
- Implements `ocfs2_fileattr_get()` and `ocfs2_fileattr_set()` for generic fileattr integration. Attribute set takes the inode metadata lock, preserves non-modifiable bits, enforces immutable/append capability checks under OCFS2 locking, starts an inode-update transaction, updates ctime, and writes the dinode.
- Defines helpers for `OCFS2_IOC_INFO`, including request flag management, coherent/non-coherent mode handling, and safe copy to/from user.
- Provides individual info request handlers for block size, cluster size, max slots, label, UUID, feature flags, journal size, free inode counts, and free-fragmentation statistics.
- Free inode reporting scans per-slot inode allocator system files. In coherent mode it uses system inode lookup and cluster locks; in non-coherent mode it resolves raw system inode block numbers and reads blocks directly.
- Free fragmentation reporting scans global bitmap chain records and group descriptors, builds a power-of-two chunk histogram, and reports min/max/average free extents plus free cluster totals. Non-coherent raw reads include extra validation of group bitmap size.
- Validates info request magic, code, and structure size before dispatching; unknown request codes are returned unfilled for forward/backward compatibility.
- Handles compat pointer arrays for 32-bit userspace when `CONFIG_COMPAT` is enabled.
- Dispatches `ocfs2_ioctl()`:
  - `OCFS2_IOC_RESVSP*` and `OCFS2_IOC_UNRESVSP*` to `ocfs2_change_file_space()`.
  - `OCFS2_IOC_GROUP_EXTEND` and group add ioctls with `CAP_SYS_RESOURCE` and mount-write protection.
  - `OCFS2_IOC_REFLINK` to `ocfs2_reflink_ioctl()`.
  - `OCFS2_IOC_INFO` to the info aggregator.
  - `FITRIM` with `CAP_SYS_ADMIN`, discard support checks, and `ocfs2_trim_fs()`.
  - `OCFS2_IOC_MOVE_EXT` to `ocfs2_ioctl_move_extents()`.
- Implements `ocfs2_compat_ioctl()` for compat reflink/info pointer translation and forwards supported commands to the native ioctl path.

Key interactions:
- Uses inode/journal helpers for attribute persistence.
- Uses system-file lookup and raw block reads for coherent vs non-coherent info modes.
- Exposes `move_extents.c` through the ioctl surface.
- Relies on user ABI structures from OCFS2 filesystem headers.

Key invariants:
- Mutating ioctls acquire mount write access where needed.
- Privileged resize/trim operations require capabilities.
- Info aggregation processes small typed request structures to preserve ABI compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ioctl.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/ioctl.h

`ioctl.h` is the public internal prototype header for OCFS2 ioctl and file attribute handling.

It declares:
- `ocfs2_fileattr_get()`
- `ocfs2_fileattr_set()`
- `ocfs2_ioctl()`
- `ocfs2_compat_ioctl()`

The header connects OCFS2 inode/file operation tables to the implementation in `ioctl.c`. It contains no policy beyond include guards and function prototypes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/journal.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/journal.c

`journal.c` implements OCFS2’s JBD2 integration and clustered recovery machinery. It covers transaction handles, metadata checksum triggers, journal load/shutdown/wipe, commit thread behavior, node recovery, replay slot tracking, local alloc/truncate/quota recovery handoff, and orphan directory recovery.

Main responsibilities:
- Maintains replay maps for offline slots, allowing recovery of slots that have no active node mapping.
- Initializes, disables, and exits recovery state through `ocfs2_recovery_init()`, `ocfs2_recovery_disable*()`, and `ocfs2_recovery_exit()`.
- Tracks nodes needing recovery in `ocfs2_recovery_map`, guarded by `osb_lock` and `recovery_lock`.
- Implements `ocfs2_commit_cache()` to flush JBD2, increment OCFS2 transaction IDs, reset transaction counts, wake downconvert/checkpoint waiters, and serialize with `j_trans_barrier`.
- Implements transaction APIs:
  - `ocfs2_start_trans()` checks readonly state, starts sb internal write, takes transaction barrier, starts JBD2 handle, and counts active transactions for clustered mounts.
  - `ocfs2_commit_trans()` stops JBD2 and releases barriers for non-nested handles.
  - `ocfs2_extend_trans()`, `ocfs2_assure_trans_credits()`, and `ocfs2_allocate_extend_trans()` manage handle credit growth/restart.
- Sets up JBD2 frozen/abort triggers for dinodes, extent blocks, refcount blocks, group descriptors, directory blocks, xattr blocks, quota blocks, dx roots, and dx leaves so metadata ECC is computed at journal freeze time.
- Provides typed `ocfs2_journal_access_*()` wrappers that set the correct checksum trigger and call JBD2 write/undo access under metadata-cache I/O locking.
- Implements `ocfs2_journal_dirty()` with abort handling if JBD2 dirtying fails.
- Allocates, initializes, loads, shuts down, and wipes journals:
  - `ocfs2_journal_alloc()` creates the OCFS2 journal skeleton.
  - `ocfs2_journal_init()` opens the slot journal system inode, locks it, creates the JBD2 journal, records dirty state, and installs data-buffer callbacks.
  - `ocfs2_journal_load()` loads JBD2, clears recorded errors, marks OCFS2 journal dirty, and starts the commit thread for clustered mounts.
  - `ocfs2_journal_shutdown()` stops commit thread, flushes/destroys JBD2, clears dirty state if safe, unlocks/releases the journal inode, and frees journal state.
- Implements recovery:
  - Forces journal data reread from disk before replay to avoid stale cached blocks.
  - Replays dirty remote slot journals, clears dirty flags, increments recovery generation, and writes journal dinode ECC.
  - Recovers dead nodes by replaying journals, stamping local alloc/truncate log clean, clearing slot ownership, and queuing second-phase cleanup.
  - Detects dead nodes at mount by trylocking journal inodes and recording recovery generations.
- Implements second-phase recovery work:
  - Cleans recovered local alloc windows.
  - Completes truncate log cleanup.
  - Recovers quotas after other recovery work.
  - Scans orphan directories and iputs queued orphan inodes so normal eviction/delete paths finish cleanup.
- Implements periodic orphan scans for clustered mounts using delayed work and an orphan scan lock/sequence number so only one node scans all orphan dirs per interval.
- Provides hard-readonly journal checks via `ocfs2_check_journals_nolocks()`.

Key invariants:
- OCFS2 transaction IDs are separate from JBD2 tids and are used by lock/cache checkpoint decisions.
- Metadata buffers must go through journal access before dirtying.
- Recovery generation prevents duplicate recovery when another node already recovered a slot.
- Journal replay is the authoritative first phase of node recovery; local alloc, truncate log, quota, and orphan cleanup are queued after the node can be considered safely recovered.
- Orphan recovery coordinates with `inode.c` delete paths to avoid deadlocks and duplicate inode wiping.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/journal.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/journal.h

`journal.h` defines OCFS2 journaling state, recovery map structures, transaction APIs, metadata access wrappers, checkpoint helpers, and journal credit formulas.

Main contents:
- Defines `enum ocfs2_journal_state`: free, loaded, and shutdown.
- Defines `struct ocfs2_recovery_map`, a flexible array of node numbers pending recovery.
- Defines `struct ocfs2_journal`, wrapping JBD2 journal state plus OCFS2-specific inode, dinode buffer, transaction count, transaction barrier, checkpoint wait queue, local-alloc cleanup list, and recovery work item.
- Declares `trans_inc_lock` and inline helpers for:
  - Incrementing OCFS2 transaction IDs without wrapping to zero.
  - Recording a cache object’s last transaction.
  - Testing whether a metadata cache object is fully checkpointed.
  - Tracking whether a cache object/inode is still “new”.
- Declares orphan scan, recovery lifecycle, replay slot, journal lifecycle, dead-node marking, mount/quota recovery completion, and recovery-thread APIs.
- Defines `ocfs2_start_checkpoint()` and `ocfs2_checkpoint_inode()`, which wakes the commit thread and waits until an inode metadata cache is fully checkpointed on clustered mounts.
- Declares transaction APIs: start, commit, extend, assure credits, and allocation-oriented extension.
- Defines journal access types: create, write, undo.
- Declares typed metadata access wrappers for dinodes, extent blocks, refcount blocks, group descriptors, xattr blocks, quota blocks, directory blocks, dx roots, dx leaves, and non-ECC buffers.
- Documents the journal access/dirty protocol: a buffer must receive access before being dirtied.
- Defines metadata credit constants and calculators for inode updates, xattr updates, quota writes/sync, group extend/add, suballocator alloc/free, inline-to-extents conversion, truncate log updates, directory operations, mknod, local alloc window moves, link/unlink/rename, xattr block creation, dx root removal, refcount tree changes, extent extension, symlink creation, group allocation, and discontiguous block groups.
- Provides wrappers for JBD2 ranged inode writes, ordered truncate, and inode fsync transaction tracking.

This header is used widely by allocation, directory, inode, xattr, refcount, truncate, and ioctl paths to size transactions and safely modify metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/localalloc.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/localalloc.c

`localalloc.c` implements OCFS2’s per-node local allocation window. It lets a mounted node reserve a contiguous slice of the global bitmap and satisfy smaller cluster allocations locally, reducing global bitmap contention.

Main responsibilities:
- Computes default local allocation size in `ocfs2_la_default_mb()`, balancing group descriptor capacity, cluster size, block size, max slots, and a 256 MiB default cap.
- Applies requested/default sizes with `ocfs2_la_set_sizes()`.
- Tracks enabled/throttled/disabled local alloc state. `ocfs2_local_alloc_seen_free_bits()` and delayed `ocfs2_la_enable_worker()` can re-enable allocation after free-space conditions improve.
- Decides whether an allocation should use local alloc in `ocfs2_alloc_should_use_local()`, based on state and request size.
- Loads the local alloc system inode for the current slot with `ocfs2_load_local_alloc()`, validates flags and bitmap size, and requires the on-disk local alloc to be clean/recovered before enabling it.
- Shuts down local alloc with `ocfs2_shutdown_local_alloc()`, disabling the state, clearing the local alloc dinode, and returning unused local-window bits to the global bitmap in one window-move transaction.
- Supports recovery:
  - `ocfs2_begin_local_alloc_recovery()` copies and clears a dead slot’s local alloc before releasing the recovered journal.
  - `ocfs2_complete_local_alloc_recovery()` later returns unused bits to the global bitmap under normal cluster locking and synchronous transaction handling.
- Reserves local alloc bits in `ocfs2_reserve_local_alloc_bits()`, double-checking state under inode mutex and sliding the window if insufficient free bits remain.
- Claims and frees local bits in `ocfs2_claim_local_alloc_bits()` and `ocfs2_free_local_alloc_bits()`, journaling the local alloc dinode and updating reservation maps.
- Counts used bits with `memweight()`, finds clear extents through the reservation map when enabled, and falls back to bitmap scanning when reservations are disabled.
- Clears local alloc state with `ocfs2_clear_local_alloc()`.
- Syncs unused local allocation bits back to the main bitmap in `ocfs2_sync_local_to_main()` by finding zero-bit runs and releasing corresponding global clusters.
- Recalculates local alloc window size after slide, fragmentation, or ENOSPC events. Fragmentation/ENOSPC halves the window, throttles or disables local alloc, and schedules a delayed re-enable.
- Reserves a new global bitmap window, creates a new local alloc window, and slides from the old window to the new one through `ocfs2_local_alloc_slide_window()`.

Key invariants:
- The local alloc inode mutex serializes window changes and state checks.
- Before a window move, the local alloc dinode is cleared first to avoid double-freeing bits if later steps fail.
- Recovery clears a dead node’s local alloc before considering its journal fully released, but returns the bits later outside the sensitive recovery context.
- Local alloc never serves allocations larger than half the window.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/localalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/localalloc.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/localalloc.h

`localalloc.h` declares the internal API for OCFS2 per-node local allocation windows.

It exposes:
- Load/shutdown: `ocfs2_load_local_alloc()`, `ocfs2_shutdown_local_alloc()`.
- Sizing: `ocfs2_la_set_sizes()`, `ocfs2_la_default_mb()`.
- Recovery: `ocfs2_begin_local_alloc_recovery()`, `ocfs2_complete_local_alloc_recovery()`.
- Allocation policy: `ocfs2_alloc_should_use_local()`.
- Reservation/claim/free operations for local bits.
- Free-space notification and delayed re-enable worker.

The header is consumed by allocation, journal recovery, and mount/shutdown paths that need to use or clean up slot-local allocation state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/localalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/locks.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/locks.c

`locks.c` implements userspace file locking support for OCFS2.

Main responsibilities:
- Implements BSD flock handling through `ocfs2_flock()`.
  - Validates `FL_FLOCK`.
  - Falls back to local VFS locking when mounted with local flocks or in local mount mode.
  - Uses OCFS2 file-private cluster locks for clustered flock enforcement.
- `ocfs2_do_flock()` maps read/write flock requests to PR/EX-style file locks, handles trylock vs blocking semantics, serializes through `fp_mutex`, converts existing locks by unlocking first, then calls `ocfs2_file_lock()` and `locks_lock_file_wait()`.
- Converts failed nonblocking cluster lock `-EAGAIN` into `-EWOULDBLOCK`.
- `ocfs2_do_funlock()` releases the OCFS2 file lock and then updates the VFS lock state.
- Implements POSIX lock handling through `ocfs2_lock()`.
  - Validates `FL_POSIX`.
  - Delegates clustered POSIX lock management to `ocfs2_plock()` using the inode block number as the lock identity.

Key invariants:
- Cluster flock state and VFS lock state are updated under the file-private mutex.
- Local flock mount mode bypasses cluster locking.
- POSIX locks are routed through the cluster plock stack, not the flock path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/locks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/locks.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/locks.h

`locks.h` declares OCFS2’s userspace file locking hooks:
- `ocfs2_flock()` for BSD flock operations.
- `ocfs2_lock()` for POSIX byte-range locks.

It is a small prototype header used by file operation setup code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/locks.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/mmap.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/mmap.c

`mmap.c` implements OCFS2’s clustered mmap fault handling.

Main responsibilities:
- `ocfs2_fault()` wraps `filemap_fault()` while blocking signals, matching OCFS2’s lock/messaging paths that may otherwise return restart-style errors at awkward VM fault points.
- `__ocfs2_page_mkwrite()` prepares a clean page-cache folio for write:
  - Rejects stale/unmapped/not-uptodate/out-of-size folios with retry-style `VM_FAULT_NOPAGE`.
  - Uses `ocfs2_write_begin_nolock()` and `ocfs2_write_end_nolock()` to allocate and prepare the full page or final partial page.
  - Returns `VM_FAULT_LOCKED` when the folio is successfully locked/prepared.
- `ocfs2_page_mkwrite()` is the cluster-aware write-fault wrapper:
  - Starts pagefault accounting.
  - Blocks signals.
  - Takes the inode metadata lock in write mode to block remote truncation and downconvert page truncation.
  - Takes `ip_alloc_sem` in write mode to serialize against file truncation and extent-tree mutation.
  - Releases all locks and ends pagefault accounting.
- Defines `ocfs2_file_vm_ops` with fault and page_mkwrite hooks.
- `ocfs2_mmap_prepare()` takes an atime-aware inode lock once during mmap setup, then installs OCFS2 VM ops.

Key invariants:
- mmap write faults reuse the normal buffered write allocation path rather than duplicating allocation rules.
- Cluster inode locking prevents concurrent remote truncation while a page is made writable.
- Allocation semaphore protects extent tree and file size interactions during page-mkwrite.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/mmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/mmap.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/mmap.h

`mmap.h` declares `ocfs2_mmap_prepare(struct vm_area_desc *desc)`.

This is the small interface used by OCFS2 file mmap setup to install clustered VM fault/page_mkwrite operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/mmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/move_extents.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/move_extents.c

`move_extents.c` implements the `OCFS2_IOC_MOVE_EXT` ioctl for explicit extent movement and automatic defragmentation. It copies data to new clusters, updates extent records, handles refcounted extents, frees old clusters through truncate log or refcount decrement, and returns partial progress to userspace.

Main responsibilities:
- Defines `struct ocfs2_move_extents_context`, carrying the target inode/file, mode flags, credits, new physical position, moved count, refcount location, user range, extent tree, metadata/data alloc contexts, and deferred deallocation context.
- `__ocfs2_move_extent()` performs the core move:
  - Copies cluster data page-by-page from old physical cpos to new physical cpos.
  - Locates the extent record for the logical cpos.
  - Verifies extent flags are unchanged.
  - Replaces/splits the extent with a new physical block, clearing `OCFS2_EXT_REFCOUNTED`.
  - Decreases refcount or appends old clusters to truncate log.
  - Updates inode fsync transaction state.
- Reserves metadata for split/move operations in `ocfs2_lock_meta_allocator_move_extents()`, including worst-case sparse extent expansion needs and journal credits.
- `ocfs2_defrag_extent()` allocates a fresh cluster run through normal allocation, optionally allows partial defrag, moves the extent in one transaction, frees newly allocated clusters on failure, and syncs COW/writeback data.
- Explicit move support:
  - Finds the allocation group containing a physical goal with `ocfs2_find_victim_alloc_group()`.
  - Aligns and validates the user-supplied goal with `ocfs2_validate_and_adjust_move_goal()`.
  - Probes a target group near the goal within a threshold using `ocfs2_probe_alloc_group()`.
  - `ocfs2_move_extent()` locks the global bitmap, claims the chosen target bits, updates bitmap counts, moves the extent, and syncs writeback.
- Defrag support:
  - `ocfs2_calc_extent_defrag_len()` accumulates small extents up to a threshold and skips already-large extents.
  - `__ocfs2_move_extents_range()` walks logical clusters with `ocfs2_get_clusters()`, skips holes, chooses defrag vs explicit move, invalidates stale extent cache after each successful move, tracks moved byte count/new offset, schedules truncate-log flush, and runs deferred deallocs.
- `ocfs2_move_extents()` enforces filesystem state and locking:
  - Rejects emergency readonly.
  - Takes inode mutex, OCFS2 rw lock, metadata lock, and `ip_alloc_sem`.
  - Runs the range move.
  - Updates inode ctime in a final inode-update transaction.
- `ocfs2_ioctl_move_extents()` validates userspace input:
  - Requires non-null arg, mount write access, regular writable file, and not immutable/append.
  - Clamps requested range to file size.
  - Defaults threshold to 1 MiB and caps it at file size.
  - Accepts only auto-defrag and partial-defrag flags.
  - Validates explicit move goals.
  - Copies result back even after partial/failing moves so userspace sees completed length and new offset.

Key invariants:
- Each moved extent is protected by journaling so metadata and old-cluster cleanup remain crash-consistent.
- Refcounted extents are unshared by the move path and require refcount-tree locking/preparation.
- Explicit movement cannot cross allocation group boundaries after goal validation.
- Extent cache is truncated after moving to prevent stale physical mapping or stale flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/move_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/move_extents.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/move_extents.h

`move_extents.h` declares the ioctl entry point:

- `ocfs2_ioctl_move_extents(struct file *filp, void __user *argp)`

It connects `ioctl.c` command dispatch to the extent movement/defragmentation implementation in `move_extents.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/move_extents.h -->