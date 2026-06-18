# Group Research: group_1642_qemu_sources_virtualization_qemu_block_nvme_c_sources_virtualizatio_e0de11432c0e

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/nvme.c -->
# File Research: sources/virtualization/qemu/block/nvme.c

## Purpose
Implements QEMU's `nvme` block protocol driver for direct access to a physical NVMe PCI device through VFIO. It maps BAR registers, initializes admin and I/O queue pairs, submits NVMe commands, maps guest I/O buffers for DMA, and exposes the device through QEMU's coroutine block driver interface.

## Main Entry Points
- `nvme_parse_filename()` parses `nvme://PCIADDR/NSID` into runtime options.
- `nvme_open()` validates options, initializes the controller with `nvme_init()`, and optionally configures write-cache behavior for `BDRV_O_NOCACHE`.
- `nvme_init()` opens the PCI device through VFIO, maps BAR0, resets/enables the controller, creates admin queues, enables MSI-X, identifies the controller/namespace, and creates an I/O queue.
- `nvme_close()` tears down queues, event notifiers, BAR mappings, VFIO state, and saved device name.
- `nvme_co_preadv()`, `nvme_co_pwritev()`, `nvme_co_flush()`, `nvme_co_pwrite_zeroes()`, and `nvme_co_pdiscard()` implement the block I/O operations.

## Internal Mechanics
Queue state is split into `NVMeQueuePair`, `NVMeQueue`, and `NVMeRequest`. Each queue pair owns DMA-mapped submission/completion queues, one page of PRP-list memory per request, a free-request list, a completion bottom half, and coroutine wait queues for request exhaustion. The admin queue is index 0; I/O queues start at index 1. The driver currently creates one I/O queue.

Command submission fills an SQ entry under the queue lock, assigns the request CID, increments `need_kick`, and defers the doorbell write through `defer_call()`. Completion processing runs in the block node's main `AioContext`, checks the CQ phase bit, translates NVMe status to errno, returns request slots to the freelist, invokes callbacks outside the queue lock, updates the CQ head doorbell, and wakes coroutines waiting for free request slots.

DMA handling maps aligned qiov buffers into VFIO IOVA space and builds NVMe PRP entries. If VFIO mapping returns ENOSPC/ENOMEM because temporary DMA mappings are exhausted, coroutines coordinate through `dma_map_lock` and `dma_flush_queue` to reset temporary mappings once outstanding DMA mappings drain. Unaligned qiovs are copied through an aligned temporary buffer.

Controller identification records namespace size, LBA shift, write-cache support, maximum transfer size, write-zeroes support, discard support, and namespace metadata restrictions. Block limits are refreshed from page size, LBA size, MDTS, and NVMe command field limits.

## Dependencies
Uses QEMU VFIO helpers, host PCI MMIO helpers, event notifiers, AioContext/BH APIs, coroutine queues and mutexes, NVMe protocol definitions from `block/nvme.h`, and QEMU block driver interfaces. It depends on Linux VFIO and a PCI NVMe device address supplied by the user.

## Filesystem/Block Relevance
This is a virtual block integration layer that exposes real NVMe hardware directly to QEMU's block layer. It is important for understanding how QEMU maps block I/O requests into hardware queue commands, handles DMA registration pressure, advertises discard/write-zeroes/flush semantics, and enforces strict alignment requirements.

## Risks and Notes
- The driver relies on careful AioContext separation: command submission may happen from any context, but kicking and completion processing happen in the BDS main context.
- Request freelist, SQ/CQ indices, `need_kick`, and `inflight` are protected by the queue lock; callbacks are invoked outside the lock to permit re-entrancy.
- Temporary DMA mappings are intentionally reclaimed lazily; failures before `dma_map_count` increments rely on later reset paths to reclaim any partial mappings.
- Only namespaces without metadata are supported.
- The driver blocks resize/grow operations and only accepts no-op truncation.
- `nvme_register_buf()` notes a FIXME that fixed mappings can exhaust IOVA space after repeated register/unregister cycles.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/parallels-ext.c -->
# File Research: sources/virtualization/qemu/block/parallels-ext.c

