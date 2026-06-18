# subset-b-005851 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/damon.h -->
# sources/distributed-fs/ceph-client/include/linux/damon.h

Purpose: Defines the public in-kernel DAMON API for data access monitoring contexts, targets, regions, access-pattern based operation schemes, quotas, watermarks, filters, and operation backends. It is the contract between DAMON core code, DAMON operation implementations, sysfs/debugfs control surfaces, and kernel users that start or manipulate monitoring contexts.

Important APIs, types, and functions: Core types include `struct damon_ctx`, `damon_attrs`, `damon_operations`, `damon_target`, `damon_region`, `damos`, `damos_quota`, `damos_watermarks`, `damos_filter`, `damos_walk_control`, and `damon_call_control`. Enumerations define operation IDs (`DAMON_OPS_VADDR`, `DAMON_OPS_FVADDR`, `DAMON_OPS_PADDR`), DAMOS actions, quota goal metrics/tuners, watermark metrics, and filter types. Public helpers allocate/destroy/add/commit regions, targets, schemes, filters, quota goals, and contexts; register/select operation backends; start/stop kdamond contexts; invoke `damon_call()` and `damos_walk()`; and set default physical address monitoring ranges. Iteration macros cover targets, regions, schemes, quota goals, and filter lists.

Control flow: Callers create a context, select an operations backend, attach targets and schemes, set monitoring intervals/region bounds, then call `damon_start()`. The kdamond thread periodically asks operations to prepare/check/update access state, aggregates region access counters, adjusts regions, applies eligible DAMOS actions subject to pattern, filter, watermark, interval, and quota rules, and services asynchronous `damon_call()` and `damos_walk()` requests. Non-kdamond users must use these safe APIs while monitoring is running.

State and persistence: State is entirely in-memory: target region lists, sampled addresses, access rates, ages, scheme quota counters, watermarks, statistics, call-control queues, walk-control state, kdamond task pointer, and operation callbacks. There is no direct persistence; userspace-facing DAMON subsystems may serialize configuration elsewhere. Private fields track interval ratios, quota feedback loop state, throughput estimates, region score histograms, and possible corruption after failed context commits.

Dependencies and integration points: Depends on memory control IDs, mutex/completion/list primitives, random sampling, task PIDs, and page-sized address alignment. Integrates with MM reclamation/pageout/migration/madvise logic through operation-specific `apply_scheme()`, with PSI and memcg metrics for quota goals, and with VFS/sysfs/debugfs frontends that configure DAMON.

Risks and test signals: Risks include invalid interval ratios, region list corruption, unsafe direct context access while kdamond runs, stale target PIDs, quota overflow or unfair prioritization, unsupported action/filter combinations per operation backend, and failure to cleanly stop kdamond threads. Test by starting/stopping multiple contexts, committing replacement targets/schemes, changing intervals while active, using all operation IDs, exercising quotas/watermarks/filters, walking schemes concurrently, and validating access-rate/age behavior across aggregation boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/damon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dasd_mod.h -->
# sources/distributed-fs/ceph-client/include/linux/dasd_mod.h

Purpose: Exposes the minimal DASD block-device information hook needed outside the s390 DASD driver implementation.

Important APIs, types, and functions: Includes `<asm/dasd.h>`, forward-declares `struct gendisk`, and declares `dasd_biodasdinfo(struct gendisk *disk, dasd_information2_t *info)`.

Control flow: A caller with a DASD-backed `gendisk` supplies an output `dasd_information2_t`; the architecture DASD implementation fills device information. The header itself contains no inline logic and is guarded by `DASD_MOD_H`.

State and persistence: No state is stored here. Persistent or runtime DASD state lives in the block driver and the architecture-specific DASD definitions.

Dependencies and integration points: Ties generic block-layer code to the s390 DASD ABI. It depends on `struct gendisk` identity and `dasd_information2_t` layout from architecture headers.

Risks and test signals: Risks are ABI/layout drift in `dasd_information2_t`, calls on non-DASD disks, and missing architecture support. Test through DASD ioctl/info paths on s390 builds and by compiling non-s390 configurations that include the header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dasd_mod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/davinci_emac.h -->
# sources/distributed-fs/ceph-client/include/linux/davinci_emac.h

Purpose: Provides legacy platform-data structures for TI DaVinci EMAC and MDIO devices.

Important APIs, types, and functions: Defines `struct mdio_platform_data` with `bus_freq`, `struct emac_platform_data` with MAC address, control/RAM offsets, hardware RAM address/size, PHY selector, RMII/version flags, no-BD-RAM flag, and board interrupt enable/disable callbacks. Version constants distinguish DM644x (`EMAC_VERSION_1`) and DM646x (`EMAC_VERSION_2`).

Control flow: Board or platform setup code populates these structures before registering EMAC/MDIO platform devices. The network driver later reads the fields to select PHY behavior, register layout, memory placement, and interrupt handling callbacks.

State and persistence: The structures describe static board state. Runtime link state, DMA rings, statistics, and PHY state are owned by the EMAC/MDIO drivers.

Dependencies and integration points: Depends on Ethernet address sizing and NVMEM consumer infrastructure. Integrates with platform-device registration, PHY/MDIO selection, SoC control-module addressing, and board-specific interrupt glue.

Risks and test signals: Risks include malformed `phy_id` strings, wrong register offsets for the SoC version, invalid MAC addresses, and callback lifetime bugs. Test board boot, PHY auto-selection and fixed 100/full mode, RMII mode, interrupt masking/unmasking, and MAC address sourcing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/davinci_emac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dax.h -->
# sources/distributed-fs/ceph-client/include/linux/dax.h

Purpose: Defines the kernel API for Direct Access devices and filesystem-DAX mappings, including direct PFN access, writeback, poison recovery, layout breaking, iomap I/O/fault integration, and hmem resource enumeration.

Important APIs, types, and functions: Key types are `dax_entry_t`, `struct dax_device`, `enum dax_access_mode`, `struct dax_operations`, and `struct dax_holder_operations`. Device APIs include `alloc_dax()`, `put_dax()`, `kill_dax()`, `dax_dev_get()`, cache/synchronous/nocache/nomc setters, `dax_direct_access()`, copy/zero/recovery helpers, holder failure notification, and read locking. Filesystem APIs include `fs_dax_get_by_bdev()`, `fs_dax_get()`, `fs_put_dax()`, `dax_writeback_mapping_range()`, busy-page queries, mapping-entry locks, `dax_iomap_rw()`, `dax_iomap_fault()`, `dax_finish_sync_fault()`, mapping entry deletion/invalidation, `dax_break_layout()`, dedupe/remap prep, and zero/truncate/unshare helpers.

Control flow: Device providers register operations that translate logical page offsets to physical addresses and optionally recover poisoned storage. Filesystems acquire a DAX device for a block device and holder, verify synchronous mapping support for `MAP_SYNC`, then use iomap-backed paths for reads, writes, faults, zeroing, and remap preparation. Layout-breaking helpers coordinate with pages or exceptional entries before operations that cannot race with DAX mappings.

State and persistence: The header exposes state owned elsewhere: DAX device lifetime, holders, cache policy, poison recovery ability, radix/xarray mapping entries, and hmem resources. Persistent data is the underlying pmem/block media; this API bypasses page cache persistence semantics and relies on flush/writeback hooks.

