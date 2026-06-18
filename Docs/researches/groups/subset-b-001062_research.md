# subset-b-001062 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/xen-blkback/xenbus.c -->
# sources/distributed-fs/ceph-client/drivers/block/xen-blkback/xenbus.c

Purpose: Xen block backend xenbus glue. It discovers a physical block device from XenStore hotplug data, opens it as a backend VBD, maps frontend rings and event channels, advertises block features, and drives Xenbus state transitions for virtual block devices.

Important APIs/types/functions: `struct backend_info` ties a `xenbus_device`, `xen_blkif`, backend watch, device numbers, and mode string. `xen_blkif_alloc()`, `xen_blkif_alloc_rings()`, `xen_blkif_map()`, `xen_blkif_disconnect()`, and `xen_blkif_free()` manage backend interface lifetime. `xen_vbd_create()` opens the real block device through `bdev_file_open_by_dev()`. `xen_blkbk_probe()`, `backend_changed()`, `frontend_changed()`, `connect_ring()`, `read_per_ring_refs()`, and `connect()` form the Xenbus protocol path. Sysfs statistics are exposed with `VBD_SHOW_ALLRING`.

Control flow: probe allocates backend state, publishes backend capabilities, registers a watch on `physical-device`, and enters `InitWait`. The backend watch reads `physical-device`, `mode`, optional cdrom type, and frontend handle, then creates the VBD and sysfs attributes. Frontend state changes trigger ring teardown, ring reference parsing, shared ring mapping, event-channel binding, and status update. Once rings and VBD are ready, `connect()` writes features, geometry, sector sizes, and switches to `Connected`; per-ring kthreads are started by `xen_update_blkif_status()`.

State and persistence: state lives in XenStore, the open `bdev_file`, per-ring grant/page caches, pending request lists, irq bindings, and kthreads. Persistent grants are module-parameter controlled and negotiated per VBD. Disconnect waits for kthreads, refuses full teardown while inflight I/O remains, unmaps rings, frees caches, validates counters, and clears `nr_ring_pages`, `rings`, and `nr_rings`.

Dependencies and integration: depends on Xenbus, grant tables, event channels, blkback common request handling, Linux block-device open/flush/cache APIs, sysfs, and kthreads. It integrates with blkback request execution through ring interrupts and `xen_blkif_schedule()` in the shared backend code.

Risks: untrusted frontend input controls queue count, protocol, ring page order, event channels, and grant refs, so bounds checks are critical. `BUG_ON()` assertions during disconnect can panic if grant accounting is corrupted. Error paths in multi-queue ring setup rely on later `xen_blkif_disconnect()` cleanup. Reconnect paths must not leak old ring grants or pending request allocations. `xen_update_blkif_status()` starts multiple kthreads after changing Xenbus state; partial startup failure must stop already-started threads.

Test signals: exercise XenStore hotplug missing/invalid `physical-device`, readonly vs writable mode, feature publication, single and multi-queue rings, ring-page-order limits, reconnect after frontend close/reopen, backend removal with inflight I/O, persistent grant enable/disable, discard/flush feature reporting, and sysfs statistic aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/xen-blkback/xenbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/xen-blkfront.c -->
# sources/distributed-fs/ceph-client/drivers/block/xen-blkfront.c

Purpose: Xen virtual block frontend driver. It presents Xen VBDs as Linux block devices, negotiates rings/features with a backend, converts blk-mq requests into Xen blkif requests, manages grant references, and recovers across suspend/resume or backend restart.

Important APIs/types/functions: `struct blkfront_info` is the device state; `struct blkfront_ring_info` is per queue/ring; `struct blk_shadow` tracks in-flight ring slots, grants, sg lists, status, and paired extra requests. Key paths are `blkfront_probe()`, `talk_to_blkback()`, `negotiate_mq()`, `setup_blkring()`, `blkfront_connect()`, `xlvbd_alloc_gendisk()`, `blkif_queue_rq()`, `blkif_queue_rw_req()`, `blkif_queue_discard_req()`, `blkif_interrupt()`, `blkif_completion()`, `blkfront_resume()`, and `blkfront_remove()`.

