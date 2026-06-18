# Group Research: group_1114_linux_stable_sources_os_linux_linux_stable_fs_xfs_xfs_healthmon_c_s_6771eadd6447

Scope verified against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included in subset A. All 12 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_healthmon.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_healthmon.c

## Purpose

Implements the live XFS health-monitor anonymous file descriptor used by privileged userspace, primarily the healer daemon, to receive structured filesystem health, shutdown, media-error, and file I/O error events.

## Main Responsibilities

- Manages the lifetime of `struct xfs_healthmon` objects with RCU-safe mount attachment, weak mount cookies, refcounts, and fd release handling.
- Queues health events from filesystem code, coalescing compatible adjacent or duplicate events to reduce userspace traffic.
- Tracks queue overflow through synthetic lost-event notifications and cumulative fdinfo counters.
- Formats internal health events into `struct xfs_health_monitor_event` v0 records for `read_iter`.
- Implements fd operations for `read_iter`, `poll`, `release`, `show_fdinfo`, and health-monitor ioctls.
- Creates the health monitor fd from `XFS_IOC_HEALTH_MONITOR` with capability, root-inode, and initial user-namespace checks.

## Key Data Flow

Events enter through report helpers:

- `xfs_healthmon_report_fs`
- `xfs_healthmon_report_group`
- `xfs_healthmon_report_inode`
- `xfs_healthmon_report_shutdown`
- `xfs_healthmon_report_media`
- `xfs_healthmon_report_file_ioerror`
- `xfs_healthmon_unmount`

Each helper obtains the active monitor through `xfs_healthmon_get`, builds an `xfs_healthmon_event`, and calls `xfs_healthmon_push`. The queue is protected by `hm->lock`; mount-to-monitor pointer updates are protected by `xfs_healthmon_lock` and RCU.

Userspace reads from the anonymous fd. `xfs_healthmon_read_iter` waits for queued events or buffered bytes, formats events into `hm->buffer` with `xfs_healthmon_format_v0`, and copies bytes to the supplied iterator.

## Event Semantics

- `RUNNING` is queued first when the fd is created.
- `UNMOUNT` is preallocated at fd creation time and inserted at the head of the event list during unmount so userspace sees teardown promptly.
- Metadata events are filtered by `metadata_event_mask`; verbose mode reports all changed bits, non-verbose mode reports runtime sickness, newly found fsck corruption, or repaired health transitions.
- Secondary health flags are filtered before reporting filesystem, AG, rtgroup, and inode metadata events.
- Media errors map XFS data/log/realtime devices to health-monitor domains.
- File I/O errors map `fserror_type` actions to buffered, direct I/O, or data-loss event types and return positive errno values to userspace.

## Important Invariants

- Only one health monitor may be attached to an `xfs_mount` at a time.
- `mount_cookie` is a weak superblock pointer value and must not be dereferenced except under the attach/detach protocol used here.
- `DETACHED_MOUNT_COOKIE` makes future event pushes return shutdown and causes reads/poll to observe EOF-ready state.
- The event queue is capped by `XFS_HEALTHMON_MAX_EVENTS`; allocation failure or queue saturation increments lost-event counters.
- Output buffer size is bounded by `XFS_HEALTHMON_MAX_OUTBUF` and at least one page.
- Anonymous fd creation happens last because installed fds cannot be safely undone.

## Dependencies

- Uses `anon_inode_getfd`, poll, wait queues, and iterator copying for the fd interface.
- Uses health conversion helpers from `xfs_health.h`.
- Receives I/O error reports through Linux `fserror` plumbing.
- Integrates with mount state via `mp->m_healthmon`.
- Emits tracepoints for creation, insert, push, merge, drop, read, and release paths.

## Risk Notes

The code is concurrency-sensitive. The most important correctness points are the RCU/refcount handoff in `xfs_healthmon_get`, detaching before final fd release, preallocating the unmount event, and preserving queue accounting when events merge or are lost.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_healthmon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_healthmon.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_healthmon.h

## Purpose

Defines the internal live-health-monitor data structures, event taxonomy, and reporting API used by XFS code to deliver health events to userspace.

## Main Types

- `struct xfs_healthmon`
  - Stores the weak mount cookie, device number, refcount, event queue, wait queue, output buffer, lost-event counters, and verbose-mode flag.
