# subset-b-003916 research

Grouped research for the Broadcom NetXtreme-E RoCE driver core, fast-path queue library, RCFW command channel, and qplib resource manager under `sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/main.c

## Purpose
`main.c` is the top-level Linux RDMA driver glue for Broadcom NetXtreme-E RoCE. It binds as a `bnxt_en` auxiliary driver, negotiates capabilities with the Ethernet function through HWRM and ULP callbacks, creates the qplib firmware/control channel, allocates interrupt and queue resources, registers an `ib_device`, and tears everything down on remove, recovery suspend, resume, or shutdown.

## Important APIs, types, and functions
The file centers on `struct bnxt_re_dev`, `struct bnxt_re_en_dev_info`, `struct bnxt_ulp_ops`, `struct auxiliary_driver`, and the static `ib_device_ops` tables. Setup helpers include `bnxt_re_setup_chip_ctx()`, `bnxt_re_set_drv_mode()`, `bnxt_re_set_db_offset()`, `bnxt_re_dev_init()`, `bnxt_re_alloc_res()`, `bnxt_re_init_res()`, and `bnxt_re_register_ib()`. HWRM helpers allocate/configure VNICs, rings, stats contexts, firmware version, function config, function caps, and doorbell pacing config. Runtime and recovery hooks are `bnxt_re_stop_irq()`, `bnxt_re_start_irq()`, `bnxt_re_suspend()`, `bnxt_re_resume()`, and `bnxt_re_remove_device()`. Async handlers translate CREQ/QP/CQ errors into IB events and update QP1 ToS/DSCP after DCB changes.

## Control flow
Module init registers debugfs and the auxiliary driver. Probe allocates `bnxt_re_en_dev_info`, creates `bnxt_re_dev`, registers with the Ethernet driver, validates MSI-X count, builds chip context, maps the doorbell BAR, allocates RCFW CMDQ/CREQ, allocates a CREQ firmware ring, enables RCFW interrupts, optionally initializes DBR pacing, queries device attributes and firmware version, allocates qplib resources, allocates NQs and their firmware rings, initializes NQs, configures VF resource limits for PFs, creates debugfs/DCB workqueue registration, reads VPD for PFs, and finally registers the RDMA device. Remove and suspend reverse the same layers through flag-guarded cleanup so partially initialized devices can unwind.

## State and persistence
Driver state is in RAM: `rdev->flags`, `chip_ctx`, `qplib_res`, `qplib_ctx`, `rcfw`, NQ ring state, stats DMA contexts, DCB workqueue, pacing page, CQ/SRQ hashes, QP list, and board VPD cache. Persistent device state is only what firmware owns after HWRM/RCFW commands: rings, stats contexts, context tables, pacing config, resource limits, VNIC state, and RoCE CC state. Pacing also exposes a shared page to user processes through `qplib_res.pacing_data`.

## Dependencies and integration points
The file integrates the RDMA core, auxiliary bus, PCI, `bnxt_en` ULP API, HWRM firmware mailbox, qplib resource/slow/fast-path modules, netdevice carrier state, DCB async events, debugfs, rdma restrack, VPD, and Linux PM/recovery callbacks. Most IB verbs are implemented in `ib_verbs.c` but registered here via `bnxt_re_dev_ops`.

## Risks
Initialization has many cross-driver resources, so failure ordering is critical. The source snapshot contains duplicated `if (BNXT_EN_VF(...))` in `bnxt_re_get_sriov_func_type()`, which may indicate merge damage. `bnxt_re_dev_init()` calls `bnxt_re_dev_uninit()` on broad failure paths after some labels have already freed pieces, so flag state must remain accurate. DBR pacing reads MMIO and uses workqueue/timer locking; missed cancellation can race teardown. Async QP/CQ error translation dereferences handles supplied by firmware and depends on qplib hash/table correctness. Suspend assumes `en_info->rdev` is valid before locking. `bnxt_re_shutdown()` does not clear `en_info->rdev`.

## Test signals
Build with `CONFIG_INFINIBAND_BNXT_RE`, auxiliary bus, PCI, and bnxt_en. Exercise probe/remove, insufficient MSI-X, HWRM query failures, RCFW channel failure, NQ ring failure, DBR pacing unsupported/failure paths, PF and VF resource limits, DCB config change, firmware fatal suspend, recovery resume, RDMA registration, restrack raw context reads, and carrier-up/down initial port event selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_fp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_fp.c

## Purpose
`qplib_fp.c` implements the qplib fast path for notification queues, shared receive queues, queue pairs, completion queues, posting send/receive work requests, processing CQEs, and fabricating flush completions when QPs enter error. It is the main bridge between RDMA verbs objects created by `ib_verbs.c`, firmware RCFW commands, hardware queue memory, doorbells, and completion delivery.

## Important APIs, types, and functions
Public entry points include `bnxt_qplib_alloc_nq()`, `bnxt_qplib_enable_nq()`, `bnxt_qplib_create_srq()`, `bnxt_qplib_post_srq_recv()`, `bnxt_qplib_create_qp1()`, `bnxt_qplib_create_qp()`, `bnxt_qplib_modify_qp()`, `bnxt_qplib_query_qp()`, `bnxt_qplib_destroy_qp()`, `bnxt_qplib_post_send()`, `bnxt_qplib_post_recv()`, `bnxt_qplib_create_cq()`, `bnxt_qplib_resize_cq()`, `bnxt_qplib_destroy_cq()`, `bnxt_qplib_poll_cq()`, and `bnxt_qplib_req_notify_cq()`. Important internal helpers manage QP1 header DMA buffers, PSN/MSN search entries, variable WQE slot accounting, CQ/NQ tasklets, flush lists, SRQ free lists, and the WA9060 phantom/fence workaround.

## Control flow
NQs are allocated as qplib HWQs, mapped to BAR doorbells, armed, and serviced by MSI-X IRQs that schedule tasklets. NQ tasklets decode CQ notification and SRQ event entries, rearm device queues, update user toggle pages, and call upper callbacks. QP/CQ/SRQ creation allocates queue memory, sends RCFW create commands, stores firmware IDs, initializes doorbell metadata, and sets up software queue rings. Post-send/post-recv validate state and space, fill WQE headers and SGEs or inline payload, update PSNs/search tables, advance software and hardware producers, and leave actual doorbell ringing to the caller-specific DB helpers. CQ polling validates CQE toggles, decodes request/response/terminal/cutoff formats, advances queue consumers, marks error QPs, and rings CQ consumer doorbells.

## State and persistence
Fast-path state lives in `bnxt_qplib_qp`, `bnxt_qplib_q`, `bnxt_qplib_swq`, `bnxt_qplib_cq`, `bnxt_qplib_srq`, and `bnxt_qplib_nq`. The driver tracks producer/consumer indices, toggle bits, flush-list membership, PSN/MSN metadata, per-WR IDs, DMA header buffers, CQ arm state, and NQ workqueues. Firmware persists QP/CQ/SRQ/NQ object IDs and queue context. User queue memory is represented by umem-backed HWQs; kernel queues are coherent DMA pages.

## Dependencies and integration points
The file depends on `roce_hsi.h` hardware descriptors, qplib resource allocation, RCFW send-message commands, qplib doorbell helpers from resource headers, Linux IRQ/tasklet/workqueue APIs, RDMA MAD/QP1 handling, and upper bnxt_re wrappers for CQ/SRQ/QP container conversion. It is called heavily from `ib_verbs.c`.

## Risks
This code is concurrency-sensitive. Flush lists require CQ flush locks and upper CQ locks to avoid races with poll and async QP errors. `bnxt_qplib_process_flush_list()` uses `list_for_each_entry()` while flush helpers can empty queues but do not remove QPs from lists, so repeated polling depends on flushed flags and external cleanup. Posting to an ERR QP schedules CQ work using `GFP_ATOMIC`; allocation failure changes error reporting. Variable WQE error recovery searches `swq` by slot and can skip completions if firmware reports unexpected slot indices. The source snapshot has duplicated `single` and duplicated `srqn_handler_t` lines in the header. Several CQ paths trust firmware-provided handles and indices before validating all bounds.

## Test signals
Cover kernel and user QP create/destroy, QP1 header buffers, SRQ post/release, static and variable WQE modes, inline send length limits, RDMA read/write, atomics, fast-reg MR, bind MW, zero-SGE receive, CQ resize cutoff completion, CQ arm/rearm, NQ IRQ restart, QP error async flush, terminal CQEs, SRQ events, and firmware malformed CQE indices. KASAN/KCSAN/lockdep are useful because most defects would be lifetime or locking issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_fp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_fp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_fp.h

## Purpose
`qplib_fp.h` declares the fast-path data model and exported APIs for bnxt_re queue objects. It describes software work requests, scatter-gather elements, QP/CQ/SRQ/NQ state, completion records, queue sizing helpers, CQ/NQ valid-bit tests, and the public functions implemented by `qplib_fp.c`.

## Important APIs, types, and functions
Key types are `bnxt_qplib_srq`, `bnxt_qplib_sge`, `bnxt_qplib_swq`, `bnxt_qplib_swqe`, `bnxt_qplib_q`, `bnxt_qplib_qp`, `bnxt_qplib_cqe`, `bnxt_qplib_cq`, `bnxt_qplib_nq_db`, `bnxt_qplib_nq`, and `bnxt_qplib_nq_work`. It defines work request type constants for send, send with immediate, RDMA write/read, atomics, local invalidate, fast-reg MR, bind MW, receive, and receive with immediate. It exposes helpers such as `bnxt_qplib_queue_full()`, `bnxt_qplib_get_swqe()`, `bnxt_qplib_get_depth()`, `bnxt_qplib_set_sq_size()`, `bnxt_qplib_calc_ilsize()`, `bnxt_re_update_msn_tbl()`, `__is_var_wqe()`, and `__is_err_cqe_for_var_wqe()`.

## Control flow
The header defines contracts used across verbs and qplib. Callers allocate and fill `bnxt_qplib_swqe`, then invoke post helpers. Create helpers consume the queue sizing fields in `bnxt_qplib_qp`, `bnxt_qplib_cq`, or `bnxt_qplib_srq`. Completion polling returns normalized `bnxt_qplib_cqe` records. Inline helpers compute queue depth in slots, translate hardware queue-full deltas, and maintain the software queue circular index.

## State and persistence
All structures are in-memory driver state, but many fields mirror firmware state: QP IDs, CQ IDs, SRQ IDs, DPI values, access flags, PSNs, MTU, retry counters, destination addressing, VLAN, SGID index, and queue doorbell state. HWQ members point to DMA or user memory backing real hardware queues. Toggle bits and valid-bit macros persist only as producer/consumer interpretation state.

## Dependencies and integration points
The header depends on `rdma/bnxt_re-abi.h` and hardware descriptor definitions from included C files. It is included by `main.c`, `ib_verbs.c`, `hw_counters.c`, `qplib_fp.c`, `qplib_rcfw.c`, and slow-path code. Its API is the boundary between RDMA core wrappers and low-level queue programming.

## Risks
Because this header defines packed hardware-facing layouts and queue math, small field or macro mistakes affect the entire fast path. The snapshot contains duplicated members (`single`) and a duplicated `typedef` line for `srqn_handler_t`, which would be compile-break risks if present in the active tree. `bnxt_qplib_queue_full()` deliberately allows false-full behavior, so callers must retry correctly. Slot/depth calculations differ between static and variable WQE modes and need bounds tests. Constants such as `BNXT_QPLIB_SWQE_MAX_INLINE_LENGTH` must stay consistent with firmware.

## Test signals
Compile coverage should catch duplicate declarations and type mismatches. Runtime tests should validate queue depth and slot calculations for static and variable WQEs, inline length clipping, RQ max-slot calculation, CQ/NQ valid-bit toggling, QP state/query mapping, SRQ free-list behavior, CQ coalescing limits, QP1 header sizes, and user/kernel DPI interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_fp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_rcfw.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_rcfw.c

## Purpose
`qplib_rcfw.c` implements the RDMA controller firmware communication channel. It allocates and maps CMDQ/CREQ rings, posts firmware commands into 16-byte command slots, waits for or polls completions, dispatches async function and QP events, initializes/deinitializes firmware, and manages CREQ interrupts.

## Important APIs, types, and functions
The main public APIs are `bnxt_qplib_alloc_rcfw_channel()`, `bnxt_qplib_enable_rcfw_channel()`, `bnxt_qplib_rcfw_send_message()`, `bnxt_qplib_init_rcfw()`, `bnxt_qplib_deinit_rcfw()`, `bnxt_qplib_rcfw_start_irq()`, `bnxt_qplib_rcfw_stop_irq()`, `bnxt_qplib_disable_rcfw_channel()`, and `bnxt_qplib_free_rcfw_channel()`. Internal helpers cover return-code mapping during device detach, firmware-stall detection, sleep wait, busy blocking wait, polling wait, command posting, no-wait cleanup commands, CREQ processing, and QP-event table lookup.

## Control flow
Channel allocation creates CREQ and CMDQ HWQs plus the shadow response table. Enabling maps the CMDQ mailbox on BAR0, maps the CREQ consumer doorbell on BAR2, installs the CREQ MSI-X handler, initializes the nonblocking command semaphore, and writes the firmware channel init structure. A caller prepares a command and response buffer, then `bnxt_qplib_rcfw_send_message()` throttles nonblocking commands, validates firmware state, copies request bytes into CMDQ slots, stamps a cookie, rings mailbox registers, and waits through blocking, interrupt-driven wait, or polling mode. CREQ tasklets validate completions, copy responses to waiter buffers, advance CMDQ consumers, wake waiters, dispatch async QP/function events, and ring the CREQ consumer doorbell.

## State and persistence
`struct bnxt_qplib_rcfw` stores the PCI device, resource pointer, CMDQ/CREQ contexts, command response table, QP lookup table, timeout/stall flags, inflight semaphore, interrupt-enabled counter, last firmware-seen timestamp, and feature flags such as RoCE mirror. Firmware initialization writes context table addresses and flags to hardware and persists until deinitialize or device reset.

## Dependencies and integration points
The file depends on qplib resource HWQ allocation, `roce_hsi.h` command/CREQ layouts, qplib fast-path QP error marking, qplib slow-path command users, Linux IRQ/tasklet/waitqueue/semaphore APIs, PCI BAR mapping, and the AEQ callback supplied by `main.c`.

## Risks
Timeout handling is subtle: `-ENODEV` firmware stall is collapsed to `-ETIMEDOUT` for callers while also setting `FIRMWARE_STALL_DETECTED`. `bnxt_qplib_map_rc()` intentionally returns success for destroy-like commands during device detach, which can hide real cleanup failures outside recovery. Late successful `CREATE_AH` completions are followed by no-wait `DESTROY_AH`; a failed destroy can leak firmware AH state. `bnxt_qplib_map_creq_db()` logs missing BAR base but does not immediately return before computing `bar_reg`. Command response table entries rely on cookie reuse only after completions advance. CREQ QP events trust qp table hashing and firmware QP IDs.

## Test signals
Test command send before and after firmware initialization, nonblocking semaphore throttling, CMDQ full, interrupt-enabled wait, polling wait with interrupts disabled, blocking wait, firmware detach, firmware stall, late waiter death for create AH, CREQ IRQ restart, async QP error dispatch, function event dispatch, initialize/deinitialize flags, and BAR mapping failures. Fault injection around wait timeouts and response status is especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_rcfw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_rcfw.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_rcfw.h

## Purpose
`qplib_rcfw.h` declares the firmware command channel ABI used by qplib slow and fast paths. It defines CMDQ and CREQ slot sizes, BAR offsets, command-slot accounting helpers, cookie flags, firmware state flags, command/response shadow entries, side buffers, QP lookup nodes, RCFW context structures, and the exported RCFW management API.

## Important APIs, types, and functions
Important structures are `bnxt_qplib_cmdqe`, `bnxt_qplib_crsbe`, `bnxt_qplib_crsqe`, `bnxt_qplib_rcfw_sbuf`, `bnxt_qplib_qp_node`, `bnxt_qplib_cmdq_mbox`, `bnxt_qplib_cmdq_ctx`, `bnxt_qplib_creq_db`, `bnxt_qplib_creq_stat`, `bnxt_qplib_creq_ctx`, `bnxt_qplib_rcfw`, and `bnxt_qplib_cmdqmsg`. Inline helpers prepare command headers, compute CMDQ pages, get and set command slots, fill `cmdqmsg`, and map QP ID to the lookup table index. It declares channel allocation, enable, IRQ, send-message, init/deinit, side-buffer, and QP-error APIs.

## Control flow
Callers build a firmware request, call `bnxt_qplib_rcfw_cmd_prep()`, wrap buffers with `bnxt_qplib_fill_cmdqmsg()`, and submit through `bnxt_qplib_rcfw_send_message()`. The implementation uses `bnxt_qplib_cmdqmsg` fields to copy request bytes to CMDQ slots, direct side-buffer DMA responses, and copy CREQ command status back to the supplied response object. QP async events use `map_qp_id_to_tbl_indx()` to locate qplib QP handles.

## State and persistence
The header describes volatile in-memory channel state: command queue producer/consumer, waitqueue, firmware flags, `last_seen`, CREQ ring state, per-cookie response records, QP table, and inflight command throttle. BAR offsets and command constants are hardware ABI values and must match firmware. `HWRM_VERSION_*` constants gate features used by other files.

## Dependencies and integration points
It includes `qplib_tlv.h` for TLV command sizing and depends on `roce_hsi.h` command structures through including C files. It is consumed by main initialization, qplib fast path, qplib slow path, resource manager, and hardware counters.

## Risks
Cookie and table sizing are central correctness points: `RCFW_MAX_COOKIE_VALUE` assumes CMDQ depth and response table size remain aligned. `map_qp_id_to_tbl_indx()` reserves the last table slot for QP1 and hashes all other QPs by modulo `qp_tbl_size - 2`; collisions are possible unless firmware/user allocation guarantees are compatible with this simple mapping. Slot helpers mutate `cmd_size`, so they must be called in the expected order. Firmware flags are bit positions in an `unsigned long`; misuse can wedge all commands.

## Test signals
Compile tests should include TLV and non-TLV command users. Unit-style checks can validate command slot counts, page-size calculations, cookie masking, QP1 table index mapping, side-buffer size rounding, and initialization flags. Integration tests should pair this header with `qplib_rcfw.c` timeout, interrupt, and firmware-init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_rcfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_res.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_res.c

## Purpose
`qplib_res.c` is the qplib resource manager. It allocates/free page-buffer-list backed hardware queues, firmware context tables, TQM rings, SGID/PD/DPI tables, stats DMA blocks, and doorbell BAR mappings used by the rest of the bnxt_re driver.

## Important APIs, types, and functions
Core allocation APIs are `bnxt_qplib_alloc_init_hwq()`, `bnxt_qplib_free_hwq()`, `bnxt_qplib_alloc_hwctx()`, `bnxt_qplib_free_hwctx()`, `bnxt_qplib_alloc_pd()`, `bnxt_qplib_dealloc_pd()`, `bnxt_qplib_alloc_dpi()`, `bnxt_qplib_dealloc_dpi()`, `bnxt_qplib_alloc_uc_dpi()`, `bnxt_qplib_free_uc_dpi()`, `bnxt_qplib_alloc_stats_ctx()`, `bnxt_qplib_free_stats_ctx()`, `bnxt_qplib_alloc_res()`, `bnxt_qplib_free_res()`, `bnxt_qplib_init_res()`, `bnxt_qplib_cleanup_res()`, `bnxt_qplib_map_db_bar()`, `bnxt_qplib_unmap_db_bar()`, and `bnxt_qplib_determine_atomics()`. Internal helpers allocate/free PBL levels, map TQM page tables, and initialize/cleanup SGID, PD, and DPI bitmaps.

## Control flow
`bnxt_qplib_alloc_init_hwq()` rounds depth/stride, determines kernel versus user memory, allocates direct or one/two-level PBL/PDE structures, fills valid/last/next-to-last PTE flags, initializes producer/consumer indices, and exposes direct page pointers for queue access. Context allocation builds QPC, MRW, SRQ, CQ, TQM, and TIM memory before RCFW firmware init consumes their addresses. Resource allocation creates the QP table, SGID table, PD bitmap, and DPI bitmap. DPI allocation reserves a page, maps UC/WC doorbell space for user or kernel use, and records the application owner. Cleanup unwinds these resources and clears SGID firmware state.

## State and persistence
State is mostly RAM and DMA memory owned by `bnxt_qplib_res`, `bnxt_qplib_hwq`, `bnxt_qplib_ctx`, SGID/PD/DPI tables, and stats contexts. Hardware-visible persistence consists of DMA page tables, context tables, stats DMA addresses, and BAR mappings while the device is active. PD and DPI allocation state is a bitmap protected by mutexes. SGID table entries mirror firmware SGID registrations and are reset on cleanup.

## Dependencies and integration points
The resource manager uses PCI DMA APIs, vmalloc, RDMA umem iteration, netdevice SGID context, qplib slow-path SGID delete helpers, RCFW constants, and PCIe atomic capability APIs. It feeds `main.c` setup, `qplib_rcfw.c` CMDQ/CREQ allocation, `qplib_fp.c` queue allocation, and `ib_verbs.c` PD/DPI/user queue flows.

## Risks
PBL allocation is complex and easy to regress around edge page counts, `nopte`, user umem, and PTE flag placement. `bnxt_qplib_alloc_pd_tbl()` and DPI bitmap sizing use `max >> 3`, which underallocates if `max` is not divisible by 8. `bnxt_qplib_dealloc_dpi()` skips `pci_iounmap()` when `dpi->dpi` is zero, which is also a valid first DPI for non-kernel allocations. `bnxt_qplib_alloc_dpi()` does not check `ioremap()` failure before returning success for WC/UC user mappings. Doorbell BAR mapping validates only UC length. Cleanup depends on `res->rcfw` being non-null when freeing QP tables.

## Test signals
Test HWQ allocation at page-count boundaries for level 0/1/2, user umem versus kernel pages, `nopte`, queue PTE last flags, context allocation failure unwind, SGID cleanup, PD/DPI bitmap exhaustion, DPI zero allocation, ioremap failure injection, DB BAR length validation, stats DMA allocation, atomic capability detection, and repeated alloc/free under KASAN and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_res.c -->
