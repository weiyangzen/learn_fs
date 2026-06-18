# Group Research: group_1456_openzfs_sources_cow_pools_openzfs_module_zfs_zio_c_sources_cow_pool_1a36c727cae7

Scope checked against `Docs/research_subset_a.md`: `sources/cow-pools/openzfs` is included in subset A. All six listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zio.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zio.c

Read coverage: complete file, 6130 lines.

Purpose: core OpenZFS ZIO engine. This file owns ZFS logical and physical I/O object creation, pipeline execution, parent/child interlocks, block allocation/free/claim, gang blocks, dedup I/O integration, encryption and checksum stages, vdev dispatch, retry/suspend/reexecute behavior, slow/deadman handling, and bookmark ordering helpers.

Main responsibilities:
- Initializes and tears down ZIO object/link caches, ZIO buffer caches, kstats, fault injection, and LZ4 hooks through `zio_init()` / `zio_fini()`.
- Provides metadata/data buffer allocation APIs: `zio_buf_alloc()`, `zio_data_buf_alloc()`, matching frees, debug allocation accounting, and optional canary overflow detection.
- Implements transform stack mechanics via `zio_push_transform()` and `zio_pop_transforms()` for compression, encryption, decryption, subblock padding, and temporary ABD substitutions.
- Manages ZIO DAG relationships with `zio_add_child()`, `zio_remove_child()`, `zio_wait_for_children()`, and `zio_notify_parent()`.
- Creates all major ZIO types: `zio_null()`, `zio_root()`, `zio_read()`, `zio_write()`, `zio_rewrite()`, `zio_free_sync()`, `zio_claim()`, `zio_trim()`, physical read/write, vdev child/delegated I/O, and flush I/O.
- Verifies block pointer structural validity through `zfs_blkptr_verify()` and `zfs_dva_valid()`.

Core pipeline flow:
- `zio_create()` initializes a `zio_t`, chooses child type, copies or references the block pointer, sets logical/gang ancestry, initial stage, pipeline bits, wait states, callbacks, flags, priority, ABD, and bookmark.
- `zio_wait()` and `zio_nowait()` set queue timestamps, select write allocators, and enter `__zio_execute()`.
- `__zio_execute()` advances through `zio_pipeline[]` by stage bit, dispatching to taskqs when a stage is blocking, stack depth is unsafe, or interrupt context must not block.
- Pipeline stages include read/write/free init, async issue, compression, encryption, checksum generation, nopwrite, DDT read/write/free, BRT free, gang assemble/issue, DVA throttle/allocate/free/claim, ready, vdev I/O start/done/assess, checksum verify, direct-I/O checksum verify, and done.
- `zio_done()` is the final convergence point: it waits for children, updates allocation throttle accounting, inherits child errors, finalizes checksum reports, pops transforms, updates vdev stats, posts events, decides reexecute/suspend behavior, unallocates failed allocations, frees gang trees, runs done callbacks, notifies parents, and destroys or wakes the waiter.

Read/write preparation:
- `zio_read_bp_init()` pushes decompression and decryption transforms as needed, decodes embedded data BPs directly, and routes dedup blocks through DDT read pipeline.
- `zio_write_bp_init()` handles override block pointers, nopwrite/BRT write flags, dedup override decisions, and falls back to normal write if override cannot satisfy properties.
- `zio_write_compress()` waits for logical/gang children to become ready, invokes `io_children_ready`, performs zero-block, compression, embedded-data, raw-compressed, and raw-encrypted special cases, applies sync-pass convergence decisions, rewrites in place when allowed, initializes BP fields, and chooses DDT/nopwrite pipeline stages.