- `enum xfs_healthmon_type`
  - Represents monitor lifecycle, lost events, unmount, shutdown, metadata health changes, media errors, and file-range I/O error events.
- `enum xfs_healthmon_domain`
  - Identifies the affected object class: mount, filesystem metadata, allocation group, inode, realtime group, data/log/realtime device, or file range.
- `struct xfs_healthmon_event`
  - Queue node containing event type/domain/time and a union of event-specific payloads.

## Main API

- `xfs_healthmon_unmount`
- `xfs_healthmon_report_fs`
- `xfs_healthmon_report_group`
- `xfs_healthmon_report_inode`
- `xfs_healthmon_report_shutdown`
- `xfs_healthmon_report_media`
- `xfs_healthmon_report_file_ioerror`
- `xfs_ioc_health_monitor`

## Important Invariants

- The mount pointer is stored only as an opaque cookie and is explicitly documented as unsafe to dereference by generic users.
- The open fd, the mount, and running event handlers each hold references to the monitor object.
- Event list and event counters are protected by `lock`.
- Formatting-buffer cursors are protected by the anonymous file inode lock.
- `unmount_event` is preallocated because unmount notification must not fail due to memory pressure.

## Dependencies

This header depends on XFS mount, inode, group, device, and userspace ioctl structures that are included by implementation files before including this header.

## Research Notes

The header is the narrow internal contract between health state producers and the monitor fd implementation. It also documents the locking model that keeps queue operations independent from the mount lifetime.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_healthmon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_hooks.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_hooks.c

## Purpose

Implements a small wrapper around Linux blocking notifier chains for optional XFS live hooks.

## Main API

- `xfs_hooks_init`
  - Initializes a hook chain with `BLOCKING_INIT_NOTIFIER_HEAD`.
- `xfs_hooks_add`
  - Registers a hook notifier and asserts that the callback is present and that `struct xfs_hook` embeds `notifier_block` at offset zero.
- `xfs_hooks_del`
  - Unregisters a hook from a chain.
- `xfs_hooks_call`
  - Invokes the blocking notifier chain and returns the final notifier status.

## Important Invariants

- `struct xfs_hook` must remain layout-compatible with `struct notifier_block` at offset zero.
- Callers are responsible for static-key gating through the header macros so empty hook sites can be compiled or patched to near-zero overhead.

## Dependencies

Uses Linux blocking notifier APIs and XFS trace/mount/ag include context. The concrete hook points live elsewhere; this file only provides generic chain mechanics.

## Research Notes

This is deliberately minimal infrastructure. It does not define hook semantics, event payloads, or lifecycle beyond registration and call dispatch.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_hooks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_hooks.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_hooks.h

## Purpose

Declares the optional live-hook abstraction for XFS and compiles it away when `CONFIG_XFS_LIVE_HOOKS` is disabled.

## Main Types and Macros

When live hooks are enabled:

- `struct xfs_hooks`
  - Wraps a `blocking_notifier_head`.
- `struct xfs_hook`
  - Embeds `struct notifier_block` as the first field.
- `xfs_hook_fn_t`
  - Typed hook callback adapter.
- `DEFINE_STATIC_XFS_HOOK_SWITCH`
- `xfs_hooks_switch_on`
- `xfs_hooks_switch_off`
- `xfs_hooks_switched_on`

When disabled:

- `struct xfs_hooks` is empty.
- Hook switches become no-ops.
- `xfs_hooks_call` returns `NOTIFY_DONE`.

## Main API

- `xfs_hooks_init`
- `xfs_hooks_add`
- `xfs_hooks_del`
- `xfs_hooks_call`
- `xfs_hook_setup`

## Important Invariants

- Static-branch enable/disable can take CPU hotplug locks, so callers must not hold locks that memory reclaim or writeback might also need while changing hook switch state.
- `xfs_hook_setup` sets callback and zero priority; users needing priority ordering must adjust the notifier field explicitly.

## Research Notes

This header is an optional instrumentation/control-plane API. Its design keeps hook call sites cheap in normal kernels and gives live features a common notifier-chain substrate.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_hooks.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_icache.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_icache.c

## Purpose

Implements XFS in-core inode cache management, inode lookup/recycling, reclaim, speculative preallocation garbage collection, deferred inode inactivation, and inode-cache walking.

