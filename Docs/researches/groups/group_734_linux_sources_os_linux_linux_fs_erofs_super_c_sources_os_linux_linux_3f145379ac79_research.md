# Group Research: group_734_linux_sources_os_linux_linux_fs_erofs_super_c_sources_os_linux_linux_3f145379ac79

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/super.c -->
# File Research: sources/os/linux/linux/fs/erofs/super.c

## Purpose
Implements the EROFS filesystem superblock, mount-context, option parsing, device setup, sysfs/export integration, inode-cache lifecycle, and module init/exit paths.

## Main Elements
- Logging and inode allocation: `_erofs_printk()`, `erofs_alloc_inode()`, `erofs_free_inode()`, and the `erofs_inode` slab cache.
- Metadata and superblock parsing: `erofs_read_metadata()`, `erofs_superblock_csum_verify()`, and `erofs_read_superblock()` validate magic, block size, incompatible features, checksum, 48-bit fields, metabox fields, xattr prefix locations, packed inode IDs, UUID, volume name, and compression configuration.
- Multi-device setup: `erofs_init_device()` and `erofs_scan_devices()` parse device slots, open block devices or backing files, register fscache cookies, probe DAX, track `total_blocks`, and manage an IDR-backed device context.
- Mount options: `erofs_fs_parameters[]`, `erofs_fc_parse_param()`, and `erofs_fc_set_dax_mode()` handle xattrs, ACLs, compressed-cache strategy, DAX, extra devices, fscache `fsid`, `domain_id`, direct I/O, filesystem offsets, and page-cache inode sharing.
- Export support: `erofs_encode_fh()`, `erofs_fh_to_dentry()`, `erofs_fh_to_parent()`, and `erofs_get_parent()` expose stable NID-based file handles.
- Mount construction: `erofs_fc_fill_super()` initializes `super_block` operations, file-backed/fscache/block-device mode, DAX constraints, compressed subsystem state, packed/metabox/root inodes, shrinker registration, xattr prefixes, sysfs name, and sysfs registration.
- Teardown and module lifecycle: `erofs_put_super()`, `erofs_kill_sb()`, `erofs_module_init()`, and `erofs_module_exit()` unwind sysfs, shrinker, internal inodes, fscache, DAX, device contexts, and compression subsystems.
- VFS callbacks: `erofs_statfs()`, `erofs_show_options()`, `erofs_evict_inode()`, and `erofs_sops`.

## Dependencies And Integration
This file is the top-level bridge between EROFS and VFS mount APIs, anonymous inode-backed modes, block-device/file-backed/fscache I/O, DAX, xattrs, POSIX ACLs, exportfs, sysfs, compression, shrinkers, and EROFS internal inode/name lookup code.

## Risk Notes
Mount correctness depends on strict validation of on-disk feature flags, block sizes, 48-bit fields, xattr prefix IDs, device counts, and metabox self-loop prevention. File-backed mounts explicitly reject stacked filesystems to avoid kernel stack recursion. Device and fscache setup have many partially initialized resources, so cleanup ordering is important. DAX and inode-share options are mutually constrained and may be silently disabled when unsupported.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/sysfs.c -->
# File Research: sources/os/linux/linux/fs/erofs/sysfs.c

## Purpose
Provides EROFS sysfs objects and attributes for global feature reporting and per-mounted-superblock tuning/debug controls.

## Main Elements
- Attribute descriptors: `struct erofs_attr` plus macros for feature, integer, boolean, and function-backed sysfs attributes.
- Per-superblock attributes: `sync_decompress`, `drop_caches`, and `dir_ra_bytes`, gated by compression configuration where relevant.
- Global attributes: optional compression acceleration engine control and the `features` kobject entries for supported on-disk features such as compression configs, big pclusters, chunked files, device tables, superblock checksums, fragments, dedupe, 48-bit layout, and metabox.
- Generic show/store dispatch: `erofs_attr_show()` and `erofs_attr_store()` map attributes to offsets in `struct erofs_sb_info` or `struct erofs_mount_opts`, parse user input, validate values, drop compressed-data caches, invalidate managed pages, and enable/disable crypto acceleration engines.
- Object lifecycle: `erofs_register_sysfs()`, `erofs_unregister_sysfs()`, `erofs_init_sysfs()`, and `erofs_exit_sysfs()` manage the `/sys/fs/erofs` kset, the global `features` kobject, and per-superblock kobjects.

