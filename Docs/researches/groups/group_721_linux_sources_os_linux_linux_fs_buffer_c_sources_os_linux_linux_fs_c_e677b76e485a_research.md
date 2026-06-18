# Group Research: group_721_linux_sources_os_linux_linux_fs_buffer_c_sources_os_linux_linux_fs_c_e677b76e485a

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/buffer.c -->
# File Research: sources/os/linux/linux/fs/buffer.c

## Purpose
Implements Linux buffer-head support for block-device buffer cache lookup, buffer-backed folio read/write paths, dirty/writeback state coordination, metadata-buffer fsync lists, buffer LRU caching, direct buffer I/O submission, invalidation, truncation helpers, and buffer-head allocation/accounting.

## Main Elements
- Basic buffer operations: `touch_buffer()`, `__lock_buffer()`, `unlock_buffer()`, `__wait_on_buffer()`, `bio_endio_bh()`, `end_buffer_read_sync()`, `bh_end_read()`, and `bh_end_write()`.
- Async folio I/O completion: `end_buffer_async_read()`, `bh_end_async_read()`, and `bh_end_async_write()` coordinate per-buffer completion with folio uptodate/writeback state; read completion can enqueue fscrypt decryption and fsverity verification work.
- Metadata buffer lists: `mmb_init()`, `mmb_mark_buffer_dirty()`, `mmb_sync()`, `mmb_fsync_noflush()`, `mmb_fsync()`, and `mmb_invalidate()` maintain per-mapping dependent metadata buffers for simple filesystems and fsync ordering.
- Block-device buffer cache lookup: `__find_get_block_slow()`, per-CPU `bh_lru`, `__find_get_block()`, `__find_get_block_nonatomic()`, `bdev_getblk()`, `__bread_gfp()`, and `__breadahead()`.
- Buffer creation and initialization: `folio_alloc_buffers()`, `alloc_page_buffers()`, `create_empty_buffers()`, `folio_set_bh()`, `grow_buffers()`, and block-device folio buffer initialization.
- Dirty and error propagation: `block_dirty_folio()`, `mark_buffer_dirty()`, `mark_buffer_write_io_error()`, `write_dirty_buffer()`, `__sync_dirty_buffer()`, and `sync_dirty_buffer()`.
- Buffer-backed write path: `__block_write_full_folio()`, `folio_zero_new_buffers()`, `__block_write_begin_int()`, `block_write_begin()`, `block_write_end()`, `generic_write_end()`, and `block_write_full_folio()`.
- Buffer-backed read and mapping helpers: `block_read_full_folio()`, `block_is_partially_uptodate()`, `generic_block_bmap()`, and `iomap_to_bh()`.
- Truncation and invalidation: `block_invalidate_folio()`, `clean_bdev_aliases()`, `block_truncate_page()`, `try_to_free_buffers()`, and `discard_buffer()`.
- mmap/extension helpers: `generic_cont_expand_simple()`, `cont_write_begin()`, and `block_page_mkwrite()`.
- Allocation/accounting: `alloc_buffer_head()`, `free_buffer_head()`, CPU hotplug cleanup, `buffer_heads_over_limit`, `buffer_init()`, and buffer read batching helpers.

## Dependencies And Integration
This is a core VFS/block-layer bridge used by buffer-head filesystems, block devices, FS-Cache-adjacent netfs code, and legacy metadata paths. It integrates with folios and address spaces, writeback control, bios and blk-crypto, fscrypt, fsverity, cgroup writeback accounting, block-device mappings, per-CPU CPU hotplug state, and filesystem `get_block_t` callbacks.

## Risk Notes
Correctness depends on careful synchronization between folio locks, `i_private_lock`, buffer lock bits, folio dirty/writeback flags, and per-buffer state. Partial-block writes, truncate races, device-size races, blockdev alias invalidation, and fscrypt/fsverity completion failure paths are high-risk. Buffer LRU references can interfere with migration, so isolated CPUs and disabled LRU states are explicitly handled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/buffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/Kconfig -->
# File Research: sources/os/linux/linux/fs/cachefiles/Kconfig

## Purpose
Defines build-time configuration for CacheFiles, the FS-Cache backend that uses a mounted local filesystem as persistent cache storage.

