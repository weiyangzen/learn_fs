# Group Research: group_963_linux_stable_sources_os_linux_linux_stable_fs_buffer_c_sources_os_li_d927570354d4

Scope confirmed against `Docs/research_subset_a.md`: all listed files are within `sources/os/linux/linux-stable`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/buffer.c -->
# File Research: sources/os/linux/linux-stable/fs/buffer.c

This is the Linux buffer-head implementation for block-buffer-backed address spaces. It provides core primitives used by block devices and legacy or buffer-head-based filesystems for block lookup, buffer allocation, dirty tracking, read/write submission, folio integration, invalidation, and fsync support.

Major responsibilities:
- Buffer locking and completion: `__lock_buffer()`, `unlock_buffer()`, `__wait_on_buffer()`, `end_buffer_read_sync()`, `end_buffer_write_sync()`, async read/write completion handlers, and error propagation through `mark_buffer_write_io_error()`.
- Buffer cache lookup and allocation: per-CPU `bh_lru`, `__find_get_block()`, `__find_get_block_nonatomic()`, `bdev_getblk()`, `__bread_gfp()`, `__breadahead()`, `grow_buffers()`, and block-device folio buffer initialization.
- Folio and buffer state coherence: `block_dirty_folio()`, `create_empty_buffers()`, `folio_alloc_buffers()`, `try_to_free_buffers()`, `block_invalidate_folio()`, `clean_bdev_aliases()`, and dirty/writeback checks.
- Generic buffered write path: `__block_write_full_folio()`, `block_write_full_folio()`, `__block_write_begin_int()`, `block_write_begin()`, `block_write_end()`, `generic_write_end()`, and zeroing helpers.
- Generic buffered read path: `block_read_full_folio()` maps blocks, submits async reads, zero-fills holes, integrates fscrypt decryption and fsverity verification.
- Truncation and mmap write support: `block_truncate_page()` and `block_page_mkwrite()`.
- Direct buffer I/O submission: `submit_bh_wbc()`, `submit_bh()`, `write_dirty_buffer()`, `__sync_dirty_buffer()`, `sync_dirty_buffer()`, `__bh_read()`, and `__bh_read_batch()`.
- Metadata buffer fsync helper support: `mapping_metadata_bhs` management through `mmb_init()`, `mmb_mark_buffer_dirty()`, `mmb_sync()`, `mmb_fsync_noflush()`, `mmb_fsync()`, and `mmb_invalidate()`.

Important design points:
- The file is built around `struct buffer_head` rings attached to folios via `b_this_page`, with the folio private pointer storing the ring head.
- Dirty state is deliberately duplicated between folios and buffers. The code carefully orders dirtying and cleaning to avoid dirty buffer / clean folio inconsistencies.
- Block-device buffer cache lookup is accelerated with a per-CPU 16-entry LRU. It disables local IRQs or preemption while manipulating LRU entries and avoids isolated CPUs.
- `i_private_lock` protects buffer attachment/removal against `block_dirty_folio()` and `try_to_free_buffers()`. Folio locks are used where sleeping is possible and scale better than a mapping-global spinlock.
- The async read path can enqueue fscrypt decryption and fsverity verification work before completing the folio read.
- Writes use buffer-level dirty bits to decide which blocks to submit, then use folio writeback state to protect the buffer ring during submission.
- I/O errors are surfaced to the address-space error state and, for metadata lists, to the metadata mapping as well.

Key invariants:
- `submit_bh_wbc()` requires the buffer to be locked, mapped, have an end I/O handler, and not be delayed or unwritten.
- `try_to_free_buffers()` requires a locked folio and refuses to free buffers under writeback or with dirty/locked/refcounted buffer heads.
- `block_invalidate_folio()` requires a locked folio and clears mapped-to-disk state after invalidating affected buffers.
- Block write begin handles all mapped/uptodate combinations, with holes zero-filled and newly allocated partial blocks zeroed to avoid stale data exposure.
- Buffer-head allocation is accounted per CPU, with `buffer_heads_over_limit` set when live buffer heads exceed the computed limit.

External interfaces exported here are broad and central to filesystem code: buffer allocation/free, block lookup/read helpers, folio dirtying/invalidation, generic block read/write helpers, truncate/mkwrite helpers, bio submission wrappers, and fsync metadata helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/buffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/Kconfig

This Kconfig file defines build-time options for the CacheFiles filesystem cache backend.

