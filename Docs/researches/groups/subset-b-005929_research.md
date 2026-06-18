# subset-b-005929 grouped research

This grouped report covers the exact source files assigned to `subset-b-005929`. Each file section is bounded by the reconciliation markers required for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ww_mutex.h -->
# sources/distributed-fs/ceph-client/include/linux/ww_mutex.h

## Purpose
Defines the public wound/wait mutex API used by kernel subsystems that must acquire multiple same-class locks in arbitrary order without deadlocking. The header provides lock-class descriptors, acquisition contexts, initialization helpers, slowpath helpers, and declarations for the core lock, trylock, interruptible lock, and unlock routines.

## Important APIs, Types, and Functions
`struct ww_class` owns the monotonically increasing acquisition stamp and lockdep class keys for a family of related ww mutexes. `struct ww_mutex` embeds either a normal `mutex` or an `rt_mutex` under `CONFIG_PREEMPT_RT`, plus the active owner acquisition context. `struct ww_acquire_ctx` records the acquiring task, stamp, count of acquired locks, wound state, algorithm choice, lockdep maps, and optional debug injection counters. `DEFINE_WD_CLASS()` selects wait/die ordering; `DEFINE_WW_CLASS()` selects wound/wait ordering. Public calls are `ww_mutex_init()`, `ww_acquire_init()`, `ww_acquire_done()`, `ww_acquire_fini()`, `ww_mutex_lock()`, `ww_mutex_lock_interruptible()`, `ww_mutex_lock_slow()`, `ww_mutex_lock_slow_interruptible()`, `ww_mutex_trylock()`, `ww_mutex_unlock()`, `ww_mutex_destroy()`, and `ww_mutex_is_locked()`.

## Control Flow
Typical use starts by defining a class, initializing each `ww_mutex`, creating a stack `ww_acquire_ctx`, and attempting locks with the same context. `ww_mutex_lock()` returns `0` on success, `-EALREADY` for the same lock/context, or `-EDEADLK` when the caller must back off. On `-EDEADLK`, the caller releases all locks already acquired for the context, waits on the contended lock via the slowpath helper, then retries the remaining lock set. `ww_acquire_done()` optionally marks the transition from acquisition to protected-data use, and `ww_acquire_fini()` releases lockdep bookkeeping after all ww mutexes are unlocked.

## State and Persistence
The header owns no persistent storage outside embedded objects, but the class stamp persists across acquire contexts and establishes ordering. Each lock stores its current acquisition context while held. Each acquire context is task-owned and must remain valid until all locks acquired under it have been released and `ww_acquire_fini()` has run. Lockdep and debug fields persist only under matching debug configs.

## Dependencies and Integration Points
Depends on `linux/mutex.h`, `linux/rtmutex.h`, lockdep annotations, `current`, atomics, and debug mutex config. Integrates with DRM/GPU reservation locking, buffer-object management, memory-management code, and other subsystems that lock sets discovered at runtime.

## Risks
The main risk is caller protocol abuse: mixing single-lock acquisition with context-based acquisition in the same class, using different contexts for the same class, freeing a context too early, failing to back off on `-EDEADLK`, or calling slowpath helpers while still holding other ww mutexes. PREEMPT_RT changes the underlying primitive, so code must rely on ww APIs rather than mutex internals. Debug-only checks catch many ordering mistakes, but production builds still depend on disciplined call patterns.

## Test Signals
Signals include lockdep/PROVE_LOCKING warnings, `CONFIG_DEBUG_WW_MUTEX_SLOWPATH` deadlock injection, DRM reservation stress tests, PREEMPT_RT lock tests, interruptible wait signal tests, and KCSAN/KASAN findings around context lifetime and unlock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ww_mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wwan.h -->
# sources/distributed-fs/ceph-client/include/linux/wwan.h

## Purpose
Defines the kernel WWAN core interface for modem control ports and data-link netdevices. The header lets transport drivers expose modem protocols as character devices, feed received control data into the core, control TX flow, and register network link operations for WWAN data devices.