## Main Elements
- `CACHEFILES`: tristate option depending on `NETFS_SUPPORT`, `FSCACHE`, and `BLOCK`.
- `CACHEFILES_DEBUG`: optional dynamic debug mask support through the module parameter.
- `CACHEFILES_ERROR_INJECTION`: optional sysctl-controlled fault injection support.
- `CACHEFILES_ONDEMAND`: optional on-demand read mode where userspace supplies cache-miss data through the CacheFiles daemon interface.

## Dependencies And Integration
Connects CacheFiles to the kernel netfs/FS-Cache infrastructure and block-backed filesystems. The help text points to `Documentation/filesystems/caching/cachefiles.rst`.

## Risk Notes
On-demand mode changes the data-fetching responsibility from the netfs to userspace and is disabled by default. Error injection requires `SYSCTL` and is intended for testing active caches.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/Makefile -->
# File Research: sources/os/linux/linux/fs/cachefiles/Makefile

## Purpose
Builds the CacheFiles module object list.

## Main Elements
- Core objects: `cache.o`, `daemon.o`, `interface.o`, `io.o`, `key.o`, `main.o`, `namei.o`, `security.o`, `volume.o`, and `xattr.o`.
- Optional objects: `error_inject.o` under `CONFIG_CACHEFILES_ERROR_INJECTION` and `ondemand.o` under `CONFIG_CACHEFILES_ONDEMAND`.
- Module target: `obj-$(CONFIG_CACHEFILES) := cachefiles.o`.

## Dependencies And Integration
Mirrors the Kconfig features and links CacheFiles into the kernel build as one composite module.

## Risk Notes
Feature-gated source files must stay aligned with prototypes and stubs in `internal.h`, especially on-demand and error-injection paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/cache.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/cache.c

## Purpose
Manages high-level cache lifecycle: binding a cache root, validating the backing filesystem, registering with FS-Cache, computing space thresholds, checking available space, withdrawing objects/volumes, and syncing the backing filesystem on shutdown.

## Main Elements
- `cachefiles_add_cache()`: acquires an FS-Cache cache cookie, prepares security credentials, opens the configured cache root, rejects idmapped/read-only/unsupported filesystems, computes block/file thresholds, creates or pins `cache` and `graveyard` directories, and registers `cachefiles_cache_ops`.
- `cachefiles_has_space()`: runs `statfs`, accounts pending writes, checks file and block thresholds, records FS-Cache no-space counters, and toggles culling state.
- `cachefiles_withdraw_objects()`: removes active objects from the cache list and withdraws their FS-Cache cookies.
- `cachefiles_withdraw_fscache_volumes()` and `cachefiles_withdraw_volumes()`: coordinate FS-Cache volume withdrawal and CacheFiles volume cleanup.
- `cachefiles_sync_cache()`: syncs the backing superblock under CacheFiles credentials and marks the cache dead on serious I/O errors.
- `cachefiles_withdraw_cache()`: top-level cache unregister path.

## Dependencies And Integration
Uses VFS path lookup, `statfs`, mount and superblock operations, CacheFiles security overrides, CacheFiles directory helpers from `namei.c`, volume/object lists, and FS-Cache registration and withdrawal APIs.

## Risk Notes
Backing filesystem capability checks are central: CacheFiles needs lookup, mkdir, tmpfile, xattrs, statfs, sync, and page-sized-or-smaller blocks. Space threshold arithmetic is based on current `statfs` values, and errors such as `-EIO` transition the cache to a dead state. Withdrawal must coordinate object list removal with FS-Cache access counts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/daemon.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/daemon.c

## Purpose
Implements the `/dev/cachefiles` misc-device control interface used by `cachefilesd` to configure, bind, monitor, cull, and unbind a CacheFiles cache.

## Main Elements
- File operations: `cachefiles_daemon_open()`, `cachefiles_daemon_release()`, `cachefiles_daemon_read()`, `cachefiles_daemon_write()`, and `cachefiles_daemon_poll()`.
- Open path: requires `CAP_SYS_ADMIN`, enforces single open with `cachefiles_open`, allocates `struct cachefiles_cache`, initializes lists, locks, xarrays, waitqueue, and default culling thresholds.
- Command dispatch: parses newline-terminated user commands and invokes handlers from `cachefiles_daemon_cmds`.
- Threshold commands: `frun`, `fcull`, `fstop`, `brun`, `bcull`, and `bstop` parse percentage limits and enforce `stop < cull < run < 100`.
- Configuration commands: `dir`, `secctx`, `tag`, `debug`, and `bind`.
- Runtime commands: `cull` and `inuse` act on the caller's current working directory.
- On-demand commands: `copen` and `restore` are included when `CONFIG_CACHEFILES_ONDEMAND` is enabled.
- Unbind/refcount path: `cachefiles_get_unbind_pincount()`, `cachefiles_put_unbind_pincount()`, `cachefiles_flush_reqs()`, and `cachefiles_daemon_unbind()`.

