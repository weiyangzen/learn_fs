# Group Research: group_872_linux_sources_os_linux_linux_fs_xfs_xfs_healthmon_c_sources_os_linux_83892473dab8

Scope checked against `Docs/research_subset_a.md`: these files are within `sources/os/linux/linux`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_healthmon.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_healthmon.c

Implements the XFS live health monitoring anonymous file descriptor used by privileged userspace, primarily a healer daemon, to receive filesystem health, shutdown, media, and file I/O error events.

Key elements:
- Defines a mount-attached `xfs_healthmon` lifetime model with RCU lookup, refcounting, weak mount cookies, a global attach/detach spinlock, and cleanup after all fd/mount/event-handler references drain.
- `xfs_ioc_health_monitor` validates privilege and ioctl format, creates a monitor, queues an initial RUNNING event, preallocates an UNMOUNT event, attaches to the mount, and returns an anonymous read-only fd.
- Event producers report filesystem, AG/rtgroup, inode, shutdown, media, and file-range I/O errors through `xfs_healthmon_report_*` helpers.
- Metadata health reporting filters old/new sick masks unless verbose mode is requested, and removes secondary health bits before emitting events.
- Queue handling merges compatible events: lost counters, health masks, shutdown flags, adjacent media ranges, and adjacent file ranges for the same inode generation.
- Queue pressure is bounded by `XFS_HEALTHMON_MAX_EVENTS`; allocation failure or full queue increments lost-event accounting, and the next successful push emits a LOST event.
- Read path uses a lazily allocated bounded output buffer, formats events into `struct xfs_health_monitor_event` v0 records, copies to userspace via `copy_to_iter`, and supports blocking/nonblocking reads.
- Poll exposes `EPOLLIN` when queued events, unread formatted bytes, or detach/EOF state is visible.
- File ioctls support monitor reconfiguration and checking whether an arbitrary fd belongs to the monitored filesystem.
- `/proc` fdinfo reports alive/dead state, dev_t, format, total events, and lost count.

Dependencies:
- Uses anonymous inode fd APIs, VFS read/poll/ioctl plumbing, wait queues, RCU, refcounting, mutexes, spinlocks, and user-copy helpers.
- Integrates with XFS mount state, health masks, tracing, shutdown flags, fserror events, realtime group/allocation group metadata, and ioctl ABI definitions.

Research notes:
- The monitor deliberately uses a weak mount reference so queued events and readers do not pin or slow unmount.
- Unmount queues a preallocated event before detaching so userspace can observe filesystem teardown even under memory pressure.
- Reads return EOF-like behavior after detachment when no data remains, allowing monitor daemons to exit cleanly.
- Only `CAP_SYS_ADMIN`, the root inode, and the initial user namespace can create the monitor fd.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_healthmon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_healthmon.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_healthmon.h

Declares the internal XFS health monitor state, event representation, event type/domain enums, and reporting entry points.

Key elements:
- `struct xfs_healthmon` stores a weak mount cookie, device number, refcount, event queue, preallocated unmount event, verbose flag, wait queue, read formatting buffer, and event/lost counters.
- `enum xfs_healthmon_type` covers monitor lifecycle, metadata health, shutdown, media error, buffered/direct I/O, and data loss events.
- `enum xfs_healthmon_domain` distinguishes mount, filesystem, AG, inode, realtime group, devices, and file ranges.
- `struct xfs_healthmon_event` is an internal tagged event object with union payloads for lost counts, health masks, group ids, inode identity, shutdown flags, media ranges, and file ranges.
- Declares reporting hooks for fs/group/inode health, shutdown, media errors, file I/O errors, unmount, and monitor ioctl creation.

Dependencies:
- Depends on XFS mount, group, inode, device, daddr, ino, and ioctl ABI types.
- Mirrors but does not expose directly the userspace `struct xfs_health_monitor_event` format used in `xfs_healthmon.c`.

Research notes:
- `mount_cookie` is explicitly documented as non-dereferenceable by users of the monitor object except guarded internal attach/detach logic.
- The event object stores inode generation numbers and file positions so userspace can correlate file-range errors without retaining kernel inode pointers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_healthmon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_hooks.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_hooks.c