## Dependencies And Integration
Used by `super.c` during mount and unmount. It integrates with Linux kobjects/sysfs, the EROFS compression cache shrinker, managed cache mapping invalidation, and optional accelerated decompression crypto engine controls.

## Risk Notes
The pointer-offset attribute mechanism is compact but depends on correct `struct_type` and `offset` metadata. Store handlers directly mutate mounted filesystem runtime fields, so validation is limited to each attribute's known range. Sysfs unregister waits for kobject completion to avoid freeing `erofs_sb_info` while sysfs references still exist.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/xattr.c -->
# File Research: sources/os/linux/linux/fs/erofs/xattr.c

## Purpose
Implements EROFS extended-attribute initialization, lookup, listing, long-prefix support, POSIX ACL retrieval, and inode-share fingerprint extraction.

## Main Elements
- Iterator state: `struct erofs_xattr_iter` carries metadata buffers, current position, output buffer state, lookup name/index, and listing dentry.
- Per-inode xattr initialization: `erofs_init_inode_xattrs()` reads the xattr ibody header, name filter, shared-xattr count, and shared xattr ID array once per inode using bit locks and memory barriers.
- Entry walking helpers: `erofs_xattr_copy_to_buffer()`, `erofs_listxattr_foreach()`, and `erofs_getxattr_foreach()` process possibly block-crossing xattr entries, names, values, and long prefix infixes.
- Inline and shared xattr scans: `erofs_xattr_iter_inline()` walks inode-local xattrs, while `erofs_xattr_iter_shared()` resolves shared xattrs from the superblock xattr area, including optional metabox storage.
- Public operations: `erofs_getxattr()` uses an xxhash name filter shortcut when valid, then searches inline and shared xattrs; `erofs_listxattr()` emits listable names with prefixes.
- VFS xattr handlers: user, trusted, and optional security handlers are exposed through `erofs_xattr_handlers`, with user xattrs controlled by mount options and trusted xattrs controlled by `CAP_SYS_ADMIN`.
- Long-prefix lifecycle: `erofs_xattr_prefixes_init()` reads variable-sized long-prefix metadata and prepares inode-share prefix strings; `erofs_xattr_prefixes_cleanup()` frees them.
- Optional features: `erofs_get_acl()` reads POSIX ACL xattrs, `erofs_inode_has_noacl()` uses the xattr name filter as a fast no-ACL check, and `erofs_xattr_fill_inode_fingerprint()` builds page-cache sharing fingerprints from configured xattrs plus domain ID.

## Dependencies And Integration
Integrates with EROFS metadata buffers, inode layout fields, superblock xattr prefix state initialized by `super.c`, Linux VFS xattr handlers, POSIX ACL conversion, security xattrs, xxhash filtering, and optional page-cache sharing.

## Risk Notes
Corruption checks around `xattr_isize`, shared counts, entry sizes, and prefix lengths are critical because metadata can cross block boundaries. The initialized bit is paired with memory barriers so readers do not observe partially filled xattr fields. The name-filter optimization must be disabled when reserved format bits indicate incompatible filter semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/xattr.h -->
# File Research: sources/os/linux/linux/fs/erofs/xattr.h

## Purpose
Declares the EROFS xattr, POSIX ACL, no-ACL filter, and inode-share fingerprint interfaces used by the rest of the EROFS filesystem.