Dependencies and integration points: Integrates with VFS inodes, address spaces, iomap, block devices, writeback control, memory failure, folios/pages, VM faults, dev_dax/hmem, and filesystem reflink/dedupe paths. Config-gated stubs keep non-DAX builds compiling while returning `-EOPNOTSUPP`, `-ENODEV`, or inert defaults.

Risks and test signals: Risks include allowing synchronous mappings on non-synchronous devices, stale DAX mappings during truncate/reflink, incorrect poison error translation, missing cache flushes, and use-after-kill of `dax_device`. Test fs-DAX mount and `MAP_SYNC`, direct I/O and mmap faults, media poison recovery, truncate/hole-punch/remap races, writeback/invalidate paths, DAX-disabled builds, and hmem registration/enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dax.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dca.h -->
# sources/distributed-fs/ceph-client/include/linux/dca.h

Purpose: Declares the Direct Cache Access provider/requester API used by PCI devices and platforms that support CPU-cache-targeted DMA hints.

Important APIs, types, and functions: Defines notifier events `DCA_PROVIDER_ADD` and `DCA_PROVIDER_REMOVE`, `struct dca_provider`, `struct dca_domain`, and `struct dca_ops` callbacks for requester add/remove, tag lookup, and device-management checks. Provider APIs allocate, free, register, unregister, and expose private storage via `dca_priv()`. Requester APIs add/remove devices and get CPU tags through `dca_get_tag()`/`dca3_get_tag()`. Internal sysfs helpers create provider/requester attributes.

Control flow: A hardware provider registers with DCA ops and a device, requesters attach if they share a compatible domain/root complex, and data paths query CPU tags for DMA steering. Notifiers announce provider availability changes to interested subsystems.

State and persistence: Runtime state consists of provider/domain lists, provider IDs, requester slots, and sysfs entries. There is no persistent state.

Dependencies and integration points: Depends on PCI bus topology and generic device/sysfs infrastructure. It integrates with DCA-capable NIC/storage drivers and provider drivers that implement hardware tag programming.

Risks and test signals: Risks include matching requesters to the wrong PCI domain, stale sysfs/requester entries after provider removal, CPU hotplug tag issues, and provider private-data sizing mistakes. Test provider add/remove, requester lifecycle, tag lookup across CPUs, sysfs visibility, and builds with DCA consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dcache.h -->
# sources/distributed-fs/ceph-client/include/linux/dcache.h

Purpose: Defines the VFS dentry cache data structures and public dcache helpers used by filesystems, path lookup, mount handling, aliasing, pruning, and overlay/stacked filesystem interactions.

Important APIs, types, and functions: Core types are `struct qstr`, `union shortname_store`, `struct dentry`, `struct dentry_operations`, `enum dentry_flags`, and `struct name_snapshot`. Extern APIs allocate and attach dentries (`d_alloc*`, `d_instantiate*`, `d_add`, `d_splice_alias`, `d_obtain_alias/root`), hash/unhash and move them (`d_rehash`, `d_drop`, `d_move`, `d_exchange`), search aliases/lookups, shrink/prune caches, create roots/tmpfiles, build paths, and snapshot names. Inline helpers cover refcounts (`dget`, `dget_dlock`, `dput`), hashed/unlinked state, lookup completion, mount/managed flags, type checks, inode access, real/backing inode lookup, and child/sibling iteration.

Control flow: Filesystem lookup code allocates or finds a dentry keyed by parent and `qstr`, validates via optional `dentry_operations`, instantiates positive or negative results, and later pathwalk uses flags and operations for revalidation, automount, transit management, and real-dentry resolution. Refcounting, RCU lookup fields, lockref, seqlock, rename lock, hash lists, LRU lists, alias lists, and child lists coordinate lookup, rename, prune, and reclaim.

State and persistence: Dentries are an in-memory cache only. They persist while referenced, hashed, pinned as roots/mountpoints, or protected by filesystem flags. Names may be inline or external; positive dentries alias inodes while negative dentries cache misses. Filesystems may attach `d_fsdata` and callbacks but on-disk persistence remains with inode/filesystem code.

Dependencies and integration points: Depends on locks, RCU, hlist/list, string hashing, wait queues, lockref, inodes, superblocks, files, paths, and mounts. It is central to VFS path resolution, NFS export reconnects, overlay real inode handling, fsnotify parent watch flags, tmpfiles, and shrinker pressure.

Risks and test signals: Risks include incorrect refcount use on zero-count dentries, RCU lookup races, mis-set entry type flags, stale negative dentries, aliasing bugs for exportable filesystems, rename/mountpoint races, and misuse of `d_backing_inode()` by normal filesystems. Test parallel lookup and rename, negative-to-positive transitions, shrink under pressure, mountpoint/autofs handling, overlay `d_real()`, NFS disconnected dentries, encrypted no-key names, tmpfile creation, and lockdep on nested dentry locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dccp.h -->
# sources/distributed-fs/ceph-client/include/linux/dccp.h

Purpose: Supplies small kernel helpers for interpreting DCCP packet headers on top of the UAPI DCCP definitions.

Important APIs, types, and functions: Inline helpers are `dccp_hdrx()`, `__dccp_basic_hdr_len()`, `dccp_hdr_seq()`, and `__dccp_hdr_len()`. They consume `struct dccp_hdr`, optional `struct dccp_hdr_ext`, and `dccp_packet_hdr_len()`.

Control flow: Callers inspect the DCCP X bit to decide whether an extended sequence header follows the base header. Sequence extraction builds either a 48-bit extended sequence from high and low fields or a short sequence from base fields. Header length combines base/extension length and packet-type-specific header length.

State and persistence: No state is stored. The helpers decode transient packet bytes.

Dependencies and integration points: Depends on `<uapi/linux/dccp.h>` layout and network byte-order helpers. Used by DCCP protocol parsing, skb validation, and congestion/control-path code.

Risks and test signals: Risks include using helpers before ensuring the skb contains enough linear header bytes, endian mistakes, and malformed X-bit/header-length combinations. Test short and extended DCCP headers, each packet type, truncated skb paths, and sequence number boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dccp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/debug_locks.h -->
# sources/distributed-fs/ceph-client/include/linux/debug_locks.h

Purpose: Declares global lock-debugging controls and wrappers used by lockdep and related debug code to report locking bugs once and then disable further lock debugging.

Important APIs, types, and functions: Exposes `debug_locks`, `debug_locks_silent`, `__debug_locks_off()`, `debug_locks_off()`, `DEBUG_LOCKS_WARN_ON()`, `SMP_DEBUG_LOCKS_WARN_ON()`, optional `locking_selftest()`, and lockdep helpers `debug_show_all_locks()`, `debug_show_held_locks()`, `debug_check_no_locks_freed()`, and `debug_check_no_locks_held()`.

Control flow: A debug check calls `DEBUG_LOCKS_WARN_ON(condition)`. If the system is not already in an oops and the condition is true, instrumentation is bracketed, `debug_locks_off()` atomically disables further lock debugging, and a warning is emitted unless silenced. SMP and lockdep-specific helpers compile to no-ops when unavailable.

State and persistence: Global in-memory state records whether lock debugging remains active and whether warnings should be silent. No persistence exists beyond logs.

