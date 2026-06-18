# Research: subset-b-001058

Grouped source research for block-driver files under `sources/distributed-fs/ceph-client/drivers/block`. Each section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/mtip32xx/mtip32xx.c -->
# sources/distributed-fs/ceph-client/drivers/block/mtip32xx/mtip32xx.c

## Purpose
This file implements the Micron RealSSD/P320/P420 PCIe block driver. It binds Micron PCI IDs, initializes an AHCI-like controller/port, exposes disks named `rssd*`, translates blk-mq requests into ATA NCQ FIS command tables, handles internal ATA ioctls, and manages controller reset, interrupt, timeout, rebuild, suspend/resume, shutdown, sysfs, and debugfs behavior.

## Important APIs, Types, And Functions
The central runtime state is `struct driver_data` and `struct mtip_port` from `mtip32xx.h`, with per-request `struct mtip_cmd` allocated as the blk-mq PDU. PCI lifecycle is owned by `mtip_pci_probe()`, `mtip_pci_remove()`, `mtip_pci_suspend()`, `mtip_pci_resume()`, and `mtip_pci_shutdown()`. Module lifecycle registers a dynamic block major and the PCI driver in `mtip_init()` and tears them down in `mtip_exit()`.

Hardware setup flows through `mtip_hw_init()`, `mtip_detect_product()`, `hba_setup()`, `mtip_dma_alloc()`, `mtip_init_port()`, and `mtip_start_port()`. Normal I/O enters through `mtip_queue_rq()`, maps scatter-gather lists in `mtip_hw_submit_io()`, fills `host_to_dev_fis` and AHCI command headers, and starts hardware with `mtip_issue_ncq_command()`. Reserved/internal commands use `mtip_exec_internal_command()` and `mtip_issue_reserved_cmd()`. Completion is split across `mtip_irq_handler()`, `mtip_handle_irq()`, `mtip_workq_sdbfx()`, `mtip_complete_command()`, and blk-mq `.complete` callback `mtip_softirq_done_fn()`.

Error and maintenance paths include `mtip_cmd_timeout()`, `mtip_service_thread()`, `mtip_handle_tfe()`, `mtip_restart_port()`, `mtip_device_reset()`, `mtip_quiesce_io()`, `mtip_ftl_rebuild_poll()`, `mtip_check_surprise_removal()`, and state-gating helpers `is_se_active()` and `is_stopped()`. User-visible support includes `mtip_block_ioctl()`, `mtip_block_compat_ioctl()`, `mtip_hw_ioctl()`, ATA pass-through helpers, `mtip_block_getgeo()`, sysfs `status`, and debugfs `rssd/<disk>/{flags,registers}`.

## Control Flow
At load, `mtip_init()` registers a block major and PCI driver. Probe chooses a NUMA node, allocates `driver_data`, enables PCI/MSI/DMA, builds an ISR workqueue and CPU bindings, applies PCI quirks, then calls `mtip_block_initialize()`. Block initialization brings up hardware, allocates a blk-mq tag set with one reserved internal-command tag, allocates a gendisk, assigns an `rssd*` name via an IDA, reads IDENTIFY/log/SMART state, sets capacity, adds the disk, and starts the service thread. If an FTL rebuild marker is present, disk addition is delayed while the service thread polls until rebuild completion.

For I/O, blk-mq calls `mtip_queue_rq()`. Passthrough/reserved requests become non-NCQ internal commands. Normal reads/writes are rejected if secure erase, removal, over-temperature, write-protect, or rebuild-failed flags block them. Otherwise the request is started, DMA-mapped, encoded as `ATA_CMD_FPDMA_READ` or `ATA_CMD_FPDMA_WRITE`, and issued by setting SActive and Command Issue bits for the request tag. If internal command or error handling flags are active, the tag is parked in `port->cmds_to_issue` and later issued by the service thread.

