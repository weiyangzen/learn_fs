# Group Research: group_1430_openzfs_sources_cow_pools_openzfs_module_os_linux_zfs_zvol_os_c_sou_7e194e0bc113

Scope: `Docs/research_subset_a.md`. This grouped report covers the listed OpenZFS files under `sources/cow-pools/openzfs/`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zvol_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zvol_os.c

## Scope

Implements Linux-specific ZVOL block-device integration: BIO/request dispatch, blk-mq support, read/write/discard handling, open/release/ioctl operations, queue-limit setup, minor creation/removal/rename, disk capacity/read-only updates, and module initialization parameters.

## APIs And Behavior

- `zvol_request_impl()` validates block operations, rejects removed/read-only/bounds-violating I/O, acquires `zv_suspend_lock`, opens the ZIL lazily for writes, and dispatches reads/writes/discards either synchronously or through per-zvol taskqs.
- `zvol_write()`, `zvol_read()`, and `zvol_discard()` translate Linux BIO/request vectors to `zfs_uio_t`, use zvol range locks, call DMU read/write/free routines, update dataset/task I/O accounting, and honor flush/FUA or `ZFS_SYNC_ALWAYS` with `zil_commit()`.
- `zvol_mq_queue_rq()`, `zvol_blk_mq_alloc_tag_set()`, `zvol_submit_bio()`/`zvol_request()` bridge Linux block queue variants to the common request path.
- `zvol_open()` and `zvol_release()` manage first-open/last-close transitions, open-count state, read-only checks, media-change checks, and the `spa_namespace_lock` retry path needed to avoid vdev-on-zvol lock inversion.
- `zvol_ioctl()` supports `BLKFLSBUF` flushing/invalidation and `BLKZNAME` name copyout; geometry/revalidation helpers expose compatibility block-device behavior.
- `zvol_alloc()`, `zvol_alloc_non_blk_mq()`, and `zvol_alloc_blk_mq()` allocate `gendisk`, queue, blk-mq tag sets, queue limits, disk naming/minors, flags, range locks, and ZVOL state.
- `zvol_os_create_minor()` owns the Linux-side creation flow: allocate minor, own the DMU objset, read volume metadata, create state, replay/destroy ZIL as needed, prefetch blkid-probed regions, insert in the zvol table, and publish the disk.
- `zvol_os_remove_minor()`, `zvol_os_free()`, `zvol_os_rename_minor()`, `zvol_os_set_disk_ro()`, and `zvol_os_set_capacity()` handle teardown and visible disk state changes.
- `zvol_init()`/`zvol_fini()` call common zvol init/fini, register/unregister the block major, initialize blk-mq tunables, and manage the Linux `ida`.

## State And Dependencies

State centers on `zvol_state_t`, Linux `struct gendisk`, `request_queue`, optional `blk_mq_tag_set`, `zv_open_count`, `zv_suspend_lock`, `zv_state_lock`, `zv_rangelock`, `zv_zilog`, and `zv_zso`. It depends on Linux block APIs across many kernel compatibility variants, OpenZFS DMU/ZIL/dataset kstats/range locks, `spa_namespace_lock`, `ida`, taskqs, and queue-limit compatibility wrappers.

## Risks And Invariants

Lock ordering is critical: first/last open deliberately take `zv_suspend_lock` before `zv_state_lock`, and first open may need `spa_namespace_lock` despite Linux block-device locks already being held. Asynchronous taskq dispatch must always release `zv_suspend_lock` and complete the BIO/request exactly once. Minor creation becomes externally visible after `add_disk()`, so state insertion and objset disowning must be ordered carefully. Removal clears `private_data` before `del_gendisk()` and drops `zv_state_lock` around block-layer teardown to avoid deadlock.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zvol_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/abd.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/abd.c

## Scope

Implements ARC Buffer Data abstraction shared by ARC/ZIO consumers: linear ABDs, scattered ABDs, gang ABDs, offset views, buffer ownership conversion, single-ABD and dual-ABD iteration, copy/compare/zero helpers, and RAID-Z iteration helpers.

## APIs And Behavior

