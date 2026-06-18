# Group Research: group_1422_openzfs_sources_cow_pools_openzfs_module_os_freebsd_spl_spl_taskq_c_eaad1d964ae0

Scope: `Docs/research_subset_a.md` includes `sources/cow-pools/openzfs`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_taskq.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_taskq.c

## Scope

FreeBSD SPL taskq compatibility implementation. It maps illumos-style `taskq_t` APIs onto FreeBSD `taskqueue(9)`, with global system queues, delayed dispatch, cancellation by task id, synced taskqueue creation, wait/drain helpers, and thread-local taskq tracking.

## Main Interfaces

- Initializes `system_taskq` and `system_delay_taskq` at `SYSINIT`; destroys them at `SYSUNINIT`.
- Creates taskqueues via `taskq_create()`, `taskq_create_proc()`, and `taskq_create_synced()`.
- Dispatches normal and delayed work through `taskq_dispatch()` and `taskq_dispatch_delay()`.
- Supports explicit `taskq_ent_t` storage through `taskq_init_ent()`, `taskq_dispatch_ent()`, and `taskq_empty_ent()`.
- Supports cancellation and waiting through `taskq_cancel_id()`, `taskq_wait()`, `taskq_wait_id()`, and `taskq_wait_outstanding()`.
- Exposes membership/current-taskq helpers: `taskq_member()` and `taskq_of_curthread()`.

## State And Control Flow

A UMA zone stores dynamically allocated `taskq_ent_t` objects. Each dispatched task gets a nonzero `taskqid_t` from an atomic counter and is inserted into a global hash table protected by striped `sx` locks. `taskq_lookup()` acquires a refcounted handle so cancellation and wait paths can safely refer to entries while the task may concurrently run.

Normal tasks use `TASK_INIT`; delayed tasks use `TIMEOUT_TASK_INIT`. Both execute through `taskq_run()`, call the requested function, then remove themselves from the id hash and drop their final reference. Cancellation removes pending tasks manually because they will not run and self-free.

`taskq_create_synced()` dispatches one synchronization task per worker, waits for each worker to record its `curthread`, resumes them, drains the queue, and returns the worker-thread array to the caller.

## Dependencies

Depends on FreeBSD `taskqueue`, `uma`, `sx`, `tsd`, atomics/refcounts, SPL `kmem`, and FreeBSD FPU kernel-thread setup on supported architectures.

## Correctness Notes

The id hash/refcount scheme is the central lifetime mechanism; any new task type must follow the same lookup/free rules. `taskq_cancel_id()` returns `EBUSY` only when a task is running and the caller did not wait; otherwise it reports successful cancellation or `ENOENT`. The TSD init callback also enables kernel FPU context for taskq threads on x86/aarch64, which matters for OpenZFS checksum/compression/crypto work.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_taskq.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_uio.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_uio.c

## Scope

FreeBSD SPL UIO bridge for ZFS. It wraps FreeBSD `struct uio` operations, provides copy-without-advancing behavior, implements skip/fault-safe movement helpers, checks page alignment, and pins user pages for direct I/O.

## Main Interfaces

- `zfs_uiomove()` wraps `uiomove()` and asserts direction consistency.
- `zfs_uiocopy()` clones a uio, copies via `vn_io_fault_uiomove()`, and reports copied bytes without advancing the original.
- `zfs_uioskip()` advances the uio by temporarily using `UIO_NOCOPY`.
- `zfs_uio_fault_move()` wraps fault-aware movement.
- `zfs_uio_page_aligned()` verifies each iovec base and length is page-aligned.
- Direct-I/O page lifecycle is handled by `zfs_uio_get_dio_pages_alloc()` and `zfs_uio_free_dio_pages()`.

## State And Control Flow

For direct I/O, the code allocates `uio->uio_dio.pages`, walks each nonempty iovec, and pins pages with `vm_fault_quick_hold_pages()`. It requires the number of pages obtained to match the expected page count and returns `EFAULT` on short holds. For write operations, pinned pages are made stable by acquiring shared busy state and removing write mappings with `pmap_remove_write()`. Release reverses this with `vm_page_sunbusy()`, `vm_page_unhold_pages()`, and frees the page array.

## Dependencies

Uses FreeBSD VM map/page APIs, `vn_io_fault_uiomove()`, SPL `zfs_uio_t` accessors, `kmem`, and FreeBSD-version-specific uio clone freeing.

## Correctness Notes

The direct-I/O path assumes aligned, page-granular iovecs: `zfs_uio_iov_step()` asserts `len == res * PAGE_SIZE`. Write-side stabilization is important because ZFS may checksum, compress, encrypt, deduplicate, or compute parity from user pages after they are pinned. Read-side direct I/O pages are not made immutable; later ABD/ZIO checksum verification must detect user modifications.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_uio.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_vfs.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_vfs.c

