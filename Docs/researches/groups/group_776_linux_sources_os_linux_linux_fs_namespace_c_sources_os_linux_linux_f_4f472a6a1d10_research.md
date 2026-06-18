# Group Research: group_776_linux_sources_os_linux_linux_fs_namespace_c_sources_os_linux_linux_f_4f472a6a1d10

Scope: `Docs/research_subset_a.md` / Linux VFS mount namespace and netfs support files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/namespace.c -->
# File Research: sources/os/linux/linux/fs/namespace.c

## Role

Core Linux VFS mount namespace implementation. This file owns `struct mount` allocation/lifetime, mount hash and mountpoint hash management, mount namespace allocation/destruction, mount tree cloning and movement, propagation semantics, mount write access accounting, legacy and new mount API syscalls, idmapped mount attribute changes, mount namespace introspection, root mount initialization, and mount namespace `proc_ns_operations`.

## Core State and Locking

- `sysctl_mount_max` limits mounts per namespace and is exposed as `fs.mount-max` when sysctl is enabled.
- Global hash tables index child mounts by `(parent vfsmount, mountpoint dentry)` and mountpoints by dentry.
- `namespace_sem` serializes topology changes, namespace teardown, proc/list/stat mount iteration, and deferred mountpoint cleanup.
- `mount_lock` is a seqlock protecting mount tree/hash mutation and lockless path-walk validation.
- Mount IDs use both an xarray-backed legacy 31-bit `mnt_id` and a monotonically increasing `mnt_id_unique`, with `MNT_UNIQUE_ID_OFFSET` avoiding confusion with old IDs.
- Mount namespaces are tracked in the namespace tree, have active and passive references, rb-tree indexed mounts, first/last rb nodes for iteration, poll event counters, owner user namespace, and ucount accounting.
- `struct pinned_mountpoint` temporarily links a caller to a `struct mountpoint` while attaching or moving mounts, preventing the mountpoint from disappearing.

## Mount Lifetime and Write Access

- `alloc_vfsmnt()` allocates a mount, assigns IDs, initializes per-CPU mount counts/writer counts, list/hash nodes, and default `nop_mnt_idmap`.
- `setup_mnt()` binds a configured superblock root to a new mount and registers it on the superblock mount list.
- `mntget()` and `mntput()` implement mount reference counting with RCU-aware finalization. Cleanup removes IDs, fsnotify state, dentries, superblock activity, stuck children, and delayed frees.
- `mnt_make_shortterm()`, `kern_mount()`, `kern_unmount()`, and `kern_unmount_array()` support long-lived internal kernel mounts.
- `mnt_get_write_access()`, `mnt_want_write()`, file variants, and matching drop/put helpers protect read-only transitions and freezer state.
- `mnt_hold_writers()` and `mnt_unhold_writers()` set `WRITE_HOLD` while summing per-CPU writer counts so read-only remounts and mount attribute changes can safely block new writers.
- `sb_prepare_remount_readonly()` applies writer holds across every mount of a superblock before beginning the superblock read-only state transition.

## Mount Lookup and Mountpoints

- `__lookup_mnt()` and `lookup_mnt()` locate a child mount at a path, using `mount_lock` sequence validation and `__legitimize_mnt()` to safely take references under RCU.
- `path_is_mountpoint()` and `__is_local_mountpoint()` distinguish local namespace mountpoints from dentries mounted elsewhere.
- `get_mountpoint()` either pins an existing mountpoint or allocates a new one, sets `DCACHE_MOUNTED`, hashes it, and attaches a pin.
- `maybe_free_mountpoint()` clears `DCACHE_MOUNTED`, unhashes, queues dentry shrinking, and frees the mountpoint when no mounts or pins remain.
- `mnt_set_mountpoint()`, `make_visible()`, `attach_mnt()`, and `mnt_change_mountpoint()` attach or reparent mounts into visible parent/child and hash structures.

## Namespace Tree and Propagation