## Purpose
Implements read-only support for the Parallels format extension cluster, specifically persistent dirty bitmap loading. It is part of the Parallels image format driver and is used when an image has `ext_off` set and is opened read-only.

## Main Entry Points
- `parallels_read_format_extension()` reads the extension cluster and calls `parallels_parse_format_extension()`.
- `parallels_parse_format_extension()` validates the extension magic and MD5 checksum, walks feature records, and dispatches supported feature types.
- `parallels_load_bitmap()` parses a dirty-bitmap feature record, creates a QEMU dirty bitmap, reads its L1 table, and loads bitmap contents.
- `parallels_load_bitmap_data()` deserializes bitmap data clusters into the created bitmap.

## Internal Mechanics
The extension begins with `ParallelsFormatExtensionHeader`, including a magic value and MD5 checksum over the rest of the cluster. It then contains feature records with `ParallelsFeatureHeader`. Supported features are an end marker and a dirty-bitmap feature. Feature flags must be zero.

Dirty bitmap metadata includes disk size in sectors, bitmap UUID, granularity, and L1 table size. L1 entries map serialized bitmap chunks: `0` means all-zero chunk, `1` means all-one chunk, and larger values are sector-numbered locations of bitmap data clusters in the image. Loaded bitmaps are marked read-only because extension write support is not implemented.

## Dependencies
Uses QEMU dirty bitmap serialization APIs, `qcrypto_hash_bytes()` for MD5 validation, UUID helpers, aligned block reads, and shared Parallels state from `parallels.h`.

## Filesystem/Block Relevance
This file bridges image-format metadata to QEMU's persistent dirty bitmap model. It matters for backup/incremental-copy workflows that consume Parallels image bitmaps.

## Risks and Notes
- Format extensions are unsupported in writable mode by the main driver; this reader asserts read-only bitmap handling.
- Unknown features, nonzero feature flags, checksum mismatches, and malformed L1 sizes fail parsing.
- On parsing failure, bitmaps already created from earlier feature records are released.
- Feature data advancement is 8-byte aligned inside the extension cluster.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/parallels-ext.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/parallels.c -->
# File Research: sources/virtualization/qemu/block/parallels.c

## Purpose
Implements QEMU's Parallels disk image format driver. It supports probing, opening, reading, writing, cluster allocation, discard/zero handling, image creation, image consistency checking/repair, header/BAT flushing, and optional backing files.

## Main Entry Points
- `parallels_probe()` identifies Parallels v2 images with either supported magic string.
- `parallels_open()` parses runtime preallocation options, opens the file child, reads and validates the header/BAT, loads format extensions in read-only mode, marks writable images in-use, builds used-cluster state, and optionally repairs detected issues.
- `parallels_close()` clears the in-use flag, writes the header, truncates tail preallocation/leaks, frees bitmaps/header memory, and removes the migration blocker.
- `parallels_co_readv()` and `parallels_co_writev()` implement sector-based reads and writes through the BAT.
- `parallels_co_block_status()` reports allocated host extents.
- `parallels_co_pdiscard()` and `parallels_co_pwrite_zeroes()` deallocate whole clusters when safe.
- `parallels_co_check()` performs image check/fix operations.
- `parallels_co_create()` and `parallels_co_create_opts()` create a new Parallels image.

## Internal Mechanics
The driver maps guest sectors to host sectors through a block allocation table (`bat_bitmap`). A BAT entry of zero means unallocated. `tracks` is the cluster size in sectors, and `off_multiplier` differs between old and extended magic formats. `block_status()` walks contiguous allocated or unallocated regions and returns the host sector mapping plus the number of sectors covered.

Writes call `allocate_clusters()`, which finds the current status, allocates missing clusters from holes or by extending the file, optionally preallocates extra space, copies data from the backing file for copy-on-write semantics, marks clusters used, updates BAT entries, and advances `data_end`. BAT modifications are tracked in `bat_dirty_bmap`; `parallels_co_flush_to_os()` writes dirty header/BAT blocks back to storage.