Dependencies and integration points: Depends on atomic exchange, cacheline read-mostly storage, instrumentation guards, `oops_in_progress`, WARN infrastructure, SMP config, lockdep, and locking selftests.

Risks and test signals: Risks include disabling diagnostics too early, warning from unsafe instrumentation contexts, missing no-op coverage on non-lockdep builds, and false positives from freed-lock memory. Test lockdep selftests, SMP-only warnings, non-SMP builds, lock-free checks during object freeing, and repeated failure suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/debug_locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/debugfs.h -->
# sources/distributed-fs/ceph-client/include/linux/debugfs.h

Purpose: Defines the debugfs public API for creating transient kernel debugging files, directories, attributes, simple value nodes, blobs, register dumps, arrays, automounts, and cancellation-aware file operations.

Important APIs, types, and functions: Types include `debugfs_blob_wrapper`, `debugfs_reg32`, `debugfs_regset32`, `debugfs_u32_array`, `debugfs_short_fops`, `debugfs_automount_t`, and `debugfs_cancellation`. Creation APIs cover full and short file operations via `_Generic` `debugfs_create_file()`, auxiliary data, unsafe files, file sizing, dirs, symlinks, automounts, scalar value files, strings, bools, blobs, regsets, u32 arrays, devm seqfiles, and xul helpers. Removal and lookup APIs include `debugfs_remove()`, `debugfs_lookup_and_remove()`, `debugfs_lookup()`, `debugfs_file_get/put()`, and `debugfs_change_name()`.

Control flow: Callers create a debugfs hierarchy and normally ignore `ERR_PTR()` failures because debugfs is optional. On open/read/write, helpers expose `inode->i_private`, auxiliary pointers, simple-attr parsing, or custom fops. Cancellation APIs allow file operations to register cleanup callbacks while userspace holds a file. Disabled builds return `ERR_PTR(-ENODEV)` or no-op stubs.

State and persistence: Debugfs entries are in-memory dentries/inodes under the debugfs mount and disappear on removal or module unload. They expose live kernel variables or callbacks, not stable ABI. Auxiliary data and value pointers must outlive the file unless protected by removal/cancellation.

Dependencies and integration points: Depends on VFS, seq_file, simple_attr, devices for devm seqfiles and runtime-PM register dumps, and architecture debugfs root directories. Integrates with drivers and subsystems for non-ABI diagnostics.

Risks and test signals: Risks include treating debugfs as stable userspace ABI, exposing writable unsafe state, stale pointers after module/device removal, failing to remove entries, and assuming debugfs exists. Test with `CONFIG_DEBUG_FS=y/n`, module unload while files are open, scalar read/write parsing, regset runtime PM behavior, recursive removal, and cancellation callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/debugobjects.h -->
# sources/distributed-fs/ceph-client/include/linux/debugobjects.h

Purpose: Declares the debugobjects framework interface for tracking lifecycle state of selected kernel object types and catching init/activate/deactivate/destroy/free misuse.

Important APIs, types, and functions: Defines `enum debug_obj_state`, `struct debug_obj`, and `struct debug_obj_descr`. Public functions include `debug_object_init()`, `debug_object_init_on_stack()`, `debug_object_activate()`, `debug_object_deactivate()`, `debug_object_destroy()`, `debug_object_free()`, `debug_object_assert_init()`, `debug_object_active_state()`, `debug_objects_early_init()`, `debug_objects_mem_init()`, and optional `debug_check_no_obj_freed()`.

Control flow: Instrumented object users describe a type with callbacks for hints, static-object detection, and fixups. Lifecycle sites call debugobjects functions; the framework validates transitions through init, inactive, active, destroyed, and not-available states and may invoke fixups. In disabled builds the calls compile to no-ops.

State and persistence: Debug state is maintained in framework-owned in-memory hash/list entries; `struct debug_obj` references the tracked object address, descriptor, state, and active substate. No persistent state exists.

Dependencies and integration points: Depends on hlist/list and spinlocks. Used by timers, workqueues, RCU, and other debug-instrumented object types, with free-memory checking when enabled.

Risks and test signals: Risks include descriptor callbacks with side effects, false positives for static or stack objects, unbalanced active-state transitions, and build differences hiding bugs when disabled. Test lifecycle misuse injection, object free checking, on-stack objects, static objects, early boot init, and active-state expect/next transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/debugobjects.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/bunzip2.h -->
# sources/distributed-fs/ceph-client/include/linux/decompress/bunzip2.h

Purpose: Declares the bzip2 decompressor entry point used by kernel image, initramfs, or ramdisk decompression code.

Important APIs, types, and functions: Exports `bunzip2()` with common decompressor arguments: optional input buffer and length, streaming `fill` callback, streaming `flush` callback, output buffer, consumed-position pointer, and error callback.

Control flow: The caller either passes preloaded compressed input with nonzero `len` or supplies a `fill` callback for streaming input. Output is either written to a caller buffer or emitted through `flush`, following the generic decompressor contract.

State and persistence: No state is declared in the header. Decoder state and temporary buffers live inside the decompressor implementation and caller-provided storage.

Dependencies and integration points: Shares the signature defined by `decompress/generic.h`, allowing format selection code to call bzip2 uniformly with gzip, LZ4, LZMA, LZO, XZ, and ZSTD.

Risks and test signals: Risks include mismatched fill/flush semantics, invalid output sizing, and poor error propagation in early boot where allocators differ. Test preloaded and streaming bzip2 initramfs inputs, corrupt streams, position reporting, and early-boot decompression builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/bunzip2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/generic.h -->
# sources/distributed-fs/ceph-client/include/linux/decompress/generic.h

Purpose: Defines the common decompressor function signature and magic-detection helper used by kernel decompression frontends.

Important APIs, types, and functions: `decompress_fn` standardizes arguments for all supported decompressors. `decompress_method(const unsigned char *inbuf, long len, const char **name)` inspects input bytes and returns the matching decompressor and optional method name.

Control flow: Callers probe compressed data with `decompress_method()`, then invoke the returned function using either preloaded input (`len != 0`, `fill == NULL`) or streaming input (`len == 0`, optional allocated input buffer and repeated `fill` calls). Output is buffered directly when `flush == NULL` or emitted via `flush` when streaming output is needed.

State and persistence: This header owns no state. Position reporting through `posp` is caller-visible transient state.

Dependencies and integration points: Integrates all format-specific headers under a shared boot/initramfs decompression interface. Implementations rely on early boot or kernel allocation helpers from `decompress/mm.h`.

Risks and test signals: Risks include wrong magic detection with short buffers, violating the `len`/`fill` contract, and buffer sizing mistakes for streaming modes. Test every supported compression magic, empty/truncated buffers, preloaded versus callback input, flush output mode, and `posp` accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/inflate.h -->
# sources/distributed-fs/ceph-client/include/linux/decompress/inflate.h

Purpose: Declares the gzip/inflate decompressor entry point for kernel decompression users.

Important APIs, types, and functions: Exports `gunzip()` with the common decompressor signature: input buffer/length, `fill`, `flush`, output buffer, consumed-position pointer, and error callback.

Control flow: The gzip implementation consumes either preloaded input or callback-provided input and writes decompressed bytes to the caller buffer or flush callback. Errors are reported through the supplied `error_fn`.