- `mnt_add_to_ns()` inserts mounts into a namespace rb-tree by unique ID and tracks first/last nodes plus visibility for restricted user-namespace mounts.
- `next_mnt()` and `skip_mnt_tree()` traverse mount subtrees in depth-first order.
- `commit_tree()` attaches newly added mount trees to the parent namespace, increments mount counts, makes the root visible, and notifies waiters.
- `clone_mnt()` duplicates a mount, preserving or adjusting mount flags, peer group, slave/master relationships, idmap, and expiry membership depending on clone flags.
- `copy_tree()` recursively clones eligible submounts, skipping or rejecting unbindable and mount-namespace-file mounts depending on flags.
- `attach_recursive_mnt()` implements the core bind/move attach path: counts mounts, propagates into shared peers, allocates group IDs, handles anonymous namespace source trees, reattaches moved mounts, commits all propagated copies, and transfers locked overmount responsibility where needed.
- Propagation mode changes are handled by `do_change_type()`, `invent_group_ids()`, `cleanup_group_ids()`, and `change_mnt_propagation()` from propagation helpers.
- `do_set_group()` supports `MOVE_MOUNT_SET_GROUP`, allowing a private mount to inherit sharing/slave relationships from a wider mount on the same superblock under strict ancestry and locked-child checks.

## Unmount and Expiry

- `may_umount_tree()` and `may_umount()` check whether mount trees appear busy.
- `umount_tree()` detaches a tree, optionally propagates unmounts, makes mounts private, updates namespace counts/events, handles connected lazy unmounts, queues fsnotify, and defers final `mntput()`.
- `do_umount()` implements regular, lazy, forced, and expiry unmount behavior, including special root handling via read-only remount.
- `__detach_mounts()` lazily disconnects all mounts on a dentry being unlinked/dropped.
- `mnt_set_expiry()`, `mark_mounts_for_expiry()`, `select_submounts()`, and `shrink_submounts()` support automount expiry and shrinkable submount cleanup.

## Mount Creation and Legacy API

- `vfs_create_mount()`, `fc_mount()`, `fc_mount_longterm()`, and `vfs_kern_mount()` convert prepared `fs_context` objects or filesystem types into detached mounts.
- `do_new_mount()` implements legacy mount creation: resolves filesystem type/subtype, creates `fs_context`, parses source/options, checks capabilities, and attaches via `do_new_mount_fc()`.
- `path_mount()` decodes legacy `mount(2)` flags into superblock flags and per-mount flags, warns on deprecated mandatory locking, and dispatches remount, bind, propagation, move, or new mount operations.
- `SYSCALL_DEFINE5(mount)` copies user strings/options and calls `do_mount()`.
- `do_reconfigure_mnt()` handles `MS_REMOUNT|MS_BIND`, changing only per-mount flags.
- `do_remount()` reconfigures the underlying superblock through `fs_context_for_reconfigure()` and then updates mount attributes.
- Timestamp expiry warnings are emitted for writable mounts whose filesystem timestamp maximum is within the uptime horizon.

## New Mount API

- `open_tree()` can return an `O_PATH` reference, a detached clone, or a new mount namespace containing a cloned tree.
- `fsmount()` turns a configured `fs_context` fd into either an anonymous detached mount fd or a new namespace fd, applying mount attributes and “too revealing” checks first.
- `move_mount()` moves or attaches mount trees from path or fd sources to path or fd targets, with support for beneath-mount semantics and propagation group setup.
- `mount_setattr()` changes mount attributes recursively or singly, including read-only, nosuid/nodev/noexec, atime policy, nosymfollow, propagation, and idmapped mount state.
- `open_tree_attr()` combines `open_tree()` with optional attribute changes before publishing the fd.
- `can_idmap_mount()` restricts idmapped mounts to filesystems that opt in, non-initial user namespaces, mounts not yet visible outside anonymous namespaces, and callers capable in relevant namespaces.
- `mount_setattr_prepare()` validates locked flags and idmap eligibility and holds writers when needed; `mount_setattr_commit()` swaps idmaps, writes flags, releases holds, and changes propagation.

## Root, Namespace Copying, and Pivot