## Important APIs, Types, and Functions
`enum wwan_port_type` classifies control protocols such as AT, MBIM, QMI, QCDM, Firehose, XMMRPC, Fastboot, ADB, MIPC, and NMEA. `struct wwan_port_ops` supplies mandatory `start`, `stop`, and nonblocking `tx` callbacks plus optional `tx_blocking` and `tx_poll`. `struct wwan_port_caps` describes TX fragment sizing and headroom. Port lifecycle and data APIs are `wwan_create_port()`, `wwan_remove_port()`, `wwan_port_rx()`, `wwan_port_txoff()`, `wwan_port_txon()`, and `wwan_port_get_drvdata()`. Network data-plane integration uses `struct wwan_netdev_priv`, `wwan_netdev_drvpriv()`, `WWAN_NO_DEFAULT_LINK`, `struct wwan_ops`, `wwan_register_ops()`, and `wwan_unregister_ops()`. Debugfs hooks are present when `CONFIG_WWAN_DEBUGFS` is enabled.

## Control Flow
A modem transport driver creates one or more ports under a shared parent device; the WWAN core exposes them as character devices associated with a virtual WWAN device. Userspace opens a port, which triggers `start`, writes data through `tx` or `tx_blocking`, and receives inbound `sk_buff` payloads passed to `wwan_port_rx()`. Flow-control transitions use `wwan_port_txoff()` and `wwan_port_txon()` to affect write/poll readiness. Data netdevices are installed by registering `wwan_ops`, after which rtnetlink-driven link creation calls `newlink` and deletion calls `dellink`.

## State and Persistence
Persistent state lives in opaque `struct wwan_port` instances, character devices, netdevices, and driver-private data stored by the core. `struct wwan_netdev_priv` persists the WWAN link id and embeds driver-private bytes at the end of netdev private storage. Debugfs directory references persist until released with `wwan_put_debugfs_dir()`.

## Dependencies and Integration Points
Depends on poll, skbuff, netdevice, device model, rtnetlink extack, debugfs, and driver data helpers. Integrates with USB, PCIe, MHI, and other modem transports, userspace modem managers, MBIM/QMI/AT protocol stacks, and Linux netdevice link management.

## Risks
Drivers must balance create/remove and register/unregister calls, honor nonblocking TX semantics, preserve SKB ownership expectations, and keep parent-device identity stable so ports are grouped correctly. Flow-control bugs can wedge userspace writers or lose wakeups. `WWAN_NO_DEFAULT_LINK` changes netdevice creation behavior and must match device expectations. Debugfs stubs return `ERR_PTR(-ENODEV)`, so consumers must not blindly dereference.

## Test Signals
Signals include WWAN core build tests, modem-manager port discovery, character device open/read/write/poll tests, TX flow-control tests, netlink newlink/dellink coverage, driver unbind cleanup, and debugfs enabled/disabled build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wwan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/xarray.h -->
# sources/distributed-fs/ceph-client/include/linux/xarray.h

## Purpose
Defines the XArray API, Linux's scalable sparse indexed pointer/value store used as the radix-tree successor. It exposes normal load/store/erase/iteration/allocation helpers and an advanced cursor API for code that needs tight control over locking, RCU traversal, marks, multi-index entries, and node updates.

## Important APIs, Types, and Functions
Entry helpers include `xa_mk_value()`, `xa_to_value()`, `xa_is_value()`, tagged pointer helpers, internal-entry helpers, `XA_ZERO_ENTRY`, `XA_RETRY_ENTRY`, `xa_is_zero()`, `xa_is_err()`, and `xa_err()`. `struct xa_limit` and predefined limits constrain ID allocation. `xa_mark_t` values provide three propagated marks plus `XA_PRESENT`. `struct xarray` embeds `xa_lock`, flags, and the RCU-protected tree head; it is initialized through `XARRAY_INIT`, `DEFINE_XARRAY*`, `xa_init_flags()`, or `xa_init()`. Normal APIs include `xa_load()`, `xa_store()`, `xa_erase()`, `xa_store_range()`, mark get/set/clear, `xa_find()`, `xa_find_after()`, `xa_extract()`, `xa_destroy()`, `xa_insert()`, `xa_alloc()`, `xa_alloc_cyclic()`, `xa_reserve()`, and `xa_release()`, with lock, bh, and irq variants for many mutators. The advanced API centers on `struct xa_state`, `XA_STATE()`, `XA_STATE_ORDER()`, `xas_load()`, `xas_store()`, `xas_find()`, `xas_find_marked()`, `xas_next()`, `xas_prev()`, `xas_retry()`, `xas_nomem()`, `xas_pause()`, multi-index split helpers, and iterator macros.