Configuration entries:
- `CACHEFILES`: tristate option for filesystem caching on files. It depends on `NETFS_SUPPORT`, `FSCACHE`, and `BLOCK`. The help text describes using a mounted local filesystem as a cache for other filesystems, primarily network filesystems.
- `CACHEFILES_DEBUG`: optional dynamic debug support for CacheFiles. It depends on `CACHEFILES` and enables runtime debug output via module parameter or cachefilesd configuration.
- `CACHEFILES_ERROR_INJECTION`: optional fault injection support. It depends on `CACHEFILES` and `SYSCTL`, enabling live error injection through sysctl while a cache is active.
- `CACHEFILES_ONDEMAND`: optional userspace-assisted on-demand read support. It depends on `CACHEFILES`, defaults to `n`, and changes miss handling so userspace fetches data for the cache backend instead of the netfs fetching directly.

The file establishes CacheFiles as an FS-Cache/netfs backend rather than a standalone filesystem. Optional modes map directly to extra compilation units in the Makefile: `error_inject.o` and `ondemand.o`.

Notable behavior implication:
- On-demand mode is explicitly opt-in and off by default, reflecting a larger userspace protocol and daemon responsibility surface.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/Makefile

This Makefile builds the CacheFiles module.

Core object list:
- `cache.o`
- `daemon.o`
- `interface.o`
- `io.o`
- `key.o`
- `main.o`
- `namei.o`
- `security.o`
- `volume.o`
- `xattr.o`

Optional object list:
- `error_inject.o` when `CONFIG_CACHEFILES_ERROR_INJECTION=y`
- `ondemand.o` when `CONFIG_CACHEFILES_ONDEMAND=y`

Build target:
- `obj-$(CONFIG_CACHEFILES) := cachefiles.o`

