# subset-b-005686 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/namespace.c -->
# sources/distributed-fs/ceph-client/fs/namespace.c

## Purpose

`namespace.c` is the VFS mount and mount-namespace implementation. It owns mount allocation, mountpoint hashing, mount tree attachment and detachment, mount propagation, namespace cloning, legacy `mount(2)`/`umount(2)`, the newer file-descriptor mount API (`open_tree`, `fsmount`, `move_mount`, `mount_setattr`, `open_tree_attr`), mount namespace proc operations, and mount enumeration/stat APIs (`statmount`, `listmount`). Although this repository path is under a Ceph client source snapshot, this file is generic Linux VFS infrastructure that network filesystems such as CephFS depend on for mount lifecycle, visibility, write access accounting, and namespace isolation.

## Important APIs, Types, and Functions

Key global state includes `namespace_sem` for topology updates and enumeration, `mount_lock` as a seqlock for mount hash/topology readers and writers, `mount_hashtable` and `mountpoint_hashtable`, `mnt_id_xa` for legacy mount ids, `mnt_group_ida` for shared peer groups, and the global `event` counter used to signal namespace changes. `struct mount_kattr` is the internal representation for `mount_setattr()` and `open_tree_attr()`, carrying set/clear flags, propagation changes, recursive mode, and idmap replacement state.

Mount lifetime is managed by `alloc_vfsmnt()`, `free_vfsmnt()`, `mntget()`, `mntput()`, `mntput_no_expire()`, `cleanup_mnt()`, `mnt_make_shortterm()`, `kern_mount()`, `kern_unmount()`, and `kern_unmount_array()`. Mount identity and propagation are handled by `mnt_alloc_id()`, `mnt_free_id()`, `mnt_alloc_group_id()`, `mnt_release_group_id()`, `invent_group_ids()`, `cleanup_group_ids()`, `change_mnt_propagation()` from `pnode.h`, and `vfsmount_to_propagation_flags()`.

Write access and read-only transitions are handled by `__mnt_is_readonly()`, `mnt_get_write_access()`, `mnt_want_write()`, file variants of those helpers, `mnt_put_write_access()`, `mnt_drop_write()`, `mnt_hold_writers()`, `mnt_unhold_writers()`, `mnt_make_readonly()`, and `sb_prepare_remount_readonly()`. These APIs are exported to filesystem code and are central to racing safely with remount-readonly and freezing.

Mountpoint and tree operations are centered on `get_mountpoint()`, `unpin_mountpoint()`, `mnt_set_mountpoint()`, `attach_mnt()`, `mnt_change_mountpoint()`, `commit_tree()`, `umount_tree()`, `attach_recursive_mnt()`, `graft_tree()`, `copy_tree()`, and `clone_private_mount()`. Namespace APIs include `alloc_mnt_ns()`, `copy_mnt_ns()`, `put_mnt_ns()`, `mount_subtree()`, `mntns_get()`, `mntns_put()`, and `mntns_install()`.

User-visible operations include `path_umount()`, `ksys_umount()`, `SYSCALL_DEFINE2(umount)`, legacy `oldumount`, `path_mount()`, `do_mount()`, `SYSCALL_DEFINE5(mount)`, `SYSCALL_DEFINE3(open_tree)`, `SYSCALL_DEFINE3(fsmount)`, `SYSCALL_DEFINE5(move_mount)`, `SYSCALL_DEFINE5(mount_setattr)`, `SYSCALL_DEFINE5(open_tree_attr)`, `SYSCALL_DEFINE4(statmount)`, `SYSCALL_DEFINE4(listmount)`, and `SYSCALL_DEFINE2(pivot_root)`.

## Control Flow

Mount creation through the legacy path begins in `mount(2)`, copies type/source/options from userspace, resolves the target path in `do_mount()`, and dispatches from `path_mount()` according to flags. Remounts go to `do_remount()` or `do_reconfigure_mnt()`, bind mounts to `do_loopback()`, propagation changes to `do_change_type()`, moves to `do_move_mount_old()`, and new filesystem mounts to `do_new_mount()`. `do_new_mount()` creates an `fs_context`, parses filesystem data, checks capabilities, obtains a `vfsmount` through `fc_mount()`, and attaches it with `do_new_mount_fc()` and `do_add_mount()`.

The fd-based API splits configuration from installation. `fsmount()` consumes an `fs_context` fd and creates a detached anonymous namespace-backed mount fd or a new namespace fd. `open_tree()` either opens an existing path, clones a detached tree, or builds a namespace containing the selected tree. `move_mount()` moves or installs trees using path/fd inputs and delegates to `vfs_move_mount()`, which either changes propagation-group membership or calls `do_move_mount()`. `mount_setattr()` builds `struct mount_kattr` from userspace, resolves the target, prepares writer holds and idmap state, then commits flags/idmaps/propagation changes.

