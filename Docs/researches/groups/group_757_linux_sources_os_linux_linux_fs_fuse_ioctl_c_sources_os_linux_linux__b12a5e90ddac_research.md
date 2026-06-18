# Group Research: group_757_linux_sources_os_linux_linux_fs_fuse_ioctl_c_sources_os_linux_linux__b12a5e90ddac

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/ioctl.c -->
# File Research: sources/os/linux/linux/fs/fuse/ioctl.c

Implements FUSE ioctl dispatch, including unrestricted retry-style deep-copy ioctls, restricted `_IOC_*`-decoded ioctls, compat handling, fs-verity ioctl sizing, and file attribute get/set via private ioctl opens.

Key entry points:
- `fuse_do_ioctl()` builds and submits `FUSE_IOCTL` requests, copies user input pages into request folios, handles server-requested `FUSE_IOCTL_RETRY`, validates returned iovecs, copies output data back to userspace, and returns either transport errors or `outarg.result`.
- `fuse_ioctl_common()`, `fuse_file_ioctl()`, and `fuse_file_compat_ioctl()` are VFS-facing wrappers that enforce connection process permission and bad-inode checks.
- `fuse_fileattr_get()` / `fuse_fileattr_set()` implement `fileattr` support by opening a temporary FUSE file and issuing `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FSGETXATTR`, or `FS_IOC_FSSETXATTR`.

Important control flow:
- `fuse_send_ioctl()` normalizes `-ENOSYS` to `-ENOTTY`, both as request error and as server result.
- `fuse_copy_ioctl_iovec_old()` supports the legacy ABI where returned iovecs were native/compat `struct iovec`; `fuse_copy_ioctl_iovec()` uses `struct fuse_ioctl_iovec` for protocol minor >= 16 and validates truncation/compat conversions.
- Restricted ioctls prebuild in/out iovecs from `_IOC_DIR` and `_IOC_SIZE`; unrestricted ioctls allow iterative retry with server-provided iovecs.
- `FS_IOC_MEASURE_VERITY` and `FS_IOC_ENABLE_VERITY` receive special setup because their effective buffer lengths are not represented by the basic ioctl size alone.

Dependencies and integration:
- Uses `fuse_simple_request()`, `fuse_folios_alloc()`, `copy_folio_from_iter()`, `copy_folio_to_iter()`, FUSE protocol structs, and VFS fileattr/fs-verity definitions.
- Exports `fuse_do_ioctl()` for other FUSE-related consumers such as CUSE.
- Temporary private ioctl path uses `fuse_file_open()` and `fuse_file_release()`.

Risks and invariants:
- Iovec sizes are bounded by `fc->max_pages << PAGE_SHIFT`; retry count is bounded by `FUSE_IOCTL_MAX_IOV`.
- Restricted mode rejects server retry to prevent arbitrary deep copies.
- Output size larger than advertised `inarg.out_size` is treated as protocol error.
- The function allocates both folio arrays and an iovec page; all exit paths release folios and memory.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/iomode.c -->
# File Research: sources/os/linux/linux/fs/fuse/iomode.c

Manages per-inode FUSE I/O modes that prevent unsafe mixing of cached page-cache I/O, direct I/O, and passthrough backing-file I/O.

Key entry points:
- `fuse_file_io_open()` decides the mode for a newly opened FUSE file.
- `fuse_file_io_release()` drops mode references on close.
- `fuse_file_cached_io_open()` enters cached mode and waits for conflicting uncached/direct/passthrough users.
- `fuse_inode_uncached_io_start()` and `fuse_inode_uncached_io_end()` maintain negative `iocachectr` counts for uncached/passthrough mode.

Important control flow:
- Positive `fi->iocachectr` means cached users exist; negative means uncached users exist.
- Cached opens wait while `fuse_is_io_cache_wait()` is true, setting `FUSE_I_CACHE_IO_MODE` so direct writers serialize.
- Passthrough opens require `CONFIG_FUSE_PASSTHROUGH`, connection passthrough support, valid open flags, and a backing id from the open response.
- If an inode already has a backing file, later opens must also use `FOPEN_PASSTHROUGH`.

Dependencies and integration:
- Coordinates with `fuse_passthrough_open()` / `fuse_passthrough_release()`.
- Uses `fuse_inode_backing()`, `fuse_inode_backing_set()`, `fuse_backing_put()`, `fi->direct_io_waitq`, and inode state bits from `fuse_i.h`.