## Main Responsibilities

- Allocates and initializes `struct xfs_inode` objects through `xfs_inode_alloc`.
- Frees inodes through RCU-safe teardown and fork/log-item cleanup.
- Performs `xfs_iget` cache lookup, cache miss loading, reclaimable-inode recycling, and metadata inode validation.
- Maintains per-AG radix-tree tags for reclaimable inodes and blockgc candidates.
- Runs inode reclaim workers and shrinker-driven reclaim scans.
- Runs blockgc scans to free post-EOF and COW speculative preallocations.
- Queues and drains deferred inode inactivation work through per-cpu `xfs_inodegc` lists.
- Registers a shrinker that accelerates inodegc under memory pressure.

## Key Data Structures

- Per-AG inode radix tree: `pag->pag_ici_root`
- Inode cache tags:
  - `XFS_ICI_RECLAIM_TAG`
  - `XFS_ICI_BLOCKGC_TAG`
- Per-AG xarray marks:
  - `XFS_PERAG_RECLAIM_MARK`
  - `XFS_PERAG_BLOCKGC_MARK`
- `struct xfs_icwalk`
  - Public/private scan filters for uid, gid, project id, minimum file size, sync mode, scan limits, reclaim-sick mode, and union matching.

## Inode Lookup Flow

`xfs_iget` verifies the inode number, finds the per-AG object, and looks in the radix tree under RCU:

- Cache hit: `xfs_iget_cache_hit`
  - Rejects stale RCU entries, inodes under construction, inactivation, or reclaim.
  - Flushes inodegc when a referenced inode still needs inactivation.
  - Recycles reclaimable inodes with `xfs_iget_recycle`.
  - Grabs live VFS inodes with `igrab`.
  - Checks free/allocated state against `XFS_IGET_CREATE`.
- Cache miss: `xfs_iget_cache_miss`
  - Allocates an inode, maps it, reads the ondisk dinode unless creating a v3 inode, validates free state, and inserts it into the per-AG radix tree.

`xfs_trans_metafile_iget` and `xfs_metafile_iget` layer metadata-file type, nlink, mode, and metadir checks on top of `xfs_iget`.

## Reclaim Flow

- `xfs_inode_mark_reclaimable` chooses between deferred inactivation and direct reclaim.
- `xfs_inodegc_set_reclaimable` sets `XFS_IRECLAIMABLE` and the reclaim radix-tree tag.
- `xfs_reclaim_inode` grabs reclaim candidates, avoids dirty/pinned inodes, handles log shutdown by aborting flush state, removes the inode from the radix tree, and frees it after lookup synchronization.
- `xfs_reclaim_inodes`, `xfs_reclaim_inodes_nr`, and `xfs_reclaim_worker` drive reclaim from unmount, shrinkers, and background work.

## Blockgc Flow

- `xfs_inode_set_eofblocks_tag` and `xfs_inode_set_cowblocks_tag` set inode flags and per-AG blockgc tags.
- `xfs_inode_free_eofblocks` frees post-EOF space when the inode matches scan filters and can be safely locked.
- `xfs_inode_free_cowblocks` cancels COW fork reservations only when writeback/direct I/O hazards are excluded and IO/MMAP locks can be taken.
- `xfs_blockgc_worker`, `xfs_blockgc_free_space`, `xfs_blockgc_flush_all`, `xfs_blockgc_free_dquots`, and `xfs_blockgc_free_quota` provide background, synchronous, and quota-pressure entry points.

## Inodegc Flow

- `xfs_inodegc_queue` marks an inode `XFS_NEED_INACTIVE`, pushes it to a per-cpu lockless list, and schedules work based on cluster-size backlog, low free space, realtime low space, quota pressure, or shrinker pressure.
- `xfs_inodegc_worker` runs in NOFS context, sets `XFS_INACTIVATING`, calls `xfs_inactive`, and moves the inode to reclaimable state.
- `xfs_inodegc_push`, `xfs_inodegc_flush`, `xfs_inodegc_stop`, and `xfs_inodegc_start` control draining and enablement.
- The inodegc shrinker does not directly free memory; it schedules inactivation so later reclaim can free inodes.

## Important Invariants

