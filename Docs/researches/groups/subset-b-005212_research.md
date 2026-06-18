# Group Research: subset-b-005212

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_cp.c -->
## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_cp.c

Purpose: implements vfio-ccw channel-program translation. It copies guest CCW chains from VFIO DMA/IOMMU-visible guest memory, follows TIC branches, converts format-0 CCWs to format-1, pins guest data pages, builds host IDALs, and later maps host completion addresses back to guest addresses.

Important APIs/types/functions: internal `struct page_array` tracks guest IOVAs and pinned pages; `struct ccwchain` stores translated CCW arrays and per-CCW page arrays. Exported operations are `cp_init()`, `cp_free()`, `cp_prefetch()`, `cp_get_orb()`, `cp_update_scsw()`, and `cp_iova_pinned()`. Key helpers include `ccwchain_calc_length()`, `ccwchain_handle_ccw()`, `ccwchain_loop_tic()`, `ccwchain_fetch_ccw()`, `get_guest_idal()`, and `page_array_pin()/unpin()`.

Control flow: `cp_init()` initializes the list, saves the ORB, copies the first guest chain via `vfio_dma_rw()`, calculates bounded chain length, and recursively follows TICs that target unseen chain segments. `cp_prefetch()` walks every chain and translates each CCW: TICs are retargeted to host CCW storage, non-TIC data addresses become host IDALs, and data-transfer CCWs pin guest pages through VFIO. `cp_get_orb()` rewrites the ORB to point at the first host CCW and forces format-2 IDAL semantics. Interrupt completion later calls `cp_update_scsw()` to convert the SCSW CPA back into the corresponding guest CPA.

State and persistence: state is in `struct channel_program` for one active I/O. It owns the chain list, saved ORB, initialized flag, and reusable `guest_cp` scratch buffer allocated by the mdev code. Pinned pages and allocated IDAL buffers persist only until `cp_free()`.

Dependencies and integration: depends on VFIO pin/unpin and `vfio_dma_rw()`, s390 channel I/O structures, IDAL helpers, and `vfio_ccw_private` container lookup. It feeds `vfio_ccw_fsm.c` start-subchannel flow and supports `vfio_ccw_ops.c` invalidation via `cp_iova_pinned()`.

Risks and test signals: high-risk areas are chain-loop handling, 2K versus 4K IDAW math, partial pin cleanup, unaligned IDAL coalescing, and DMA32 host address assumptions. Test by issuing direct and IDAL CCWs, TIC fan-out/back-edge programs, skipped reads, zero-count commands, invalid guest addresses, DMA unmap during pending I/O, and final SCSW CPA translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_cp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_cp.h -->
## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_cp.h

Purpose: declares the channel-program translation interface used by vfio-ccw. It is the narrow contract between the finite-state-machine I/O path and the lower-level CCW/IDAL translation implementation.

Important APIs/types/functions: `CCWCHAIN_LEN_MAX` caps a single chain at 256 CCWs. `struct channel_program` contains the translated chain list, saved ORB, initialization state, and `guest_cp` scratch storage. Public functions are `cp_init()`, `cp_free()`, `cp_prefetch()`, `cp_get_orb()`, `cp_update_scsw()`, and `cp_iova_pinned()`.

Control flow: users allocate or embed a `channel_program`, allocate `guest_cp`, call `cp_init()` with the userspace ORB, call `cp_prefetch()` before issuing I/O, pass `cp_get_orb()` to `ssch`, update completion status with `cp_update_scsw()`, and finally release resources with `cp_free()`. `cp_iova_pinned()` is an asynchronous invalidation guard used outside the normal start/completion flow.

State and persistence: the header exposes that the object is stateful and single-operation oriented. `initialized` prevents double initialization and allows free/update/pinned checks to no-op on inactive programs. The list contents are intentionally opaque to callers.

Dependencies and integration: includes s390 `cio`, `scsw`, local `orb.h`, and trace support. It is included by private vfio-ccw driver state and by the channel-program implementation.