- `alloc_mnt_ns()` creates regular or anonymous mount namespaces, initializes namespace IDs, ucounts, rb-tree state, poll waitqueue, passive refs, and user namespace ownership.
- `copy_mnt_ns()` implements `CLONE_NEWNS`, including empty mount namespaces, recursive tree copy, cross-user-namespace slave conversion, locked mount trees, and root/pwd remapping.
- `mount_subtree()` temporarily places a mount in an anonymous namespace to resolve and return a subtree root with an active superblock reference.
- `init_mount_tree()` creates an immutable `nullfs` mount and mutable `rootfs` overmount, installs them into `init_mnt_ns`, sets init task root/pwd to rootfs, and registers the namespace.
- `mnt_init()` creates caches/hash tables, initializes kernfs/sysfs/shmem/rootfs, creates `/sys/fs`, and calls `init_mount_tree()`.
- `path_pivot_root()` and `pivot_root()` enforce non-shared, mounted, reachable roots, then atomically swap the root mount and old root mount and update process fs references.

## Introspection and Proc Namespace Operations

- `/proc` mount iteration uses `mounts_op`, reading namespace mounts in unique-ID order under `namespace_sem`.
- `statmount()` fills `struct statmount` fields selected by a mask: superblock basics, mount IDs, old IDs, attributes, propagation, peer/master IDs, root path, mountpoint, type/subtype, source, options, security options, mount namespace ID, supported mask, and idmap uid/gid maps.
- `listmount()` returns mount IDs below a parent or namespace root, forward or reverse, filtering by reachability and permission.
- `lookup_mnt_ns()`, `grab_requested_mnt_ns()`, and fd/ns-id handling allow introspection of another mount namespace with passive references and capability checks.
- `mntns_operations` implements proc namespace get/put/install/owner. Installing a mount namespace requires capability in both target and caller user namespaces, rejects anonymous namespaces, requires a private `fs_struct`, switches namespace, and resets root/pwd.

## Security and User Namespace Constraints

- `may_mount()` gates namespace mutation on `CAP_SYS_ADMIN` in the current mount namespace owner.
- LSM hooks are called for mount, unmount, move mount, pivot root, kernel mount, and statfs-style disclosure.
- Locked mount flags prevent less privileged namespaces from clearing readonly, nodev, nosuid, noexec, or atime restrictions.
- `lock_mnt_tree()` locks sensitive attributes when a tree crosses user namespace boundaries and hides covered mounts from unprivileged exposure.
- `mount_too_revealing()` prevents restricted pseudo-filesystems from exposing a fuller view inside non-initial user namespaces unless an adequate visible mount already exists.
- `mnt_may_suid()` treats foreign mounts as nosuid and requires the current user namespace to match the superblock user namespace.

## Dependencies

Uses VFS internals, fs contexts, path lookup, dcache/mount propagation helpers, fsnotify, LSM hooks, user namespaces, namespace tree APIs, xarray/IDA, sysctl, proc namespace APIs, idmapped mount helpers, rootfs/nullfs/shmem initialization, and architecture syscall glue.

## Research Notes

This file is the central mount topology authority in Linux. Its main invariants are lock ordering, mount visibility under RCU path walk, propagation correctness, namespace ownership/capability checks, and writer exclusion during read-only/idmap transitions. The newer fd-based mount API and `statmount()`/`listmount()` code coexist with legacy `mount(2)` and `umount(2)` while sharing the same core tree, propagation, and lifetime machinery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/namespace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/netfs/Kconfig

## Role

Kconfig definitions for Linux netfs helper library and FS-Cache support.

## Options

- `NETFS_SUPPORT`
  - Tristate base option enabling network filesystem helpers.
  - Described as providing high-level buffered I/O helpers, read segmentation, local caching abstraction, and transparent huge page support.
- `NETFS_STATS`
  - Boolean statistics gathering option.
  - Depends on `NETFS_SUPPORT && PROC_FS`.
  - Exports local caching statistics through `/proc/fs/fscache/stats`.
  - Help text notes debugging value and possible multi-CPU cacheline overhead.