Risks and invariants:
- Server mistakes in open mode are converted to user-visible `-EIO`.
- `FOPEN_PARALLEL_DIRECT_WRITES` is stripped unless `FOPEN_DIRECT_IO` is present.
- First passthrough open excludes cached mode; last passthrough close wakes cached waiters and drops backing reference.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/iomode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/passthrough.c -->
# File Research: sources/os/linux/linux/fs/fuse/passthrough.c

Implements FUSE passthrough operations that forward reads, writes, splice, and mmap to a kernel backing file while preserving FUSE-visible inode metadata effects.

Key entry points:
- `fuse_passthrough_read_iter()`, `fuse_passthrough_write_iter()`
- `fuse_passthrough_splice_read()`, `fuse_passthrough_splice_write()`
- `fuse_passthrough_mmap()`
- `fuse_passthrough_open()` and `fuse_passthrough_release()`

Important control flow:
- Read/splice-read/mmap use a `backing_file_ctx` with `ff->cred` and an accessed callback that invalidates FUSE atime.
- Write/splice-write lock the FUSE inode, call backing-file write helpers, and update FUSE write attributes through `fuse_passthrough_end_write()`.
- `fuse_passthrough_open()` validates a positive backing id, looks up `struct fuse_backing`, opens a per-FUSE-file backing file using `backing_file_open()`, and stores backing file plus credentials in `struct fuse_file`.
- Release closes the backing file and drops credentials.

Dependencies and integration:
- Depends on Linux backing-file helpers and FUSE backing-id registry.
- Called from `iomode.c` when `FOPEN_PASSTHROUGH` is accepted.

Risks and invariants:
- A separate backing file is opened per FUSE file to preserve the FUSE path context.
- Write paths deliberately serialize with `inode_lock()`.
- `fuse_passthrough_release()` expects `ff->passthrough` and `ff->cred` to be initialized.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/passthrough.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/readdir.c -->
# File Research: sources/os/linux/linux/fs/fuse/readdir.c

Implements FUSE directory iteration, readdirplus dentry/inode population, and optional directory entry caching for `FOPEN_CACHE_DIR`.

Key entry points:
- `fuse_readdir()` chooses cached or uncached readdir.
- `fuse_readdir_uncached()` sends `FUSE_READDIR` or `FUSE_READDIRPLUS`.
- `fuse_readdir_cached()` reads from the per-inode readdir cache.
- `parse_dirfile()` and `parse_dirplusfile()` validate and emit server-returned entries.

Important control flow:
- `fuse_use_readdirplus()` honors `do_readdirplus`, `readdirplus_auto`, position zero, and advisory state bits.
- `fuse_add_dirent_to_cache()` appends dirents into page-cache-backed directory cache only if the position matches the cache tail.
- `fuse_readdir_cache_end()` marks cache complete when the server returns EOF.
- Readdirplus entries call `fuse_direntplus_link()` to instantiate or refresh dentries and inodes, update lookup counts, set entry timeouts, and handle stale inode replacement.
- If a readdirplus link fails after a nodeid lookup was gained, `fuse_force_forget()` sends a forced forget.

Dependencies and integration:
- Uses FUSE read request helpers, dcache APIs, page cache APIs, ACL cache invalidation, inode attr versioning, and FUSE lookup/nlookup accounting.

Risks and invariants:
- Dirents with zero names, names larger than `FUSE_NAME_MAX`, slash-containing names, or malformed record lengths cause `-EIO`.
- Cache validity depends on readdir cache version, size, position, directory mtime, and inode i_version.
- Cached iteration resets stream state after seeks or cache version changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/sysctl.c -->
# File Research: sources/os/linux/linux/fs/fuse/sysctl.c

Registers `/proc/sys/fs/fuse` tunables for global FUSE request sizing and timeout limits.

Key entry points:
- `fuse_sysctl_register()`
- `fuse_sysctl_unregister()`

Tunables:
- `max_pages_limit` maps to `fuse_max_pages_limit`, min 1, max 65535.
- `default_request_timeout` maps to `fuse_default_req_timeout`, min 0, max 65535.
- `max_request_timeout` maps to `fuse_max_req_timeout`, min 0, max 65535.