Allocation and COW behavior:
- Ordinary allocating writes pass through `zio_dva_throttle()` and `zio_dva_allocate()`, selecting a metaslab class, reserving throttle capacity for async writes, allocating DVAs, falling back between classes, and falling back to gang blocks on fragmentation/ENOSPC where possible.
- `zio_dva_unallocate()` gives back newly allocated normal or gang constituent blocks when a logical write fails before commit.
- Frees are immediate only when safe; gang, dedup, BRT, non-current-txg, and deferred sync-pass cases are queued or represented as async free ZIOs.
- `zio_alloc_zil()` separately allocates intent log blocks across log, special embedded log, special, embedded log, then normal classes, filling ZIL BP properties and encryption parameters.

Gang block support:
- The long gang block section documents and implements two-phase gang handling.
- `zio_gang_tree_assemble()` recursively reads gang headers into an in-core tree before issuing read/free/claim/rewrite work.
- `zio_gang_tree_issue()` walks the assembled tree and invokes type-specific callbacks.
- `zio_write_gang_block()` allocates a gang header, splits residual data across gang members, attempts opportunistic contiguous allocations, creates nested gang writes when needed, and activates dynamic gang header feature when required.

Dedup and BRT:
- `zio_ddt_read_start()` / `zio_ddt_read_done()` route dedup reads through DDT entries and attempt repair reads from alternate DDT phys variants after child errors.
- `zio_ddt_write()` is the complex DDT write path: looks up entries, verifies collisions when requested, fills existing DVAs, piggybacks on in-flight writes, issues shortfall writes, extends DDT phys entries at READY, and rolls back optimistic refs on child write failure.
- `zio_ddt_free()` decrements DDT refs or clears the dedup bit if the table entry was pruned and the block must be freed normally.
- `zio_brt_free()` decrements cloned block references and stops the free pipeline when references remain.

Vdev I/O:
- `zio_vdev_io_start()` enters `SCL_ZIO` for logical mirror dispatch, handles leaf alignment/padding transforms, skips unnecessary resilver repair writes, queues leaf reads/writes/trims, applies device injections, and calls vdev ops.
- `zio_vdev_io_done()` drains vdev children, updates queue completion, applies post-I/O injections, calls vdev completion ops, and probes unexpectedly failing devices.
- `zio_vdev_io_assess()` releases `SCL_ZIO`, frees vdev-specific data, retries non-leaf logical I/O when allowed, maps inaccessible leaf errors to `ENXIO`, disables unsupported flushes, and stops the pipeline on terminal errors.

Integrity and crypto:
- `zio_encrypt()` handles raw encrypted receive/write metadata, indirect MAC checksums, objset MACs, authenticated unencrypted object types, normal encrypted leaf blocks, ZIL MAC placement, and transform pushing for encrypted ABDs.
- `zio_checksum_generate()` chooses label, gang header, physical, or BP checksum and calls `zio_checksum_compute()`.
- `zio_checksum_verify()` calls `zio_checksum_error()`, records checksum stats/events, and marks direct-I/O checksum failures specially.
- Direct I/O write verification is handled by `zio_dio_checksum_verify()` and `zio_dio_chksum_verify_error_report()`.

Failure handling:
- `zio_deadman()` traverses a ZIO tree, logs slow/hung I/O, posts deadman events, and may interrupt leaf I/O or panic depending on failmode.
- `zio_suspend()`, `zio_resume()`, and `zio_reexecute()` implement pool suspension, retry after resume, and top-down reexecution of failed logical I/O trees.
- `zio_worst_error()` ranks propagated errors as success, `ENXIO`, `ECKSUM`, `EIO`, then other.

Other utilities:
- `zbookmark_compare()`, `zbookmark_subtree_completed()`, and `zbookmark_subtree_tbd()` compare traversal bookmarks, including special canonicalization for meta-dnode bookmarks.
- Tunables include sync pass behavior, slow I/O threshold, allocation throttling, requeue priority, metadata exclusion from debug caches, and deadman logging breadth.