- `NETFS_DEBUG`
  - Boolean dynamic debugging option.
  - Depends on `NETFS_SUPPORT`.
  - Enables debug output controlled through `/sys/module/netfs/parameters/debug`.
- `FSCACHE`
  - Boolean general filesystem local caching manager.
  - Depends on `NETFS_SUPPORT`.
  - Enables pluggable local cache backends for network and other filesystems.
  - Points to `Documentation/filesystems/caching/fscache.rst`.
- `FSCACHE_STATS`
  - Boolean FS-Cache statistics option.
  - Depends on `FSCACHE && PROC_FS`.
  - Selects `NETFS_STATS`.
  - Exports the same `/proc/fs/fscache/stats` interface and references FS-Cache documentation.

## Dependencies

Defines feature switches consumed by `fs/netfs/Makefile` and by conditional compilation throughout the netfs and FS-Cache implementation.

## Research Notes

The configuration hierarchy makes `NETFS_SUPPORT` the base library switch and layers FS-Cache plus statistics/debug facilities on top. FS-Cache statistics automatically select netfs statistics so cache-level counters share the common reporting path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/Makefile -->
# File Research: sources/os/linux/linux/fs/netfs/Makefile

## Role

Build rules for the Linux netfs helper module/object.

## Object Composition

`netfs-y` always includes:

- `buffered_read.o`
- `buffered_write.o`
- `direct_read.o`
- `direct_write.o`
- `iterator.o`
- `locking.o`
- `main.o`
- `misc.o`
- `objects.o`
- `read_collect.o`
- `read_pgpriv2.o`
- `read_retry.o`
- `read_single.o`
- `rolling_buffer.o`
- `write_collect.o`
- `write_issue.o`
- `write_retry.o`

Conditional objects:

- `stats.o` when `CONFIG_NETFS_STATS` is enabled.
- FS-Cache core objects when `CONFIG_FSCACHE` is enabled:
  - `fscache_cache.o`
  - `fscache_cookie.o`
  - `fscache_io.o`
  - `fscache_main.o`
  - `fscache_volume.o`
- `fscache_proc.o` when both `CONFIG_FSCACHE` and `CONFIG_PROC_FS=y`.
- `fscache_stats.o` when `CONFIG_FSCACHE_STATS` is enabled.

Final target:

- `obj-$(CONFIG_NETFS_SUPPORT) += netfs.o`

## Research Notes

The Makefile shows netfs as one composite object built from shared read/write, iterator, request/object, and retry/collector code. FS-Cache is compiled into the same `netfs.o` composite only when local caching is configured.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/buffered_read.c -->
# File Research: sources/os/linux/linux/fs/netfs/buffered_read.c

## Role

High-level buffered read support for network filesystems using the page cache. It manages readahead, `read_folio`, read-for-write prefetch, cache-vs-server source selection, zero filling beyond the readable point, rolling buffer setup, read subrequest queuing, and buffered `read_iter()` dispatch.

## Read Request Expansion and Cache Setup

- `netfs_cache_expand_readahead()` lets cache backends expand the requested readahead range.
- `netfs_rreq_expand()` lets both cache and filesystem expand readahead, then calls `readahead_expand()` so the VM includes the adjusted range.
- `netfs_begin_cache_read()` starts an FS-Cache read operation for the inode cookie through `fscache_begin_read_operation()`.

## Subrequest Preparation and Dispatch

- `netfs_prepare_read_iterator()` prepares a subrequest iterator from a rolling buffer or readahead control:
  - limits server reads by `sreq_max_len`;
  - loads folios from the readahead window into the rolling buffer;
  - limits by maximum segment count;
  - truncates `io_iter` and advances the rolling buffer.
- `netfs_cache_prepare_read()` asks the cache backend whether a slice should be read from cache, downloaded from server, or otherwise filled.
- `netfs_read_cache_to_pagecache()` submits a cache read into the pagecache iterator.
- `netfs_queue_read()` marks a subrequest in progress and appends it to the read stream with release ordering so the collector can safely consume it.
- `netfs_issue_read()` dispatches subrequests to server, cache, or zero-fill completion depending on `subreq->source`.