State and persistence: No state is held in the header. Inflate state is temporary inside the implementation.

Dependencies and integration points: Participates in the generic decompression method table and early boot/initramfs loading paths.

Risks and test signals: Risks include truncated gzip streams, CRC/header handling mismatches, callback contract violations, and early allocator differences. Test compressed kernel/initramfs gzip images, corrupt headers, short reads, flush-only output, and consumed-position reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/inflate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/mm.h -->
# sources/distributed-fs/ceph-client/include/linux/decompress/mm.h

Purpose: Provides allocation wrappers for decompressor code in two environments: early/pre-boot static decompression and normal in-kernel ramdisk decompression.

Important APIs, types, and functions: In `STATIC` builds it defines `malloc_ptr`, `malloc_count`, `malloc()`, `free()`, `large_malloc()`, `large_free()`, `STATIC_RW_DATA`, `MALLOC_VISIBLE`, and `INIT`. In normal builds it maps `malloc/free` to `kmalloc/kfree`, large allocation to `vmalloc/vfree`, marks `INIT` as `__init`, and defines `STATIC`.

Control flow: Early boot allocation starts from external `free_mem_ptr`, aligns allocations to eight bytes, advances a bump pointer, checks `free_mem_end_ptr` when available, and resets the pointer only when nested allocation count returns to zero. Normal kernel code uses slab/vmalloc allocators.

State and persistence: Early boot mode maintains global allocator cursor and allocation nesting count. Allocations are temporary for decompression; no persistent state is intended.

Dependencies and integration points: Depends on boot decompressor-provided `free_mem_ptr/free_mem_end_ptr` in static mode and on kernel memory APIs in normal mode. Included by format implementations to avoid duplicating environment-specific allocation logic.

Risks and test signals: Risks include early memory overflow, negative size handling, allocation nesting leaks preventing pointer reset, and accidental local data where an architecture needs relocatable pre-boot code. Test static decompressor builds, bounded free-memory regions, nested allocations/frees, large allocation users, and normal initramfs decompression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/unlz4.h -->
# sources/distributed-fs/ceph-client/include/linux/decompress/unlz4.h

Purpose: Declares the LZ4 decompressor entry point under the generic kernel decompression ABI.

Important APIs, types, and functions: Exports `unlz4()` with input buffer/length, `fill`, `flush`, output buffer, input position pointer, and error callback.

Control flow: Callers invoke `unlz4()` after magic detection or explicit LZ4 selection; the implementation streams input/output according to the shared decompressor contract.

State and persistence: The header declares no state. Temporary decoder state is implementation-local.

Dependencies and integration points: Integrates with kernel image and initramfs decompression, `decompress_method()`, and `decompress/mm.h` allocation wrappers.

Risks and test signals: Risks include malformed block handling, output-size assumptions, and early-boot callback behavior. Test LZ4-compressed kernel/initramfs data, corrupt streams, streaming input, flush output, and position accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/unlz4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/unlzma.h -->
# sources/distributed-fs/ceph-client/include/linux/decompress/unlzma.h

Purpose: Declares the LZMA decompressor entry point for kernel decompression paths.

Important APIs, types, and functions: Exports `unlzma()` with the shared decompressor arguments, including input callbacks, output buffer/flush callback, consumed-position pointer, and error callback.

Control flow: The LZMA decoder is selected by magic or caller choice, then consumes preloaded or streamed input and emits output through the common ABI. The header allows generic decompression code to call it uniformly.

State and persistence: No header-owned state. LZMA dictionaries and temporary memory are allocated by the implementation via decompressor memory wrappers.

Dependencies and integration points: Works with `decompress/generic.h` and `decompress/mm.h` in boot and runtime initramfs contexts.

Risks and test signals: Risks include high memory use in early boot, malformed dictionary properties, truncated input, and incorrect `posp` reporting. Test valid and corrupt LZMA streams, minimal-memory boot configurations, callback input, direct output buffer mode, and error callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/unlzma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/unlzo.h -->
# sources/distributed-fs/ceph-client/include/linux/decompress/unlzo.h

Purpose: Declares the LZO decompressor entry point for kernel image, initramfs, and ramdisk loading paths.

Important APIs, types, and functions: Exports `unlzo()` with the generic decompressor ABI.

Control flow: The caller provides preloaded or callback-supplied compressed input and receives decompressed output via buffer or flush callback. Errors are reported through the supplied error function.

State and persistence: No state is held by the header; decompressor-local state is temporary.

Dependencies and integration points: Integrates with generic decompressor selection and the allocation behavior defined in `decompress/mm.h`.

Risks and test signals: Risks include malformed LZO block sizes, buffer overrun on direct output, short read handling, and early boot allocation constraints. Test valid LZO initramfs images, corrupt block headers, streaming reads, flush writes, and position tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/unlzo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/unxz.h -->
# sources/distributed-fs/ceph-client/include/linux/decompress/unxz.h

Purpose: Declares the XZ decompressor wrapper for kernel, initramfs, and initrd decompression.

Important APIs, types, and functions: Exports `unxz(unsigned char *in, long in_size, fill, flush, unsigned char *out, long *in_used, error)` using the same streaming shape as the generic decompressor ABI.

Control flow: XZ input may be preloaded or supplied through `fill`; output is written to `out` or emitted through `flush`. `in_used` reports consumed bytes for callers that need trailer or concatenated data handling.

State and persistence: The header owns no state. Decoder dictionaries and stream state live inside the implementation and allocation wrappers.

Dependencies and integration points: Used by generic decompressor selection and boot/initramfs loaders. The SPDX license differs (`0BSD`) because this wrapper follows upstream XZ decompressor licensing.

Risks and test signals: Risks include dictionary memory pressure, unsupported XZ options in early boot, truncated streams, and error propagation. Test XZ-compressed kernel/initramfs images, corrupt headers, large dictionary rejection, streaming input, and `in_used` accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/unxz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/unzstd.h -->
# sources/distributed-fs/ceph-client/include/linux/decompress/unzstd.h

Purpose: Declares the Zstandard decompressor entry point for kernel decompression users.

Important APIs, types, and functions: Exports `unzstd()` with common arguments for input buffer/length, `fill`, `flush`, output buffer, input-position pointer, and error callback.

Control flow: Generic decompression code selects ZSTD by magic and invokes this entry point. The implementation handles either preloaded or streaming input and direct or flushed output.

State and persistence: No state is declared in the header. ZSTD frame/window state is temporary in the implementation.

Dependencies and integration points: Integrates with `decompress/generic.h`, boot/initramfs loading code, and decompressor memory allocation wrappers.

Risks and test signals: Risks include large window requirements, malformed frame handling, short callback reads, and output-size mismatches. Test ZSTD kernel/initramfs images, invalid frames, streaming modes, low-memory boot decompression, and position reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/decompress/unzstd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/delay.h -->
# sources/distributed-fs/ceph-client/include/linux/delay.h

Purpose: Defines kernel delay and sleep helpers ranging from calibrated busy waits to flexible sleeps that choose an appropriate delay mechanism.