Dependencies and integration:
- Uses `register_sysctl()` with `proc_douintvec_minmax`.
- Bounds match `fuse_init_out` protocol fields that are `u16`.

Risks and invariants:
- Register failure returns `-ENOMEM`.
- Unregister clears the global table header after `unregister_sysctl_table()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/trace.c -->
# File Research: sources/os/linux/linux/fs/fuse/trace.c

Defines FUSE tracepoint storage for the tracepoint declarations in `fuse_trace.h`.

Key behavior:
- Includes `dev_uring_i.h`, `fuse_i.h`, `fuse_dev_i.h`, and `<linux/pagemap.h>`.
- Defines `CREATE_TRACE_POINTS` before including `fuse_trace.h`, causing the tracepoint definitions to be emitted in this translation unit.

Dependencies and integration:
- Pure trace infrastructure file; no runtime functions are declared here.
- Integrates FUSE core and io_uring/dev trace events into the kernel tracing subsystem.

Risks and invariants:
- Must remain the single translation unit defining `CREATE_TRACE_POINTS` for FUSE tracepoints to avoid duplicate definitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/virtio_fs.c -->
# File Research: sources/os/linux/linux/fs/fuse/virtio_fs.c

Implements the virtio-fs kernel driver and filesystem type, connecting FUSE request queues to virtio virtqueues, exposing device sysfs state, supporting optional DAX, and mounting by virtiofs tag.

Major structures:
- `struct virtio_fs`: one virtio-fs device instance, including tag, virtqueues, CPU queue map, optional DAX window, and sysfs kobjects.
- `struct virtio_fs_vq`: per-virtqueue state with lock, virtqueue pointer, pending/end queues, work items, `fuse_dev`, connected state, and in-flight accounting.
- `struct virtio_fs_forget`: high-priority `FUSE_FORGET` request wrapper.

Key areas:
- Mount parameter parsing supports `dax`, `dax=always`, `dax=never`, and `dax=inode`.
- Sysfs exposes `/sys/fs/virtiofs/<id>/tag` and queue attributes under `mqs`.
- Probe reads the virtio tag, sets up virtqueues, maps request queues to CPUs, sets up DAX if available, marks device ready, and registers the instance.
- Remove stops queues, drains work, resets device, deletes sysfs, and drops references.

Request flow:
- `virtio_fs_send_req()` assigns FUSE unique IDs, selects a request queue using `mq_map[raw_smp_processor_id()]`, and calls `virtio_fs_enqueue_req()`.
- `virtio_fs_enqueue_req()` builds scatterlists for FUSE headers, argument bounce buffer, and page folios, queues them with `virtqueue_add_sgs()`, links the request into the FUSE processing hash, sets `FR_SENT`, and kicks the device.
- Completion interrupts schedule work; `virtio_fs_requests_done_work()` collects completed buffers, verifies response length/unique, and ends requests directly or via worker if `may_block`.
- Queue-full requests are placed on `queued_reqs` and retried from dispatch work.
- `FUSE_FORGET` uses the hiprio virtqueue through `virtio_fs_send_forget()` and `send_forget_request()`.

DAX:
- `virtio_fs_setup_dax()` allocates a DAX device, discovers the virtio shared memory cache region, reserves/remaps it with `devm_memremap_pages()`, and records physical/kaddr window state.
- DAX ops implement direct access and zero-page-range over the shared cache window.

Mount/superblock lifecycle:
- `virtio_fs_get_tree()` finds the tag instance, creates FUSE connection/mount objects, caps `fc->max_pages_limit` to virtqueue size minus protocol overhead, and uses `sget_fc()`.
- `virtio_fs_fill_super()` allocates one `fuse_dev` per virtqueue, validates DAX mode, calls `fuse_fill_super_common()`, installs devices, starts queues, and sends FUSE init.
- `virtio_fs_conn_destroy()` cancels DAX work, stops forget/all queues, drains, destroys the FUSE connection, and frees fuse devices.
- `virtio_kill_sb()` handles superblock teardown.

Dependencies and integration:
- Integrates virtio core, FUSE core, sysfs/kobject, DAX, fs_context, iomap-style page folio request plumbing, and workqueues.
- Registers `virtio_driver` for `VIRTIO_ID_FS` and `file_system_type` named `virtiofs`.

Risks and invariants:
- `virtio_fs_mutex` protects instance list and remove/mount teardown races.
- In-flight counters and completions ensure removal/unmount waits for queued/completing requests.
- Response verification catches short, mismatched-length, and mismatched-unique replies.
- Suspend/freeze is explicitly unsupported and returns `-EOPNOTSUPP`.
- Interrupt requests are TODO; blocking lock interruption is not implemented.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/virtio_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/xattr.c -->
# File Research: sources/os/linux/linux/fs/fuse/xattr.c

Implements FUSE extended attribute operations and registers the VFS xattr handler.

Key entry points:
- `fuse_setxattr()`
- `fuse_getxattr()`
- `fuse_listxattr()`
- `fuse_removexattr()`
- `fuse_xattr_handlers[]`

Important control flow:
- Set/get/list/remove each sends the corresponding FUSE opcode and marks the connection operation unsupported after `-ENOSYS`, translating to `-EOPNOTSUPP`.
- `fuse_setxattr()` uses extended setxattr input size only when `fc->setxattr_ext` is enabled.
- `fuse_getxattr()` and `fuse_listxattr()` use the common “size query when size is zero, data transfer when size is nonzero” pattern.
- `fuse_verify_xattr_list()` validates returned xattr list entries are nonempty NUL-terminated strings.

Dependencies and integration:
- Uses FUSE protocol args plus Linux xattr and POSIX ACL xattr headers.
- VFS handler has empty prefix, allowing all namespaces to be forwarded to userspace.

Risks and invariants:
- Bad inodes return `-EIO`; list also enforces `fuse_allow_current_process()`.
- Size query results are capped to `XATTR_SIZE_MAX` or `XATTR_LIST_MAX`.
- Successful set/remove updates ctime.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/Kconfig -->
# File Research: sources/os/linux/linux/fs/gfs2/Kconfig

Defines Kconfig entries for GFS2 filesystem support and optional DLM cluster locking.

Key configuration:
- `GFS2_FS` is a tristate filesystem option selecting `BUFFER_HEAD`, `FS_POSIX_ACL`, `CRC32`, `QUOTACTL`, and `FS_IOMAP`.
- `GFS2_FS_LOCKING_DLM` enables DLM locking and depends on GFS2, networking, configfs, sysfs, and DLM availability.

Purpose:
- Describes GFS2 as a shared-block cluster filesystem with immediate cross-node consistency through a lock module.
- Notes `nolock` is built in by default and DLM is needed for cluster environments.

Integration:
- Drives compilation of `fs/gfs2` objects and optional `lock_dlm.o` through the Makefile.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/Makefile -->
# File Research: sources/os/linux/linux/fs/gfs2/Makefile

Builds the GFS2 kernel module/object from its component source files.

Key behavior:
- Adds `-I$(src)` to compilation flags.
- Builds `gfs2.o` when `CONFIG_GFS2_FS` is enabled.
- Core objects include ACL, bmap, dir, xattr, glock/glops, log/lops, metadata I/O, inode, quota, recovery, resource groups, superblock, transactions, util, file, export, dentry, and mount logic.
- Adds `lock_dlm.o` when `CONFIG_GFS2_FS_LOCKING_DLM` is enabled.

Integration:
- Mirrors the Kconfig split between core filesystem and DLM cluster locking.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/acl.c -->
# File Research: sources/os/linux/linux/fs/gfs2/acl.c

Implements POSIX ACL get/set operations for GFS2 through system extended attributes.

Key entry points:
- `gfs2_get_acl()`
- `__gfs2_set_acl()`
- `gfs2_set_acl()`

Important control flow:
- `gfs2_acl_name()` maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`.
- ACL get returns `-ECHILD` under RCU lookup, acquires the inode glock in shared mode if needed, reads ACL xattr data, and converts it with `posix_acl_from_xattr()`.
- ACL set checks max ACL entries, gets quota accounting, acquires exclusive glock if needed, updates inode mode for access ACLs, stores/deletes xattr data, updates cached ACL, and marks inode dirty if mode changed.