- Inode numbers are set to zero before RCU freeing so cache lookups can detect stale or reused entries.
- Reclaim and blockgc tag state is mirrored from inode radix-tree tags into per-AG xarray marks.
- Reclaim must not perform ordinary writeback; callers push the AIL first if dirty inode metadata must be cleaned.
- Sick inodes are not reclaimed unless unmount, no-recovery, or shutdown conditions make that appropriate.
- Blockgc does not free COW staging extents for files with unsafe writeback or direct I/O state.
- Deferred inactivation is disabled/drained under `sb->s_umount` coordination.

## Dependencies

This file integrates with inode formatting/loading, quota, bmap utilities, reflink, AG group iteration, log/AIL pushing, health tracking, metadata-file validation, workqueues, shrinkers, radix trees, and RCU.

## Research Notes

This is the coordination center for XFS inode memory lifecycle. The hardest parts are the state transitions among `XFS_INEW`, `XFS_NEED_INACTIVE`, `XFS_INACTIVATING`, `XFS_IRECLAIMABLE`, `XFS_IRECLAIM`, `XFS_IFLUSHING`, and `XFS_ISTALE`, all of which protect against lookup, reclaim, flush, and free races.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_icache.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_icache.h

## Purpose

Declares the inode-cache, reclaim, blockgc, and inodegc APIs exported by `xfs_icache.c`.

## Main Types

- `struct xfs_icwalk`
  - Public scan parameters for blockgc-style inode walks.
  - Includes filter flags, uid/gid/project id filters, minimum file size, and scan limit.

## Main Flags

- `XFS_ICWALK_FLAG_SYNC`
- `XFS_ICWALK_FLAG_UID`
- `XFS_ICWALK_FLAG_GID`
- `XFS_ICWALK_FLAG_PRID`
- `XFS_ICWALK_FLAG_MINFILESIZE`
- `XFS_ICWALK_FLAGS_VALID`

## Main API

- Inode lookup/allocation:
  - `xfs_iget`
  - `xfs_inode_alloc`
  - `xfs_inode_free`
- Reclaim:
  - `xfs_reclaim_worker`
  - `xfs_reclaim_inodes`
  - `xfs_reclaim_inodes_count`
  - `xfs_reclaim_inodes_nr`
  - `xfs_inode_mark_reclaimable`
- Blockgc:
  - `xfs_blockgc_free_dquots`
  - `xfs_blockgc_free_quota`
  - `xfs_blockgc_free_space`
  - `xfs_blockgc_flush_all`
  - EOF/COW tag setters and clearers
  - `xfs_blockgc_worker`
  - `xfs_blockgc_stop`
  - `xfs_blockgc_start`
- Inodegc:
  - `xfs_inodegc_worker`
  - `xfs_inodegc_push`
  - `xfs_inodegc_flush`
  - `xfs_inodegc_stop`
  - `xfs_inodegc_start`
  - `xfs_inodegc_register_shrinker`

## Important Invariants

- `xfs_iget` flags distinguish creation, untrusted lookup, don't-cache lookup, incore-only lookup, and no-retry lookup.
- Synchronous blockgc callers must avoid holding inode IO/MMAP locks, as documented by the implementation.
- Inodegc and blockgc lifecycle control is mount-level state and must coordinate with unmount.

## Research Notes

This header is the public in-kernel surface for inode cache users. Most behavior is implemented in `xfs_icache.c`; the header mostly communicates scan-filter contracts and lifecycle entry points.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_icache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_icreate_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_icreate_item.c

## Purpose

Implements the XFS inode-create log item, which logs initialization of newly allocated inode chunks and replays that initialization during log recovery.

## Main Responsibilities

- Defines `xfs_icreate_cache` for `struct xfs_icreate_item` allocation.
- Provides log item operations for sizing, formatting, and release.
- Implements `xfs_icreate_log` to attach a dirty inode-create item to a transaction.
- Implements recovery ordering and pass2 replay for `XFS_LI_ICREATE` items.

## Key Data Flow

`xfs_icreate_log` records:

- allocation group number
- AG block number
- inode count
- inode size
- allocation extent length
- generation number

The item is formatted as a single `XLOG_REG_TYPE_ICREATE` vector. During recovery, `xlog_recover_icreate_commit_pass2` validates the record, checks for cancelled inode cluster buffers, and calls `xfs_ialloc_inode_init` to stamp initialized inode buffers.

