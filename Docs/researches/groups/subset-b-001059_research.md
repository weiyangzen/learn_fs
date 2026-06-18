# subset-b-001059 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/zoned.c -->
# sources/distributed-fs/ceph-client/drivers/block/null_blk/zoned.c

## Purpose
Implements zoned block device behavior for the `null_blk` synthetic block driver. It lets null_blk emulate conventional and sequential write required zones, write pointers, zone append, zone management commands, max active/open zone limits, optional memory-backed contents, badblocks interaction, and configfs-driven read-only/offline zone condition injection.

## Important APIs, Types, And Functions
The file works against `struct nullb_device`, `struct nullb`, `struct nullb_cmd`, and `struct nullb_zone` from `null_blk.h`, and Linux block layer zone types and request operations. Public entry points used by the rest of null_blk are `null_init_zoned_dev()`, `null_register_zoned_dev()`, `null_free_zoned_dev()`, `null_report_zones()`, `null_zone_valid_read_len()`, `null_process_zoned_cmd()`, and `zone_cond_store()`.

`null_init_zoned_dev()` validates power-of-two zone size, capacity constraints, smaller-last-zone rules, max active/open limits, and initializes each zone's type, start, length, capacity, condition, write pointer, and per-zone lock. It also programs `queue_limits` with `BLK_FEAT_ZONED`, chunk size, zone append maximum, and resource limits.

`null_zone_write()` is the core write path. Conventional zones pass through to `null_process_cmd()`. Sequential zones enforce write-at-WP semantics, implement zone append by rewriting the request sector, optionally enforce active/open resources, process badblocks and memory backing, advance `zone->wp`, and transition to `FULL` at capacity.

Zone management is implemented by `null_open_zone()`, `null_close_zone()`, `null_finish_zone()`, `null_reset_zone()`, and `null_zone_mgmt()`. Resource accounting is centralized in `null_check_active()`, `null_check_open()`, `null_check_zone_resources()`, and `null_close_imp_open_zone()`.

## Control Flow
Device setup calls `null_init_zoned_dev()`, then registration calls `blk_revalidate_disk_zones()` through `null_register_zoned_dev()`. Reads and writes later enter `null_process_zoned_cmd()`. Writes and zone appends go to `null_zone_write()`, management commands go to `null_zone_mgmt()`, and all other operations are passed through under the target zone lock after rejecting offline zones.

Zone reporting computes the first zone from the requested sector, copies zone state under the zone lock, and calls `disk_report_zone()` with a local `struct blk_zone` to avoid allowing stacked devices to mutate the internal zone array. Configfs writes through `zone_cond_store()` parse a sector, find the zone, reject non-zoned/unpowered/conventional-zone cases, and toggle read-only or offline state through `null_set_zone_cond()`.

## State And Persistence Behavior
All zone state is in memory in `dev->zones`: type, condition, start, length, capacity, write pointer, and lock. Resource state is kept in device counters: `nr_zones_exp_open`, `nr_zones_imp_open`, `nr_zones_closed`, `zone_max_active`, `zone_max_open`, `need_zone_res_mgmt`, and `imp_close_zone_no`. There is no persistent metadata; module/device teardown frees the zone array. If `memory_backed` is enabled, writes, resets, and condition toggles affect the in-memory data store through null_blk memory helpers.

Locking switches by backing mode: non-memory-backed zones use spinlocks, while memory-backed zones use mutexes because `null_handle_memory_backed()` and discard paths can sleep. Resource counters are guarded by `zone_res_lock`.

## Dependencies And Integration Points
This code integrates with null_blk main command processing, null_blk configfs attributes, block zoned APIs (`blk_revalidate_disk_zones`, `disk_report_zone`), request operations (`REQ_OP_ZONE_*`, `REQ_OP_ZONE_APPEND`), tracepoints in `trace.h`, badblocks handling, and optional memory-backed data handling. It is built when null_blk and zoned block support are enabled.

## Risks
The highest-risk behavior is correct synchronization between per-zone locks and `zone_res_lock`, because resource counters must match zone condition transitions. Boundary handling is also critical: smaller last zones, `zone_capacity < zone_size`, write pointer overflow, and zone append maximum alignment all affect block-layer correctness. Memory-backed paths use mutexes to avoid sleeping under spinlock; future changes must preserve that distinction. `null_finish_zone()` sets `wp` to `start + len` rather than `start + capacity`, which is intentional in current code but is a detail to recheck when changing capacity semantics. Configfs condition toggling invalidates write pointers with `NULL_ZONE_INVALID_WP`, so write and report paths must continue to handle invalid WPs safely.