Risks and test signals: callers must respect the lifecycle or they can leak pins or attempt I/O with stale translated CCWs. Test signals are correct behavior for repeated init, free without init, invalidation checks on inactive programs, and completion CPA update after successful, halted, and cleared I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_cp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_drv.c -->
## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_drv.c

Purpose: provides the css subchannel driver and module lifecycle for VFIO mediated non-QDIO CCW passthrough. It binds I/O subchannels, creates the mdev parent, handles interrupts and channel-path events, initializes debug/workqueue/region caches, and tears everything down on module exit.

Important APIs/types/functions: global resources include `vfio_ccw_work_q`, region kmem caches, and s390 debug IDs. Core functions are `vfio_ccw_sch_quiesce()`, `vfio_ccw_sch_io_todo()`, `vfio_ccw_crw_todo()`, `vfio_ccw_sch_irq()`, `vfio_ccw_sch_probe()/remove()/shutdown()`, `vfio_ccw_sch_event()`, `vfio_ccw_chp_event()`, and module init/exit.

Control flow: probe rejects QDIO, allocates a `vfio_ccw_parent`, registers a child device, and registers the mdev parent. Open/close behavior is handled by the mdev/FSM code, while hardware interrupts enter `vfio_ccw_sch_irq()` and dispatch `VFIO_CCW_EVENT_INTERRUPT`. Deferred I/O work copies the IRB into the user-visible region, frees completed channel programs, transitions back to IDLE on final solicited interrupt, and signals the I/O eventfd. Channel-path events update path masks, cancel/halt/clear affected paths, queue CRWs, and signal userspace through CRW work.

State and persistence: persistent module state is the workqueue, caches, debug features, css driver registration, ISC registration, and per-subchannel parent device. Per-device runtime state lives in `vfio_ccw_private`. CRWs are queued in a list until userspace reads them through the CRW region.

Dependencies and integration: depends on css/cio/chp infrastructure, mdev, eventfd workqueues, s390 debug, and vfio-ccw FSM/private structures. It is the bridge from host subchannel events into userspace VFIO notification.

Risks and test signals: key risks are lock ordering around `sch->lock`, quiesce completion races, CRW drops under GFP_ATOMIC failure, and correct cleanup after partial init. Test bind/unbind, unexpected interrupts, not-oper transitions, channel-path vary/offline/online events, final versus intermediate interrupts, and module init failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_fsm.c -->
## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_fsm.c

Purpose: implements the vfio-ccw device finite-state machine. It validates user I/O requests, translates and starts channel programs, handles halt/clear async commands, processes interrupts, and controls open/close transitions.

Important APIs/types/functions: the exported dispatch table is `vfio_ccw_jumptable`. Major actions are `fsm_io_request()`, `fsm_io_helper()`, `fsm_async_request()`, `fsm_do_halt()`, `fsm_do_clear()`, `fsm_irq()`, `fsm_open()`, `fsm_close()`, and error/retry/busy handlers. States and events are defined in `vfio_ccw_private.h`.

Control flow: writes to the I/O region generate `VFIO_CCW_EVENT_IO_REQ`. In IDLE, `fsm_io_request()` copies the SCSW, rejects transport mode and halt/clear on the legacy I/O region, builds the channel program via `cp_init()` and `cp_prefetch()`, then calls `ssch()` through `fsm_io_helper()`. Success moves to `CP_PENDING`; translation or start errors free the CP and return IDLE. Async command-region writes dispatch HSCH or CSCH. Interrupts copy the per-CPU IRB and queue deferred work, optionally completing a quiesce waiter.

State and persistence: device state moves among NOT_OPER, STANDBY, IDLE, CP_PROCESSING, and CP_PENDING. The active channel program persists in CP_PENDING until the deferred interrupt path frees it. Close disables or quiesces the subchannel and frees any active CP.