## Control Flow
Normal callers use the wrapper APIs, which take `xa_lock`, may call `might_alloc()`, delegate to `__xa_*` helpers, and release the lock. Iteration macros repeatedly call `xa_find()`/`xa_find_after()` and may take RCU internally. Allocation APIs require arrays initialized with allocation flags so free marks are maintained. Advanced callers create an `xa_state`, acquire either RCU or `xa_lock`, walk to an index, operate on entries, retry on `XA_RETRY_ENTRY`, handle allocation failure with `xas_nomem()`, and reset or pause the cursor after dropping locks. Inline fast paths handle leaf-node next/marked iteration and fall back to out-of-line functions for tree walks, internal entries, multi-index siblings, and boundary cases.

## State and Persistence
The XArray persists entries in `xa_head` and `struct xa_node` chunks. Nodes track shift, parent, slot count, value count, slot pointers, and mark bitmaps. Array flags persist GFP behavior, lock context requirements, allocation/free tracking, zero-busy behavior, accounting, and summary marks. Entries can be NULL, aligned pointers, value entries, tagged pointers, retry/zero/sibling internal entries, or error-encoded return values. RCU protects readers while writers update slots under `xa_lock`.

## Dependencies and Integration Points
Depends on bitmap, bug, compiler attributes, errno encoding, GFP flags, lockdep, RCU, scheduler allocation checks, spinlocks, and optional `list_lru`. Integrates heavily with the page cache, swap cache, ID allocation, filesystems, memory management, device subsystems, and any kernel code formerly using radix trees or IDR-like indexed maps.

## Risks
Storing internal entries through normal APIs is a bug. Callers must distinguish value entries, tagged pointers, NULL/reserved zero entries, and `xa_err()` results. Locking context must match `XA_FLAGS_LOCK_IRQ` or `XA_FLAGS_LOCK_BH` expectations. Advanced iteration can observe retry entries and must restart correctly after lock drops. Multi-index sibling handling is conditional on `CONFIG_XARRAY_MULTI`. Incorrect mark maintenance can break allocation and marked lookup. RCU readers must revalidate entries that can move or be replaced.

## Test Signals
Signals include XArray/radix-tree test suites, ID allocation wrap tests, page-cache stress, swap-cache tests, lockdep for wrong lock context, KCSAN for RCU misuse, fault-injection around `xas_nomem()`, multi-index split tests, and benchmarks for `xa_for_each*` versus advanced iterators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/xarray.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/xattr.h -->
# sources/distributed-fs/ceph-client/include/linux/xattr.h

## Purpose
Defines kernel extended-attribute interfaces for VFS and simple in-memory xattr storage. It provides handler dispatch contracts for filesystems, VFS get/set/list/remove declarations, POSIX ACL name detection, and rhashtable-backed `simple_xattrs` helpers used by pseudo filesystems.

## Important APIs, Types, and Functions
`is_posix_acl_xattr()` identifies access/default POSIX ACL xattr names. `struct xattr_handler` describes exact-name or prefix-based handlers with optional `list`, `get`, and `set` callbacks. VFS APIs include `__vfs_getxattr()`, `vfs_getxattr()`, `vfs_listxattr()`, `__vfs_setxattr()`, `__vfs_setxattr_noperm()`, locked set/remove variants, `vfs_setxattr()`, and `vfs_removexattr()`. `xattr_prefix()`, `xattr_full_name()`, `generic_listxattr()`, `vfs_getxattr_alloc()`, and `xattr_supports_user_prefix()` are helper APIs. Simple storage uses `struct simple_xattrs`, `struct simple_xattr`, `struct simple_xattr_limits`, `SIMPLE_XATTR_MAX_NR`, `SIMPLE_XATTR_MAX_SIZE`, allocation/free/get/set/list/add helpers, and cleanup `DEFINE_CLASS()` wrappers.

## Control Flow
Filesystem xattr operations match a requested name against handler name or prefix, call `xattr_handler_can_list()` for list visibility, and dispatch to handler callbacks through VFS helpers with mount idmap, dentry, inode, value buffer, size, and flags. Simple xattrs are initialized or lazily allocated, entries are allocated with flexible-array value storage, inserted into an rhashtable by name, replaced or removed through set helpers, and freed directly or by RCU callback.

## State and Persistence
VFS xattrs persist in filesystem-specific metadata, while `simple_xattrs` persist in an in-memory rhashtable owned by the containing object. `simple_xattr_limits` atomically tracks count and aggregate value bytes for bounded `user.*` storage. Individual `simple_xattr` objects persist name, size, value bytes, hash node, and RCU head until explicitly freed.