Control flow: probe records virtual-device metadata and waits for backend state. When the backend enters `InitWait`, the frontend creates ring pages/event channels, writes ring refs, queue count, protocol, and persistent-grant preference to XenStore, then switches to `Initialised`. On backend `Connected`, it gathers backend geometry and features, allocates grants/indirect pages/shadow arrays, creates a blk-mq gendisk, switches to `Connected`, and starts queues. I/O submission maps request segments to grants, optionally builds indirect descriptors or a second request, publishes ring entries, and notifies the backend. Interrupts validate responses, release or retain grants, update feature support on `EOPNOTSUPP`, and complete blk-mq requests.

State and persistence: persistent state includes XenStore fields, minor bitmap reservations, per-ring grants, indirect pages, shadow freelists, delayed persistent-grant purge work, gendisk/queue structures, and saved bios/requests during resume. On suspend/reconnect, existing block-device structures remain while rings are torn down and rebuilt; pending bios and special requests are requeued after features are renegotiated.

Dependencies and integration: depends on Xenbus, Xen event channels, grant-table APIs, Xen blkif protocol definitions, blk-mq, gendisk, request queue limits, scatterlist mapping, workqueues, and block zoned/discard/flush capability plumbing. It integrates with `/dev/xvd*` naming and Xen HVM/PV disk discovery rules.

Risks: the backend may be untrusted, so response id, operation, ring producer overflow, grant lifetime, and feature revocation checks are essential. Persistent grants deliberately keep mappings live and require periodic purge. Bounce buffers are forced for untrusted or persistent-grant paths and must avoid stale data exposure. Extra-request handling for large page sizes depends on paired shadow state. Error state intentionally suppresses late EOI to stop further interrupts.

Test signals: validate boot discovery, HVM filtering, frontend/backend state transitions, capacity change notifications, single/multi queue negotiation, ring-page-order negotiation, discard/secure erase/flush/FUA downgrade, direct vs bounce-buffer I/O, indirect descriptor and extra-request paths, suspend/resume requeue, persistent grant purge, malformed backend responses, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/xen-blkfront.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/z2ram.c -->
# sources/distributed-fs/ceph-client/drivers/block/z2ram.c

Purpose: Amiga-specific RAM disk block driver exposing unused Zorro II RAM, Chip RAM, or selected memory-list entries as `/dev/z2ram*` devices for swap or ramdisk use.

Important APIs/types/functions: global state includes `z2ram_map`, `z2ram_size`, memory counters, `current_device`, per-minor `gendisk` pointers, a global mutex, and an I/O spinlock. `z2_queue_rq()` copies request data between block bios and mapped RAM chunks. `get_z2ram()` consumes bits from `zorro_unused_z2ram`; `get_chipram()` allocates Chip RAM chunks. `z2_open()` selects memory according to the minor, builds the chunk map, and sets capacity. `z2_init()` registers the fixed major, blk-mq tag set, and disks.

Control flow: module init only succeeds on Amiga hardware, registers major 37, initializes a single-queue blk-mq tag set, and creates minors. Opening a minor lazily claims the selected memory pool and fixes the driver to that single active minor. Requests bounds-check sector ranges, translate logical offsets through `z2ram_map`, and copy under `z2ram_lock`. Exit unregisters disks and returns claimed Zorro/Chip memory where implemented.

State and persistence: all backing storage is volatile physical RAM. The active minor and map are global, so only one configuration can be open at a time. Zorro RAM is marked used by clearing `zorro_unused_z2ram` and partially restored on module exit. Release does not tear down the active mapping and contains a FIXME for unmapping memory.