## Scope

FreeBSD VFS compatibility helpers for OpenZFS. It manages mount options, snapshot mounting, and asynchronous vnode release.

## Main Interfaces

- `vfs_setmntopt()` allocates and appends a `struct vfsopt` to `mnt_opt`.
- `vfs_clearmntopt()` deletes a named mount option.
- `vfs_optionisset()` queries `mnt_optnew`.
- `mount_snapshot()` mounts a ZFS snapshot filesystem on a synthetic `.zfs/snapshot/<name>` vnode.
- `vn_rele_async()` releases a vnode immediately when safe, or dispatches `vrele()` to a taskq when the last reference would trigger inactive processing.

## State And Control Flow

`mount_snapshot()` validates filesystem type/path lengths, resolves the VFS type, checks that the covered vnode is a directory and not already mounted, marks `VI_MOUNT`, allocates a new mount using parent credentials, sets `from`, read-only, nosuid, and ignored mount flags, then calls `VFS_MOUNT()`. On success it installs the mount under the covered vnode, adds it to `mountlist`, signals a mount event, and returns the snapshot root vnode. On mount failure it clears `VI_MOUNT`, ends the sequence counter write, releases the vnode, frees mount options, and destroys the mount.

## Dependencies

Uses FreeBSD mount/vnode internals, mount option lists, `VFS_MOUNT`, `VFS_ROOT`, namecache purge when enabled, `taskq_dispatch()`, and vnode reference counts.

## Correctness Notes

Snapshot mounts deliberately use parent mount credentials so ordinary users cannot unmount the automounted snapshot. The covered vnode is carefully transitioned through `VI_MOUNT`, `vn_seqc_write_begin/end`, and mount-list insertion. `vn_rele_async()` is a deadlock-avoidance helper: it avoids re-entering filesystem inactive paths synchronously when releasing the final vnode reference.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_vm.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_vm.c

## Scope

Small VM compatibility shim exposing FreeBSD VM pager constants and object lock wrappers under ZFS/SPL names.

## Main Interfaces

- Exports constant aliases for `VM_PAGER_BAD`, `VM_PAGER_ERROR`, `VM_PAGER_OK`, `VM_PAGER_PEND`, `VM_PAGER_PUT_SYNC`, and `VM_PAGER_PUT_INVAL`.
- Provides `zfs_vmobject_assert_wlocked()`, `zfs_vmobject_wlock()`, and `zfs_vmobject_wunlock()`.

## Dependencies

Depends directly on FreeBSD VM headers and lock macros: `VM_OBJECT_ASSERT_WLOCKED`, `VM_OBJECT_WLOCK`, and `VM_OBJECT_WUNLOCK`.

## Correctness Notes

This file intentionally keeps the wrappers as hard functions for compatibility, even though assertion file/line reporting is less helpful than a macro would be. It has no internal state.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_vm.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_zlib.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_zlib.c

## Scope

FreeBSD SPL zlib wrapper for OpenZFS compression/decompression callers. It adapts kernel allocation callbacks to FreeBSD malloc/free and provides ZFS-style `z_compress_level()` and `z_uncompress()`.

## Main Interfaces

- Internal zlib wrappers: `zlib_deflateInit()`, `zlib_deflate()`, `zlib_deflateEnd()`, `zlib_inflateInit()`, `zlib_inflate()`, and `zlib_inflateEnd()`.
- Public compression API: `z_compress_level(dest, destLen, source, sourceLen, level)`.
- Public decompression API: `z_uncompress(dest, destLen, source, sourceLen)`.

## State And Control Flow

`zcalloc()` and `zcfree()` route zlib allocation through `M_SOLARIS`. The workspace allocator stubs currently return `NULL`; disabled `#if 0` checks mean the zlib paths rely on the zlib stream allocation callbacks rather than an active workspace cache.

`z_compress_level()` initializes a `z_stream`, validates output size fits in `uInt`, calls deflate with `Z_FINISH`, maps incomplete output to `Z_BUF_ERROR`, stores `stream.total_out`, and tears down the stream. `z_uncompress()` mirrors this with inflate and maps missing dictionary or truncated input conditions to `Z_DATA_ERROR`.

## Dependencies

Uses FreeBSD kernel zlib from `contrib/zlib/zlib.h`, SPL `kmem`/`M_SOLARIS`, and ZFS zmod API expectations.

## Correctness Notes

The output-size truncation guard is important because zlib uses `uInt` lengths while ZFS passes `size_t`. Workspace caching is documented but not active in this FreeBSD implementation. Error conversion in `z_uncompress()` preserves expected zlib API semantics for corrupted/truncated inputs.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_zlib.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_zone.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_zone.c

## Scope

FreeBSD jail-backed implementation of ZFS zone dataset visibility and hostid helpers. It stores the list of datasets delegated to each jail using jail OSD storage.