## Dependencies and Integration Points
Depends on slab allocation, spinlocks, MM types, rhashtable types, user namespaces/idmapped mounts, delegated inode handling, and UAPI xattr constants. Integrates with filesystems, security modules, POSIX ACL code, tmpfs/pseudo-filesystem helpers, and user-facing `getxattr`, `setxattr`, `listxattr`, and `removexattr` syscalls.

## Risks
Risks include handler prefix/name mismatches, listing attributes that should be hidden by permissions, idmap confusion in `set`, RCU lifetime bugs in simple storage, unbounded memory growth if limits are not used, and incorrect handling of `size == 0` probe semantics. POSIX ACL xattrs have special semantics and should not be treated as ordinary user metadata.

## Test Signals
Signals include xattr syscall tests, filesystem xattr and ACL suites, idmapped mount tests, LSM permission tests, simple_xattr limit tests, rhashtable/RCU debug coverage, and fault injection for allocation and replacement paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/xxhash.h -->
# sources/distributed-fs/ceph-client/include/linux/xxhash.h

## Purpose
Declares the in-kernel xxHash interface for fast non-cryptographic hashing. The header exposes one-shot 32-bit and 64-bit hashes, a word-size convenience wrapper, and streaming xxh64 state operations.

## Important APIs, Types, and Functions
`xxh32()` hashes a byte range with a 32-bit seed and returns a 32-bit hash. `xxh64()` hashes a byte range with a 64-bit seed and returns a 64-bit hash. `xxhash()` is an inline word-size selector that calls `xxh64()` on 64-bit builds and `xxh32()` on 32-bit builds when cross-machine stability is not required. `struct xxh64_state` stores private streaming state: total length, four accumulators, a partial 32-byte buffer, and buffered byte count. Streaming calls are `xxh64_reset()`, `xxh64_update()`, and `xxh64_digest()`.

## Control Flow
One-shot callers pass the complete input, length, and seed directly to `xxh32()` or `xxh64()`. Streaming callers reset a state with a seed, call `xxh64_update()` for each chunk, and call `xxh64_digest()` whenever a current hash is needed; digesting does not finalize or prevent later updates.

## State and Persistence
The one-shot APIs own no persistent state. Streaming state persists in caller-allocated `struct xxh64_state` and must not be inspected or modified directly despite the visible fields. The seed and accumulated byte sequence determine reproducible results for a fixed algorithm width.

## Dependencies and Integration Points
Depends only on Linux integer and size types. Integrates with kernel code that needs fast checksums or hash-table keys where collision resistance is not a security boundary, such as compression metadata, deduplication hints, caches, or content fingerprints.

## Risks
xxHash is not cryptographic and must not protect against adversarial collision or integrity attacks. `xxhash()` intentionally varies with word size, so persistent on-disk or network formats should choose `xxh32()` or `xxh64()` explicitly. Streaming state layout is visible for allocation only and should not become an ABI.

## Test Signals
Signals include known-vector tests for `xxh32`/`xxh64`, chunked-versus-one-shot equivalence, 32-bit and 64-bit build coverage for `xxhash()`, unaligned input tests, and fuzzing around zero-length and partial-buffer updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/xxhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/xz.h -->
# sources/distributed-fs/ceph-client/include/linux/xz.h

## Purpose
Declares the XZ and MicroLZMA decompressor APIs used in kernel and standalone/preboot contexts. It defines decoder modes, return codes, buffer descriptors, opaque decoder states, lifecycle routines, and optional internal CRC32 helpers.

## Important APIs, Types, and Functions
`enum xz_mode` selects `XZ_SINGLE`, `XZ_PREALLOC`, or `XZ_DYNALLOC`. `enum xz_ret` reports progress and failures including `XZ_OK`, `XZ_STREAM_END`, unsupported checks, memory errors, memory-limit errors, format/options/data errors, and buffer errors. `struct xz_buf` carries input and output buffers plus current positions. XZ lifecycle APIs are `xz_dec_init()`, `xz_dec_run()`, `xz_dec_reset()`, and `xz_dec_end()`. MicroLZMA uses opaque `struct xz_dec_microlzma` plus `xz_dec_microlzma_alloc()`, `xz_dec_microlzma_reset()`, `xz_dec_microlzma_run()`, and `xz_dec_microlzma_end()`. Standalone CRC support exposes `xz_crc32_init()` and `xz_crc32()` when `XZ_INTERNAL_CRC32` is enabled.