The layout matches the subsystem split: module setup in `main.c`, daemon device protocol in `daemon.c`, FS-Cache hooks in `interface.c`, VFS object lookup in `namei.c`, netfs I/O operations in `io.c`, coherency xattrs in `xattr.c`, volume management in `volume.c`, and security credential handling in `security.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/cache.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/cache.c

This file manages high-level CacheFiles cache registration, space accounting, culling thresholds, withdrawal, and backing filesystem sync.

Primary functions:
- `cachefiles_add_cache()`: brings a cache online. It acquires an FS-Cache cache cookie, establishes security credentials, resolves the configured root directory, rejects idmapped and read-only mounts, validates required backing filesystem operations, reads statfs data, computes file/block culling thresholds, creates or opens `cache` and `graveyard` directories, registers with FS-Cache, and marks the cache ready.
- `cachefiles_has_space()`: checks free files and blocks against configured stop/cull/run thresholds. It subtracts pending write reservations from available blocks, starts culling when below cull thresholds, stops allocation below stop thresholds, and clears culling when above run thresholds.
- `cachefiles_withdraw_cache()`: unregisters from FS-Cache, withdraws fscache volumes and active objects, waits for object cleanup, withdraws CacheFiles volumes, syncs the backing filesystem, and relinquishes the cache cookie.
- Internal helpers withdraw active objects, withdraw fscache volumes, withdraw cachefiles volume structures, and sync the backing superblock.

Key constraints enforced:
- Backing root must support lookup, mkdir, tmpfile, xattrs, statfs, sync_fs, and a block size no larger than `PAGE_SIZE`.
- Idmapped mounts are rejected.
- The cache root must not be read-only.
- Cache limits are computed as percentages of total file and block counts at bind time.

Integration points:
- Calls into `security.c` for credential setup.
- Calls into `namei.c` for creating/opening cache directories.
- Registers `cachefiles_cache_ops` from `interface.c` with FS-Cache.
- Signals daemon state changes when culling starts or stops.

Error handling:
- VFS and statfs errors are traced.
- `-EIO` from backing operations marks the cache dead through `cachefiles_io_error()`.
- Partial setup is unwound by releasing directories, mount references, credentials, and FS-Cache cache cookies.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/daemon.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/daemon.c

This file implements the `/dev/cachefiles` daemon control interface. It provides a single-open misc-device protocol used by cachefilesd or equivalent userspace to configure, bind, monitor, cull, and optionally operate on-demand cache requests.

Major elements:
- `cachefiles_daemon_fops`: file operations for open, release, read, write, poll, and llseek.
- `cachefiles_daemon_cmds`: command table mapping text commands to handlers: `bind`, `brun`, `bcull`, `bstop`, `cull`, `debug`, `dir`, `frun`, `fcull`, `fstop`, `inuse`, `secctx`, `tag`, plus `copen` and `restore` when on-demand mode is enabled.
- `cachefiles_daemon_open()`: requires `CAP_SYS_ADMIN`, enforces single open with `cachefiles_open`, allocates and initializes `struct cachefiles_cache`, default thresholds, xarrays, lists, waitqueue, and unbind refcount.
- `cachefiles_daemon_release()`: marks the cache dead, flushes on-demand requests if enabled, detaches the file from the cache, and drops the unbind pin.
- `cachefiles_daemon_read()`: returns either ordinary culling/threshold state or delegates to on-demand request reads.
- `cachefiles_daemon_write()`: copies and parses one command string, serializes command execution with `daemon_mutex`, and dispatches to the matching handler.
- `cachefiles_daemon_poll()`: exposes readable state changes, on-demand requests, and culling state.

Configuration command behavior:
- `dir`: sets the cache root path once.
- `tag`: sets an FS-Cache cache tag once.
- `secctx`: converts a security context to a secid once.
- `frun/fcull/fstop` and `brun/bcull/bstop`: set percentage thresholds with strict ordering `stop < cull < run < 100`.
- `bind`: validates thresholds, requires `dir`, optionally enables on-demand mode, defaults tag to `CacheFiles`, and calls `cachefiles_add_cache()`.
- `cull` and `inuse`: operate relative to the daemon process current working directory and reject names containing `/`.

Concurrency and lifetime:
- `unbind_pincount` protects delayed unbind while anonymous on-demand fds may still exist.
- `cachefiles_flush_reqs()` completes and erases all pending on-demand requests, using a memory barrier paired with enqueue-side checks to avoid orphaned requests during teardown.
- `daemon_mutex` prevents overlapping command mutation of cache state.

Security:
- Opening requires admin capability.
- Filesystem operations are performed under cache credentials where appropriate.
- `secctx` is mediated through LSM security conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/daemon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/error_inject.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/error_inject.c

This optional file implements sysctl-backed error injection for CacheFiles when `CONFIG_CACHEFILES_ERROR_INJECTION` is enabled.

Main state:
- `cachefiles_error_injection_state`: global unsigned integer controlling injected failures.

Sysctl:
- Registers `/proc/sys/cachefiles/error_injection` with mode `0644` and `proc_douintvec`.
- `cachefiles_register_error_injection()` registers the sysctl table and returns `-ENOMEM` if registration fails.
- `cachefiles_unregister_error_injection()` unregisters it.

Consumers:
- Inline helpers in `internal.h` interpret the state:
  - read/remove errors return `-EIO` when bit 1 is set.
  - write errors return `-EIO` when bit 1 is set or `-ENOSPC` when bit 0 is set.

Purpose:
- Provides a controlled way to exercise CacheFiles error paths for VFS operations, xattr updates, lookup, read/write, truncate, unlink, rename, and fallocate paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/error_inject.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/interface.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/interface.c

This file implements the FS-Cache-facing CacheFiles backend operations for cookie/object lifecycle, resize, invalidation, lookup, withdrawal, and operation setup.

Primary object lifecycle:
- `cachefiles_alloc_object()` allocates a `struct cachefiles_object`, initializes locking/refcount/list fields, links it to the volume and cookie, assigns a debug id, and initializes on-demand metadata if needed.
- `cachefiles_grab_object()`, `cachefiles_see_object()`, and `cachefiles_put_object()` provide traced object reference management. Final release requires no open file, frees the cooked name, on-demand info, cookie reference, and slab object.
- `cachefiles_lookup_cookie()` creates the object, cooks the object key into a filename, looks up or creates backing storage, links it to the active object list, and adjusts backing file size.
- `cachefiles_withdraw_cookie()` removes an active object from the cache list, cleans on-demand state, commits or deletes the backing file, closes it, clears `cookie->cache_priv`, and drops the object reference.
- `cachefiles_invalidate_cookie()` replaces the current backing file with an unlinked tmpfile, marks content empty and needing update, resumes FS-Cache invalidation, and buries the old object if necessary.

Size and coherency handling:
- `cachefiles_adjust_size()` rounds object size to `CACHEFILES_DIO_BLOCK_SIZE`, truncates/discards partial tail pages when extending, and sets the backing file size.
- `cachefiles_shorten_object()` truncates a file to rounded DIO size and zero-fills the tail range when the logical object size is not DIO-aligned.
- `cachefiles_resize_cookie()` shrinks backing storage when needed and updates cookie object size.
- `cachefiles_commit_object()` writes xattrs when local writes or updates occurred and links tmpfiles into place.

FS-Cache ops exported:
- `cachefiles_cache_ops` supplies `acquire_volume`, `free_volume`, `lookup_cookie`, `withdraw_cookie`, `invalidate_cookie`, `begin_operation`, `resize_cookie`, and `prepare_to_write`.

Important behavior:
- Tmpfiles are used for invalidation and new object creation, then committed atomically by link in `namei.c`.
- Retired cookies delete existing non-tmpfile objects.
- Local-write and update flags drive xattr coherency updates.
- Object file pointer substitution is protected by `object->lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/interface.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/internal.h