Unmount starts at `path_umount()`, validates in `can_umount()`, and calls `do_umount()`. Forced unmount can call `sb->s_op->umount_begin`. Root unmount is converted into a readonly remount. Normal unmount takes `namespace_sem` and `mount_lock`, checks the mount is still valid and not locked, shrinks submounts, checks busy propagation, and calls `umount_tree()` with synchronous and propagation flags. Lazy detach uses `UMOUNT_PROPAGATE` without the synchronous busy check. `namespace_unlock()` later handles fsnotify, deferred mountpoint dentry shrinking, RCU synchronization, and final `mntput()`.

Tree attachment is deliberately two phase. `do_lock_mount()` or `lock_mount_exact()` pins a mountpoint and locks the target inode plus namespace. `attach_recursive_mnt()` then counts pending mounts, handles shared propagation through `propagate_mnt()`, moves a source tree out of its old parent or anonymous namespace, attaches the source and propagated copies, handles overmount replacement, updates namespace rbtrees through `commit_tree()`, and unwinds group ids and partial trees on failure.

Mount enumeration uses the namespace rbtree sorted by unique mount id. Proc mount iteration uses `mnt_find_id_at()` under `namespace_sem`. `statmount()` copies a `mnt_id_req`, resolves a mount namespace by id/fd/current namespace or a mount fd, builds fixed fields and strings in a retryable `seq_file` buffer, and copies a `struct statmount` plus string payload to userspace. `listmount()` resolves a namespace and root, verifies reachability/capability, walks the rbtree forward or backward, and returns matching child mount ids.

## State and Persistence Behavior

All state is in-kernel and memory-resident. Mounts carry per-mount flags, roots, parent/mountpoint pointers, namespace membership, propagation group ids, idmaps, expiry list entries, per-superblock mount linkage, and per-CPU ref/write counters. Namespaces carry a root mount, mount rbtree, mount count, passive/active references, user namespace ownership, ucounts charging, event counters, and poll waitqueues. No durable on-disk state is written by this file, but changes affect persistent VFS visibility and therefore filesystem access semantics.

Mount lifetime uses a combination of refcounts, RCU, task work, delayed work, and namespace references. Detached or unmounted mounts have `mnt_ns` cleared and are placed on `unmounted` until `namespace_unlock()` can run RCU cleanup. Long-term kernel mounts use `MNT_NS_INTERNAL` until explicitly made short-term. Anonymous mount namespaces are used as detached mount containers and can be dissolved on file release with `dissolve_on_fput()`.

Read-only and writer state uses per-CPU writer counters and `WRITE_HOLD` bits to make remount-readonly and mount attribute changes race safely with active writers. Mount ids are allocated from an xarray and unique 64-bit ids start above the 32-bit legacy range to avoid user ABI confusion.

## Dependencies and Integration Points

The file integrates with VFS path lookup, dcache, superblock management, fs contexts, idmapped mounts, user namespaces, proc namespace operations, sysctl, sysfs/kernfs/shmem/rootfs initialization, fsnotify, LSM hooks, pidfs/nsfs loop detection, pnode mount propagation, RCU, xarray/IDA, rbtrees, seq_file, uaccess, and task work. Filesystems interact through exported helpers such as `vfs_kern_mount()`, `kern_mount()`, `kern_unmount()`, `mnt_want_write()`, `mnt_drop_write()`, `clone_private_mount()`, `mount_subtree()`, `path_is_under()`, and mount namespace proc operations.

For CephFS and other network filesystems, the key integration points are superblock reconfiguration, mount option display (`show_options`, `show_devname`, `show_path`), write access/freeze protection, mount propagation into namespaces, idmapped mount permission checks through `FS_ALLOW_IDMAP`, and visibility restrictions in user namespaces through `mount_too_revealing()`.

## Risks and Edge Cases

The dominant risks are races among namespace topology changes, RCU path walking, final mount references, remount-readonly, and propagation. The code uses strict lock ordering (`inode_lock` before `namespace_sem`, `namespace_sem` before mount hash writes), seqlock retry loops, and memory barriers, but regressions here can produce use-after-free, leaked mounts, hidden writable mounts after readonly transitions, or namespace visibility bugs.

Security-sensitive checks include `CAP_SYS_ADMIN` in the relevant user namespace, locked mount flags that cannot be cleared, prevention of nsfs mount loops, restrictions on anonymous namespace origins, `mount_too_revealing()` for user namespaces, `mnt_may_suid()` for foreign mounts, idmapped mount restrictions, and LSM hooks for mount, umount, move, pivot, statfs, and option display. Errors here may expose covered directories, permit unsafe suid semantics, or allow namespace cycles.

Compatibility risk is high because the file implements legacy and modern mount ABIs. `statmount()` and `listmount()` must preserve id semantics, buffer sizing, restart behavior, reachability filtering, and permission behavior. The initial nullfs/rootfs layering also makes early boot assumptions visible to `pivot_root()` and namespace creation.

## Test Signals