## Important Invariants

- The log item has exactly one vector.
- The AG number, AG block number, inode size, inode count, and allocation length must match current filesystem geometry.
- The chunk length must be either a full inode allocation or the supported sparse minimum allocation.
- The inode count must be consistent with the extent length.
- ICREATE recovery is ordered with buffer-list recovery because it is logically equivalent to replaying initialized inode allocation buffers.
- If any cluster buffer was cancelled, replay is skipped conservatively; partial cancellation triggers a warning.

## Dependencies

Uses XFS transaction/log item infrastructure, log recovery reorder hooks, inode allocation geometry, cancellation tracking, and inode-buffer initialization.

## Research Notes

This file keeps inode chunk initialization recoverable without logging every initialized inode buffer directly. Its validation path is intentionally strict because malformed icreate records can otherwise initialize arbitrary inode buffers during recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_icreate_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_icreate_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_icreate_item.h

## Purpose

Declares the in-memory inode-create log item and its transaction helper.

## Main Types

- `struct xfs_icreate_item`
  - Embeds `struct xfs_log_item`.
  - Carries an `xfs_icreate_log` format record.

## Main API

- `xfs_icreate_cache`
- `xfs_icreate_log`

## Important Invariants

- The header exposes only the constructor/logging helper; formatting and recovery are private to the `.c` file.
- The logged fields describe a newly allocated inode chunk by AG-relative start, count, inode size, extent length, and generation.

## Research Notes

This is a small transaction-log interface used by inode allocation code to make bulk inode initialization crash recoverable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_icreate_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_inode.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_inode.c

## Purpose

Implements core XFS inode operations: inode locking, namespace mutations, inode creation, truncation and inactivation, unlinked-list recovery, inode freeing, inode flushing, layout breaking, and helper utilities.

## Main Responsibilities

- Provides multi-lock inode locking primitives over VFS `i_rwsem`, mapping `invalidate_lock`, and XFS `i_lock`.
- Implements directory namespace operations:
  - lookup
  - create
  - tmpfile create
  - hardlink
  - remove
  - rename, exchange, and whiteout rename
- Initializes newly allocated inodes and dquot attachments.
- Truncates data/attr fork extents and cancels COW reservations.
- Runs inactive cleanup for unreferenced inodes.
- Frees unlinked inodes and handles inode-cluster stale marking.
- Waits for pinned inodes and forces log commits for inode fsync semantics.
- Flushes dirty inode state to inode cluster buffers and coordinates clustered inode writeback.
- Reloads incomplete incore unlinked-list state.
- Breaks leases and DAX layouts before extent-remapping operations.

## Locking Model

The file defines and enforces the XFS inode lock hierarchy:

- IOLOCK: VFS inode `i_rwsem`
- MMAPLOCK: mapping `invalidate_lock`
- ILOCK: XFS inode `i_lock`

`xfs_ilock`, `xfs_ilock_nowait`, `xfs_iunlock`, `xfs_ilock_demote`, and `xfs_assert_ilocked` operate on combinations of these locks. Multi-inode helpers sort or order locks by inode number and use lockdep subclasses:

- `xfs_lock_inodes`
- `xfs_lock_two_inodes`
- `xfs_ilock2_io_mmap`
- `xfs_iunlock2_io_mmap`
- `xfs_iunlock2_remapping`

## Namespace Operation Flow

- `xfs_lookup`
  - Looks up a directory name, igets the target inode, and rejects regular directory entries pointing to metadata files.
- `xfs_create`
  - Allocates dquots, reserves a transaction, allocates an inode, joins parent/child inodes, creates the directory entry and parent pointer data, attaches quotas, commits, and returns the locked-created inode after setup.
- `xfs_create_tmpfile`
  - Allocates an inode as an unlinked tmpfile and commits it on the unlinked list.
- `xfs_link`
  - Attaches dquots, checks project inheritance constraints, adds the directory entry, and commits the link transaction.
- `xfs_remove`
  - Removes a child directory entry and updates link/unlinked state through directory helper code while respecting AGI-before-AGF lock ordering.
- `xfs_rename`
  - Handles normal rename, exchange, and whiteout. It sorts all participating inodes, allocates parent-pointer contexts, optionally allocates a tmpfile whiteout inode, reserves quota/blocks, locks AGIs before directory block changes when needed, and delegates directory mutation to `xfs_dir_rename_children`.