Dependencies and integration: depends on m68k/Amiga setup, `amigahw`, Zorro memory metadata, Chip RAM allocation APIs, low-level remapping for memory-list entries, and blk-mq/gendisk block APIs.

Risks: global single-device state makes concurrent opens sensitive; release is incomplete; memory-list mappings have architecture-specific remap behavior; request handling assumes the request bio buffer can be copied directly for the current segment; cleanup is asymmetric for list-entry mappings. Fixed major/minor layout constrains extension.

Test signals: test Amiga-only probe rejection elsewhere, each minor mode, invalid memory-list indexes, no-memory cases, read/write across chunk boundaries, out-of-range I/O, repeated opens of same vs different minors, module unload memory restoration, and blk-mq error return behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/z2ram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zloop.c -->
# sources/distributed-fs/ceph-client/drivers/block/zloop.c

Purpose: zoned loop block driver that exposes a zoned block device backed by one file per zone under a configured directory. A misc control device accepts add/remove commands and each created `zloopN` disk implements conventional and sequential zones.

Important APIs/types/functions: `struct zloop_options` holds parsed control options. `struct zloop_device` owns blk-mq state, disk, workqueue, base directory, per-zone files, zone geometry, open-zone LRU, and behavior flags. `struct zloop_zone` tracks file, locks, flags, condition, start, write pointer, and original GFP mask. Key functions are `zloop_ctl_write()`, `zloop_parse_options()`, `zloop_ctl_add()`, `zloop_ctl_remove()`, `zloop_init_zone()`, `zloop_queue_rq()`, `zloop_rw()`, zone management helpers, `zloop_report_zones()`, and cache safety helpers using `user.zloop.wp`.

Control flow: users write `add` or `remove` to `/dev/zloop-control`. Add parses geometry and behavior, allocates an id, opens the data directory, creates/restores per-zone files, determines block size, allocates blk-mq/gendisk, validates zones, and publishes `zloopN`. I/O is queued to a per-device workqueue. Reads/writes call file `read_iter`/`write_iter`; sequential writes enforce write-pointer placement, implicit open, full transitions, and optional ordered zone append. Zone operations open, close, reset, finish, or reset all sequential zones.

State and persistence: backing data persists in zone files. Sequential zone state is inferred from file size and in-memory write pointers; `ZLOOP_ZONE_SEQ_ERROR` forces stat-based repair on next operation. Optional discard-write-cache records safe write pointers in xattrs during flush and truncates back to those on remove. Open zones are tracked in an LRU list for max-open-zone enforcement.

Dependencies and integration: depends on blk-mq, zoned block APIs, VFS file I/O, truncate/stat/xattr, miscdevice control, parser helpers, workqueues, and filesystem sync. It integrates with block zoned reporting and queue limits including zone append and max open zones.

Risks: correctness depends on backing filesystem support for direct I/O alignment, xattrs, truncation, and durable sync. Ordered zone append advances the write pointer before work execution; failed writes rely on later recovery. `zloop_finish_zone()` truncates to `zone_size` although sequential capacity may be smaller, which should be checked against intended semantics. Deletion races are guarded by state checks but queued work must drain through gendisk teardown. Restore validation must match existing files to requested geometry.

Test signals: add/remove parsing, invalid capacities/zone sizes, restore from existing files, conventional and sequential I/O, short read zero-fill, partial write failure, zone reset/open/close/finish/report, max-open-zones LRU behavior, ordered vs unordered append, buffered vs direct I/O, xattr cache discard, filesystem sync failure, and remove while device is open or I/O is queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zloop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/block/zram/Kconfig

Purpose: Kconfig menu for the zram compressed RAM block device and its selectable compression backends/features.

Important symbols: `ZRAM` enables the driver and selects `ZSMALLOC`. Backend booleans select LZ4, LZ4HC, ZSTD, DEFLATE, 842, and LZO/LZO-RLE libraries. `ZRAM_BACKEND_FORCE_LZO` guarantees LZO support when no other backend is selected. The default compressor choice emits `ZRAM_DEF_COMP`. Optional features include `ZRAM_WRITEBACK`, `ZRAM_TRACK_ENTRY_ACTIME`, `ZRAM_MEMORY_TRACKING`, and `ZRAM_MULTI_COMP`.