Important signals include Linux VFS selftests for mount API behavior, namespace and idmapped mount tests, LTP mount/umount/pivot_root/unshare tests, fsnotify mount namespace notifications, `statmount`/`listmount` ABI tests with small and overflow buffers, syzkaller coverage for mount propagation and racing unmount, and filesystem-specific tests that use `mnt_want_write()`/`mnt_drop_write()` across remount-readonly and freeze. Runtime signals include `/proc/*/mountinfo`, `/proc/sys/fs/mount-max`, `statmount()` results, mount namespace poll events, and warnings from `VFS_WARN_ON_ONCE`, `WARN_ON_ONCE`, and timestamp expiry warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/netfs/Kconfig

## Purpose

This Kconfig file defines the build-time feature switches for the Linux netfs helper library and FS-Cache manager. It lets filesystems select shared network-filesystem buffered I/O, direct/unbuffered I/O, cache integration, debugging, and optional `/proc` statistics.

## Important Symbols

`NETFS_SUPPORT` is a tristate base option. It enables the `netfs` module or built-in library that provides common high-level helpers for network filesystems, including read segmentation, buffered I/O coordination, local caching hooks, and transparent huge page-oriented pagecache handling.

`NETFS_STATS` is a bool depending on `NETFS_SUPPORT && PROC_FS`. It enables netfs statistics and exposes them through `/proc/fs/fscache/stats`. The help text explicitly calls out cacheline bouncing overhead on multi-CPU systems.

`NETFS_DEBUG` is a bool depending on `NETFS_SUPPORT`. It permits dynamic debug output in netfslib and FS-Cache, controlled through `/sys/module/netfs/parameters/debug`.

`FSCACHE` is a bool depending on `NETFS_SUPPORT`. It enables the generic filesystem local caching manager used by network and other filesystems to cache data locally through pluggable backends.

`FSCACHE_STATS` is a bool depending on `FSCACHE && PROC_FS` and selects `NETFS_STATS`. It enables FS-Cache-specific statistics in the same `/proc/fs/fscache/stats` location.

## Control Flow and Build Behavior

There is no runtime control flow in this file. Its dependency graph constrains which objects the Makefile may include. `FSCACHE` cannot be enabled without `NETFS_SUPPORT`, stats require procfs, and FS-Cache stats automatically select generic netfs stats.

## State and Persistence Behavior

The file creates kernel configuration state, not runtime state. The selected symbols persist in the configured kernel build and determine whether netfs/FS-Cache code, debug knobs, and proc stats exist.

## Dependencies and Integration Points

The main dependencies are Kconfig symbol relationships with `PROC_FS` and netfs users that select or depend on `NETFS_SUPPORT`/`FSCACHE`. Documentation points to `Documentation/filesystems/caching/fscache.rst`. The Makefile consumes these symbols to include `stats.o`, `fscache_*` objects, and proc support.

## Risks and Test Signals

Risk centers on dependency drift: enabling statistics without procfs, FS-Cache without netfs base support, or a filesystem assuming cache APIs exist when `FSCACHE` is disabled. Test signals are kernel config matrix builds with `NETFS_SUPPORT=m/y`, `FSCACHE=n/y`, procfs disabled, stats enabled, and runtime checks for `/proc/fs/fscache/stats` and dynamic debug parameter availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/netfs/Makefile

## Purpose

This Makefile assembles the `netfs.o` composite object for the shared network-filesystem support library. It maps Kconfig selections to the core netfs read/write, object, locking, retry, rolling-buffer, and optional FS-Cache objects.

## Important Build Units

The unconditional `netfs-y` list includes buffered read/write, direct read/write, iterator helpers, I/O locking, module initialization, miscellaneous wait/folio helpers, object allocation, read collection, page-private copy-to-cache support, read retry/single-read, rolling buffer, write collection, write issue, and write retry. This establishes that the base netfs library includes both buffered and unbuffered paths plus shared request lifecycle and collection machinery.

`netfs-$(CONFIG_NETFS_STATS) += stats.o` adds generic statistics only when enabled. `netfs-$(CONFIG_FSCACHE)` adds cache, cookie, I/O, main, and volume FS-Cache objects. `fscache_proc.o` is included only when both procfs and FS-Cache are enabled, and `fscache_stats.o` is included with `CONFIG_FSCACHE_STATS`.

`obj-$(CONFIG_NETFS_SUPPORT) += netfs.o` makes the composite object built-in, modular, or absent according to `NETFS_SUPPORT`.

## Control Flow and State

There is no runtime control flow. The file defines link composition and therefore which symbols are available at runtime. Because `netfs.o` is composite, optional objects participate in the same module/built-in image as the base helpers.

## Dependencies and Integration Points

The Makefile integrates with Kbuild composite-object conventions and the symbols defined in `Kconfig`. It is an important integration point for netfs users such as CephFS because missing objects mean missing exports or disabled caching/statistics behavior.

## Risks and Test Signals