## Pagecache Read Engine

`netfs_read_to_pagecache()` slices a request into subrequests and for each slice:

- allocates a `netfs_io_subrequest`;
- queues it on the stream before preparing source state;
- asks FS-Cache for a source;
- for server reads, respects `netfs_read_zero_point()` and inode size, converting ranges beyond the zero point to zero-fill;
- calls optional filesystem `prepare_read()`;
- prepares iterators after source/length selection;
- marks `NETFS_RREQ_ALL_QUEUED` when the final slice is queued;
- handles pause/failure flags and wakes the collector on early exit;
- records deferred setup errors in `rreq->error`.

## Public Buffered Read Helpers

- `netfs_readahead()`
  - Allocates a read request for the readahead window.
  - Enables offloaded collection.
  - Begins cache access, records stats/traces, expands the request, initializes a destination rolling buffer, and calls `netfs_read_to_pagecache()`.
- `netfs_read_folio()`
  - Waits for writeback.
  - If the folio is dirty due to streaming writes, delegates to `netfs_read_gaps()`.
  - Otherwise creates a single-folio rolling buffer, reads the folio through cache/server/zero-fill, waits, and returns while unlocking the folio on error paths.
- `netfs_read_gaps()`
  - Reads only the clean gaps around a dirty streaming-write range in a folio.
  - Constructs a bvec array with the target folio for gaps and a temporary sink folio for the dirty middle range.
  - On success, restores group/private state, frees `netfs_folio` metadata, marks the folio uptodate, and flushes dcache.
- `netfs_write_begin()` `[DEPRECATED]`
  - Legacy write-begin helper that locks a folio, optionally calls filesystem conflict handling, skips reads for full/beyond-EOF writes when possible, otherwise preloads the folio through the read engine.
- `netfs_prefetch_for_write()`
  - Preloads a folio before buffered write when cache/content requirements need read-modify-write behavior.

## Read Iterator Dispatch

- `netfs_buffered_read_iter()` rejects direct/unbuffered state, brackets `filemap_read()` with `netfs_start_io_read()` / `netfs_end_io_read()`, and exports a buffered-only read path.
- `netfs_file_read_iter()` chooses unbuffered/direct read when `IOCB_DIRECT` is set or `NETFS_ICTX_UNBUFFERED` is active; otherwise it uses buffered reads.

## Dependencies

Uses `netfs_io_request`, `netfs_io_subrequest`, rolling buffers, folios, readahead controls, FS-Cache resources, filesystem netfs operations, tracepoints, stats counters, and read collector completion paths from other netfs files.

## Research Notes

The key abstraction is that a single pagecache read can be split into heterogeneous subrequests: cache reads, server downloads, and zero-fill segments. The file also bridges streaming writes back into coherent pagecache state by reading around dirty subranges rather than forcing full folio invalidation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/buffered_read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/buffered_write.c -->
# File Research: sources/os/linux/linux/fs/netfs/buffered_write.c

## Role

High-level buffered write support for netfs users. It copies user data into pagecache folios, supports large folios, tracks dirty subranges for streaming writes, handles writethrough for sync writes, updates inode size/block estimates, switches to unbuffered writes when required, and implements `page_mkwrite` handling for mmap writes.

## Inode Size Accounting

- `netfs_update_i_size()` updates inode size after copied data extends EOF.
- Filesystems may override size handling with `ctx->ops->update_i_size`.
- Default handling updates `i_size`, updates FS-Cache cookie size when enabled, and estimates `i_blocks` growth in sector units under `inode->i_lock`.

## Folio Selection and Write Strategy