## Main Elements
- Includes `internal.h`, POSIX ACL xattr declarations, and generic Linux xattr declarations.
- When `CONFIG_EROFS_FS_XATTR` is enabled, declares `erofs_xattr_handlers`, `erofs_xattr_prefixes_init()`, `erofs_xattr_prefixes_cleanup()`, and `erofs_listxattr()`.
- When xattrs are disabled, provides no-op cleanup/init stubs and NULL-style macros for listxattr and xattr handlers.
- When POSIX ACLs are enabled, declares `erofs_get_acl()`; otherwise it maps the ACL getter to NULL.
- Always declares `erofs_xattr_fill_inode_fingerprint()` and `erofs_inode_has_noacl()` for optional call sites that may have configuration-specific definitions or stubs elsewhere.

## Dependencies And Integration
This header is consumed by `super.c`, inode operations, and xattr-related EROFS code to wire VFS xattr handlers and ACL hooks according to Kconfig.

## Risk Notes
Configuration stubs must stay type-compatible with call sites. The always-declared fingerprint and no-ACL helpers require matching definitions or configuration-provided inline behavior elsewhere in the EROFS internal headers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/zdata.c -->
# File Research: sources/os/linux/linux/fs/erofs/zdata.c

## Purpose
Implements compressed EROFS folio read and readahead, including pcluster sharing, compressed-page caching, bio submission, decompression scheduling, and decompressed-output distribution.

## Main Elements
- Core structures: `z_erofs_pcluster` represents a compressed physical cluster with lock/refcount, compressed bvecs, output bvecs, algorithm, size, and partial-decode state; `z_erofs_frontend` builds pcluster chains for a read; `z_erofs_backend` performs decompression.
- Bvec storage: inline bvecs plus linked bvset pages support variable numbers of output bvecs with `z_erofs_bvec_enqueue()` and dequeue helpers.
- Pcluster allocation: size-class slab caches are created by `z_erofs_create_pcluster_pool()` and used by `z_erofs_alloc_pcluster()`.
- Worker infrastructure: `z_erofs_init_subsystem()` initializes decompressors, pcluster slabs, and a high-priority workqueue; optional per-CPU kthread workers and CPU hotplug handlers provide lower-overhead atomic-context dispatch.
- Managed compressed cache: `z_erofs_init_super()` creates `managed_cache`, while `z_erofs_bind_cache()`, `z_erofs_cache_release_folio()`, `z_erofs_cache_invalidate_folio()`, and shrinker helpers connect cached compressed folios to pclusters.
- Pcluster registration and lifetime: `z_erofs_register_pcluster()`, `z_erofs_pcluster_begin()`, `z_erofs_get_pcluster()`, `z_erofs_put_pcluster()`, and `z_erofs_shrink_scan()` coordinate XArray lookup, deduplication of inflight work, lockref state, and RCU freeing.
- Frontend scan: `z_erofs_scan_folio()` maps logical ranges, handles fragments and holes, attaches folio pages to pclusters, tracks partial/full decode state, and marks online folio completion state.
- Backend decode: `z_erofs_decompress_pcluster()` builds input/output page arrays, handles overlapped in-place I/O, invokes the selected decompressor, copies secondary outputs, releases short-lived pages, and resets or frees pclusters.
- I/O submission: `z_erofs_fill_bio_vec()`, `z_erofs_submit_queue()`, and `z_erofs_endio()` prepare cached/in-place/temporary compressed pages, submit bios through block, file-backed, or fscache paths, and kick decompression after I/O completion.
- Address-space operations: `z_erofs_read_folio()` and `z_erofs_readahead()` implement compressed reads, readmore expansion, reverse-order readahead scanning, and queue execution.

## Dependencies And Integration
This file depends on EROFS mapping from `zmap.c`, decompressor backends, managed cache and shrinker utilities from `zutil.c`, block/fileio/fscache bio helpers, pagepool helpers, tracepoints, PSI memory-stall tracking, optional CPU hotplug and per-CPU kthreads, and VFS address-space operations.

