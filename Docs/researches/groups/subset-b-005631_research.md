# subset-b-005631 Research

Grouped source research for VFS buffer-head infrastructure, CacheFiles FS-Cache backing-store implementation, CacheFiles optional on-demand mode, and CephFS ACL build/runtime integration. Each section is source-path aligned and marker-delimited for deterministic split into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/buffer.c -->
# sources/distributed-fs/ceph-client/fs/buffer.c

## Purpose
`buffer.c` is the Linux VFS buffer-head implementation. It bridges block-mapped filesystems, block-device page cache, folios, bios, writeback, fsync metadata buffers, and legacy `buffer_head` APIs such as `bread`, `getblk`, `submit_bh`, and `block_write_begin`. The file is not Ceph-specific, but it is in this source tree as core filesystem infrastructure used by many local filesystems and by backing filesystems that CacheFiles may sit on.

## Important APIs, Types, and Functions
Important exported APIs include buffer locking and completion (`__lock_buffer`, `unlock_buffer`, `__wait_on_buffer`, `end_buffer_read_sync`, `end_buffer_write_sync`), buffer lookup/allocation (`bdev_getblk`, `__find_get_block`, `__find_get_block_nonatomic`, `__bread_gfp`, `__breadahead`, `folio_alloc_buffers`, `alloc_page_buffers`, `create_empty_buffers`), dirty/writeback helpers (`mark_buffer_dirty`, `block_dirty_folio`, `write_dirty_buffer`, `sync_dirty_buffer`, `__sync_dirty_buffer`, `mark_buffer_write_io_error`), block-mapped address-space operations (`block_read_full_folio`, `__block_write_full_folio`, `block_write_full_folio`, `block_write_begin`, `block_write_end`, `generic_write_end`, `block_truncate_page`, `block_page_mkwrite`, `generic_block_bmap`), invalidation/freeing (`block_invalidate_folio`, `clean_bdev_aliases`, `try_to_free_buffers`, `invalidate_bh_lrus`), and metadata-buffer fsync support (`mmb_init`, `mmb_mark_buffer_dirty`, `mmb_sync`, `mmb_fsync_noflush`, `mmb_fsync`, `mmb_invalidate`). Key local types are `struct bh_lru`, `struct postprocess_bh_ctx`, and per-CPU `struct bh_accounting`.

## Control Flow
Reads start by finding or creating buffers for a block-device or file folio, mapping missing blocks through a filesystem `get_block_t` or iomap, submitting individual locked buffers as bios, then completing through `end_buffer_async_read_io` and `end_buffer_async_read`. If fscrypt or fsverity applies, completion queues decrypt and/or verify work before marking buffers and the folio uptodate. Writes prepare buffers in `__block_write_begin_int`, zero newly allocated partial blocks, commit copied ranges with `block_commit_write`, then write dirty mapped buffers from `__block_write_full_folio` through `submit_bh_wbc`. Error recovery writes any already mapped dirty buffers and records mapping errors. `try_to_free_buffers` detaches clean unused buffer rings under the folio lock and `i_private_lock`. The metadata-buffer path records dependent buffers in `mapping_metadata_bhs`, moves initially dirty buffers to a temporary list during fsync, submits them, waits for completion, and only keeps buffers that became dirty again.

## State and Persistence Behavior
Persistent effects are actual block I/O and inode/page-cache dirty state. `buffer_head` state bits track mapped, uptodate, dirty, lock, request, async read/write, delay, unwritten, new, metadata, and write-error state. Folio state is kept coherent with buffer state so dirty folios, partial uptodate checks, truncation zeroing, and writeback completion remain correct. The per-CPU BH LRU keeps extra buffer references for lookup speed, while buffer-head accounting exposes pressure through `buffer_heads_over_limit`. `mmb` lists persist only in memory but are critical to durable fsync of filesystem metadata such as indirect blocks.

## Dependencies and Integration Points
This file integrates with the block layer (`bio`, `blkdev`, `blk_crypto_submit_bio`, request flags), the page cache and folio APIs, writeback control, fscrypt, fsverity, iomap conversion, inode dirty tracking, memory cgroups, CPU hotplug, and tracepoints. Filesystems call these helpers from address-space operations, mmap page-fault handling, truncate paths, fsync, block mapping, and buffer-cache reads.

## Risks and Edge Cases
The main risks are lost dirty state during races among `block_dirty_folio`, `try_to_free_buffers`, writeback, and truncate; stale data exposure when new or partially written buffers are not zeroed; I/O completion races across multiple buffer heads in one folio; block-device alias corruption if newly allocated blocks still have dirty aliases; and reference leaks through the per-CPU LRU. Crypto and verity post-processing add failure paths where a successful bio may still become a failed read. Boundary checks around maximum file size, end-of-device bios, i_size races, and mmap writes beyond EOF are high-risk.

## Test Signals
Useful signals include xfstests for buffer-head filesystems, truncate and mmap dirtying races, fsync metadata durability tests, block-device alias tests after allocation/free, fscrypt/fsverity buffered-read coverage, writeback under memory pressure, CPU hotplug with populated BH LRUs, fault injection for read/write bio errors, and lockdep/KASAN/KCSAN coverage of folio and `i_private_lock` interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/Kconfig -->
# sources/distributed-fs/ceph-client/fs/cachefiles/Kconfig

## Purpose
This Kconfig file defines the build-time feature switches for CacheFiles, the FS-Cache backend that stores network filesystem cache objects as files on a mounted local filesystem.

## Important APIs, Types, and Functions
It declares `CONFIG_CACHEFILES`, `CONFIG_CACHEFILES_DEBUG`, `CONFIG_CACHEFILES_ERROR_INJECTION`, and `CONFIG_CACHEFILES_ONDEMAND`. `CACHEFILES` is a tristate depending on `NETFS_SUPPORT`, `FSCACHE`, and `BLOCK`. Debug, error injection, and on-demand mode are optional booleans layered on top.