The used-cluster bitmap is built from current BAT entries. It is used both for normal allocation and for consistency checking. The check path validates the in-use flag, `data_off`, clusters outside the image, leaked tail space, and duplicate BAT entries. With fix flags, it updates metadata, clears bad entries, reallocates duplicate clusters, truncates leaked space, and collects block-fragmentation statistics.

Image creation writes a v2 header with `HEADER_MAGIC2`, calculated geometry, BAT size, total sectors, and data offset, then zeroes the BAT/data-offset padding area.

## Dependencies
Uses QEMU block coroutines, image creation QAPI visitors, qdict option conversion, bitmap helpers, migration blockers, aligned allocation, and shared Parallels declarations from `parallels.h`. Format extension parsing is delegated to `parallels_read_format_extension()`.

## Filesystem/Block Relevance
This is a sparse COW-capable virtual disk image format. It shows how QEMU maintains a cluster allocation table, performs backing-file copy-on-write, supports hole reuse, handles preallocation, and repairs metadata corruption.

## Risks and Notes
- The driver uses a conservative coroutine mutex around BAT access and image extension.
- Live migration is blocked because the format lacks the needed activation/migration support.
- Discard/zero is only supported for whole clusters and is rejected when a backing file exists, because the format has no explicit zero marker and could expose stale backing data.
- Format extensions are ignored with a warning in writable mode, preserving historical behavior but leaving extension metadata unsupported for writes.
- `parallels_open()` may auto-repair writable, active images unless opened for check, inactive, or read-only.
- Allocation from backing currently reads full new clusters even when the subsequent write may overwrite most or all of them; comments call this out as inefficient.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/parallels.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/parallels.h -->
# File Research: sources/virtualization/qemu/block/parallels.h

## Purpose
Defines the shared Parallels image-format structures, constants, preallocation enum, driver state, and extension-reader prototype used by `parallels.c` and `parallels-ext.c`.

## Main Contents
- Geometry defaults: `HEADS_NUMBER`, `SEC_IN_CYL`, and `DEFAULT_CLUSTER_SIZE`.
- `ParallelsHeader`, the packed little-endian on-disk header with magic, version, geometry, BAT entry count, virtual sector count, in-use marker, data offset, flags, and extension offset.
- `ParallelsPreallocMode`, with `fallocate` and `truncate` modes.
- `BDRVParallelsState`, holding the coroutine lock, header/BAT pointers, dirty BAT bitmap, used-cluster bitmap, image extents, preallocation settings, geometry, offset multiplier, and migration blocker.
- `parallels_read_format_extension()` declaration.

## Dependencies
Includes QEMU coroutine declarations and expects block-layer types such as `BlockDriverState`, `Error`, and graph-lock annotations from surrounding includes.

## Filesystem/Block Relevance
This header is the data contract for Parallels sparse image metadata and runtime state. Its packed header layout defines the on-disk ABI used by the format driver.

## Risks and Notes
- `ParallelsHeader` is always little-endian; all users must convert fields explicitly.
- `BDRVParallelsState.lock` protects both BAT access and image extension, making it central to allocation correctness.
- Header changes are format changes and affect compatibility with Parallels/OpenVZ ploop-style images.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/parallels.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/preallocate.c -->
# File Research: sources/virtualization/qemu/block/preallocate.c

## Purpose
Implements QEMU's `preallocate` block filter. The filter sits above a child node and preallocates additional zeroed space when writes extend beyond the known file end, reducing repeated small file extensions.

## Main Entry Points
- `preallocate_open()` opens the child, parses `prealloc-align` and `prealloc-size`, initializes invalid cached state, and configures supported write/zero flags.
- `preallocate_close()` cancels the resize-drop BH and truncates the child back to the real data size when valid.
- `preallocate_reopen_prepare()`, `preallocate_reopen_commit()`, and `preallocate_reopen_abort()` handle option changes and read-only reopen behavior.
- `preallocate_co_pwritev_part()` and `preallocate_co_pwrite_zeroes()` call `handle_write()` before forwarding writes.
- `preallocate_co_truncate()` reconciles explicit user truncation/preallocation with filter-owned preallocation.
- `preallocate_set_perm()` and `preallocate_child_perm()` manage exclusive write/resize permissions and cached state validity.