## Dependencies And Integration
Bridges userspace cache manager commands to `cache.c`, `namei.c`, `security.c`, and `ondemand.c`. Uses miscdevice registration from `main.c`, xarrays for on-demand requests, daemon poll wakeups, and CacheFiles credential overrides for VFS operations.

## Risk Notes
The daemon lifetime is guarded by `CACHEFILES_DEAD`, `unbind_pincount`, and request xarray flushing. Memory barriers in `cachefiles_flush_reqs()` pair with on-demand request enqueueing to avoid orphaned requests. Command parsing rejects embedded NULs and overly large writes, but each command handler still depends on strict daemon-side sequencing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/daemon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/error_inject.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/error_inject.c

## Purpose
Registers a sysctl used to inject CacheFiles read, write, allocation-space, and remove errors during testing.

## Main Elements
- Global state: `cachefiles_error_injection_state`.
- Sysctl table: `/proc/sys/cachefiles/error_injection`, mode `0644`, handled by `proc_douintvec`.
- `cachefiles_register_error_injection()`: registers the sysctl table.
- `cachefiles_unregister_error_injection()`: unregisters it.

## Dependencies And Integration
Enabled by `CONFIG_CACHEFILES_ERROR_INJECTION`. Inline helpers in `internal.h` interpret state bits and return synthetic `-EIO` or `-ENOSPC` to CacheFiles code paths.

## Risk Notes
This is intentionally disruptive and applies while a cache is in service. Production builds without the option compile the helpers to no-op stubs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/error_inject.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/interface.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/interface.c

## Purpose
Implements the FS-Cache cache-ops interface for CacheFiles objects: allocation, lookup, withdrawal, invalidation, resizing, object xattr commit, and object reference tracing.

## Main Elements
- Object lifetime: `cachefiles_alloc_object()`, `cachefiles_see_object()`, `cachefiles_grab_object()`, and `cachefiles_put_object()`.
- Size management: `cachefiles_adjust_size()` rounds object EOF to the CacheFiles DIO block size and truncates or expands backing files.
- Lookup path: `cachefiles_lookup_cookie()` cooks a key, creates a CacheFiles object, looks up or creates the backing file, adds it to the active object list, and adjusts size.
- Resize path: `cachefiles_resize_cookie()` shrinks backing files with `cachefiles_shorten_object()` or updates cookie size on expansion.
- Cleanup path: `cachefiles_commit_object()`, `cachefiles_clean_up_object()`, and `cachefiles_withdraw_cookie()` commit xattrs, link tmpfiles, delete retired objects, unmark inodes, close files, and drop references.
- Invalidation: `cachefiles_invalidate_cookie()` replaces an object file with a tmpfile, resumes FS-Cache invalidation, and buries the old object.
- `cachefiles_cache_ops`: exports CacheFiles callbacks to FS-Cache.

## Dependencies And Integration
Integrates FS-Cache cookies and volumes with CacheFiles object records, VFS files, xattrs, tmpfiles, name lookup, on-demand object state, and netfs cache-resource operations implemented in `io.c`.

## Risk Notes
Invalidation and withdrawal swap file pointers under `object->lock` while I/O may be active. Tmpfile commit and xattr update determine whether cache content is durable and coherent. Size rounding prevents partial DIO fallback but requires careful truncation/zeroing to avoid stale data exposure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/interface.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/internal.h -->
# File Research: sources/os/linux/linux/fs/cachefiles/internal.h

## Purpose
Defines CacheFiles internal data structures, state flags, inline helpers, feature stubs, prototypes, error handling macros, and debug/assertion infrastructure shared across the module.