- Allocation/lifetime: `abd_alloc()`, `abd_alloc_linear()`, `abd_alloc_sametype()`, `abd_alloc_gang()`, `abd_free()`, `abd_alloc_struct()`, and `abd_free_struct()`.
- Gang support: `abd_gang_add()`, `abd_gang_get_offset()`, and internal gang freeing/splicing let multiple ABDs be viewed as one logical ABD, with duplicate link wrappers when one ABD participates in multiple gang ABDs.
- Offset/view support: `abd_get_offset()`, `abd_get_offset_size()`, and `abd_get_offset_struct()` create child ABDs sharing underlying storage, with debug refcounts on parents.
- Buffer wrappers: `abd_get_from_buf()`, `abd_get_from_buf_struct()`, `abd_to_buf()`, `abd_release_ownership_of_buf()`, and `abd_take_ownership_of_buf()` handle linear wrappers and ownership transfer.
- Iteration: `abd_iterate_func()`, Linux kernel `abd_iterate_page_func()`, and `abd_iterate_func2()` map/unmap segments across linear, scatter, and gang layouts.
- Data operations: `abd_copy_to_buf_off()`, `abd_copy_from_buf_off()`, `abd_copy_off()`, `abd_cmp_buf_off()`, `abd_cmp()`, `abd_zero_off()`, and `abd_cmp_zero_off()`.
- RAID-Z helpers: `abd_raidz_gen_iterate()` and `abd_raidz_rec_iterate()` provide bounded mapped segments to parity generation/reconstruction callbacks.
- `abd_verify()` enforces layout, flag, parent, child, and gang invariants under debug builds.

## State And Dependencies

The file manipulates `abd_t` flags, size, parent/child debug refcounts, gang list links, mutexes, linear buffers, scatter chunks, and platform-provided ABD iterator operations. It depends on zio buffer allocators, scatter chunk alloc/free/stat helpers from ABD platform code, `list_t`, `zfs_refcount`, and RAID-Z callback contracts.

## Risks And Invariants

ABD ownership flags decide whether underlying memory is freed; incorrect ownership transfer can leak or double-free zio buffers. Offset ABDs must not outlive parents. Gang ABD links are protected by child `abd_mtx` because one ABD can appear in multiple gang aggregations through wrapper ABDs. Iteration code must progress across gang boundaries and unmap every mapped segment, including error exits. RAID-Z iteration assumes segment sizes are progressive and 512-byte aligned except at valid boundaries.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/abd.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/aggsum.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/aggsum.c

## Scope

Implements aggregate-sum counters: fanned-out, bucketed counters optimized for high-frequency updates and relatively rare exact reads.

## APIs And Behavior

- `aggsum_init()` initializes global bounds, the global lock, bucket fanout based on boot CPU count, and per-bucket locks.
- `aggsum_fini()` destroys bucket locks, frees buckets, and destroys the global lock.
- `aggsum_lower_bound()` and `aggsum_upper_bound()` return approximate atomic bounds without taking locks.
- `aggsum_add()` updates the CPU-selected bucket on the fast path when borrowed capacity covers the delta; otherwise it clears/borrows against the global lower/upper bounds.
- `aggsum_value()` serializes through the global lock, clears all borrowed bucket state, asserts lower and upper bounds converge, and returns the exact value.
- `aggsum_compare()` often answers from bounds alone; otherwise it clears buckets until the target is outside the bounds or the exact value is known.

## State And Dependencies

`aggsum_t` tracks lower/upper bounds, global lock, bucket count/shift, and an array of `aggsum_bucket_t` values containing bucket locks, deltas, and borrowed capacity. It depends on SPL mutexes, atomic load/store helpers, `CPU_SEQID_UNSTABLE`, `boot_ncpus`, and kmem allocation.

## Risks And Invariants

The lower and upper bounds intentionally diverge while buckets hold borrowed capacity. Exact reads and comparisons are expensive because they clear buckets and force future writers to borrow again. CPU hot-add does not expand buckets, so fanout is fixed at initialization. Signed lower-bound arithmetic is mixed with unsigned upper-bound reads; callers must respect the compare/value semantics rather than treating approximate bounds as exact.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/aggsum.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/blake3_zfs.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/blake3_zfs.c

## Scope