Implements the small live-hook wrapper around Linux blocking notifier chains for optional XFS hook points.

Key elements:
- `xfs_hooks_init` initializes a blocking notifier head.
- `xfs_hooks_add` registers a hook after asserting a callback is installed and that `struct xfs_hook.nb` is first in the structure.
- `xfs_hooks_del` unregisters a hook.
- `xfs_hooks_call` invokes the chain and returns the final notifier result.

Dependencies:
- Depends on notifier-chain infrastructure and `CONFIG_XFS_LIVE_HOOKS` declarations from `xfs_hooks.h`.
- Includes core XFS headers for consistency and tracing/assertion support.

Research notes:
- The implementation is intentionally thin; static-key enable/disable behavior lives in the header macros used by hook call sites.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_hooks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_hooks.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_hooks.h

Declares optional XFS live hook infrastructure and compiles it away when `CONFIG_XFS_LIVE_HOOKS` is disabled.

Key elements:
- With live hooks enabled, `struct xfs_hooks` wraps a `blocking_notifier_head`, and `struct xfs_hook` embeds a leading `notifier_block`.
- Defines static branch helper macros for hook-switch declaration, on/off, and checked-on tests.
- Declares hook chain initialization, registration, unregistration, call, and `xfs_hook_setup`.
- With live hooks disabled, provides empty structs/no-op macros and makes calls return `NOTIFY_DONE`.

Dependencies:
- Uses Linux blocking notifier chains and static keys/jump labels.
- Callers must handle static-branch patching constraints noted in the header comments.

Research notes:
- The header warns that static branch updates take the CPU hotplug lock, so callers must avoid holding locks that memory reclaim/writeback might need while switching hooks on or off.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_hooks.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_icache.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_icache.c

Implements the XFS in-core inode cache: inode allocation/freeing, `iget`, reclaim tagging, inode cache walks, speculative block garbage collection, deferred inode inactivation, and inodegc shrinker integration.

Key elements:
- Maintains per-AG radix-tree inode caches with tags for reclaimable inodes and inodes needing EOF/COW block cleanup; tags are propagated into per-group xarray marks.
- `xfs_inode_alloc` initializes the embedded VFS inode and XFS inode fields, forks, work items, mapping folio order, and unlinked-list state.
- Freeing uses RCU and clears inode number/state before release so concurrent RCU cache lookups can detect recycled or freed objects.
- `xfs_iget` validates inode numbers, handles cache hits/misses, recycles reclaimable inodes, reads inode cores from disk when needed, inserts new inodes into the per-AG radix tree, and returns requested inode locks.
- Cache-hit handling avoids inodes under construction, reclaim, inactivation, or incomplete inactive cleanup; it can queue inodegc and retry when necessary.
- `xfs_trans_metafile_iget` and `xfs_metafile_iget` validate metadata inode mode, link count, metadir membership, and metafile type.
- Reclaim logic grabs eligible reclaimable inodes, avoids sick inodes unless unmount/norecovery/shutdown requires it, flushes AIL as needed, removes inodes from the radix tree, and frees them after coordination with lookup races.
- Inode-cache walking batches tagged radix-tree lookups per AG and dispatches per-goal processing for reclaim or block garbage collection.
- Blockgc tags and workers release speculative post-EOF blocks and pending COW reservations, with quota/id/min-size filtering and sync/async behavior.
- Inodegc queues inodes needing inactive processing onto per-CPU lockless lists, schedules delayed work based on backlog/free-space/quota pressure, and can be pushed/flushed/stopped/started.
- Inodegc worker runs `xfs_inactive`, marks inodes reclaimable, tracks errors, and uses NOFS allocation context.
- A phony shrinker accelerates inodegc under memory pressure and can throttle frontend queuing when shrinker-triggered backlog exists.

Dependencies:
- Uses radix trees, xarrays, RCU, per-CPU state, delayed workqueues, shrinkers, lockless lists, VFS inode lifecycle, quota, reflink/COW, bmap utilities, AIL/log state, XFS per-AG groups, health state, and metadata inode helpers.