## Main Elements
- Core constants and enums: `CACHEFILES_DIO_BLOCK_SIZE`, `enum cachefiles_content`, and on-demand object states.
- Data structures: `cachefiles_volume`, `cachefiles_ondemand_info`, `cachefiles_object`, `cachefiles_cache`, and `cachefiles_req`.
- State flags: object tmpfile state, cache readiness/death/culling/state-change/on-demand mode, request marks, and closed on-demand IDs.
- Cache-resource helpers: `cachefiles_cres_file()` and `cachefiles_cres_object()`.
- Daemon notification: `cachefiles_state_changed()`.
- Prototypes for cache, daemon, interface, I/O, key, namei, ondemand, security, volume, and xattr files.
- Error-injection stubs and helpers: `cachefiles_inject_read_error()`, `cachefiles_inject_write_error()`, and `cachefiles_inject_remove_error()`.
- On-demand compile-time stubs when `CONFIG_CACHEFILES_ONDEMAND` is disabled.
- Credential override helpers: `cachefiles_begin_secure()` and `cachefiles_end_secure()`.
- Error macros: `cachefiles_io_error()` and `cachefiles_io_error_obj()`.
- Debug and assertion macros.

## Dependencies And Integration
This header is the module's internal contract and directly ties CacheFiles to FS-Cache, xarrays, credentials/security, tracepoints, and the user ABI in `<linux/cachefiles.h>`.

## Risk Notes
The macros can mark a cache dead and flush on-demand requests from many call sites, so error paths have broad side effects. On-demand stubs must preserve behavior when the feature is disabled. Assertion macros call `BUG()` in active builds, making invariant failures fatal.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/io.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/io.c

## Purpose
Implements CacheFiles netfs cache I/O operations using direct `kiocb` reads and writes against backing files, including read-source selection, sparse-file occupancy queries, write preparation, async completion, and netfs cache-ops registration.

## Main Elements
- I/O request wrapper: `struct cachefiles_kiocb` tracks the backing `kiocb`, object reference, completion callback, invalidation counter, skipped bytes, and pending write block accounting.
- Read path: `cachefiles_read()` optionally seeks to data, zero-fills holes, submits `vfs_iocb_iter_read()` with `IOCB_DIRECT`, and completes through `cachefiles_read_complete()`.
- Occupancy: `cachefiles_query_occupancy()` uses `SEEK_DATA` and `SEEK_HOLE`, rounded to cache granularity, to report cached extents.
- Write path: `__cachefiles_write()` submits direct writes, tracks `b_writing`, handles async completion in `cachefiles_write_complete()`, and sets `FSCACHE_COOKIE_HAVE_DATA`.
- Read preparation: `cachefiles_do_prepare_read()` chooses between cache read, server download, zero-fill, or invalid on-demand read by probing backing file holes and honoring cookie state.
- Write preparation: `__cachefiles_prepare_write()` enforces page/DIO alignment, checks free space, detects allocated extents, and punches partially allocated regions when space is insufficient.
- Netfs write integration: `cachefiles_prepare_write_subreq()` and `cachefiles_issue_write()` align write subrequests to `CACHEFILES_DIO_BLOCK_SIZE` before writing to cache.
- Operation lifetime: `cachefiles_begin_operation()` pins the object file in cache resources and `cachefiles_end_operation()` releases it.
- `cachefiles_netfs_cache_ops`: supplies CacheFiles read, write, issue-write, prepare-read, prepare-write, on-demand read preparation, occupancy, and cleanup callbacks.

## Dependencies And Integration
Connects CacheFiles objects to the netfs library through `netfs_cache_ops`. Uses VFS direct I/O iter operations, sparse-file seeks, fallocate hole punching, CacheFiles space accounting, on-demand request handling, FS-Cache cookie access waits, and tracepoints.

## Risk Notes
Alignment is strict because CacheFiles relies on DIO and avoids partial-cache-block writes. Read paths guard against invalidation races by comparing `inval_counter`. Seek errors and fallocate failures can mark the cache dead. Async `kiocb` lifetime depends on two references: submission and completion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/key.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/key.c

## Purpose
Encodes FS-Cache binary cookie keys into filesystem-safe CacheFiles object names.

## Main Elements
- `cachefiles_charmap`: 64-character alphabet for custom base64-like encoding.
- `cachefiles_filecharmap`: marks directly usable printable filename characters, excluding control characters, spaces, tabs, and `/`.
- `how_many_hex_digits()`: helper for compact integer encoding size estimates.
- `cachefiles_cook_key()`: chooses direct string encoding, 32-bit comma-separated hex encoding in the smaller endian representation, or base64-like encoding; stores the resulting name in `object->d_name`.