## Control Flow
There is no runtime control flow. Build configuration selects whether `fs/cachefiles` is compiled and which optional source files and internal code paths are enabled.

## State and Persistence Behavior
The state is compile-time configuration. Enabling `CACHEFILES` creates the module/built-in backend and its `/dev/cachefiles` daemon interface. `CACHEFILES_ERROR_INJECTION` exposes sysctl-driven test state. `CACHEFILES_ONDEMAND` enables the userspace delegated cache-miss protocol.

## Dependencies and Integration Points
The options integrate with the netfs library, FS-Cache core, block layer, sysctl for error injection, module parameter debug support, and userspace cachefilesd configuration.

## Risks and Edge Cases
Incorrect dependency changes can produce build combinations where CacheFiles lacks the netfs/FSCache/block primitives it assumes. On-demand mode is default off and materially changes read-miss behavior, so tests must cover both compiled-in and compiled-out stubs.

## Test Signals
Build `CACHEFILES` as built-in and module, with and without debug, error injection, and on-demand mode. Confirm `make oldconfig` prompts are sensible and that disabled optional features leave stubbed internal helpers link-clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/Makefile -->
# sources/distributed-fs/ceph-client/fs/cachefiles/Makefile

## Purpose
This Makefile composes the CacheFiles module object from its core implementation files and conditionally adds optional error-injection and on-demand sources.

## Important APIs, Types, and Functions
`cachefiles-y` includes `cache.o`, `daemon.o`, `interface.o`, `io.o`, `key.o`, `main.o`, `namei.o`, `security.o`, `volume.o`, and `xattr.o`. `cachefiles-$(CONFIG_CACHEFILES_ERROR_INJECTION)` adds `error_inject.o`; `cachefiles-$(CONFIG_CACHEFILES_ONDEMAND)` adds `ondemand.o`; `obj-$(CONFIG_CACHEFILES)` emits `cachefiles.o`.

## Control Flow
There is no runtime flow. Kbuild turns the selected objects into the CacheFiles module or built-in object, matching the internal header's conditional stubs.

## State and Persistence Behavior
Build selection determines which runtime features exist. The object list also defines link availability for exported internal symbols such as daemon fops, cache ops, netfs I/O ops, xattr helpers, volume acquisition, and on-demand request handlers.

## Dependencies and Integration Points
The Makefile integrates with the Kconfig symbols in the same directory and with core kernel Kbuild. Its ordering must keep `main.o` linked with all helpers it registers or references.

## Risks and Edge Cases
Missing an object causes link failures or feature stubs to diverge from actual compiled implementations. Adding on-demand calls outside `#ifdef CONFIG_CACHEFILES_ONDEMAND` without updating the Makefile and stubs would break non-on-demand builds.

## Test Signals
Run kernel builds for `CONFIG_CACHEFILES=n`, `m`, and `y`, and matrix builds for `CONFIG_CACHEFILES_ERROR_INJECTION` and `CONFIG_CACHEFILES_ONDEMAND`. Link failures are the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/cache.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/cache.c

## Purpose
`cache.c` manages high-level VFS lifecycle for a CacheFiles cache: binding a configured directory, validating the backing filesystem, registering with FS-Cache, enforcing free-space thresholds, and withdrawing the cache cleanly.

## Important APIs, Types, and Functions
The public functions are `cachefiles_add_cache`, `cachefiles_has_space`, and `cachefiles_withdraw_cache`. Important internal helpers are `cachefiles_withdraw_objects`, `cachefiles_withdraw_fscache_volumes`, `cachefiles_withdraw_volumes`, and `cachefiles_sync_cache`.

## Control Flow
`cachefiles_add_cache` acquires an FS-Cache cache cookie, prepares security credentials, resolves the configured root directory, rejects idmapped or read-only mounts and unsupported backing filesystems, computes file/block culling thresholds from `statfs`, creates or opens `cache` and `graveyard` directories, then calls `fscache_add_cache` and marks `CACHEFILES_READY`. `cachefiles_has_space` uses `statfs`, subtracts in-flight `b_writing`, compares remaining files/blocks against stop/cull/run thresholds, toggles `CACHEFILES_CULLING`, and returns `-ENOBUFS` for allocation stops. Withdrawal first unregisters the FS-Cache cache, withdraws active volume cookies, withdraws objects, waits for object cleanup, releases CacheFiles volumes, syncs the backing filesystem, and relinquishes the FS-Cache cookie.

## State and Persistence Behavior
Persistent state is the backing directory tree under the configured root, including live cache and graveyard directories. Runtime state in `struct cachefiles_cache` includes mount/dentry pointers, threshold percentages and absolute thresholds, ready/dead/culling flags, volume/object lists, released counters, and in-flight block-write accounting.

## Dependencies and Integration Points
This file depends on VFS path lookup, statfs, mount and superblock operations, FS-Cache cache registration/withdrawal, CacheFiles directory helpers, security credential override helpers, and tracepoints. It is invoked by daemon `bind`/release flow and by I/O allocation checks.

## Risks and Edge Cases
Backing filesystem capability checks are safety critical: missing `tmpfile`, xattr, statfs, sync, directory, or DIO-compatible blocksize support would corrupt later assumptions. Free-space logic must account for pending writes or CacheFiles can overcommit. Withdrawal must avoid racing object and volume access counts and must not free cache state before on-demand or FS-Cache users have quiesced.

## Test Signals
Test binding on supported and unsupported backing filesystems, read-only and idmapped mounts, low-free-space culling transitions, `statfs` failure injection, bind/unbind under active objects, and sync failure handling. Tracepoints and `cachefilesd` poll/read output expose culling state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/daemon.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/daemon.c