Interrupts read HBA/port status, acknowledge port status, queue per-slot-group completion work for SDB FIS completions, process legacy internal-command completions, and wake the service thread for taskfile/interface errors. Completion workers clear hardware completed registers and complete each request. blk-mq completion unmaps DMA, releases unaligned-command budget, and ends the request. Timeouts set `MTIP_PF_TO_ACTIVE_BIT`, wake the service thread, reset the device, requeue parked commands, or fail requests if reset fails.

## State And Persistence Behavior
Persistent media lives on the SSD; the driver stores only volatile kernel state. Important state bits live in `dd->dd_flag` and `port->flags`: remove-pending, secure-lock, over-temperature, write-protect, rebuild-failed, init-done, internal-command active, error-handling active, timeout active, issue-commands, rebuild, and service-thread stop. DMA-coherent buffers hold RX FIS, IDENTIFY data, SMART data, log data, command list entries, and per-command tables. `rssd_index_ida` persists naming only for the lifetime of the module. Debugfs and sysfs report live state but do not persist configuration.

## Dependencies And Integration Points
The driver integrates with PCI/MSI, DMA mapping/coherent allocation, blk-mq, gendisk/block-device operations, ATA command definitions, AHCI register definitions, debugfs, sysfs device attributes, NUMA CPU masks, kthreads, workqueues, IRQ affinity, IDA allocation, and compat ioctl translation. It exposes legacy ATA HDIO ioctls and block geometry for userspace tools.

## Risks
This is hardware-facing code with several race-sensitive paths: surprise removal while registers are being read, interrupt completion workers racing with teardown, internal commands pausing normal NCQ, timeout recovery resetting active hardware, and unaligned write depth accounting. ATA pass-through ioctls copy user buffers and map DMA buffers, so size checks and cleanup order matter. The service-thread wait condition relies on flag bits rather than a separate queue. `mtip_exit()` unregisters the block major before the PCI driver, which is unusual and should be checked against kernel teardown expectations. FTL rebuild polling can block device availability for a long period.

## Test Signals
Useful signals include successful module load with version log, PCI probe for supported IDs, `rssd*` disk creation with correct capacity, sysfs `status` transitions, debugfs flags/register reads, read/write fio or blktests runs, ATA ioctl paths (`HDIO_GET_IDENTITY`, SMART, taskfile), timeout injection via blk fake timeout, remove/surprise-remove behavior, suspend/resume/shutdown with standby immediate, FTL rebuild simulation, and teardown under active I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/mtip32xx/mtip32xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/mtip32xx/mtip32xx.h -->
# sources/distributed-fs/ceph-client/drivers/block/mtip32xx/mtip32xx.h

## Purpose
This header defines constants, flags, hardware data structures, request state, port state, and per-device state for the Micron RealSSD PCIe block driver implemented by `mtip32xx.c`.

## Important APIs, Types, And Functions
Key constants cover PCI IDs, driver identity, timeout values, command-slot geometry, scatter-gather limits, BAR selection, FTL rebuild markers, secure erase mode, and the `rssd` minor count. The main enum defines port flag bits (`MTIP_PF_*`) and device flag bits (`MTIP_DDF_*`) plus masks for I/O pausing and stopping.

Important types are `struct smart_attr` for SMART attributes, `struct mtip_work` for per-slot-group completion work, `struct host_to_dev_fis` for ATA register FIS layout, `struct mtip_cmd_hdr` for AHCI command headers, `struct mtip_cmd_sg` for PRD entries, `struct mtip_cmd` for per-request blk-mq private state, `struct mtip_port` for one hardware port, and `struct driver_data` for one PCI device. `DEFINE_HANDLER(group)` generates workqueue handlers that dispatch to `mtip_workq_sdbfx()`.