Control flow and state: this file has no runtime control flow; it controls compilation, default strings, and dependency closure. The default compressor choice is constrained by enabled backend symbols. Memory tracking selects access-time tracking.

Dependencies and integration: integrates zram with block, sysfs, MMU, zsmalloc, compression libraries, debugfs, writeback support, and admin documentation.

Risks: invalid combinations are mostly prevented by dependencies, but default compressor availability depends on matching backend selection. The force-LZO fallback changes configuration even when a user did not explicitly choose LZO.

Test signals: config matrix builds for each backend, no-backend fallback to LZO, default compressor string correctness, writeback/access-time/debugfs combinations, and multi-compressor builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/Makefile -->
# sources/distributed-fs/ceph-client/drivers/block/zram/Makefile

Purpose: kernel build wiring for the zram module.

Important entries: `zram-y` always includes `zcomp.o` and `zram_drv.o`. Conditional `zram-$(CONFIG_ZRAM_BACKEND_*)` entries add backend object files. `obj-$(CONFIG_ZRAM) += zram.o` emits the module or built-in object according to `CONFIG_ZRAM`.

Control flow and state: no runtime behavior. Build-time object inclusion follows Kconfig backend symbols.

Dependencies and integration: integrates the compression frontend and backend object files into the zram driver target.

Risks: Kconfig and Makefile must stay synchronized. Adding a backend requires both a symbol and a conditional object entry. LZO adds both `backend_lzorle.o` and `backend_lzo.o`.

Test signals: build zram as built-in and module with each backend combination; verify all declared backend symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_842.c -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_842.c

Purpose: zram compression backend adapter for the kernel software 842 compressor.

Important APIs/types/functions: implements `const struct zcomp_ops backend_842`. `create_842()` allocates `SW842_MEM_COMPRESS` workspace, `destroy_842()` frees it, `compress_842()` calls `sw842_compress()`, and `decompress_842()` calls `sw842_decompress()`.

Control flow and state: setup/release params are no-ops; each per-CPU zcomp context has a private compression workspace. Compression updates `req->dst_len` only on success; decompression uses a local output length.

Dependencies and integration: depends on `linux/sw842.h` and the common zcomp request/ops abstraction. Compiled only when the 842 backend is enabled.

Risks: return codes are passed through directly from sw842, unlike some backends that normalize to `-EINVAL`; callers must tolerate that. Decompression does not write the final decompressed length back to `req->dst_len`, matching zram's fixed-page expectation.

Test signals: backend creation under memory pressure, round-trip compression/decompression of pages, incompressible data behavior, and error-code propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_842.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_842.h -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_842.h

Purpose: declaration header for the zram 842 backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_842`.

Control flow and state: no runtime control flow or mutable state.

Dependencies and integration: allows `zcomp.c` to reference the backend ops table when `CONFIG_ZRAM_BACKEND_842` is enabled.

Risks: declaration must match the C file symbol name; include guard prevents duplicate declarations.

Test signals: compile with 842 backend enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_842.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_deflate.c -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_deflate.c

Purpose: zram backend adapter for raw deflate through kernel zlib.

Important APIs/types/functions: `struct deflate_ctx` owns separate compression and decompression `z_stream_s` objects. `deflate_setup_params()` defaults compression level and negative raw-window `winbits`. `deflate_create()` allocates zlib workspaces and initializes streams. `deflate_compress()` resets and finishes a deflate stream; `deflate_decompress()` resets and inflates with sync flush. `backend_deflate` exports zcomp ops.

Control flow and state: immutable params set level/window once per `zcomp`; mutable zlib streams live per CPU context. Destroy ends initialized streams and frees workspaces.

Dependencies and integration: depends on `linux/zlib.h`, vmalloc workspaces, and the common zcomp frontend. Uses raw deflate defaults matching the crypto API value.

Risks: most zlib failures collapse to `-EINVAL`, losing detail. Error cleanup must only end streams with allocated workspaces. Tuned `winbits` compatibility matters for data generated by previous settings.

Test signals: default and explicit level/window setup, failed workspace allocation, round-trip pages, malformed compressed input, and stream reuse across many requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_deflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_deflate.h -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_deflate.h

Purpose: declaration header for the deflate zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_deflate`.