## Purpose
`daemon.c` implements the `/dev/cachefiles` control interface used by cachefilesd. It parses configuration/control commands, exposes cache state to userspace, handles polling, binds/unbinds caches, and coordinates daemon lifetime.

## Important APIs, Types, and Functions
It exports `cachefiles_daemon_fops`, `cachefiles_flush_reqs`, `cachefiles_get_unbind_pincount`, and `cachefiles_put_unbind_pincount`. The file operations are open, release, read, write, poll, and noop llseek. Command handlers include `bind`, `dir`, `tag`, `secctx`, `frun`, `fcull`, `fstop`, `brun`, `bcull`, `bstop`, `cull`, `debug`, `inuse`, plus on-demand `copen` and `restore` when configured.

## Control Flow
Open requires `CAP_SYS_ADMIN`, enforces a single open instance with `cachefiles_open`, allocates and initializes `struct cachefiles_cache`, sets default culling thresholds, initializes xarrays and lists, and attaches it to `file->private_data`. Writes copy one command from userspace, reject embedded NULs and oversized input, split command and arguments, serialize through `daemon_mutex`, and dispatch to the command table unless `CACHEFILES_DEAD` is set. Reads report either ordinary culling/threshold/release state or on-demand requests. Poll reports readable state changes or on-demand work and writable culling state. Release marks the cache dead, flushes on-demand requests if necessary, drops the daemon pointer, and decrements the unbind pin count, which eventually calls unbind and frees the cache.

## State and Persistence Behavior
Daemon-set state includes root directory, tag, optional security context ID, threshold percentages, ready/dead/culling/on-demand flags, request xarrays, and unbind pin count. `bind` persists by creating/opening cache directories and registering the cache. `cull` persists by unlinking or moving backing objects into the graveyard. Read drains `f_released` and `b_released` counters.

## Dependencies and Integration Points
The daemon interface connects userspace cachefilesd to `cache.c`, `namei.c`, `security.c`, `ondemand.c`, and FS-Cache. It uses Linux capability checks, copy-from-user/copy-to-user, poll waitqueues, current working directory for `cull`/`inuse`, LSM security helpers, and VFS path operations under CacheFiles credentials.

## Risks and Edge Cases
Single-open and unbind pinning prevent use-after-free while anonymous on-demand fds exist. Command parsing must reject malformed thresholds and second `dir`, `tag`, or `secctx` commands. The threshold invariant is `stop < cull < run < 100` for both files and blocks. `cachefiles_flush_reqs` relies on memory ordering with request enqueue to avoid orphaned on-demand requests during daemon death.

## Test Signals
Exercise command parser errors, duplicate open, non-admin open, bind without `dir`, bad threshold ranges, on-demand and non-on-demand poll/read behavior, release during active requests, `cull` and `inuse` with invalid cwd or names containing `/`, and daemon restart/recovery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/daemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/error_inject.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/error_inject.c

## Purpose
`error_inject.c` provides a small sysctl-controlled error injection mechanism for CacheFiles test builds.

## Important APIs, Types, and Functions
It defines the global `cachefiles_error_injection_state`, the `cachefiles_sysctls` table with `error_injection`, and registration helpers `cachefiles_register_error_injection` and `cachefiles_unregister_error_injection`.

## Control Flow
Module init calls registration when `CONFIG_CACHEFILES_ERROR_INJECTION` is enabled. The sysctl is registered under `cachefiles/error_injection`; reads and writes go through `proc_douintvec`. Module exit unregisters the table.

## State and Persistence Behavior
The sysctl integer is runtime-only state. `internal.h` interprets bit 1 as write `-ENOSPC`, bit 2 as read/write/remove `-EIO`, and disabled builds compile the state to zero through stubs.

## Dependencies and Integration Points
This file integrates with `main.c` init/exit and the inline injection helpers in `internal.h`, which are called throughout daemon, cache, namei, io, interface, and xattr paths.

## Risks and Edge Cases
Registration failure aborts module init. Tests must reset the global after use because it affects broad paths. Unsupported combinations are handled by stubs, so call sites should not require this object when the Kconfig option is off.

## Test Signals
Confirm the sysctl exists only with the option enabled; inject read, write/ENOSPC, write/EIO, and remove/EIO failures; verify cleanup unregisters the sysctl; and run non-error-injection builds to catch missing stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/error_inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/interface.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/interface.c

## Purpose
`interface.c` implements the FS-Cache cache-ops interface for CacheFiles cookies. It allocates backing objects, maps FS-Cache cookies to local files, handles resize/invalidation/withdrawal, and exposes the `cachefiles_cache_ops` vtable to FS-Cache.

## Important APIs, Types, and Functions
Important functions include `cachefiles_alloc_object`, `cachefiles_see_object`, `cachefiles_grab_object`, `cachefiles_put_object`, `cachefiles_adjust_size`, `cachefiles_lookup_cookie`, `cachefiles_shorten_object`, `cachefiles_resize_cookie`, `cachefiles_commit_object`, `cachefiles_clean_up_object`, `cachefiles_withdraw_cookie`, and `cachefiles_invalidate_cookie`. The exported integration object is `const struct fscache_cache_ops cachefiles_cache_ops`.

## Control Flow
Lookup allocates a `cachefiles_object`, optionally initializes on-demand metadata, cooks the cookie key into a backing filename, stores the object in `cookie->cache_priv`, enters cache credentials, and calls `cachefiles_look_up_object`. Successful lookup links the object to the cache list and adjusts backing file size to a direct-I/O block multiple. Resize shrinks by truncating and zeroing DIO padding, while growth only updates the cookie size. Withdrawal removes the object from active lists, sends on-demand close/cleanup, commits xattrs or deletes retired objects, unmarks the inode, drops the file, clears `cookie->cache_priv`, and releases the object reference. Invalidation swaps in a new tmpfile, marks content absent, resumes FS-Cache invalidation, then buries the old file if needed.

