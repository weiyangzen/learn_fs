# subset-b-005796 research

Grouped research report for XFS inode, inode-cache, inode-log, hook, and health monitor files under `sources/distributed-fs/ceph-client/fs/xfs`. Each section is delimited for reconciliation into the source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_healthmon.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_healthmon.c

## Purpose
`xfs_healthmon.c` implements the live XFS health monitor anonymous file descriptor returned by `XFS_IOC_HEALTH_MONITOR`. It lets privileged userspace, specifically a filesystem healer/monitor daemon, subscribe to kernel events about filesystem health state, shutdown reasons, media errors, file range I/O failures, lost events, and unmount. The full 1260-line file was read.

## Important APIs, Types, and Functions
The mount-facing API consists of `xfs_ioc_health_monitor`, `xfs_healthmon_unmount`, `xfs_healthmon_report_fs`, `xfs_healthmon_report_group`, `xfs_healthmon_report_inode`, `xfs_healthmon_report_shutdown`, `xfs_healthmon_report_media`, and `xfs_healthmon_report_file_ioerror`. Object lifetime is handled by `xfs_healthmon_get`, `xfs_healthmon_put`, `xfs_healthmon_attach`, and `xfs_healthmon_detach`.

Queue handling is centered on `xfs_healthmon_push`, `xfs_healthmon_merge_events`, `xfs_healthmon_clear_lost_prev`, `__xfs_healthmon_insert`, and `__xfs_healthmon_push`. Userspace delivery is handled by `xfs_healthmon_read_iter`, `xfs_healthmon_poll`, `xfs_healthmon_format_v0`, `xfs_healthmon_copybuf`, `xfs_healthmon_format_pop`, and `xfs_healthmon_alloc_outbuf`. Reconfiguration and validation use `xfs_healthmon_validate`, `xfs_healthmon_reconfigure`, `xfs_healthmon_file_on_monitored_fs`, and `xfs_healthmon_ioctl`.

## Control Flow
`xfs_ioc_health_monitor` validates CAP_SYS_ADMIN, root-inode use, initial user namespace, format, flags, and zero padding. It allocates `struct xfs_healthmon`, queues an initial `RUNNING` event, preallocates an `UNMOUNT` event so unmount notification cannot fail later, attaches the monitor to `mp->m_healthmon`, and finally installs an anon inode fd.

Report functions take a ref to the monitor through RCU, build a stack event, optionally filter metadata masks via `metadata_event_mask`, and queue it. Queueing first emits any prior lost-event count, tries to merge with the last queued event, enforces `XFS_HEALTHMON_MAX_EVENTS`, and accounts dropped events through `lost_prev_event` and `total_lost`.

Reads wait for queued events, detached EOF, or buffered bytes. The read path serializes formatting with the anonymous inode lock, drains any prior output buffer bytes, pops queued events under `hm->lock`, converts them to `struct xfs_health_monitor_event` v0 records, copies to the caller iterator, and resets buffer cursors when empty. Poll reports `EPOLLIN` when event data or detach state is visible.

## State and Persistence Behavior
All health monitor state is memory resident. The weak mount association is represented by `mount_cookie`, which stores `mp->m_super` while attached and zero after detach; the code explicitly says not to dereference it except while synchronized with detach logic. `mp->m_healthmon` is RCU protected and pointer updates are serialized by `xfs_healthmon_lock`. The open fd, the mount attachment, and running event handlers hold references.

Events are heap objects on a singly linked queue with total and lost counters. `hm->buffer`, `bufhead`, and `buftail` persist partially formatted read data across short reads. No filesystem metadata is written by this file, though it exposes persistent-health observations and shutdown/media fault signals to userspace.

## Dependencies and Integration Points
The file integrates with XFS health flag translation (`xfs_healthmon_fs_mask`, per-AG, rtgroup, inode masks), mount state (`mp->m_healthmon`), anon inode fd creation, VFS file operations, poll/eventpoll, Linux `fserror` events, shutdown flag definitions, media device selection, tracepoints, and ioctls from `xfs_fs.h`/`xfs_ioctl.h`. It is a consumer of health reports from scrub/repair/metadata checking, buffer and direct I/O error notification, media failure reporting, and unmount.

## Risks and Edge Cases
Lifetime correctness is central: the monitor can outlive the mount, event reporters race with detach, and unmount must still wake readers. Queue capacity and allocation failure intentionally lose events but must preserve a later `LOST` count. Event merging must not combine unrelated inode generations, group numbers, file ranges, or devices. The read path must not return stale buffered data incorrectly after detach, and short userspace buffers require stable buffer cursor handling. The ioctl surface is deliberately privileged and format-versioned; accepting bad padding or unsupported flags would weaken ABI validation.