## Main Interfaces

- `zone_dataset_attach()` adds a dataset to a jail after `PRIV_ZFS_JAIL` authorization.
- `zone_dataset_detach()` removes a delegated dataset from a jail.
- `zone_dataset_visible()` checks whether the current process can see a dataset and whether it is writable.
- `zone_get_hostid()` returns the current jail hostid.
- `zone_sysinit()` / `zone_sysuninit()` register and deregister the jail OSD slot.

## State And Control Flow

Each jail stores a `zone_dataset_head` list in `zone_slot`; each entry is a variable-sized `zone_dataset_t` containing the delegated dataset name. Attach allocates before taking prison locks, rejects duplicates, creates the OSD list lazily, and inserts the dataset. Detach finds the jail/list/name, removes the entry, and deletes the OSD slot when the list becomes empty.

Visibility is global-zone permissive. In a jail, it first checks whether the requested dataset is equal to or under a delegated dataset, which is visible and writable. It then checks whether the requested dataset is a parent of a delegated dataset, which is visible but read-only.

## Dependencies

Uses FreeBSD jails/prisons, OSD jail storage, privilege checks, allprison locking, and SPL policy wrappers.

## Correctness Notes

The prefix checks distinguish dataset separators `/`, snapshot separator `@`, exact names, and trailing slash parent forms. The OSD destructor frees every delegated dataset entry when a jail is destroyed.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_zone.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/abd_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/abd_os.c

## Scope

FreeBSD implementation of ARC Buffered Data OS primitives. It allocates and accounts for linear/scatter ABDs, wraps user pages for direct I/O, maps/unmaps ABD chunks, provides kstats, and supports borrow/return buffer operations for GEOM and other consumers.

## Main Interfaces

- Allocation/accounting: `abd_size_alloc_linear()`, `abd_alloc_chunks()`, `abd_free_chunks()`, `abd_alloc_struct_impl()`, `abd_free_struct_impl()`.
- Stats lifecycle: `abd_init()`, `abd_fini()`, `abd_update_scatter_stats()`, `abd_update_linear_stats()`, `abd_kstats_update()`.
- Zero/scatter support: `abd_alloc_zero_scatter()` and `abd_free_zero_scatter()`.
- Direct-I/O page wrapping: `abd_alloc_from_pages()`, `abd_get_offset_scatter()`, `abd_get_offset_from_pages()`.
- Iteration: `abd_iter_init()`, `abd_iter_at_end()`, `abd_iter_advance()`, `abd_iter_map()`, `abd_iter_unmap()`.
- Raw buffer borrowing: `abd_borrow_buf()`, `abd_borrow_buf_copy()`, `abd_return_buf()`, `abd_return_buf_copy()`.

## State And Control Flow

Scatter ABDs are page-chunk arrays allocated from `abd_chunk_cache`. Linear ABDs are used for small allocations or when scatter is disabled. `abd_zero_scatter` represents a full `SPA_MAXBLOCKSIZE` zero ABD by pointing every chunk at `zero_region`, avoiding per-page zero allocations.

`abd_alloc_from_pages()` can create a linear-page ABD for single-page user buffers or a scatter ABD whose chunks point directly at `vm_page_t` user pages. Iteration maps linear data directly, maps user pages through `zfs_map_page()`, or uses kernel-addressed scatter chunks without mapping.

Borrowing returns a direct pointer for linear ABDs and temporary `zio_buf` storage for scatter/gang ABDs; copy variants move contents in or out.

## Dependencies

Depends on ARC space accounting, kstats/wmsums, FreeBSD VM page mapping, `kmem_cache`, ZIO buffer allocation, ABD core helpers, and direct-I/O UIO page state.

## Correctness Notes

Scatter waste is charged to ARC via `ARC_SPACE_ABD_CHUNK_WASTE`. ABDs created from user pages must not free their underlying pages. Debug return checks intentionally avoid asserting unchanged direct-I/O read pages because user space may mutate them; ZIO checksums are expected to catch that.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/abd_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/arc_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/arc_os.c

## Scope

FreeBSD ARC OS integration. It supplies platform memory sizing/availability helpers, registers the low-memory event handler, and exposes the FreeBSD-specific `zfs_arc_free_target` sysctl parameter.

## Main Interfaces

- `arc_available_memory()` computes reclaim pressure from free pages and, on some platforms, UMA heap availability.
- `arc_default_max()` computes default ARC max from physical memory.
- `arc_all_memory()` and `arc_free_memory()` report physical/free memory.
- `arc_memory_throttle()` is a FreeBSD no-op returning success.
- `arc_lowmem_init()` and `arc_lowmem_fini()` manage the `vm_lowmem` event handler.
- `arc_register_hotplug()` and `arc_unregister_hotplug()` are no-ops.