## State and Persistence Behavior
Runtime state is `struct cachefiles_object`: cookie, volume, active-list link, backing `struct file`, cooked name, debug ID, refcount, content state, tmpfile flag, and optional on-demand state. Persistent state is updated through backing file truncation, xattr writes, tmpfile linking, and old object removal. Cookie flags such as `FSCACHE_COOKIE_LOCAL_WRITE`, `NEEDS_UPDATE`, `RETIRED`, `NO_DATA_TO_READ`, and `HAVE_DATA` drive persistence decisions.

## Dependencies and Integration Points
This file is the FS-Cache entry point into CacheFiles. It depends on object-name cooking, VFS namei helpers, xattr coherency helpers, netfs operation begin/end from `io.c`, on-demand helpers, volume state, and fscache reference/access APIs.

## Risks and Edge Cases
Object reference counts and `cookie->cache_priv` lifetime are critical. Failed lookup leaves an allocated object attached until FS-Cache drops its access count. Invalidation must atomically swap the file under `object->lock` so new I/O targets the tmpfile. Size adjustment must preserve DIO alignment without accidentally exposing padding as real object data. Xattr update failure can leave stale or dirty cache objects.

## Test Signals
Test lookup of new, existing, stale, and weird objects; object size shrink/grow paths; invalidation while I/O is active; retired cookie deletion; local-write xattr commits; failed tmpfile creation; and reference leak detection through tracepoints and slab/KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/internal.h -->
# sources/distributed-fs/ceph-client/fs/cachefiles/internal.h

## Purpose
`internal.h` is the private contract for the CacheFiles implementation. It defines core structures, content/state enums, flags, inline helpers, conditional stubs, function prototypes, tracing hooks, credential override helpers, error macros, and debug/assertion macros.

## Important APIs, Types, and Functions
Key types are `enum cachefiles_content`, `struct cachefiles_volume`, `enum cachefiles_object_state`, `struct cachefiles_ondemand_info`, `struct cachefiles_object`, `struct cachefiles_cache`, `struct cachefiles_req`, and `enum cachefiles_has_space_for`. Important helpers include `cachefiles_in_ondemand_mode`, `cachefiles_cres_file`, `cachefiles_cres_object`, `cachefiles_state_changed`, error-injection inline helpers, on-demand state accessors, `cachefiles_begin_secure`, `cachefiles_end_secure`, `cachefiles_io_error`, and `cachefiles_io_error_obj`.

## Control Flow
The header itself is declarative, but its inlines participate in common flows: netfs cache resources recover the backing file/object through `cres`, daemon poll wakeups go through `cachefiles_state_changed`, VFS operations run under override creds through begin/end secure helpers, and fatal I/O errors mark a cache dead and flush on-demand requests. `CONFIG_CACHEFILES_ONDEMAND` and `CONFIG_CACHEFILES_ERROR_INJECTION` switch between real declarations and no-op/error stubs.

## State and Persistence Behavior
It defines all major runtime state: cache mount/dentries/credentials, volume fanout directories, object file/name/content/tmpfile state, request xarrays, culling thresholds and counters, released counters, write-block accounting, security ID, daemon flags, and on-demand object IDs. `enum cachefiles_content` values are persisted in object xattrs and must remain stable.

## Dependencies and Integration Points
The header integrates with FS-Cache, netfs cache resources, Linux credentials and security, xarray, tracepoints, and the `linux/cachefiles.h` userspace ABI. Every implementation file in `fs/cachefiles` depends on it.

## Risks and Edge Cases
Changing persisted enum values, struct fields used across files, flag bit positions, request semantics, or conditional stubs can break on-disk compatibility, non-optional builds, or daemon ABI behavior. Error macros have side effects beyond logging: they mark the cache dead and may flush requests.

## Test Signals
Build all Kconfig matrices, check on-disk xattr content values, run sparse/lockdep for helper use, test fatal I/O transitions to `CACHEFILES_DEAD`, and verify on-demand-off builds link with stubbed helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/io.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/io.c

## Purpose
`io.c` implements CacheFiles netfs-cache operations: direct reads and writes to backing files, occupancy queries, read-source selection, write preparation, write submission, and operation cleanup.

## Important APIs, Types, and Functions
Important functions are `cachefiles_read`, `cachefiles_query_occupancy`, `cachefiles_write_complete`, `__cachefiles_write`, `cachefiles_write`, `cachefiles_do_prepare_read`, `cachefiles_prepare_read`, `cachefiles_prepare_ondemand_read`, `__cachefiles_prepare_write`, `cachefiles_prepare_write`, `cachefiles_prepare_write_subreq`, `cachefiles_issue_write`, `cachefiles_end_operation`, and `cachefiles_begin_operation`. The local `struct cachefiles_kiocb` wraps a kernel `kiocb`, object ref, completion callback, invalidation generation, range data, async state, and in-flight block count.

## Control Flow
Reads wait for a readable FS-Cache operation, optionally seek to data to skip holes, zero-fill holes when requested, allocate a `cachefiles_kiocb`, submit direct `vfs_iocb_iter_read`, and complete synchronously or asynchronously through `cachefiles_read_complete`. Completion checks the cookie invalidation counter and calls the netfs termination callback. Writes prepare a similar kiocb, account in-flight blocks in `cache->b_writing`, submit direct `vfs_iocb_iter_write`, and on completion subtract accounting, marks `FSCACHE_COOKIE_HAVE_DATA`, and terminates the netfs request. Read preparation uses `SEEK_DATA` and `SEEK_HOLE` to choose cache read, server download, zero fill, or on-demand userspace fetch. Write preparation enforces page/DIO alignment, checks allocation status and free space, and may punch partially allocated regions when space is insufficient.