## Control Flow
The header does not execute code, but it shapes control flow by defining the flags tested by submit, timeout, service-thread, and teardown paths. `MTIP_PF_PAUSE_IO` gates normal NCQ submission while internal command, error handling, secure erase, firmware download, or timeout handling is active. `MTIP_DDF_STOP_IO` gates request acceptance when removal, security lock, over-temperature, write-protect, or rebuild failure is present.

## State And Persistence Behavior
All structures are volatile kernel runtime state. `struct mtip_port` owns MMIO pointers, command/FIS DMA regions, identify/log/SMART buffers, queued-command bitmaps, waitqueue, flags, pause timers, unaligned-slot accounting, and per-slot-group locks. `struct driver_data` owns the PCI device, disk, queue/tag set, product information, service thread, debugfs node, workqueue, NUMA binding, and driver flags. The header stores no persistent configuration.

## Dependencies And Integration Points
The header depends on Linux spinlocks, rwsems, ATA definitions, interrupt/workqueue primitives, DMA address types, blk-mq through opaque request private data in the C file, and AHCI-compatible register semantics. It forms the internal contract between hardware register code, blk-mq request handling, debugfs/sysfs code, and PCI lifecycle code.

## Risks
Many structs mirror hardware ABI layouts and use packed/little-endian fields; accidental field changes can break DMA command interpretation. Flag bits are shared across IRQ, service-thread, ioctl, submit, timeout, and teardown contexts, requiring atomic bit operations and careful ordering. The per-tag math assumes slot groups of 32 commands and a maximum of eight groups.

## Test Signals
Compile-time structure layout coverage comes from building the driver. Runtime test signals are indirect: successful DMA command submission, correct IDENTIFY parsing, correct completion by tag, correct pause/stop behavior from flag masks, and absence of data corruption under high queue depth and unaligned I/O constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/mtip32xx/mtip32xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/n64cart.c -->
# sources/distributed-fs/ceph-client/drivers/block/n64cart.c

## Purpose
This file implements a tiny read-only block driver for Nintendo 64 cartridge data exposed through a platform device. It maps the PI registers, uses DMA to copy cartridge ranges into bio pages, and publishes one `n64cart` disk without partition scanning.

## Important APIs, Types, And Functions
Module parameters `start` and `size` define the cartridge byte range. Register helpers `n64cart_write_reg()`, `n64cart_read_reg()`, and `n64cart_wait_dma()` drive the PI DMA engine. `n64cart_do_bvec()` maps each bio vector for DMA, programs DRAM address, cartridge address, and DMA length, waits for completion, and unmaps. `n64cart_submit_bio()` iterates all bio segments and ends or errors the bio. `n64cart_probe()` allocates and registers the gendisk. `n64cart_init()` registers a probe-only platform driver.

## Control Flow
During init, `platform_driver_probe()` calls `n64cart_probe()`. Probe validates that `start` and `size` are provided and that size is 4 KiB aligned, maps the register resource with devm, allocates a disk with 4 KiB logical/physical block sizes, marks it read-only and no-partition, sets capacity from `size`, and adds it. For each bio, the driver computes the byte offset from the sector, processes each segment by DMAing from `start + pos`, and calls `bio_endio()` once all segments succeed.

## State And Persistence Behavior
The driver keeps only global `reg_base`, `start`, and `size`. The underlying cartridge data is persistent/ROM-like and the disk is explicitly read-only. There is no dynamic removal path, no private disk allocation retained for unload, and no write handling beyond the read-only block-layer flag.

## Dependencies And Integration Points
It depends on platform-device resources, MMIO accessors, DMA mapping for bio vectors, blkdev/gendisk APIs, and module parameters. It integrates as an embedded boot-time platform driver rather than a hot-unpluggable module.

## Risks
The driver busy-waits on DMA status with `cpu_relax()` and has no timeout. Alignment is only WARNed for bvec offset/length rather than rejected. The comment states no module/unload support; the disk pointer is not stored for remove, so this is intended for constrained embedded boot use. Incorrect `start` or `size` parameters can expose the wrong cartridge region.