Risks include forgetting to add a new object to `netfs-y`, accidentally putting a core dependency behind `CONFIG_FSCACHE`, or creating unresolved symbols in config combinations. Test signals are `allmodconfig`, `allyesconfig`, minimal configs with `CONFIG_NETFS_SUPPORT=n`, `m`, and `y`, and build tests with FS-Cache and procfs independently toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/buffered_read.c -->
# sources/distributed-fs/ceph-client/fs/netfs/buffered_read.c

## Purpose

`buffered_read.c` implements high-level netfs buffered read support. It drives readahead, single-folio reads, deprecated `write_begin` read-for-write preparation, prefetch for writes, and the generic buffered `read_iter` dispatch. The file abstracts the choice among local cache, server download, and zero-fill while using pagecache folios and rolling buffers as I/O destinations.

## Important APIs and Functions

Exported APIs are `netfs_readahead()`, `netfs_read_folio()`, `netfs_write_begin()`, `netfs_prefetch_for_write()`, `netfs_buffered_read_iter()`, and `netfs_file_read_iter()`. The read pipeline uses `struct netfs_io_request`, `struct netfs_io_subrequest`, `struct netfs_inode`, `struct netfs_cache_resources`, `struct readahead_control`, `struct rolling_buffer`, and folio/private state from `internal.h`.

Important internal helpers include `netfs_cache_expand_readahead()`, `netfs_rreq_expand()`, `netfs_begin_cache_read()`, `netfs_prepare_read_iterator()`, `netfs_cache_prepare_read()`, `netfs_read_cache_to_pagecache()`, `netfs_queue_read()`, `netfs_issue_read()`, `netfs_read_to_pagecache()`, `netfs_create_singular_buffer()`, `netfs_read_gaps()`, and `netfs_skip_folio_read()`.

## Control Flow

`netfs_readahead()` allocates a request for the readahead window, offloads collection, begins a cache read operation if possible, lets cache and filesystem expand the window, initializes a rolling destination buffer, then calls `netfs_read_to_pagecache()`. The request is released immediately after submission; completion is handled by the collector path.

`netfs_read_to_pagecache()` is the central slicer. For each remaining range it allocates a subrequest, asks the cache to prepare a read, clamps server reads to the inode zero point and I/O stream limits, optionally calls filesystem `prepare_read`, prepares the iterator over pagecache folios, queues the subrequest on stream 0 under the request lock, and issues cache/server/zero-fill work. On allocation or preparation failure it sets `NETFS_RREQ_ALL_QUEUED`, wakes the collector, and records the first error in `rreq->error`.

`netfs_read_folio()` handles `->read_folio`. Dirty folios with partial streaming-write state go to `netfs_read_gaps()`, which builds a bvec layout that reads only the gaps and discards the dirty middle into a temporary sink folio. Clean non-uptodate folios use a singular rolling buffer, call the central pagecache read path, wait synchronously, and return with the folio unlocked by the collection path.

`netfs_write_begin()` and `netfs_prefetch_for_write()` preload data before a partial buffered write. They avoid reads when a full folio write or beyond-EOF write can safely zero gaps, otherwise they allocate a read-for-write request, mark the folio as not to be unlocked by normal read completion, read into the folio, and wait. `netfs_buffered_read_iter()` gates `filemap_read()` with netfs read locking. `netfs_file_read_iter()` chooses unbuffered/direct read when `IOCB_DIRECT` or `NETFS_ICTX_UNBUFFERED` is set; otherwise it uses the buffered path.

## State and Persistence Behavior

The file mutates in-memory pagecache folios, folio uptodate state, folio dirty/private state, rolling-buffer cursors, request flags, subrequest lists, transferred/submitted positions, and netfs statistics. It does not persist metadata directly. It respects `ctx->zero_point` to synthesize zeros beyond known server data and uses FS-Cache cookies via `fscache_begin_read_operation()` when caching is available.

## Dependencies and Integration Points

The code depends on filesystem-provided `netfs_inode` operations: `issue_read`, optional `prepare_read`, optional `expand_readahead`, and optional `check_write_begin`. It integrates with FS-Cache through `fscache_begin_read_operation()` and cache resource ops `expand_readahead`, `prepare_read`, and `read`. It also relies on netfs object allocation, read collection, retry handling, rolling-buffer helpers, iterator limiting, VFS `filemap_read()`, readahead APIs, and folio primitives.

## Risks and Edge Cases

Key risks are iterator lifetime errors, mismatched folio references from readahead extraction, incorrect zero-fill boundaries around `zero_point` and EOF, deadlocks between read-for-write and writeback/private folio state, and collector races around `NETFS_RREQ_ALL_QUEUED` and stream activation. `netfs_read_gaps()` is especially sensitive because it mixes real folio bvecs with a sink folio to preserve dirty data while filling gaps.