## State and Persistence Behavior
Persistent effects are direct writes, punched holes, and file allocation changes in the backing cache file. Runtime state includes kiocb refs, object refs, `b_writing`, cookie invalidation counters, `NO_DATA_TO_READ`, `HAVE_DATA`, and netfs subrequest flags such as `NETFS_SREQ_COPY_TO_CACHE` and `NETFS_SREQ_ONDEMAND`.

## Dependencies and Integration Points
This file plugs CacheFiles into `struct netfs_cache_ops`. It depends on FS-Cache operation gating, VFS direct I/O, `llseek` hole/data reporting, fallocate, netfs request/subrequest APIs, on-demand read requests, tracepoints, and credential override helpers.

## Risks and Edge Cases
Alignment is strict because backing files are opened with `O_DIRECT`; partial DIO ranges are skipped or extended only in controlled cases. Invalidation races are detected by comparing counters after reads. Hole/data seeking must handle `-ENXIO` distinctly from real errors. Space checks must include in-flight writes or writes can overrun culling thresholds. Async and sync completion share refcounted cleanup, so double completion or missed `cachefiles_put_kiocb` would leak or free early.

## Test Signals
Test cache hits, holes, partial cached extents, `SEEK_DATA`/`SEEK_HOLE` errors, on-demand read retry, direct-I/O misalignment, low-space write preparation, fallocate punch failures, async read/write completion, invalidation during read, and netfs write-subrequest termination accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/key.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/key.c

## Purpose
`key.c` converts FS-Cache binary cookie keys into safe CacheFiles backing filenames.

## Important APIs, Types, and Functions
The primary API is `cachefiles_cook_key`. Helpers and data tables include `cachefiles_charmap`, `cachefiles_filecharmap`, and `how_many_hex_digits`.

## Control Flow
The function reads the cookie key, rejects keys that exceed the NAME_MAX-derived limit via `BUG_ON`, then chooses one of three encodings. Printable filename-safe ASCII keys are prefixed with `D` and copied directly. Non-printable keys are compared against compact big-endian and little-endian 32-bit hex chunk encodings, prefixed `S` or `T`, and the shorter one is used when it beats base64 length. Otherwise a custom base64-like encoding prefixed `E` plus padding count maps 3 raw bytes to 4 safe characters.

## State and Persistence Behavior
The computed name is allocated and stored in `object->d_name`. It becomes part of the persistent backing path `cache/volume/fanout/name`, so encoding stability is required for cache reuse across mounts and daemon restarts.

## Dependencies and Integration Points
It depends on FS-Cache cookie keys (`fscache_get_key`, `key_len`) and is called by `cachefiles_lookup_cookie` before namei lookup or creation.

## Risks and Edge Cases
Filename encoding is an on-disk ABI. Any change to prefixes, charmap, endian choice, padding, or printable-character policy can orphan existing cache entries. The code assumes padded key memory for 32-bit chunk reads. Slash, space, tab, and control characters must never appear directly in filenames.

## Test Signals
Test printable keys, slash/control/non-ASCII keys, short and non-multiple-of-three keys, all-zero and endian-sensitive 32-bit chunks, maximum-length keys, and stable encoded output across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/main.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/main.c

## Purpose
`main.c` is the CacheFiles module entry point. It registers the misc device used by cachefilesd, creates the object slab cache, registers optional error injection, defines tracepoints, and provides module metadata.

## Important APIs, Types, and Functions
Important state and functions are `cachefiles_debug`, module parameter `debug`, global `cachefiles_object_jar`, miscdevice `cachefiles_dev`, `cachefiles_init`, and `cachefiles_exit`.

## Control Flow
`cachefiles_init` registers error injection first, registers `/dev/cachefiles` as a misc device backed by `cachefiles_daemon_fops`, creates the `cachefiles_object_jar` slab, and reports loaded state. Failures unwind in reverse order. `cachefiles_exit` destroys the slab, deregisters the misc device, and unregisters error injection.

## State and Persistence Behavior
Runtime state includes the debug mask, miscdevice registration, and object slab cache. It does not persist cache data itself; backing cache state is created later by daemon bind and VFS helpers.

## Dependencies and Integration Points
This file integrates Kbuild/Kconfig output with the daemon interface, `error_inject.c`, tracepoint creation, module parameters, fs initcall ordering, and object allocation in `interface.c`.

## Risks and Edge Cases
Init ordering matters: object allocation cannot occur before the slab exists, and userspace cannot open the device before fops are registered. Error paths must deregister only what succeeded. Exit assumes no live daemon/object users remain.

## Test Signals
Load/unload as a module, built-in boot init, misc device creation, debug parameter read/write, forced init failures through fault injection, and leak checks after open/bind/unbind/unload cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/namei.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/namei.c

## Purpose
`namei.c` owns CacheFiles path walking, directory creation/pinning, backing object lookup/creation/opening, tmpfile commit, object burial/culling, and active-inode marking.

## Important APIs, Types, and Functions
Important APIs include `cachefiles_unmark_inode_in_use`, `cachefiles_get_directory`, `cachefiles_put_directory`, `cachefiles_bury_object`, `cachefiles_delete_object`, `cachefiles_create_tmpfile`, `cachefiles_look_up_object`, `cachefiles_commit_tmpfile`, `cachefiles_cull`, and `cachefiles_check_in_use`. Important local helpers include active mark/unmark functions, `cachefiles_unlink`, `cachefiles_create_file`, `cachefiles_open_file`, and `cachefiles_lookup_for_cull`.

