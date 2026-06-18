# Research: subset-b-005362

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_hipd.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_hipd.h

## Purpose

`sym_hipd.h` is the main hardware-private contract for the Symbios/LSI 53C8xx and 53C1010 SCSI host adapter driver. It defines the script-visible memory layouts, software state structures, MMIO access helpers, DMA scatter/gather builders, and allocator interfaces used by the rest of the `sym53c8xx_2` driver. The file is not a standalone implementation; it is the shape agreement between the Linux SCSI glue, firmware/SCRIPTS engine, NVRAM policy, and DMA allocator.

## Important APIs, Types, And Functions

Important constants include host status values (`HS_IDLE`, `HS_BUSY`, `HS_COMPLETE`, `HS_SEL_TIMEOUT`, `HS_COMP_ERR`), software interrupt reasons (`SIR_*`), extended error bits (`XE_*`), negotiation status (`NS_SYNC`, `NS_WIDE`, `NS_PPR`), device/host policy flags (`SYM_DISC_ENABLED`, `SYM_TAGS_ENABLED`, `SYM_AVOID_BUS_RESET`), queue sizing (`SYM_CONF_MAX_QUEUE`, `MAX_QUEUE`), and DMA addressing-mode masks.

Key hardware access macros are `INB/INW/INL`, `OUTB/OUTW/OUTL`, offset variants, bit set/clear helpers, `OUTL_DSP()`, and `OUTONB_STD()`. These wrap `ioread*()`/`iowrite*()` against `np->s.ioaddr` and add memory barriers before restarting the SCRIPTS processor.

The main types are `struct sym_trans` for negotiated transfer parameters, `struct sym_tcb` and `struct sym_lcb` for target and LUN state, `struct sym_ccb` for per-command state, `struct sym_dsb` for the script-visible data structure block, and `struct sym_hcb` for host adapter state. `struct sym_ccbh`, `struct sym_tcbh`, and `struct sym_lcbh` are explicitly laid out headers copied or directly loaded by SCRIPTS depending on chip features. Allocator-facing types include `m_pool_ident_t`, `struct sym_m_vtob`, and `struct sym_m_pool`.

The exported driver methods declared here include firmware binding (`sym_find_firmware()`, `sym_fw_bind_script()`), host/interrupt control (`sym_start_up()`, `sym_interrupt()`, `sym_reset_scsi_bus()`), command lifecycle (`sym_get_ccb()`, `sym_free_ccb()`, `sym_queue_scsiio()`, `sym_abort_scsiio()`), target/LUN lifecycle (`sym_alloc_lcb()`, `sym_free_lcb()`, `sym_clear_tasks()`), and host allocation/attach (`sym_hcb_attach()`, `sym_hcb_free()`).

## Control Flow And State

The structures expose the runtime flow expected by the driver. A Linux `scsi_cmnd` is wrapped by a `sym_ccb`; its first member is `struct sym_dsb`, which is addressed by the chip DSA register. The DSB contains the script entry points, phase mismatch contexts, selection tables, message/CDB/sense table moves, and the scatter/gather move table. The host keeps free, busy, and completion CCB queues plus hashed CCB lookup by DSA bus address.

Target state is split into `sym_tcb` and `sym_lcb`. The target block holds desired and last-printed transfer parameters, NVRAM/user flags, negotiated command limits, and pointers to LUN structures. The LUN block maintains task tables, busy tagged/untagged counters, tag allocation buffers, optional device queueing state, and command reordering counters. `sym_lp()` hides the LUN 0 fast path versus allocated multi-LUN table.

`sym_hcb` is persistent per-adapter state. It stores saved and runtime chip register values, script RAM/main-memory addresses, firmware callback pointers, queue producer/consumer positions, controller capabilities, DMA mode state, abort buffers, and 64-bit DMA segment maps where enabled. The SCRIPTS processor observes several of these fields directly, so layout and byte order conversions are part of the ABI.

## Dependencies And Integration Points

This header depends on Linux memory/DMA/MMIO facilities, SCSI core types, and many driver-private definitions from surrounding `sym53c8xx_2` headers such as register layouts, firmware address tables, table move/select records, and OS-specific `sym_shcb` fields. It integrates with `sym_malloc.c` through `__sym_calloc_dma()`, `__sym_mfree_dma()`, and `__vtobus()`, and with NVRAM code by storing `usrflags`, `usr_period`, `usr_width`, and `usrtags` in each target.

The DMA scatter/gather builder has three compile-time modes. Mode 0 writes a 32-bit bus address and length. Mode 1 packs address bits 32-39 into the high byte of the size field. Mode 2 uses chip DMA segment registers and `sym_lookup_dmap()` to map 64-bit upper address bits into a segment selector. These fields are consumed by firmware/SCRIPTS, so incorrect packing causes silent data corruption.

## Risks And Test Signals