Dependencies and integration: uses s390 `ssch/hsch/csch`, `cio_enable_subchannel()`, `cio_disable_subchannel()`, `vfio_ccw_sch_quiesce()`, tracepoints, and channel-program APIs.

Risks and test signals: high-risk paths are error unwind after partial CP translation, simultaneous async commands while pending, close during pending I/O, and not-oper recursion. Test expected return codes: `-EOPNOTSUPP` for transport/halt/clear in the I/O region, `-EAGAIN` while processing, `-EBUSY` while pending, and successful IRQ-driven IDLE return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_fsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_ops.c -->
## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_ops.c

Purpose: implements the mediated VFIO device operations for vfio-ccw. It allocates per-mdev state, exposes VFIO regions and IRQs, handles reset/open/close/read/write/ioctl, and reacts to IOMMU invalidations.

Important APIs/types/functions: `vfio_ccw_dev_ops` supplies VFIO callbacks. Main functions include `vfio_ccw_mdev_init_dev()`, `probe/remove`, `open_device/close_device`, region `read/write`, `vfio_ccw_mdev_ioctl()`, `vfio_ccw_mdev_set_irqs()`, `vfio_ccw_register_dev_region()`, `vfio_ccw_unregister_dev_regions()`, `vfio_ccw_dma_unmap()`, and request notification.

Control flow: probe allocates a `vfio_ccw_private` and registers an emulated-IOMMU VFIO device. Init allocates `guest_cp` and DMA-capable usercopy regions. Open registers async/SCHIB/CRW extra regions and sends FSM OPEN. Reads and writes decode offsets with `VFIO_CCW_OFFSET_TO_INDEX`; config-region writes copy user data under `io_mutex` and trigger the FSM I/O request. Ioctls report device/region/IRQ info, set eventfds, or reset through close/open. DMA unmap checks whether the active CP pins the invalidated IOVA and resets if necessary.

State and persistence: per-device persistent state includes VFIO eventfd contexts, allocated regions, dynamic region array, FSM state, CRW list, active CP, and work items. Dynamic regions exist only while the device is open.

Dependencies and integration: integrates mdev, VFIO core, VFIO iommufd emulated callbacks, nospec index masking, eventfd, region registration helpers, and the vfio-ccw FSM.

Risks and test signals: risks include eventfd lifetime leaks, region-index bounds, write concurrency returning `-EAGAIN`, dynamic region release ordering, and reset on DMA invalidation while I/O is active. Test VFIO GET_INFO/GET_REGION_INFO/SET_IRQS/RESET, concurrent config writes, eventfd enable/disable/signal forms, open failure unwind, and iommufd attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_private.h -->
## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_private.h

Purpose: central private header for vfio-ccw. It defines device private state, dynamic region plumbing, parent mdev structures, FSM states/events, debug macros, and cross-file globals.

Important APIs/types/functions: `struct vfio_ccw_private` embeds `struct vfio_device`, FSM state, synchronization objects, user-visible regions, dynamic region array, active `channel_program`, IRB/SCSW snapshots, CRW list, eventfd triggers, and work items. It also defines `struct vfio_ccw_region`, `struct vfio_ccw_regops`, `struct vfio_ccw_parent`, `struct vfio_ccw_crw`, state/event enums, `vfio_ccw_fsm_event()`, and registration prototypes for extra regions.

Control flow: the inline `vfio_ccw_fsm_event()` traces state/event against the parent subchannel id and dispatches through `vfio_ccw_jumptable`. Dynamic region offsets are partitioned by a 10-bit offset shift/mask so VFIO region index and intra-region offset can share a file position.

State and persistence: this header documents all durable per-device state boundaries. The active CP, region buffers, eventfds, and work structs live for the mdev lifetime; some additional regions are registered only during open. CRW list entries persist until consumed or device release.

Dependencies and integration: includes VFIO, mdev, eventfd, workqueue, s390 CRW/debug, css, and channel-program APIs. It is consumed by driver, ops, FSM, and region support files.