This header defines CacheFiles internal data structures, enums, inline helpers, prototypes, error macros, and debug/assertion helpers.

Core data structures:
- `enum cachefiles_content`: persistent content states stored on disk, including no data, single/all data, backing-fs map, and dirty.
- `struct cachefiles_volume`: per-FS-Cache volume state with cache pointer, FS-Cache volume cookie, volume dentry, and 256 fanout dentries.
- `enum cachefiles_object_state` and `struct cachefiles_ondemand_info`: on-demand object state and worker/lock/id tracking.
- `struct cachefiles_object`: per-cookie object with FS-Cache cookie, volume, active-list link, backing file, cooked name, debug id, lock, refcount, content state, flags, and optional on-demand data.
- `struct cachefiles_cache`: whole cache state, including FS-Cache cookie, mount, store/graveyard dentries, daemon file, lists, credentials, daemon synchronization, release counters, threshold percentages and computed limits, flags, root/tag, unbind pin, on-demand xarrays, id counters, and security id state.
- `struct cachefiles_req`: on-demand request record with object pointer, completion, refcount, error, and user-visible message.

Important flags:
- Cache flags include ready, dead, culling, state changed, and on-demand mode.
- Object flag `CACHEFILES_OBJECT_USING_TMPFILE` tracks unlinked tmpfile storage.
- `CACHEFILES_REQ_NEW` is the xarray mark used to select unread on-demand requests.

Inline helpers:
- `cachefiles_in_ondemand_mode()`
- resource accessors for `netfs_cache_resources`
- daemon state wakeup helper
- optional error injection no-op implementations
- injected read/write/remove error helpers
- secure credential override begin/end helpers
- on-demand object state helpers and stubs when disabled.

Prototype organization:
- Grouped declarations for `cache.c`, `daemon.c`, `interface.c`, `io.c`, `key.c`, `namei.c`, `ondemand.c`, `security.c`, `volume.c`, and `xattr.c`.

Error handling:
- `cachefiles_io_error()` logs, notifies FS-Cache, marks the cache dead, and flushes on-demand requests when applicable.
- `cachefiles_io_error_obj()` adds object debug id context.

Debugging:
- Runtime debug masks are defined for function entry, exit, and debug messages.
- Assertions call `BUG()` in the active configuration block.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/io.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/io.c

This file implements CacheFiles data-path operations for netfs cache reads, writes, occupancy queries, read preparation, write preparation, and cache-resource operation setup.

I/O request wrapper:
- `struct cachefiles_kiocb` embeds a `kiocb`, refcount, range information, object pointer, termination callback, invalidation counter, async flag, and write block reservation count.
- `cachefiles_put_kiocb()` releases object and file references on final put.

Read path:
- `cachefiles_read()` waits for read access, optionally seeks for data with `SEEK_DATA`, zero-fills holes depending on requested hole behavior, allocates a direct-I/O kiocb, submits `vfs_iocb_iter_read()`, and reports completion through `cachefiles_read_complete()`.
- `cachefiles_read_complete()` validates the cookie invalidation counter before accepting successful data and converts stale completion to `-ESTALE`.
- `cachefiles_query_occupancy()` uses `SEEK_DATA` and `SEEK_HOLE` to report cached data ranges rounded to cache granularity.

Write path:
- `__cachefiles_write()` allocates a direct write kiocb, accounts pending blocks in `cache->b_writing`, submits `vfs_iocb_iter_write()`, and finalizes through `cachefiles_write_complete()`.
- `cachefiles_write_complete()` ends async write accounting, subtracts reserved pending blocks, marks the cookie as having data, invokes completion, and releases references.
- `cachefiles_write()` gates writes on FS-Cache operation state.

Read preparation:
- `cachefiles_do_prepare_read()` decides whether a netfs subrequest should read from cache, fill zeroes, download from server and copy to cache, or perform on-demand read.
- It handles EOF, no-data cookies, missing backing files, `SEEK_DATA/SEEK_HOLE` boundaries, and on-demand fetch/retry behavior.
- `cachefiles_prepare_read()` and `cachefiles_prepare_ondemand_read()` are wrappers for ordinary and on-demand paths.