## Internal Mechanics
The state tracks three boundaries:
- `data_end`: real logical data end as exposed by the filter.
- `zero_start`: start of a trailing region known to read as zero.
- `file_end`: actual child file length, including filter-owned preallocation.

When a write crosses `data_end`, `handle_write()` updates `data_end`, checks whether the write crosses `file_end`, and if needed issues `bdrv_co_pwrite_zeroes()` with `BDRV_REQ_NO_FALLBACK | BDRV_REQ_SERIALISING | BDRV_REQ_NO_WAIT` from an aligned preallocation start to an aligned preallocation end. Zero writes can be merged with the preallocation request when flags permit.

The filter keeps exclusive write and resize permissions on the child while its cached boundaries are valid. When parents no longer need write+resize, a bottom half drops extra preallocation by truncating to `data_end`, invalidates cached state, and refreshes child permissions.

## Dependencies
Uses QEMU block filter APIs, coroutine I/O, child permission callbacks, QemuOpts runtime parsing, bottom halves, and sector/request-alignment rules.

## Filesystem/Block Relevance
This filter changes allocation behavior without changing visible guest data. It is relevant for sparse-file growth, write-zeroes behavior, and the distinction between logical disk length and physically preallocated trailing zero space.

## Risks and Notes
- Cached state is valid only while the filter has exclusive child write and resize permissions.
- Errors during delayed resize dropping leave the filter holding exclusive permissions indefinitely.
- Preallocation requires aligned `prealloc-align`; it must align to both 512 bytes and the child request alignment.
- The filter reports `data_end` as length, not `file_end`, hiding trailing preallocated space from users.
- Explicit truncation with non-falloc modes may first drop filter-owned preallocation so the requested operation has the expected semantics.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/preallocate.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/progress_meter.c -->
# File Research: sources/virtualization/qemu/block/progress_meter.c

## Purpose
Provides small thread-safe helper functions for process progress tracking through QEMU's `ProgressMeter` structure.

## Main Entry Points
- `progress_init()` initializes the progress lock.
- `progress_destroy()` destroys the lock.
- `progress_get_snapshot()` reads `current` and `total` atomically under the lock.
- `progress_work_done()` increments completed work.
- `progress_set_remaining()` sets `total` to `current + remaining`.
- `progress_increase_remaining()` increments `total`.

## Internal Mechanics
All state access is protected by `pm->lock` through `QEMU_LOCK_GUARD`. The helper does not define units; callers decide what `current`, `total`, and increments mean.

## Dependencies
Uses QEMU mutex/lock guard support through coroutine/QEMU headers and the public `qemu/progress_meter.h` declaration.

## Filesystem/Block Relevance
This is support infrastructure for block operations that need progress reporting, such as image conversion, backup, mirror, or similar long-running jobs.

## Risks and Notes
- The helper performs no overflow checks on `current` or `total`.
- It provides snapshots only, not notifications or rate estimation.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/progress_meter.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qapi-system.c -->
# File Research: sources/virtualization/qemu/block/qapi-system.c

## Purpose
Implements QMP command handlers for block-device operations that are specific to QEMU system emulators: removable media tray handling, medium insertion/removal/change, legacy eject, I/O throttling, and block latency histogram configuration.

## Main Entry Points
- `qmp_get_blk()` resolves exactly one of QMP `device` or `id` to a `BlockBackend`.
- `qmp_blockdev_open_tray()` and `qmp_blockdev_close_tray()` open/close removable media trays.
- `qmp_blockdev_remove_medium()` removes a node from a backend.
- `qmp_blockdev_insert_medium()` inserts an existing node into a backend.
- `qmp_blockdev_change_medium()` opens a new image, opens/removes/inserts/closes media around the change.
- `qmp_eject()` opens the tray and removes the medium.
- `qmp_block_set_io_throttle()` translates QMP throttle fields into `ThrottleConfig`.
- `qmp_block_latency_histogram_set()` sets or clears latency histogram boundaries.