Research notes:
- Inode lookup and reclaim rely heavily on `i_flags_lock`, ILOCK, radix-tree tags, and RCU ordering to avoid use-after-free during cache walks.
- Reclaim does no normal metadata I/O; callers needing clean inodes must push the AIL first.
- Blockgc avoids freeing COW staging extents under dirty/writeback/direct-I/O conditions because completion paths rely on those reservations.
- Inodegc is separate from reclaim because inactive processing can require transactions and metadata updates before memory can be reclaimed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_icache.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_icache.h

Declares public interfaces and control flags for the XFS inode cache, reclaim, blockgc, and inodegc subsystems.

Key elements:
- `struct xfs_icwalk` carries inode-walk filters: flags, uid, gid, project id, minimum file size, and scan limit.
- Defines public inode walk flags for sync mode, uid/gid/project filtering, and minimum file size filtering.
- Defines `xfs_iget` flags for create, untrusted lookup, don’t-cache, incore-only, and no-retry behavior.
- Declares inode allocation/free, reclaim workers/counts/scans, reclaimable marking, blockgc quota/free-space helpers, EOF/COW block tag management, blockgc worker control, inodegc worker control, flush/push/stop/start, and inodegc shrinker registration.

Dependencies:
- Exposes XFS mount, per-AG, inode, dquot, and transaction-facing cache operations to the rest of the filesystem.

Research notes:
- The header name guard still says `XFS_SYNC_H`, reflecting older sync/reclaim grouping, but contents are inode-cache focused.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_icache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_icreate_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_icreate_item.c

Implements the XFS inode-create log item used to log initialization of newly allocated inode chunks and replay them during recovery.

Key elements:
- Defines the global `xfs_icreate_cache` slab cache and `ICR_ITEM` helper.
- Log item ops compute size, format a single `xfs_icreate_log` vector, and release cache/shadow memory after commit.
- `xfs_icreate_log` allocates an icreate item, fills AG/block/count/inode-size/length/generation fields in big-endian log format, joins it to the transaction, marks the transaction dirty, and sets the item dirty bit.
- Recovery reorder places icreate replay with buffer-list replay because inode items modifying the same buffers must see initialized inode cluster buffers first.
- Recovery pass validates log item type/size, AG/block/count/inode-size/length consistency, supported sparse/full chunk lengths, and count-vs-length geometry.
- Recovery checks for canceled inode cluster buffers and skips replay if the chunk was canceled.
- Successful replay calls `xfs_ialloc_inode_init` to stamp inode templates into delayed-write buffers.

Dependencies:
- Integrates with XFS transaction/log item infrastructure, log recovery, inode allocation geometry, buffer cancellation tracking, and tracing.

Research notes:
- Recovery currently expects all or none of the inode cluster buffers in a logged allocation to be canceled; partial cancellation only warns and skips replay.
- The item acts as the logical equivalent of logging newly initialized inode buffers without logging every byte of the chunk.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_icreate_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_icreate_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_icreate_item.h

Declares the in-memory inode-create log item and its logging entry point.

Key elements:
- `struct xfs_icreate_item` embeds a generic `xfs_log_item` and the `xfs_icreate_log` format payload.
- Exposes `xfs_icreate_cache`.
- Declares `xfs_icreate_log` for transaction code that allocates inode chunks.

Dependencies:
- Depends on XFS transaction, inode allocation, AG block, and log-format types.