## Test Signals
Useful tests include creating a monitor only as init-namespace CAP_SYS_ADMIN on the root inode, double-monitor attach returning `-EEXIST`, first read returning `RUNNING`, poll wakeups after health events, verbose versus non-verbose health mask filtering, merged adjacent media and file-range errors, queue overflow producing a later lost-event record, short-buffer reads over multiple calls, fdinfo state/counters, `XFS_IOC_HEALTH_FD_ON_MONITORED_FS` success and `-ESTALE`, unmount injecting the preallocated event and later EOF, and racing fd close with unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_healthmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_healthmon.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_healthmon.h

## Purpose
`xfs_healthmon.h` defines the in-kernel state, event taxonomy, event payload layout, and reporting entry points for XFS live health monitoring. The complete 184-line header was read.

## Important APIs, Types, and Functions
`struct xfs_healthmon` is the monitor object attached weakly to an XFS mount. It contains the mount cookie, device number, reference count, event queue lock, first/last event pointers, preallocated unmount event, queue counters, verbose flag, wait queue, read formatting buffer, and total/lost counters.

`enum xfs_healthmon_type` names event types such as `RUNNING`, `LOST`, `UNMOUNT`, `SHUTDOWN`, `SICK`, `CORRUPT`, `HEALTHY`, `MEDIA_ERROR`, buffered/direct I/O errors, and data loss. `enum xfs_healthmon_domain` scopes events to mount, filesystem, allocation group, inode, realtime group, data/realtime/log devices, or file ranges. `struct xfs_healthmon_event` is a tagged union containing payloads for lost counts, metadata masks, group ids, inode id/generation, shutdown flags, media sector ranges, and file error ranges.

## Control Flow
The header declares report functions that filesystem subsystems call at event points. Consumers do not format userspace ABI structures directly; they pass native XFS event fields into `xfs_healthmon_report_*`, while `xfs_ioc_health_monitor` creates the file descriptor and `xfs_healthmon_unmount` detaches and notifies readers.

## State and Persistence Behavior
The structures are entirely incore. The queue and buffer fields define how reports survive until userspace reads them, while `total_events`, `total_lost`, and `lost_prev_event` keep accounting across event drops. The `mount_cookie` is intentionally a weak reference to prevent the monitor fd from pinning the filesystem.

## Dependencies and Integration Points
The header depends on XFS mount, inode, group, device, and health flag types plus the userspace ioctl structures in XFS headers. It is included by the health monitor implementation and by XFS subsystems that emit health, media, shutdown, or file I/O error events.

## Risks and Edge Cases
The event union relies on correct pairing of type and domain with payload fields. New event types or domains require synchronized updates to the enum, formatting maps, merge logic, tracepoints, and userspace ABI translation. The header documents that `mount_cookie` must not be dereferenced casually; violating that contract risks UAF after unmount.

## Test Signals
Compile-time coverage should catch missing prototypes and enum map updates. Runtime tests should verify all declared report APIs generate the expected domain/type/payload combinations and that ABI formatting remains stable when new enum values are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_healthmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_hooks.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_hooks.c

## Purpose
`xfs_hooks.c` provides a tiny wrapper around Linux blocking notifier chains for optional XFS live hook points. The full 52-line file was read.

## Important APIs, Types, and Functions
The exported helpers are `xfs_hooks_init`, `xfs_hooks_add`, `xfs_hooks_del`, and `xfs_hooks_call`. `xfs_hooks_add` asserts that the embedded notifier callback is set and uses a build-time assertion that `struct xfs_hook.nb` starts at offset zero, allowing notifier calls to be treated as hook calls by container layout.

## Control Flow
Callers initialize a hook chain with `BLOCKING_INIT_NOTIFIER_HEAD`, register hook objects with `blocking_notifier_chain_register`, unregister them with `blocking_notifier_chain_unregister`, and invoke all listeners with `blocking_notifier_call_chain`. The call result is the final notifier return code.

## State and Persistence Behavior
State is purely memory resident in the notifier chain and registered hook objects. There is no filesystem metadata persistence. Blocking notifier chains internally serialize registration and callback dispatch through kernel notifier infrastructure.

## Dependencies and Integration Points
This file depends on Linux notifier APIs and XFS wrapper types from `xfs_hooks.h`. It is compiled only when live hooks are enabled by configuration and is intended for XFS features that need dynamic hook registration around live repair or observability points.

## Risks and Edge Cases
Callbacks run under blocking notifier semantics and therefore can sleep, but hook users must still respect the lock context of the hook point. Registering hooks while holding locks that interact badly with jump-label static key changes is a risk described in the header. A hook object with an unset callback is a hard assertion failure.