Partial reads, cache holes, cache withdrawal, large folio alignment, `IOCB_NOIO`/`IOCB_NOWAIT` behavior inherited from filemap, and deprecated `netfs_write_begin()` users are regression-prone. Incorrect handling can expose stale data, fail to zero beyond EOF, unlock folios incorrectly, or lose errors after some subrequests were already queued.

## Test Signals

Useful tests include xfstests generic buffered read/write, readahead, mmap and write_begin coverage on netfs users; FS-Cache enabled/disabled reads; reads beyond EOF and beyond `zero_point`; cache hole reads; large-folio and THP-sized readahead; dirty streaming-write folio gap reads; direct-vs-buffered dispatch tests; fault injection for allocation, cache prepare, and filesystem prepare failures; and tracepoint/stat counter inspection for read source selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/buffered_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/buffered_write.c -->
# sources/distributed-fs/ceph-client/fs/netfs/buffered_write.c

## Purpose

`buffered_write.c` implements high-level netfs buffered writes into the pagecache and mmap write-fault handling. It supports normal dirtying, writethrough for synchronous writes, streaming writes that track dirty byte ranges in non-uptodate folios, cache-aware read-modify-write, folio grouping for filesystem-specific coherency domains such as Ceph snapshots, and dispatch selection between buffered and unbuffered write paths.

## Important APIs and Functions

Exported APIs are `netfs_update_i_size()`, `netfs_perform_write()`, `netfs_buffered_write_iter_locked()`, `netfs_file_write_iter()`, and `netfs_page_mkwrite()`. Internal helpers include `__netfs_set_group()`, `netfs_set_group()`, and `netfs_grab_folio_for_write()`.

Important state types are `struct netfs_inode`, `struct netfs_group`, `struct netfs_folio`, `struct netfs_io_request`, `struct writeback_control`, folios and address spaces. `NETFS_FOLIO_COPY_TO_CACHE` and `NETFS_FOLIO_INFO`-tagged private data distinguish cache-copy and streaming-write state from filesystem group pointers.

## Control Flow

`netfs_file_write_iter()` is the generic entry. It rejects empty writes, dispatches to unbuffered/direct write if `IOCB_DIRECT` or `NETFS_ICTX_UNBUFFERED` is set, otherwise starts netfs write exclusion, runs `generic_write_checks()`, calls `netfs_buffered_write_iter_locked()`, ends write exclusion, and performs `generic_write_sync()` for successful synchronous writes.

`netfs_buffered_write_iter_locked()` performs privilege stripping and timestamp update before delegating to `netfs_perform_write()`. `netfs_perform_write()` optionally begins a writethrough request for `IOCB_DSYNC`/`IOCB_SYNC`, then loops over the user iterator. For each chunk it faults in user pages before locking the destination folio, obtains the largest suitable folio, waits for writeback if private state exists, checks signals, and chooses one of several modification modes.

If a folio is uptodate, data is copied atomically and the folio is grouped. If the folio lies beyond `ctx->zero_point`, unwritten portions are zeroed and the folio becomes uptodate. Whole-folio writes can avoid prefetch. If the file is readable or caching is enabled, partial writes prefetch existing data with `netfs_prefetch_for_write()` to avoid losing old contents. If streaming is possible, a new `struct netfs_folio` tracks `dirty_offset` and `dirty_len`; contiguous writes extend it, while overlapping or incompatible writes flush the folio and retry.

After copying, the code flushes dcache, updates i_size and estimated blocks through `netfs_update_i_size()`, advances position and written count, either marks the folio dirty or advances a writethrough request, releases the folio, and throttles dirty pages. On exit it marks modified attributes, calls optional `post_modify()`, finishes writethrough, updates `ki_pos`, and returns either bytes written or the first error.

`netfs_page_mkwrite()` handles writable mmap faults. It starts pagefault write protection, locks the folio, waits for writeback, requires uptodate data, flushes incompatible group contents to disk if needed, tags the folio with the requested group, updates file time and modified-attr state, and returns `VM_FAULT_LOCKED` with the folio held for the VM.

## State and Persistence Behavior

The file changes pagecache contents, dirty tags, folio private/group state, inode size, estimated `i_blocks`, FS-Cache cookie size, netfs modified-attribute flags, and writeback/writethrough request state. Actual persistence is deferred to writeback or writethrough paths in other netfs files and filesystem backends. Synchronous writes use writethrough request machinery and later `generic_write_sync()` to satisfy durability expectations.

## Dependencies and Integration Points

It depends on buffered read support for `netfs_prefetch_for_write()`, write issue support for writethrough (`netfs_begin_writethrough()`, `netfs_advance_writethrough()`, `netfs_end_writethrough()`), direct write support for dispatch fallback, netfs locking helpers, FS-Cache cookie update/invalidation hooks, VFS generic write checks, folio/pagecache APIs, dirty throttling, and filesystem operations `update_i_size()` and `post_modify()`.

CephFS integration is visible through `netfs_group`, which lets dirty folios be associated with coherency groups such as snapshots and forces flushing when an incompatible group attempts to modify a folio.