## Risk Notes
Most risk is concurrency-related: pclusters are shared across reads through an XArray, protected by mutexes, lockrefs, spinlocks, and RCU. Managed folio `private` state, preallocated cache folios, in-place pages, short-lived pages, and bvec pages have different lifetimes and must not be mixed. Decompression can run synchronously, on an unbound workqueue, or on per-CPU kthreads, so bio completion and foreground waiting must preserve queue ownership. Partial decoding, fragments, metadata-backed compressed data, and file-backed/fscache I/O all add separate error and cleanup paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/zdata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/zmap.c -->
# File Research: sources/os/linux/linux/fs/erofs/zmap.c

## Purpose
Translates EROFS compressed inode metadata into logical-to-physical block mappings for compressed reads and fiemap-style reporting.

## Main Elements
- Mapping recorder: `struct z_erofs_maprecorder` holds inode, target map, current logical cluster, cluster type, head type, deltas, physical block, compressed-block count, tail metadata offset, and metabox state.
- Full index loading: `z_erofs_load_full_lcluster()` reads standard lcluster indexes and decodes HEAD/NONHEAD type, cluster offset, deltas, partial references, physical block, and big-pcluster block counts.
- Compact index loading: `z_erofs_load_compact_lcluster()` decodes packed 2-byte/4-byte lcluster formats with bit extraction, special final-pack delta handling, big-pcluster CBLKCNT handling, and physical block reconstruction.
- Extent discovery: `z_erofs_extent_lookback()`, `z_erofs_get_extent_compressedlen()`, and `z_erofs_get_extent_decompressedlen()` find the head cluster, compressed byte length, and full decompressed span.
- Legacy/full-or-compact mapping: `z_erofs_map_blocks_fo()` handles normal compressed maps, ztailpacking inline data, fragment pclusters in the packed inode, partial references, algorithm selection, and readmore/fiemap expansion.
- Extent-style mapping: `z_erofs_map_blocks_ext()` supports newer extent records, including short records with implicit physical continuity, binary search over large logical starts, fragments, partial references, and shifted/interlaced/plain algorithm selection.
- Inode compression metadata initialization: `z_erofs_fill_inode()` reads the map header once per inode, initializes advise bits, cluster size, algorithms, extents, fragment offsets, inline tail data size, and validates big-pcluster feature consistency.
- Sanity checks: `z_erofs_map_sanity_check()` validates algorithm support, compressed and decompressed lengths, maximum pcluster sizes, and 48-bit physical address bounds.
- Public mapping and iomap reporting: `z_erofs_map_blocks_iter()` drives initialization and mapping; `z_erofs_iomap_report_ops` reports compressed extents, fragments, and holes through iomap.

## Dependencies And Integration
Used by `zdata.c` read and readahead paths, fiemap/reporting paths, EROFS metadata buffer APIs, inode compression fields, tracepoints, and superblock feature flags parsed in `super.c`.

## Risk Notes
The compact index decoder is bit-dense and relies on careful handling of special NONHEAD encodings, lookback/lookahead deltas, and old mkfs quirks. Mapping results are trusted by decompression I/O, so corruption checks for unsupported algorithms, impossible extents, pcluster limits, and 48-bit overflow are essential. Tailpacking and fragment handling mutate cached inode fields during initialization and must be serialized by the inode compression init bit lock.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/zmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/zutil.c -->
# File Research: sources/os/linux/linux/fs/erofs/zutil.c

## Purpose
Provides shared compressed-EROFS utility infrastructure: global decompression buffers, reserved page allocation, pagepool release, and the global pcluster shrinker.