Provides ABD-backed BLAKE3 keyed checksum/MAC routines for OpenZFS checksum infrastructure.

## APIs And Behavior

- `abd_checksum_blake3_native()` copies a keyed BLAKE3 context template, iterates over the ABD contents, updates the context incrementally, and writes the 256-bit digest into `zio_cksum_t`.
- `abd_checksum_blake3_byteswap()` computes the native checksum and byte-swaps each 64-bit checksum word for the byteswap variant.
- `abd_checksum_blake3_tmpl_init()` allocates and initializes a keyed BLAKE3 template from the 32-byte checksum salt.
- `abd_checksum_blake3_tmpl_free()` zeroes and frees the template context.
- Kernel builds use per-CPU BLAKE3 contexts under disabled preemption; userspace builds allocate a temporary context per call.

## State And Dependencies

Depends on BLAKE3 context functions, ABD iteration, zio checksum salt/checksum types, kmem allocation, and kernel per-CPU `blake3_per_cpu_ctx`.

## Risks And Invariants

The checksum functions require a non-null template created by the matching initializer. Kernel callers rely on preemption being disabled while using the per-CPU context. Template and temporary contexts are wiped on free/userspace cleanup, preserving keyed checksum material hygiene.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/blake3_zfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/blkptr.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/blkptr.c

## Scope

Implements encoding and decoding of embedded-data block pointers, where small compressed payloads are stored directly inside a `blkptr_t`.

## APIs And Behavior

- `encode_embedded_bp_compressed()` clears the block pointer, sets embedded/compression/byteorder/size fields, and packs payload bytes into permitted payload words using bitfield macros.
- `decode_embedded_bp_compressed()` reverses that packing and extracts the compressed payload bytes from payload words.
- `decode_embedded_bp()` validates output length, decodes the compressed payload, and either returns it directly for uncompressed data or wraps source/destination buffers in stack ABDs and calls `zio_decompress_data()`.

## State And Dependencies

Uses `blkptr_t` layout macros, embedded BP size/compression fields, `zio_decompress_data()`, and transient ABD wrappers around stack/local buffers.

## Risks And Invariants

Only payload words may be used; the encoder/decoder skip non-payload words in the block pointer. Payload size must not exceed `BPE_PAYLOAD_SIZE`, and logical size must fit the caller buffer exactly. Decompression assumes embedded payloads are byte streams and relies on ABD wrappers being freed after use even though they do not own external buffers.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/blkptr.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/bplist.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/bplist.c

## Scope

Implements a simple mutex-protected in-memory list of block pointers.

## APIs And Behavior

- `bplist_create()` initializes the list and mutex.
- `bplist_destroy()` destroys the list and mutex; callers are expected to have drained or cleared entries.
- `bplist_append()` allocates a `bplist_entry_t`, copies the block pointer, and appends it under lock.
- `bplist_iterate()` removes entries from the head, drops the lock while invoking the caller callback, frees each entry, and records the most recently removed entry for debugging.
- `bplist_clear()` removes and frees all queued entries under lock.

## State And Dependencies

State is limited to `bplist_t`, `bplist_entry_t`, a mutex, and an SPL list. Callback signatures accept a `dmu_tx_t` so the list can be used by transactional block-pointer processing code.

## Risks And Invariants

Callbacks run without `bpl_lock`, so they can be slow or re-enter other subsystems without holding the list mutex. Entries are consumed by iteration; this is not a read-only walk. The global `bplist_iterate_last_removed` is only a debugging aid and not a synchronization mechanism.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/bplist.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/bpobj.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/bpobj.c

## Scope

Implements persistent block-pointer objects used to store lists of block pointers and nested sub-objects, including allocation, freeing, open/close, iteration with optional removal, enqueueing block pointers/subobjects, prefetching, and space accounting.

## APIs And Behavior