## Dependencies And Integration
Called during object lookup before traversing the backing cache directory. Uses FS-Cache cookie keys and Linux `NAME_MAX` constraints.

## Risk Notes
The code assumes keys fit within `NAME_MAX - 3` and that binary keys considered for 32-bit hex encoding are padded to a full word count. Filename safety is critical because names are passed directly into VFS lookup/create helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/key.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/main.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/main.c

## Purpose
Provides CacheFiles module initialization and teardown.

## Main Elements
- Module parameter: `cachefiles_debug`.
- Module metadata: description, author, and GPL license.
- Global object slab: `cachefiles_object_jar`.
- Misc device: dynamically allocated `/dev/cachefiles` with `cachefiles_daemon_fops`.
- `cachefiles_init()`: registers error injection, registers the misc device, creates the object slab, and logs load status.
- `cachefiles_exit()`: destroys the slab, deregisters the misc device, unregisters error injection, and logs unload status.

## Dependencies And Integration
Uses `fs_initcall()` so CacheFiles initializes during filesystem setup. Depends on daemon file operations and optional error-injection registration.

## Risk Notes
Initialization unwinds in reverse order on failure. The object slab must outlive all `cachefiles_object` instances, which are controlled by daemon/cache shutdown paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/namei.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/namei.c

## Purpose
Handles CacheFiles backing filesystem namespace operations: directory creation/pinning, inode in-use marking, file lookup/open/create, tmpfile commit, unlink/rename-to-graveyard deletion, daemon culling, and in-use checks.

## Main Elements
- In-use marking: `__cachefiles_mark_inode_in_use()`, `cachefiles_mark_inode_in_use()`, `__cachefiles_unmark_inode_in_use()`, and `cachefiles_unmark_inode_in_use()` use `S_KERNEL_FILE` to prevent culling/removal of active cache entries.
- Directory management: `cachefiles_get_directory()` looks up or creates cache directories, validates required inode operations, and pins them; `cachefiles_put_directory()` unmarks and releases them.
- Removal helpers: `cachefiles_unlink()`, `cachefiles_bury_object()`, and `cachefiles_delete_object()` unlink files or rename directories into the graveyard.
- Tmpfile handling: `cachefiles_create_tmpfile()` creates an unlinked direct-I/O backing file, marks it in use, initializes on-demand state, sizes it, and validates read/write iter ops.
- Object creation/open: `cachefiles_create_file()`, `cachefiles_open_file()`, and `cachefiles_look_up_object()` locate existing cache files, validate xattrs, replace stale files, or create tmpfiles.
- Tmpfile commit: `cachefiles_commit_tmpfile()` links an unlinked tmpfile into the fanout directory, replacing stale objects if needed.
- Daemon operations: `cachefiles_lookup_for_cull()`, `cachefiles_cull()`, and `cachefiles_check_in_use()`.

## Dependencies And Integration
Works under CacheFiles security overrides from callers. Integrates VFS helpers for create/remove/rename/link/tmpfile/open, LSM path checks, xattr coherency, on-demand initialization, CacheFiles volume fanout directories, and daemon culling commands.

## Risk Notes
Namespace races are handled through VFS `start_creating`, `start_removing`, and rename helpers plus `S_KERNEL_FILE`, but failures can leave objects stale or force cache shutdown on serious I/O/security errors. Directory objects are moved to a graveyard instead of directly removed. Active-file detection relies on inode flags shared with culling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/ondemand.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/ondemand.c

## Purpose
Implements CacheFiles on-demand mode, where userspace receives open/read/close requests through `/dev/cachefiles` and supplies data via anonymous per-object file descriptors.

## Main Elements
- Anonymous fd operations: `cachefiles_ondemand_fd_release()`, `cachefiles_ondemand_fd_write_iter()`, `cachefiles_ondemand_fd_llseek()`, and `cachefiles_ondemand_fd_ioctl()`.
- `copen` handling: `cachefiles_ondemand_copen()` completes an open request, records object size, updates cookie data-read flags, and transitions object state to open.
- Recovery: `cachefiles_ondemand_restore()` marks pending requests new again after daemon restart.
- Anonymous fd creation: `cachefiles_ondemand_get_fd()` allocates an object ID, fd, and anon inode file, installs fd payload data, and pins cache unbind.
- Request selection and daemon read: `cachefiles_ondemand_select_req()` skips reopening reads and queues reopen work; `cachefiles_ondemand_daemon_read()` returns the next request message to userspace.
- Request lifecycle: `cachefiles_ondemand_send_req()` allocates requests, atomically enqueues them in the cache xarray, wakes the daemon, waits killably, and handles completion races.
- Request payload builders: open, close, and read initializers.
- Object lifecycle: `cachefiles_ondemand_init_object()`, `cachefiles_ondemand_clean_object()`, `cachefiles_ondemand_init_obj_info()`, `cachefiles_ondemand_deinit_obj_info()`, and `cachefiles_ondemand_read()`.