## Control Flow
Callers allocate a decoder for the selected mode, fill `xz_buf`, repeatedly call `xz_dec_run()` until `XZ_STREAM_END` or an error, optionally reset multi-call state for another stream, then end the decoder. Single-call mode decodes an entire stream in one call using the output buffer as dictionary workspace. Preallocated mode reserves dictionary memory at init time. Dynamic mode allocates after stream headers disclose dictionary size. MicroLZMA allocation records mode and dictionary size; each stream must be reset with compressed and uncompressed sizes before `xz_dec_microlzma_run()` loops to completion.

## State and Persistence
Opaque decoder states persist allocation mode, dictionary buffers, stream parser state, and integrity-check state. `xz_buf` position fields are mutable progress state owned by the caller. In single-call XZ mode, failed decodes leave input/output positions unmodified and output contents after the original position undefined.

## Dependencies and Integration Points
Depends on Linux or standalone stddef/stdint types and optional CRC32 selection. Integrates with kernel image/initramfs decompression, filesystems such as EROFS for MicroLZMA, module or firmware decompressors, and preboot code that may compile only selected modes.

## Risks
Mode-specific semantics are easy to misuse. `XZ_DYNALLOC` can return memory errors from `xz_dec_run()`, while `XZ_PREALLOC` reports dictionary limit failures. `XZ_BUF_ERROR` means different things in single-call and multi-call mode. MicroLZMA can keep returning `XZ_OK` without a buffer error, so callers must enforce input/output availability and detect truncation to avoid infinite loops. Unsupported integrity checks may be recoverable only in configurations that define support for any check.

## Test Signals
Signals include valid XZ streams across dictionary sizes, truncated/corrupt stream tests, unsupported option/check tests, low-memory and memory-limit injection, single-call buffer-too-small tests, MicroLZMA EROFS vectors, and standalone builds with internal CRC enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/xz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zconf.h -->
# sources/distributed-fs/ceph-client/include/linux/zconf.h

## Purpose
Provides the kernel zlib configuration constants and base typedefs used by `linux/zlib.h`. It captures maximum window and memory-level settings plus derived defaults for deflate/inflate workspace sizing.

## Important APIs, Types, and Functions
Defines `MAX_MEM_LEVEL`, `MAX_WBITS`, `DEF_WBITS`, and `DEF_MEM_LEVEL`, with defaults matching a 32 KiB LZ77 window and zlib's usual memory level. Type aliases are `Byte`, `uInt`, `uLong`, and `voidp`.

## Control Flow
No runtime control flow. Preprocessor selection allows build flags to reduce `MAX_MEM_LEVEL` or `MAX_WBITS`, and default macros derive decompression window and memory-level values from those build-time limits.

## State and Persistence
No state is stored here. The macros influence the memory footprint and capability of zlib stream workspaces allocated by callers and used by the implementation.

## Dependencies and Integration Points
Included by `linux/zlib.h` and therefore by all in-kernel users of the modified zlib interface. Integrates with deflate/inflate workspace sizing, gzip/zlib/deflate format support, and build-time tuning for memory-constrained environments.

## Risks
Reducing `MAX_WBITS` lowers memory use but can break decompression of gzip streams created with larger windows. Reducing `MAX_MEM_LEVEL` can degrade compression ratio or speed. The typedefs are legacy zlib names and can obscure exact integer width assumptions; code requiring fixed wire-format width should use explicit Linux integer types.

## Test Signals
Signals include zlib build coverage with default and reduced macros, gzip extraction compatibility tests, compression-ratio/performance checks under reduced memory settings, and workspace-size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zlib.h -->
# sources/distributed-fs/ceph-client/include/linux/zlib.h

## Purpose
Declares the Linux-kernel zlib deflate/inflate interface. This is a modified zlib API that keeps the stream model but requires callers to allocate per-stream workspaces in advance, adding kernel-specific flush and inflate helpers.

## Important APIs, Types, and Functions
`z_stream` carries input/output pointers, available byte counts, totals, error message, opaque internal state, caller-provided `workspace`, data type, checksum, and reserved field. Constants define flush modes (`Z_NO_FLUSH`, `Z_PACKET_FLUSH`, `Z_SYNC_FLUSH`, `Z_FULL_FLUSH`, `Z_FINISH`, `Z_BLOCK`), return codes, compression levels, strategies, data types, and `Z_DEFLATED`. Workspace APIs are `zlib_deflate_workspacesize()` and `zlib_inflate_workspacesize()`. Core APIs are `zlib_deflateInit2()`, `zlib_deflate()`, `zlib_deflateReset()`, `zlib_deflateEnd()`, `zlib_inflateInit2()`, `zlib_inflate()`, `zlib_inflateReset()`, `zlib_inflateEnd()`, `zlib_inflateIncomp()`, and `zlib_inflate_blob()`. Convenience macros provide `zlib_deflateInit()` and `zlib_inflateInit()`. `deflateBound()` estimates an upper bound for compressed output.