## State And Control Flow

`arc_free_target_init()` runs after pagedaemon/page counters are initialized and captures `vm_cnt.v_free_target` into `zfs_arc_free_target`. On low-memory events, `arc_lowmem()` prevents ARC growth, marks ARC warm, computes a shrink target from `arc_c`, `arc_c_min`, `arc_shrink_shift`, and current available memory, reduces target size, and only waits for eviction when invoked from `pageproc`.

## Dependencies

Uses FreeBSD `vm_cnt`, `freemem`, `physmem`, UMA availability APIs, eventhandlers, DTrace probes, and core ARC globals/functions from `arc_impl.h`.

## Correctness Notes

The low-memory callback avoids blocking arbitrary threads because they may hold ARC locks and deadlock with reclaim. The `pageproc` special case is allowed to wait for eviction and records indirect memory-pressure stats; other callers only request direct reclaim pressure.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/arc_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/crypto_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/crypto_os.c

## Scope

FreeBSD OpenCrypto backend for ZFS encryption and HMAC. It implements SHA-512 HMAC helpers, creates AEAD crypto sessions for AES-GCM/AES-CCM, dispatches uio-backed cryptographic operations, and waits for async OpenCrypto completion.

## Main Interfaces

- HMAC: `crypto_mac_init()`, `crypto_mac_update()`, `crypto_mac_final()`, `crypto_mac()`.
- Session lifecycle: `freebsd_crypt_newsession()` and `freebsd_crypt_freesession()`.
- Dispatch: `freebsd_crypt_uio()` encrypts/decrypts authenticated uio payloads.
- Completion callbacks: `freebsd_zfs_crypt_done()` and synchronous no-op callback.

## State And Control Flow

`crypto_mac_init()` implements HMAC-SHA512 key normalization, ipad/opad setup, and inner/outer SHA512 context initialization. `crypto_mac_final()` completes inner and outer hashes, zeroes context/digest storage, and supports `mdsize == 0` for full digest output.

`freebsd_crypt_newsession()` maps ZFS crypt modes to OpenCrypto AEAD algorithms, validates AES key sizes, forces software crypto capability, initializes a mutex, and increments `crypt_sessions`. `freebsd_crypt_uio()` optionally creates a one-shot session, sets `crp_op`, `CRYPTO_F_CBIFSYNC`, `CRYPTO_F_IV_SEPARATE`, uio storage, AAD/payload/digest offsets, IV bytes, dispatches, frees the request, and frees temporary sessions.

`zfs_crypto_dispatch()` loops over `EAGAIN` and `ENOMEM`, sleeps briefly on memory pressure, and waits on `fs_done` for async sessions.

## Dependencies

Uses FreeBSD OpenCrypto, SHA512, ZFS `zio_crypt_info`, `crypto_key_t`, SPL UIO accessors, and kernel mutex/sleep APIs.

## Correctness Notes

Hardware crypto drivers are deliberately avoided because common FreeBSD offload drivers have AAD-length constraints unsuitable for ZFS. `session->fs_done` is reset on retry; async completion wakes sleepers on the `cryptop`. Sensitive key/HMAC intermediate buffers are zeroed after use.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/crypto_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/dmu_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/dmu_os.c

## Scope

FreeBSD DMU page-cache integration. It copies between VM pages and DMU buffers for writes and reads, including read-behind/read-ahead page filling.

## Main Interfaces

- `dmu_write_pages()` writes an array of VM pages into DMU buffers under a transaction.
- `dmu_read_pages()` fills requested VM pages from DMU buffers and opportunistically fills read-behind and read-ahead pages.

## State And Control Flow

`dmu_write_pages()` holds a DMU buffer array for the target object/range, marks each buffer for fill or dirty depending on full/partial coverage, maps each VM page through `zfs_map_page()`, copies into `db_data`, unmaps, and releases the buffer array.

`dmu_read_pages()` holds a buffer array for the page range, optionally grabs backward pages before the first requested page, copies into the primary page array while handling bogus pages and partial final pages, zero-fills the remainder of a partially filled page, then optionally fills forward read-ahead pages. Filled speculative pages are activated if waiters exist, otherwise deactivated.

## Dependencies

Uses DMU buffer hold/release APIs, FreeBSD VM page grab/busy/valid APIs, pmap write-map checks, ZFS page mapping helpers, and ZPL znode/vnops headers.

## Correctness Notes

The code asserts page index/order consistency and that pages being filled are not dirty or write-mapped. Partial DMU writes use `DMU_PARTIAL_FIRST` / `DMU_PARTIAL_MORE` flags for correct dirtying. Reads rely on DMU’s last-block zero-fill behavior and explicitly zero-fill any incomplete VM page.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/dmu_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/event_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/event_os.c

## Scope