## Dependencies And Integration
Enabled only with `CONFIG_CACHEFILES_ONDEMAND`. Integrates with the daemon command table, CacheFiles object state, request xarrays, anonymous inodes, CacheFiles direct write helpers, FS-Cache workqueue, and the user ABI in `<linux/cachefiles.h>`.

## Risk Notes
This file is concurrency-sensitive: request enqueueing is paired with daemon shutdown barriers, fd release can race `copen`, read requests can trigger object reopen work, and interrupted waits must either remove or wait for completion of a request. Anonymous fd lifetime pins both object and cache unbind state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/ondemand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/security.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/security.c

## Purpose
Builds and adjusts the credentials CacheFiles uses for kernel-side VFS access to the backing cache.

## Main Elements
- `cachefiles_get_security_ID()`: prepares kernel credentials from the current task and optionally applies the daemon-specified LSM security ID.
- `cachefiles_check_cache_dir()`: asks LSM hooks whether mkdir and create are permitted in the cache root.
- `cachefiles_determine_cache_security()`: derives create-file credentials from the backing cache root inode, replaces `cache->cache_cred`, restores the override, and validates directory permissions.

## Dependencies And Integration
Works with daemon `secctx` configuration, LSM credential APIs, and credential override helpers in `internal.h`. Called during cache binding before CacheFiles creates backing directories and files.

## Risk Notes
Credential replacement deliberately drops and reapplies override credentials while deriving file-creation security. Security hook failures prevent cache binding unless unsupported create-file-as behavior is treated as acceptable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/volume.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/volume.c

## Purpose
Creates, validates, pins, withdraws, and frees CacheFiles volume directories and their 256 fanout subdirectories.

## Main Elements
- `cachefiles_acquire_volume()`: allocates a volume object, creates or opens the volume directory from the FS-Cache volume key, sets or validates volume xattrs, creates and pins `@00` through `@ff` fanout directories, and links the volume into the cache list.
- `__cachefiles_free_volume()`: releases all fanout directories and the volume directory and clears `vcookie->cache_priv`.
- `cachefiles_free_volume()`: removes the volume from the cache list and frees it.
- `cachefiles_withdraw_volume()`: writes volume xattrs and frees the volume during cache withdrawal.

## Dependencies And Integration
Uses directory helpers from `namei.c`, xattr coherency from `xattr.c`, FS-Cache volume access counters, and CacheFiles cache object-list locking.

## Risk Notes
Existing volume directories with stale xattrs are buried and retried. Partial fanout creation failure must release all already pinned directories. The volume is pinned by an FS-Cache access count to suppress premature wakeups.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/xattr.c -->
# File Research: sources/os/linux/linux/fs/cachefiles/xattr.c

## Purpose
Stores and validates CacheFiles coherency metadata in backing filesystem extended attributes for cache objects and volumes.

## Main Elements
- Object xattr format: `struct cachefiles_xattr` stores object size, zero point, object type, content state, and netfs auxiliary coherency data.
- Volume xattr format: `struct cachefiles_vol_xattr` stores a reserved field and volume coherency data.
- `cachefiles_set_object_xattr()`: writes object coherency metadata and marks locally written cookies as dirty.
- `cachefiles_check_auxdata()`: reads object xattr and validates type, auxiliary data, object size, and dirty state.
- `cachefiles_remove_object_xattr()`: removes an object xattr to mark a backing file stale.
- `cachefiles_prepare_to_write()`: writes a dirty marker before local write unless the object is still a tmpfile.
- `cachefiles_set_volume_xattr()` and `cachefiles_check_volume_xattr()`: write and validate volume coherency metadata.

## Dependencies And Integration
Uses VFS xattr operations under mount write access and CacheFiles credential context supplied by callers. Provides coherency checks for `namei.c`, object commit in `interface.c`, and volume setup in `volume.c`.