- `netfs_grab_folio_for_write()` locks a folio for writing and requests the largest supported folio order for the target write chunk.
- `netfs_perform_write()` is the main buffered copy loop:
  - sets up writethrough state for `IOCB_DSYNC`/`IOCB_SYNC`;
  - faults user pages before locking destination folios to avoid deadlocks with same-page writes;
  - waits for writeback when folio private data is owned by writeback;
  - rejects interrupted waits appropriately;
  - handles group conflicts by flushing existing dirty content;
  - copies into uptodate folios directly;
  - zero-fills writes beyond `netfs_read_zero_point()`;
  - performs whole-folio modifications without prefetch where possible;
  - prefetches for write when local caching is enabled and read-modify-write is required;
  - creates or extends `struct netfs_folio` metadata for streaming dirty ranges;
  - flushes and retries incompatible overlapping streaming writes;
  - marks fully covered folios uptodate and dirty or advances writethrough state.
- Dirty folios can carry either a filesystem group, the `NETFS_FOLIO_COPY_TO_CACHE` marker, or `struct netfs_folio` metadata describing a partial dirty range and group.

## Buffered Write Entry Points

- `netfs_buffered_write_iter_locked()`
  - Assumes caller already holds appropriate locks and ran generic write checks.
  - Removes file privileges, updates modification time, then calls `netfs_perform_write()`.
- `netfs_file_write_iter()`
  - Returns immediately for zero-length writes.
  - Uses `netfs_unbuffered_write_iter()` for direct I/O or `NETFS_ICTX_UNBUFFERED`.
  - Otherwise brackets `generic_write_checks()` and buffered write with `netfs_start_io_write()` / `netfs_end_io_write()`.
  - Calls `generic_write_sync()` after successful buffered writes.

## Writethrough and Sync Handling

For sync writes, `netfs_perform_write()` attaches a `writeback_control`, waits for prior data in range, starts a writethrough request, advances it as folios are copied, ends writethrough after the loop, and can return `-EIOCBQUEUED` for async completion.

## mmap Write Faults

`netfs_page_mkwrite()`:

- brackets the fault with `sb_start_pagefault()` / `sb_end_pagefault()`;
- locks the folio and waits for writeback;
- requires the folio to be uptodate;
- flushes and retries if an incompatible group is already attached;
- adjusts folio private group/copy-to-cache state;
- updates file time and modified-attribute state;
- calls optional `post_modify()`;
- returns `VM_FAULT_LOCKED` on success.

## Dependencies

Uses Linux folio/pagecache APIs, writeback control, dirty throttling, generic write checks/sync, FS-Cache cookie updates, netfs group/private folio helpers, writethrough helpers, tracepoints, and direct/unbuffered write entry points.

## Research Notes

The file is optimized to avoid unnecessary read-modify-write cycles while preserving correctness for local caching, content transformations, mmap writes, and filesystem grouping such as snapshots. The `netfs_folio` dirty-range metadata is central: it lets netfs track streaming writes into not-yet-uptodate folios and later read only gaps or flush conflicting ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/buffered_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/direct_read.c -->
# File Research: sources/os/linux/linux/fs/netfs/direct_read.c

## Role

Unbuffered/direct read support for netfs users. It bypasses pagecache and local cache, slices reads according to network limits, pins or copies caller iterators as needed for async operation, and integrates with direct-I/O accounting.

## Subrequest Handling

- `netfs_prepare_dio_read_iterator()` limits each read subrequest by `sreq_max_len` and optional segment limits, traces preparation, copies the current request iterator to `subreq->io_iter`, truncates it, and advances the request iterator.
- `netfs_dispatch_unbuffered_reads()` loops over the request range:
  - allocates subrequests;
  - marks them as server downloads;
  - queues them on the read stream;
  - calls optional filesystem `prepare_read()`;
  - prepares/truncates iterators;
  - updates submitted byte counts;
  - marks `NETFS_RREQ_ALL_QUEUED` at the end;
  - submits via filesystem `issue_read()`;
  - handles pause and failure state.

## Request Execution

- `netfs_unbuffered_read()` validates nonzero request length, calls `inode_dio_begin()`, dispatches subrequests, and either waits synchronously or returns `-EIOCBQUEUED` for async operation.
- The read collector, not this function, is responsible for `inode_dio_end()` after completion.

## Public Entry Points