## Test Signals
Expected signals are failure on missing parameters, failure on non-4K size, successful `n64cart` read-only disk registration, correct capacity, successful reads of aligned blocks, no write acceptance, and stable behavior under multi-segment bios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/n64cart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/nbd.c -->
# sources/distributed-fs/ceph-client/drivers/block/nbd.c

## Purpose
This file implements the Linux Network Block Device client driver. It exposes `/dev/nbd*` block devices, binds them to TCP or stream UNIX sockets through legacy ioctls or generic netlink, sends block requests using the NBD protocol, receives replies in workqueue threads, supports reconnect/multi-connection operation, and manages debugfs/sysfs/status reporting.

## Important APIs, Types, And Functions
Runtime state is split into `struct nbd_device` for the disk/tag-set/lifetime, `struct nbd_config` for a live configuration, `struct nbd_sock` for each socket, and `struct nbd_cmd` for per-request state. Device creation/removal uses `nbd_dev_add()`, `nbd_dev_remove()`, `nbd_put()`, and IDR `nbd_index_idr`. Request handling uses blk-mq ops `nbd_queue_rq()`, `nbd_complete_rq()`, `nbd_init_request()`, and `nbd_xmit_timeout()`.

Transport functions include `nbd_send_cmd()`, `nbd_pending_cmd_work()`, `nbd_read_reply()`, `nbd_handle_reply()`, `recv_work()`, `sock_xmit()`, and `__sock_xmit()`. Configuration paths include ioctl handlers `nbd_ioctl()` and `__nbd_ioctl()`, config allocation/refcounting in `nbd_alloc_and_init_config()` and `nbd_config_put()`, netlink handlers `nbd_genl_connect()`, `nbd_genl_disconnect()`, `nbd_genl_reconfigure()`, and `nbd_genl_status()`, plus `nbd_start_device()`, `nbd_disconnect_and_put()`, and `nbd_reconnect_socket()`.

## Control Flow
Module init validates `max_part`/`nbds_max`, registers the NBD major, creates an async delete workqueue, registers the generic-netlink family, initializes debugfs, and pre-creates `nbds_max` devices. Opening a disk creates a config if needed. Legacy ioctl setup adds sockets, sets size/block size/timeout/flags, then `NBD_DO_IT` starts receive workers and waits for them to exit. Netlink setup can allocate or reuse a device, allocate config, set size/timeouts/server/client flags, add sockets, optional backend identifier, create sysfs backend, start receive workers, and return the selected index.

For I/O, blk-mq calls `nbd_queue_rq()`, which locks the command and sends through a socket selected by hardware queue index. `nbd_send_cmd()` builds an NBD request with a cookie/tag handle, sends the header, sends write payload bvecs if needed, and marks the command inflight. Partial sends are pinned to the socket via `nsock->pending` and resumed by `nbd_pending_cmd_work()` to avoid tag confusion. Receive workers read reply headers, validate magic/tag/socket/cookie/inflight state, receive read payloads into request bvecs, clear inflight, and complete the request.

Timeouts either requeue to another live socket, wait for reconnect if configured, warn and extend when socket timeout is disabled, or mark the connection timed out, shut down sockets, and complete the request with error. Disconnect sends `NBD_CMD_DISC`, shuts down sockets, clears inflight requests, resets capacity on last opener, drops config refs, and may destroy the device if `DESTROY_ON_DISCONNECT` is set.

## State And Persistence Behavior
NBD stores no block data locally; all persistence is in the remote server. Kernel state includes config flags, runtime flags, bytesize, block size, live socket array, live/recv thread counters, backend string, sysfs files, debugfs directory, per-request cookies, and refcounts. `NBD_RT_BOUND` distinguishes netlink-controlled devices from ioctl-controlled devices. `NBD_DESTROY_ON_DISCONNECT` and `NBD_DISCONNECT_REQUESTED` control device lifetime.