## Risk Notes
Xattr mismatches return `-ESTALE` and force object or volume replacement. Dirty object detection is noted as a TODO for conflict resolution. Non-memory xattr write/remove failures can mark the whole cache dead.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/cachefiles/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/Kconfig -->
# File Research: sources/os/linux/linux/fs/ceph/Kconfig

## Purpose
Defines build-time configuration for the Linux CephFS client and optional CephFS features.

## Main Elements
- `CEPH_FS`: tristate Ceph distributed filesystem client, depending on `INET`, selecting `CEPH_LIB`, `NETFS_SUPPORT`, and encryption algorithms when fs encryption is enabled.
- `CEPH_FSCACHE`: optional persistent read-only local caching support through FS-Cache, constrained by whether CephFS and FS-Cache are built-in or modular.
- `CEPH_FS_POSIX_ACL`: optional POSIX ACL support, selecting `FS_POSIX_ACL`.
- `CEPH_FS_SECURITY_LABEL`: optional security label xattr support when Linux security modules are enabled.

## Dependencies And Integration
Controls which CephFS source files are built in `fs/ceph/Makefile` and connects CephFS to netfs, FS-Cache, encryption, POSIX ACL, and LSM infrastructure.

## Risk Notes
The FS-Cache dependency expression preserves module/built-in compatibility. ACL and security-label support are separate feature gates, so builds can include CephFS without those xattr-related paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/Makefile -->
# File Research: sources/os/linux/linux/fs/ceph/Makefile

## Purpose
Defines the CephFS client composite object list for the kernel build.

## Main Elements
- Core module target: `obj-$(CONFIG_CEPH_FS) += ceph.o`.
- Core sources: superblock, inode, directory, file, locks, address-space, ioctl, export, capabilities, snapshots, xattrs, quota, I/O, MDS client/map, strings, fragments, debugfs, utilities, and metrics.
- Optional sources: `cache.o` for `CONFIG_CEPH_FSCACHE`, `acl.o` for `CONFIG_CEPH_FS_POSIX_ACL`, and `crypto.o` for `CONFIG_FS_ENCRYPTION`.

## Dependencies And Integration
Maps Kconfig options to the CephFS build. The `acl.c` file in this group is built only when POSIX ACL support is enabled.

## Risk Notes
Optional files must match feature guards in headers and runtime code, particularly ACL, FS-Cache, and encryption integration points.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/acl.c -->
# File Research: sources/os/linux/linux/fs/ceph/acl.c

## Purpose
Implements CephFS POSIX ACL get/set support and ACL initialization payload preparation for newly created inodes.

## Main Elements
- `ceph_set_cached_acl()`: caches or forgets ACLs depending on whether the inode currently has `CEPH_CAP_XATTR_SHARED`.
- `ceph_get_acl()`: fetches ACL xattrs through `__ceph_getxattr()`, retries `-ERANGE` up to ten times, converts xattr bytes to `struct posix_acl`, and updates the VFS ACL cache.
- `ceph_set_acl()`: rejects snapshot inodes, validates access/default ACL type, updates mode through `posix_acl_update_mode()`, serializes ACLs to xattr format, applies mode changes with `__ceph_setattr()`, writes ACL xattrs with `__ceph_setxattr()`, and rolls mode back if xattr write fails.
- `ceph_pre_init_acls()`: computes inherited ACLs for new inode creation, drops equivalent access ACLs, encodes one or two ACL xattr records into a Ceph pagelist, and stores ACL pointers plus pagelist in `ceph_acl_sec_ctx`.
- `ceph_init_inode_acls()`: seeds the new inode ACL cache from the prepared ACL/security context.

## Dependencies And Integration
Uses Linux POSIX ACL helpers, Ceph xattr and setattr routines, Ceph capability state, Ceph pagelists for MDS request payloads, and Ceph inode/client helpers from `super.h` and `mds_client.h`.

## Risk Notes
ACL caching is valid only when xattr-shared capabilities are issued; otherwise cached ACLs are forgotten. `ceph_set_acl()` changes mode before setting the ACL xattr and attempts rollback on xattr failure. `ceph_pre_init_acls()` transfers ACL ownership to the caller on success, so error paths must release ACLs, temporary xattr buffers, and pagelists.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/acl.c -->