Control flow and state: none.

Dependencies and integration: consumed by `zcomp.c` backend registration when deflate support is configured.

Risks: only symbol/header synchronization risk.

Test signals: compile coverage with `CONFIG_ZRAM_BACKEND_DEFLATE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_deflate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4.c -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4.c

Purpose: zram backend adapter for LZ4 fast compression, with optional dictionary support.

Important APIs/types/functions: `struct lz4_ctx` holds either raw workspace memory or dictionary-capable compression/decode streams. `lz4_setup_params()` defaults acceleration and loads an optional dictionary into `params->drv_data`. `lz4_compress()` calls `LZ4_compress_fast()` or `LZ4_compress_fast_continue()`. `lz4_decompress()` calls safe LZ4 decode APIs.

Control flow and state: dictionary-less contexts allocate `LZ4_MEM_COMPRESS`; dictionary contexts allocate per-CPU stream structs and copy/reset dictionary state for each request. Params release frees the shared dictionary stream.

Dependencies and integration: depends on kernel LZ4 compression/decompression APIs and zcomp ops.

Risks: dictionary size must be fully accepted by `LZ4_loadDict()` or setup fails. Compression failure is normalized to `-EINVAL`. Dictionary stream reset correctness is central to reproducible compressed output.

Test signals: no-dictionary round trips, dictionary setup and repeated requests, invalid dictionary acceptance, acceleration levels, and decompression of malformed data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4.h -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4.h

Purpose: declaration header for the LZ4 zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_lz4`.

Control flow and state: none.

Dependencies and integration: used by the zcomp backend registry.

Risks: symbol mismatch only.

Test signals: compile coverage with `CONFIG_ZRAM_BACKEND_LZ4`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4hc.c -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4hc.c

Purpose: zram backend adapter for high-compression LZ4HC, including dictionary-capable operation.

Important APIs/types/functions: `struct lz4hc_ctx` stores either `LZ4HC_MEM_COMPRESS` workspace or HC/decode streams. `lz4hc_setup_params()` defaults compression level. `lz4hc_compress()` uses `LZ4_compress_HC()` or resets/loads a dictionary into `LZ4_streamHC_t` before `LZ4_compress_HC_continue()`. `lz4hc_decompress()` mirrors LZ4 safe decompression.

Control flow and state: setup has no shared driver data; per-CPU context owns all mutable stream/workspace state. Dictionary mode reloads the provided dictionary each request.

Dependencies and integration: depends on kernel LZ4HC/LZ4 APIs and zcomp.

Risks: higher compression may increase CPU latency in zram write paths. Dictionary load mismatch returns `-EINVAL`. Allocation failures currently return `-EINVAL` in create error handling rather than `-ENOMEM`.

Test signals: default and explicit compression levels, dictionary and no-dictionary round trips, compression failure with too-small destination, and malformed input decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4hc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4hc.h -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4hc.h