## Control Flow
Compression callers size and assign a workspace, initialize the stream, repeatedly supply input and output space to `zlib_deflate()`, optionally flush, finish with repeated `Z_FINISH` calls until `Z_STREAM_END`, then end or reset. Decompression callers allocate inflate workspace, initialize with default or explicit window bits, repeatedly call `zlib_inflate()` until `Z_STREAM_END` or an error, then reset or end. `Z_BLOCK` lets inflate stop on deflate block boundaries. `zlib_inflateIncomp()` updates history for incompressible data without producing output and is intended for PPP-style stored-block handling.

## State and Persistence
Persistent stream state lives in caller-owned `z_stream` plus the preallocated `workspace`; implementation-private details hang off `state`. `next_in`, `avail_in`, `total_in`, `next_out`, `avail_out`, and `total_out` are mutable progress counters. `adler` tracks Adler-32 or CRC32 depending on format. Reset APIs preserve allocated workspace while returning stream state to a reusable baseline.

## Dependencies and Integration Points
Depends on `linux/zconf.h`. Integrates with kernel compression users including PPP deflate, filesystems, boot and initramfs utilities, firmware/blob unpacking, and any code handling zlib, gzip, or raw deflate streams.

## Risks
Callers must provide correctly sized workspaces before init; unlike userspace zlib, allocation is not implicit. Buffer-progress loops must handle `Z_OK` with full output, nonfatal `Z_BUF_ERROR`, and repeated `Z_FINISH` calls. `windowBits` controls raw versus zlib/gzip decoding and must match producer format. Checksums and dictionary requests must be handled correctly. The visible dummy `internal_state` is only a compiler workaround, not an API.