## Test Signals
Good signals include `blktests` zoned block tests, fio zoned workloads with regular write and zone append, zone reset/open/close/finish command tests, configfs toggling of read-only/offline zones, memory-backed read-after-write and reset/discard checks, badblocks injection, and limit tests for max active/open resources. Tracepoints `trace_nullb_report_zones()` and `trace_nullb_zone_op()` are useful for confirming state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/zoned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/ps3disk.c -->
# sources/distributed-fs/ceph-client/drivers/block/ps3disk.c

## Purpose
Implements the PlayStation 3 disk block driver. It exposes PS3 hypervisor storage regions as Linux block devices and translates blk-mq read, write, and flush requests into LV1 storage calls using a single 64 KiB DMA bounce buffer.

## Important APIs, Types, And Functions
`struct ps3disk_private` stores the blk-mq tag set, gendisk, current request, block-size conversion factor, raw capacity, model string, and spinlock. `struct lv1_ata_cmnd_block` models the command block used for ATA IDENTIFY through LV1.

The blk-mq entry point is `ps3disk_queue_rq()`, backed by `ps3disk_do_request()`, `ps3disk_submit_request_sg()`, and `ps3disk_submit_flush_request()`. Interrupt completion is handled by `ps3disk_interrupt()`. Probe/remove lifecycle is implemented by `ps3disk_probe()` and `ps3disk_remove()`, and module setup uses `ps3disk_init()` and `ps3disk_exit()`.

ATA helper functions copied from libata, including `ata_id_n_sectors()` and `ata_id_c_string()`, decode capacity and model information after `ps3disk_identify()` sends `ATA_CMD_ID_ATA`.

## Control Flow
Module init first checks `FW_FEATURE_PS3_LV1`, registers a dynamic block major, and registers a `ps3_system_bus_driver` matching PS3 storage disk devices. Probe reserves a disk index, allocates private state and a DMA bounce buffer, calls `ps3stor_setup()` with the interrupt handler, identifies the disk, allocates a single-queue blk-mq tag set and disk, sets queue limits, sets capacity from the selected PS3 storage region, and publishes the disk.

For I/O, `ps3disk_queue_rq()` starts the request, takes `priv->lock`, and submits it. Reads and writes are converted from Linux 512-byte sectors to device block sectors using `blocking_factor`. Writes gather request segments into `dev->bounce_buf` before `lv1_storage_write()`. Reads call `lv1_storage_read()` and scatter the bounce buffer back to bio segments in the interrupt handler. Flushes issue `LV1_STORAGE_ATA_HDDOUT`. On completion, `ps3disk_interrupt()` fetches async status, checks the tag, completes non-block-layer commands through `dev->done`, or ends the block request and restarts hardware queues.

## State And Persistence Behavior
The driver does not own persistent metadata. Persistent data is the physical PS3 disk content behind LV1 storage. Runtime state includes one outstanding block request in `priv->req`, a global disk-index bitmap `ps3disk_mask`, the bounce buffer and logical partition address managed by PS3 storage helpers, and cached capacity/model information. Removal clears the bitmap bit, deletes the disk, synchronizes disk cache, tears down PS3 storage, frees the bounce buffer and private data, and clears driver data.

## Dependencies And Integration Points
Depends on PS3 platform firmware and hypervisor interfaces (`asm/lv1call.h`, `asm/ps3stor.h`, `FW_FEATURE_PS3_LV1`), blk-mq, Linux ATA identify helpers/macros, and the PS3 system bus. It is wired from the parent block `Makefile` under `CONFIG_PS3_DISK` and aliases `PS3_MODULE_ALIAS_STOR_DISK`.

## Risks
The single `priv->req` field means the queue model depends on one in-flight request at a time; queue-depth changes would require careful redesign. The 64 KiB bounce buffer caps hardware request size and all segment copying must stay within queue limits. Interrupt code logs tag mismatches but still proceeds, so request/tag consistency is important. Error handling around `ps3disk_identify()` is permissive: probe continues after identify failure, which may leave model/capacity metadata incomplete but capacity still comes from the PS3 region. Cache flush during remove is best-effort and hardware-specific.