Important APIs, types, and functions: Exposes `loops_per_jiffy`, `lpj_fine`, architecture `udelay()` integration, `mdelay()`, `ndelay()`, `calibrate_delay()`, `calibrate_delay_is_known()`, weak `calibration_delay_done()`, `msleep()`, `msleep_interruptible()`, `usleep_range_state()`, `usleep_range()`, `usleep_range_idle()`, `ssleep()`, and `fsleep()`.

Control flow: `mdelay()` uses direct `udelay()` for small compile-time constants and loops millisecond chunks otherwise to avoid overflow. `ndelay()` rounds to microseconds if an architecture does not provide native nanosecond delay. `fsleep()` busy-waits for very short sleeps, uses `usleep_range()` when jiffy-based `msleep()` would exceed the target slack, and otherwise uses `msleep()`.

State and persistence: Calibration state is held in global loop-per-jiffy values. Sleep functions do not persist state beyond scheduler/timer state.

Dependencies and integration points: Depends on architecture delay loops, scheduler task states, jiffies, math helpers, hrtimer/timer behavior, and boot-time calibration.

Risks and test signals: Risks include busy-waiting too long in sleepable contexts, inaccurate calibration, overflow on high bogomips systems, and unexpected load-average effects. Test delay calibration, `fsleep()` boundaries, interruptible sleeps, idle sleeps, non-high-res timer kernels, and architecture overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/delayacct.h -->
# sources/distributed-fs/ceph-client/include/linux/delayacct.h

Purpose: Defines per-task delay accounting storage and fast-path wrappers for collecting delays caused by block I/O, swapin, reclaim, thrashing, compaction, write-protect copy, and IRQ/softirq time.

Important APIs, types, and functions: Under `CONFIG_TASK_DELAY_ACCT`, `struct task_delay_info` stores starts, min/max/total delays, counts, timestamps of max delays, and a raw spinlock. APIs include task init/exit/free, taskstats export, block-I/O ticks, start/end wrappers for each delay category, and IRQ delay charging. A static key `delayacct_key`, `delayacct_on`, and `delayacct_cache` gate allocation and fast-path overhead.

Control flow: Fork/task init clears inherited delay pointers and allocates accounting state if enabled. Delay sites call start/end wrappers; wrappers first check the static branch and `task->delays` before calling out-of-line accounting functions. Taskstats export copies accumulated values to userspace structures.

State and persistence: State is per-task in memory and freed when the task exits or fork fails. Values are cumulative nanoseconds and counts, with min/max tracking for selected categories. Persistence is only via taskstats snapshots delivered to userspace.

Dependencies and integration points: Depends on taskstats UAPI, scheduler task state, slab cache, jump labels/static keys, raw spinlocks, and memory-management/block-I/O instrumentation sites.

Risks and test signals: Risks include start/end imbalance, static-key overhead regressions, inherited pointer reuse after fork, racey export without locking, and missed accounting when `current->delays` is absent. Test with `CONFIG_TASK_DELAY_ACCT=y/n`, enabling/disabling accounting, taskstats reads, block I/O waits, reclaim/thrashing/compaction paths, fork/exit stress, and IRQ delay charging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/delayacct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/delayed_call.h -->
# sources/distributed-fs/ceph-client/include/linux/delayed_call.h

Purpose: Provides a tiny closure-like helper for storing a callback and argument to execute later.

Important APIs, types, and functions: Defines `struct delayed_call`, `DEFINE_DELAYED_CALL(name)`, `set_delayed_call()`, `do_delayed_call()`, and `clear_delayed_call()`.

Control flow: A caller initializes or defines a `delayed_call`, stores a function and argument with `set_delayed_call()`, and later invokes it with `do_delayed_call()` if a function is present. `clear_delayed_call()` disables future invocation without touching the argument.

State and persistence: State is just the callback pointer and opaque argument stored in caller-owned memory. There is no synchronization or ownership management.

Dependencies and integration points: Used by VFS-style interfaces that need to return cleanup actions or deferred release functions without a full object. It has no external dependencies beyond basic C types.

Risks and test signals: Risks include dangling arguments, double invocation when callers forget to clear, lack of type checking for the `void *` argument, and missing locking if shared across threads. Test paths that set and execute cleanup callbacks, no-callback cases, and error paths that clear or transfer ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/delayed_call.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dev_printk.h -->
# sources/distributed-fs/ceph-client/include/linux/dev_printk.h

Purpose: Defines device-scoped printk helpers that attach subsystem/device identity to kernel logs and provide once, ratelimited, dynamic-debug, WARN, and probe-error variants.

Important APIs, types, and functions: Defines `struct dev_printk_info`, `dev_vprintk_emit()`, `dev_printk_emit()`, `_dev_printk()` and level-specific `_dev_*()` functions when printk is enabled. Macros include `dev_printk()`, `dev_no_printk()`, `dev_emerg/alert/crit/err/warn/notice/info/dbg`, once and ratelimited variants, `dev_vdbg`, `dev_WARN`, `dev_WARN_ONCE`, `dev_err_probe()`, `dev_warn_probe()`, `dev_err_ptr_probe()`, and `dev_err_cast_probe()`.

Control flow: Device log macros emit printk index metadata, apply `dev_fmt()`, and call level-specific emitters. `dev_dbg()` routes through dynamic debug, unconditional debug, or compile-time checked no-op depending on configuration. Once macros use static booleans; ratelimited macros use static ratelimit state. Probe helpers normalize deferred-probe logging and return the original error for convenient propagation.

State and persistence: Log state includes static once flags, ratelimit buckets, dynamic-debug descriptors, and emitted printk records. No driver state is persisted.

Dependencies and integration points: Depends on printk, dynamic debug, ratelimit, WARN, `dev_name()`, and `dev_driver_string()` from the driver core. Integrated across nearly all device drivers for diagnostics.

Risks and test signals: Risks include format-string mistakes, log flooding when ratelimit is bypassed, missing output with `CONFIG_PRINTK=n`, dereferencing invalid `struct device`, and noisy deferred-probe logs. Test compile-time format checking, dynamic debug enablement, ratelimited suppression, once-only output, probe deferral paths, and no-printk builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dev_printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devcoredump.h -->
# sources/distributed-fs/ceph-client/include/linux/devcoredump.h

Purpose: Declares the device coredump API that lets drivers expose crash dump data to userspace for a bounded time after device/firmware failures.

Important APIs, types, and functions: Defines `DEVCD_TIMEOUT`, `_devcd_free_sgtable()`, `dev_coredumpv()`, `dev_coredumpm_timeout()`, `dev_coredumpsg()`, `dev_coredump_put()`, and convenience `dev_coredumpm()`.

Control flow: Drivers submit dumps as vmalloc buffers, custom read/free callbacks, or scatterlists. The framework creates a device coredump object, exposes it for userspace reads, and frees data after read or timeout. If devcoredump support is disabled, stubs immediately free the provided buffer or scatterlist.

State and persistence: Coredump data is transient and normally expires after five minutes if unread. `_devcd_free_sgtable()` frees pages and chained scatterlist tables. The framework owns data lifetime after submission.

Dependencies and integration points: Depends on device core, modules for owner pinning, vmalloc/slab, scatterlists, pages, and sysfs/devcoredump framework implementation. Integrated by drivers that collect firmware/device crash state.