## Test Signals
Tests should initialize a chain, register multiple hooks, verify call order/return propagation, unregister hooks, and confirm no callbacks run after deletion. Configuration tests should cover builds with and without `CONFIG_XFS_LIVE_HOOKS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_hooks.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_hooks.h

## Purpose
`xfs_hooks.h` declares the optional XFS live hook abstraction and its compile-time no-op fallback. The complete 65-line header was read.

## Important APIs, Types, and Functions
When `CONFIG_XFS_LIVE_HOOKS` is enabled, `struct xfs_hooks` wraps `struct blocking_notifier_head`, and `struct xfs_hook` embeds `struct notifier_block` as its first member. `xfs_hook_setup` initializes the callback and priority. The header declares `xfs_hooks_init`, `xfs_hooks_add`, `xfs_hooks_del`, and `xfs_hooks_call`.

The static-key helpers `DEFINE_STATIC_XFS_HOOK_SWITCH`, `xfs_hooks_switch_on`, `xfs_hooks_switch_off`, and `xfs_hooks_switched_on` let hook sites skip notifier overhead when no hooks are active. Without the config option, hooks are empty/no-op and calls return `NOTIFY_DONE`.

## Control Flow
Feature code can guard hook calls with the static branch and then dispatch a notifier chain. Registration paths can turn the branch on and off around adding or removing hooks. In no-op builds the same call sites compile away to minimal code.

## State and Persistence Behavior
All state is runtime-only: notifier heads, hook objects, and static keys. The file defines no persistent XFS data format.

## Dependencies and Integration Points
The header integrates with Linux static keys, jump labels, blocking notifier chains, and XFS live hook users. The comment explicitly warns that static key patching takes the CPU hotplug lock, so callers must consider memory reclaim/writeback lock interactions when enabling/disabling hooks.

## Risks and Edge Cases
The first-member layout of `struct xfs_hook` is part of the ABI between XFS wrappers and notifier code. Static key toggling in the wrong lock context can deadlock with CPU hotplug or memory reclaim. No-op builds must preserve source compatibility for call sites that expect hook APIs to exist.

## Test Signals
Build coverage should include both config paths. Runtime checks should verify static-branch state tracks hook registration, hook callbacks receive action and private data, and no-op builds return `NOTIFY_DONE` without needing notifier storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_hooks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_icache.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_icache.c

## Purpose
`xfs_icache.c` implements XFS in-core inode allocation, lookup, recycling, reclaim, inode-cache walking, speculative preallocation garbage collection, deferred inode inactivation, and the inodegc shrinker. It is the main memory-lifetime and background-cleanup manager for XFS inodes. The full 2354-line file was read.

## Important APIs, Types, and Functions
Public APIs include `xfs_inode_alloc`, `xfs_inode_free`, `xfs_iget`, `xfs_trans_metafile_iget`, `xfs_metafile_iget`, reclaim functions (`xfs_reclaim_worker`, `xfs_reclaim_inodes`, `xfs_reclaim_inodes_nr`, `xfs_reclaim_inodes_count`, `xfs_inode_mark_reclaimable`), blockgc functions (`xfs_inode_set_eofblocks_tag`, `xfs_inode_clear_eofblocks_tag`, `xfs_inode_set_cowblocks_tag`, `xfs_inode_clear_cowblocks_tag`, `xfs_blockgc_worker`, `xfs_blockgc_stop`, `xfs_blockgc_start`, `xfs_blockgc_free_space`, `xfs_blockgc_flush_all`, `xfs_blockgc_free_dquots`, `xfs_blockgc_free_quota`), and inodegc functions (`xfs_inodegc_worker`, `xfs_inodegc_push`, `xfs_inodegc_flush`, `xfs_inodegc_stop`, `xfs_inodegc_start`, `xfs_inodegc_register_shrinker`).

Internal machinery includes per-AG radix tree tags `XFS_ICI_RECLAIM_TAG` and `XFS_ICI_BLOCKGC_TAG`, per-mount xarray marks, `xfs_perag_set_inode_tag`, `xfs_perag_clear_inode_tag`, `xfs_iget_cache_hit`, `xfs_iget_cache_miss`, `xfs_iget_recycle`, `xfs_reclaim_inode`, `xfs_icwalk_ag`, `xfs_icwalk`, `xfs_blockgc_igrab`, `xfs_blockgc_scan_inode`, `xfs_inode_free_eofblocks`, and `xfs_inode_free_cowblocks`.

## Control Flow
`xfs_iget` validates the inode number, finds the containing per-AG structure, and looks up the agino in the per-AG radix tree under RCU. Cache hits are screened for stale RCU objects, `XFS_INEW`, reclaim, inactivation, free-state mismatches, and reclaimable recycling. Cache misses allocate a fresh inode, map it to disk, optionally read the disk inode, check free/allocated state, preload the radix tree, lock as requested, and insert under the per-AG lock.

Reclaim starts when `xfs_inode_mark_reclaimable` either queues inodegc for inactivation or directly tags the inode reclaimable. Reclaim workers and shrinkers walk marked per-AG trees in batches, grab eligible inodes by setting `XFS_IRECLAIM`, flush AIL as needed, skip pinned or dirty inodes, remove clean reclaimable inodes from the radix tree, and free them through RCU.

Blockgc tags inodes with post-EOF or COW preallocations. Background or synchronous scans grab safe live inodes, filter by quota/user/group/project/min-size criteria, take IO/MMAP locks as needed, free EOF blocks, cancel idle COW reservations, clear tags when stale, and flush inodegc at the end of synchronous space reclamation.

Inodegc queues unreferenced inodes needing metadata cleanup to per-CPU llist work items. Workers set `XFS_INACTIVATING`, run `xfs_inactive`, mark the inode reclaimable, and record errors. Stop/start/flush routines coordinate delayed work, mount state, and shrinker-triggered throttling.

## State and Persistence Behavior
The file manages incore state: `struct xfs_inode` initialization, VFS inode state, fork memory, dquot attachment pointers, inode flags, sickness bits, per-AG radix tree membership, per-AG reclaimable counts, blockgc/reclaim xarray marks, delayed work state, per-CPU inodegc lists, and shrinker private data. It does not directly define on-disk formats, but it triggers persistent metadata updates through `xfs_inactive`, EOF/COW block freeing, transaction commits, dquot updates, and log/AIL pushes.

RCU freeing is used so lookup can safely see objects until grace periods complete. Inode numbers are set to zero before free to detect stale RCU lookups. Reclaim and blockgc tags bridge inode flags to per-AG scans and mount-level work scheduling.

## Dependencies and Integration Points
This file integrates with VFS inode allocation and `iput`, XFS inode buffer conversion, imap, transactions, quota/dquot code, AIL/log forcing, per-AG group management, radix trees/xarrays, reflink COW cancellation, bmap EOF freeing, health marking, metadata inodes, delayed workqueues, shrinker APIs, memory reclaim NOFS context, and mount tunables such as blockgc/inodegc enablement.

## Risks and Edge Cases
The highest-risk areas are lock/RCU ordering during cache lookup and reclaim, recycling reclaimable inodes, avoiding deadlock with inodegc while creating inodes, and not reclaiming sick inodes except during unmount/norecovery/shutdown. Dirty, pinned, flushing, or stale inodes must not be freed. Blockgc cannot free COW fork blocks under active writeback or direct I/O. Inodegc queue throttling must avoid NOFS deadlocks. Per-AG tag counts must stay balanced or background workers and shrinkers will either spin or miss reclaimable work.

## Test Signals
Tests should cover cache hit, miss, stale RCU lookup, inode recycling, `XFS_IGET_CREATE`, `XFS_IGET_INCORE`, noretry behavior, malformed free/allocated state detection, metadata inode type validation, reclaim of clean inodes, shutdown reclaim of dirty/sick inodes, blockgc EOF and COW cleanup under sync and background modes, quota-triggered blockgc filters, inodegc start/stop/flush races, shrinker-triggered inodegc throttling, unmount draining, and tag/count balance assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_icache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_icache.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_icache.h

## Purpose
`xfs_icache.h` declares the public inode cache, inode reclaim, block garbage collection, and inodegc interfaces used throughout XFS. The full 84-line header was read.

## Important APIs, Types, and Functions
`struct xfs_icwalk` packages inode-walk filters: flags, uid, gid, project id, minimum file size, and scan limit. Public flags include sync mode, uid/gid/project filtering, and minimum file size filtering. `XFS_IGET_*` flags control inode lookup creation, untrusted lookup, dontcache behavior, incore-only lookup, and noretry behavior.

The header declares inode allocation/free and lookup (`xfs_inode_alloc`, `xfs_inode_free`, `xfs_iget`), reclaim (`xfs_reclaim_worker`, `xfs_reclaim_inodes`, `xfs_reclaim_inodes_count`, `xfs_reclaim_inodes_nr`, `xfs_inode_mark_reclaimable`), blockgc (`xfs_blockgc_free_dquots`, `xfs_blockgc_free_quota`, `xfs_blockgc_free_space`, `xfs_blockgc_flush_all`, tag setters/clearers, worker stop/start), and inodegc (`xfs_inodegc_worker`, push/flush/stop/start, shrinker registration).

## Control Flow
Callers use `xfs_iget` to obtain in-core inodes under requested locks, use tag setters to schedule EOF/COW block cleanup, and use inodegc/reclaim interfaces to transition unused inodes through inactivation to reclaimable cache entries and final free.

## State and Persistence Behavior
The header exposes flags and APIs that drive incore inode state transitions. Persistence happens indirectly through the implementation when inode inactivation, EOF/COW cleanup, quota changes, or log pushes commit metadata updates.

## Dependencies and Integration Points
The declarations are used by VFS operation code, transaction code, reclaim shrinkers, quota allocation retry paths, unmount/remount code, speculative preallocation cleanup, and inode lifetime management.

## Risks and Edge Cases
Misusing `XFS_IGET_CREATE`, `XFS_IGET_UNTRUSTED`, or `XFS_IGET_INCORE` can produce incorrect corruption handling or lookup semantics. The header notes that blockgc synchronous scans must not be called while holding inode ILOCK/IOLOCK/MMAPLOCK. Filter flags must remain disjoint from private implementation flags.

## Test Signals
Build and API tests should validate flag combinations, incore-only lookup, no-retry lookup under contention, blockgc scans filtered by uid/gid/project/min-size, and shrinker registration during mount/unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_icache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_icreate_item.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_icreate_item.c

## Purpose
`xfs_icreate_item.c` implements the XFS inode-create log item. It records newly initialized inode chunks compactly in the journal and replays them during log recovery as initialized inode cluster buffers. The complete 260-line file was read.

## Important APIs, Types, and Functions
`xfs_icreate_log` creates and joins an `XFS_LI_ICREATE` log item to a transaction. The log item ops are `xfs_icreate_item_size`, `xfs_icreate_item_format`, and `xfs_icreate_item_release`, with `XFS_ITEM_RELEASE_WHEN_COMMITTED`. Recovery is handled by `xlog_icreate_item_ops`, `xlog_recover_icreate_reorder`, and `xlog_recover_icreate_commit_pass2`.

## Control Flow
At inode allocation time, `xfs_icreate_log` allocates from `xfs_icreate_cache`, initializes the log item, fills `struct xfs_icreate_log` with AG number, AG block, inode count, inode size, extent length, and generation in big endian, joins it to the transaction, marks the transaction dirty, and sets the item dirty bit.

During recovery, icreate items are reordered with buffers because they are equivalent to logged initialized inode buffers and must replay before later inode items modify those buffers. Pass2 validates type, size, AG number, AG block, inode size, count, length, supported chunk length, count/length consistency, and buffer cancellation state. If the inode cluster buffers were canceled, replay is skipped; otherwise recovery calls `xfs_ialloc_inode_init` to stamp initialized inodes into delayed-write buffers.

## State and Persistence Behavior
The persistent journal record is `struct xfs_icreate_log`. It avoids logging entire initialized inode buffers during normal operation but reconstructs them at recovery time. Recovery writes initialized inode buffers through the buffer list so later recovered inode items can modify cached buffers instead of operating on uninitialized media.

## Dependencies and Integration Points
The file integrates with XFS transactions, log item formatting, log recovery ordering, inode allocation geometry, cancellation tracking, buffer recovery lists, `xfs_ialloc_inode_init`, tracepoints, and the slab cache `xfs_icreate_cache`.

## Risks and Edge Cases
Recovery must reject malformed records before initializing inode clusters. Count/length mismatches or unsupported sparse/full allocation lengths indicate corruption. Partial cancellation is suspicious; current code skips replay if any cluster buffer is canceled and warns if only some are canceled. Recovery ordering is critical because subsequent inode item replay assumes the inode buffers already exist.

## Test Signals
Tests should cover normal inode allocation log formatting, recovery replay of full and sparse chunks, invalid type/size/agno/agbno/isize/count/length records, count-length inconsistency, buffer cancellation skip, partial cancellation warning, and ordering relative to later inode item replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_icreate_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_icreate_item.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_icreate_item.h

## Purpose
`xfs_icreate_item.h` declares the in-memory icreate log item and the API for logging inode chunk creation. The complete 22-line header was read.

## Important APIs, Types, and Functions
`struct xfs_icreate_item` embeds a generic `struct xfs_log_item` and the formatted `struct xfs_icreate_log`. The header declares the global slab cache `xfs_icreate_cache` and `xfs_icreate_log`.

## Control Flow
Inode allocation code calls `xfs_icreate_log` with transaction, AG location, inode count, inode size, allocation length, and generation. The implementation owns allocation, formatting, transaction joining, and later recovery behavior.

## State and Persistence Behavior
The header defines only the incore wrapper for a journal record. Persistent behavior is the log item record that recovery interprets to initialize inode chunks.

## Dependencies and Integration Points
It is used by inode allocation and transaction code that needs compact inode-create logging. It depends on XFS transaction, AG, inode geometry, and log item types supplied by other XFS headers.

## Risks and Edge Cases
The header is small, but callers must pass geometry-consistent values because recovery validates and depends on them. Slab cache initialization/teardown must match use of `xfs_icreate_cache`.

## Test Signals
Compile coverage of callers, slab cache lifetime tests, and recovery tests for records produced by `xfs_icreate_log` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_icreate_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_inode.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_inode.c

## Purpose
`xfs_inode.c` implements core XFS inode operations: inode lock orchestration, directory lookup, create/tmpfile/link/remove/rename, truncate and inactivation, inode freeing and stale cluster handling, inode flush to disk buffers, unlinked-list reload, DAX/layout break helpers, and assorted inode utilities. The full 3066-line file was read.

## Important APIs, Types, and Functions
Locking APIs include `xfs_ilock`, `xfs_ilock_nowait`, `xfs_iunlock`, `xfs_ilock_demote`, `xfs_assert_ilocked`, `xfs_lock_inodes`, and `xfs_lock_two_inodes`. Lookup and namespace operations include `xfs_lookup`, `xfs_icreate`, `xfs_icreate_dqalloc`, `xfs_create`, `xfs_create_tmpfile`, `xfs_link`, `xfs_remove`, and `xfs_rename`.

Cleanup and persistence functions include `xfs_itruncate_extents_flags`, `xfs_inactive`, `xfs_inode_needs_inactive`, `xfs_ifree`, `xfs_iflush_cluster`, `xfs_log_force_inode`, and `xfs_irele`. Unlinked-list and stale-inode helpers include `xfs_iunlink_lookup`, `xfs_iunlink_reload_next`, `xfs_inode_reload_unlinked_bucket`, `xfs_inode_reload_unlinked`, `xfs_ifree_mark_inode_stale`, and `xfs_ifree_cluster`. Layout helpers include `xfs_ilock2_io_mmap`, `xfs_iunlock2_io_mmap`, `xfs_iunlock2_remapping`, `xfs_break_dax_layouts`, and `xfs_break_layouts`.

## Control Flow
The lock helpers impose XFS lock order: VFS `i_rwsem`/IOLOCK first, mapping `invalidate_lock`/MMAPLOCK second, XFS `i_lock`/ILOCK last. Multi-inode locking sorts by inode number and uses trylock/retry when earlier locked inodes are in the AIL to avoid log tail deadlocks.

Creation allocates dquots, parent-pointer context, transaction reservations, the new inode number, and the in-core inode; joins parent and child to the transaction; updates directory and parent metadata; attaches dquots; commits; and returns the new inode locked/initialized for VFS setup. Tmpfile creation allocates an unlinked inode. Link/remove/rename similarly coordinate quota attachment, parent pointers, directory operations, log reservations, AGI locking order, synchronous mount flags, and transaction commit/cancel unwinding.

Inactivation runs when an inode loses its last reference and needs persistent cleanup. It records unresolved health, skips read-only/internal/shutdown cases, cancels COW reservations, frees EOF blocks, truncates unlinked regular/directories/symlinks, removes attributes, and frees the inode from allocation metadata. Inode freeing uninitializes the inode, updates quota, removes it from unlinked lists, and can stale entire inode cluster buffers while marking all cached cluster inodes stale.

Flush paths convert dirty incore inode fields and forks into an inode cluster buffer. `xfs_iflush_cluster` nonblockingly scans all inode log items attached to a buffer, locks clean candidates, calls `xfs_iflush`, and queues the buffer for writeback through AIL push machinery.

## State and Persistence Behavior
This file is a primary persistence bridge. It commits namespace changes, link counts, inode core changes, fork truncation, attribute removal, quota accounting, unlinked-list updates, inode free state, and flushed dinodes. It mutates incore inode flags such as `XFS_ISTALE`, `XFS_IFLUSHING`, `XFS_IREMAPPING`, `XFS_IQUOTAUNCHECKED`, sickness bits, fork state, generation, nlink, dquot attachment, and transaction log item state.

Crash consistency depends on transaction reservations, log item ordering, AGI-before-AGF lock order, inode cluster buffer staling, and logging inode size before truncating blocks to avoid stale data exposure. Unlinked-list reload can reconstruct incore previous pointers after recovery finds unrecovered unlinked inodes.

## Dependencies and Integration Points
The file integrates with VFS inode locks and leases, pagecache invalidation, DAX layout breaking, XFS transactions/defer ops, directory code, parent pointers, symlinks, attributes, quota, filestreams, inode allocation/freeing, bmap/truncate, reflink COW, AGI/AGF buffers, log/AIL, inode item flushing, health marking, realtime and zoned behavior, metadata inodes, and trace/error injection infrastructure.

## Risks and Edge Cases
Lock ordering is the dominant risk: IOLOCK/MMAPLOCK/ILOCK nesting, AGI-before-AGF, inode cluster buffers locked late, and multi-inode AIL interactions must remain consistent. Namespace operations have complex unwind paths with locked inodes, dquot references, parent-pointer contexts, and temporary whiteout inodes. Inactivation must not write on read-only mounts except recovery, must not process internal metadata inodes, and must handle quotacheck and unlinked inodes correctly. Staling inode clusters must find every cached inode in the cluster or stale dirty inodes can survive incorrectly. Flush corruption checks must shut down safely before failed buffers can move the log tail incorrectly.

## Test Signals
Test signals include lockdep runs for create/link/remove/rename/exchange/whiteout/remap paths, xfstests for tmpfile and parent pointers, quota low-space retry and reservationless directory updates, unlink and unmount inactivation, crash recovery of unlinked lists and inode frees, stale inode cluster writeback, forced `xfs_iflush` error tags, DAX layout break retries, project quota inheritance failures, metadata inode lookup rejection from normal directories, and fsync/log force behavior after inode modifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_inode.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_inode.h

## Purpose
`xfs_inode.h` defines the core in-memory XFS inode structure, inode flag and locking contracts, convenience helpers, and public inode operation prototypes. The full 679-line header was read.

## Important APIs, Types, and Functions
`typedef struct xfs_inode` embeds mount pointer, dquot pointers, inode number and disk mapping, data/attr/COW forks, log item pointer, locks, pin count, inodegc list node, health state, flags, delayed block count, disk size, block counts, project id, extent hints, fork offset, metadata type, dinode flags, unlinked-list pointers, embedded VFS inode, and pending I/O completion work.

Important inline helpers include `XFS_I`, `VFS_I`, `VFS_IC`, `XFS_ISIZE`, `xfs_new_eof`, `xfs_iflags_*`, `xfs_is_reflink_inode`, `xfs_is_metadir_inode`, `xfs_is_internal_inode`, `xfs_is_zoned_inode`, `xfs_is_cow_inode`, `xfs_inode_has_filedata`, `xfs_inode_has_cow_data`, `xfs_inode_has_bigtime`, `xfs_inode_has_large_extent_counts`, `xfs_inode_buftarg`, atomic write capability checks, `xfs_finish_inode_setup`, and `xfs_setup_existing_inode`.

The header defines incore flags (`XFS_IRECLAIM`, `XFS_ISTALE`, `XFS_IRECLAIMABLE`, `XFS_INEW`, `XFS_IFLUSHING`, `XFS_NEED_INACTIVE`, `XFS_INACTIVATING`, `XFS_IREMAPPING`, and more), lock flags for IOLOCK/ILOCK/MMAPLOCK modes, lockdep subclass fields, and layout break reasons.

## Control Flow
Most source files use this header to transition between XFS and VFS inodes, test or mutate inode flags under `i_flags_lock`, choose forks, determine data size semantics, choose data/realtime devices, and enforce lock ordering. Public prototypes expose namespace operations, locking, truncation, inode free, log force, inactivation, unlinked-list reload, remap locks, fork-zap checks, block accounting, and create-time dquot allocation.

## State and Persistence Behavior
`struct xfs_inode` is the authoritative incore shadow of persistent dinode state and related runtime-only state. Persistent fields include disk size, block counts, forks, project id, extent hints, flags, creation time, metadata type, unlinked pointers, and VFS inode mode/uid/gid/nlink/times/generation. Runtime-only fields include locks, health bits, reclaim/inactivation/remap/flush flags, dquot pointers, COW fork pointer, delayed block counters, and workqueue state.

## Dependencies and Integration Points
The header is included across nearly all XFS subsystems: VFS operations, inode cache, inode item logging, bmap, directory, attributes, reflink, quota, recovery, health, realtime, metadata directory, DAX/layout code, and writeback. It also encodes lock ordering assumptions used by lockdep and by multi-inode transaction code.

## Risks and Edge Cases
Flag operations must hold `i_flags_lock` unless documented otherwise. `XFS_ISIZE` differs for regular files because VFS `i_size` can be newer than `i_disk_size`; using the wrong size risks stale exposure or missed truncation. Lock subclass bit fields are tight due to lockdep limits. Internal inode detection changes with metadata directory support. COW and realtime/zoned helpers affect allocation and write semantics; mistakes can free or write the wrong fork/device.

## Test Signals
Test coverage should include flag transition assertions, lockdep validation for nested locks, regular versus non-regular size behavior, internal inode detection with and without metadata directories, fork size helpers with and without attr forks, COW/reflink/zoned predicates, atomic write capability, and inode setup completion clearing `XFS_INEW`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_inode_item.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_inode_item.c

## Purpose
`xfs_inode_item.c` implements the XFS inode log item. It decides how dirty inode state is precommitted, formatted into journal vectors, pinned/unpinned, pushed from the AIL, released, and completed after inode-buffer writeback. The complete 1241-line file was read.

## Important APIs, Types, and Functions
Log item ops include `xfs_inode_item_sort`, `xfs_inode_item_precommit`, `xfs_inode_item_size`, `xfs_inode_item_format`, `xfs_inode_item_pin`, `xfs_inode_item_unpin`, `xfs_inode_item_release`, `xfs_inode_item_committed`, `xfs_inode_item_push`, and `xfs_inode_item_committing`. Public lifecycle helpers are `xfs_inode_item_init`, `xfs_inode_item_destroy`, `xfs_buf_inode_iodone`, `xfs_iflush_abort`, `xfs_iflush_shutdown_abort`, and `xfs_inode_item_format_convert`.

Formatting helpers include data/attr fork sizing and formatting, `xfs_inode_to_log_dinode_ts`, `xfs_copy_dm_fields_to_log_dinode`, `xfs_inode_to_log_dinode_iext_counters`, `xfs_inode_to_log_dinode`, and `xfs_inode_item_format_core`. Flush completion helpers include `xfs_iflush_ail_updates`, `xfs_iflush_finish`, and `xfs_iflush_abort_clean`.

## Control Flow
Precommit applies final inode state changes before logging: clears lazytime dirty state, upgrades eligible inodes to bigtime, repairs invalid realtime inherited extent hints, attaches and pins the inode cluster buffer if needed, records dirty flags for later fsync/datasync sequencing, converts iversion-only logging into core logging, and merges `ili_last_fields` so relogging remains crash safe.

Size/format operations emit one format vector, the inode core, and optional data/attr fork vectors depending on fork format and dirty fields. The formatter copies extents, btree roots, local data, device ids, timestamps, DM fields, extent counters, v3 metadata, UUID, LSN, and metadata type into log-format structures.

During commit, pin increments the inode pin count; committing records commit sequence numbers for fsync/datasync optimization and releases inode locks; committed suppresses AIL insertion for stale inodes; unpin clears commit sequence numbers on the last unpin. AIL push locks the cluster buffer, calls `xfs_iflush_cluster`, and queues the buffer for delayed write. Buffer iodone removes flushed inode items from the AIL when their flush LSN still matches and clears flush state or aborts stale items.

## State and Persistence Behavior
The inode log item tracks `ili_fields`, `ili_last_fields`, `ili_dirty_flags`, `ili_lock_flags`, `ili_flush_lsn`, commit sequences, AIL membership, pin count, and the attached inode cluster buffer. Persistent output is the journal representation of inode core/fork changes and later the on-disk dinode written by the buffer flush path. The `ili_last_fields` mechanism prevents dropping logged fields before the corresponding inode buffer write reaches disk.

## Dependencies and Integration Points
The file integrates with XFS transactions/CIL, log item ops, AIL push, inode cluster buffers, `xfs_iflush_cluster`, VFS timestamps and iversion, bigtime and large extent count features, realtime extent rules, DM field preservation, inode fork helpers, buffer iodone callbacks, shutdown handling, and 32-bit log format recovery conversion.

## Risks and Edge Cases
Late cluster-buffer attachment exists to maintain AGI -> AGF -> inode cluster buffer lock order; moving it earlier can deadlock. Formatting must avoid leaking uninitialized data and must keep format sizes consistent with actual copied fork data. Dirty fields, last fields, AIL deletion, buffer references, and flush flags are tightly synchronized; mistakes can leave clean stale inodes in the AIL, lose inode updates after relogging, or double-release buffers. Shutdown abort must safely lock or reference cluster buffers from arbitrary context.

## Test Signals
Tests should cover inode core-only logging, extent/local/btree data and attr fork logging, device inode logging, bigtime upgrade, invalid rtinherit hint cleanup, DM field preservation, fsync/datasync sequence behavior, AIL push of pinned/locked/flushing/stale items, inode buffer iodone after relogging, stale inode abort during cluster free, shutdown abort races, and 32-bit inode log format conversion during recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_inode_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_inode_item.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_inode_item.h

## Purpose
`xfs_inode_item.h` declares the in-memory inode log item, its clean-state helper, public lifecycle/abort functions, format conversion helper, and slab cache. The full 62-line header was read.

## Important APIs, Types, and Functions
`struct xfs_inode_log_item` embeds the generic log item, back pointer to `struct xfs_inode`, lock flags, per-transaction dirty flags, `ili_lock`, last flushed fields, currently logged fields, last flush LSN, and commit sequence numbers for fsync/datasync optimization. `xfs_inode_clean` returns true when there is no inode item or no logged inode fields.

The header declares `xfs_inode_item_init`, `xfs_inode_item_destroy`, `xfs_iflush_abort`, `xfs_iflush_shutdown_abort`, `xfs_inode_item_format_convert`, and the slab cache `xfs_ili_cache`.

## Control Flow
Transactions initialize and use the inode log item to track dirty inode state. Flush and shutdown paths call the abort helpers to clear logging/flush state safely. Recovery can call the format converter for old 32-bit inode log format records.

## State and Persistence Behavior
The log item is runtime state that controls when inode changes are present in the journal, pinned, written to inode cluster buffers, and safe to consider clean. Commit sequence numbers persist only in memory and optimize data integrity sync decisions.

## Dependencies and Integration Points
The header is consumed by inode cache, inode core operations, transaction code, log recovery, AIL push, and buffer writeback. It depends on XFS log item, inode, mount, buffer, and log format structures.

## Risks and Edge Cases
`ili_lock` is the synchronization point between dirtying, flushing, and completion even though those paths hold different inode locks. Callers must not treat `xfs_inode_clean` as equivalent to no pending writeback unless they also understand pin/flush state. Destroy requires no attached buffer and no AIL membership.

## Test Signals
Signals include lifecycle creation/destruction, dirty-to-clean transitions through commit and buffer iodone, abort behavior with and without attached buffers, shutdown abort while flushing, `xfs_inode_clean` behavior for no item and empty fields, and old-format log recovery conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_inode_item.h -->