Dependencies and integration:
- Uses GFS2 glocks, xattr helpers, quota accounting, transactions indirectly through xattr set, and Linux POSIX ACL helpers.

Risks and invariants:
- Max ACL entries are bounded by filesystem block size via `GFS2_ACL_MAX_ENTRIES`.
- `__gfs2_get_acl()` treats `gfs2_xattr_acl_get()` length <= 0 as an error pointer, so absence/error handling is delegated to xattr helper behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/acl.h -->
# File Research: sources/os/linux/linux/fs/gfs2/acl.h

Declares GFS2 POSIX ACL interfaces and the ACL entry limit macro.

Exports:
- `GFS2_ACL_MAX_ENTRIES(sdp)` computes the maximum ACL entries from block size.
- `gfs2_get_acl()`
- `__gfs2_set_acl()`
- `gfs2_set_acl()`

Integration:
- Included by ACL implementation and inode/xattr code paths that need ACL operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/aops.c -->
# File Research: sources/os/linux/linux/fs/gfs2/aops.c

Implements GFS2 address-space operations for normal and journaled-data files, including read, writeback, readahead, bmap, dirtying, invalidation, and folio release.

Key entry points:
- `gfs2_jdata_writeback()`
- `gfs2_internal_read()`
- `adjust_fs_space()`
- `gfs2_release_folio()`
- `gfs2_set_aops()`