## Main Elements
- Global buffer pool: `struct z_erofs_gbuf`, `z_erofs_get_gbuf()`, and `z_erofs_put_gbuf()` provide per-CPU-indexed vmapped buffers protected by spinlocks and migration disabling.
- Buffer sizing: `z_erofs_gbuf_growsize()` grows all global buffers to a requested page count without shrinking existing buffers.
- Init/exit: `z_erofs_gbuf_init()` allocates buffer descriptors and an optional reserved-page pool; `z_erofs_gbuf_exit()` unmaps buffers, frees pages, and releases descriptors.
- Page allocation helpers: `__erofs_allocpage()` first uses a caller pagepool, then optional reserved pages, then `alloc_page()`; `erofs_release_pages()` returns pages to the reserved pool when possible or drops them.
- Shrinker registration: `erofs_shrinker_register()` and `erofs_shrinker_unregister()` add/remove mounted superblocks to a global list and drain managed pcluster slots during unmount.
- Shrinker callbacks: `erofs_shrink_count()` reports global reclaimable pcluster count, and `erofs_shrink_scan()` fairly iterates mounted EROFS superblocks, taking `umount_mutex` and calling `z_erofs_shrink_scan()`.
- Subsystem lifecycle: `erofs_init_shrinker()` allocates/registers the shrinker, and `erofs_exit_shrinker()` frees it.

## Dependencies And Integration
Used by compressed decompressor implementations and `zdata.c` for temporary buffers, emergency page allocation, pagepool handling, and reclaim of cached compressed pclusters across all mounted EROFS instances.

## Risk Notes
`z_erofs_get_gbuf()` relies on CPU migration being disabled so the selected buffer remains stable until `z_erofs_put_gbuf()`. Growing buffers must preserve old page arrays while safely swapping vmapped pointers under each buffer lock. The shrinker walks a global superblock list while coordinating with unmount through `umount_mutex`; failure to drain managed slots before unregistration would leave cached pclusters behind.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/zutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/eventfd.c -->
# File Research: sources/os/linux/linux/fs/eventfd.c

## Purpose
Implements Linux `eventfd`, an anonymous-file counter object used for userspace and kernel event notification through read, write, poll, and exported context APIs.

## Main Elements
- Core state: `struct eventfd_ctx` holds a kref, waitqueue, 64-bit counter, flags, and proc-visible ID.
- Kernel signaling: `eventfd_signal_mask()` increments the counter up to `ULLONG_MAX`, wakes poll waiters, supports an extra poll mask, and guards against recursive eventfd wakeups with `current->in_eventfd`.
- Lifetime management: `eventfd_ctx_put()`, `eventfd_free()`, and `eventfd_free_ctx()` handle kref release and IDA ID cleanup.
- File operations: `eventfd_poll()` reports readable, writable, and overflow/error states; `eventfd_read()` blocks or returns `-EAGAIN` until count is nonzero, then consumes either one semaphore unit or the whole count; `eventfd_write()` validates a u64 write and blocks until the counter can accept it.
- Atomic waitqueue removal: `eventfd_ctx_remove_wait_queue()` removes an external wait entry while reading/resetting the counter under the waitqueue lock.
- Proc fdinfo: `eventfd_show_fdinfo()` reports count, ID, and semaphore mode.
- External acquisition APIs: `eventfd_fget()`, `eventfd_ctx_fdget()`, and `eventfd_ctx_fileget()` validate eventfd files and take file/context references.
- Syscalls: `eventfd2` and legacy `eventfd` create anonymous inode files through `do_eventfd()`, validate flags, initialize context, allocate IDs, and publish descriptors.

## Dependencies And Integration
Integrates with anonymous inodes, VFS file operations, poll/epoll waitqueues, exported kernel notification users, proc fdinfo, IDA allocation, krefs, and user-copy/iov-iter helpers.

## Risk Notes
All counter updates occur under `ctx->wqh.lock`, and the poll path depends on ordering through `poll_wait()` waitqueue locking to avoid missed wakeups. Recursive wakeups can deadlock or overflow stacks, so `current->in_eventfd` is used around wakeup paths. Writes must reject `ULLONG_MAX` and reserve one count value so overflow can be signaled as `EPOLLERR`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/eventfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/eventpoll.c -->
# File Research: sources/os/linux/linux/fs/eventpoll.c