The largest risk is ABI drift between C layouts and SCRIPTS offsets. Comments state that CCB/TCB/LCB headers and phase mismatch contexts must remain at specific offsets, and several fields are read by chip scripts with limited arithmetic. Any structure edit needs compile-time layout review and hardware/firmware tests.

Other risks are DMA address truncation in the wrong `SYM_CONF_DMA_ADDRESSING_MODE`, missing memory barriers before script restart, queue size misconfiguration beyond a page, and stale global header copies on chips without `FE_LDSTR`. Useful tests are boot/probe on each supported chip class, heavy tagged queue I/O, disconnect/reselect stress, sync/wide/PPR negotiation, 64-bit DMA boundary tests, abort/reset paths, and debug-flag traces for allocation, negotiation, queue, result, and phase behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_hipd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_malloc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_malloc.c

## Purpose

`sym_malloc.c` implements the private allocator used by the Symbios/LSI 53C8xx driver for naturally aligned memory, especially DMA-coherent script-visible objects. The allocator is intentionally simple: it obtains page-sized clusters, splits them into power-of-two chunks down to 16 bytes, merges buddies on free, and tracks virtual-to-bus translations for DMA pools.

## Important APIs, Types, And Functions

The internal allocator is `___sym_malloc()` and `___sym_mfree()`. `__sym_calloc2()` wraps allocation with zeroing and optional warnings, and `__sym_mfree()` adds debug logging. `mp0` is the non-DMA pool used to allocate allocator metadata such as `MPOOL` and `VTOB` records.

DMA-specific pool management is handled by `___get_dma_mem_cluster()`, `___free_dma_mem_cluster()`, `___get_dma_pool()`, `___cre_dma_pool()`, and `___del_dma_pool()`. The external functions declared in `sym_hipd.h` are implemented as `__sym_calloc_dma()`, `__sym_mfree_dma()`, and `__vtobus()`.

## Control Flow And State

Allocation rounds the requested size up to the next allocator bucket and searches the corresponding free list. If the bucket is empty, larger buckets are searched until a whole cluster must be obtained with the pool method. A larger block is then split downward by placing buddy halves into lower free lists. Freeing performs the reverse: it searches the current free list for the buddy address, merges when found, and repeats until either the buddy is absent or the full cluster size is reached.

DMA pools are keyed by `m_pool_ident_t`, which is a `struct device *` in this driver. Each DMA cluster allocation creates a `sym_m_vtob` record in `mp0`, fills it through `dma_alloc_coherent()`, hashes it by virtual cluster address, and links it into the pool. `__vtobus()` masks an arbitrary pointer down to the cluster base, finds the `VTOB` record, and returns the coherent DMA address plus the offset.

All public DMA allocation/free/translation operations are serialized by the global `sym53c8xx_lock` spinlock with IRQ save/restore. When `SYM_MEM_FREE_UNUSED` is enabled, completely free clusters are returned immediately and empty DMA pools are deleted.

## Dependencies And Integration Points

The file includes `sym_glue.h` and relies on allocator definitions from `sym_hipd.h`: `m_pool_p`, `m_vtob_p`, bucket sizes, cluster size/mask, `M_GET_MEM_CLUSTER()`, and DMA cluster helpers. It uses Linux `dma_alloc_coherent()`/`dma_free_coherent()` through inline helpers in the header, page allocation for the metadata pool, and `spin_lock_irqsave()` because callers can be in atomic SCSI paths.

Driver code consumes this allocator through macros such as `sym_calloc_dma()`, `sym_mfree_dma()`, and `vtobus()`. The allocator's alignment behavior supports SCRIPTS address arithmetic and table-layout assumptions described in `sym_hipd.h`.

## Risks And Test Signals

`__vtobus()` panics on failed lookup, so every translated pointer must originate from the matching DMA pool and remain inside an allocated cluster. Pointer arithmetic uses `m - a` on `void *`, which depends on compiler behavior accepted by this kernel codebase. The global lock is simple but serializes all sym DMA allocator users; deadlock risk comes from calling into it while holding locks that can be taken by DMA allocation reclaim paths, although allocations use atomic/GFP constraints.

Useful test signals are allocation failure warnings, `DEBUG_ALLOC` traces, stress with many CCB/LCB/table allocations, repeated attach/detach to verify pool deletion, DMA mapping under IOMMU/SWIOTLB, and fault injection around `dma_alloc_coherent()` and metadata allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_malloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_misc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_misc.h

## Purpose

`sym_misc.h` provides small infrastructure helpers for the `sym53c8xx_2` driver: an intrusive doubly linked queue abstraction, bitmap macros, and a compile-time log2-round-up expression used by CCB hash calculations.

## Important APIs, Types, And Functions