- `bpobj_alloc_empty()`/`bpobj_decr_empty()` manage the shared empty bpobj feature object and its feature refcount.
- `bpobj_alloc()` chooses the on-disk bonus size based on pool version/features and allocates a `DMU_OT_BPOBJ`; `bpobj_free()` recursively frees nested subobjects and the bpobj object.
- `bpobj_open()`, `bpobj_close()`, `bpobj_is_open()`, and `bpobj_is_empty()` manage in-memory handles and detect supported bonus fields (`comp`, `subobj`, `freed`).
- `bpobj_iterate()` removes visited entries and updates accounting; `bpobj_iterate_nofree()` walks without mutation; `livelist_bpobj_iterate_from_nofree()` walks from a given index for livelists.
- The internal iterator avoids recursive C stack use by maintaining an explicit stack of `bpobj_info_t`, visiting direct block pointers, then nested subobjects from deepest to shallowest.
- `bpobj_enqueue_subobj()` adds a subobject to a parent, flattening small subobject lists and/or block-pointer arrays into the parent when possible to reduce future traversal depth.
- `bpobj_prefetch_subobj()` prefetches the metadata that `bpobj_enqueue_subobj()` is likely to touch.
- `bpobj_enqueue()` stores a sanitized block pointer, records whether it represents a free, updates counts and byte/compressed/uncompressed accounting, and caches the current data dbuf.
- `bpobj_space()` and `bpobj_space_range()` return stored or iterated space accounting; `bplist_append_cb()` appends iterated block pointers to a `bplist`.

## State And Dependencies

Persistent state lives in the bpobj data object, bonus `bpobj_phys_t`, optional subobject array object, and stored block-pointer array. In-memory state includes `bpobj_t` locks, cached dbufs, feature capability booleans, and explicit iterator stack nodes. Dependencies include DMU object/buf APIs, ZAP pool directory entries, SPA feature flags, `bp_get_dsize[_sync]`, dsl pool sync-context checks, and bplist callbacks.

## Risks And Invariants

Space accounting must propagate through parent subobjects when freeing nested entries. Iteration with `free=true` assumes dirty bonus buffers and transactional context; early callback errors leave entries unremoved. `bpobj_enqueue()` intentionally strips embedded payload/checksum/fill details for compression while preserving fields needed for accounting and traversal. The shared empty bpobj must never be freed as a normal bpobj.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/bpobj.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/bptree.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/bptree.c

## Scope

Implements the pool bptree queue of destroyed dataset root block pointers, enabling asynchronous freeing by scan/sync code.

## APIs And Behavior

- `bptree_alloc()` creates the bptree object and initializes bonus fields `bt_begin`, `bt_end`, and space accounting.
- `bptree_free()` asserts the queue is empty and frees the object.
- `bptree_is_empty()` checks whether `bt_begin == bt_end`.
- `bptree_add()` appends a destroyed dataset root block pointer plus birth TXG and updates byte/compressed/uncompressed counters; it is sync-context only.
- `bptree_iterate()` reads each queued entry, traverses destroyed dataset blocks with `traverse_dataset_destroyed()`, calls the caller callback for non-hole/non-redacted non-dnode-level BPs, optionally updates space accounting and frees completed queue entries.
- When freeing, traversal bookmarks are saved on errors so later invocations can resume; I/O-like errors can be skipped to later entries while preserving queue state.

## State And Dependencies

Persistent state is `bptree_phys_t` in the bonus buffer plus an array of `bptree_entry_phys_t` records in the object data. Dependencies include DMU object/buf/read/write/free APIs, destroyed-dataset traversal, SPA block size/accounting helpers, and scan/free policy such as `zfs_free_leak_on_eio`.

## Risks And Invariants

Only sync context may mutate/free bptree entries. `bt_begin` only advances when no earlier I/O errors require preserving entry positions; otherwise completed entries may be made future no-ops. Space counters must reach zero when the queue is fully drained, except the leak-on-EIO path forcibly clears them.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/bptree.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/bqueue.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/bqueue.c

## Scope

Implements a bounded blocking queue with batched enqueue/dequeue lists and capacity measured in caller-supplied item sizes.

## APIs And Behavior

- `bqueue_init()` initializes shared, enqueuing, and dequeuing lists, condition variables, lock, maximum capacity, node offset, and fill fraction.
- `bqueue_destroy()` asserts all lists/sizes are empty, destroys synchronization primitives, and tears down lists.
- `bqueue_enqueue()` appends to a private enqueuing list and flushes it to the shared list when the batched size reaches the fill threshold.
- `bqueue_enqueue_flush()` forces a flush and wakeup for final records or low-volume producers.
- `bqueue_dequeue()` consumes from a private dequeuing list; if empty, it waits for shared-list data, moves the whole shared list locally, wakes producers, and returns the head entry.