## Control Flow
Directory setup uses `start_creating`, creates missing directories after space and LSM checks, marks directory inodes with `S_KERNEL_FILE` to block culling/removal, verifies directory operations and xattr support, and returns pinned dentries. Object lookup searches the fanout directory for the cooked object name, buries weird non-regular entries, opens regular files with `O_DIRECT`, initializes on-demand state, checks xattr coherency, and creates tmpfiles for missing or stale objects. New objects are unlinked tmpfiles until commit. Commit starts a create lookup, removes any stale conflicting entry, links the tmpfile into place, and clears the tmpfile flag. Burial unlinks files directly or renames directories into the graveyard with unique names. Cull and inuse commands look up candidates while rejecting in-use `S_KERNEL_FILE` inodes.

## State and Persistence Behavior
Persistent state is the backing directory tree: root `cache`, `graveyard`, volume directories, fanout directories, object files, linked tmpfiles, and graveyard entries. Runtime active state is encoded by `S_KERNEL_FILE` on backing inodes so userspace culling and CacheFiles object access do not collide. Release counters are updated when active objects are unmarked.

## Dependencies and Integration Points
The file uses VFS helper protocols (`start_creating`, `end_creating`, `start_removing`, `start_renaming_dentry`), LSM path checks, CacheFiles xattrs, object size/content state from `interface.c`, culling thresholds from `cache.c`, on-demand initialization, tracepoints, and FS-Cache kill reasons.

## Risks and Edge Cases
Inode marking is central: missed unmarking can make entries permanently uncullable, while missed marking can let userspace remove active cache files. Tmpfile commit races with another creator and must loop by unlinking stale entries. Directory burial must avoid mountpoints and directory loops. `cachefiles_check_in_use` depends on lookup helpers that may return with parent locks held, making lock discipline important.

## Test Signals
Test new object creation, stale xattr replacement, weird file type burial, tmpfile commit races, culling busy and idle objects, directory and file unlink errors, graveyard rename collision retries, mountpoint rejection, and active-inode mark/unmark leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/ondemand.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/ondemand.c

## Purpose
`ondemand.c` implements CacheFiles on-demand mode, where cache misses are delegated to a userspace backend through `/dev/cachefiles` messages and per-object anonymous fds.

## Important APIs, Types, and Functions
Important APIs include `cachefiles_ondemand_copen`, `cachefiles_ondemand_restore`, `cachefiles_ondemand_daemon_read`, `cachefiles_ondemand_init_object`, `cachefiles_ondemand_clean_object`, `cachefiles_ondemand_init_obj_info`, `cachefiles_ondemand_deinit_obj_info`, and `cachefiles_ondemand_read`. Local pieces include `struct ondemand_anon_file`, `cachefiles_ondemand_fd_fops`, fd release/write/llseek/ioctl handlers, `cachefiles_ondemand_get_fd`, `cachefiles_ondemand_select_req`, `cachefiles_ondemand_finish_req`, and `cachefiles_ondemand_send_req`.

## Control Flow
Opening an object sends an `OPEN` request with volume and cookie keys. Daemon read selects a marked new request from the request xarray fairly, creates an anonymous fd for `OPEN`, copies the message to userspace, and installs the fd after successful copy. Userspace completes `OPEN` by writing `copen id,size`, which updates cookie object size and opens state, or stores an error. Cache misses call `cachefiles_ondemand_read`, enqueue a `READ` request, and wait for userspace to write data through the anonymous fd and issue `CACHEFILES_IOC_READ_COMPLETE`. Object cleanup sends `CLOSE`, cancels outstanding object requests, marks dropping, and waits for reopen work to finish. Restore re-marks all pending requests as new after daemon recovery.

## State and Persistence Behavior
Runtime state is held in `cache->reqs`, `cache->ondemand_ids`, cyclic request/message counters, object `ondemand_id`, object on-demand state (`CLOSE`, `OPEN`, `REOPENING`, `DROPPING`), and anonymous fd references. Persistent cache content is written indirectly when userspace writes to the anonymous fd, which calls the ordinary CacheFiles prepare/write path against the backing file.

## Dependencies and Integration Points
This file depends on the userspace ABI in `linux/cachefiles.h`, anon inodes, xarrays, wait completions, fscache workqueue, daemon read/write/poll paths, CacheFiles direct write helpers, and unbind pinning from `daemon.c`.

## Risks and Edge Cases
The request protocol has many races: daemon death versus enqueue, fd release versus `copen`, interrupted wait versus daemon completion, close requests without replies, and read requests on closed objects requiring reopen work. Unbind pinning must keep cache state alive while anonymous fds exist. Message ID reuse is deliberately avoided with cyclic free-slot selection. `restore` can replay half-processed requests after daemon crash, so request handlers must be idempotent enough for recovery.

## Test Signals
Test open/read/close happy paths, daemon crash and `restore`, anonymous fd close before `copen`, interrupted waits, object drop with pending requests, duplicate opens, read completion ioctl validation, userspace write alignment and errors, and on-demand-off build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/ondemand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/security.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/security.c

## Purpose
`security.c` prepares and validates credentials used by the kernel to access the CacheFiles backing filesystem.

## Important APIs, Types, and Functions
Public functions are `cachefiles_get_security_ID` and `cachefiles_determine_cache_security`. The local helper `cachefiles_check_cache_dir` probes LSM permission for directory and file creation.

## Control Flow
`cachefiles_get_security_ID` prepares kernel credentials from the current task and optionally applies a daemon-provided security context ID. `cachefiles_determine_cache_security` duplicates current creds, temporarily drops the override, derives file-creation security from the cache root inode with `set_create_files_as`, replaces `cache->cache_cred`, reinstalls the override, and checks whether mkdir/create are allowed in the root. `-EOPNOTSUPP` from permission probing is treated as acceptable.

