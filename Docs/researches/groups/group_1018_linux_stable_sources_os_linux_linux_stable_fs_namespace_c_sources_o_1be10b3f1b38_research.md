# Group Research: group_1018_linux_stable_sources_os_linux_linux_stable_fs_namespace_c_sources_o_1be10b3f1b38

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux-stable`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/namespace.c -->
# File Research: sources/os/linux/linux-stable/fs/namespace.c

## Purpose

`fs/namespace.c` is the Linux VFS mount namespace implementation. It owns mount object lifetime, mount hash lookup, mountpoint tracking, mount namespace allocation and teardown, mount propagation, legacy and modern mount syscalls, `pivot_root()`, `statmount()`, `listmount()`, and namespace operations exposed through proc/nsfs.

This file is central to how Linux represents filesystem topology per mount namespace. It connects VFS objects (`vfsmount`, `mount`, `dentry`, `super_block`) with process namespace state (`mnt_namespace`, `nsproxy`, `fs_struct`) and enforces capability, propagation, idmapped mount, and visibility rules.

## Main Data And Globals

- `sysctl_mount_max`: per-namespace maximum mount count, exposed as `fs.mount-max`.
- `mount_hashtable`: hashes child mounts by `(parent vfsmount, mountpoint dentry)`.
- `mountpoint_hashtable`: hashes `struct mountpoint` by dentry.
- `mnt_cache`: slab cache for `struct mount`.
- `namespace_sem`: global rwsem serializing namespace topology operations.
- `mount_lock`: seqlock protecting mount hash/tree mutations and RCU mount lookup.
- `mnt_id_xa`, `mnt_group_ida`: unique mount ID allocation and peer group IDs.
- `init_mnt_ns`: initial mount namespace.
- `unmounted`, `ex_mountpoints`, `emptied_ns`: deferred cleanup lists protected by `namespace_sem`.

Important internal records:

- `struct mount_kattr`: normalized mount attribute mutation request used by `mount_setattr()` and `open_tree_attr()`.
- `struct pinned_mountpoint`: pins a `struct mountpoint` while a mount operation is being prepared.
- `struct kstatmount`: kernel-side assembly object for `statmount()`.
- `struct klistmount`: kernel-side assembly object for `listmount()`.

## Mount Allocation And Lifetime

Mounts are allocated by `alloc_vfsmnt()`:

- Allocates from `mnt_cache`.
- Allocates old 31-bit mount ID and monotonically increasing unique ID.
- Stores device/source name.
- Allocates per-CPU count/writer counters on SMP.
- Initializes all linkage lists, hash nodes, propagation lists, and default mount idmap.

Mount setup happens in `setup_mnt()`:

- Pins the superblock active count.
- Sets `mnt_sb`, `mnt_root`, parent/self mountpoint defaults.
- Adds the mount to the superblock’s `s_mounts` list.

Lifetime release uses a layered path:

- `mntput()` decrements mount refs.
- `mntput_no_expire()` handles fast path when still namespace-attached.
- `mntput_no_expire_slowpath()` handles final detached cleanup, marks `MNT_DOOMED`, detaches children, schedules task work or delayed work when needed.
- `cleanup_mnt()` verifies writers are gone, kills pins/stuck children, sends fsnotify delete, drops root/superblock, frees ID, then RCU-frees the mount.
- Kernel long-term mounts use `kern_mount()`, `kern_unmount()`, and `kern_unmount_array()`.

The file relies heavily on RCU and seqlock retry patterns so path walking can safely observe mounts while topology changes.

## Mount Lookup And Mountpoints

`__lookup_mnt()` is the low-level hash lookup for a child mounted at a parent/dentry pair. `lookup_mnt()` wraps it with RCU and `legitimize_mnt()` to return a referenced `vfsmount`.

Mountpoint objects are managed by:

- `get_mountpoint()`: finds or creates a `struct mountpoint` for a dentry, sets `DCACHE_MOUNTED`, and pins it in a caller-provided `pinned_mountpoint`.
- `lookup_mountpoint()`: hash lookup and pin insertion.
- `unpin_mountpoint()`: removes the pin and possibly frees the mountpoint.
- `maybe_free_mountpoint()`: clears `DCACHE_MOUNTED`, drops dentry, removes from hash when no mounts/pins remain.

`path_is_mountpoint()` checks whether a specific path is a mountpoint in the current namespace, while `__is_local_mountpoint()` checks by dentry across the current namespace.

## Write Access And Read-Only Transitions

The file maintains per-mount writer counters to make remount-readonly safe:

- `mnt_get_write_access()` increments writer count, waits out `WRITE_HOLD`, then checks read-only state.
- `mnt_want_write()` also takes superblock freeze protection.
- `mnt_get_write_access_file()` and `mnt_want_write_file()` optimize for files already opened for write.
- `mnt_put_write_access()` / `mnt_drop_write()` release.
- `mnt_hold_writers()` sets `WRITE_HOLD` and verifies no active writers.
- `mnt_unhold_writers()` releases the hold after publishing read-only flag changes.
- `sb_prepare_remount_readonly()` walks all mounts of a superblock and holds writers before transitioning the superblock read-only.

The memory barriers around writer counters, `WRITE_HOLD`, and `s_readonly_remount` are core correctness points.

## Attaching, Detaching, And Tree Topology

Core topology helpers:

- `mnt_set_mountpoint()`: sets parent/mountpoint/mp linkage.
- `make_visible()`: adds a mount to hash and parent child list; also records overmount relationships.
- `attach_mnt()`: combines mountpoint setup and visibility.
- `mnt_change_mountpoint()`: moves an existing mount to a different parent/mountpoint.
- `mnt_add_to_ns()`: inserts mount into namespace RB tree ordered by unique ID and queues notification.
- `commit_tree()`: attaches a tree to a namespace and publishes it.
- `next_mnt()` / `skip_mnt_tree()`: depth-first mount tree traversal.

Unmounting is handled by:

- `umount_tree()`: gathers a subtree, handles propagation, removes mounts from namespaces, optionally disconnects, and queues references for cleanup.
- `do_umount()`: implements policy for `umount(2)`, including expire, force, detach, busy checks, locked mounts, root remount-readonly special case.
- `path_umount()` and `ksys_umount()` are syscall helpers.
- `__detach_mounts()` lazily detaches mounts from a dentry during unlink/drop-style paths.
- `mark_mounts_for_expiry()` and `shrink_submounts()` expire shrinkable/unused mounts.

`namespace_unlock()` performs deferred cleanup and fsnotify delivery after topology operations, downgrading locks when possible for notifications.

## Mount Propagation And Copying

Propagation logic is integrated with `pnode.c` helpers:

- `clone_mnt()` clones a mount, preserving or altering peer/slave/private state based on flags.
- `copy_tree()` recursively clones a subtree, respecting unbindable mounts, locked mounts, and namespace-file loop prevention.
- `invent_group_ids()` allocates peer group IDs for making mounts shared.
- `cleanup_group_ids()` rolls group IDs back after failures.
- `attach_recursive_mnt()` attaches or moves a mount tree and handles propagation into peer groups, locking across user namespace boundaries, pending mount counts, overmount handoff, and failure cleanup.
- `do_change_type()` changes mount propagation type for one mount or recursively.
- `do_set_group()` sets sharing/slave group relationship between two mount roots.

The file is careful to reject propagation cases that would create loops or meaningless overmounts, especially in `can_move_mount_beneath()` and `check_for_nsfs_mounts()`.

## Legacy Mount API

Legacy `mount(2)` flow:

- `SYSCALL_DEFINE5(mount)` copies type/source/options from userspace.
- `do_mount()` resolves target path.
- `path_mount()` parses flags into superblock flags and mount flags, checks LSM and capabilities, warns for deprecated `mand`, then dispatches:
  - `MS_REMOUNT|MS_BIND` -> `do_reconfigure_mnt()`
  - `MS_REMOUNT` -> `do_remount()`
  - `MS_BIND` -> `do_loopback()`
  - propagation flags -> `do_change_type()`
  - `MS_MOVE` -> `do_move_mount_old()`
  - otherwise -> `do_new_mount()`
- `do_new_mount()` gets filesystem type, creates an `fs_context`, parses source/options, checks mount capability, and delegates to `do_new_mount_fc()`.
- `do_new_mount_fc()` gets the tree, runs LSM mount checks, rejects overly revealing mounts, warns about timestamp expiry, locks the mountpoint, and attaches.

`copy_mount_options()` and `copy_mount_string()` handle legacy userspace data copying.

## Modern Mount API

Modern syscalls implemented here:

- `open_tree()`: opens a path as an O_PATH file, clones a tree into an anonymous namespace, or creates a new mount namespace with `OPEN_TREE_NAMESPACE`.
- `open_tree_attr()`: variant that can apply mount attributes before publishing the fd.
- `fsmount()`: converts an `fsopen()` context with a prepared root into a detached mount fd, or a namespace file with `FSMOUNT_NAMESPACE`.
- `move_mount()`: moves a mount tree, installs detached mounts, handles fd/path targets, supports `MOVE_MOUNT_BENEATH`, and supports propagation-group setting.
- `mount_setattr()`: changes mount attributes, propagation, and idmapping recursively or non-recursively.

Important validation:

- `can_change_locked_flags()` prevents clearing locked read-only, nodev, nosuid, noexec, or atime restrictions.
- `can_idmap_mount()` restricts idmapped mounts to anonymous, not-yet-exposed mounts, supported filesystems, controlled superblocks, and non-filesystem-wide idmaps.
- `build_mount_kattr()` normalizes userspace `struct mount_attr`.
- `mount_setattr_prepare()` holds writers where needed before commit.
- `mount_setattr_commit()` updates idmaps, flags, propagation, and namespace event.

## Namespace Creation And Switching

Mount namespaces are allocated by `alloc_mnt_ns()`:

- Charges user namespace ucounts.
- Initializes namespace ID, passive refcount, RB tree, poll waitqueue, user namespace ref, and anonymous flag.

Namespace copy and creation:

- `copy_mnt_ns()` implements `CLONE_NEWNS`, including empty mount namespace support and user namespace crossing behavior.
- `create_new_namespace()` builds a new namespace for `OPEN_TREE_NAMESPACE`/`FSMOUNT_NAMESPACE`.
- `get_detached_copy()` creates anonymous detached namespace copies for cloned mount-tree file descriptors.
- `mount_subtree()` mounts and looks up a subtree in an anonymous namespace.

Namespace lifetime:

- `put_mnt_ns()` drops active refs and tears down the root tree when the namespace is no longer active.
- `mnt_ns_release()` frees passive refs after RCU.
- `lookup_mnt_ns()` finds namespaces by ID for `statmount()`/`listmount()`.

Proc namespace ops:

- `mntns_get()`, `mntns_put()`, `mntns_install()`, `mntns_owner()`.
- `mntns_install()` requires capability over both target and caller user namespaces, rejects anonymous namespaces, and updates root/pwd.

## Root And Path Operations

`pivot_root()` is implemented by:

- `SYSCALL_DEFINE2(pivot_root)` resolving `new_root` and `put_old`.
- `path_pivot_root()` enforcing mountpoint, reachability, shared propagation, lock, and namespace constraints.
- It reattaches `new_root` over old root and old root under `put_old`, then updates fs refs with `chroot_fs_refs()`.

Path reachability helpers:

- `is_path_reachable()` tests whether a mount/dentry is reachable from a root.
- `path_is_under()` exports this check under the mount seqlock.
- `current_chrooted()` tests whether the current fs root differs from namespace root.

## statmount() And listmount()

This file implements newer mount inspection syscalls.

`statmount()`:

- Parses `struct mnt_id_req`.
- Can identify target by mount namespace + unique mount ID, namespace fd, or mount fd (`STATMOUNT_BY_FD`).
- Assembles fixed fields and variable strings/options into `struct statmount`.
- Supports superblock basics, mount basics, propagation info, root, mount point, fs type/subtype, source, option strings/arrays, security options, namespace ID, and idmap uid/gid maps.
- Retries with larger seq buffer on `-EAGAIN`.

`listmount()`:

- Lists unique mount IDs under a parent ID or namespace root.
- Supports reverse order.
- Uses namespace RB tree ordering and reachability checks.
- Enforces capability behavior for inaccessible namespace views.

These syscalls rely on `namespace_sem` read locking for topology stability but intentionally tolerate concurrent mount flag/idmap changes using `READ_ONCE()`/`WRITE_ONCE()` semantics.

## Security And Namespace Policy

Security/capability checks appear throughout:

- `may_mount()` requires `CAP_SYS_ADMIN` in the current mount namespace owner user namespace.
- LSM hooks: `security_sb_mount`, `security_sb_umount`, `security_sb_kern_mount`, `security_move_mount`, `security_sb_pivotroot`, `security_sb_statfs`, `security_sb_show_options`.
- `mount_too_revealing()` prevents exposing userns-visible special filesystems too permissively unless already visible with safe locked attributes.
- `mnt_may_suid()` rejects suid trust on foreign mounts and requires current user namespace compatibility.
- Locked mount flags prevent less-privileged namespaces from relaxing inherited constraints.
- Namespace-file bind loops are rejected through `mnt_ns_loop()` and `check_for_nsfs_mounts()`.

## Initialization

`mnt_init()`:

- Creates `mnt_cache`.
- Allocates mount and mountpoint hash tables.
- Initializes kernfs, sysfs, `/sys/fs`, shmem, rootfs.
- Calls `init_mount_tree()`.

`init_mount_tree()`:

- Creates immutable `nullfs` mount as namespace root.
- Mounts mutable `rootfs` over it.
- Adds both mounts to `init_mnt_ns`.
- Sets init task root and cwd to mutable rootfs.
- Adds initial namespace to namespace tree.

## Error Handling And Failure Paths

The file uses rollback-oriented patterns:

- Failed mount attachment unmounts cloned trees with `umount_tree()`.
- Failed propagation cleans pending counts and group IDs.
- Failed namespace creation stores `emptied_ns` for cleanup on `namespace_unlock()`.
- `__free` cleanup annotations are used for paths, mounts, namespaces, files, and ID maps.
- Mount operations carefully avoid dropping final refs under locks unless topology guarantees stability.

## Key Takeaways

`namespace.c` is the mount topology authority for Linux. It combines high-concurrency lookup, serialized topology mutation, propagation semantics, namespace ownership, idmapped mount policy, and syscall-facing mount management. Correctness depends on the interaction between `namespace_sem`, `mount_lock`, RCU, mount refcounts, writer holds, namespace passive refs, and explicit failure rollback.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/namespace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/netfs/Kconfig

## Purpose

This Kconfig file defines configuration switches for the kernel netfs helper library and FS-Cache support used by network filesystems and other filesystems that want shared high-level caching and I/O helpers.

## Config Symbols

- `NETFS_SUPPORT`
  - Tristate base option for netfs helper support.
  - Enables high-level buffered I/O helpers, read segmentation, local caching integration, and transparent huge page support.
  - Other netfs objects are built under this symbol.

- `NETFS_STATS`
  - Boolean statistics gathering for local caching.
  - Depends on `NETFS_SUPPORT && PROC_FS`.
  - Exports stats through `/proc/fs/fscache/stats`.
  - The help text notes measurable overhead, especially from cacheline bouncing on multi-CPU systems.

- `NETFS_DEBUG`
  - Boolean dynamic debugging support for netfslib and FS-Cache.
  - Depends on `NETFS_SUPPORT`.
  - Allows debug output controlled through `/sys/module/netfs/parameters/debug`.

- `FSCACHE`
  - Boolean generic filesystem local caching manager.
  - Depends on `NETFS_SUPPORT`.
  - Enables pluggable local caches for network and other filesystems.
  - Points readers to `Documentation/filesystems/caching/fscache.rst`.

- `FSCACHE_STATS`
  - Boolean FS-Cache statistics.
  - Depends on `FSCACHE && PROC_FS`.
  - Selects `NETFS_STATS`.
  - Also exports through `/proc/fs/fscache/stats`.

## Dependencies And Build Impact

`FSCACHE` is layered on `NETFS_SUPPORT`; FS-Cache cannot be enabled without the netfs helper library. Stats require procfs. Debugging is independent of stats but still requires netfs support.

## Key Takeaways

The file separates core netfs infrastructure, optional debugging, optional generic local caching, and optional stats. It makes FS-Cache an extension of the netfs library rather than an independent subsystem.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/netfs/Makefile

## Purpose

This Makefile defines the object composition for the `netfs` kernel module/built-in object under `CONFIG_NETFS_SUPPORT`.

## Core Objects

`netfs-y` includes the core helper library:

- Buffered I/O:
  - `buffered_read.o`
  - `buffered_write.o`
- Direct/unbuffered I/O:
  - `direct_read.o`
  - `direct_write.o`
- Iterator and locking helpers:
  - `iterator.o`
  - `locking.o`
- Common infrastructure:
  - `main.o`
  - `misc.o`
  - `objects.o`
- Read pipeline:
  - `read_collect.o`
  - `read_pgpriv2.o`
  - `read_retry.o`
  - `read_single.o`
  - `rolling_buffer.o`
- Write pipeline:
  - `write_collect.o`
  - `write_issue.o`
  - `write_retry.o`

## Conditional Objects

- `CONFIG_NETFS_STATS`
  - Adds `stats.o`.

- `CONFIG_FSCACHE`
  - Adds FS-Cache implementation pieces:
    - `fscache_cache.o`
    - `fscache_cookie.o`
    - `fscache_io.o`
    - `fscache_main.o`
    - `fscache_volume.o`

- `CONFIG_PROC_FS && CONFIG_FSCACHE`
  - Adds `fscache_proc.o`.

- `CONFIG_FSCACHE_STATS`
  - Adds `fscache_stats.o`.

## Output

`obj-$(CONFIG_NETFS_SUPPORT) += netfs.o` builds the aggregate netfs object when support is enabled.

## Key Takeaways

The Makefile shows the netfs library as a single aggregate object with optional stats and FS-Cache pieces. The read/write code is split into high-level buffered/direct entry points and lower-level collection/issue/retry machinery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/buffered_read.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/buffered_read.c

## Purpose

`buffered_read.c` implements high-level buffered read helpers for network filesystems using the Linux page cache. It supports readahead, read-folio, read-for-write prefetch, partial dirty folio gap filling, cache-backed reads through FS-Cache, server reads, and zero-fill beyond the netfs zero point/EOF.

The exported helpers are intended for filesystems that embed `struct netfs_inode` adjacent to their inode and provide netfs operations.

## Main Entry Points

- `netfs_readahead(struct readahead_control *ractl)`
  - Handles VM readahead into pagecache.
  - May expand the request based on cache and filesystem preferences.
  - Reads from cache, server, or zero-fill sources.

- `netfs_read_folio(struct file *file, struct folio *folio)`
  - Handles a single folio read.
  - If folio is dirty due to streaming write state, delegates to `netfs_read_gaps()`.

- `netfs_write_begin(...)`
  - Deprecated helper for old write-begin paths.
  - Preloads a folio before partial write if necessary.

- `netfs_prefetch_for_write(struct file *file, struct folio *folio, size_t offset, size_t len)`
  - Reads folio contents before a write that requires existing data.

- `netfs_buffered_read_iter(struct kiocb *iocb, struct iov_iter *iter)`
  - Buffered `read_iter()` helper.
  - Uses `filemap_read()` inside netfs read serialization.

- `netfs_file_read_iter(struct kiocb *iocb, struct iov_iter *iter)`
  - Generic netfs read dispatcher.
  - Uses unbuffered/direct path when `IOCB_DIRECT` or `NETFS_ICTX_UNBUFFERED` is set; otherwise buffered read.

## Request Expansion

`netfs_rreq_expand()` gives both local cache and filesystem a chance to widen readahead:

- `netfs_cache_expand_readahead()` calls cache `expand_readahead()` if present.
- Filesystem `rreq->netfs_ops->expand_readahead()` may also adjust.
- `readahead_expand()` reconciles VM readahead state with the requested range.

This lets cache granularity, RPC sizes, and THP-friendly boundaries influence read size while still containing the original requested region.

## Cache Operation Setup

`netfs_begin_cache_read()` calls `fscache_begin_read_operation()` with the inode cookie. Failures such as `-ENOMEM`, `-EINTR`, or `-ERESTARTSYS` cause request cleanup.

Cache read source selection:

- `netfs_cache_prepare_read()` asks cache ops to prepare a read.
- If no cache ops exist, default source is `NETFS_DOWNLOAD_FROM_SERVER`.
- Cache may return `NETFS_READ_FROM_CACHE` or another source state.

## Subrequest Preparation And Dispatch

`netfs_read_to_pagecache()` is the main slicer:

1. Allocates `netfs_io_subrequest`.
2. Queues it on the request stream with `netfs_queue_read()`.
3. Chooses cache/server/zero-fill source.
4. Applies zero-point and EOF handling.
5. Calls filesystem `prepare_read()` for server reads.
6. Prepares the iterator with `netfs_prepare_read_iterator()`.
7. Marks `NETFS_RREQ_ALL_QUEUED` when all slices are queued.
8. Dispatches through `netfs_issue_read()`.

`netfs_prepare_read_iterator()`:

- Limits server reads to stream `sreq_max_len`.
- Loads folios from `readahead_control` into the rolling buffer as needed.
- Applies segment limits using `netfs_limit_iter()`.
- Assigns `subreq->io_iter`, truncates it, and advances the rolling buffer.

`netfs_issue_read()` dispatches by source:

- Server: `rreq->netfs_ops->issue_read(subreq)`.
- Cache: `netfs_read_cache_to_pagecache()`.
- Zero-fill/default: zeros iterator, marks transferred, completes subrequest.

## Rolling Buffer Use

Readahead and folio reads use `rolling_buffer`:

- `rolling_buffer_init()` creates request buffer state.
- `rolling_buffer_load_from_ra()` extracts folios from VM readahead.
- `rolling_buffer_append()` creates singular buffers for one folio.
- `rolling_buffer_advance()` advances after slicing.

This abstracts pagecache folios as I/O iterators for server/cache operations.

## Dirty Folio Gap Reads

`netfs_read_gaps()` handles a folio that is dirty but only partially populated due to streaming writes:

- Reads only gaps before/after the dirty range into the real folio.
- Routes the already-dirty middle range into a temporary sink folio.
- Builds a bvec iterator combining real folio and sink.
- On success, clears netfs folio info, restores group/private state, flushes dcache, marks folio uptodate.

This avoids overwriting locally dirty data while still completing folio contents.

## Write-Begin And Prefetch Paths

`netfs_skip_folio_read()` decides if a write can avoid pre-reading:

- Full folio write.
- Folio entirely beyond EOF.
- Write from folio start through EOF.
- Optional `always_fill` mode for complete zeroing beyond EOF.

`netfs_write_begin()`:

- Gets/locks folio.
- Lets filesystem `check_write_begin()` resolve conflicts.
- Skips read when safe.
- Otherwise allocates read-for-write request and reads the folio.

`netfs_prefetch_for_write()` is a focused prefetch helper for modern write paths.

## Synchronization And Error Handling

- Request completion waits are performed with `netfs_wait_for_read()`.
- Readahead sets `NETFS_RREQ_OFFLOAD_COLLECTION` for async collection.
- Subrequest list insertion uses spinlock plus release ordering.
- `NETFS_RREQ_ALL_QUEUED` is published with write barriers before waking collectors.
- Folios are unlocked on completion or cleanup paths.
- Errors are stored with `cmpxchg(&rreq->error, 0, ret)` so earlier errors are preserved.

## Exports

Exports:

- `netfs_readahead`
- `netfs_read_folio`
- `netfs_write_begin`
- `netfs_buffered_read_iter`
- `netfs_file_read_iter`

## Key Takeaways

This file is the buffered-read orchestration layer for netfs. It turns VM read and readahead requests into source-aware netfs subrequests, safely mixing local cache reads, server downloads, and zero-fill while preserving pagecache and dirty-folio correctness.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/buffered_read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/buffered_write.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/buffered_write.c

## Purpose

`buffered_write.c` implements high-level buffered write helpers for network filesystems using pagecache folios. It supports normal buffered writes, writethrough writes for sync modes, streaming writes into not-yet-uptodate folios, cache-aware prefetch for partial writes, netfs folio grouping, inode size updates, and mmap page-mkwrite handling.

## Main Entry Points

- `netfs_perform_write(struct kiocb *iocb, struct iov_iter *iter, struct netfs_group *netfs_group)`
  - Core buffered write loop copying user data into pagecache folios.

- `netfs_buffered_write_iter_locked(struct kiocb *iocb, struct iov_iter *from, struct netfs_group *netfs_group)`
  - Removes file privileges, updates timestamps, then calls `netfs_perform_write()`.

- `netfs_file_write_iter(struct kiocb *iocb, struct iov_iter *from)`
  - Generic netfs `write_iter()` dispatcher.
  - Uses unbuffered/direct write for `IOCB_DIRECT` or `NETFS_ICTX_UNBUFFERED`; otherwise buffered path.

- `netfs_page_mkwrite(struct vm_fault *vmf, struct netfs_group *netfs_group)`
  - Handles mmap write faults and group transitions.

- `netfs_update_i_size(struct netfs_inode *ctx, struct inode *inode, loff_t pos, size_t copied)`
  - Updates inode size and approximates block count growth.

## Folio Acquisition

`netfs_grab_folio_for_write()`:

- Uses `__filemap_get_folio()` with `FGP_WRITEBEGIN`.
- Requests larger folios when the mapping supports them using `fgf_set_order()`.
- Chooses folio size based on write position and remaining chunk.

`netfs_perform_write()` uses `mapping_max_folio_size()` and iterates chunk-by-chunk until the source iterator is drained.

## Buffered Write Flow

For each chunk:

1. Fault in source user pages with `fault_in_iov_iter_readable()` before locking destination folio to avoid deadlocks.
2. Get and lock a target folio.
3. Wait for writeback if private netfs state exists.
4. Check signal interruption.
5. Read current netfs folio info/group.
6. Resolve group conflicts by flushing existing folio data if needed.
7. Choose write strategy:
   - Modify an uptodate folio.
   - Zero and fill beyond zero point.
   - Whole-folio write without pre-read.
   - Cache-enabled prefetch then modify.
   - Streaming write into an empty/non-uptodate folio.
   - Continue an existing streaming write.
   - Flush incompatible content and retry.
8. Update folio private/group state.
9. Mark uptodate if fully initialized.
10. Flush dcache, update inode size, advance position and written count.
11. Mark dirty or advance writethrough.
12. Balance dirty pages and reschedule.

## Streaming Write State

For non-cache streaming writes into folios that are not uptodate:

- A `struct netfs_folio` is allocated and stored in folio private data with `NETFS_FOLIO_INFO`.
- It records dirty offset, dirty length, and netfs group.
- Sequential continuation can extend the dirty range.
- If the write fills the whole folio, it is promoted to uptodate and the private info can be removed.
- Incompatible overlap/disjoint writes trigger writeback of existing content before retry.

This avoids read-modify-write when the workload writes forward and the local cache does not require a fully populated folio.

## Cache-Aware Behavior

When local caching is enabled:

- Streaming writes are avoided because cache consistency may require full folio contents.
- Existing `netfs_folio` state conflicts are flushed.
- `netfs_prefetch_for_write()` is used before copying into a non-uptodate folio.
- `NETFS_FOLIO_COPY_TO_CACHE` is handled as a special private marker distinct from a real netfs group.

## Writethrough Support

For `IOCB_DSYNC` or `IOCB_SYNC`:

- Existing dirty data in range is written and waited.
- `netfs_begin_writethrough()` creates a write request.
- Dirty folios are passed through `netfs_advance_writethrough()`.
- `netfs_end_writethrough()` finalizes and may return `-EIOCBQUEUED`.
- Writeback control is attached/detached around the operation.

This lets synchronous writes copy into pagecache while also issuing backing I/O.

## Inode Size Handling

`netfs_update_i_size()`:

- If filesystem provides `ctx->ops->update_i_size`, delegates.
- Otherwise takes `inode->i_lock`, updates `i_size`, updates FS-Cache cookie object size when enabled, and approximates `i_blocks`.
- Only grows size; it does not shrink.

The core write loop calls it after each successful copy.

## Generic Write Wrapper

`netfs_file_write_iter()`:

- Rejects zero-length writes early.
- Selects unbuffered/direct write if needed.
- Starts serialized netfs write I/O with `netfs_start_io_write()`.
- Runs `generic_write_checks()`.
- Calls buffered write locked helper.
- Ends netfs write serialization.
- Performs `generic_write_sync()` for positive results.

## mmap Page-Mkwrite

`netfs_page_mkwrite()`:

- Starts pagefault accounting with `sb_start_pagefault()`.
- Locks folio and waits for writeback.
- Requires folio to be uptodate.
- If group conflicts exist, writes back the folio and returns retry/OOM/SIGBUS as appropriate.
- Updates folio group/private state.
- Updates file time, marks modified attribute flag, and calls `post_modify()` if supplied.
- Returns `VM_FAULT_LOCKED` on success with folio locked.

## Error Handling

Important failure paths:

- Copy failure returns `-EFAULT` unless partial data was already written.
- Signal while blocked returns `-EINTR` after partial write or `-ERESTARTSYS` before any data.
- Allocation failures return `-ENOMEM`.
- Writeback or prefetch failures exit the loop.
- Function returns bytes written if any, otherwise negative error.

## Exports

Exports:

- `netfs_perform_write`
- `netfs_buffered_write_iter_locked`
- `netfs_file_write_iter`
- `netfs_page_mkwrite`

## Key Takeaways

This file is the buffered-write state machine for netfs. It balances pagecache semantics, network filesystem grouping, local cache requirements, streaming-write optimization, synchronous writethrough, and mmap write fault handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/buffered_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/direct_read.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/direct_read.c

## Purpose

`direct_read.c` implements netfs direct and unbuffered read support. It bypasses pagecache and local disk cache, slices application-buffer reads into subrequests according to netfs/server limits, and supports synchronous and asynchronous kiocb completion.

## Main Entry Points

- `netfs_unbuffered_read_iter_locked(struct kiocb *iocb, struct iov_iter *iter)`
  - Performs direct or unbuffered read when caller already holds appropriate locks.

- `netfs_unbuffered_read_iter(struct kiocb *iocb, struct iov_iter *iter)`
  - Public wrapper that serializes direct I/O using `netfs_start_io_direct()` / `netfs_end_io_direct()`.

Internal helpers:

- `netfs_unbuffered_read()`
- `netfs_dispatch_unbuffered_reads()`
- `netfs_prepare_dio_read_iterator()`

## Read Dispatch Flow

`netfs_unbuffered_read_iter_locked()`:

1. Returns 0 for empty read without updating atime.
2. Calls `kiocb_write_and_wait()` to flush conflicting writes.
3. Updates file access time.
4. Allocates `netfs_io_request` with origin:
   - `NETFS_DIO_READ` for `IOCB_DIRECT`
   - `NETFS_UNBUFFERED_READ` otherwise
5. Extracts or copies the destination iterator:
   - User-backed iterators are extracted into a bvec iterator with `netfs_extract_user_iter()`.
   - Non-user-backed iterators are copied directly and advanced.
6. For async operations, stores `iocb` and sets `NETFS_RREQ_OFFLOAD_COLLECTION`.
7. Calls `netfs_unbuffered_read()`.

`netfs_unbuffered_read()`:

- Rejects zero-sized request as `-EIO`.
- Begins inode DIO accounting with `inode_dio_begin()`.
- Dispatches subrequests.
- Waits synchronously or returns `-EIOCBQUEUED` for async.

## Subrequest Slicing

`netfs_dispatch_unbuffered_reads()` loops over the requested range:

- Allocates a subrequest.
- Sets source to `NETFS_DOWNLOAD_FROM_SERVER`.
- Sets start and length.
- Queues it with `netfs_queue_read()`.
- Runs filesystem `prepare_read()` if present.
- Calls `netfs_prepare_dio_read_iterator()` to limit and assign iterator.
- Updates request submitted count.
- Sets `NETFS_RREQ_ALL_QUEUED` when final slice is queued.
- Calls filesystem `issue_read()`.
- Honors pause and failed flags.

If allocation or preparation fails while bytes remain, it sets `NETFS_RREQ_ALL_QUEUED` and wakes the collector so outstanding state can complete.

`netfs_prepare_dio_read_iterator()`:

- Limits length to stream `sreq_max_len`.
- Applies segment count limits via `netfs_limit_iter()`.
- Assigns `subreq->io_iter` from request iterator.
- Truncates subrequest iterator and advances request iterator.

## Iterator Ownership

The direct read path must preserve user buffers across async completion:

- User-backed iterators are extracted into request-owned bvecs.
- `direct_bv`, `direct_bv_count`, and `direct_bv_unpin` track extracted buffers and pinning behavior.
- Non-user-backed iterators are assumed stable for the operation.

## Completion Semantics

- Sync reads wait via `netfs_wait_for_read()`, advance `iocb->ki_pos`, and return transferred bytes.
- Async reads return `-EIOCBQUEUED`; completion is handled by the netfs read collector.
- `inode_dio_end()` is intentionally left to collection because subrequests may still be outstanding.

## Exports

Exports:

- `netfs_unbuffered_read_iter_locked`
- `netfs_unbuffered_read_iter`

## Key Takeaways

This file is a thin but critical direct-read adapter: it turns a user/kernel iterator into request-owned I/O state, slices by netfs limits, bypasses cache/pagecache, and hands completion to netfs read collection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/direct_read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/direct_write.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/direct_write.c

## Purpose

`direct_write.c` implements netfs unbuffered and direct write support. It writes data directly to the server without going through pagecache or local FS-Cache, while coordinating direct I/O exclusion, cache invalidation, i_size update, retry, and async kiocb completion.

## Main Entry Points

- `netfs_unbuffered_write_iter_locked(struct kiocb *iocb, struct iov_iter *iter, struct netfs_group *netfs_group)`
  - Creates and dispatches an unbuffered/direct write request when caller holds appropriate locks.

- `netfs_unbuffered_write_iter(struct kiocb *iocb, struct iov_iter *from)`
  - Public write path with generic checks, direct I/O serialization, pagecache invalidation, zero-point update, and cache invalidation.

Internal helpers:

- `netfs_unbuffered_write()`
- `netfs_unbuffered_write_collect()`
- `netfs_unbuffered_write_done()`
- `netfs_unbuffered_write_async()`

## Public Write Flow

`netfs_unbuffered_write_iter()`:

1. Returns 0 on empty write.
2. Traces and counts DIO write stats.
3. Starts direct I/O serialization with `netfs_start_io_direct()`.
4. Runs `generic_write_checks()`.
5. Removes privileges and updates timestamps.
6. Handles `IOCB_NOWAIT` by rejecting if range has pagecache pages that would block invalidation.
7. Otherwise writes and waits for pagecache data in range.
8. Invalidates clean cached pages in the write range before direct write.
9. Updates netfs zero point under `inode->i_lock` if write extends it.
10. Invalidates FS-Cache cookie with `FSCACHE_INVAL_DIO_WRITE`.
11. Calls locked unbuffered write helper.
12. Ends direct I/O serialization.

## Request Setup

`netfs_unbuffered_write_iter_locked()`:

- Creates a write request using `netfs_create_write_req()`.
- Origin is `NETFS_DIO_WRITE` for `IOCB_DIRECT`, otherwise `NETFS_UNBUFFERED_WRITE`.
- Marks stream 0 available.
- Extracts user-backed iterators into request-owned bvecs with `netfs_extract_user_iter()`.
- Copies non-user iterators directly.
- Sets `NETFS_RREQ_USE_IO_ITER` and `NETFS_RREQ_UPLOAD_TO_SERVER`.
- For async writes, queues work to `system_dfl_wq` and returns `-EIOCBQUEUED`.
- For sync writes, calls `netfs_unbuffered_write()` and returns transferred bytes or error.

The file has TODO placeholders for bounce-buffer encryption/compression style transforms.

## Serial Subrequest Dispatch

`netfs_unbuffered_write()` intentionally dispatches subrequests serially:

- It prepares a write subrequest through `netfs_prepare_write()`.
- Truncates iterator to remaining request length.
- Limits request by stream max length and max segments.
- Issues write with `stream->issue_write()`.
- Waits for stream progress before issuing the next subrequest.

The serial design avoids gaps on partial failures such as server-side `ENOSPC`.

## Retry Handling

If a subrequest needs retry:

- Marks subrequest error `-EAGAIN`.
- Advances request iterator by bytes already transferred.
- Calls filesystem `retry_request()` if available for server uploads.
- Clears retry/boundary/failed flags.
- Resets iterator, start, len, transferred, and increments retry count.
- Resets max length/segments.
- Either re-runs stream `prepare_write()` or reissues with `netfs_reissue_write()`.

## Completion And Cleanup

`netfs_unbuffered_write_collect()`:

- Removes subrequest from stream list.
- Adds transferred bytes to request.
- Advances request iterator.
- Updates stream/request collected positions.
- Drops subrequest ref.

`netfs_unbuffered_write_done()`:

- Updates inode size if no request error.
- For DIO writes, invalidates any pagecache folios that mmap may have populated under the written range.
- Calls `inode_dio_end()` for DIO writes.
- Wakes waiters on `NETFS_RREQ_IN_PROGRESS`.
- Completes async kiocb by advancing `ki_pos` and calling `ki_complete()`.
- Clears subrequests.

## Error Handling

- Failed preparation stores subrequest error into request and exits.
- Failed issued write records `wreq->error`.
- Signal during synchronous non-kiocb write returns `-EINTR` after progress or `-ERESTARTSYS` before progress.
- Sync caller returns transferred bytes if any, otherwise error.
- Async caller returns `-EIOCBQUEUED`.

## Exports

Exports:

- `netfs_unbuffered_write_iter_locked`
- `netfs_unbuffered_write_iter`

## Key Takeaways

This file is the direct/unbuffered write counterpart to the buffered write machinery. It prioritizes contiguous server writes, direct I/O accounting, pagecache/cache coherency, and safe async completion over parallel subrequest dispatch.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/direct_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_cache.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_cache.c

## Purpose

`fscache_cache.c` implements FS-Cache cache-level object management. It tracks registered cache backends, cache acquisition/relinquish, live access pinning, I/O error state, withdrawal, and optional procfs listing.

This is the global cache registry layer beneath netfs/FS-Cache cookies and volumes.

## Main Globals

- `fscache_caches`: global list of cache records.
- `fscache_addremove_sem`: rwsem protecting cache add/remove/lookup.
- `fscache_clearance_waiters`: waitqueue exported for cache clearance users.
- `fscache_cache_debug_id`: atomic ID source for trace/debug identifiers.

Exported globals:

- `fscache_addremove_sem`
- `fscache_clearance_waiters`

## Cache Allocation And Lookup

`fscache_alloc_cache(const char *name)`:

- Allocates and zeroes `struct fscache_cache`.
- Optionally duplicates the cache name.
- Initializes refcount to 1.
- Initializes list linkage.
- Assigns debug ID.

`fscache_lookup_cache(const char *name, bool is_cache)`:

- First searches under read lock.
- Matches named cache by exact name.
- Matches unnamed cache if both requested and existing are unnamed.
- If no name is requested, can fall back to the first named cache.
- If not found, allocates a candidate and retries under write lock.
- If an unnamed cache exists and caller is acquiring a real cache, it can assign the candidate name to that unnamed cache.
- Adds a new cache to `fscache_caches` if still absent.
- Uses refcount-not-zero acquisition to avoid resurrecting freed caches.

The unnamed-cache behavior lets consumers initially refer to a default cache and later bind it to a named backend.

## Cache Acquisition And Release

`fscache_acquire_cache(const char *name)`:

- Requires a name.
- Looks up or creates a cache record.
- Transitions state from `FSCACHE_CACHE_IS_NOT_PRESENT` to `FSCACHE_CACHE_IS_PREPARING`.
- Returns `-EBUSY` if a cache tag is already in use.

`fscache_put_cache(struct fscache_cache *cache, enum fscache_cache_trace where)`:

- Drops a reference.
- Removes the cache from the global list and frees name/object when refcount reaches zero.
- Emits trace events.

`fscache_relinquish_cache(struct fscache_cache *cache)`:

- Clears ops and private data.
- Resets state to not-present.
- Drops the caller reference with trace reason depending on whether preparation failed or active cache was relinquished.

## Adding And Withdrawing Cache Backends

`fscache_add_cache(struct fscache_cache *cache, const struct fscache_cache_ops *ops, void *cache_priv)`:

- Requires state `FSCACHE_CACHE_IS_PREPARING`.
- Pins `n_accesses` by incrementing it, preventing withdrawal waitups from reaching zero during active service.
- Stores backend ops and private data under write lock.
- Sets state active.
- Logs cache addition.

`fscache_withdraw_cache(struct fscache_cache *cache)`:

- Sets state withdrawn.
- Drops the artificial service pin on `n_accesses`.
- Waits until active accesses drain to zero.
- Logs withdrawal with object count.

## Access Pinning

`fscache_begin_cache_access(struct fscache_cache *cache, enum fscache_access_trace why)`:

- Checks cache is live.
- Increments `n_accesses`.
- Uses memory barrier after atomic increment and rechecks liveness.
- If cache went non-live, immediately ends access and returns false.
- Otherwise returns true.

`fscache_end_cache_access(struct fscache_cache *cache, enum fscache_access_trace why)`:

- Uses memory barrier before decrement.
- Decrements `n_accesses`.
- Wakes waiters when it reaches zero.

This prevents cache backends from being withdrawn while operations are actively using them.

## I/O Error Handling

`fscache_io_error(struct fscache_cache *cache)`:

- Transitions active cache to `FSCACHE_CACHE_GOT_IOERROR`.
- Logs that the cache stopped due to I/O error.
- Exported for backend use.

## Procfs Listing

When `CONFIG_PROC_FS` is enabled, the file defines `fscache_caches_seq_ops` for `/proc/fs/fscache/caches`.

The seq output includes:

- Cache debug ID.
- Refcount.
- Volume count.
- Object count.
- Active access count.
- Cache state character.
- Cache name or `-`.

Iteration holds `fscache_addremove_sem` read lock across seq traversal.

## Synchronization

- Cache registry mutations use `fscache_addremove_sem`.
- Per-cache lifetime uses `refcount_t`.
- Active use uses `atomic_t n_accesses`.
- Cache state transitions use helper functions/macros from internal FS-Cache code.
- Memory barriers around access counters enforce live-state visibility.

## Exports

Exports:

- `fscache_acquire_cache`
- `fscache_put_cache`
- `fscache_relinquish_cache`
- `fscache_add_cache`
- `fscache_io_error`
- `fscache_withdraw_cache`

## Key Takeaways

This file is the FS-Cache backend registry and lifetime manager. It separates cache record references from active access pins, supports named/default cache lookup, provides a prepare-active-withdraw state model, and exposes cache state for diagnostics through procfs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_cache.c -->