Risks and test signals: risks are ABI drift in region layout, state table mismatches, alignment assumptions on `vfio_ccw_private`, and missing release callbacks for extra regions. Test compile-time coverage across all users, state/event table completeness, open/close allocation lifecycle, and debug trace visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_trace.c -->
## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_trace.c

Purpose: instantiates vfio-ccw tracepoints and exports their symbols so other compilation units can emit structured trace events.

Important APIs/types/functions: defines `CREATE_TRACE_POINTS`, includes `vfio_ccw_trace.h`, and exports `vfio_ccw_chp_event`, `vfio_ccw_fsm_async_request`, `vfio_ccw_fsm_event`, and `vfio_ccw_fsm_io_request`.

Control flow: this file has no runtime branching beyond normal tracepoint registration generated by the kernel trace framework. Compilation of this unit materializes the trace events declared in the header.

State and persistence: tracepoint descriptors are static kernel instrumentation state. There is no per-device state here.

Dependencies and integration: depends on Linux tracepoint generation rules and the local trace header. Driver and FSM code call the generated trace hooks.

Risks and test signals: risks are duplicate `CREATE_TRACE_POINTS` definitions or missing export when trace users are modular. Test by building vfio-ccw as module/built-in and confirming trace events appear under tracing with expected names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_trace.h -->
## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_trace.h

Purpose: declares trace events for vfio-ccw channel-path and FSM diagnostics. It gives maintainers structured observability for device state transitions, async commands, I/O request failures, and channel path changes.

Important APIs/types/functions: `TRACE_EVENT()` definitions cover `vfio_ccw_chp_event`, `vfio_ccw_fsm_async_request`, `vfio_ccw_fsm_event`, and `vfio_ccw_fsm_io_request`. Each records subchannel id components plus event-specific fields such as path mask, command, state, event, fctl, errno, and error string.

Control flow: call sites pass raw state/action data to tracepoints; the header defines assignment and printk formatting. The bottom `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` block follows kernel tracepoint conventions.

State and persistence: no mutable driver state is owned here. Trace records are transient unless tracing infrastructure buffers them.

Dependencies and integration: includes local `cio.h` and Linux tracepoint APIs. `vfio_ccw_private.h`, `vfio_ccw_drv.c`, and `vfio_ccw_fsm.c` use these tracepoints.

Risks and test signals: risks include format mismatch, pointer lifetime for `errstr`, and missing include-path correctness when moved. Test by enabling events, triggering start/halt/clear/errors/channel-path events, and verifying formatted output has correct subchannel ids and errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/Makefile -->
## sources/distributed-fs/ceph-client/drivers/s390/crypto/Makefile

Purpose: describes how s390 crypto driver objects are grouped into kernel modules based on Kconfig symbols. It wires AP bus, zcrypt, protected-key handlers, and VFIO AP support into the build.

Important APIs/types/functions: build groups include `ap-objs`, `zcrypt-objs`, `pkey-objs`, `pkey-cca-objs`, `pkey-ep11-objs`, `pkey-pckmo-objs`, `pkey-uv-objs`, and `vfio_ap-objs`. The controlling symbols are `CONFIG_AP`, `CONFIG_ZCRYPT`, `CONFIG_PKEY`, `CONFIG_PKEY_CCA`, `CONFIG_PKEY_EP11`, `CONFIG_PKEY_PCKMO`, `CONFIG_PKEY_UV`, and `CONFIG_VFIO_AP`.

Control flow: there is no runtime flow, but build dependency order is encoded: zcrypt and adapter drivers depend on `ap.o`; pkey base/API/sysfs build into `pkey.o`; hardware-specific pkey handlers are separate modules/objects that register with the pkey base.

State and persistence: build-time only. Its decisions determine which runtime modules and symbol exports exist.

Dependencies and integration: integrates AP core (`ap_bus.o`, `ap_card.o`, `ap_queue.o`), zcrypt card/queue/message drivers, pkey handlers, and VFIO AP matrix support.