- `netfs_unbuffered_read_iter_locked()`
  - Expects caller to hold appropriate locks.
  - Returns 0 for zero-length reads without updating atime.
  - Calls `kiocb_write_and_wait()` to flush conflicting writes.
  - Updates atime with `file_accessed()`.
  - Allocates a read request as `NETFS_DIO_READ` or `NETFS_UNBUFFERED_READ`.
  - Extracts user-backed iterators into request-owned bvec storage for async safety, or copies and advances non-user iterators.
  - Sets offloaded collection for async I/O.
  - For sync I/O, advances `ki_pos` by transferred bytes and returns the transferred count.
- `netfs_unbuffered_read_iter()`
  - Brackets the locked helper with `netfs_start_io_direct()` / `netfs_end_io_direct()`.

## Dependencies

Uses netfs request/subrequest objects, read stream collection, iterator extraction/pinning helpers, direct-I/O inode counters, generic write-and-wait helpers, and filesystem `prepare_read` / `issue_read` operations.

## Research Notes

Direct reads intentionally avoid both pagecache and FS-Cache. The code preserves async correctness by taking ownership of user-backed iterators before returning to the caller, since the original iterator cannot be trusted after an async `read_iter()` returns.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/direct_read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/direct_write.c -->
# File Research: sources/os/linux/linux/fs/netfs/direct_write.c

## Role

Unbuffered/direct write support for netfs users. It writes directly to the server, bypassing pagecache and local cache, while serializing subrequests to avoid gaps after partial failures, coordinating with direct-I/O counters, invalidating cached folios, and supporting async `kiocb` completion.

## Completion and Collection

- `netfs_unbuffered_write_done()` finalizes a write request:
  - updates inode size if no request error occurred;
  - invalidates pagecache folios covering direct-write ranges that may have appeared via mmap;
  - calls `inode_dio_end()` for direct writes;
  - wakes waiters on `NETFS_RREQ_IN_PROGRESS`;
  - advances async `ki_pos` and calls `ki_complete()`;
  - clears subrequests.
- `netfs_unbuffered_write_collect()` removes a completed subrequest from its stream, advances transferred counts and request iterator, updates collected offsets, and drops the subrequest reference.

## Direct Write Engine

`netfs_unbuffered_write()`:

- begins direct-I/O accounting for `NETFS_DIO_WRITE`;
- prepares one subrequest at a time through `netfs_prepare_write()`;
- truncates the iterator to remaining request length and stream limits;
- submits via `stream->issue_write()`;
- waits for each subrequest before dispatching the next to prevent unwritten holes after errors such as `ENOSPC`;
- records failures in `wreq->error`;
- handles retry requests by advancing past transferred bytes, invoking optional filesystem `retry_request()`, resetting subrequest flags/iterator/start/length, and reissuing;
- finalizes through `netfs_unbuffered_write_done()`.

## Public Entry Points

- `netfs_unbuffered_write_iter_locked()`
  - Creates a write request for `NETFS_DIO_WRITE` or `NETFS_UNBUFFERED_WRITE`.
  - Extracts user-backed iterators into request-owned bvec storage, recording pin/unpin state, or copies stable kernel iterators.
  - Sets `NETFS_RREQ_USE_IO_ITER` and `NETFS_RREQ_UPLOAD_TO_SERVER`.
  - Queues async writes on `system_dfl_wq` and returns `-EIOCBQUEUED`, or runs synchronously and advances `ki_pos`.
- `netfs_unbuffered_write_iter()`
  - Returns 0 for empty writes.
  - Brackets operation with `netfs_start_io_direct()` / `netfs_end_io_direct()`.
  - Runs generic write checks, privilege stripping, and time update.
  - For `IOCB_NOWAIT`, refuses to block if cached pages exist or invalidation would block.
  - Otherwise waits for dirty pagecache in range.
  - Invalidates clean cached pages before issuing the direct write.
  - Updates the netfs zero point under `inode->i_lock`.
  - Invalidates the FS-Cache cookie for the direct-write range.
  - Calls the locked direct write helper.

## Dependencies