Risks and test signals: Risks include submitting data with the wrong allocator/free callback, leaking chained scatterlists, double-free on disabled configs, exposing sensitive crash memory, and replacing unread dumps. Test vmalloc/custom/sg dump paths, timeout cleanup, module unload while dump is open, disabled config stubs, chained scatterlist freeing, and userspace read truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devcoredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devfreq-event.h -->
# sources/distributed-fs/ceph-client/include/linux/devfreq-event.h

Purpose: Defines the devfreq-event provider framework, which exposes raw utilization/event counters for devfreq governors and device drivers.

Important APIs, types, and functions: Core types are `struct devfreq_event_dev`, `devfreq_event_data`, `devfreq_event_ops`, and `devfreq_event_desc`. APIs enable/disable devices, test enable state, set/get/reset events, find event devices by firmware phandle, count phandles, add/remove event devices, use devm-managed registration, and retrieve driver data.

Control flow: Provider drivers register an event device with descriptor and callbacks. Consumers obtain it from firmware phandles, enable it, optionally set/reset the event, then periodically call `get_event()` to retrieve load and total counts used for utilization calculations. The framework tracks enable nesting with `enable_count` under a mutex.

State and persistence: Runtime state includes registered event-device list membership, embedded `struct device`, enable count, mutex, descriptor, and provider-private driver data. Counter values are sampled, not persisted.

Dependencies and integration points: Depends on device core, firmware phandles, devfreq governors/profiles, and PM counter hardware. Disabled builds return `-EINVAL`, `ERR_PTR(-EINVAL)`, false, or NULL.

Risks and test signals: Risks include enable/disable imbalance, counter reset races, divide-by-zero when total count is zero, stale phandle references, and provider callbacks sleeping under unexpected locks. Test provider registration/removal, devm cleanup, multiple consumers, enable nesting, event sampling, disabled config stubs, and firmware phandle lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devfreq-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devfreq-governor.h -->
# sources/distributed-fs/ceph-client/include/linux/devfreq-governor.h

Purpose: Provides the internal devfreq governor interface used by devfreq policy modules and the devfreq core.

Important APIs, types, and functions: Defines `DEVFREQ_NAME_LEN`, `to_devfreq()`, governor event codes, min/max frequency sentinels, governor feature flags, governor attribute flags, and `struct devfreq_governor`. Functions start/stop/suspend/resume monitoring, update polling intervals, add/remove/devm-add governors, update status/target frequency, query frequency range, and inline `devfreq_update_stats()`.

Control flow: A governor registers with name, flags, attributes, `get_target_freq()`, and `event_handler()`. The core calls event handlers under `devfreq->lock` for lifecycle and PM events, uses monitoring work unless the governor is IRQ-driven, and asks the governor for target frequencies before applying profile callbacks.

State and persistence: Registered governors live on a core list. Per-device governor data is stored in `struct devfreq`, while profile status snapshots are refreshed through `devfreq_update_stats()`. No persistent state is defined here.

Dependencies and integration points: Depends on `linux/devfreq.h`, device core, OPP/QoS integration exposed by devfreq, and sysfs attributes selected by governor flags.

Risks and test signals: Risks include event handlers assuming unlocked state, immutable governors being switched, IRQ-driven governors accidentally scheduled, invalid polling updates, and missing `get_dev_status()`. Test governor register/remove, lifecycle events, polling interval sysfs, suspend/resume, OPP changes, and lockdep around `devfreq->lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devfreq-governor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devfreq.h -->
# sources/distributed-fs/ceph-client/include/linux/devfreq.h

Purpose: Defines the generic Dynamic Voltage and Frequency Scaling framework for non-CPU devices, including profiles, devices, governors, notifiers, OPP helpers, PM integration, QoS limits, statistics, and passive governor data.

Important APIs, types, and functions: Key types are `enum devfreq_timer`, `struct devfreq_dev_status`, `struct devfreq_dev_profile`, `struct devfreq_stats`, `struct devfreq`, `struct devfreq_freqs`, `struct devfreq_simple_ondemand_data`, and `struct devfreq_passive_data`. APIs add/remove devfreq devices, devm-manage them, suspend/resume one or all devices, update frequency, get recommended OPPs, register OPP and transition notifiers, and find devfreq devices by DT node/phandle.

Control flow: A device driver supplies a profile with target and status callbacks, initial frequency, polling interval, optional frequency table, cooling flag, and sysfs groups. The devfreq core creates an embedded device, attaches a governor, monitors load by delayed work or governor events, chooses a target frequency, calls the profile `target()`, updates statistics, and notifies listeners before/after transitions. Passive governors can follow a parent devfreq or cpufreq policy.

State and persistence: Runtime state includes the devfreq device, mutex, profile, governor, OPP table reference, delayed work, frequency table, previous frequency, last status, governor/user data, PM QoS requests, scaling limits, suspend counters/frequencies, transition stats, notifier head, and optional thermal cooling device. No persistent storage is defined.

Dependencies and integration points: Depends on device core, notifiers, PM OPP, PM QoS, workqueues, SRCU notifiers, thermal cooling, firmware phandles, and optional cpufreq parent data. Disabled builds return inert stubs.

Risks and test signals: Risks include profile callbacks returning stale current frequency, unsorted frequency tables, QoS/OPP limit mismatches, stats races without `devfreq->lock`, suspend/resume imbalance, notifier leaks, and passive governor cycles. Test add/remove/devm cleanup, all built-in governors, OPP table changes, PM QoS sysfs limits, transition notifier ordering, suspend/resume nesting, thermal cooling registration, and `CONFIG_PM_DEVFREQ=n` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devfreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devfreq_cooling.h -->
# sources/distributed-fs/ceph-client/include/linux/devfreq_cooling.h

Purpose: Declares thermal cooling-device registration helpers for devfreq-managed devices.

Important APIs, types, and functions: Defines `struct devfreq_cooling_power` with optional `get_real_power()` and declares `of_devfreq_cooling_register_power()`, `of_devfreq_cooling_register()`, `devfreq_cooling_register()`, `devfreq_cooling_unregister()`, and `devfreq_cooling_em_register()`.

Control flow: A devfreq device registers as a thermal cooling device, optionally with firmware node data or an energy model and real-power callback. Thermal governors then limit devfreq cooling states, using either estimated utilization-scaled power or driver-reported real power. Unregister tears down the thermal cooling device.

State and persistence: Cooling state is held in the thermal/devfreq framework, including power tables and current cooling limits. This header defines no persistent state.

Dependencies and integration points: Depends on devfreq, thermal framework, device tree nodes, and optionally energy model data. Disabled builds return `ERR_PTR(-EINVAL)` and no-op unregister.

Risks and test signals: Risks include power callbacks exceeding table maximums, stale cooling devices after devfreq removal, wrong OPP/thermal mapping, and missing disabled-config handling. Test thermal zone binding, cooling state changes, EM registration, real-power callbacks, unregister on driver removal, and `CONFIG_DEVFREQ_THERMAL=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devfreq_cooling.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device-mapper.h -->
# sources/distributed-fs/ceph-client/include/linux/device-mapper.h

Purpose: Defines the in-kernel Device Mapper target and mapped-device API, including target callbacks, table management, device acquisition, bio/request mapping return codes, queue modes, DAX hooks, zoned-device support, events, and logging helpers.