## Internal Mechanics
Tray opening checks removability, tray presence, tray-open state, and medium lock state. If locked and not forced, it sends an eject request and returns an in-progress error. Medium removal verifies removability/tray state for attached devices, checks block operation blockers for eject, removes the BDS from the backend, and updates device media callbacks for tray-less devices.

Medium insertion validates that the backend is removable or device-less, the tray is open when applicable, and no medium is already present. It rejects node insertion when the target node is already attached to a backend. `change-medium` derives open flags from the backend root state, applies read-only override policy, preserves detect-zeroes, opens the new image, opens the tray, removes old media, inserts the new BDS, and closes the tray.

Throttle handling fills every total/read/write BPS and IOPS bucket, optional burst maxima and burst lengths, optional IOPS size, validates the config, then enables, updates, or disables the backend throttle group. Histogram handling applies common or per-operation boundaries to read/write/zone-append/flush latency histograms.

## Dependencies
Uses QAPI block command types, `BlockBackend`, blockdev graph helpers, removable-media callbacks, throttle groups/config validation, block accounting histograms, and graph/main-loop locking.

## Filesystem/Block Relevance
This is the management-plane layer for runtime block-device media and performance controls. It connects QMP commands to QEMU block backends and block graph nodes.

## Risks and Notes
- `qmp_get_blk()` enforces exactly one of `device` and `id`; callers rely on its error shape.
- Some tray-related errors are intentionally ignored by higher-level commands for tray-less devices.
- `change-medium` must relinquish its opened image reference regardless of insertion success because the backend takes its own reference on success.
- Histogram clearing checks no common/read/write/flush boundaries, but append-specific presence is handled later in setting paths.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qapi-system.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qapi.c -->
# File Research: sources/virtualization/qemu/block/qapi.c

## Purpose
Implements block-layer QAPI query and human-readable dump helpers. It builds QMP response objects for block devices, block nodes, block graphs, image metadata, snapshots, block statistics, latency histograms, and format-specific information.

## Main Entry Points
- `bdrv_block_device_info()` builds `BlockDeviceInfo` for an inserted backend/node.
- `bdrv_query_snapshot_info_list()` converts internal snapshot records into QAPI `SnapshotInfoList`.
- `bdrv_query_image_info()` recursively builds `ImageInfo` for an image/backing chain.
- `bdrv_query_block_graph_info()` recursively builds full graph information including children.
- `qmp_query_block()` implements the QMP query for visible block backends.
- `qmp_query_blockstats()` reports either backend-level stats or node-level stats.
- `bdrv_snapshot_dump()`, `bdrv_image_info_specific_dump()`, and `bdrv_node_info_dump()` print human-readable monitor/qemu-img-style output.

## Internal Mechanics
`bdrv_block_device_info()` refreshes filenames, records read-only/driver/cache/encryption/active state, child node references, backing filename, dirty bitmaps, detect-zeroes, throttle settings, write threshold, and image metadata. It skips implicit filters for backend-level compatibility where appropriate.

`bdrv_do_query_node_info()` is the common node metadata builder. It reads length, allocated size, cluster size, dirty flag, block limits, format-specific info, backing filenames, and snapshot lists. Image and graph queries layer recursion on top of this base.

Stats collection splits backend accounting (`bdrv_query_blk_stats()`) from recursive node stats (`bdrv_query_bds_stats()`). Backend stats include byte/op counts, failed/invalid operations, merged counts, total latencies, idle time, timed interval stats, queue depth, and latency histograms. Node stats include node name, highest write offset, driver-specific stats, primary/data child recursion, and legacy backing recursion for backend-level queries.

Dump helpers convert QAPI objects through QObject visitors and recursively print dictionaries/lists with indentation. Node-info dumping prints image/protocol names, virtual/file length, disk size, encryption, cluster size, dirty shutdown status, backing details, block limits, snapshots, and format-specific data.

## Dependencies
Uses QAPI block-core types and visitors, QObject/QDict/QList/QNum/QBool helpers, QEMU printing utilities, block dirty bitmap queries, throttle-group APIs, write-threshold support, block accounting, and `BlockBackend` traversal.