## State And Dependencies

`bqueue_t` contains three lists, size counters, max size/fill fraction, embedded-node offset, one mutex, and producer/consumer condition variables. Stored objects must contain a `bqueue_node_t` at the configured offset.

## Risks And Invariants

The API assumes at most one concurrent enqueuer and at most one concurrent dequeuer per queue, though the enqueuer and dequeuer may run concurrently with each other. Producers can remain below the fill threshold indefinitely unless `bqueue_enqueue_flush()` is used. Capacity waiting uses shared `bq_size`, while batched private list sizes are tracked separately.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/bqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/brt.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/brt.c

## Scope

Implements OpenZFS Block Reference Tables for block cloning: per-top-level-vdev reference tables, in-memory range counters, pending clone tracking by TXG, BRT add/decrement/sync/load/unload, statistics, and BRT module tunables.

## APIs And Behavior

- Global lifecycle: `brt_init()`/`brt_fini()` create/destroy the BRT entry cache and kstats; `brt_create()`, `brt_load()`, and `brt_unload()` initialize, load, or tear down per-pool BRT state.
- Vdev state: `brt_vdevs_expand()`, `brt_vdev_realloc()`, `brt_vdev_create()`, `brt_vdev_load()`, `brt_vdev_sync()`, `brt_vdev_destroy()`, and `brt_vdevs_free()` manage per-vdev ZAP objects, entry-count arrays, dirty bitmaps, bonus metadata, dnode holds, and feature refcounts.
- Lookup/accounting: `brt_maybe_exists()` uses the in-memory per-region entry-count array as a fast no-entry filter; `brt_get_dspace()`, `brt_get_used()`, `brt_get_saved()`, and `brt_get_ratio()` expose BRT space metrics.
- Reference decrement: `brt_entry_decref()` loads or finds an entry, decrements BRT reference count, updates vdev counters, and returns whether the underlying block should be freed immediately.
- Reference query: `brt_entry_get_refcount()` checks in-memory state first, then ZAP state.
- Pending clone tracking: `brt_pending_add()` and `brt_pending_remove()` update per-TXG pending AVL trees; `brt_pending_apply()`/`brt_pending_apply_vdev()` convert pending references into real BRT entries during sync, using DDT instead when cloned BPs are dedup blocks.
- Sync: `brt_sync()` detects dirty vdevs, creates an assigned DMU transaction, and `brt_sync_table()` writes/removes ZAP entries, syncs vdev metadata, or destroys empty vdev BRT objects.
- Prefetch: `brt_prefetch()` and `brt_prefetch_all()` prefetch BRT ZAP entries/objects to reduce sync-time or scan-time latency.
- Module parameters expose BRT ZAP prefetch and default ZAP blockshift settings.

## State And Dependencies

Per-pool state lives in `spa_brt_lock`, `spa_brt_vdevs`, `spa_brt_nvdevs`, and `spa_brt_rangesize`. Each `brt_vdev_t` holds locks, MOS object IDs, a dnode for the entries ZAP, in-memory `bv_entcount` array, dirty bitmap, AVL tree of sync entries, per-TXG pending AVL trees, counters for total/used/saved space, and endian state. Dependencies include SPA/vdev config, DMU/ZAP/dnode APIs, block-cloning feature flags, DDT addref for dedup blocks, `bp_get_dsize`, kstats, `wmsum`, AVL trees, and bitmaps.

## Risks And Invariants

The entry-count array is the core free-path optimization; false positives are tolerated, but false negatives would leak BRT references and are guarded by sync ordering. `brt_entry_decref()` drops the vdev lock for ZAP lookup and must handle races where another thread inserts the entry meanwhile. Pending trees are per-TXG and applied only in syncing context. Endian handling changes ZAP integer size/count ordering depending on the block-cloning-endian feature. Vdev shrink is not supported. Dirty entry-count bitmaps exist, but syncing currently rewrites the whole in-memory array when any tracked block is dirty.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/brt.c -->