Small FreeBSD kqueue helper for ZFS event code. It initializes a `knlist` protected by an `sx` lock.

## Main Interfaces

- `knlist_init_sx(struct knlist *knl, struct sx *lock)` installs lock, unlock, and assertion callbacks for a `knlist`.

## State And Control Flow

The helper callbacks call `sx_xlock()`, `sx_xunlock()`, and `sx_assert()` based on requested lock state. There is no persistent file-local state.

## Dependencies

Uses FreeBSD `struct knlist`, `struct sx`, and event/kqueue locking contracts.

## Correctness Notes

This allows FreeBSD event notification code to use `sx` locks where `knlist_init()` expects function pointers for locking and assertions.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/event_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/hkdf.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/hkdf.c

## Scope

HKDF-SHA512 implementation for FreeBSD ZFS encryption key derivation, using the platform HMAC helpers from `crypto_os.c`.

## Main Interfaces

- `hkdf_sha512()` performs extract then expand.
- Internal `hkdf_sha512_extract()` computes HMAC-SHA512 using `salt` as the HMAC key and `key_material` as input.
- Internal `hkdf_sha512_expand()` expands the extract key with `info` and counter blocks.

## State And Control Flow

Extract initializes a `crypto_key_t` from the salt and computes a SHA512 digest. Expand creates a `crypto_key_t` from the extract key, computes numbered HMAC blocks `T(i) = HMAC(PRK, T(i-1) || info || i)`, and copies the requested number of output bytes. It rejects expansion requiring more than 255 digest blocks.

## Dependencies

Uses `crypto_mac*()` HMAC helpers, `crypto_key_t`, SHA512 digest constants, and ZFS error macros.

## Correctness Notes

The block-count expression is intended to cap HKDF output at the RFC limit of 255 hash-length blocks. The code does not explicitly zero `extract_key` or temporary `T` before returning, so secret material lifetime depends on stack reuse and compiler behavior.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/hkdf.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/kmod_core.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/kmod_core.c

## Scope

FreeBSD kernel module entry point and `/dev/zfs` character device glue. It handles ioctl marshalling, per-open devfs private state, module load/unload/shutdown, and module dependency declarations.

## Main Interfaces

- `/dev/zfs` cdev operations: `zfsdev_open()` and `zfsdev_ioctl()`.
- Device lifecycle: `zfsdev_attach()` and `zfsdev_detach()`.
- Devfs private state hooks: `zfsdev_private_set_state()` and `zfsdev_private_get_state()`.
- Module lifecycle: `zfs__init()`, `zfs__fini()`, `zfs_shutdown()`, and `zfs_modevent()`.

## State And Control Flow

`zfsdev_ioctl()` validates the ioctl argument length, copies a user `zfs_cmd_t` into kernel memory, optionally translates legacy ioctl commands/structures, calls `zfsdev_ioctl_common()`, copies results back to user memory, frees temporary buffers, and verifies no rrw TSD remains.

`zfs__init()` holds root mount while initializing the ZFS kernel module, creates GEOM probe TSD storage, prints the feature-support version, releases root hold, and initializes sysevents. `zfs__fini()` refuses unload while pools/zvols/injection are busy, finalizes ZFS, and destroys GEOM probe TSD storage. Module load registers a post-sync shutdown handler; unload deregisters it after successful fini.

## Dependencies

Uses FreeBSD cdev/devfs, root mount hold, eventhandlers, module framework, ioctl compatibility code, OpenZFS `zfs_kmod_init/fini`, zvol busy checks, and GEOM probe TSD key.

## Correctness Notes

Unload is blocked while ZFS or zvol state is active. Shutdown skips fini during panic because normal teardown paths are not safe in a panicked kernel. Legacy ioctl compatibility is isolated behind `ZFS_LEGACY_SUPPORT`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/kmod_core.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/spa_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/spa_os.c

## Scope

FreeBSD SPA OS hooks, primarily root pool import from on-disk GEOM labels. Other import/export/activate/deactivate hooks are no-ops.

## Main Interfaces

- `spa_import_rootpool()` imports or prepares the root pool configuration.
- `spa_generate_rootconf()` reads top-level vdev configs from GEOM labels and constructs a root vdev tree.
- `spa_history_zone()` returns `"freebsd"`.
- `spa_import_os()`, `spa_export_os()`, `spa_activate_os()`, and `spa_deactivate_os()` are empty hooks.

## State And Control Flow

`spa_generate_rootconf()` calls `vdev_geom_read_pool_label()`, selects the highest-TXG config as the base, determines top-level child count and holes, duplicates available child vdev trees by ID, fills holes with `VDEV_TYPE_HOLE`, fills missing children with `VDEV_TYPE_MISSING`, wraps them under a synthetic root vdev with the pool GUID, removes top-level-only GUID fields from the pool config, frees intermediate configs, and returns the assembled config.