`SYM_QUEHEAD` is the queue node/header type. Core helpers are `sym_que_init()`, `sym_que_first()`, `sym_que_last()`, `sym_que_empty()`, `sym_que_splice()`, `sym_que_move()`, `sym_remque_head()`, and `sym_remque_tail()`. Low-level insertion/removal is performed by `__sym_que_add()` and `__sym_que_del()`, with macro aliases `sym_insque()`, `sym_remque()`, `sym_insque_head()`, and `sym_insque_tail()`. `sym_que_entry()` wraps `container_of()`.

Bitmap macros `sym_set_bit()`, `sym_clr_bit()`, and `sym_is_bit()` operate on `u32` arrays. `_LGRU16_()` computes a rounded-up base-2 logarithm for 16-bit constants using chained ternary fragments.

## Control Flow And State

The queue implementation uses a circular sentinel model. Empty queues point `flink` and `blink` back to the head. Insertions splice a new node between a previous and next node; removals reconnect neighbors without reinitializing the removed node. `sym_que_splice()` prepends a whole non-empty list into another head, while `sym_que_move()` transfers all elements and reinitializes the origin.

There is no locking in this header. Queue safety depends entirely on callers holding the correct host lock or being in serialized initialization/teardown code.

## Dependencies And Integration Points

The queue type is embedded in `struct sym_ccb`, `struct sym_hcb`, and optional LUN queueing structures defined in `sym_hipd.h`. It supports free, busy, completion, waiting, and started CCB lists. `_LGRU16_()` is used in the DSA-to-CCB hash macro to keep hash calculation matched to the `struct sym_ccb` size.

## Risks And Test Signals

Because `sym_remque()` does not poison or reinitialize nodes, double removal or reusing a node in two queues can corrupt the list silently. `sym_que_splice()` leaves the donor list linked into the destination rather than resetting it, while `sym_que_move()` does reset the origin; callers must choose the correct semantic. Bitmap macros assume valid indexes and a `u32 *` backing store.