Risks and test signals: risks are missing object membership when adding a handler, broken module autoload names used by `pkey_handler_request_modules()`, and unresolved symbols if AP/zcrypt ordering changes. Test with built-in and modular configurations for AP, ZCRYPT, PKEY, individual pkey handlers, and VFIO_AP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_bus.c -->
## sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_bus.c

Purpose: implements the Adjunct Processor bus core for s390 crypto. It discovers AP cards/queues, exposes bus sysfs policy, schedules queue polling/interrupt processing, manages AP resource reservations, and provides exported services used by zcrypt, pkey, and VFIO AP.

Important APIs/types/functions: exported state includes `ap_domain_index`, `ap_max_msg_size`, `ap_queues`, `ap_perms`, `ap_attr_mutex`, and helpers such as `ap_init_apmsg()`, `ap_release_apmsg()`, `ap_get_qdev()`, `ap_driver_register()`, `ap_bus_force_rescan()`, `ap_parse_mask_str()`, `ap_hex2bitmap()`, `ap_wait_apqn_bindings_complete()`, `ap_owned_by_def_drv()`, `ap_test_config_usage_domain()`, `ap_sb_available()`, and `ap_is_se_guest()`.

Control flow: module init checks AP instruction support, initializes debug, message mempool, permissions, QCI data, bus/root devices, adapter interrupts, scan timer/work, and optional poll thread. Periodic or forced scans refresh QCI, notify drivers, select a default domain, walk adapters, create/remove/update card and queue devices, then emit init-scan and bindings-complete uevents. Queue work is driven by AP adapter interrupts, high-resolution poll timer, or optional poll thread; all call the tasklet, which iterates the queue hash and runs each queue state machine.

State and persistence: persistent global state includes masks, QCI current/old snapshots, scan counters, binding completion, queue hash, timers, tasklet, poll thread, interrupt registration, and root bus device. AP messages may use a preallocated mempool for no-IO allocation paths.

Dependencies and integration: depends on s390 AP instructions, QCI/APFT/QACT facilities, CHSC notifications, airq interrupts, Linux driver core/sysfs, and `ap_card`/`ap_queue` creation helpers.

Risks and test signals: risks are scan/mask races, reservation policy regressions, APQN reference handling, mempool exhaustion, and missed polling after interrupt reset. Test sysfs masks and relative mask parsing, QCI changes, AP hotplug/config changes, default domain selection, bindings completion, interrupt and timer polling modes, and no-memory pkey conversion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_bus.h -->
## sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_bus.h

Purpose: defines the AP bus public/internal contract for card, queue, zcrypt, pkey, and VFIO AP code. It centralizes AP constants, response codes, state-machine enums, device structures, driver callbacks, message format, permissions, and exported helper prototypes.

Important APIs/types/functions: defines `struct ap_driver`, `struct ap_device`, `struct ap_card`, `struct ap_queue`, `struct ap_message`, `struct ap_perms`, AP response constants, AP device types CEX4-CEX8, queue state enums, and exported helpers for driver registration, message allocation, queuing/cancel/flush, queue usability, APQN lookup, mask parsing, binding completion, and uevents.

Control flow: drivers register with `ap_driver_register()` using match ids and optional callbacks. Request users allocate/fill `ap_message`, set `receive`, call `ap_queue_message()`, and receive completion in tasklet context. Bus code invokes queue state-machine events and driver callbacks during scans.

State and persistence: structures reveal the core persistent state: per-card hardware info and counters; per-queue qid, device state, config/checkstop flags, SE bind state, list counts, timeout timer, reply buffer, and state-machine state; global permission bitmaps.

Dependencies and integration: depends on Linux device model/hashtable and s390 AP/ISC definitions. It is shared by `ap_bus.c`, `ap_card.c`, `ap_queue.c`, zcrypt, pkey, and VFIO AP.

Risks and test signals: risks are ABI-like structure expectations across modules, queue receive callbacks running in tasklet context, and endianness of inverted AP masks. Test build coverage across all consumers, queue lifecycle transitions, APQN lookup reference counts, and mask parser behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_card.c -->
## sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_card.c