Write preparation:
- `__cachefiles_prepare_write()` enforces page/DIO alignment, rounds length, checks cache space, detects allocated versus unallocated regions using `SEEK_DATA/SEEK_HOLE`, and punches holes when partially allocated regions cannot be safely overwritten under low-space conditions.
- `cachefiles_prepare_write()` performs file availability wait and credential override.
- `cachefiles_prepare_write_subreq()` sets netfs write stream limits and ensures the file exists.
- `cachefiles_issue_write()` trims or extends netfs write subrequests to `CACHEFILES_DIO_BLOCK_SIZE` boundaries, prepares space, and submits cache writes.

Operation setup:
- `cachefiles_begin_operation()` installs `cachefiles_netfs_cache_ops` into `netfs_cache_resources`, snapshots the object file under `object->lock`, and validates file presence unless only parameters are wanted.
- `cachefiles_end_operation()` drops the cached file reference and ends FS-Cache cookie access.

Important design details:
- Cache I/O is direct I/O (`IOCB_DIRECT`) and write uses `IOCB_WRITE`.
- `memalloc_nofs_save()` prevents filesystem recursion problems during backing I/O.
- Pending block accounting prevents `cachefiles_has_space()` from overestimating available cache space.
- On-demand mode reuses the same preparation logic but can trigger userspace fetches before retrying cache reads.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/key.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/key.c

This file converts FS-Cache binary cookie keys into safe backing filesystem filenames.

Key function:
- `cachefiles_cook_key()` takes the raw cookie key from `fscache_get_key()` and stores an allocated filename in `object->d_name`.

Encoding strategy:
- If the key consists entirely of filename-safe printable characters, it uses direct string encoding prefixed with `D`.
- Otherwise, it compares compactness of big-endian and little-endian 32-bit hex chunk encodings:
  - `S` indicates big-endian hex chunks.
  - `T` indicates little-endian hex chunks.
  - subsequent chunks are comma-separated.
- If hex is not smaller than custom base64, it uses base64-like encoding:
  - prefix `E`
  - second character records padding count
  - character map is digits, lowercase, uppercase, underscore, hyphen.

Constraints and assumptions:
- The key length must fit within `NAME_MAX - 3`.
- Hex encoding assumes the key has been padded to a whole number of 32-bit words.
- `/`, whitespace, control characters, space, and tab are excluded from direct filename rendering.

Purpose:
- Provides deterministic, path-safe, compact names for cache object files under fanout directories.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/key.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/main.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/main.c

This file implements CacheFiles module initialization and teardown.

Module metadata:
- Description: mounted-filesystem based cache.
- Author: Red Hat.
- License: GPL.
- Runtime parameter: `cachefiles_debug`, controlling debug mask output.

Global state:
- `cachefiles_object_jar`: slab cache for `struct cachefiles_object`.
- `cachefiles_dev`: misc device named `cachefiles`, dynamic minor, using `cachefiles_daemon_fops`.

Initialization:
- `cachefiles_init()` registers error injection support, registers the misc device, creates the `cachefiles_object_jar` slab cache, and logs successful load.
- It is registered with `fs_initcall()`, so it initializes during filesystem subsystem startup.

Failure unwind:
- If slab creation fails, the misc device is deregistered.
- If misc registration fails, error injection is unregistered.
- Errors are logged and returned.

Teardown:
- `cachefiles_exit()` destroys the object slab, deregisters the misc device, unregisters error injection, and logs unload.
- Registered with `module_exit()`.

This file is the narrow module shell; operational behavior lives in the daemon, FS-Cache interface, path lookup, and I/O files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/namei.c

This file handles CacheFiles backing filesystem path walking, directory creation, object file lookup, tmpfile creation/commit, culling, and deletion.

In-use marking:
- Uses inode flag `S_KERNEL_FILE` to mark cache directories/files as actively used by CacheFiles.
- `cachefiles_mark_inode_in_use()` and unmark helpers serialize with inode lock.
- Culling checks this flag to avoid deleting active cache files.

Directory management:
- `cachefiles_get_directory()` looks up or creates a subdirectory, marks it in use, validates it is searchable, supports required directory operations and xattrs, and returns a pinned dentry.
- `cachefiles_put_directory()` unmarks and drops a directory dentry.