## Inactivation and Freeing

- `xfs_inode_needs_inactive` decides whether inactive cleanup must run before reclaim.
- `xfs_inactive` cancels COW reservations, frees EOF blocks for linked files, truncates unlinked regular files/directories/symlinks, removes attributes, and frees the inode.
- `xfs_inactive_dir` marks incore directory buffers stale before a recovered temporary directory is discarded.
- `xfs_inactive_truncate` logs zero size before freeing extents to avoid stale data exposure after crash.
- `xfs_inactive_ifree` removes the inode from unlinked lists and returns it to free inode btrees.
- `xfs_ifree` uninitializes the inode, clears owner-change replay bits, and frees the backing inode cluster when the chunk becomes empty.
- `xfs_ifree_cluster` locks inode cluster buffers, marks all incore inodes in the cluster stale, and invalidates/stales the buffer transactionally.

## Unlinked List Recovery

- `xfs_iunlink_lookup` searches the per-AG inode cache while the AGI stabilizes unlinked-list existence.
- `xfs_iunlink_reload_next` reloads missing unlinked inodes into cache, validates zero nlink, and reconstructs `i_prev_unlinked`.
- `xfs_inode_reload_unlinked_bucket` walks an AGI unlinked bucket and reloads missing incore list links.
- `xfs_inode_reload_unlinked` provides the transaction wrapper for one inode.

## Inode Flush Flow

- `xfs_iflush` validates incore inode/fork state, updates flush iteration for old dinodes, verifies local forks, copies dirty core/forks to the ondisk dinode, computes CRC, and moves `ili_fields` to `ili_last_fields`.
- `xfs_iflush_cluster` scans all inode log items attached to a cluster buffer, nonblocking-locks eligible inodes, aborts on shutdown, and queues a delayed-write buffer when at least one inode flushes.
- `xfs_iunpin_wait` forces the log for the inode commit sequence and waits for the pin count to reach zero.
- `xfs_log_force_inode` synchronously forces the log through the last commit sequence that touched the inode.

## Important Invariants

- Directory tree lookups must not expose metadata-directory inodes as normal files.
- Project-inheritance directories reject links/renames that would bypass tree quota, except for legacy project-less special files.
- Truncation callers must hold the inode lock exclusively, must use a permanent log reservation, and may receive a rolled transaction.
- Inactive cleanup skips internal metadata inodes because they require explicit resource cleanup elsewhere.
- Inode freeing must mark all cached inodes in a freed cluster stale; missing one can leave dirty stale inodes attached to invalid buffers.
- Flush clears dirty fields only after copying them to the buffer and relies on `ili_last_fields` until buffer I/O completion makes them durable.
- Layout breaking distinguishes write breaks from unmap breaks; DAX unmap breaks must also wait for busy DAX pages.

## Dependencies

This file integrates with directory code, parent pointers, attributes, symlinks, inode allocation, bmap and bmap btrees, reflink/COW, quotas, filestreams, log transactions, AIL, buffer items, health state, pNFS, DAX, and VFS lease/layout APIs.

## Research Notes

`xfs_inode.c` is the core behavioral hub for XFS inode operations. The main complexity is not the individual namespace operations but their ordering constraints: inode locks, AGI/AGF ordering, transaction rolling, dquot accounting, unlinked-list recovery, stale cluster invalidation, and log-item flush coordination all have to line up.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_inode.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_inode.h

## Purpose

Defines the kernel-only XFS incore inode structure, inode state flags, lock flags/subclasses, inline helpers, and core inode operation prototypes.

## Main Types

- `typedef struct xfs_inode`
  - Embeds the VFS inode.
  - Stores mount, dquots, inode number, imap, data/attr/COW forks, log item, inode locks, pin count, inactivation list node, health bitmaps, flags, block counts, project id, extent hints, metatype, unlinked-list pointers, and pending I/O completion state.
- `enum layout_break_reason`
  - `BREAK_WRITE`
  - `BREAK_UNMAP`

## Main Inline Helpers