Purpose: implements AP card device allocation and card-level sysfs attributes. It presents hardware type/function/configuration/counter state for each AP adapter discovered by the bus.

Important APIs/types/functions: `ap_card_create()` allocates and initializes `struct ap_card`. Sysfs attributes include `hwtype`, `raw_hwtype`, `depth`, `ap_functions`, `request_count`, `requestq_count`, `pendingq_count`, `modalias`, `config`, `chkstop`, and `max_msg_size`.

Control flow: bus scan calls `ap_card_create()` with TAPQ hardware info and compatible type, fills device parent/bus/name, and registers the device. Attribute reads aggregate queue counters under `ap_queues_lock` or report cached card hardware info. `config_store()` calls SCLP configure/deconfigure and emits a config uevent.

State and persistence: card state stores raw and compatible AP type, TAPQ hardware info, id, max message size, config/checkstop flags, and total request count. Queue counters remain per queue but are aggregated for card attributes.

Dependencies and integration: uses AP bus structures, global queue hash, SCLP AP configure/deconfigure, Linux device attributes, and AP uevents from `ap_bus.c`.

Risks and test signals: risks include stale config state if SCLP succeeds but later scan disagrees, counter aggregation races, and max message size calculation from hardware ML field. Test sysfs reads, request-count reset, card configure/deconfigure, uevents, and device release after bus removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_debug.h -->
## sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_debug.h

Purpose: provides debug feature levels and convenience macros for AP bus logging through s390 debugfs/debug feature infrastructure.

Important APIs/types/functions: defines `DBF_ERR`, `DBF_WARN`, `DBF_INFO`, `DBF_DEBUG`, helper level selectors `RC2ERR()` and `RC2WARN()`, `AP_DBF_MAX_SPRINTF_ARGS`, and macros `AP_DBF()`, `AP_DBF_ERR()`, `AP_DBF_WARN()`, and `AP_DBF_INFO()`. Declares external `debug_info_t *ap_dbf_info`.

Control flow: AP code calls these macros to log formatted events at a severity level into the `ap` debug feature registered by `ap_bus.c`.

State and persistence: owns no state except the external debug handle declaration. Actual debug buffers are initialized and destroyed in AP bus module lifecycle.

Dependencies and integration: depends on `<asm/debug.h>`. Used by `ap_bus.c` and `ap_queue.c` for scan, state-machine, and error diagnostics.

Risks and test signals: risks are use before debug initialization and format argument count exceeding the registered buffer sizing. Test by enabling AP debug output, exercising scan/error paths, and building with/without AP debug options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_queue.c -->
## sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_queue.c

Purpose: implements AP queue devices, their request/reply state machine, queue sysfs attributes, secure-execution bind/associate controls, and AP instruction send/receive/reset handling.

Important APIs/types/functions: exported functions include `ap_sm_event()`, `ap_sm_event_loop()`, `ap_queue_create()`, `ap_queue_init_reply()`, `ap_queue_message()`, `ap_queue_usable()`, `ap_cancel_message()`, `ap_flush_queue()`, `ap_queue_prepare_remove()`, `ap_queue_remove()`, and `ap_queue_init_state()`. Internal state handlers cover reset, reset wait, IRQ enable wait, read, write, queue full, and SE association wait.

Control flow: messages enter `requestq` through `ap_queue_message()`. The state machine sends with NQAP, moves successful sends to `pendingq`, receives replies with DQAP, matches by PSMID, invokes the message receive callback in tasklet context, and reschedules through `ap_wait()`. Timeouts reset queues. Queue creation initializes lists/timer and optional SE sysfs groups. Remove flushes pending/requested messages, zaps the queue, and returns state to uninitiated.

State and persistence: per queue state includes config/checkstop flags, device state, queue counters, request/pending lists, reply buffer, timeout timer, AP state-machine state, RAPQ F bit, last error response, SE bind state, and association index. Counters persist until reset through sysfs.