`spa_import_rootpool()` uses that config to replace or add namespace state for the root pool, marks it as root, applies import flags including checkpoint rewind, parses the vdev tree under `SCL_ALL`, immediately frees the parsed tree, exits namespace, and frees the temporary config.

## Dependencies

Uses GEOM label reading, SPA namespace/config locks, nvlist helpers, vdev config parsing/freeing, and pool import flags.

## Correctness Notes

Root-pool import must reconstruct a full root vdev tree even when boot labels only contain top-level configs. Missing or hole children are represented explicitly to preserve child IDs. Existing active imports are treated as success.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/spa_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/sysctl_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/sysctl_os.c

## Scope

FreeBSD sysctl namespace and tunable setter glue for OpenZFS. It creates `vfs.zfs.*` subtrees and implements validation/update callbacks for ARC, L2ARC, metaslab, MMP, deadman, RAIDZ, SPA, vdev, spacemap, and ZIO tunables.

## Main Interfaces

- Sysctl nodes: `arc`, `brt`, `condense`, `dbuf`, `dbuf_cache`, `deadman`, `dedup`, `l2arc`, `livelist`, `lua`, `metaslab`, `mg`, `multihost`, `prefetch`, `reconstruct`, `recv`, `send`, `spa`, `trim`, `txg`, `vdev`, `vnops`, `zevent`, `zil`, and `zio`.
- ARC setters: `param_set_arc_u64()`, `param_set_arc_int()`, `param_set_arc_max()`, `param_set_arc_min()`, `param_set_arc_free_target()`, `param_set_arc_no_grow_shift()`.
- L2ARC setter: `param_set_l2arc_dwpd_limit()`.
- Other setters: `param_set_active_allocator()`, `param_set_multihost_interval()`, `param_set_deadman_synctime()`, `param_set_deadman_ziotime()`, `param_set_deadman_failmode()`, `param_set_raidz_impl()`, `param_set_slop_shift()`, `param_set_min_auto_ashift()`, `param_set_max_auto_ashift()`.

## State And Control Flow

Most setters call `sysctl_handle_*`, return unchanged on read/no new value, validate ranges, mutate the global tunable, and trigger the relevant side effect. ARC setters call `arc_tuning_update()`. DWPD changes reset L2ARC endurance counters. Multihost interval changes signal MMP threads when SPA is initialized. Deadman setters propagate timing to SPA deadman state. RAIDZ implementation selection allocates a temporary string buffer and delegates validation to `vdev_raidz_impl_set()`.

## Dependencies

Depends on FreeBSD sysctl handlers, ARC/L2ARC globals, vdev ashift globals, MMP/deadman/metaslab common setters, and OpenZFS version metadata.

## Correctness Notes

`param_set_arc_max()` and `param_set_arc_min()` validate against minimum ARC size, current opposite bound, and total memory. `debugflags` intentionally prevents enabling `ZFS_DEBUG_MODIFY` after boot because ARC buffers would lack debug checksum metadata. `param_set_deadman_ziotime()` assigns `zfs_deadman_ziotime_ms` but calls `spa_set_deadman_ziotime(MSEC2NSEC(zfs_deadman_synctime_ms))`, which is notable and should be checked against upstream intent.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/sysctl_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/vdev_geom.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/vdev_geom.c

## Scope

FreeBSD GEOM-backed disk vdev implementation. It attaches ZFS vdevs to GEOM providers, reads labels, finds devices by path or GUIDs, handles provider events, translates ZIO reads/writes/trims/flushes into BIOs, and exposes `vdev_disk_ops`.

## Main Interfaces

- GEOM class: `zfs_vdev_class` with attrchanged callback.
- Attach/open helpers: `vdev_geom_attach()`, `vdev_geom_detach()`, `vdev_geom_open_by_path()`, `vdev_geom_open_by_guids()`, `vdev_geom_open()`, `vdev_geom_close()`.
- Label scanning: `vdev_geom_read_pool_label()`, `vdev_geom_read_config()`, `vdev_attach_ok()`, `process_vdev_config()`.
- I/O: `vdev_geom_io_start()`, `vdev_geom_io_intr()`, `vdev_geom_io_done()`.
- Unmapped I/O helpers: `vdev_geom_check_unmapped()` and `vdev_geom_fill_unmap_cb()`.
- Exported ops table: `vdev_disk_ops`.

## State And Control Flow

A shared GEOM named `zfs::vdev` owns consumers for providers. Each consumer private list tracks all `vdev_t` instances using that provider. Provider physpath changes update `vdev_physpath` and request config updates. Resize events autoexpand healthy vdevs when the pool requests it. Orphan events mark vdevs for async removal instead of closing under GEOM topology lock.