## Risks and Edge Cases

The riskiest areas are partial writes to non-uptodate folios, streaming-write range tracking, group transitions, and interactions with writeback-owned private data. Incorrect group handling can mix data from different coherency domains. Incorrect dirty-range tracking can lose unwritten data, especially when copy faults produce partial progress. Writethrough error ordering must preserve `-EIOCBQUEUED` for async completion and report late writeback errors when no earlier error exists.

Other edge cases include beyond-EOF zeroing, `zero_point` advancement, large folio sizing, faulting user pages before locking destination folios to avoid deadlocks, signal interruption after partial writes, mmap faults against incompatible folio groups, and file-size/block accounting races when the server later reports authoritative metadata.

## Test Signals

Relevant tests include xfstests generic buffered writes, partial writes with copy faults, writes beyond EOF, mmap write faults, fsx-style mixed mmap/read/write/truncate workloads, Ceph snapshot/group coherency tests, FS-Cache enabled partial writes, synchronous writes and writethrough completion, large-folio writes, dirty throttling under memory pressure, and fault injection for allocation, prefetch, writeback wait, and writethrough submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/buffered_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/direct_read.c -->
# sources/distributed-fs/ceph-client/fs/netfs/direct_read.c

## Purpose

`direct_read.c` implements netfs unbuffered and direct reads that bypass the pagecache and local disk cache. It slices user or kernel iterators into filesystem/server read subrequests, manages direct-I/O inode accounting, supports synchronous and asynchronous completion, and routes generic netfs read dispatch to filesystem `issue_read()` operations.

## Important APIs and Functions

Exported APIs are `netfs_unbuffered_read_iter_locked()` and `netfs_unbuffered_read_iter()`. Internal helpers are `netfs_prepare_dio_read_iterator()`, `netfs_dispatch_unbuffered_reads()`, and `netfs_unbuffered_read()`.

The central data types are `struct netfs_io_request`, `struct netfs_io_subrequest`, `struct netfs_io_stream`, `struct kiocb`, and `struct iov_iter`. The file uses request origins `NETFS_DIO_READ` and `NETFS_UNBUFFERED_READ`, stream constraints `sreq_max_len` and `sreq_max_segs`, and request flags such as `NETFS_RREQ_ALL_QUEUED`, `NETFS_RREQ_OFFLOAD_COLLECTION`, `NETFS_RREQ_PAUSE`, and `NETFS_RREQ_FAILED`.

## Control Flow

`netfs_unbuffered_read_iter()` is the unlocked public entry. It returns zero for empty reads, starts direct-I/O exclusion with `netfs_start_io_direct()`, calls the locked helper, and ends the direct-I/O section.

`netfs_unbuffered_read_iter_locked()` first waits for dirty pagecache data in the target range with `kiocb_write_and_wait()`, updates file access time, allocates a request at `ki_pos` for the iterator length, and chooses the origin based on `IOCB_DIRECT`. If the iterator is user-backed, it extracts and pins a stable bvec iterator because async I/O cannot rely on the caller's iterator after return. Kernel/non-user iterators are copied directly and advanced. Async requests store `iocb` and set offloaded collection.

`netfs_unbuffered_read()` validates nonzero length, begins inode DIO accounting, dispatches subrequests, and either waits synchronously through `netfs_wait_for_read()` or returns `-EIOCBQUEUED`. If nothing was submitted, it releases the request and ends DIO accounting immediately.

`netfs_dispatch_unbuffered_reads()` loops over the requested range. It allocates a subrequest, marks it as server download, appends it to stream 0 under the request spinlock, calls optional filesystem `prepare_read()`, clamps iterator length through `netfs_prepare_dio_read_iterator()`, updates `submitted`, marks all queued when the range is exhausted, and calls filesystem `issue_read()`. It honors request pause/failure flags between submissions.

## State and Persistence Behavior

The file does not update persistent filesystem state. It mutates request/subrequest lists, iterator positions, pinned bvec arrays, submitted/transferred counters, inode direct-I/O counters, and `ki_pos` on synchronous successful completion. Pagecache is intentionally bypassed, though dirty cached data is waited on before reading to avoid stale direct reads.

## Dependencies and Integration Points

It depends on netfs object allocation and collection, iterator extraction/limiting, direct-I/O locking in `locking.c`, VFS `kiocb_write_and_wait()` and `file_accessed()`, filesystem `netfs_ops->prepare_read` and `issue_read`, and read completion functions in `read_collect.c`. It is selected by `netfs_file_read_iter()` when direct or unbuffered mode is requested.

## Risks and Edge Cases

Risks include pinning and unpinning user pages correctly across async completion, advancing caller iterators only for bytes represented by the netfs-owned iterator, reporting partial submission when bvec allocation shortens a request, and pairing `inode_dio_begin()` with completion-side `inode_dio_end()`. A zero-sized dispatched request is treated as an internal error. Pause/retry/failure flags must prevent issuing further subrequests after backend failure.