- Fork access and sizing:
  - `xfs_inode_has_attr_fork`
  - `xfs_ifork_ptr`
  - `xfs_inode_fork_boff`
  - `xfs_inode_data_fork_size`
  - `xfs_inode_attr_fork_size`
  - `xfs_inode_fork_size`
- VFS/XFS conversions:
  - `XFS_I`
  - `VFS_I`
  - `VFS_IC`
- Size and EOF handling:
  - `XFS_ISIZE`
  - `xfs_new_eof`
- Flag manipulation:
  - `xfs_iflags_set`
  - `xfs_iflags_clear`
  - `xfs_iflags_test`
  - test-and-set/clear variants
- Feature checks:
  - reflink, metadata directory, internal inode, zoned realtime inode, COW inode, bigtime, large extent counts, big realtime allocation, hardware/software atomic write support.

## State Flags

Defines core incore inode flags, including:

- `XFS_IRECLAIM`
- `XFS_ISTALE`
- `XFS_IRECLAIMABLE`
- `XFS_INEW`
- `XFS_IFLUSHING`
- `XFS_IPINNED`
- `XFS_IEOFBLOCKS`
- `XFS_NEED_INACTIVE`
- `XFS_IRECOVERY`
- `XFS_ICOWBLOCKS`
- `XFS_INACTIVATING`
- `XFS_IQUOTAUNCHECKED`
- `XFS_IREMAPPING`

It also defines aggregate reset/reclaim masks.

## Locking API

Defines lock mode bits for:

- IOLOCK shared/exclusive
- ILOCK shared/exclusive
- MMAPLOCK shared/exclusive

Defines lockdep subclass encoding for parent locking, realtime metadata inodes, and inode-number ordered multi-inode locking.

## Main Prototypes

Exports inode operations for:

- namespace mutation: lookup, create, tmpfile, remove, link, rename
- locking: lock/unlock/demote/assert, shared map locks, multi-inode lock helpers
- truncation, freeing, creation, inactivation
- pin waiting, inode flush clustering, log force
- unlinked-list lookup/reload
- layout breaking
- quota allocation for creates
- block counting and allocation unit sizing

## Important Invariants

- `i_flags_lock` protects `i_flags`, `i_checked`, and `i_sick` updates.
- Unlinked-list pointer fields are updated only with AGI locking.
- `XFS_ISIZE` returns VFS size for regular files but disk size for other inode types.
- Internal inode detection changes depending on whether metadata directories are enabled.
- IOLOCK must be acquired before MMAPLOCK, and MMAPLOCK before ILOCK.
- Lock subclass fields are limited by lockdep subclass capacity.

## Research Notes

This header is the primary shared contract for XFS inode state. Its inline helpers encode many policy decisions, especially around internal metadata inodes, realtime/zoned behavior, COW semantics, and multi-lock ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item.c

## Purpose

Implements XFS inode log items: precommit synchronization, log vector sizing/formatting, pin/unpin behavior, AIL push support, commit sequence tracking, inode flush completion, flush abort, and old-format conversion.

## Main Responsibilities

- Defines `xfs_ili_cache` for `struct xfs_inode_log_item`.
- Provides `xfs_inode_item_ops` for transaction/log integration.
- Converts incore inode state into log dinode records and fork payload vectors.
- Coordinates dirty fields, last-flushed fields, flush LSNs, and buffer attachment.
- Tracks commit sequence numbers for fsync and datasync optimization.
- Handles inode log item pin/unpin and AIL push behavior.
- Completes inode buffer I/O by deleting flushed items from the AIL and clearing flush state.
- Aborts inode flush state during stale inode cleanup or shutdown.
- Converts 32-bit inode log format records to native format for recovery.

## Precommit Flow

`xfs_inode_item_precommit` runs before final transaction logging:

- Clears lazy timestamp dirty state from the VFS inode.
- Upgrades eligible inodes to bigtime format.
- Fixes invalid realtime inherited extent-size hints.
- Reads and attaches the inode cluster buffer to the log item if needed.
- Sets `ili_dirty_flags` and merges new logged fields with `ili_last_fields`.
- Converts iversion logging into core inode logging.
- Optionally verifies the generated dinode under expensive debug checks.

The sort key is inode number so precommit buffer locking happens in stable order.

## Formatting Flow