Object deletion and burial:
- `cachefiles_unlink()` performs security check and `vfs_unlink()`, with EIO mapped to cache I/O error.
- `cachefiles_bury_object()` unlinks regular files directly, but renames directories into the graveyard using unique names so userspace can later clean them up.
- It handles stale dentries, mountpoints, rename security checks, collision retry, and graveyard loop prevention.
- `cachefiles_delete_object()` removes a cache file from its fanout directory.

Tmpfile and file creation:
- `cachefiles_create_tmpfile()` opens an unlinked tmpfile in the fanout directory with `O_RDWR | O_LARGEFILE | O_DIRECT`, marks it in use, initializes on-demand state, sizes it to rounded DIO object size, and verifies read/write iter support.
- `cachefiles_create_file()` checks file-space availability, creates a tmpfile, marks the cookie needing update, flags object as using tmpfile, and stores `object->file`.
- `cachefiles_commit_tmpfile()` links a tmpfile into the final fanout/name location, replacing stale existing entries if needed, and clears the tmpfile flag on success.

Existing object lookup:
- `cachefiles_look_up_object()` looks up `cache/volume/fanout/object-name`.
- Missing entries create new tmpfiles.
- Non-regular stale/weird entries are buried, then recreated.
- Regular files are opened by `cachefiles_open_file()`, which marks in use, opens direct I/O file handle, initializes on-demand state, checks auxdata xattr coherency, clears no-data flag, sets `object->file`, and touches atime.

Culling:
- `cachefiles_lookup_for_cull()` gets a removable dentry and rejects files marked `S_KERNEL_FILE`.
- `cachefiles_cull()` marks the victim as kernel file to prevent reuse, buries it, and counts the cull.
- `cachefiles_check_in_use()` returns whether a named object is busy or available.

Important interactions:
- Fanout directory is selected by low byte of `cookie->key_hash`.
- All backing VFS operations rely on secure credential overrides set by callers.
- Error injection hooks are present around lookup, mkdir, tmpfile, truncate, link, rename, and unlink paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/ondemand.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/ondemand.c

This optional file implements CacheFiles on-demand read mode, where userspace receives cache miss/open/read/close requests and can write fetched data through anonymous object fds.

Core protocol:
- Requests are stored in `cache->reqs` xarray and marked `CACHEFILES_REQ_NEW` until delivered to userspace.
- Each request contains a `cachefiles_msg` with opcode, length, msg id, object id, and opcode-specific payload.
- Object ids are allocated from `cache->ondemand_ids`.
- Userspace reads requests through `/dev/cachefiles`, replies to open with `copen`, completes reads with `CACHEFILES_IOC_READ_COMPLETE`, and writes fetched data to the anonymous fd.

Anonymous fd operations:
- `cachefiles_ondemand_get_fd()` allocates an object id, unused fd, and anon inode file using `cachefiles_ondemand_fd_fops`; it embeds the fd in the open message payload.
- `cachefiles_ondemand_fd_write_iter()` writes userspace-provided data into the backing cache file after preparing aligned cache space.
- `cachefiles_ondemand_fd_llseek()` delegates seeks to the backing file.
- `cachefiles_ondemand_fd_ioctl()` handles `CACHEFILES_IOC_READ_COMPLETE` by locating and completing the matching read request.
- `cachefiles_ondemand_fd_release()` marks the object closed, completes pending close requests, removes object id, drops object and unbind refs.

Request handling:
- `cachefiles_ondemand_send_req()` allocates and initializes a request, atomically checks cache liveness and enqueues it, wakes daemon pollers, waits killably for completion, handles interruption by trying to finish the request, and resets open state on failure.
- Memory barriers pair with `cachefiles_flush_reqs()` to avoid orphaning requests during daemon shutdown.
- `cachefiles_ondemand_daemon_read()` fairly selects new requests, skips reopening reads as needed, creates fds for open requests, copies messages to userspace, installs fds, and auto-finishes close/error requests.

Open/close/read commands:
- `cachefiles_ondemand_copen()` parses `copen <id>,<cache_size>`, removes the matching open request, updates cookie object size and no-data flag, transitions object state to open, and completes the request.
- `cachefiles_ondemand_restore()` re-marks existing requests as new after userspace daemon recovery.
- `cachefiles_ondemand_read()` sends a read request with offset and length.
- `cachefiles_ondemand_clean_object()` sends close, marks dropping, completes all requests for the object with `-EIO`, erases them, and cancels reopen work.

Reopen behavior:
- If a read request targets a closed object, `cachefiles_ondemand_select_req()` moves the object to reopening state and queues `ondemand_object_worker()`, which sends a new open request.
- Reads for objects already reopening are skipped until open completes.