## Dependencies And Integration Points
The driver integrates with blk-mq, gendisk, block ioctls, generic netlink (`linux/nbd-netlink.h`), NBD UAPI (`linux/nbd.h`), sockets, kernel credentials for socket I/O, workqueues, debugfs, sysfs device attributes, IDR indexing, module parameters, tracepoints (`trace/events/nbd.h`), and queue limit updates for discard, flush/FUA, write zeroes, rotational, block size, capacity, and partition scanning.

## Risks
The highest-risk areas are request lifetime races between send completion and receive completion, partial-send recovery, timeout/requeue races, stale replies after reconnect, and config teardown while workers hold refs. The code uses cookies and `NBD_CMD_INFLIGHT` to detect double or stale replies. Socket I/O uses `GFP_NOIO`/memalloc context because block I/O over networking can recurse into reclaim. Netlink status intentionally reads some state racefully. Legacy ioctl and netlink controls are mutually constrained to prevent mixed ownership.

## Test Signals
Signals include successful creation of default `/dev/nbd*` devices, ioctl attach/read/write/disconnect, netlink connect/reconfigure/status/disconnect, multi-connection rejection unless server flags allow it, reconnect after dead link, timeout behavior with and without `tag_set.timeout`, sysfs `pid`/`backend`, debugfs entries, discard/flush/FUA/write-zeroes queue limit changes, partition scan after sizing, and blktests NBD coverage under forced socket failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/nbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/block/null_blk/Kconfig

## Purpose
This Kconfig fragment declares build options for the null block test driver and its optional fault-injection support.

## Important APIs, Types, And Functions
`config BLK_DEV_NULL_BLK` is a tristate option named "Null test block driver" and selects `CONFIGFS_FS`, because runtime device creation/configuration is exposed through configfs. `config BLK_DEV_NULL_BLK_FAULT_INJECTION` is a bool depending on `BLK_DEV_NULL_BLK` and `FAULT_INJECTION_CONFIGFS`, enabling per-device fault injection groups used by `main.c`.

## Control Flow
There is no runtime control flow. Build selection of `BLK_DEV_NULL_BLK` controls whether `null_blk.o` is built. Enabling fault injection compiles extra fault attributes, configfs groups, and failure decisions for request timeout, request requeue, and hardware-context initialization.

## State And Persistence Behavior
The file stores compile-time configuration only. Runtime state is in `main.c` and optional fault-injection configfs state.

## Dependencies And Integration Points
The Kconfig integrates null_blk with configfs and the generic fault-injection framework. It also indirectly coordinates with the Makefile, which adds `main.o`, `zoned.o`, and optional tracing objects based on configuration.

## Risks
Because `BLK_DEV_NULL_BLK` selects configfs, disabling configfs independently is not possible when the driver is enabled. Fault injection depends on `FAULT_INJECTION_CONFIGFS`; tests expecting fault knobs must ensure this option is enabled.

## Test Signals
Build-menu visibility, successful module or built-in build for `BLK_DEV_NULL_BLK`, and presence/absence of configfs fault groups under created nullb devices validate the configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/Makefile -->
# sources/distributed-fs/ceph-client/drivers/block/null_blk/Makefile

## Purpose
This Makefile describes how the null block driver is compiled from its component objects.

## Important APIs, Types, And Functions
`ccflags-y += -I$(src)` ensures trace-event includes can find local headers. `obj-$(CONFIG_BLK_DEV_NULL_BLK) += null_blk.o` builds the driver when selected. `null_blk-objs := main.o` makes `main.c` mandatory. `trace.o` is added only when both zoned block support and tracing are enabled. `zoned.o` is added when `CONFIG_BLK_DEV_ZONED` is enabled.

## Control Flow
There is no runtime flow. Build flow starts with `main.o`, then conditionally includes zoned support and zoned tracepoints. The trace object is guarded by zoned support because the local tracepoints describe zoned operations.