Dependencies and integration: uses s390 AP instructions (`nqap`, `dqap`, `rapq`, `zapq`, `aqic`, `bapq`, `aapq`, `tapq`), AP bus polling/interrupt helpers, AP tracepoints, and Linux device/sysfs/timer APIs.

Risks and test signals: risks include callback execution in tasklet context, lost replies after cancellation, queue_count recovery when hardware reports empty, reset races, and SE bind/association state errors. Test normal send/reply, queue full, timeout reset, cancellation, flush on config/checkstop, IRQ enablement, poll-only mode, driver override sysfs, and SE bind/associate transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_api.c -->
## sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_api.c

Purpose: exposes the `/dev/pkey` misc-device ioctl ABI and in-kernel `pkey_key2protkey()` service. It validates user requests, copies key material and APQN lists, delegates crypto operations to registered pkey handlers, and scrubs sensitive buffers.

Important APIs/types/functions: exported `pkey_key2protkey()` and ioctl handlers for `PKEY_GENSECK`, `PKEY_CLR2SECK`, `PKEY_SEC2PROTK`, `PKEY_CLR2PROTK`, `PKEY_FINDCARD`, `PKEY_SKEY2PKEY`, `PKEY_VERIFYKEY`, `PKEY_GENPROTK`, `PKEY_VERIFYPROTK`, `PKEY_KBLOB2PROTK`, `PKEY_GENSECK2`, `PKEY_CLR2SECK2`, `PKEY_VERIFYKEY2`, `PKEY_KBLOB2PROTK2`, `PKEY_APQNS4K`, `PKEY_APQNS4KT`, and `PKEY_KBLOB2PROTK3`.

Control flow: `key2protkey()` first tries a direct key-based handler and then slowpath handlers. `pkey_key2protkey()` additionally requests handler modules on `-ENODEV` and retries. Ioctls copy fixed structures from userspace, optionally copy variable key/APQN arrays, call pkey handler wrapper functions, copy results back, and zero local sensitive structures. The misc device is registered in `pkey_api_init()` and removed in `pkey_api_exit()`.

State and persistence: this file keeps little persistent state beyond the miscdevice. Sensitive key buffers are temporary and freed with `kfree_sensitive()` or wiped with `memzero_explicit()`. Handler registry state lives in `pkey_base.c`.

Dependencies and integration: uses Linux miscdevice, usercopy helpers, pkey UAPI structs, zcrypt CCA token definitions, and pkey handler dispatch wrappers.

Risks and test signals: risks are ABI validation gaps, incorrect buffer length negotiation, missed scrubbing, unbounded APQN counts from user input, and fallback behavior masking handler-specific errors. Test every ioctl success and failure path, small output buffers, NULL optional pointers, unsupported key sizes/types, module autoload retry, and KASAN/usercopy validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_base.c -->
## sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_base.c

Purpose: provides pkey module initialization, debug feature setup, and the RCU-protected protected-key handler registry. It lets independent handlers such as CCA, EP11, PCKMO, and UV plug into common pkey APIs.

Important APIs/types/functions: exports `pkey_dbf_info`, `pkey_handler_register()`, `pkey_handler_unregister()`, `pkey_handler_get_keybased()`, `pkey_handler_get_keytypebased()`, `pkey_handler_put()`, all `pkey_handler_*` invocation wrappers, and `pkey_handler_request_modules()`.

Control flow: handlers register after validation and duplicate checks under a spinlock, then `synchronize_rcu()` publishes the update. Lookup walks the RCU list, pins candidate modules with `try_module_get()`, and returns the first handler supporting a key blob or key subtype. Wrapper functions acquire a handler, call the relevant operation if present, then drop the module reference. Slowpath conversion snapshots up to ten handlers supporting slowpath conversion and tries them until one succeeds. Module init registers the debug feature and pkey misc API; CPU feature matching requires MSA.