- `xfs_inode_item_size` accounts for format, core, and optional data/attr fork vectors.
- `xfs_inode_item_format_data_fork` formats extent arrays, btree roots, local data, or device payloads according to data fork format.
- `xfs_inode_item_format_attr_fork` formats attr fork extent arrays, btree roots, or local attr data.
- `xfs_inode_to_log_dinode` translates incore/VFS inode fields into the log dinode, including timestamps, owner ids, nlink, generation, size, blocks, flags, metatype, UUID, CRC placeholders, and extent counters.
- `xfs_inode_item_format` emits the format record, core record, and fork payloads, then updates the exact logged field mask.

## Pin, Push, and Commit Semantics

- `xfs_inode_item_pin` increments `i_pincount`.
- `xfs_inode_item_unpin` decrements the pin count, clears commit/datasync sequences at zero, and wakes waiters.
- `xfs_inode_item_push` tries to flush the inode cluster buffer from the AIL unless pinned, stale, locked, or already flushing.
- `xfs_inode_item_committed` skips AIL insertion for stale inodes and unpins directly.
- `xfs_inode_item_committing` records commit sequence numbers and only records datasync sequence numbers for changes beyond iversion/timestamp-only updates.
- `xfs_inode_item_release` unlocks inode locks held by the transaction item.

## Flush Completion and Abort

- `xfs_buf_inode_iodone` walks inode log items attached to an inode buffer, handles stale inodes, batches AIL updates, and finishes flush state.
- `xfs_iflush_ail_updates` deletes successfully flushed inode items from the AIL if their LSN has not changed.
- `xfs_iflush_finish` detaches clean inodes from the buffer, clears `ili_last_fields`, `ili_flush_lsn`, `XFS_LI_FLUSHING`, and `XFS_IFLUSHING`.
- `xfs_iflush_abort` removes an inode item from the AIL and clears buffer/field state while the cluster buffer is locked.
- `xfs_iflush_shutdown_abort` safely locks the cluster buffer from arbitrary shutdown context before aborting.

## Important Invariants

- Inode cluster buffer attachment is delayed until precommit to preserve AGI/AGF/buffer lock ordering.
- Inode fork logged size reflects current fork size, not the largest previous relogged size.
- Dirty inode fields cannot be forgotten until the backing inode buffer I/O completes; `ili_last_fields` preserves this relationship.
- A stale inode item must not be inserted into the AIL after its cluster buffer is freed.
- The inode log item may hold a buffer reference while attached to `bp->b_li_list`; cleanup must drop that reference exactly once.

## Dependencies

Uses transaction/log item infrastructure, buffer log item lists, AIL operations, inode fork conversion helpers, dinode verifiers, timestamp/iversion helpers, realtime bitmap include context, and shutdown/error handling.

## Research Notes

This file is the bridge between incore inode mutation and journal durability. The subtle logic is the three-way coordination among transaction commit, inode flush, and buffer I/O completion, especially when inodes are relogged while a previous flush is still outstanding.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item.h

## Purpose

Declares the XFS inode log item structure and the helper API for inode log item lifecycle, flush abort, and recovery-format conversion.

## Main Types

- `struct xfs_inode_log_item`
  - Embeds `struct xfs_log_item`.
  - Points back to the owning `struct xfs_inode`.
  - Tracks transaction-held inode lock flags and dirty flags.
  - Uses `ili_lock` to serialize dirty/flush state.
  - Tracks last flushed fields, current fields, flush LSN, commit sequence, and datasync sequence.

## Main API

- `xfs_inode_clean`
- `xfs_inode_item_init`
- `xfs_inode_item_destroy`
- `xfs_iflush_abort`
- `xfs_iflush_shutdown_abort`
- `xfs_inode_item_format_convert`
- `xfs_ili_cache`

## Important Invariants

- `ili_lock` protects interactions between dirty state and flush state because inode dirtying, flushing, and completion use different inode lock combinations.
- `ili_commit_seq` and `ili_datasync_seq` allow fsync/fdatasync paths to decide whether a log force is needed without checking pin state under ILOCK.
- `xfs_inode_clean` treats an inode without an item, or with no logged dirty fields, as clean.

## Research Notes

This header is the state contract consumed by transaction code, inode flush code, and fsync/log-force paths. The fields are intentionally fine-grained because correctness depends on distinguishing current dirty fields from fields already copied to an inode buffer but not yet durable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item.h -->