Purpose: declaration header for the LZ4HC zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_lz4hc`.

Control flow and state: none.

Dependencies and integration: used by zcomp conditional backend registration.

Risks: symbol/header drift.

Test signals: compile with LZ4HC enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4hc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzo.c -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzo.c

Purpose: zram backend adapter for classic LZO1X compression.

Important APIs/types/functions: `lzo_create()` allocates `LZO1X_MEM_COMPRESS` workspace, `lzo_destroy()` frees it, `lzo_compress()` calls `lzo1x_1_compress()`, `lzo_decompress()` calls `lzo1x_decompress_safe()`, and `backend_lzo` publishes zcomp ops.

Control flow and state: no params are used. Each runtime context has one compression workspace. LZO return `LZO_E_OK` maps to zero; other codes pass through.

Dependencies and integration: depends on `linux/lzo.h` and zcomp. It is included together with lzo-rle when LZO backend support is enabled.

Risks: nonzero LZO library error codes are not normalized to Linux errno. Workspace allocation is a write-path prerequisite for every CPU stream.

Test signals: round-trip pages, incompressible data, malformed input, and memory allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzo.h -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzo.h

Purpose: declaration header for the LZO zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_lzo`.

Control flow and state: none.

Dependencies and integration: used by `zcomp.c` for backend lookup.

Risks: symbol mismatch.

Test signals: compile with LZO backend enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzorle.c -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzorle.c

Purpose: zram backend adapter for LZO-RLE compression with LZO-compatible safe decompression.

Important APIs/types/functions: mirrors the LZO backend with `lzorle_create()`, `lzorle_destroy()`, `lzorle_compress()` using `lzorle1x_1_compress()`, `lzorle_decompress()` using `lzo1x_decompress_safe()`, and `backend_lzorle` named `lzo-rle`.

Control flow and state: no params; per-CPU context owns the LZO workspace. Compression/decompression return zero on `LZO_E_OK`, otherwise library code.

Dependencies and integration: depends on `linux/lzo.h`, zcomp, and the LZO backend Kconfig option.

Risks: same error-code normalization concern as LZO. Compatibility relies on standard LZO decompressor accepting LZO-RLE output.

Test signals: round-trip RLE-heavy and random pages, malformed input, and allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzorle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzorle.h -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzorle.h

Purpose: declaration header for the LZO-RLE zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_lzorle`.

Control flow and state: none.

Dependencies and integration: consumed by zcomp's backend list.

Risks: symbol/header drift.

Test signals: compile with LZO backend support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzorle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_zstd.c -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_zstd.c

Purpose: zram backend adapter for Zstandard compression, supporting default compression contexts and optional dictionaries.

Important APIs/types/functions: `struct zstd_ctx` owns per-CPU compression/decompression contexts and optional workspace memory. `struct zstd_params` stores shared custom allocator, prepared cdict/ddict, and compression parameters. `zstd_setup_params()` chooses level, computes params, and creates dictionaries by reference. `zstd_create()` builds per-CPU contexts using embedded vmalloc workspaces without a dictionary or advanced allocation with dictionaries. `zstd_compress()` and `zstd_decompress()` dispatch to dictionary or non-dictionary APIs.

Control flow and state: shared params live in `params->drv_data`; per-CPU contexts are separate. Custom allocation uses `GFP_NOIO | __GFP_NOWARN`. Destroy frees embedded workspaces or explicit zstd contexts based on which allocation path was used.

Dependencies and integration: depends on kernel zstd APIs, zcomp, vmalloc, and kvfree/kzalloc helpers.

Risks: dictionary objects are by-reference, so the dictionary buffer lifetime must exceed backend use. In `zstd_create()` error handling calls `zstd_release_params(params)`, which releases shared params from a per-context creation failure and can affect other contexts during initialization cleanup. Memory use can be high for zstd workspaces.

Test signals: no-dictionary and dictionary round trips, default level behavior, invalid dictionary setup, allocation failure at each context stage, malformed input, and teardown after partial CPU context creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_zstd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_zstd.h -->
# sources/distributed-fs/ceph-client/drivers/block/zram/backend_zstd.h

Purpose: declaration header for the Zstandard zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_zstd`.

Control flow and state: none.

Dependencies and integration: used by zcomp when ZSTD backend support is configured.