State and persistence: persistent state is the global handler list protected by RCU and a write spinlock, plus the debug feature. Module references protect handlers while callbacks execute.

Dependencies and integration: depends on Linux module/RCU/list APIs, s390 debug, pkey API init/exit, and optional handler module names matching the Makefile.

Risks and test signals: risks include handler unregister races, module reference leaks, slowpath ten-handler cap, and missing callbacks returning `-ENODEV`. Test concurrent register/unregister with ioctl activity, handler autoload, duplicate registration, missing optional operations, and module unload after pkey use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_base.h -->
## sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_base.h

Purpose: defines shared pkey constants, token layouts, key-size helpers, handler interface, and handler dispatch prototypes used by pkey API and hardware-specific handlers.

Important APIs/types/functions: constants include `KEYBLOBBUFSIZE`, `MINKEYBLOBBUFSIZE`, `PROTKEYBLOBBUFSIZE`, `MAXAPQNSINLIST`, and `AES_WK_VP_SIZE`. Token views include `struct protkeytoken`, `struct protaeskeytoken`, and `struct clearkeytoken`. Helper functions map AES key types/sizes. `struct pkey_handler` defines callbacks for support checks, conversion, generation, clear-to-key, verification, and APQN discovery.

Control flow: API code calls dispatch wrappers declared here; handlers implement the callback table and register/unregister with `pkey_handler_register()` and `pkey_handler_unregister()`. Support-check callbacks must be non-sleeping because they run under RCU read lock.

State and persistence: no storage is owned here except external debug declarations. The handler structure embeds a list node used by the base registry.

Dependencies and integration: includes s390 pkey UAPI and debug definitions. Shared by pkey base, pkey API, and pkey handler modules such as CCA.

Risks and test signals: risks are mismatched token layout packing, callback sleep violations under RCU, and inconsistent keytype/size mapping. Test compile coverage for all handlers, verify packed token sizes against UAPI expectations, and exercise AES/ECC/HMAC size helper mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_cca.c -->
## sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_cca.c

Purpose: implements the CCA protected-key handler. It recognizes CCA AES data, CCA AES cipher, and CCA ECC private key blobs; finds suitable APQNs; generates or imports CCA secure keys; converts CCA keys to protected keys; and verifies CCA key metadata.

Important APIs/types/functions: handler callbacks are `is_cca_key()`, `is_cca_keytype()`, `cca_apqns4key()`, `cca_apqns4type()`, `cca_key2protkey()`, `cca_gen_key()`, `cca_clr2key()`, `cca_verifykey()`, and `cca_slowpath_key2protkey()`. It registers `cca_handler` with the pkey base. When modular, AP device ids cover CEX4 through CEX8.

Control flow: APQN discovery extracts MKVPs from token formats and calls `cca_findcard2()` with appropriate minimum hardware type and master-key set. Key conversion validates token structure, waits for zcrypt operational state, discovers APQNs if wildcard/none were supplied, and tries candidate APQNs until CCA conversion succeeds. Key generation and clear-to-key validate type/subtype/size, discover APQNs if needed, then call CCA zcrypt helpers. Slowpath protected-key conversion builds a CCA data secure key from a clear-key token and converts that secure key to a protected key, retrying once.

State and persistence: only the static handler table persists. Sensitive intermediate secure keys in slowpath are stack-local and short-lived. APQN lists are bounded by `MAXAPQNSINLIST`.

Dependencies and integration: depends on zcrypt CCA misc helpers, AP device types, pkey base registry, pkey token definitions, and module CPU feature infrastructure indirectly through pkey base.

Risks and test signals: risks include token length/version validation, wildcard APQN semantics, current versus alternate MKVP matching, min hardware type selection, and clear-key slowpath policy (`PKEY_XFLAG_NOCLEARKEY`). Test CCA AES data/cipher/ECC verification, current/alternate MKVP APQN discovery, explicit and wildcard APQNs, CEX generation by subtype, no-memory flags, and malformed token rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_cca.c -->