Important APIs, types, and functions: Key types include `enum dm_queue_mode`, `status_type_t`, `union map_info`, `struct dm_dev`, `struct target_type`, `struct dm_target`, `struct dm_arg_set`, `struct dm_arg`, and zoned `struct dm_report_zones_args`. Callback typedefs cover target construction/destruction, bio and request mapping, endio, suspend/resume, status, messages, ioctls, report_zones, busy checks, device iteration, I/O hints, and DAX operations. APIs register targets, parse args, get/put underlying devices, create/hold/reference mapped devices, suspend/resume, wait/emit events, create/complete/swap tables, get live tables under SRCU, and manipulate geometry/queue limits.

Control flow: A DM target module registers a `target_type`; table loading calls its `ctr()` with parsed arguments and target geometry, target code opens underlying devices via `dm_get_device()`, and I/O dispatch invokes `map()`/request callbacks. Targets return submitted, remapped, requeue, delay-requeue, or kill codes; endio callbacks can complete, defer, or requeue. Tables are built empty, populated per target, completed, then swapped into a suspended mapped device.

State and persistence: Runtime state includes target private data, opened lower devices, target feature flags, per-I/O private data, live tables, mapped-device references, event numbers, queue mode, and table queue limits. Persistent mapping configuration is provided by userspace/device-mapper ioctl or early boot parameters, not stored in this header.

Dependencies and integration points: Integrates with block layer bios/requests, gendisks, queue limits, blk crypto, zoned block devices, DAX, ratelimited printk, ioctls, module registration, and early boot `dm-mod.create=`.

Risks and test signals: Risks include wrong map/endio return codes, leaking `dm_dev` references, accepting partial bios incorrectly, unsafely swapping tables without suspend, inconsistent feature flags, DAX offset mistakes, zoned model misreporting, and logging/status buffer overflows. Test table load/unload, suspend/resume and event waits, bio/request targets, flush/discard/write-zeroes paths, partial bio acceptance, zoned report/reset/append behavior, DAX targets, arg parsing errors, and target module init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device-mapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device.h -->
# sources/distributed-fs/ceph-client/include/linux/device.h

Purpose: Defines the central Linux driver-model `struct device` API and the high-level interfaces for device attributes, registration, lifetime, binding, links, firmware nodes, hotplug/offline, sysfs groups, root devices, DMA metadata, PM state, and diagnostics.

Important APIs, types, and functions: Defines `struct subsys_interface`, `device_type`, `device_attribute`, `dev_ext_attribute`, `device_dma_parameters`, device-link enums/flags, `dev_links_info`, `dev_msi_info`, physical-location enums/structs, device flags/accessors, `struct device`, and `struct device_link`. APIs cover subsystem registration, sysfs attributes and binary files, driver override, name/NUMA/MSI/driver-data helpers, PM flags, device locking guards, sync-state helpers, register/add/del/unregister, child iteration/find, rename/move/owner changes, hotplug locks and offline/online, firmware-node setters, root-device creation, manual driver attach/bind/release/probe, dynamic `device_create()`, group management, devm groups, get/put/kill references, devtmpfs mount, shutdown, device links, and char-device module aliases.

Control flow: Subsystems initialize a device, set parent/type/bus/class/release/DMA/firmware data, name it, add it to the driver core, then probe/bind matching drivers through bus logic. Reference counts are managed by `get_device()`/`put_device()` and the release callback frees embedded objects. Device links enforce supplier/consumer probe, PM, sync-state, and removal ordering. Sysfs attributes/groups and uevents expose device state to userspace.

State and persistence: `struct device` stores kobject identity, hierarchy, core private data, bus/driver/class/type, platform and driver data, override name, mutex, PM data, DMA masks/ranges/pools/IOMMU state, firmware nodes, dev_t/id, devres list, sysfs groups, release callback, physical location, removable/offline/sync flags, and bit flags. State is in-memory and mirrored into sysfs/devtmpfs while registered.

Dependencies and integration points: Includes device printk, energy model, resources, kobjects, klists, PM, uid/gid, bus/class/devres/driver subheaders, cleanup guards, and architecture device data. It is the root integration point for nearly every kernel bus, class, driver, DMA/IOMMU subsystem, power management, firmware, and userspace hotplug.

Risks and test signals: Risks include missing release callbacks, reference leaks, use after `device_del()`, direct driver_override manipulation, lock-order problems around `device_lock()`, device-link cycles, sysfs attribute lifetime bugs, incorrect DMA masks, and sync_state never firing due to unbound consumers. Test register/unregister/refcount lifetimes, probe/remove/reprobe, driver override sysfs, child iteration references, device links with PM runtime, offline/online paths, firmware-node assignment, devres cleanup, dynamic device creation/destruction, and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device/bus.h -->
# sources/distributed-fs/ceph-client/include/linux/device/bus.h

Purpose: Defines the bus-specific portion of the Linux driver model, including bus registration, device/driver matching, bus attributes, iteration helpers, notifiers, DMA hooks, PM hooks, and online/offline callbacks.

Important APIs, types, and functions: Key type is `struct bus_type`, with name/dev_name, default bus/device/driver groups, match/uevent/probe/sync_state/remove/shutdown callbacks, IRQ affinity, online/offline, suspend/resume, VF count, DMA configure/cleanup, PM ops, driver_override support, and parent-lock requirement. Other APIs define `bus_attribute`, `device_match_t`, generic match helpers, `device_iter_t`, bus device/driver iteration and find helpers, breadth-first sorting, notifier registration, notifier event enum, and accessors for bus kset/root device.

Control flow: A bus registers its `bus_type`; devices and drivers added to that bus are matched with the bus `match()` callback and probed via bus/driver callbacks. Iteration/find helpers walk bus device lists and return referenced devices. Notifiers report device add/remove and driver bind/unbind events, often while the device lock is held.

State and persistence: Bus core state is maintained internally in `subsys_private`, ksets, device/driver lists, attributes, and notifier chains. The header exposes the immutable bus descriptor and callback contract, not storage implementation.

Dependencies and integration points: Depends on kobjects, klists, PM, devices, drivers, ACPI/OF/fwnode matching, notifiers, and DMA setup. Used by PCI, platform, USB, virtual, and other bus implementations.

Risks and test signals: Risks include match callbacks returning wrong errors, notifier deadlocks under device lock, forgetting to drop references from find helpers, parent-lock ordering issues, and inconsistent DMA cleanup. Test bus register/unregister, driver/device hotplug, deferred probe, generic match helpers, notifier ordering, bus sysfs attributes, bus rescan, and online/offline callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device/class.h -->
# sources/distributed-fs/ceph-client/include/linux/device/class.h

Purpose: Defines the class-specific driver-model API for grouping devices by function rather than physical bus topology.

Important APIs, types, and functions: Defines `struct class`, `struct class_dev_iter`, `struct class_attribute`, `struct class_attribute_string`, and `struct class_interface`. APIs register/unregister/test classes, create class_compat links, iterate/find class devices, create/remove class files with optional namespace, show string attributes, register/unregister class interfaces, and create/destroy dynamically allocated classes.

Control flow: A subsystem registers a class with default attributes, devnode/uevent/release/shutdown/namespace/ownership/PM callbacks. Devices assigned to the class appear in the class hierarchy and can be found or iterated by helpers. Class interfaces receive add/remove callbacks for matching devices without exclusively binding them like drivers.