## Purpose
Implements Linux `epoll`: anonymous eventpoll files, interest set management, ready-list delivery, nested epoll loop/path checks, file cleanup, busy-poll controls, and epoll syscalls.

## Main Elements
- Core objects: `struct eventpoll` owns the mutex, waitqueues, ready list, overflow list, RB tree of watched descriptors, upward refs, wakeup source, user quota, refcount, and optional busy-poll settings; `struct epitem` represents one watched `(file, fd)` pair and its poll wait entries.
- Ready state machine: `ep_start_scan()` steals `rdllist` and diverts callbacks to `ovflist`; `ep_done_scan()` drains overflow back to the ready list and wakes waiters. Helpers encode scan and per-item overflow state.
- Busy poll support: optional NAPI tracking, timeout/budget/preference ioctls, and IRQ suspend/resume logic are integrated with ready checks.
- Wakeup and poll hooks: `ep_ptable_queue_proc()` registers `ep_poll_callback()` on target waitqueues; callbacks filter masks, queue ready items, handle `EPOLLEXCLUSIVE`, wake `ep->wq` and poll waiters, maintain wakeup sources, update busy-poll NAPI IDs, and implement the `POLLFREE` release/acquire handshake with waitqueue removal.
- Removal and lifetime: `ep_remove()`, `ep_remove_file()`, `ep_remove_epi()`, `eventpoll_release_file()`, and `ep_clear_and_put()` coordinate explicit deletes, epoll-file close, watched-file close, pollwait draining, RB tree erasure, file `f_ep` cleanup, RCU freeing, and `eventpoll` refcounts.
- Polling epoll files: `ep_eventpoll_poll()` and `ep_item_poll()` support polling nested epoll instances with lockdep nesting depth annotations.
- Insertion and modification: `ep_alloc_epitem()`, `ep_register_epitem()`, `ep_insert()`, and `ep_modify()` enforce per-user watch limits, install target-file links, allocate wakeup sources, attach poll callbacks, sample initial readiness, and update event masks with memory barriers.
- Loop and path checks: `ep_ctl_lock()`, `ep_loop_check()`, `ep_loop_check_proc()`, `ep_get_upwards_depth_proc()`, `reverse_path_check()`, and `path_limits[]` prevent cycles, excessive nesting, and excessive wakeup path amplification under `epnested_mutex`.
- Event delivery: `ep_deliver_event()` repolls items, copies events to userspace, handles oneshot and edge-triggered semantics, and requeues level-triggered items; `ep_send_events()` and `ep_poll()` implement wait, timeout, signal, busy-poll, and retry behavior.
- Syscalls and helpers: `epoll_create`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `epoll_pwait`, `epoll_pwait2`, compat variants, `epoll_sendevents()`, KCMP helper lookup, proc fdinfo, and `eventpoll_init()`.

## Dependencies And Integration
This file is central VFS/poll infrastructure. It integrates with anonymous inodes, waitqueues, file reference and `f_ep` tracking, RCU, RB trees, per-user counters, power-management wakeup sources, sysctl, proc fdinfo, signal-mask helpers, user-copy helpers, optional KCMP, compat syscalls, optional networking busy-poll/NAPI, and epoll UAPI constants.

## Risk Notes
The implementation is dominated by concurrency constraints. Lock ordering across `epnested_mutex`, `ep->mtx`, `file->f_lock`, and `ep->lock` must remain strict. Ready delivery intentionally drops `ep->lock` while copying to userspace, so `ovflist` must catch concurrent callbacks without losing events. File teardown races are handled by file refcount pinning, `f_ep` under `file->f_lock`, RCU freeing, and two-pass pollwait/tree draining. Nested epoll checks must remain atomic with insertion to prevent cycles or wakeup amplification. `POLLFREE`, `EPOLLONESHOT`, `EPOLLET`, `EPOLLEXCLUSIVE`, wakeup sources, and busy-poll all add separate correctness constraints.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/eventpoll.c -->