Important control flow:
- Normal writeback uses `iomap_writepages()` with `gfs2_writeback_ops`; if no pages were written, it forces AIL flush to avoid dirty throttling loops.
- Journaled-data writeback uses custom batching so GFS2 can begin transactions before locking folios.
- `gfs2_read_folio()` chooses iomap read for non-jdata, stuffed read for inline data, or `mpage_read_folio()` for journaled data with buffers.
- `stuffed_read_folio()` reads inline file data from the dinode and zero-fills the folio tail.
- `adjust_fs_space()` updates statfs accounting after filesystem grow by comparing rindex total space with master/local statfs state.
- `gfs2_invalidate_folio()` and `gfs2_release_folio()` handle buffer-head/journal metadata cleanup for jdata mappings.

Dependencies and integration:
- Uses iomap, mpage, buffer heads, GFS2 transactions, log/AIl, quota/statfs, glocks, and bmap mapping.
- `gfs2_set_aops()` selects `gfs2_jdata_aops` for journaled-data inodes and `gfs2_aops` otherwise.

Risks and invariants:
- Journaled writeback asserts the inode glock is exclusive.
- Jdata dirtying marks folios checked when inside a transaction.
- Release refuses folios with active buffer refs, transaction-owned bufdata, dirty buffers, or pinned buffers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/aops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/aops.h -->
# File Research: sources/os/linux/linux/fs/gfs2/aops.h

Declares GFS2 address-space helper functions shared outside `aops.c`.

Exports:
- `adjust_fs_space(struct inode *inode)`
- `gfs2_jdata_writeback(struct address_space *mapping, struct writeback_control *wbc)`

Integration:
- Used by resource-index grow/statfs paths and journaled-data writeback callers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/aops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/bmap.c -->
# File Research: sources/os/linux/linux/fs/gfs2/bmap.c

Implements GFS2 block mapping, iomap integration, allocation, stuffed-file unstuffing, truncation, hole punching, journal extent mapping, and writeback extent lookup.

Major concepts:
- `struct metapath` represents a path through dinode and indirect metadata blocks.
- Stuffed inodes store data inline in the dinode; large writes/grows unstuff them into normal blocks.
- GFS2 maps data through a height-based indirect tree and uses iomap for buffered/direct I/O.

Key entry points:
- `gfs2_unstuff_dinode()`
- `gfs2_iomap_get()` / `gfs2_iomap_alloc()`
- `gfs2_block_map()`
- `gfs2_get_extent()` / `gfs2_alloc_extent()`
- `gfs2_setattr_size()`
- `gfs2_truncatei_resume()` / `gfs2_file_dealloc()`
- `gfs2_map_journal_extents()` / `gfs2_free_journal_extents()`
- `gfs2_write_alloc_required()`
- `__gfs2_punch_hole()`
- `gfs2_iomap_ops`, `gfs2_iomap_write_ops`, `gfs2_writeback_ops`