Object metadata:
- `cachefiles_ondemand_init_obj_info()` allocates per-object info only in on-demand mode.
- `cachefiles_ondemand_init_object()` sends an open request unless the object is already open.
- Open request payload contains volume key and cookie key and requires `FSCACHE_ADV_WANT_CACHE_SIZE`.

Key risks controlled by the implementation:
- It avoids stale msg id reuse with cyclic xarray allocation.
- It handles daemon death by completing and erasing outstanding requests.
- It guards against anonymous fd being closed before `copen`.
- It waits for reopen work during object cleanup to prevent use-after-free.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/ondemand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/security.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/security.c

This file manages credentials and LSM security context for CacheFiles backing filesystem access.

Main functions:
- `cachefiles_get_security_ID()` creates kernel credentials from `current`. If the daemon configured a security context with `secctx`, it applies that secid using `set_security_override()`. The resulting credentials are stored in `cache->cache_cred`.
- `cachefiles_determine_cache_security()` replaces the initial credentials with credentials configured to create files as the cache root directory’s security context. It temporarily drops the active override, calls `set_create_files_as()`, installs the new credentials, reapplies override, and checks whether mkdir/create are permitted in the root.
- `cachefiles_check_cache_dir()` uses LSM hooks `security_inode_mkdir()` and `security_inode_create()` to validate create permissions.

Usage model:
- Callers use `cachefiles_begin_secure()` and `cachefiles_end_secure()` from `internal.h` to override current credentials while manipulating backing cache files.
- Security setup happens during `cachefiles_add_cache()` before directories are created/opened.

Important behavior:
- If `security_inode_mkdir()` returns `-EOPNOTSUPP`, cache security determination treats that as acceptable.
- Failed LSM context selection or create-as setup prevents cache registration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/volume.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/volume.c

This file manages CacheFiles per-volume directory structures.

Primary flow:
- `cachefiles_acquire_volume()` allocates `struct cachefiles_volume`, binds it to the FS-Cache volume cookie and cache, constructs a volume directory name from the volume key prefixed with `I`, creates or opens that directory under `cache->store`, checks or sets volume coherency xattr, creates 256 fanout directories named `@00` through `@ff`, stores the volume in `vcookie->cache_priv`, pins FS-Cache volume access, and links the volume into `cache->volumes`.
- `cachefiles_free_volume()` removes the volume from the cache list and frees dentries/structure.
- `cachefiles_withdraw_volume()` writes the volume xattr and frees the volume structure.

Coherency:
- Newly created volume directories receive a volume xattr.
- Existing volume directories are checked against the volume coherency data.
- If an existing volume is stale (`-ESTALE`), the directory is buried and acquisition retries.

Fanout:
- Each volume pre-creates and pins 256 fanout directories. Object files are later placed under one of these by low byte of cookie key hash.