## State And Persistence Behavior
No runtime state or persistence exists in the Makefile.

## Dependencies And Integration Points
It integrates Kconfig symbols with Kbuild object composition. The include path supports `trace.h`'s `TRACE_INCLUDE_PATH .` pattern and local inclusion from generated trace code.

## Risks
Tracepoint compilation is sensitive to include paths and `CREATE_TRACE_POINTS`; removing `-I$(src)` can break generated trace includes. Building zoned functionality without matching source objects would leave the inline stubs in `null_blk.h` mismatched with runtime expectations.

## Test Signals
Build with `CONFIG_BLK_DEV_NULL_BLK=m/y`, with and without `CONFIG_BLK_DEV_ZONED`, and with and without `CONFIG_TRACING`, should include the expected objects and produce no trace include failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/main.c -->
# sources/distributed-fs/ceph-client/drivers/block/null_blk/main.c

## Purpose
This file implements the null_blk test block driver. It creates synthetic block devices through module parameters and configfs, exercises blk-mq queueing/completion paths, optionally stores data in memory, supports discard/cache/FUA/badblocks/zoned hooks, throttles bandwidth, supports polling and timer/softirq/inline completions, and optionally injects request faults.

## Important APIs, Types, And Functions
Core runtime types are `struct nullb_device` and `struct nullb` from `null_blk.h`, plus local `struct nullb_page` for memory-backed radix-tree pages. Module parameters populate global defaults such as `gb`, `bs`, `submit_queues`, `poll_queues`, `irqmode`, `completion_nsec`, `memory_backed`, `discard`, `cache_size`, `mbps`, zoned settings, shared tags, and fault strings.

Configfs is implemented with generated `NULLB_DEVICE_ATTR()` attributes, `nullb_device_power_store()`, badblocks stores, zone condition stores, `nullb_group_make_group()`, `nullb_group_drop_item()`, and subsystem `nullb_subsys`. Device lifecycle is `null_alloc_dev()`, `null_add_dev()`, `null_del_dev()`, `null_destroy_dev()`, and `null_free_dev()`. blk-mq integration is `null_mq_ops` with `null_queue_rq()`, `null_queue_rqs()`, `null_complete_rq()`, `null_timeout_rq()`, `null_poll()`, `null_map_queues()`, and `null_init_hctx()`.

Memory-backed behavior uses `null_alloc_page()`, `null_insert_page()`, `copy_to_nullb()`, `copy_from_nullb()`, `null_handle_discard()`, `null_handle_flush()`, `null_handle_data_transfer()`, and `null_process_cmd()`. Throttling uses `null_handle_throttled()` and `nullb_bwtimer_fn()`. Init/exit are `null_init()` and `null_exit()`.

## Control Flow
Module init validates global parameters, initializes optional fault attributes, registers the configfs subsystem, registers a dynamic block major, and creates `nr_devices` default devices. Configfs users can create named device groups and set attributes before powering them on; once powered, most attributes reject changes with `-EBUSY`, while submit/poll queue counts can be applied live through `blk_mq_update_nr_hw_queues()`.

`null_add_dev()` validates config, allocates `struct nullb`, queue state, tag set, queue limits, optional zoned state, cache/writeback features, disk, IDA index, capacity, and gendisk. It adds the disk and tracks it in `nullb_list`. `null_del_dev()` reverses this, cancels throttling, deletes the disk, releases tag sets/queues, flushes cache storage, and detaches the device.

For each request, `null_queue_rq()` prepares the command PDU, handles injected timeout/requeue, enforces bandwidth throttling, starts the request, and either queues it to a poll list, leaves fake timeouts incomplete, or calls `null_handle_cmd()`. `null_handle_cmd()` handles flush specially, dispatches zoned or generic processing, preserves earlier timeout errors, and completes inline, through softirq, or through an hrtimer. Generic processing checks configured badblocks, performs memory-backed reads/writes/discards when enabled, and otherwise completes successfully without storing data. Poll queues defer processing until `null_poll()` drains the poll list and batches completions.

