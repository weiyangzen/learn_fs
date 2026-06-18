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