Error handling:
- Partial fanout setup unwinds by putting all created directories.
- All directory operations run under secure cache credentials.
- Weird or stale volume directories can be moved to the graveyard through `cachefiles_bury_object()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/cachefiles/xattr.c

This file manages CacheFiles coherency metadata stored as user xattrs on backing files and volume directories.

Object xattr:
- Name: `user.CacheFiles.cache`.
- `struct cachefiles_xattr` stores:
  - big-endian object size
  - zero point
  - object type
  - content state
  - netfs auxiliary coherency data.
- `cachefiles_set_object_xattr()` writes object size, content state, and auxdata. Local-write cookies are marked `CACHEFILES_CONTENT_DIRTY`.
- `cachefiles_check_auxdata()` reads and validates the object xattr against expected type, auxdata, object size, and dirty state. Dirty objects are currently treated stale with a warning and TODO for conflict resolution.
- `cachefiles_remove_object_xattr()` removes the xattr to mark an object stale, treating missing xattr as success.

Write marker:
- `cachefiles_prepare_to_write()` writes an object xattr before local write unless the object is currently an unlinked tmpfile.

Volume xattr:
- `struct cachefiles_vol_xattr` stores reserved zero field plus FS-Cache volume coherency data.
- `cachefiles_set_volume_xattr()` writes volume coherency data.
- `cachefiles_check_volume_xattr()` validates xattr length, reserved field, and coherency bytes.

Operational details:
- Xattr writes use `mnt_want_write_file()` or `mnt_want_write()` around VFS set/remove operations.
- Error injection hooks can force read/write/remove failures.
- Non-memory VFS failures generally mark the cache or object as I/O failed.
- Tracepoints record coherency success/failure reason for object and volume checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/cachefiles/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/ceph/Kconfig

This Kconfig file defines CephFS client filesystem build options.

Configuration entries:
- `CEPH_FS`: tristate Ceph distributed filesystem client. It depends on `INET`, selects `CEPH_LIB`, `NETFS_SUPPORT`, and `FS_ENCRYPTION_ALGS` when filesystem encryption is enabled. It defaults to `n`.
- `CEPH_FSCACHE`: optional persistent read-only local caching support using FS-Cache. It is available only when CephFS and FS-Cache linkage are compatible: module CephFS with FS-Cache or built-in CephFS with built-in FS-Cache.
- `CEPH_FS_POSIX_ACL`: optional POSIX ACL support. It depends on `CEPH_FS` and selects `FS_POSIX_ACL`.
- `CEPH_FS_SECURITY_LABEL`: optional security label xattr support. It depends on `CEPH_FS` and `SECURITY`.

This file places CephFS in the same netfs ecosystem as CacheFiles by selecting `NETFS_SUPPORT` and optionally using FS-Cache. The ACL option controls compilation of `acl.o` from the Makefile.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ceph/Makefile

This Makefile builds the Ceph filesystem client module.

Main target:
- `obj-$(CONFIG_CEPH_FS) += ceph.o`

Core CephFS objects:
- `super.o`, `inode.o`, `dir.o`, `file.o`, `locks.o`, `addr.o`, `ioctl.o`
- `export.o`, `caps.o`, `snap.o`, `xattr.o`, `quota.o`, `io.o`
- `mds_client.o`, `mdsmap.o`, `strings.o`, `ceph_frag.o`
- `debugfs.o`, `util.o`, `metric.o`, `subvolume_metrics.o`

Optional objects:
- `cache.o` when `CONFIG_CEPH_FSCACHE` is enabled.
- `acl.o` when `CONFIG_CEPH_FS_POSIX_ACL` is enabled.
- `crypto.o` when `CONFIG_FS_ENCRYPTION` is enabled.

The file shows CephFS as a multi-component network filesystem client with optional local caching, ACLs, and encryption support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/acl.c

This file implements CephFS POSIX ACL get, set, pre-initialization, and inode cache initialization.

ACL cache handling:
- `ceph_set_cached_acl()` updates the VFS cached ACL only if the inode currently has `CEPH_CAP_XATTR_SHARED`; otherwise it forgets the cached ACL. This prevents caching ACLs without valid shared xattr capability from the MDS.

Get ACL:
- `ceph_get_acl()` rejects RCU mode with `-ECHILD`.
- It maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`.
- It first queries xattr size with `__ceph_getxattr()`, allocates a buffer if needed, then reads the xattr.
- It retries up to 10 times on `-ERANGE`, handling xattr size races.
- Positive data is decoded with `posix_acl_from_xattr()`.
- Missing or zero-length xattr yields `NULL`.
- Other failures are logged rate-limited and returned as `-EIO`.
- Successful non-error results are cached through `ceph_set_cached_acl()`.

Set ACL:
- `ceph_set_acl()` rejects snapshots with `-EROFS`.
- Access ACLs may update the inode mode through `posix_acl_update_mode()`.
- Default ACLs are allowed only on directories; setting a default ACL on non-directories returns `-EINVAL` unless removing it.
- ACLs are serialized with `posix_acl_to_xattr()`.
- If mode changes, it first calls `__ceph_setattr()` with new mode and ctime.
- Then it writes the ACL xattr with `__ceph_setxattr()`.
- If xattr write fails after a mode change, it attempts to restore the old mode and ctime.
- Successful updates refresh the cached ACL.

Create-time ACL initialization:
- `ceph_pre_init_acls()` calls `posix_acl_create()` for a new inode, simplifies equivalent access ACLs into mode bits, and builds a Ceph pagelist containing one or two xattr name/value pairs for access/default ACLs.
- It stores resulting ACL pointers and pagelist in `struct ceph_acl_sec_ctx`.
- It carefully releases ACLs, temporary xattr buffers, and pagelist on error.
- `ceph_init_inode_acls()` installs the prepared access/default ACLs into the new inode cache if the inode exists.

Important interactions:
- Uses Ceph MDS xattr and setattr helpers rather than local filesystem xattr ops.
- ACL caching is tied to Ceph capability state.
- Create-time ACLs are encoded into the request payload so the MDS can apply them atomically with inode creation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/acl.c -->