Uses netfs write request creation, write preparation/issue/retry helpers, iterator extraction, direct-I/O counters, pagecache invalidation/writeback, FS-Cache invalidation, inode size/zero-point helpers, and async workqueue completion.

## Research Notes

The important correctness choice is serial subrequest dispatch. Unlike reads, direct writes are not freely parallelized because a later successful subrequest after an earlier partial failure could create server-side holes. Pagecache and FS-Cache are invalidated before direct writes so later buffered reads refetch authoritative data.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/direct_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_cache.c -->
# File Research: sources/os/linux/linux/fs/netfs/fscache_cache.c

## Role

FS-Cache cache-level registry and lifecycle management. It allocates cache records, looks up or names caches, transitions caches through preparing/active/withdrawn/error states, pins active caches during access, handles reference release, and exposes cache state through procfs when enabled.

## Global State

- `fscache_caches`: global list of cache records.
- `fscache_addremove_sem`: exported rwsem protecting cache list add/remove and cache registration state changes.
- `fscache_clearance_waiters`: exported waitqueue used by broader FS-Cache clearance logic.
- `fscache_cache_debug_id`: atomic counter assigning trace/debug IDs to caches.

## Cache Lookup and Acquisition

- `fscache_alloc_cache()` allocates a cache record, optionally duplicates a name, initializes the refcount/list node, and assigns a debug ID.
- `fscache_get_cache_maybe()` conditionally increments a nonzero refcount and traces acquisition.
- `fscache_lookup_cache()`:
  - first searches under read lock for an exact named or unnamed cache;
  - for unnamed lookups, can return the first named cache;
  - if not found, allocates a candidate and retries under write lock;
  - can convert an unnamed cache into a named cache when a backend cache registers with `is_cache=true`;
  - otherwise inserts the new candidate in the global list.
- `fscache_acquire_cache()` requires a name, looks up the cache, and atomically transitions it from `FSCACHE_CACHE_IS_NOT_PRESENT` to `FSCACHE_CACHE_IS_PREPARING`; if already in use it returns `-EBUSY`.

## Registration, Access, and Withdrawal

- `fscache_add_cache()` requires the preparing state, pins `n_accesses`, installs backend ops/private data, marks the cache active, and logs the cache addition.
- `fscache_begin_cache_access()` permits access only while the cache is live:
  - checks active state;
  - increments `n_accesses`;
  - uses an atomic barrier and rechecks liveness;
  - rolls back if the cache became inactive.
- `fscache_end_cache_access()` decrements `n_accesses`, traces the transition, and wakes waiters when it reaches zero.
- `fscache_io_error()` transitions an active cache to `FSCACHE_CACHE_GOT_IOERROR` and logs that the cache stopped due to I/O error.
- `fscache_withdraw_cache()` marks the cache withdrawn, drops the artificial active pin, traces the unpin, and waits until `n_accesses` reaches zero.

## Release

- `fscache_put_cache()` drops a cache reference, traces it, and on final reference removes the cache from the global list under write lock, frees the name, and frees the record.
- `fscache_relinquish_cache()` clears backend ops/private data, resets state to not-present, and releases the caller reference with a trace reason distinguishing preparation failure from normal relinquish.

## Procfs Reporting

When `CONFIG_PROC_FS` is enabled:

- `fscache_cache_states` maps cache states to single-character display codes.
- `fscache_caches_seq_show()` prints a header or one cache row containing debug ID, refcount, volume count, object count, access count, state character, and name.
- seq iteration holds `fscache_addremove_sem` for reading across traversal.
- `fscache_caches_seq_ops` exposes start/next/stop/show operations.

## Dependencies

Uses FS-Cache internal state helpers, tracepoints, Linux refcount/atomic/list/rwsem/waitqueue APIs, proc seq APIs, backend `fscache_cache_ops`, and exported synchronization primitives consumed by other FS-Cache code.

## Research Notes

The file separates cache object references from active access pins. References manage record lifetime, while `n_accesses` allows withdrawal to stop new users and wait for in-flight users. The unnamed-cache adoption path lets volumes discover a placeholder before a backend cache is fully named and registered.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_cache.c -->