## Test Signals
Meaningful testing requires PS3 LV1 hardware or an emulator with compatible storage behavior. Signals include successful probe logs with model/capacity, read/write filesystem smoke tests, flush/fsync tests, removal/shutdown cache sync, request failure injection from LV1 calls, and boot/module load on non-PS3 platforms returning `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/ps3disk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/ps3vram.c -->
# sources/distributed-fs/ceph-client/drivers/block/ps3vram.c

## Purpose
Exposes PlayStation 3 GPU video RAM as a Linux block device. The driver allocates RSX/GPU memory through LV1, maps a 2 MiB XDR system-memory buffer into the GPU context, uses the FIFO DMA engine to move pages between XDR and VRAM, and maintains a small write-back cache to service block bios.

## Important APIs, Types, And Functions
`struct ps3vram_priv` owns the gendisk, VRAM size, LV1 memory/context handles, MMIO control/report mappings, XDR buffer, FIFO pointers, cache, spinlock, and queued bio list. `struct ps3vram_cache` stores cache geometry, tags, and hit/miss counters; each `struct ps3vram_tag` records VRAM page address and present/dirty flags.

Hardware/FIFO helpers include `ps3vram_notifier_reset()`, `ps3vram_notifier_wait()`, `ps3vram_init_ring()`, `ps3vram_wait_ring()`, `ps3vram_begin_ring()`, `ps3vram_fire_ring()`, `ps3vram_bind()`, `ps3vram_upload()`, and `ps3vram_download()`. Cache and I/O helpers are `ps3vram_cache_match()`, `ps3vram_cache_evict()`, `ps3vram_cache_load()`, `ps3vram_cache_flush()`, `ps3vram_read()`, `ps3vram_write()`, `ps3vram_do_bio()`, and `ps3vram_submit_bio()`.

## Control Flow
Module init checks PS3 LV1 firmware, registers a dynamic block major, and registers a PS3 GPU RAM disk system-bus driver. Probe allocates private state and a 2 MiB XDR buffer, opens the GPU HV device, allocates as much GPU memory as possible up to the `size` module parameter, allocates a GPU context, maps XDR into the context, ioremaps control and reports areas, initializes and binds FIFO channels, initializes cache tags, creates `/proc/ps3vram`, allocates a no-partition disk, sets capacity to allocated VRAM, and adds the disk.

The block layer calls `ps3vram_submit_bio()` directly through `submit_bio`. Bios are serialized by `priv->list`: the first submitter drains the list synchronously with `ps3vram_do_bio()`, while later bios queue and return. Each bio segment is mapped with `bvec_virt()` and serviced by `ps3vram_read()` or `ps3vram_write()`. Cache misses evict a random entry, write back dirty contents with `ps3vram_upload()`, then load the requested page with `ps3vram_download()`. Writes update the XDR cache copy and set `CACHE_PAGE_DIRTY`; dirty pages reach VRAM on eviction or cleanup.

## State And Persistence Behavior
The block contents live in allocated GPU memory and disappear when the driver releases that memory. Dirty data can remain in XDR cache until eviction or `ps3vram_cache_flush()` during cleanup, so orderly remove/shutdown matters. Runtime state includes FIFO positions, cache tags, hit/miss counters exported through `/proc/ps3vram`, queued bios, LV1 handles, and MMIO mappings. There is no durable metadata or partition scanning (`GENHD_FL_NO_PART`).

## Dependencies And Integration Points
Depends on PS3 platform headers and LV1 GPU APIs (`ps3_open_hv_device`, `lv1_gpu_memory_allocate`, `lv1_gpu_context_allocate`, `lv1_gpu_context_iomap`, `lv1_gpu_fb_blit`), global `ps3_gpu_mutex`, Linux block `submit_bio`, procfs, and system-bus matching `PS3_MATCH_ID_GPU` plus `PS3_MATCH_SUB_ID_GPU_RAMDISK`. Parent block build logic includes it under `CONFIG_PS3_VRAM`.

## Risks
This driver is tightly coupled to RSX FIFO details and big-endian MMIO ordering; regressions are hard to validate without real hardware. I/O is synchronous and serialized, so stalls in notifier or FIFO wait paths can block submitters. Cache replacement uses `jiffies` plus a static counter and is not optimized for performance. Dirty cache writeback errors are logged but cannot reliably recover user data. The code assumes PS3 ppc64 has no highmem for bio segment virtual mapping. Cleanup must preserve ordering across disk deletion, proc removal, cache flush, unmap, context free, memory free, and HV close.

## Test Signals
Signals include successful probe with allocated GPU memory, `/proc/ps3vram` hit/miss changes under read/write workloads, block read/write integrity tests, cache flush on module unload or shutdown, timeout logging from notifier/FIFO waits, and non-PS3 module load returning `-ENODEV`. Hardware-in-the-loop tests are required for DMA correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/ps3vram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rbd.c -->
# sources/distributed-fs/ceph-client/drivers/block/rbd.c

## Purpose
Implements the in-kernel Ceph RADOS Block Device driver. It maps Ceph RBD images into Linux block devices, handles sysfs map/unmap control, translates block requests into Ceph OSD object operations, supports RBD v1 and v2 metadata, snapshots, clone layering, exclusive locks, object maps, data pools, striping v2, discards, write zeroes, watch/notify refreshes, and parent copyup.

## Important APIs, Types, And Functions
Key state types are `struct rbd_device`, `struct rbd_client`, `struct rbd_spec`, `struct rbd_options`, `struct rbd_image_header`, `struct rbd_img_request`, and `struct rbd_obj_request`. `rbd_device` owns block-disk state, Ceph client/spec/options, header/layout/mapping, watch and exclusive-lock state, object map, parent chain, blk-mq tag set, sysfs device, and open/removal state.

User-visible control is provided through the `rbd` bus attributes `add`, `remove`, `add_single_major`, `remove_single_major`, and `supported_features`, plus per-device sysfs attributes such as `size`, `features`, `pool`, `image_id`, `current_snap`, `parent`, and `refresh`. Block operations are `rbd_open()`, `rbd_release()`, and blk-mq `rbd_queue_rq()`.

Metadata helpers include `rbd_dev_image_id()`, `rbd_dev_header_name()`, `rbd_dev_header_info()`, `rbd_dev_v1_header_info()`, `rbd_dev_v2_header_info()`, `rbd_dev_v2_header_onetime()`, `rbd_dev_v2_snap_context()`, `rbd_dev_setup_parent()`, `rbd_dev_probe_parent()`, and `rbd_dev_refresh()`.

Request processing centers on `rbd_queue_workfn()`, `rbd_img_fill_request()`, `rbd_img_handle_request()`, `rbd_obj_handle_request()`, `rbd_obj_advance_read()`, `rbd_obj_advance_write()`, and `rbd_obj_advance_copyup()`. Exclusive locking and watch/notify are handled by `rbd_try_acquire_lock()`, `rbd_acquire_lock()`, `rbd_request_lock()`, `rbd_release_lock()`, `rbd_watch_cb()`, `rbd_watch_errcb()`, and `rbd_reregister_watch()`.

## Control Flow
Module init validates libceph compatibility, creates request slab caches, allocates the global workqueue, optionally registers a single block major, and registers the `rbd` sysfs bus. Mapping starts when a privileged user writes an add string. `do_rbd_add()` parses monitor addresses, Ceph/RBD options, pool/image/snapshot identity, obtains or creates a shared `rbd_client`, resolves the pool id, creates an `rbd_device`, marks read-only snapshots, probes image metadata and parent chain, initializes the disk, optionally acquires the exclusive lock, adds the sysfs device and disk, and links it into `rbd_dev_list`.

I/O enters `rbd_queue_rq()`, which maps block operations to `OBJ_OP_READ`, `OBJ_OP_WRITE`, `OBJ_OP_DISCARD`, or `OBJ_OP_ZEROOUT`, rejects writes to read-only mappings, initializes an image request in the blk-mq PDU, and queues `rbd_queue_workfn()` on the global workqueue. The worker captures snapshot/parent state under `header_rwsem`, splits the image extent into object requests using Ceph striping helpers, then starts the image state machine. The image state machine obtains exclusive lock if required, captures current write snap context, checks mapping bounds, starts each object state machine, waits for pending object completions, and completes the blk-mq request.

Read object flow first consults the object map when usable. A missing object in a layered image is reverse-mapped to the parent and read through a child image request; holes and short reads are zero-filled. Write/discard/zeroout flow may pre-update object map state, issue guarded object operations, perform copyup when an object is missing but parent data overlaps, update snapshot object maps for fast-diff/deep-copyup, then post-update object map deletion state. Parent-chain recursion is avoided by scheduling child image requests through the workqueue and open-coding completion unwinding.

Removal starts from a privileged write to remove. `do_rbd_remove()` finds the device, rejects busy devices unless `force` is specified, sets `REMOVING`, optionally freezes and marks the disk dead, deletes disk/sysfs state, releases locks, unregisters watches, releases image metadata and parent devices, and drops the final device reference.

## State And Persistence Behavior
Kernel runtime state is extensive but volatile: shared Ceph clients, per-device blk-mq disks, image headers, snapshot contexts, object maps, parent chain references, lock owner information, watch handles, pending request state machines, and open counts. Persistent state lives in Ceph RADOS objects: v1 headers/data objects, v2 id/header/object-map/data objects, RBD class metadata, snapshots, locks, and data pools. The driver reads and updates persistent object maps and locks using Ceph class methods and OSD operations, but all local maps and headers are reloaded on map, refresh, lock acquire, watch re-registration, or notification.

Concurrency is coordinated with `header_rwsem`, `lock_rwsem`, `watch_mutex`, `object_map_lock`, `lock_lists_lock`, per-request mutexes, global client/device list locks, and krefs. Parent references use `atomic_inc_return_safe()` and `atomic_dec_return_safe()` so parent metadata can be torn down once in-flight parent-dependent requests drain.

## Dependencies And Integration Points
The driver is deeply integrated with libceph (`ceph_client`, OSD client, monitor client, class lock client, striper, decode helpers), Linux blk-mq, sysfs bus/device infrastructure, IDA allocation, workqueues, krefs, RCU string handling in object locators, and RBD on-disk constants from `rbd_types.h`. It depends on Ceph OSD class methods such as `get_id`, `get_size`, `get_features`, `get_snapcontext`, `object_map_load`, `object_map_update`, `copyup`, `parent_get`, and lock/watch/notify behavior.

## Risks
Major risk areas are request state-machine correctness, exclusive-lock handoff, object-map consistency, and parent copyup. Object map updates are asynchronous and protected by class locks; failures are often logged and surfaced but can leave performance features invalid or require refresh. Lock transitions must quiesce running I/O before release, reacquire after watch reregistration, and safely handle dead clients through watcher checks and monitor blocklisting. Header refresh races can change size, snapshots, and parent overlap while I/O is in flight, so `header_rwsem` and parent refs are critical. Discard/zeroout behavior depends on `alloc_size`, object boundaries, filestore compatibility comments, and object-map deletion state. The map string parser is sysfs-facing and CAP_SYS_ADMIN-gated, but invalid option handling and token ownership remain sensitive.

## Test Signals
Strong signals include Ceph RBD map/unmap smoke tests, read/write/discard/write-zeroes workloads, snapshot read-only mappings, clone/layered read fallback, copyup under parent overlap, flatten refresh behavior, object-map enabled and invalid cases, exclusive-lock contention between clients, watch error/reregister simulation, forced remove during I/O, xfstests or fio on mapped images, and Ceph QA suites that exercise in-kernel RBD. Sysfs attributes should reflect capacity, features, parent chain, snapshot identity, and refresh updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rbd_types.h -->
# sources/distributed-fs/ceph-client/drivers/block/rbd_types.h

## Purpose
Defines shared RBD on-disk object naming constants, lock/notify constants, object-map states, image flags, default object sizing, and packed v1 image header structures used by the kernel RBD driver.

## Important APIs, Types, And Functions
Format v2 constants include `RBD_HEADER_PREFIX`, `RBD_OBJECT_MAP_PREFIX`, `RBD_ID_PREFIX`, and `RBD_V2_DATA_FORMAT`. Locking constants are `RBD_LOCK_NAME`, `RBD_LOCK_TAG`, and `RBD_LOCK_COOKIE_PREFIX`. `enum rbd_notify_op` defines watch/notify operations for acquired lock, released lock, request lock, and header update.

Object-map states are `OBJECT_NONEXISTENT`, `OBJECT_EXISTS`, `OBJECT_PENDING`, and `OBJECT_EXISTS_CLEAN`. Image flags include `RBD_FLAG_OBJECT_MAP_INVALID` and `RBD_FLAG_FAST_DIFF_INVALID`.

Format v1 constants include `RBD_SUFFIX`, `RBD_V1_DATA_FORMAT`, `RBD_DIRECTORY`, `RBD_INFO`, object-order bounds, and header magic/version strings. `struct rbd_image_snap_ondisk` and `struct rbd_image_header_ondisk` are packed little-endian representations of v1 snapshot and header metadata.

## Control Flow
This header has no executable control flow. `rbd.c` includes it to generate object names, decode v1 headers, validate image format fields, identify lock and notify payloads, and interpret object-map states and invalid flags.

## State And Persistence Behavior
The constants describe persistent RADOS object layout and encoded metadata. v2 images use id, header, object-map, and data object prefixes. v1 images use a single `<name>.rbd` header and data object format. The packed structures are persisted in RADOS for v1 images and must remain ABI-compatible.

## Dependencies And Integration Points
Depends only on Linux fixed-width types. It is an integration contract between kernel RBD code, Ceph OSD class methods, userspace RBD tooling, and persisted RADOS metadata. Layout or value changes would affect compatibility with existing images.

## Risks
The packed v1 structures contain flexible snapshot arrays and little-endian fields; readers must validate lengths and counts before decoding. Changing any prefix, lock name, notify op value, object-map state, or header magic would break interoperability. Object order bounds affect assumptions about sector-sized I/O and memory sizing in the driver.

## Test Signals
Signals are indirect: successful mapping of v1 and v2 images, snapshot enumeration, object-map load/update, lock handoff notifications, and compatibility tests against images created by userspace `rbd` tools. Static ABI review is important for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rbd_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/block/rnbd/Kconfig

## Purpose
Defines Kconfig symbols for the RDMA Network Block Device subsystem and its client/server drivers.

## Important APIs, Types, And Functions
This file declares internal `BLK_DEV_RNBD`, plus user-visible tristate symbols `BLK_DEV_RNBD_CLIENT` and `BLK_DEV_RNBD_SERVER`. The client depends on `INFINIBAND_RTRS_CLIENT`, selects `BLK_DEV_RNBD` and `SG_POOL`, and describes remote block-device mapping over RTRS. The server depends on `INFINIBAND_RTRS_SERVER`, selects `BLK_DEV_RNBD`, and describes exporting local block devices over RTRS.

## Control Flow
There is no runtime flow. During kernel configuration, enabling client or server pulls in the common RNBD symbol. The parent block Kconfig sources this file so these options appear under block driver configuration.

## State And Persistence Behavior
Kconfig state is build-time configuration only. It controls whether RNBD client/server objects are built in, built as modules, or omitted. No runtime state or persistent data is defined here.

## Dependencies And Integration Points
RNBD is tied to the RTRS RDMA transport stack through `INFINIBAND_RTRS_CLIENT` and `INFINIBAND_RTRS_SERVER`. Client additionally selects scatterlist pool support. The matching `Makefile` consumes these symbols to build `rnbd-client.o` and `rnbd-server.o`.

## Risks
Dependency correctness is the main risk. If RTRS symbols or SG pool requirements change, this file must be updated or builds may fail. Because `BLK_DEV_RNBD` is a hidden bool selected by both endpoints, common code assumptions must stay compatible with either client-only or server-only builds.

## Test Signals
Signals include Kconfig dependency resolution for client-only, server-only, both, module, and built-in combinations; compile tests with and without RTRS; and module packaging checks that selected symbols produce the expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/block/rnbd/Makefile

## Purpose
Builds the RNBD client and server composite objects and supplies include flags needed for RTRS integration and server trace compilation.

## Important APIs, Types, And Functions
The file sets `ccflags-y := -I$(srctree)/drivers/infiniband/ulp/rtrs`, defines `rnbd-client-y` as `rnbd-clt.o` plus `rnbd-clt-sysfs.o`, defines `rnbd-server-y` as `rnbd-srv.o`, `rnbd-srv-sysfs.o`, and `rnbd-srv-trace.o`, adds a per-object include flag for `rnbd-srv-trace.o`, and wires final objects to `CONFIG_BLK_DEV_RNBD_CLIENT` and `CONFIG_BLK_DEV_RNBD_SERVER`.

## Control Flow
There is no runtime control flow. Kbuild uses the object lists to link client and server modules or built-ins depending on Kconfig. The parent block `Makefile` descends into `rnbd/` when `CONFIG_BLK_DEV_RNBD` is selected.

## State And Persistence Behavior
No runtime or persistent state is represented. The file controls build composition only.

## Dependencies And Integration Points
Integrates with Kbuild, the RNBD source files in the same directory, and RTRS headers under `drivers/infiniband/ulp/rtrs`. The trace object needs `-I$(src)` so generated or local trace headers can be found during compilation.

## Risks
Build breakage is the main risk. Object-list drift from source renames, missing RTRS include paths, or trace include path changes will fail compilation. Because client and server are separate composite objects, shared code additions must be explicitly added to the right object list or a common object strategy.

## Test Signals
Signals include compile tests for `CONFIG_BLK_DEV_RNBD_CLIENT=m/y`, `CONFIG_BLK_DEV_RNBD_SERVER=m/y`, and both enabled; clean builds after touching trace headers; and verifying final modules contain the expected sysfs and trace objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/Makefile -->