Key dependencies:
- Uses SPA, vdev, metaslab, ARC, DDT, BRT, DSL scan, crypto, ABD, checksum, compression, and fault injection subsystems.
- Directly consumes `zio_checksum.c`, `zio_compress.c`, and `zio_inject.c` APIs.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zio.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zio_checksum.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zio_checksum.c

Read coverage: complete file, 609 lines.

Purpose: checksum algorithm registry and checksum compute/verify implementation for ZIO and SPA blocks.

Main responsibilities:
- Defines `zio_checksum_table[]`, mapping checksum IDs to native/byteswap ABD functions, optional context-template init/free functions, flags, and stable on-disk names.
- Provides Fletcher-2 and Fletcher-4 ABD implementations, plus references to SHA-256, SHA-512, Skein, Edon-R, and BLAKE3 functions.
- Maps checksum algorithms to feature flags with `zio_checksum_to_feature()`.
- Selects inherited/on/dedup checksum settings with `zio_checksum_select()` and `zio_checksum_dedup_select()`.

Checksum table behavior:
- `inherit` and `on` are policy values, not executable checksum functions.
- `off` returns zero checksum.
- `label` and `gang_header` use SHA-256 and embedded checksum fields.
- `zilog` and `zilog2` use Fletcher-2 embedded forms.
- `sha256`, `sha512`, `skein`, and `blake3` are metadata/dedup/nopwrite-capable.
- Salted algorithms use per-SPA checksum templates initialized lazily from the pool checksum salt.

Embedded checksum logic:
- `zio_checksum_compute()` handles embedded checksums by temporarily writing verifier data into `zio_eck_t`, computing over the ABD, then writing the resulting checksum back into the embedded checksum field.
- Gang headers use a verifier derived from DVA identity and physical birth.
- Labels use a verifier derived from label offset.
- ZILOG2 sizes the checksum range from `zil_chain_t.zc_nused`.

Encryption interaction:
- `zio_checksum_handle_crypt()` preserves MAC words in encrypted block checksums.
- For non-strong checksums it XORs entropy from high words into low words before storing MAC-related words.
- Verification truncates encrypted non-objset checksums to compare only the checksum portion; MAC validation happens through decryption/authentication.

Verification:
- `zio_checksum_error_impl()` validates algorithm IDs, initializes templates, extracts expected embedded or BP checksum, handles byteswapped embedded records, recomputes the actual checksum, restores overwritten verifier bytes, fills `zio_bad_cksum_t`, and returns `ECKSUM` on mismatch.
- `zio_checksum_error()` selects checksum type from BP or physical checksum property, adjusts gang header size for dynamic gang headers, retries old gang size for compatibility, updates the in-core gang node size if old-style verification succeeds, and applies checksum fault injection after a clean verify.

Lifecycle:
- `zio_checksum_templates_free()` frees any per-SPA checksum context templates before SPA deallocation.

Key dependencies:
- Called by `zio.c` checksum generate/verify stages.
- Uses ABD iteration, Fletcher helpers, algorithm-specific checksum providers, SPA feature/template state, ZIL structures, and ZIO fault injection.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zio_checksum.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zio_compress.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zio_compress.c

Read coverage: complete file, 181 lines.

Purpose: compression algorithm registry and helper selection/wrapper functions for ZIO compression and decompression.

Main responsibilities:
- Defines `zio_compress_table[]`, mapping compression IDs to names, default levels, compression functions, decompression functions, and optional decompression-with-level functions.
- Implements policy selection for inherited/on compression and compression levels.
- Provides generic `zio_compress_data()` and `zio_decompress_data()` wrappers used by `zio.c`.
- Maps compression algorithms to required SPA features with `zio_compress_to_feature()`.

Compression table:
- Policy/non-compression entries: `inherit`, `on`, `uncompressed`, `empty`.
- Algorithms: `lzjb`, `gzip-1` through `gzip-9`, `zle`, `lz4`, `zstd`.
- `zle` uses level/parameter `64`.
- `zstd` uses `ZIO_ZSTD_LEVEL_DEFAULT` and supports a level-aware decompressor.