Because direct reads bypass both pagecache and local cache, coherency depends on waiting for dirty pagecache data first and on filesystem backend consistency. Async completion must update `ki_pos` and invoke `ki_complete` through the collector path, not through this file after it returns `-EIOCBQUEUED`.

## Test Signals

Useful tests include direct read xfstests, async `io_uring`/AIO reads, reads from user and kernel iterators, dirty pagecache followed by direct read, backend `rsize`/segment-limit slicing, partial bvec extraction failures, signal interruption, request pause/retry injection, and DIO accounting checks that truncate/writeback wait correctly blocks buffered writers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/direct_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/direct_write.c -->
# sources/distributed-fs/ceph-client/fs/netfs/direct_write.c

## Purpose

`direct_write.c` implements netfs unbuffered and direct writes that send data to the server without storing it in the pagecache or local cache. It serializes subrequest dispatch to avoid leaving server-side gaps after partial failures, handles synchronous and asynchronous writes, invalidates overlapping cached folios, updates inode size, and invalidates FS-Cache contents for direct writes.

## Important APIs and Functions

Exported APIs are `netfs_unbuffered_write_iter_locked()` and `netfs_unbuffered_write_iter()`. Internal helpers are `netfs_unbuffered_write_done()`, `netfs_unbuffered_write_collect()`, `netfs_unbuffered_write()`, and `netfs_unbuffered_write_async()`.

The file uses `struct netfs_io_request` as a write request, stream 0 as the upload stream, `struct netfs_io_subrequest` for backend writes, request origins `NETFS_DIO_WRITE` and `NETFS_UNBUFFERED_WRITE`, request flags such as `NETFS_RREQ_USE_IO_ITER` and `NETFS_RREQ_UPLOAD_TO_SERVER`, and subrequest flags such as `NETFS_SREQ_FAILED`, `NETFS_SREQ_NEED_RETRY`, and `NETFS_SREQ_BOUNDARY`.

## Control Flow

`netfs_unbuffered_write_iter()` is the public entry. It rejects empty writes, starts direct-I/O exclusion, runs generic write checks, strips privileges, updates timestamps, waits for or invalidates overlapping pagecache depending on `IOCB_NOWAIT`, invalidates clean pagecache for the target range before submission, advances `ictx->zero_point` to cover the write, invalidates the FS-Cache cookie, then calls the locked helper and ends direct I/O.

`netfs_unbuffered_write_iter_locked()` allocates a write request, marks stream 0 available, extracts a stable iterator from user-backed buffers or copies kernel iterators, records request length, sets upload/use-iterator flags, and dispatches. Async writes initialize work, store `iocb`, queue to `system_dfl_wq`, and return `-EIOCBQUEUED`. Synchronous writes call `netfs_unbuffered_write()` directly, update `ki_pos`, return transferred bytes or error, and drop request references.

`netfs_unbuffered_write()` begins inode DIO accounting for direct writes, repeatedly prepares a write subrequest, truncates it to remaining data and stream limits, issues it, waits for that stream's in-progress work to finish, and then either collects success, handles failure, or retries. Retry resets iterators and subrequest fields, calls filesystem `retry_request()` when supplied, and either reruns `prepare_write()` or reissues through generic write helpers. Dispatch is serial so a later range is not written if an earlier range failed.

`netfs_unbuffered_write_done()` finalizes the request. On success it updates i_size, invalidates pagecache folios overlapping direct writes that may have appeared via mmap, ends inode DIO accounting, wakes waiters on `NETFS_RREQ_IN_PROGRESS`, completes async `kiocb` with bytes written or error, and clears subrequests.

## State and Persistence Behavior

This path directly changes server-side file contents through backend write operations. It mutates request transfer counters, stream collected positions, `ki_pos`, inode size through `netfs_update_i_size()`, `ictx->zero_point`, pagecache invalidation state, FS-Cache invalidation state, and direct-I/O exclusion counters. It avoids populating local cache or pagecache with the new data.

## Dependencies and Integration Points

The file depends on write request creation and preparation in `write_issue.c`, reissue helpers, write completion and wait helpers, iterator extraction, VFS generic write checks, pagecache invalidation, FS-Cache invalidation, and netfs direct-I/O locking. Backend integration occurs through stream `issue_write`, optional `prepare_write`, optional filesystem `retry_request`, and write subrequest termination.

## Risks and Edge Cases

Important risks include correctly pairing request references across async work and caller return, preserving `-EIOCBQUEUED`, avoiding gaps by serial dispatch, handling partial subrequest transfer before retry, invalidating pagecache without discarding dirty local data, and ensuring DIO accounting ends only after real completion. NOWAIT behavior can return `-EAGAIN` if cached pages would block invalidation.

The TODO bounce-buffer paths are explicit future integration points for encryption/compression/block expansion. Until implemented, filesystems needing transformed direct writes must either avoid this path or provide compatible iterators. Errors after partial transfer must return bytes written to the caller where VFS semantics require it.