## State and Persistence Behavior
The main runtime state is `cache->cache_cred`, plus optional `secid`/`have_secid` set by the daemon. These credentials do not persist on their own, but they determine labels and permission behavior for subsequently created backing directories and files.

## Dependencies and Integration Points
This file integrates LSM hooks, kernel credential APIs, daemon `secctx`, `cachefiles_begin_secure`/`cachefiles_end_secure`, and `cachefiles_add_cache` bind validation.

## Risks and Edge Cases
Credential override ordering is delicate: returning without reinstalling the override would break callers. Bad security contexts must fail bind before cache operations begin. LSMs that do not support create checks may return `-EOPNOTSUPP`, which is intentionally normalized.

## Test Signals
Test bind with and without `secctx`, invalid security contexts, SELinux/AppArmor create denials, backing directories with incompatible labels, and audit logs for created cache files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/volume.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/volume.c

## Purpose
`volume.c` maps FS-Cache volume cookies to CacheFiles backing directories and fanout subdirectories.

## Important APIs, Types, and Functions
The public functions are `cachefiles_acquire_volume`, `cachefiles_free_volume`, and `cachefiles_withdraw_volume`. The internal `__cachefiles_free_volume` releases dentries and clears the FS-Cache private pointer.

## Control Flow
Acquire allocates `struct cachefiles_volume`, builds a directory name from the volume key prefixed with `I`, enters cache credentials, creates or opens the volume directory, sets or validates its xattr coherency data, replaces stale volume directories by burying them, then creates and pins 256 fanout directories named `@00` through `@ff`. On success it stores the volume in `vcookie->cache_priv`, increments `n_accesses` to pin wakeups, and links the volume into the cache list. Free removes the volume from the cache list and releases fanout and volume dentries. Withdraw updates the volume xattr before freeing.

## State and Persistence Behavior
Persistent state is the volume directory, its coherency xattr, and the 256 fanout directories containing object files. Runtime state is the `cachefiles_volume` with `dentry`, `fanout[]`, `vcookie`, cache link, and cache pointer.

## Dependencies and Integration Points
This file uses `cachefiles_get_directory`, `cachefiles_put_directory`, xattr coherency helpers, FS-Cache volume access accounting, cache object-list lock, and namei burial for stale volume directories.

## Risks and Edge Cases
Partial fanout creation must unwind all directories. Coherency mismatches must remove stale directories without leaving active marks. The fixed 256-way fanout is part of object path layout and must match object lookup by low cookie hash byte.

## Test Signals
Test new volume creation, existing coherent volume reuse, stale volume xattr replacement, fanout creation failure unwind, concurrent volume withdraw/free, and object lookup across all fanout buckets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/volume.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/xattr.c -->
# sources/distributed-fs/ceph-client/fs/cachefiles/xattr.c

## Purpose
`xattr.c` stores and validates CacheFiles coherency metadata in backing filesystem extended attributes for both object files and volume directories.

## Important APIs, Types, and Functions
Important types are packed `struct cachefiles_xattr` and `struct cachefiles_vol_xattr`. Public functions are `cachefiles_set_object_xattr`, `cachefiles_check_auxdata`, `cachefiles_remove_object_xattr`, `cachefiles_prepare_to_write`, `cachefiles_set_volume_xattr`, and `cachefiles_check_volume_xattr`. The xattr name is `user.CacheFiles.cache`.

## Control Flow
Setting an object xattr allocates a buffer containing object size, zero point, object type, content state, and netfs aux data, then writes it under mount write access. Checking object auxdata reads exactly the expected size and compares type, aux data, object size, and dirty content state. Dirty objects are rejected as stale pending future conflict resolution. Removing an xattr marks an object stale and treats missing xattrs as success. Volume xattr set/check writes a reserved zero field plus volume coherency bytes and validates reserved/data fields.

## State and Persistence Behavior
Object xattrs are persistent coherency records controlling whether a cache file can be reused after remount or lookup. `CACHEFILES_CONTENT_DIRTY` is written when local-write state exists. Volume xattrs persist netfs volume coherency data. Removal makes an object effectively stale.

## Dependencies and Integration Points
This file depends on VFS xattr APIs, mount write accounting, FS-Cache cookie aux/coherency accessors, CacheFiles content enums, tracepoints, and fatal I/O error handling. It is used by object lookup, commit, invalidation, volume acquisition, volume withdrawal, and write preparation.

## Risks and Edge Cases
The packed xattr layout is on-disk ABI. Exact length matching means aux length changes intentionally stale old cache files. Dirty content is currently rejected rather than reconciled. Failed xattr writes may mark the whole cache dead except for memory errors. The trace helper reads the first aux bytes as big-endian data, so zero-length aux data deserves care.

## Test Signals
Test coherent and stale object xattrs, aux mismatch, object size mismatch, dirty content rejection, missing xattr removal, EIO on get/set/remove, volume coherency mismatch, xattr length changes, and remount reuse of valid cache entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/cachefiles/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/Kconfig -->
# sources/distributed-fs/ceph-client/fs/ceph/Kconfig

## Purpose
This Kconfig file declares the CephFS client and optional CephFS features in this tree.

## Important APIs, Types, and Functions
It defines `CONFIG_CEPH_FS`, `CONFIG_CEPH_FSCACHE`, `CONFIG_CEPH_FS_POSIX_ACL`, and `CONFIG_CEPH_FS_SECURITY_LABEL`. `CEPH_FS` depends on `INET` and selects `CEPH_LIB`, `NETFS_SUPPORT`, and encryption algorithms when filesystem encryption is enabled.