## State And Persistence Behavior
The driver is synthetic. Without `memory_backed`, data is not persisted and reads normally complete without filling buffers except under KMSAN zero-fill behavior. With `memory_backed`, written sectors are stored in radix trees of pages (`data`) and optional writeback cache pages (`cache`). Cache pages use bitmap bits for valid sectors plus lock/free sentinel bits. `REQ_FUA` writes bypass/flush cache sector state. Flush drains the cache into the backing radix tree. All state is volatile and lost when the device or module is removed. Badblocks, configfs attributes, throttling counters, queue mappings, and zoned state are runtime-only.

## Dependencies And Integration Points
The file integrates with blk-mq, gendisk, configfs, module parameters, IDA, radix trees, badblocks, hrtimers, fault injection configfs, optional zoned support from `zoned.c`, queue limits, request polling, KMSAN, and block features for discard, write cache, FUA, rotational, and zoned reporting.

## Risks
Memory-backed mode uses spinlock-protected radix trees but temporarily drops the lock for allocation/preload, so lookup/insert races are handled by radix insert fallback and page-private checks. Cache flushing uses lock/free sentinel bits to avoid freeing a page while another thread flushes it. Poll timeout must remove requests from the poll list safely. Shared global tag sets mean multiple devices share blk-mq resources when `shared_tags` is set. Configfs power transitions must avoid double add/delete. Throttling stops hardware queues and relies on timer refill to restart them.

## Test Signals
Signals include module load/unload, default `nullb*` device creation, configfs create/attribute/power flows, blk-mq reads/writes with every irq mode, poll I/O, bandwidth throttling, memory-backed data readback, discard clearing stored data, cache flush/FUA behavior, badblocks full and partial errors, fault-injected timeout/requeue/init_hctx failure, live queue-count updates, zoned mode when configured, and teardown while I/O is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/null_blk.h -->
# sources/distributed-fs/ceph-client/drivers/block/null_blk/null_blk.h

## Purpose
This header defines the shared data structures and function contracts for null_blk core, zoned support, tracing, and memory-backed helpers.

## Important APIs, Types, And Functions
`struct nullb_cmd` is the blk-mq request PDU and carries status, fake-timeout state, queue pointer, and optional timer. `struct nullb_queue` is per-hctx queue state with poll list and lock. `struct nullb_zone` represents a zoned block zone with lock, type, condition, start, write pointer, length, and capacity. `struct nullb_device` stores configfs/module configuration, radix-tree storage/cache, badblocks, zoned accounting, and all tunables. `struct nullb` is the live disk instance with queue, gendisk, tag set, throttling timer/counter, cache flush position, lock, queue array, and disk name.

The header declares core helpers `null_handle_discard()`, `null_process_cmd()`, `null_handle_badblocks()`, and `null_handle_memory_backed()`. When `CONFIG_BLK_DEV_ZONED` is enabled it declares zoned helpers implemented elsewhere; otherwise it provides stubs returning unsupported/no-op behavior and maps `null_report_zones` to `NULL`.

## Control Flow
The header controls compile-time flow for zoned support. `main.c` can call zoned operations unconditionally because the header supplies either real declarations or stubs. It also defines the layout that blk-mq callbacks, memory-backed data paths, configfs code, and tracepoints share.

## State And Persistence Behavior
All state is volatile per module/device lifetime. `struct nullb_device` contains the pseudo-persistent contents when memory backing is enabled, represented by `data` and `cache` radix trees. Zone arrays and counters represent simulated zoned-media state. No on-disk persistence is defined.

## Dependencies And Integration Points
The header depends on blkdev, blk-mq, hrtimer, configfs, badblocks, fault injection, spinlocks, and mutexes. It is included by `main.c`, `trace.h`, `trace.c`, and zoned support.