## Test Signals

Relevant tests include direct write xfstests, async DIO/AIO/io_uring writes, NOWAIT writes with cached pages, mmap racing with DIO writes, partial backend failure and retry injection, FS-Cache invalidation checks after DIO, large writes sliced by backend limits, signal interruption during synchronous unbuffered writes, and truncate/read-after-direct-write coherency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/direct_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_cache.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_cache.c

## Purpose

`fscache_cache.c` manages FS-Cache cache-level records. It tracks registered cache backends, cache lookup/acquisition by name, cache activation and withdrawal, access pinning, I/O-error state transitions, and optional `/proc/fs/fscache/caches` enumeration.

## Important APIs and Functions

Exported globals are `fscache_addremove_sem` and `fscache_clearance_waiters`. Exported functions are `fscache_acquire_cache()`, `fscache_put_cache()`, `fscache_relinquish_cache()`, `fscache_add_cache()`, `fscache_io_error()`, and `fscache_withdraw_cache()`. `fscache_lookup_cache()`, `fscache_begin_cache_access()`, and `fscache_end_cache_access()` are non-exported or internal-facing helpers visible in this file.

Important internal state includes the global `fscache_caches` list, per-cache `ref`, `n_accesses`, `n_volumes`, `object_count`, `state`, `ops`, `cache_priv`, `name`, and `debug_id`. Cache states are displayed with `fscache_cache_states` as not-present, preparing, active, I/O error, or withdrawn.

## Control Flow

`fscache_lookup_cache()` first searches the global list under a read lock. It matches exact named caches, exact unnamed caches, or, for unnamed lookups, any named cache. If nothing matches, it allocates a candidate and repeats the search under the write lock. A newly added real cache can claim an existing unnamed record, allowing volumes that found an unnamed placeholder to attach to the backend when it appears. Otherwise the candidate is inserted and returned with one reference.

`fscache_acquire_cache()` looks up a named cache for backend registration and atomically transitions it from `FSCACHE_CACHE_IS_NOT_PRESENT` to `FSCACHE_CACHE_IS_PREPARING`. If another backend is using the tag, it drops the reference and returns `-EBUSY`.

`fscache_add_cache()` publishes a prepared backend. It requires the preparing state, artificially increments `n_accesses` to keep access wakeups suppressed while active, installs backend ops and private data under `fscache_addremove_sem`, transitions to active, and logs the added cache.

`fscache_begin_cache_access()` permits users to pin a live cache. It checks liveness, increments `n_accesses`, uses a memory barrier, rechecks liveness, and backs out if the cache was withdrawn concurrently. `fscache_end_cache_access()` decrements `n_accesses` and wakes waiters when it reaches zero.

`fscache_io_error()` transitions an active cache to I/O-error state and logs that it stopped. `fscache_withdraw_cache()` marks the cache withdrawn, drops the artificial active pin, and waits for `n_accesses` to drain. `fscache_relinquish_cache()` clears backend ops/private data, resets state to not-present, and releases the backend's reference. `fscache_put_cache()` removes and frees a record when the final ref drops.

## State and Persistence Behavior

The file manages in-memory cache registry state. It does not persist data itself; actual cache storage is delegated to backend `fscache_cache_ops`. State transitions determine whether volumes/cookies may access cache resources. The `n_accesses` counter is a runtime pin that prevents backend withdrawal from racing with ongoing operations.

## Dependencies and Integration Points

It depends on FS-Cache internal state helpers/macros, tracepoints, refcount APIs, rwsems, wait queues, and optional procfs seq operations. Cache backends call `fscache_acquire_cache()`, then `fscache_add_cache()`, later `fscache_withdraw_cache()` and `fscache_relinquish_cache()`. Volume and cookie code uses cache lookup/access state to bind network filesystem data to cache backends.

## Risks and Edge Cases

Concurrency risks center on lookup versus backend registration, unnamed placeholder adoption, state transitions during access pinning, and final reference removal while iterating `/proc`. `fscache_begin_cache_access()` must recheck liveness after incrementing `n_accesses`; otherwise withdrawal could complete while an operation begins. Backend error handling must reliably prevent new accesses after `fscache_io_error()`.

Naming behavior is subtle: unnamed lookups can match the first named cache, and real caches can rename an unnamed placeholder. This is designed behavior but can surprise tests if multiple cache backends or volumes are configured. `fscache_put_cache()` removes the cache record under the global write semaphore only after refcount reaches zero.

## Test Signals

Useful tests include cache backend registration and duplicate-name `-EBUSY`, unnamed volume before named backend registration, withdrawal waiting for active accesses, I/O-error transition blocking new access, procfs cache listing under concurrent add/remove, refcount leak checks, and FS-Cache integration tests that mount a netfs with cache enabled, withdraw the backend, and verify graceful fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_cache.c -->