Opening sets a TSD marker so lower zvol probing can avoid recursion, validates `/dev/` paths, then either opens by path ignoring GUIDs for new/add/split cases or validates path labels and falls back to all-provider GUID search. On success it records provider size, sector ashift, stripe ashift, rotation rate, block-device status, and TRIM capability.

I/O start handles policy skips for disabled flush/delete, allocates a `bio`, maps ZIO type to BIO command, and for read/write either supplies unmapped page arrays for suitable scatter ABDs or borrows/copies a linear buffer. Completion records BIO errors/residuals, detects device removal, destroys non-data BIOs immediately, and delays ZIO interrupt. `io_done` returns borrowed buffers or frees unmapped page arrays.

## Dependencies

Uses FreeBSD GEOM provider/consumer APIs, BIOs, topology locking, VM page extraction, ABD iteration/borrowing, ZIO delay/error paths, SPA async requests, vdev config/label helpers, sysctl tunables, and TSD key from module init.

## Correctness Notes

Lock ordering is critical: provider orphan handling avoids taking SPA config locks while holding GEOM topology. Device discovery releases topology while reading labels, then reacquires it to detach. BIO offsets/sizes are sector-aligned for label probing. Unmapped I/O is used only when the provider accepts it and ABD chunk layout can be represented as a virtually contiguous page array. Close may be delayed during reopen unless the provider is orphaned or errored.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/vdev_geom.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/vdev_label_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/vdev_label_os.c

## Scope

FreeBSD vdev label OS helpers for writing pad2 boot metadata and checking whether the boot reserve area contains FreeBSD BTX boot code.

## Main Interfaces

- `vdev_label_write_pad2()` writes caller data plus zero padding to the label pad2 area.
- `vdev_check_boot_reserve()` reads the reserved boot area and reports `EBUSY` if BTX magic is present.

## State And Control Flow

`vdev_label_write_pad2()` validates size, leaf status, and liveness; requires full config writer lock; allocates an I/O ABD of `VDEV_PAD_SIZE`; copies input bytes, zero-fills the rest, issues a label write zio at `vl_be`, waits, frees the ABD, and returns the error.

`vdev_check_boot_reserve()` allocates one ashift-sized linear ABD, issues a child read using a negative logical offset to reach `VDEV_BOOT_OFFSET`, waits, inspects the first five bytes for BTX magic, frees the ABD, and returns `EBUSY` or success.

## Dependencies

Uses SPA/vdev label layout constants, ZIO root/child I/O, ABD allocation/copy/zero, and FreeBSD boot-area knowledge.

## Correctness Notes

The boot reserve check protects FreeBSD `zfsboot` data from being overwritten when attaching disks to RAIDZ. `zio_vdev_child_io()` normally offsets by `VDEV_LABEL_START_SIZE`, so this file intentionally passes an offset adjusted below zero to address the reserved area.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/vdev_label_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_acl.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_acl.c

## Scope

FreeBSD ZFS NFSv4 ACL implementation. It handles old and FUID ACL formats, ACL storage in SA or external DMU objects, mode derivation, chmod/chown ACL updates, ACL inheritance, get/set ACL operations, and access checks for regular access, delete, and rename.

## Main Interfaces

- Format ops: `zfs_acl_v0_ops` and `zfs_acl_fuid_ops`.
- Allocation/lifetime: `zfs_acl_alloc()`, `zfs_acl_node_alloc()`, `zfs_acl_free()`.
- Version/storage: `zfs_external_acl()`, `zfs_znode_acl_version()`, `zfs_acl_node_read()`, `zfs_aclset_common()`.
- Conversion: `zfs_acl_xform()`, `zfs_vsec_2_aclp()`, `zfs_copy_ace_2_fuid()`, `zfs_copy_fuid_2_ace()`, `zfs_copy_ace_2_oldace()`.
- Mode and chmod/chown: `zfs_mode_compute()`, `zfs_acl_chown_setattr()`, `zfs_acl_chmod_setattr()`.
- Creation/inheritance: `zfs_acl_ids_create()`, `zfs_acl_ids_free()`, `zfs_acl_ids_overquota()`.
- User APIs: `zfs_getacl()` and `zfs_setacl()`.
- Access checks: `zfs_has_access()`, `zfs_zaccess()`, `zfs_zaccess_rwx()`, `zfs_zaccess_unix()`, `zfs_zaccess_delete()`, `zfs_zaccess_rename()`, and `zfs_fastaccesschk_execute()`.

## State And Control Flow

The ACL is represented as `zfs_acl_t` containing a list of `zfs_acl_node_t` buffers and format-specific operation callbacks. Old ACLs store fixed `zfs_oldace_t`; FUID ACLs support compact owner/group/everyone ACE headers, explicit FUID ACEs, and object ACEs.