Selection behavior:
- `zio_compress_select()` resolves `inherit` to parent and `on` to LZ4 if `SPA_FEATURE_LZ4_COMPRESS` is active, otherwise legacy LZJB.
- `zio_complevel_select()` returns zero for algorithms without levels; otherwise resolves level inheritance.

Compression wrapper:
- `zio_compress_data()` asserts an executable compressor, resolves ZSTD levels, allocates a destination ABD matching source layout when needed, calls the compressor, and returns original size when compression fails to fit the requested maximum.
- `zio_decompress_data()` validates the algorithm and dispatches to either a level-aware decompressor or the ordinary decompressor.

Key dependencies:
- Used by `zio_write_compress()` for write-side compression and by read/decrypt paths for decompression.
- Algorithm functions are supplied by OpenZFS compression modules, including ZLE from `zle.c`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zio_compress.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zio_inject.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zio_inject.c

Read coverage: complete file, 1199 lines.

Purpose: ZFS fault injection registry and runtime handlers used by ZIO, ARC, vdev, import/export, and test tooling.

Main responsibilities:
- Maintains global `inject_handlers` list guarded by `inject_lock`.
- Tracks global `zio_injection_enabled` and delay-specific `inject_delay_count`.
- Registers, lists, and clears injection records via `zio_inject_fault()`, `zio_inject_list_next()`, and `zio_clear_fault()`.
- Implements matching and injection for data faults, decrypt faults, panic faults, device faults, label faults, ignored writes, I/O delay, ready-stage delay, import delay, and export delay.

Handler model:
- Each `inject_handler_t` has an ID, optional held `spa_t`, optional pool name for import/export delay, a `zinject_record_t`, delay lanes, and list linkage.
- Normal handlers take an injection reference on the SPA so the pool cannot disappear from the namespace while the handler exists.
- Import/export delay handlers match by pool name and intentionally do not hold an SPA.
- Delay-I/O handlers allocate lane arrays to model limited-concurrency latency injection.

Matching:
- `freq_triggered()` supports legacy 0-100 frequencies and scaled percentage frequencies.
- `zio_match_handler()` matches MOS metadata by type or exact objset/object/level/blkid/DVA/error ranges and updates match/inject counters.
- `zio_match_dva()` maps a physical vdev child ZIO back to the matching BP DVA index.
- `zio_match_iotype()` matches read/write/free/flush/trim/probe or all standard I/O types.

Runtime injection paths:
- `zio_handle_fault_injection()` injects data read errors, excluding non-logical I/O, non-read I/O, and rebuild checksum cases.
- `zio_handle_decrypt_injection()` injects authentication/decryption failures for matching bookmarks.
- `zio_handle_device_injection()` and `zio_handle_device_injections()` inject vdev/device errors, failfast behavior, retry marking, ENXIO open failure aux state, and EILSEQ bit flips.
- `zio_handle_label_injection()` injects label-region errors by translating relative label offsets to the active label copy.
- `zio_handle_ignored_writes()` probabilistically strips vdev I/O stages from syncing writes to simulate hardware accepting but losing writes.
- `spa_handle_ignored_writes()` validates ignored-write duration windows.
- `zio_handle_io_delay()` assigns matching vdev I/O to the soonest available delay lane and returns a target completion timestamp.
- `zio_handle_ready_delay()` delays logical I/O before READY when configured.
- `zio_handle_import_delay()` and `zio_handle_export_delay()` apply one-shot pool-level pauses.

Registration details:
- `zio_inject_fault()` validates delay lane/timer values, optionally unloads SPA, optionally converts byte ranges to blkids with `zio_calculate_range()`, enforces single import/export delay per pool, allocates handler state, inserts it under writer lock, increments enabled counters, and optionally flushes ARC.
- `zio_calculate_range()` resolves dataset/object/dnode and converts byte ranges and indirect levels into block ID ranges.
- `zio_clear_fault()` removes the handler, releases delay lanes, pool-name strings, SPA injection references, and decrements global counters.