State and persistence: Class state is held by the driver core in private structures and kobjects; class devices and attributes exist in sysfs while registered. No persistent configuration is stored by the header.

Dependencies and integration points: Depends on kobjects, klists, PM, bus matching helpers, namespace operations, and devtmpfs node callbacks. Used by block, net, input, tty, DRM, and many other functional device groupings.

Risks and test signals: Risks include missing release callbacks for dynamic classes/devices, leaking references from `class_find_device()`, wrong namespace/ownership in sysfs, class interface callbacks racing with removal, and devnode mode mistakes. Test class register/unregister, device creation under classes, class attribute read/write, namespace-specific files, class interface add/remove, class_compat links, and dynamic `class_create()` cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device/class.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device/devres.h -->
# sources/distributed-fs/ceph-client/include/linux/device/devres.h

Purpose: Defines managed device-resource APIs that bind allocations, mappings, pages, per-CPU memory, and cleanup actions to a device lifetime.

Important APIs, types, and functions: Defines `dr_release_t`, `dr_match_t`, raw `devres_alloc/free/add/find/get/remove/destroy/release`, group APIs, managed allocation helpers (`devm_kmalloc`, `devm_kzalloc`, arrays, `devm_krealloc`, memdup, kstrdup, kasprintf), managed per-CPU/page allocation, managed I/O mapping helpers, custom action APIs (`devm_add_action`, `devm_add_action_or_reset`, remove/release/is_added), and `CONFIG_HAS_IOMEM` stubs.

Control flow: Drivers allocate resources with devm helpers or create explicit devres records. The driver core releases records automatically when the device unbinds or when a group is released. Groups provide transactional probe error handling; `devm_add_action_or_reset()` runs the action immediately if registration fails.

State and persistence: Device-owned `devres_head` and `devres_lock` in `struct device` store resource records. State persists only until explicit removal or device teardown.

Dependencies and integration points: Depends on error pointers, GFP flags, NUMA, overflow helpers, percpu allocation, resources, I/O memory, and device core teardown. Used heavily by probe/remove paths to reduce manual cleanup.

Risks and test signals: Risks include mixing devm and manual frees, wrong match callbacks removing another resource, action/data mismatch, group leaks on probe failure, and silent `devm_add_action()` failure if not checked. Test probe failure unwind, remove ordering, devres groups, managed I/O map disabled builds, allocation overflow handling, and action-or-reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device/devres.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device/driver.h -->
# sources/distributed-fs/ceph-client/include/linux/device/driver.h

Purpose: Defines the driver-specific portion of the Linux driver model, including `struct device_driver`, probe strategy, driver registration, driver attributes, device iteration, deferred probe, and module/builtin driver boilerplate macros.

Important APIs, types, and functions: Defines `enum probe_type`, `struct device_driver`, and `struct driver_attribute`. APIs include `driver_register()`, `driver_unregister()`, `driver_find()`, probe-completion waits, driver sysfs file creation/removal, `driver_set_override()`, `driver_for_each_device()`, `driver_find_device()` plus name/OF/fwnode/devt/ACPI/next wrappers, deferred probe helpers, `driver_init()`, `module_driver()`, and `builtin_driver()`.

Control flow: A subsystem-specific driver registration macro eventually registers a `device_driver` with a bus. The driver core matches devices, chooses synchronous/asynchronous probe behavior from `probe_type`, calls probe/sync_state/remove/shutdown/PM callbacks, attaches default attribute groups, and exposes optional bind/unbind unless suppressed. Iteration helpers walk bound devices and return referenced matches.

State and persistence: Driver state includes name, bus, owner, built-in module name, match tables, callbacks, sysfs groups, PM ops, coredump hook, and private driver-core structures. It lives in memory while registered and is represented in sysfs.

Dependencies and integration points: Depends on kobjects, klists, PM, bus APIs, modules, OF/ACPI match tables, sysfs attributes, devcoredump, and Rust post-unbind integration.

Risks and test signals: Risks include unregister while devices are bound, missing module owner, unsafe asynchronous probe assumptions, deferred-probe stalls, reference leaks from find helpers, and incorrect driver override parsing. Test registration/unregistration, bind/unbind sysfs, async and forced-sync probe paths, deferred probe completion, driver attributes, coredump callback, and module_driver/builtin_driver expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device/driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device/faux.h -->
# sources/distributed-fs/ceph-client/include/linux/device/faux.h

Purpose: Declares a simple faux-bus device abstraction for drivers that need a `struct device` anchor without real bus resources or binding complexity.

Important APIs, types, and functions: Defines `struct faux_device`, `to_faux_device()`, `struct faux_device_ops`, `faux_device_create()`, `faux_device_create_with_groups()`, `faux_device_destroy()`, `faux_device_get_drvdata()`, and `faux_device_set_drvdata()`.

Control flow: A caller creates a named faux device with optional parent, callbacks, and attribute groups. The faux bus probes it, optionally invoking `probe`; later destruction removes it and invokes optional remove handling. Driver data helpers forward to the embedded `struct device`.

State and persistence: State is the embedded `struct device`, optional sysfs groups, driver data, and faux bus binding state. It is in-memory and visible through the driver model while alive.

Dependencies and integration points: Depends on container helpers and device core. Intended for firmware loading or other tasks that need device-scoped APIs, devres, logging, or sysfs without platform resources.

Risks and test signals: Risks include using faux devices where real hardware resources need bus semantics, missing destroy calls, callback lifetime bugs, and sysfs group cleanup mistakes. Test create/destroy, parent reference handling, probe failure, remove callback, drvdata helpers, and attribute group visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device/faux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device_cgroup.h -->
# sources/distributed-fs/ceph-client/include/linux/device_cgroup.h

Purpose: Defines device-cgroup permission helpers for block/character device access and mknod checks, with optional cgroup-BPF integration.

Important APIs, types, and functions: Defines access bits `DEVCG_ACC_MKNOD`, `DEVCG_ACC_READ`, `DEVCG_ACC_WRITE`, device type bits `DEVCG_DEV_BLOCK`, `DEVCG_DEV_CHAR`, `DEVCG_DEV_ALL`, `devcgroup_check_permission()`, `devcgroup_inode_permission()`, and `devcgroup_inode_mknod()`.

Control flow: VFS permission paths call `devcgroup_inode_permission()` for block/char inodes with read/write masks; mknod paths call `devcgroup_inode_mknod()` with mode and device number. Helpers classify block versus character devices, ignore non-device inodes and whiteouts, translate mask bits to access bits, and delegate to `devcgroup_check_permission()`. Disabled builds allow all access.

State and persistence: Permission policy state lives in device cgroup and/or cgroup BPF subsystems, not this header. Helpers operate on transient inode/mknod inputs.

Dependencies and integration points: Depends on VFS inode mode/device helpers, `WHITEOUT_DEV`, cgroup device controller, and cgroup BPF. Integrated into filesystem permission and mknod enforcement.

Risks and test signals: Risks include failing to exempt overlay whiteouts, wrong major/minor extraction, read/write mask under-enforcement, and disabled-config behavior diverging from policy expectations. Test block and char read/write/mknod permissions, wildcard policies, cgroup BPF hooks, overlay whiteout creation, non-device inodes, and configs without device cgroups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/device_cgroup.h -->