Important control flow:
- Mapping starts with `__gfs2_iomap_get()`, which handles inline data, holes, mapped extents, metadata height growth needs, and `IOMAP_REPORT`.
- Allocation uses `gfs2_iomap_begin_write()` to reserve quota/resource groups, start a transaction, unstuff if needed, and call `__gfs2_iomap_alloc()`.
- `__gfs2_iomap_alloc()` is a state machine for growing tree height, growing depth, and allocating contiguous data blocks.
- `gfs2_iomap_end()` releases reservations/quota, adjusts grow statfs for rindex writes, marks ordered inodes, and punches unwritten tail blocks if short writes left new allocations unused.
- Truncation uses `trunc_start()`, `punch_hole()`, and `trunc_end()` with `GFS2_DIF_TRUNC_IN_PROG` for crash recovery.
- `punch_hole()` walks metadata bottom-up/right-to-left, frees blocks per resource group, rewrites the dinode at transaction boundaries, and updates statfs/quota.
- Journal mapping caches logical-to-physical journal extents for efficient log I/O.

Dependencies and integration:
- Heavy integration with GFS2 glocks, metadata I/O, resource groups, quota, transactions, log, iomap, buffer heads, tracepoints, and directory unstuff support.
- `gfs2_block_map()` bridges legacy buffer-head users to iomap.

Risks and invariants:
- `gfs2_block_zero_range()` must not be called with an open transaction because iomap write paths begin their own transactions.
- Deallocation splits work by resource group and transaction thresholds to preserve consistency and concurrency.
- Short writes to newly allocated extents are cleaned up by pagecache truncation plus hole punch.
- Many corruption checks withdraw/mark consistency errors if metadata shape, block pointers, or metatypes are invalid.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/bmap.h -->
# File Research: sources/os/linux/linux/fs/gfs2/bmap.h

Declares GFS2 block mapping, iomap, allocation, truncation, journal extent, and hole-punch interfaces.

Key exports:
- `gfs2_write_calc_reserv()` estimates data and indirect blocks needed for a write.
- `gfs2_iomap_ops`, `gfs2_iomap_write_ops`, `gfs2_writeback_ops`
- `gfs2_unstuff_dinode()`, `gfs2_block_map()`, `gfs2_iomap_get()`, `gfs2_iomap_alloc()`
- `gfs2_get_extent()`, `gfs2_alloc_extent()`
- `gfs2_setattr_size()`, `gfs2_truncatei_resume()`, `gfs2_file_dealloc()`
- `gfs2_map_journal_extents()`, `gfs2_free_journal_extents()`
- `gfs2_write_alloc_required()`
- `__gfs2_punch_hole()`

Integration:
- Shared by address-space, file, directory, inode, journal, and recovery paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/bmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/dentry.c -->
# File Research: sources/os/linux/linux/fs/gfs2/dentry.c

Defines GFS2 dentry operations for clustered lookup validation, filesystem-specific hashing, and deletion decisions.

Key entry points:
- `gfs2_drevalidate()`
- `gfs2_dhash()`
- `gfs2_dentry_delete()`
- `gfs2_dops`

Important control flow:
- Revalidation rejects RCU mode with `-ECHILD`.
- For cluster-locking mounts, it acquires the parent directory glock in shared mode unless already held and checks the name/inode pair with `gfs2_dir_check()`.
- Negative dentries are valid only if the name still returns `-ENOENT`.
- Hashing uses GFS2’s on-disk CRC32-based directory hash.
- Dentry deletion returns true when the inode’s iopen glock is being demoted.

Dependencies and integration:
- Uses GFS2 glocks, directory lookup validation, inode state, and VFS dentry operations.

Risks and invariants:
- In nolock/local mode, dentries are considered valid without distributed lookup recheck.
- Bad inodes invalidate dentries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/dentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/dir.c -->
# File Research: sources/os/linux/linux/fs/gfs2/dir.c

Implements GFS2 directory storage, lookup, insertion, deletion, readdir, extendible hashing, hash-table caching, leaf splitting/chaining, and exhash deallocation.

Major concepts:
- Linear/stuffed directories store dirents inside the dinode.
- Exhash directories store a directory file containing 64-bit leaf block pointers; leaf blocks contain dirents.
- Hash table entries can point to the same leaf; leaf depth controls how many hash slots reference a leaf.
- At maximum depth, full leaves chain via `lf_next`.

Key entry points:
- `gfs2_dir_get_new_buffer()`
- `gfs2_dir_hash_inval()`
- `gfs2_dir_read()`
- `gfs2_dir_search()`
- `gfs2_dir_check()`
- `gfs2_dir_add()`
- `gfs2_dir_del()`
- `gfs2_dir_mvino()`
- `gfs2_dir_exhash_dealloc()`
- `gfs2_diradd_alloc_required()`