Lifecycle:
- `zio_inject_init()` initializes lock, delay mutex, and list.
- `zio_inject_fini()` destroys them.
- Kernel exports expose injection state and public handler APIs.

Key dependencies:
- Called throughout `zio.c` at decompression/decryption, checksum verification, ready stage, vdev issue/done, ignored writes, and delay paths.
- Uses ARC flushing, SPA namespace/ref management, vdev label math, dnode lookup, and ZFS ioctl injection records.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zio_inject.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zle.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zle.c

Read coverage: complete file, 97 lines.

Purpose: zero-length encoding compression algorithm implementation for ZIO compression table entry `zle`.

Algorithm:
- Encodes runs as one-byte length tags.
- If tag value is below parameter `n`, the next `tag + 1` bytes are literal data.
- If tag value is at least `n`, it represents a run of zeros of length `256 - tag + 1`.
- OpenZFS registers this through `ZFS_COMPRESS_WRAP_DECL(zfs_zle_compress)` and `ZFS_DECOMPRESS_WRAP_DECL(zfs_zle_decompress)`.

Compression:
- `zfs_zle_compress_buf()` walks source and destination buffers.
- Zero runs are emitted as length-only records.
- Literal runs are emitted as a length byte plus copied non-zero-containing bytes, stopping before zero pairs where possible.
- If output cannot finish within destination capacity, it returns original source length to indicate no useful compression.

Decompression:
- `zfs_zle_decompress_buf()` reads length tags, copies literal bytes or fills zero runs.
- It validates source and destination bounds and returns `0` only when exactly the destination length is produced; malformed/truncated streams return `-1`.

Key dependencies:
- Referenced by `zio_compress_table[]` in `zio_compress.c`.
- Used by write compression and read decompression paths in `zio.c`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zle.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zrlock.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zrlock.c

Read coverage: complete file, 189 lines.

Purpose: Zero Reference Lock implementation, a lightweight lock/reference primitive for cases where many readers may hold references and a writer may only lock when the reference count is zero.

Semantics:
- Readers call `zrl_add_impl()` and `zrl_remove()`.
- A writer-like caller uses `zrl_tryenter()` only; it never waits for readers to drain.
- `ZRL_LOCKED` is `-1` and semantically means zero references but exclusively locked.
- `ZRL_DESTROYED` is `-2` for debug/sanity after destruction.
- Reader acquisition is reentrant because it increments a count and does not track per-thread ownership for correctness.

Functions:
- `zrl_init()` initializes mutex, condition variable, refcount, and debug owner/caller fields.
- `zrl_destroy()` asserts zero references, destroys synchronization primitives, and marks destroyed.
- `zrl_add_impl()` uses atomic CAS to increment the refcount while not locked; if locked, waits on the condition variable until unlocked.
- `zrl_remove()` decrements the refcount atomically and asserts non-negative count in debug builds.
- `zrl_tryenter()` atomically transitions refcount from zero to `ZRL_LOCKED`; returns failure if references exist.
- `zrl_exit()` releases exclusive locked state, clears debug owner, sets refcount to zero, and broadcasts waiters.
- `zrl_is_zero()` returns true for zero or locked states.
- `zrl_is_locked()` checks exclusive locked state.
- `zrl_owner()` is available in debug builds.

Concurrency notes:
- Fast reader acquisition is lock-free unless the ZRL is exclusively locked.
- Waiting readers use `zr_mtx` and `zr_cv`.
- There is no writer priority and no blocking writer acquisition, avoiding reader/writer priority policy complexity.

Exports:
- Kernel builds export `zrl_add_impl` and `zrl_remove`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zrlock.c -->