## Filesystem/Block Relevance
This file is the reporting surface for QEMU block storage. It determines what management tools see for image topology, backing chains, allocation details, limits, snapshots, dirty bitmaps, and performance counters.

## Risks and Notes
- Backend-level queries intentionally skip implicit filters, while node-level queries stay at exact nodes.
- Recursive graph and image queries must free partially built QAPI objects on error.
- Snapshot listing treats unsupported or no-medium as recoverable for node info, but propagates other errors.
- Human-readable dumping depends on QObject conversion of QAPI structs and assumes only supported QObject types are produced.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qapi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qcow.c -->
# File Research: sources/virtualization/qemu/block/qcow.c

## Purpose
Implements QEMU's legacy `qcow` v1 image format driver. It supports sparse copy-on-write allocation, backing files, compressed clusters, deprecated AES-CBC encryption, image creation, image reads/writes, block status, and making an image empty.

## Main Entry Points
- `qcow_probe()` detects qcow v1 headers.
- `qcow_open()` opens the file child, validates the header, initializes encryption if present, loads the L1 table, allocates L2/cache buffers, reads the backing filename, blocks migration, and initializes the coroutine lock.
- `qcow_co_preadv()` reads guest data from allocated clusters, compressed clusters, backing files, or zero-fill.
- `qcow_co_pwritev()` allocates clusters as needed and writes plaintext or encrypted data.
- `qcow_co_pwritev_compressed()` compresses full clusters and stores compressed cluster descriptors.
- `qcow_co_block_status()` reports allocated/compressed/mappable state.
- `qcow_make_empty()` clears the L1 table, truncates after it, and resets the L2 cache.
- `qcow_co_create()` and `qcow_co_create_opts()` create new qcow v1 images.
- `qcow_close()` releases encryption, tables, caches, and migration blocker.

## Internal Mechanics
The format uses a big-endian header, an L1 table of L2-table offsets, and L2 tables containing cluster descriptors. `get_cluster_offset()` is the central lookup/allocation routine. It loads or allocates L2 tables, keeps a 16-entry L2 cache with hit counts, allocates data clusters at aligned EOF, handles conversion from compressed to normal clusters for partial overwrites, initializes unwritten encrypted sectors with encrypted zeros, and writes L1/L2 updates synchronously.

Reads lock the driver state while resolving cluster mappings. Unallocated clusters read from the backing file when present or return zeroes. Compressed clusters are read and inflated into `cluster_cache`. Normal clusters are read from the file; encrypted images decrypt data after reading. Multi-iov reads are staged through an aligned temporary buffer.

Writes invalidate the compressed cluster cache, stage encrypted or multi-iov data into a temporary buffer, allocate normal clusters through `get_cluster_offset()`, encrypt in place when needed, and write to the backing file child. Compressed writes deflate a cluster with raw zlib, fall back to normal writes if compression is ineffective, otherwise allocate a compressed descriptor and write compressed bytes.

Image creation writes a v1 header, optional backing filename, and zeroed L1 table. Backing images use 512-byte clusters to avoid copying unmodified sectors; standalone images use 4 KiB clusters.

## Dependencies
Uses zlib, QEMU crypto block helpers, QAPI create-option visitors, block backend creation, block debug events, migration blockers, aligned allocation, qdict option conversion, and shared block crypto option helpers.

## Filesystem/Block Relevance
This is a legacy sparse COW image implementation. It demonstrates classic table-based virtual disk allocation, backing-chain reads, compressed cluster representation, and historical in-format encryption handling.

## Risks and Notes
- qcow v1 blocks live migration through a migration blocker.
- AES-CBC encrypted qcow is deprecated and rejected in system emulators when the block whitelist is active.
- The format cannot store a backing format; create-options only validate the requested backing format.
- Request alignment is forced to 512 bytes, partly to keep encrypted-sector handling safe.
- Compressed cluster cache is single-cluster and disabled on writes.
- Many metadata updates are synchronous to preserve consistency after L1/L2 changes.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qcow.c -->