Test signals are queue integrity under command allocation/completion stress, abort paths that move busy CCBs to completion queues, and debug queue tracing with `DEBUG_QUEUE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_nvram.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_nvram.c

## Purpose

`sym_nvram.c` discovers, reads, validates, and applies persistent adapter configuration for the Symbios/LSI driver. It supports Symbios 24C16 EEPROM format, Tekram 24C16/93C46 formats, and optional PA-RISC firmware initiator data. The result is translated into host identity, parity, scan ordering, bus reset policy, and per-target queueing/disconnect/sync/wide settings.

## Important APIs, Types, And Functions

The public functions are `sym_nvram_setup_host()`, `sym_nvram_setup_target()`, `sym_read_nvram()`, and `sym_nvram_type()`. Format-specific policy helpers are `sym_Symbios_setup_target()` and `sym_Tekram_setup_target()`. Debug-only dumpers are compiled behind `SYM_CONF_DEBUG_NVRAM`.

The 24C16 serial EEPROM path is implemented by `S24C16_set_bit()`, `S24C16_start()`, `S24C16_stop()`, `S24C16_do_bit()`, `S24C16_write_ack()`, `S24C16_read_ack()`, `S24C16_write_byte()`, and `S24C16_read_byte()`. `sym_read_S24C16_nvram()` reads arbitrary byte ranges. Optional write support is guarded by `SYM_CONF_NVRAM_WRITE_SUPPORT`.

The 93C46 Tekram path uses `T93C46_Clk()`, `T93C46_Read_Bit()`, `T93C46_Write_Bit()`, `T93C46_Stop()`, `T93C46_Send_Command()`, `T93C46_Read_Word()`, and `T93C46_Read_Data()`. Format validators are `sym_read_Symbios_nvram()` and `sym_read_Tekram_nvram()`.

## Control Flow And State

`sym_read_nvram()` probes in priority order. It first attempts Symbios format by reading from `SYMBIOS_NVRAM_ADDRESS`, checking type, trailer, byte count, and checksum. If that fails, it tries Tekram format, choosing 24C16 for specific NCR device IDs and falling back to 93C46 where appropriate, then validates the 0x1234 checksum. If both fail, it asks PA-RISC PDC firmware where compiled. `nvp->type` records the winning source or zero.

EEPROM access is bit-banged through chip GPIO registers. Each read saves `nc_gpreg` and `nc_gpcntl`, configures data/clock pins, performs start/address/read/ack/stop sequences, and restores original GPIO state. The deliberate `udelay()` calls and dummy mailbox reads pace the serial protocol.

Host setup applies validated NVRAM only after detection. Symbios NVRAM can disable parity bits in `rv_scntl0`, set `np->myaddr`, increase verbosity, request reverse scan ordering, and set `SYM_AVOID_BUS_RESET`. Tekram sets the host ID. PA-RISC can override initiator ID, sync factor, width, and bus mode.

Per-target setup mutates `struct sym_tcb`: Symbios can disable tags, disable disconnects, disable boot/LUN scanning, and set requested period/width. Tekram can set tag count from `max_tags_index`, enable disconnect, set period from `Tekram_sync[]`, and enable wide negotiation.

## Dependencies And Integration Points

This file includes `sym_glue.h` and `sym_nvram.h`, uses PCI device IDs to decide Tekram access method, and directly touches chip registers through `INB()`/`OUTB()` macros. Its outputs are consumed during HCB attach and target initialization, shaping later SCSI negotiation, queue depth, scan behavior, and reset policy.

## Risks And Test Signals

Hardware risks are concentrated in GPIO bit-banging. A missed restore of `gpcntl/gpreg`, wrong pin direction, or insufficient delay can leave EEPROM or adapter GPIO in a bad state. Validation failures intentionally fall through to other formats, so corrupted EEPROM should not be trusted. The optional write path contains an apparent `y` loop variable use not declared in the visible function, making write support suspect if enabled.

Useful tests are probe on cards with no NVRAM, Symbios NVRAM, Tekram 24C16, Tekram 93C46, and PA-RISC firmware; checksum/trailer corruption tests; confirmation that host ID/parity/scan order are applied; and per-target negotiation traces showing expected tags, disconnect, sync period, and width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_nvram.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_nvram.h

## Purpose

`sym_nvram.h` defines the persistent configuration formats and public NVRAM interface for the Symbios/LSI 53C8xx driver. It captures the on-card Symbios and Tekram EEPROM layouts, related flag definitions, and the `struct sym_nvram` union passed to setup code.

## Important APIs, Types, And Functions

The Symbios format is represented by `struct Symbios_nvram`, including controller flags, boot-order host records, 16 target records, SCAM records, spare target space, and trailer. Important flags include parity, verbose messages, high-to-low scan order, avoid bus reset, target disconnect, scan-at-boot, scan-LUNs, and tagged queueing.

The Tekram format is represented by `struct Tekram_nvram`, with 16 target records plus host ID, removable/media policy, boot delay index, max tags index, and flags for parity, sync negotiation, disconnect, start command, tagged commands, and wide negotiation.

`struct sym_nvram` stores a type discriminator (`SYM_SYMBIOS_NVRAM`, `SYM_TEKRAM_NVRAM`, `SYM_PARISC_PDC`) and, when NVRAM support is enabled, the corresponding union payload. Public functions are `sym_nvram_setup_host()`, `sym_nvram_setup_target()`, `sym_read_nvram()`, and `sym_nvram_type()`. Stub inline implementations are provided when `SYM_CONF_NVRAM_SUPPORT` is disabled.

## Control Flow And State

The header itself has no runtime control flow, but its structures define the persistent state decoded by `sym_nvram.c`. The data affects HBA initialization and per-target defaults before normal SCSI negotiation begins.

## Dependencies And Integration Points

It includes `sym53c8xx.h` for driver configuration and SCSI/HBA types. The structures are used by NVRAM readers, host attach code, and target setup code. On non-PA-RISC systems a dummy `struct pdc_initiator` is declared so the union remains compilable without firmware support.

## Risks And Test Signals

These structures map binary EEPROM layouts, so packing, field sizes, and flag meanings must remain stable. The fallback stubs have a signature mismatch risk: the disabled-support `sym_nvram_setup_target()` inline accepts fewer parameters than the enabled declaration in this file's visible code, which would matter if compiled in a configuration that calls the three-argument form while NVRAM support is off.

Test signals are successful compilation across NVRAM-enabled/disabled and PA-RISC/non-PA-RISC configurations, plus runtime confirmation that decoded fields match EEPROM dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_nvram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/virtio_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/virtio_scsi.c

## Purpose

`virtio_scsi.c` implements the Linux SCSI host adapter driver for virtio SCSI devices. It bridges SCSI midlayer commands, error handling, device scanning, hotplug/change events, blk-mq queue mapping, and virtio virtqueue transport. The device model uses one control virtqueue, one event virtqueue, and one or more request virtqueues.

## Important APIs, Types, And Functions

Primary state is `struct virtio_scsi`, which holds the virtio device, event buffers, queue counts/maps, stop-events flag, control/event queues, DMA-from-device event storage, and flexible request queue array. `struct virtio_scsi_vq` wraps a `struct virtqueue *` with a spinlock. `struct virtio_scsi_cmd` is per-command storage placed in `scsi_cmnd` private data for normal I/O or allocated from a mempool for TMFs.

Submission and completion helpers include `__virtscsi_add_cmd()`, `virtscsi_add_cmd()`, `virtscsi_kick_vq()`, `virtscsi_queuecommand()`, `virtscsi_complete_cmd()`, `virtscsi_vq_done()`, `virtscsi_req_done()`, and `virtscsi_mq_poll()`. Header builders are `virtio_scsi_init_hdr()` and, with protection information, `virtio_scsi_init_hdr_pi()`.

Error handling uses `virtscsi_tmf()`, `virtscsi_abort()`, `virtscsi_device_reset()`, and `virtscsi_eh_timed_out()`. Event handling uses `virtscsi_kick_event()`, `virtscsi_kick_event_all()`, `virtscsi_complete_event()`, `virtscsi_handle_event()`, `virtscsi_handle_transport_reset()`, `virtscsi_handle_param_change()`, and `virtscsi_rescan_hotunplug()`.

Lifecycle is implemented by `virtscsi_probe()`, `virtscsi_remove()`, `virtscsi_freeze()`, `virtscsi_restore()`, module init/exit, and the `virtio_driver` registration.

## Control Flow And State

Probe reads virtio config values, clamps queue count to possible CPUs/blk-mq queues, allocates a `Scsi_Host` with enough private space for request queues, initializes virtqueues, configures CDB/sense sizes, sets SCSI host limits, advertises protection information where supported, calls `scsi_add_host()`, marks the virtio device ready, posts event buffers, and scans the host.

Normal I/O starts in `virtscsi_queuecommand()`. The blk-mq unique tag selects a request virtqueue. The driver fills a virtio SCSI request header, copies the CDB, builds SG lists containing request header, optional data-out/protection buffers, response header, optional data-in/protection buffers, and adds them to the virtqueue under `vq_lock`. It kicks immediately only when `SCMD_LAST` is set; batched requests are kicked via `commit_rqs()`.

Completion callbacks drain virtqueue buffers while callbacks are disabled, translate virtio response codes into SCSI host/status bytes, set residuals and sense data, and call `scsi_done()`. Poll queues omit interrupts and are drained from `mq_poll`.

The event queue keeps eight reusable event buffers. Completion of an event buffer queues work unless removal has set `stop_events`. Work handles missed events by probing existing devices and rescanning the host, handles transport reset by adding/removing LUNs, handles parameter-change ASC/ASCQ by rescanning a device, then reposts the event buffer.

Task management functions allocate a command object from a mempool, send TMF requests on the control queue, wait synchronously, interpret TMF responses, poll request queues once to close interrupt races, and free the command object.

## Dependencies And Integration Points

The driver integrates with virtio core (`virtio_find_vqs()`, config access, feature negotiation, device ready/reset), SCSI core (`scsi_host_template`, queuecommand, EH handlers, scan/add/remove/rescan), blk-mq queue mapping and polling, block integrity/DIF/DIX support, DMA cache-clean inbuf posting for events, and system freezable workqueues. Module parameter `virtscsi_poll_queues` controls how many request queues are allocated for polling.

## Risks And Test Signals

Risks include races during event teardown, TMF completion before request interrupt processing, virtqueue full handling, and endian conversion of event/reason/status fields. The code explicitly polls request queues after TMFs and sets `stop_events` before canceling work to mitigate two major races. Another risk is stale hot-unplug state when missed events occur; the driver mitigates by issuing INQUIRY to known devices and rescanning.

Useful tests are virtio-scsi boot and hotplug/hotunplug, missed-event injection, queue-depth changes, request batching with `SCMD_LAST`, blk-mq poll queues, suspend/resume freeze/restore, abort and LUN reset error handling, T10 PI I/O, large SG lists up to `seg_max`, and transport failure response mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/virtio_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/vmw_pvscsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/vmw_pvscsi.c

## Purpose

`vmw_pvscsi.c` implements the Linux PCI driver for VMware's paravirtualized SCSI host adapter. It maps VMware PVSCSI MMIO registers and DMA rings, translates SCSI commands into request descriptors, processes completion and message rings, supports SCSI error handling, and registers a `Scsi_Host` behind the PCI device.

## Important APIs, Types, And Functions

Driver-private state is `struct pvscsi_adapter`, containing MMIO base, revision/features, hardware lock, optional message workqueue, request/completion/message rings and DMA addresses, shared ring state page, PCI and SCSI host pointers, a free context list, and a context map. Each `struct pvscsi_ctx` tracks the SCSI command, per-context SG list page, DMA addresses for data/sense/SG list, and optional abort completion.

Register and command helpers are `pvscsi_reg_read()`, `pvscsi_reg_write()`, `pvscsi_write_cmd_desc()`, `ll_adapter_reset()`, `ll_bus_reset()`, `ll_device_reset()`, `pvscsi_abort_cmd()`, `pvscsi_kick_rw_io()`, and `pvscsi_process_request_ring()`.

I/O helpers include `pvscsi_acquire_context()`, `pvscsi_release_context()`, `pvscsi_map_context()`, `pvscsi_get_context()`, `pvscsi_create_sg()`, `pvscsi_map_buffers()`, `pvscsi_unmap_buffers()`, `pvscsi_queue_ring()`, and `pvscsi_queue_lck()`. Completion and EH paths are `pvscsi_process_completion_ring()`, `pvscsi_complete_request()`, `pvscsi_abort()`, `pvscsi_host_reset()`, `pvscsi_bus_reset()`, `pvscsi_device_reset()`, and `pvscsi_reset_all()`.

Lifecycle and resources are handled by `pvscsi_probe()`, `pvscsi_remove()`, `pvscsi_shutdown()`, `pvscsi_allocate_rings()`, `pvscsi_setup_all_rings()`, `pvscsi_allocate_sg()`, `pvscsi_release_resources()`, and IRQ setup/shutdown. Hotplug messages flow through `pvscsi_process_msg_ring()`, `pvscsi_process_msg()`, and `pvscsi_msg_workqueue_handler()`.

## Control Flow And State

Probe enables PCI, sets a 64-bit or 32-bit coherent DMA mask, requests BARs, locates an MMIO BAR large enough for the PVSCSI register layout, maps it, and uses a temporary adapter to query controller configuration for max targets. It chooses ring pages, allocates a SCSI host, resets the adapter, detects optional message-ring and request-threshold support, allocates coherent ring memory, sets up rings with page frame numbers, allocates the context map and per-context SG pages, obtains one IRQ vector, registers an ISR, adds the SCSI host, unmasks interrupts, and scans.

Queueing takes `hw_lock`, obtains a context from `cmd_pool`, fills a request ring slot selected by `reqProdIdx`, maps the sense buffer, sets CDB/LUN/tag/direction fields, maps data either as direct DMA or as a one-page PVSCSI SG list, writes a non-zero context ID, uses a compiler barrier, advances `reqProdIdx`, releases the lock, and kicks either the RW or non-RW path. RW kicks can be coalesced by the device-supplied request threshold.

Completions are consumed while `cmpConsIdx != cmpProdIdx`. Barriers prevent the compiler from reading a descriptor before the emulated device has published it or advancing the consumer before descriptor fields are consumed. Completion maps `hostStatus` and `scsiStatus` to Linux SCSI result bytes, sets residuals where appropriate, unmaps buffers, releases the context, and calls `scsi_done()`. If an abort is pending for that context, the normal completion is swallowed and the abort waiter is completed.

Error handling serializes with the hardware lock. Abort first drains completions, locates the context, sets `abort_cmp`, sends `PVSCSI_CMD_ABORT_CMD`, waits up to two seconds, then either reports `DID_ABORT` or fails. Host reset disables message work, drains request/completion rings around adapter reset, completes all outstanding commands as reset, rebuilds rings, and unmasks interrupts. Bus/device reset flushes requests, sends the reset command, and drains completions.

Message-ring interrupts schedule an ordered workqueue. Device-added messages add a missing SCSI device, while device-removed messages look up and remove the device.

## Dependencies And Integration Points

The driver depends on PCI, DMA coherent allocation, Linux SCSI midlayer, IRQ vector allocation, workqueues, and the ABI structures in `vmw_pvscsi.h`. It exposes module parameters for ring pages, message-ring pages, commands per LUN, MSI/MSI-X disable switches, message-ring enablement, and request-threshold coalescing.

## Risks And Test Signals

Resource cleanup has sharp edges: several error labels call `pvscsi_shutdown_intr()` even on paths where IRQ vectors may not have been allocated, so probe-failure paths should be audited in the exact kernel context. Ring memory and context mappings are tightly coupled; `pvscsi_reset_all()` is only safe after reset or when the completion ring will not be walked again. The code relies on x86 strong ordering and uses compiler barriers rather than full memory barriers because PVSCSI is VMware/x86-focused.

Other risks are SG count overflow beyond a single PVSCSI SG page, residual underflow if a completion reports larger `dataLen` in underrun cases, hotplug message races with host removal, and abort races with normal completion. Tests should cover 32/64-bit DMA masks, MSI-X/MSI/INTx, ring-page parameter extremes, heavy queue depth, abort/reset paths, hot-add/remove messages, direct and SG I/O, request coalescing, suspend/shutdown, and probe failure injection at each allocation/register step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/vmw_pvscsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/vmw_pvscsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/vmw_pvscsi.h

## Purpose

`vmw_pvscsi.h` defines the VMware PVSCSI adapter ABI used by `vmw_pvscsi.c`: PCI ID, register offsets, command opcodes, ring state, request/completion/message descriptors, SG element format, config page format, interrupt bits, and ring sizing limits. It is the contract between the guest driver and VMware virtual hardware.

## Important APIs, Types, And Functions

Key enums are `HostBusAdapterStatus`, `ScsiDeviceStatus`, `PVSCSIRegOffset`, `PVSCSICommands`, config page types/address types, and message types. Important command descriptors are `PVSCSICmdDescSetupRings`, `PVSCSICmdDescSetupMsgRing`, `PVSCSICmdDescAbortCmd`, `PVSCSICmdDescResetDevice`, `PVSCSICmdDescConfigCmd`, and `PVSCSICmdDescSetupReqCall`.

Ring ABI types are `PVSCSIRingsState`, `PVSCSIRingReqDesc`, `PVSCSISGElement`, `PVSCSIRingCmpDesc`, `PVSCSIRingMsgDesc`, and `PVSCSIMsgDescDevStatusChanged`. Configuration query output is represented by `PVSCSIConfigPageHeader` and `PVSCSIConfigPageController`.

## Control Flow And State

The header has no executable flow, but defines producer/consumer indexes for request, completion, and message rings. Requests carry a non-zero 64-bit context, data address/length, sense address/length, flags, CDB, LUN, tag, bus/target, and vCPU hint. Completions return the same context, transfer length, sense length, host status, and SCSI status. Message descriptors notify device add/remove events.

Setup commands pass page frame numbers for ring memory to the device. The rings state page also contains a request call threshold used for driver-side request coalescing when supported by the virtual adapter.

## Dependencies And Integration Points

The header includes Linux integer types and is consumed directly by the PVSCSI PCI driver. Its constants determine SCSI host limits such as maximum SG entries, maximum ring depth, supported interrupt bits, and MMIO mapping size.

## Risks And Test Signals

Because all descriptors are `__packed` ABI structures, field size, ordering, and alignment are critical. The `MASK(n)` macro uses `1 << n`, so callers must avoid widths that overflow an `int`; current ring log2 values are small. The request context restrictions documented in comments matter because the driver maps contexts to 1-based indexes.

Test signals include successful setup-ring command negotiation, correct max queue depth from page counts, completion context round trips, hotplug message decoding, config page query status, and interrupt masking/unmasking behavior for completion and message bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/vmw_pvscsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/wd33c93.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/wd33c93.c

## Purpose

`wd33c93.c` is the generic core driver for Western Digital WD33C93-family SCSI controller chips used by several platform-specific host adapters. It provides command queueing, selection, disconnect/reselect, synchronous transfer negotiation, PIO/DMA data movement coordination, interrupt-state handling, abort/reset support, runtime setup parsing, and `/proc` diagnostics.

## Important APIs, Types, And Functions

The exported entry points are `wd33c93_init()`, `wd33c93_queuecommand()`, `wd33c93_intr()`, `wd33c93_abort()`, `wd33c93_host_reset()`, `wd33c93_show_info()`, and `wd33c93_write_info()`. Platform glue supplies register addresses plus `dma_setup_t` and `dma_stop_t` callbacks.

Register helpers are `read_wd33c93()`, `read_wd33c93_count()`, `read_aux_stat()`, `write_wd33c93()`, `write_wd33c93_count()`, `write_wd33c93_cmd()`, `write_wd33c93_cdb()`, and `read_1_byte()`. Transfer helpers are `transfer_pio()` and `transfer_bytes()`.

Negotiation/setup helpers are `round_period()`, `calc_sync_xfer()`, `calc_sync_msg()`, `calc_sx_table()`, `set_clk_freq()`, `set_resync()`, `wd33c93_setup()`, and `check_setup_args()`. Core command scheduling is `wd33c93_execute()`, and chip reset is `reset_wd33c93()`.

## Control Flow And State

`wd33c93_init()` initializes `struct WD33C93_hostdata`, calculates synchronous period tables from input clock, applies command-line/module setup keywords, resets the chip, detects chip revision/microcode, initializes queues and statistics, and prints configuration. Runtime state is stored in hostdata: `input_Q`, `selecting`, `connected`, `disconnected_Q`, per-target/lun busy bits, DMA state, level-2 command mode, disconnect policy, sync parameters, incoming/outgoing messages, and proc counters.

`wd33c93_queuecommand_lck()` prepares the command-private `scsi_pointer` scratchpad with SG pointer/residual state, presets illegal status, inserts the command into `input_Q` with REQUEST SENSE prioritized at the head, then calls `wd33c93_execute()`.

`wd33c93_execute()` runs only when no command is selecting or connected. It chooses the first queued command whose target/lun is not busy, removes it from `input_Q`, decides whether disconnect/reselect should be allowed using global policy, target type, disconnected queue presence, and queued work for other targets, programs destination/source/LUN/sync registers, marks the target/lun busy, and starts either `SEL_ATN` for explicit message negotiation or `SEL_ATN_XFER` for level-2 select-and-transfer.

`wd33c93_intr()` is the main state machine. It ignores non-interrupt/busy states, stops platform DMA when needed and updates residual pointers, reads the WD status to clear the interrupt, and switches on command/status phase. It handles selection timeouts, successful selection and outgoing IDENTIFY/SDTR construction, data in/out via PIO or DMA, command/status/message phases, message parsing, level-2 completion, saved/restored data pointers, command-complete and temporary disconnects, unexpected disconnects, reselection on both newer and older chips, and unknown interrupts.

Completion clears the busy bit, sets SCSI result/status/message bytes, calls `scsi_done()`, unlocks, and starts another queued command. Temporary disconnects move the command to `disconnected_Q`; reselection locates it by target/lun, removes it from that queue, restores direction registers, and resumes transfer or connected state.

Abort has four cases: remove an unissued command from `input_Q`, actively abort/disconnect a connected command, fail for a disconnected command, or report a likely race if the command is in no queue. Host reset stops DMA, clears all queues/state/sync status, resets the chip, and returns success.

## Dependencies And Integration Points

The file depends on the SCSI midlayer, platform IRQ/register mapping, platform DMA callbacks, and definitions in `wd33c93.h`. It exports symbols for board-specific drivers. `/proc` integration uses `seq_file` output and writable runtime keywords to adjust debug, disconnect, period, resync, proc mask, DMA mode, level2, burst, fast, and nosync settings.

## Risks And Test Signals

This is a complex interrupt-driven state machine with several historical edge cases. Risks include stale queue links via `host_scribble`, races around `scsi_done()` re-enabling interrupts, incorrect residual updates after partial DMA/disconnect, unsupported connected-command abort behavior, infinite-print loop on intrusive reselect trouble, and assumptions around older chips that lack advanced reselection messages. Runtime option parsing is permissive and mostly unvalidated for `level2`.

High-value tests include single and multi-device I/O, disconnect/reselect under concurrent targets, REQUEST SENSE prioritization, sync negotiation accepted/rejected/unsolicited, fast/burst/nodma modes, SG boundary transitions, PIO fallback, selection timeout, abort for queued/connected/disconnected commands, host reset recovery, old WD33C93 versus A/B chips, and proc runtime changes with statistics enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/wd33c93.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/wd33c93.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/wd33c93.h

## Purpose

`wd33c93.h` defines the register map, command/status constants, host-private state, platform callback types, and exported API for the generic WD33C93 SCSI core. Platform-specific drivers include this header to wire a particular board's registers and DMA engine into the shared core.

## Important APIs, Types, And Functions

The header defines WD register offsets (`WD_OWN_ID`, `WD_CONTROL`, `WD_COMMAND`, `WD_DATA`, etc.), WD commands (`WD_CMD_RESET`, `WD_CMD_SEL_ATN_XFER`, `WD_CMD_TRANS_INFO`, and others), auxiliary status bits, SCSI bus phase encodings, command status register values, own-ID/control/timeout/synchronous-transfer/destination/source bit fields, and chip identifiers.

`wd33c93_regs` stores the two memory-mapped chip register pointers (`SASR` and `SCMD`). `dma_setup_t` and `dma_stop_t` are platform callbacks for beginning and stopping DMA. `struct sx_period` maps transfer period nanoseconds to register values. `struct WD33C93_hostdata` is the full per-host state block used by the core.

Exported functions are `wd33c93_init()`, `wd33c93_queuecommand()`, `wd33c93_intr()`, `wd33c93_abort()`, `wd33c93_host_reset()`, `wd33c93_show_info()`, and `wd33c93_write_info()`. `WD33C93_scsi_pointer()` returns the command-private scratchpad.

## Control Flow And State

The header defines state machine values (`S_UNCONNECTED`, `S_SELECTING`, `S_RUNNING_LEVEL2`, `S_CONNECTED`, `S_PRE_TMP_DISC`, `S_PRE_CMP_DISC`), DMA state (`D_DMA_OFF`, `D_DMA_RUNNING`), level-2 command modes, disconnect policy, debug flags, sync negotiation states, and proc-output masks.

`struct WD33C93_hostdata` persists queue heads, current selecting/connected commands, disconnected queue, per-target busy bits, DMA mode, synchronous transfer settings, message buffers, setup/debug flags, clock/chip revision, and optional statistics. This state is mutated by `wd33c93.c` under its lock and by platform interrupt entry points calling `wd33c93_intr()`.

## Dependencies And Integration Points

The header depends on Linux SCSI host and command types. It deliberately keeps platform hardware dependencies abstract through `wd33c93_regs`, `dma_setup_t`, and `dma_stop_t`, allowing Amiga, SGI, MVME, and other board drivers to share the SCSI protocol core while providing register location and DMA mechanics.

## Risks And Test Signals

Several compile-time debug/proc macros are enabled directly in the header, affecting code inclusion and runtime behavior. `uchar` is a global macro alias. Queue pointers are stored in `scsi_cmnd->host_scribble`, so any integration with other code using that field would conflict. The hostdata layout is part of platform allocation assumptions because board drivers allocate `Scsi_Host` private data for it.

Tests should compile all platform users, verify `cmd_size` is sufficient for `scsi_pointer`, exercise DMA callbacks with both directions and stop statuses, inspect `/proc` output masks, and run interrupt/queue/reset paths on each chip revision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/wd33c93.h -->