## Test Signals
Signals include RFC 1950/1951/1952 vectors, raw/zlib/gzip inflate tests, PPP `Z_PACKET_FLUSH` and `zlib_inflateIncomp()` tests, workspace-size boundary tests, `Z_BLOCK` behavior, `zlib_inflate_blob()` success/error paths, truncated/corrupt input fuzzing, and build coverage across reduced `MAX_WBITS`/`MAX_MEM_LEVEL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zorro.h -->
# sources/distributed-fs/ceph-client/include/linux/zorro.h

## Purpose
Defines the Linux Amiga Zorro AutoConfig bus device and driver interfaces. It bridges architecture-discovered Zorro expansion boards into the generic device model and exposes helpers for resource management, driver registration, device lookup, and Zorro II RAM tracking.

## Important APIs, Types, and Functions
`struct zorro_dev` represents a discovered expansion device with ROM data, `zorro_id`, generic `struct device`, slot address/size, name, and memory resource. `struct zorro_driver` contains list linkage, name, optional match table, `probe`/`remove` callbacks, and embedded `device_driver`. Conversion helpers are `to_zorro_dev()` and `to_zorro_driver()`. Iteration uses `zorro_for_each_dev()`. Driver APIs are `zorro_register_driver()` and `zorro_unregister_driver()`. Global discovery state is `zorro_num_autocon`, `zorro_autocon`, and init-time `zorro_autocon_init[]`. Resource helpers expose start/end/length/flags and wrap `request_mem_region()`/`release_mem_region()`. `zorro_get_drvdata()` and `zorro_set_drvdata()` wrap generic device driver data. Zorro II RAM constants and `zorro_unused_z2ram` track allocatable 64 KiB chunks.

## Control Flow
Architecture boot code discovers AutoConfig boards into temporary init data, the Zorro bus creates persistent `zorro_dev` objects, and drivers register match tables plus callbacks. The bus matches devices and calls `probe`; drivers request the memory resource before using board address space and release it on remove. Lookup and iteration helpers allow legacy code to scan all discovered boards.

## State and Persistence
Persistent state includes the `zorro_autocon` array of devices, each device's resource and driver data, registered driver list, and the `zorro_unused_z2ram` bitmap. `zorro_autocon_init[]` is `__initdata` and valid only until init memory is freed.

## Dependencies and Integration Points
Depends on UAPI Zorro IDs, generic device model, init annotations, ioport resources, module device tables, and architecture `asm/zorro.h`. Integrates with Amiga/m68k platform setup, memory-resource management, module autoloading, and legacy Zorro board drivers.

## Risks
Use of init-only discovery data after boot is invalid. Drivers must request resources to avoid overlapping MMIO use. `remove` can be NULL for non-hotplug-capable drivers, so callers must respect optional removal. Zorro II RAM bitmap users must clear bits for allocated chunks to avoid double allocation.

## Test Signals
Signals include m68k/Amiga build and boot tests, Zorro driver probe/remove tests, resource conflict tests, module alias matching, `zorro_find_device()` coverage, and Zorro II RAM allocation bitmap validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zorro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zsmalloc.h -->
# sources/distributed-fs/ceph-client/include/linux/zsmalloc.h

## Purpose
Declares the zsmalloc compressed-object allocator API. It provides pool lifecycle, handle-based allocation/free, compaction, size-class queries, statistics, and object read/write helpers for storing compressed pages or similar variable-sized objects in tightly packed memory.

## Important APIs, Types, and Functions
`struct zs_pool` is the opaque allocator pool. `struct zs_pool_stats` currently reports `pages_compacted`. Core lifecycle and allocation APIs are `zs_create_pool()`, `zs_destroy_pool()`, `zs_malloc()`, and `zs_free()`. Capacity and maintenance APIs include `zs_huge_class_size()`, `zs_get_total_pages()`, `zs_compact()`, `zs_lookup_class_index()`, and `zs_pool_stats()`. Object access uses `zs_obj_read_begin()`, `zs_obj_read_end()`, `zs_obj_read_sg_begin()`, `zs_obj_read_sg_end()`, and `zs_obj_write()`. `zsmalloc_mops` exposes movable-page operations.

## Control Flow
Callers create a pool, allocate objects by size and NUMA node, receive opaque unsigned-long handles, access object contents through read/write helpers that map or copy handle memory, and free handles back to the pool. Compaction can migrate objects to free pages and reports reclaimed page activity. Scatterlist read helpers support direct readout into SG-backed consumers.

## State and Persistence
Persistent allocator state lives in `struct zs_pool` and its internal size classes, pages, and object metadata. Object identity is represented by opaque handles, not stable virtual addresses. Pool statistics persist as counters populated by `zs_pool_stats()`.

## Dependencies and Integration Points
Depends on Linux types, GFP allocation flags, NUMA node IDs, scatterlists, and movable page operations. Integrates with zswap, zram, memory reclaim/compaction, compressed page storage, and migration infrastructure.

## Risks
Handles must not be treated as direct pointers or used after `zs_free()`. Object access begin/end pairs must be balanced, especially if the implementation maps temporary memory or pins migration. Compaction can move objects, so users must rely on handles and allocator APIs. Incorrect size-class assumptions can waste memory or corrupt object boundaries.

## Test Signals
Signals include zsmalloc selftests, zram/zswap stress, compaction and migration tests, NUMA allocation coverage, KASAN/KMSAN around object read/write lengths, scatterlist read tests, and leak checks on pool destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zsmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zstd.h -->
# sources/distributed-fs/ceph-client/include/linux/zstd.h

## Purpose
Defines the kernel wrapper API around upstream Zstandard. It exposes selected compression, decompression, streaming, dictionary, frame-inspection, parameter-selection, and external-sequence APIs with kernel-style names because the upstream symbols are not exported directly.

## Important APIs, Types, and Functions
Helper APIs include `zstd_compress_bound()`, `zstd_is_error()`, `zstd_get_error_code()`, `zstd_get_error_name()`, and compression-level limit helpers. The header typedefs upstream types into kernel names: custom memory, dictionary load/content types, strategies, compression/frame/combined parameters, contexts, dictionaries, streams, buffers, frame headers, and sequences. Parameter APIs include `zstd_get_params()`, `zstd_get_cparams()`, and `zstd_cctx_set_param()`. Single-pass compression uses workspace-bound helpers, `zstd_init_cctx()`, `zstd_compress_cctx()`, advanced context creation/free, dictionary creation/free, and `zstd_compress_using_cdict()`. Single-pass decompression mirrors this with `zstd_dctx_workspace_bound()`, `zstd_init_dctx()`, `zstd_decompress_dctx()`, advanced dctx/ddict APIs, and `zstd_decompress_using_ddict()`. Streaming APIs include cstream/dstream workspace bounds, init/reset, `zstd_compress_stream()`, `zstd_flush_stream()`, `zstd_end_stream()`, and `zstd_decompress_stream()`. Inspection and advanced compression include `zstd_find_frame_compressed_size()`, `zstd_get_frame_header()`, `zstd_register_sequence_producer()`, and `zstd_compress_sequences_and_literals()`.

## Control Flow
Workspace-mode callers compute a bound for chosen parameters, allocate workspace, initialize a context inside that workspace, call compression/decompression, then free the workspace when the context is no longer used. Advanced allocation-mode callers create contexts or dictionaries with `zstd_custom_mem` and free them explicitly. Streaming compression initializes a stream with parameters and optional pledged source size, feeds buffers until input is consumed, flushes as needed, and calls `zstd_end_stream()` until it returns zero. Streaming decompression initializes with a maximum window, loops over input/output buffers, and treats return zero as a fully decoded and flushed frame.

## State and Persistence
Contexts, streams, and dictionaries persist compression tables, window state, frame state, loaded dictionaries, and custom allocator ownership. By-reference dictionary APIs require the dictionary buffer to outlive the dictionary object. Streaming input/output buffers carry mutable `pos` fields. Workspace-backed contexts are valid only while the caller-provided workspace remains alive and sufficiently sized.

## Dependencies and Integration Points
Depends on Linux types, `linux/zstd_errors.h`, and `linux/zstd_lib.h`. Integrates with kernel filesystems, initramfs and module compression, Btrfs/EROFS/SquashFS-style compressed data paths, dictionary users, and code that needs frame metadata or external sequence production.

## Risks
Almost all size-returning functions can encode errors and must be checked with `zstd_is_error()`. Workspace bounds must match the actual parameters and external-sequence usage; too-small workspaces fail at init or operation time. Decompression without a known output bound should use streaming APIs. Maximum window limits are critical for untrusted data. By-reference dictionaries create lifetime hazards. Streaming callers must continue flush/end loops until zero and must honor partial input consumption.

## Test Signals
Signals include zstd known-vector compression/decompression, workspace-bound tests across levels and strategies, dictionary lifetime tests, streaming partial-buffer tests, max-window rejection, frame-header/skippable-frame inspection tests, external sequence producer tests, and fuzzing corrupt frames with error-code validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zstd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zstd_errors.h -->
# sources/distributed-fs/ceph-client/include/linux/zstd_errors.h

## Purpose
Defines the exported Zstandard error-code enum and symbol-visibility macros used by the kernel zstd wrapper. It is the stable error taxonomy consumed by `zstd_is_error()`, `zstd_get_error_code()`, and error-name helpers.

## Important APIs, Types, and Functions
Visibility macros are `ZSTDERRORLIB_VISIBLE`, `ZSTDERRORLIB_HIDDEN`, and `ZSTDERRORLIB_API`. `typedef enum ZSTD_ErrorCode` lists stable and unstable zstd errors, including no error, generic failure, unknown prefix, unsupported version/frame parameters, window too large, corruption, checksum failure, literal and dictionary errors, unsupported or out-of-bound parameters, table/symbol limits, wrong stage or missing init, allocation/workspace failures, destination/source size issues, null destination, and no-forward-progress conditions. `ZSTD_getErrorString()` maps an enum code to a string.

## Control Flow
No runtime control flow is implemented in the header. Callers receive size-like return values from zstd APIs, test them with the wrapper error predicate, translate to `ZSTD_ErrorCode`, and optionally format the code through `ZSTD_getErrorString()` or higher-level name helpers.

## State and Persistence
No state is owned. The enum values are part of the static API contract. Values below 100 are documented as stable; later values are explicitly not stable and may change.

## Dependencies and Integration Points
Used by `linux/zstd.h` and upstream-derived zstd library internals. Integrates with kernel error reporting, compression/decompression callers, and any tests comparing zstd error categories.

## Risks
Code must prefer enum names and `ZSTD_isError()`-style predicates over hard-coded numeric values, especially for library versions before stable value pinning or for codes at 100 and above. The header notes static-linking assumptions and no official dynamic-linking support, so it should not be treated as a cross-library ABI independent of the bundled zstd version.

## Test Signals
Signals include error-code mapping tests, corrupt frame and bad-parameter tests that produce expected enum names, build coverage for visibility macros, and checks that callers do not persist unstable numeric error values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zstd_errors.h -->