## Risks
Changing structure fields affects blk-mq PDU sizing, configfs behavior, and zoned helper assumptions. Zoned stubs must remain behaviorally compatible with callers when zoned support is disabled. `struct nullb_device` mixes immutable-after-config fields with live-updatable queue fields, so users of the header must respect locking and configured/up flags.

## Test Signals
Successful builds with and without `CONFIG_BLK_DEV_ZONED` are the primary header test. Runtime signals include correct PDU operation, configfs attribute state reflecting `struct nullb_device`, zoned calls returning `-EOPNOTSUPP` or working depending on config, and memory-backed helpers operating on the declared radix trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/null_blk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/trace.c -->
# sources/distributed-fs/ceph-client/drivers/block/null_blk/trace.c

## Purpose
This file implements a small helper used by null_blk tracepoints to format the disk name consistently.

## Important APIs, Types, And Functions
`nullb_trace_disk_name(struct trace_seq *p, char *name)` returns the current trace-sequence buffer pointer, optionally appends `disk=<name>, ` when a non-empty name is supplied, then terminates the trace sequence with NUL. It is declared in `trace.h` and used through the `__print_disk_name()` macro.

## Control Flow
Tracepoint print formatting calls this helper during trace rendering. If the disk name is absent, it emits an empty prefix; otherwise it emits a disk prefix before event-specific fields.

## State And Persistence Behavior
The helper has no persistent state. It writes only to the transient `trace_seq` supplied by ftrace.

## Dependencies And Integration Points
It depends on local `trace.h`, Linux trace sequence APIs, and the null_blk zoned tracepoint build path. It is compiled only when the Makefile includes `trace.o`.

## Risks
Formatting helpers run in tracing contexts, so they must avoid sleeping and must respect trace sequence conventions. Returning the pre-write buffer pointer is important for `TP_printk()` string substitution.

## Test Signals
Enable null_blk zoned trace events and verify event text includes `disk=<name>, ` when a disk is available and remains well-formed when no disk name is assigned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/trace.h -->
# sources/distributed-fs/ceph-client/drivers/block/null_blk/trace.h

## Purpose
This header defines ftrace trace events for null_blk zoned operations and report-zones activity.

## Important APIs, Types, And Functions
It sets `TRACE_SYSTEM nullb`, declares `nullb_trace_disk_name()`, defines `__print_disk_name()`, and provides `__assign_disk_name()` for copying a `gendisk` name into trace entries. `TRACE_EVENT(nullb_zone_op)` records disk, request operation, zone number, and zone condition for a `struct nullb_cmd`. `TRACE_EVENT(nullb_report_zones)` records disk and number of zones reported for a `struct nullb`.

## Control Flow
Zoned code can call generated trace hooks when a zone operation or report-zones path occurs. The tracepoint fast-assign blocks copy stable values into the trace entry, and `TP_printk()` renders them using block operation and zone-condition string helpers.

## State And Persistence Behavior
Trace events do not alter device state. They capture transient snapshots into the ftrace ring buffer when enabled.

## Dependencies And Integration Points
The header depends on Linux tracepoint/trace_seq APIs, `null_blk.h`, gendisk names, blk-mq request access through `blk_mq_rq_from_pdu()`, `blk_op_str()`, and `blk_zone_cond_str()`. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` align with the local Makefile include path and generated trace code.

## Risks
Trace headers are sensitive to include guards and the `TRACE_HEADER_MULTI_READ` pattern. The event uses `__field_struct(enum req_op, op)` because normal `__field()` signedness handling does not work for bitwise enum types. Incorrect request-to-PDU assumptions would break trace assignment.

## Test Signals
Build with tracing and zoned null_blk enabled, then enable `nullb:nullb_zone_op` and `nullb:nullb_report_zones` through tracefs. Zone operations should report disk name, request operation, zone number, condition, and reported-zone counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/null_blk/trace.h -->