Important control flow:
- Directory data I/O uses `gfs2_dir_write_data()` / `gfs2_dir_read_data()`; stuffed directories use dinode payload, exhash hash tables use journaled directory data blocks.
- `gfs2_dir_get_hash_table()` lazily reads and caches the exhash table, validating that file size matches `2^i_depth * sizeof(__be64)`.
- `gfs2_dirent_scan()` validates record lengths, alignment, block bounds, sentinel rules, and then applies scan callbacks for find, previous, last, space, offset, and gather operations.
- `gfs2_dir_search()` finds a dirent and returns the target inode through `gfs2_inode_lookup()`.
- `gfs2_dir_add()` first uses saved allocation search state if available; otherwise it finds free dirent space, converts linear directories to exhash, splits leaves, doubles hash table depth, or appends chained leaves.
- `dir_make_exhash()` converts stuffed directory contents into a leaf and replaces dinode payload with the initial hash pointer table.
- `dir_split_leaf()` allocates a new leaf, rewrites half the hash pointers, and redistributes entries based on hash divider.
- `dir_double_exhash()` doubles the hash table by duplicating each pointer and increments directory depth.
- `gfs2_dir_read()` gathers dirents, computes stable cookies, sorts hash collisions, and emits entries through `dir_emit()`.
- `gfs2_dir_exhash_dealloc()` walks hash slots and frees leaf chains via `leaf_dealloc()`.

Dependencies and integration:
- Uses bmap allocation/extent helpers, metadata I/O, transactions, resource groups, quota, glocks, VFS dir_context, and GFS2 on-disk directory/leaf formats.

Risks and invariants:
- Corrupt dirent counts, bad record lengths, wrong metatypes, invalid hash-table size, zero inode sentinels in non-first entries, and impossible split geometry trigger consistency errors or `-EIO`.
- Hash cache must be invalidated before hash-table rewrites.
- `gfs2_diradd_alloc_required()` can save a buffer/dirent for later insertion; callers must release through `gfs2_dir_no_add()` if not used.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/dir.h -->
# File Research: sources/os/linux/linux/fs/gfs2/dir.h

Declares GFS2 directory APIs, directory-add state, hash helpers, and dirent initialization helpers.

Key exports:
- `struct gfs2_diradd` holds allocation/search state for adding entries.
- `gfs2_dir_search()`, `gfs2_dir_check()`, `gfs2_dir_add()`, `gfs2_dir_del()`, `gfs2_dir_read()`, `gfs2_dir_mvino()`
- `gfs2_dir_exhash_dealloc()`
- `gfs2_diradd_alloc_required()`
- `gfs2_dir_get_new_buffer()`
- `gfs2_dir_hash_inval()`
- `gfs2_qdot`, `gfs2_qdotdot`

Inline helpers:
- `gfs2_disk_hash()` computes the on-disk CRC32 directory hash.
- `gfs2_str2qstr()` builds a hashed qstr from a string.
- `gfs2_qstr2dirent()` initializes an on-disk dirent skeleton from a qstr and record length.

Integration:
- Used by inode, dentry, export, bmap, and directory implementation paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/export.c -->
# File Research: sources/os/linux/linux/fs/gfs2/export.c

Implements GFS2 export operations for NFS file handles, parent lookup, and reverse name lookup.

Key entry points:
- `gfs2_encode_fh()`
- `gfs2_fh_to_dentry()`
- `gfs2_fh_to_parent()`
- `gfs2_get_name()`
- `gfs2_get_parent()`
- `gfs2_export_ops`

Important control flow:
- File handles encode formal inode number and disk address; parent handles append the same pair for the parent.
- Supports small, large, and old handle sizes.
- `gfs2_get_dentry()` rejects zero formal inode numbers as stale and looks up inodes by inum.
- `gfs2_get_name()` scans the parent directory under shared glock with a filldir actor that matches child block address and copies the name.
- `gfs2_get_parent()` resolves `..` through `gfs2_lookupi()`.

Dependencies and integration:
- Uses exportfs, GFS2 directory reading, inode lookup by inum, glocks, and dentry alias helpers.

Risks and invariants:
- Insufficient file handle buffers return `FILEID_INVALID` after updating the required length.
- Missing reverse name during export lookup returns `-ENOENT`.
- File handles rely on both formal inode number and disk address to detect stale references.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/export.c -->