## Control Flow
There is no runtime control flow. Configuration selects whether CephFS builds, whether it can use FS-Cache for persistent read-only local caching, whether POSIX ACL support is compiled, and whether security-label xattr handling is compiled.

## State and Persistence Behavior
Compile-time state controls the availability of runtime features. Enabling POSIX ACLs changes inode permission behavior and includes `acl.o`; enabling FSCACHE includes Ceph cache integration when dependency constraints are met.

## Dependencies and Integration Points
The file integrates CephFS with networking, libceph, netfs, FS encryption, FS-Cache, POSIX ACL core, and security module xattrs.

## Risks and Edge Cases
The `CEPH_FSCACHE` dependency differs for module versus built-in CephFS to ensure FS-Cache availability matches link mode. Incorrect dependencies can create invalid built-in/module combinations. ACL/security-label options change user-visible xattr and permission semantics.

## Test Signals
Build CephFS as `n`, `m`, and `y`; build with and without FS-Cache, POSIX ACLs, security labels, and encryption; verify menu dependency behavior and link outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/Makefile -->
# sources/distributed-fs/ceph-client/fs/ceph/Makefile

## Purpose
This Makefile builds the CephFS client object and conditionally includes optional feature objects.

## Important APIs, Types, and Functions
`obj-$(CONFIG_CEPH_FS)` emits `ceph.o`. Core `ceph-y` objects include superblock, inode, directory, file, locks, address-space, ioctl, export, caps, snap, xattr, quota, io, MDS client/map, strings, fragments, debugfs, util, metrics, and subvolume metrics. Optional additions are `cache.o` for `CONFIG_CEPH_FSCACHE`, `acl.o` for `CONFIG_CEPH_FS_POSIX_ACL`, and `crypto.o` for `CONFIG_FS_ENCRYPTION`.

## Control Flow
There is no runtime flow. Kbuild assembles `ceph.o` from the selected objects based on Kconfig.

## State and Persistence Behavior
The selected objects determine which runtime subsystems exist in the CephFS client, including ACL xattr handling, FS-Cache integration, and encryption helpers.

## Dependencies and Integration Points
The Makefile integrates with CephFS Kconfig and the wider kernel build. `acl.o` corresponds to `acl.c` and is only present when POSIX ACL support is selected.

## Risks and Edge Cases
Adding calls to optional objects without Kconfig guards causes link failures in reduced builds. Object ordering and inclusion must stay aligned with declarations in Ceph headers and operation tables.

## Test Signals
Build CephFS with ACL, cache, and crypto options independently toggled, as module and built-in where dependencies allow. Link errors are the primary regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/acl.c -->
# sources/distributed-fs/ceph-client/fs/ceph/acl.c

## Purpose
`acl.c` implements CephFS POSIX ACL get/set and create-time ACL initialization. It maps Linux POSIX ACL operations to Ceph xattrs and MDS setattr/xattr requests.

## Important APIs, Types, and Functions
Important functions are `ceph_set_cached_acl`, `ceph_get_acl`, `ceph_set_acl`, `ceph_pre_init_acls`, and `ceph_init_inode_acls`. It uses POSIX ACL xattr names `system.posix_acl_access` and `system.posix_acl_default`, Ceph inode/client helpers, `struct ceph_acl_sec_ctx`, and Ceph pagelists for create-time xattr batches.

## Control Flow
`ceph_get_acl` rejects RCU lookups with `-ECHILD`, selects the xattr name by ACL type, probes xattr size with `__ceph_getxattr`, allocates a buffer, retries up to ten times on `-ERANGE`, converts xattr bytes with `posix_acl_from_xattr`, treats missing/zero data as no ACL, logs other failures as `-EIO`, and caches only when Ceph xattr-shared caps are issued. `ceph_set_acl` rejects snapshot inodes, validates access/default ACL semantics, updates mode with `posix_acl_update_mode` for access ACLs, writes the mode/ctime through `__ceph_setattr` if needed, writes the ACL xattr through `__ceph_setxattr`, and attempts to roll back mode/ctime if xattr write fails. `ceph_pre_init_acls` computes inherited ACLs for create, drops equivalent access ACLs, encodes one or two xattr name/value pairs into a Ceph pagelist, and stores ACL pointers plus pagelist in `ceph_acl_sec_ctx`. `ceph_init_inode_acls` installs those ACLs into the new inode cache.

## State and Persistence Behavior
ACL persistence is through Ceph xattrs and mode updates on the MDS. In-memory ACL cache state is only trusted when `CEPH_CAP_XATTR_SHARED` is currently issued; otherwise cached ACLs are forgotten to avoid stale permission data. Create-time ACL state is staged in `ceph_acl_sec_ctx` until the MDS create request and then cached in the inode.

## Dependencies and Integration Points
The file depends on Linux POSIX ACL core, xattr conversion helpers, Ceph inode caps, Ceph xattr and setattr helpers, MDS client pagelist encoding, snapshots, and Ceph logging. It is compiled only when `CONFIG_CEPH_FS_POSIX_ACL` is enabled.

## Risks and Edge Cases
ACL xattr size can change between probe and read, so bounded `-ERANGE` retry is required. Mode rollback after xattr failure is best effort and can itself fail. ACL operations on snapshots must be read-only. Cache correctness depends on xattr-shared caps; caching without them would expose stale ACLs. Create-time pagelist reservation must handle memory failures without leaking ACL refs or pagelists.

## Test Signals
Test get/set access and default ACLs, setting default ACLs on non-directories, ACL removal, mode changes induced by access ACLs, snapshot rejection, MDS/xattr failures with rollback, `-ERANGE` retries, create inheritance with one and two ACL xattrs, and ACL cache invalidation when xattr caps are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/acl.c -->