Risks: symbol/header synchronization only.

Test signals: compile with ZSTD backend enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/backend_zstd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/zcomp.c -->
# sources/distributed-fs/ceph-client/drivers/block/zram/zcomp.c

Purpose: dynamic compression frontend for zram. It registers configured backend ops, allocates per-CPU compression streams, handles CPU hotplug, and exposes compressor lookup/availability helpers.

Important APIs/types/functions: `backends[]` is the conditional backend registry. `lookup_backend_ops()`, `zcomp_lookup_backend_name()`, and `zcomp_available_show()` serve sysfs/config selection. `zcomp_strm_init()` and `zcomp_strm_free()` create backend contexts plus page-sized scratch buffers. `zcomp_stream_get()`/`put()` lock a per-CPU stream safely across CPU hotplug. `zcomp_compress()` and `zcomp_decompress()` wrap backend ops. `zcomp_create()`, `zcomp_init()`, and `zcomp_destroy()` manage full compressor lifetime.

Control flow: create validates backend name, allocates `struct zcomp`, sets ops, allocates per-CPU streams, lets the backend setup immutable params, initializes stream locks, and registers a CPU hotplug instance. CPU-up initializes streams; CPU-dead frees them under the stream lock. Compression gets a locked stream, builds a `zcomp_req` for one page and a two-page output buffer, and delegates to the backend.

State and persistence: per-device `zcomp_params` are shared and backend-owned `drv_data` may persist for the compressor lifetime. Per-CPU `zcomp_strm` contains mutable backend context, compressed buffer, and local copy buffer. Stream `buffer == NULL` marks a stream destroyed during CPU hotplug and makes `zcomp_stream_get()` retry after migration.

Dependencies and integration: depends on all enabled backend headers, cpuhp state `CPUHP_ZCOMP_PREPARE`, vmalloc, sysfs formatting, mutexes, and zram driver callers.

Risks: backends must implement setup/release/create/destroy consistently or hotplug cleanup can leak or double-free. `zcomp_stream_get()` loops until it lands on a live CPU stream; CPU hotplug races are handled by lock and NULL-buffer retry. The two-page compression buffer assumes zram handles incompressible pages outside the backend.

Test signals: backend lookup with sysfs-style strings, available compressor formatting, create/destroy under each backend, CPU hotplug online/offline, compression/decompression round trips, backend setup failure cleanup, and concurrent stream users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/zcomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/zcomp.h -->
# sources/distributed-fs/ceph-client/drivers/block/zram/zcomp.h

Purpose: shared zram compression abstraction between the zram driver, the compression frontend, and backend adapters.

Important APIs/types/functions: `ZCOMP_PARAM_NOT_SET` marks unset tunables. `struct zcomp_params` contains shared dictionary, level, deflate-specific params, and backend private data. `struct zcomp_ctx` is mutable per-stream backend context. `struct zcomp_strm` adds a mutex, compression buffer, local copy buffer, and context. `struct zcomp_req` describes one compression/decompression operation. `struct zcomp_ops` is the backend vtable. `struct zcomp` binds per-CPU streams, ops, params, and a CPU-hotplug node.

Control flow and state: the header defines contracts only. Backend setup/release operates on shared params; create/destroy operates on runtime contexts; compress/decompress operates on requests and can mutate context. Public functions cover CPU hotplug, availability display, lookup, create/destroy, stream locking, and request execution.

Dependencies and integration: depends on kernel mutex definitions and is included by every backend plus `zcomp.c`. It is the integration boundary between zram device logic and compression libraries.

Risks: params are shared across contexts and must be treated as immutable after setup except for backend-owned data. Contexts are not shareable and rely on `zcomp_stream_get()` locking. Backend return-code conventions vary, so frontend callers should treat any nonzero as failure.

Test signals: compile all backend implementations against vtable signature, validate unset parameter defaults, and test concurrent per-CPU stream use through the public API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/zcomp.h -->