Research notes:
- The public surface is intentionally minimal because formatting/recovery details live in `xfs_icreate_item.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_icreate_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_inode.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_inode.c

Implements core XFS inode operations: inode locking, namespace operations, inode creation/deletion, inactive cleanup, unlinked-list recovery, inode flushing, layout breaking, and inode utility helpers.

Key elements:
- Provides lock helpers for IOLOCK, MMAPLOCK, and ILOCK with documented ordering, trylock rollback, demotion, lockdep subclassing, and assertions.
- Implements multi-inode locking in inode-number order for rename/remap-style operations, with AIL-aware trylock retries to avoid log-tail deadlocks.
- `xfs_lookup` resolves directory entries, igets target inodes, handles case-insensitive names, and rejects metadata inodes reachable from the regular directory tree.
- `xfs_icreate`, `xfs_create`, and `xfs_create_tmpfile` allocate quota resources, reserve transactions, allocate inode numbers, initialize in-core/on-disk inode state, attach dquots, update directories or unlinked lists, and commit.
- `xfs_link`, `xfs_remove`, and `xfs_rename` implement namespace updates with quota attachment, parent pointer support, project-id inheritance checks, whiteout support, reservation fallback, AGI lock ordering, and synchronous-mount behavior.
- Truncation helpers remove blocks past EOF, cancel COW reservations, clear reflink/COW tags when possible, and relog inode core state through rolling transactions.
- Inactive processing handles COW cleanup, EOF block freeing, unlinked regular-file truncation, directory buffer staling, symlink cleanup, attribute fork teardown, inode free, dquot detach, and persistent marking of unresolved inode health.
- `xfs_ifree` returns unlinked inodes to the free list, clears obsolete logged owner fields, and can stale an entire inode cluster buffer when the chunk becomes free.
- Cluster-freeing logic marks all cached inodes in the freed cluster stale and attaches dirty inodes to the stale buffer so journal completion removes them safely.
- Pin helpers force log sequences and wait for inode pin counts to drop.
- `xfs_iflush` validates incore inode state, updates legacy flushiter, verifies local forks, copies dirty state to the on-disk inode buffer, coordinates `ili_fields`/`ili_last_fields`, stores flush LSN, calculates CRC, and marks corrupt cores sick.
- `xfs_iflush_cluster` scans inodes attached to a cluster buffer, nonblockingly flushes eligible dirty inodes, handles shutdown aborts, and fails the buffer/shuts down on corruption.
- Layout helpers break file leases and DAX layouts while obeying VFS inode and XFS MMAPLOCK ordering for two-inode operations.
- Utility helpers reload unrecovered unlinked lists, detect zapped forks, count realtime/data blocks, calculate allocation unit size, and decide always-COW behavior.

Dependencies:
- Uses VFS inode locking/state, XFS directory, bmap, reflink, quota, parent pointers, transactions, defer ops, inode allocation/free, log/AIL, buffer items, symlink/attr cleanup, metadata inode support, DAX/layout lease APIs, and health tracking.

Research notes:
- Namespace removal deliberately drops link counts before removing directory entries to preserve AGI-before-AGF lock ordering.
- Inactive processing is skipped for read-only mounts except recovery, internal metadata inodes, shutdown/norecovery paths, and already-free inodes.
- Inode cluster staling is carefully synchronized with inode flush and reclaim to avoid stale dirty inodes remaining in AIL or memory.
- Flush failure due to corrupt incore state forces shutdown before releasing the buffer so log-tail movement cannot make recovery unsafe.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_inode.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_inode.h

Defines the kernel XFS inode structure, inode state flags, lock flags/subclasses, inline helpers, and exported inode operation prototypes.

Key elements:
- `struct xfs_inode` embeds mount/quota pointers, inode number and imap, data/attr/COW forks, log item pointer, inode locks, pin count, inodegc list node, health bitsets, state flags, size/block/project/extent metadata, unlinked-list pointers, embedded VFS inode, and pending I/O completion work.
- Inline helpers convert between VFS and XFS inodes, select forks, compute fork sizes, test unlinked/attr-fork/COW/reflink/metadir/internal/zoned/bigtime/large-extent-count state, and compute visible file size.
- Defines in-core state flags for reclaim, stale, new, DM field preservation, truncation, EOF/COW block tags, inactive processing, recovery, quotacheck, remapping, and combined reclaim masks.
- Defines IOLOCK, ILOCK, MMAPLOCK shared/exclusive flags plus lockdep subclass encoding for parent, realtime metadata, and inode-number ordered locking.
- Declares namespace operations, locking operations, inode creation/free/truncate/flush helpers, inode release/log-force helpers, unlinked-list recovery, block counting, layout breaking, allocation unit, and dquot allocation interfaces.
- Includes helpers for stable writes and finishing newly instantiated VFS inode setup.

Dependencies:
- Pulls in inode buffer/fork/util definitions and depends on XFS mount, transaction, dquot, bmap, VFS inode, lockdep, DAX, quota, and metadir concepts.

Research notes:
- The lock flag layout reserves low bits for actual locks and high bits for lockdep subclass annotations.
- `XFS_INACTIVATING` and `XFS_NEED_INACTIVE` encode the handoff from VFS reclaim to background metadata cleanup before reclaimable state.
- Internal inode detection differs depending on whether metadata directories are enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_inode_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_inode_item.c

Implements the XFS inode log item: transaction precommit handling, log vector sizing/formatting, inode pin/unpin, AIL pushing, commit sequence tracking, flush completion, flush abort, and log-format conversion.

Key elements:
- Defines `xfs_ili_cache`, `INODE_ITEM`, inode log item sort key by inode number, and optional expensive precommit verification.
- Precommit updates VFS dirty-time state, upgrades eligible inodes to bigtime, fixes bad realtime extent-size hints, attaches/holds the inode cluster buffer late in transaction ordering, stores dirty flags, converts iversion logging to core logging, and merges last-flushed fields back into current fields.
- Late buffer attachment preserves AGI/AGF/inode-cluster lock ordering and ensures dirty inodes keep their backing buffer in memory while journaled.
- Size calculation accounts for log format, log dinode core, data fork extents/btree/local data, and attr fork extents/btree/local data.
- Formatting emits a 64-bit inode log format, log dinode core, and optional fork payloads while clearing incompatible/empty log field bits to avoid stale or uninitialized log data.
- Log dinode conversion handles bigtime vs legacy timestamps, legacy DMAPI field preservation, large extent counters, v3 inode fields, metatype, uuid, LSN, crc placeholder, and v2 flushiter.
- Pin/unpin increments/decrements inode pin counts and clears fsync/datasync commit sequences when the last pin drops.
- AIL push tries to flush the inode cluster buffer, returns pinned/flushing/locked states as appropriate, and queues flushed buffers for delayed write.
- Commit handling records commit and datasync sequence numbers before release and bypasses AIL insertion for stale inodes.
- Flush completion removes successfully written inode items from the AIL when LSNs match, clears failed bits, finishes flush state, detaches clean items from buffers, and drops buffer references.
- Abort paths remove inode items from AIL, clear flush/log fields, detach from buffers, handle shutdown from contexts without the cluster buffer locked, and release buffer references safely.
- Provides conversion from old 32-bit inode log format records to the native 64-bit structure for recovery.

Dependencies:
- Integrates with XFS transaction item ops, CIL/AIL, inode flush code in `xfs_inode.c`, buffer items, log recovery format definitions, VFS inode timestamps/versioning, realtime extent helpers, and shutdown/error handling.

Research notes:
- The `ili_fields`/`ili_last_fields` protocol prevents relogging from dropping data before a prior flush reaches disk.
- Inode items must keep a valid buffer pointer while in the AIL so push operations can locate the cluster buffer.
- Stale inode commit handling avoids inserting clean stale inodes into the AIL, which would otherwise persist until reclaim assertions fire.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_inode_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_inode_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_inode_item.h

Declares the XFS inode log item state and exported inode logging/flush helpers.

Key elements:
- `struct xfs_inode_log_item` embeds the generic log item, backpointer to the inode, transaction lock flags, per-transaction dirty flags, a flush-state spinlock, current/last logged field masks, flush LSN, and commit/datasync sequence numbers.
- `xfs_inode_clean` tests whether an inode has no active log item dirty fields.
- Declares inode item initialization/destruction, flush abort helpers, shutdown abort helper, and old-format conversion.
- Exposes `xfs_ili_cache`.

Dependencies:
- Depends on XFS log item, inode, mount, buffer, bmap record, and log-format definitions.

Research notes:
- `ili_lock` is the key synchronization point between dirtying, flushing, completion, and fsync sequence tracking because those paths hold different inode locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_inode_item.h -->