Reading computes ACL size/count from SA or legacy znode ACL fields, allocates a node, loads embedded, external, or SA ACE data, caches read-only ACLs on the znode, and maps checksum errors to `EIO`. Setting updates mode/pflags/ctime and writes ACL data either into SA attributes, embedded legacy znode fields, or an external DMU ACL object, allocating/freeing external objects as size/version changes.

Mode computation walks ACEs in order and derives POSIX mode bits from the first relevant owner/group/everyone read/write/execute decisions. Chmod rebuilds ACLs around trivial mode ACE masks while optionally preserving inheritable special ACEs and trimming groupmask permissions. Creation can inherit parent ACEs according to dataset `aclinherit`/`aclmode`, synthesize trivial ACLs, create FUID owner/group ids, and handle setgid policy.

Access checking first rejects dataset/flag conflicts such as read-only mounts, immutable data writes, quarantined reads/execs, and nounlink delete. It then evaluates ACEs in NFSv4 order, removes decided bits from the working mask, tracks deny masks, supports append fallback, and finally consults FreeBSD privilege policy for unresolved bits.

## Dependencies

Uses ZPL znodes/vnodes, SA attributes, DMU transactions/objects, ZIL ACL logging, FUID/idmap mapping, quota checks, FreeBSD credential and secpolicy helpers, NFSv4 ACL common routines, dataset ACL properties, and vnode locks.

## Correctness Notes

`z_acl_lock` and vnode lock expectations are strict on read/set paths. ACL cache replacement occurs during set and after successful writes. Delete/rename follow NFSv4 delete-child/delete semantics plus BSD-specific directory write requirements. FreeBSD intentionally ignores individual alternate data stream permissions for many xattr operations to avoid bogus `EACCES`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ctldir.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ctldir.c

## Scope

FreeBSD implementation of the synthetic `.zfs` control directory and `.zfs/snapshot` automount behavior. It builds virtual vnodes for `.zfs`, `snapshot`, and snapshot mountpoints using an in-file synthetic filesystem layer.

## Main Interfaces

- Synthetic vnode helpers: `sfs_vgetx()`, `sfs_vnode_get()`, `sfs_vnode_insert()`, `sfs_readdir_common()`, and reclaim helpers.
- Control directory lifecycle: `zfsctl_create()`, `zfsctl_destroy()`, `zfsctl_root()`, `zfsctl_is_node()`.
- VOP vectors: `zfsctl_ops_root`, `zfsctl_ops_snapdir`, and `zfsctl_ops_snapshot`.
- Snapshot lookup/mount: `zfsctl_snapdir_lookup()`, `zfsctl_snapshot_lookup()`, `zfsctl_snapshot_zname()`, `zfsctl_mounted_here()`.
- Snapshot listing/attrs: `zfsctl_snapdir_readdir()` and `zfsctl_snapdir_getattr()`.
- Unmount/lookup helpers: `zfsctl_lookup_objset()`, `zfsctl_umount_snapshots()`, `zfsctl_snapshot_unmount()`.

## State And Control Flow

`sfs_node_t` stores synthetic names, parent IDs, and IDs. The vnode hash key uses both parent and child id to avoid clashes between synthetic/root/snapshot id domains. `zfsctl_create()` allocates `.zfs` and `snapshot` nodes and copies root creation time for `.zfs` attributes.

Root lookup accepts `.`, `..`, and `snapshot`; root readdir emits `.`, `..`, and `snapshot`. Common vnode methods reject writes, report virtual directory attributes, produce short ZFS fids, expose pathconf ACL behavior, and return a trivial read/execute NFSv4 ACL.

Snapshot directory lookup validates a snapshot name, obtains or creates a synthetic snapshot vnode, waits/retries if another mount is in progress, constructs `<dataset>@<snap>` and mountpoint strings, calls `mount_snapshot()`, and returns the mounted snapshot root. On success it sets the mounted snapshot zfsvfs parent to the head filesystem and clears `VV_ROOT` so NFS traversal behaves as expected.

Snapshot readdir walks `dmu_snapshot_list_next()` with the directory offset as a cookie. Snapshot vnode reclaim frees its synthetic node; inactive recycles it. Unmount helpers locate mounted snapshot vnodes and call `dounmount()`.

## Dependencies

Uses FreeBSD vnode hash, VOP vectors, mount and namei APIs, ZFS dataset/snapshot listing, `mount_snapshot()` from `spl_vfs.c`, ZFS enter/exit, and NFS-oriented fid/path resolution behavior.

## Correctness Notes

The snapshot vnode can be uncovered, mounting, covered, or recently unmounted; lookup loops carefully to avoid racing automount and unmount. `zfsctl_umount_snapshots()` loops until transient uncovered states settle. The file explicitly notes root readdir’s small-buffer limitation: it expects enough room for its fixed entries or returns according to FreeBSD directory-read conventions.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ctldir.c -->