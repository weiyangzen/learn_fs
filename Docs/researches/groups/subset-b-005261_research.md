# Research: subset-b-005261 fnic driver files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_debugfs.c

Purpose: this file owns the debugfs surface for the Cisco fnic FCoE HBA driver. It creates `/sys/kernel/debug/fnic`, the global trace controls and trace dumps, and per-host statistics directories under `fnic/statistics/hostN`. The code does not implement the trace rings or stat formatting itself; it bridges debugfs file operations to helpers such as `fnic_get_trace_data`, `fnic_fc_trace_get_data`, `fnic_get_stats_data`, and `fnic_get_debug_info`.

Important APIs and functions: `fnic_debugfs_init()` creates the root and `statistics` directories and allocates a small `fc_trace_flag_type` selector object used as `inode->i_private` for multiple files. `fnic_trace_debugfs_init()` exposes `tracing_enable` and `trace`; `fnic_fc_trace_debugfs_init()` exposes `fc_trace_enable`, `fc_trace_clear`, `fc_trace_rdata`, and `fc_trace`. `fnic_stats_debugfs_init()` creates per-host `stats` and `reset_stats` files. The control file operations are `fnic_trace_ctrl_read/write`; trace data uses `fnic_trace_debugfs_open/read/lseek/release`; statistics use `fnic_stats_debugfs_open/read/release`; and reset control uses `fnic_reset_stats_open/read/write/release`.

Control flow: module initialization in `fnic_main.c` calls the global debugfs init before trace-buffer initialization. Later probe calls `fnic_stats_debugfs_init(fnic)` after the SCSI host is registered. On open, trace/stat files snapshot the current in-memory state into a vmalloc buffer and later serve reads from that fixed buffer, so read operations do not hold driver locks for the whole user read. Writes to trace-control files parse an integer and directly set global trace enable/clear variables. Writing a nonzero `reset_stats` zeroes most cumulative stats and updates `last_reset_time`.

State and persistence: debugfs dentries are kept in static globals for root/trace files and in `struct fnic` for per-host stats. State is volatile kernel memory only. `reset_stats_write()` intentionally preserves the first `u64` of `io_path_stats` and `fw_stats` by zeroing from `+1`, and sets `io_cmpl_skip` to active I/O count to avoid stat skew after reset.

Dependencies and integration: this file depends on Linux debugfs, vmalloc, user-copy helpers, and fnic tracing/stat declarations from `fnic.h`/`fnic_stats.h`. It integrates with probe/remove and module load/unload paths in `fnic_main.c`, plus stats updated by ISR, FCS, and SCSI paths.

Risks: debugfs creation return values are mostly not validated, so partial debugfs setups are possible. `fc_trc_flag` must outlive all files that use its member addresses as private data; teardown order removes files before freeing it, which is important. Stats reset uses raw `memset` over structs containing atomics; this is common in driver stats but depends on no concurrent reader requiring exact atomic consistency. Test signals include mounting debugfs, checking expected files, reading trace/stat files before and after I/O, writing trace enables, writing `reset_stats=1`, and verifying remove/module-unload leaves no stale debugfs entries or use-after-free warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_fcs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_fcs.c

Purpose: this file handles the FCoE/FIP control-plane side of fnic: link-state transitions, receive-frame import from the raw receive queue, transmit of FC/FIP frames on the raw work queue, target-port registration with the FC transport, and firmware reset transitions between Ethernet and FC modes. It connects the lower vNIC queue engine to FDLS fabric discovery and to the SCSI transport's `fc_rport` model.

Important APIs and functions: `fnic_fdls_init()` initializes the iport and FDLS lists; `fnic_fdls_link_status_change()` drives link-up/link-down fabric discovery; `fnic_handle_link()` serializes link events and reset-in-progress coordination; `fnic_handle_frame()` and `fnic_handle_fip_frame()` drain queued received frames into FDLS/FIP handlers; `fnic_rq_cmpl_handler()` services RQ completion queues; `fnic_alloc_rq_frame()` and `fnic_free_rq_buf()` manage receive DMA buffers. Transmit APIs include `fnic_send_fcoe_frame()`, `fnic_send_fip_frame()`, `fnic_flush_tx()`, and the internal `fnic_send_frame()`. Target-port APIs include `fnic_fdls_add_tport()`, `fnic_fdls_remove_tport()`, `fnic_delete_fcp_tports()`, `fnic_tport_event_handler()`, and `fnic_flush_tport_event_list()`. `fnic_fcpio_reset()` issues firmware reset through the SCSI copy-WQ path.

Control flow: RQ completions decode either FCP or Ethernet CQ descriptors, validate FCS/CRC/error bits, classify FIP vs FCoE frames, allocate a frame-list element, append to `frame_queue` or `fip_frame_queue`, and schedule the ordered workqueue. Link events read vNIC link status/down count, avoid transitional states, mark `reset_in_progress`, call FDLS link down/up handlers, then complete `reset_completion_wait`. Outgoing FDLS frames are wrapped with Ethernet/FCoE headers and either queued on `tx_queue` during mode transitions or DMA-mapped and posted to raw WQ. FLOGI registration changes `fnic->state` to `FNIC_IN_ETH_TRANS_FC_MODE` and delegates the firmware command to `fnic_flogi_reg_handler()`.

State and persistence: key state lives in `fnic->state`, `fnic->link_status`, `link_down_cnt`, `reset_in_progress`, `iport->state`, `iport->fpma/fcfmac`, frame queues, and target-port lists. Persistent external effects are vNIC MAC filters, VLAN setting through `fnic->set_vlan`, and FC transport rports. All state is runtime-only.

Dependencies and integration: this file depends on Linux workqueues, DMA mapping, mempools, SCSI FC transport, vNIC queue/CQ helpers, FIP handlers from `fip.c`, and FDLS discovery functions from `fdls_disc.c`. ISR code invokes its CQ handlers; main probe initializes pools, queues, timers, work items, and calls `fnic_fdls_init()`.

Risks: frame lifetime is split across interrupt, workqueue, and teardown paths, so mempool ownership is sensitive. `fnic_flush_tx()` walks `tx_queue` without taking `fnic_lock`, relying on caller/context serialization. Link/reset coordination can wait up to many 5-second intervals before skipping a link event. Test signals include link up/down and flap testing, FIP VLAN discovery, FLOGI/PLOGI/SCR target discovery, rport add/delete observation, receive error counter increments for bad frames, transmit queue flush across firmware mode transition, and unload under active discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_fcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_fdls.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_fdls.h

Purpose: this header defines the FDLS, FIP, iport, target-port, OXID, and receive-frame contracts used by fnic fabric discovery and login code. It is the state model shared by `fnic_fcs.c`, `fnic_scsi.c`, `fdls_disc.c`, and `fip.c`.

Important types and constants: the top comment describes the intended discovery sequence: VLAN discovery, FCF solicitation/selection, FLOGI, keepalive, name-server PLOGI/SCR/GPN_FT/RFT_ID/RFF_ID/RPN_ID, and per-target PLOGI/PRLI/ADISC/LOGO handling. OXID constants define a 512-entry pool and encode frame type bits into OXIDs. Fabric flags include `FNIC_FDLS_FABRIC_ABORT_ISSUED` and `FNIC_FDLS_FPMA_LEARNT`; target flags include discovery-list, abort, ADISC, retry, busy, terminating, deleted, and SCSI-registered bits. `enum fnic_fdls_state_e`, `enum fdls_tgt_state_e`, and `enum fnic_iport_state_e` describe fabric, target, and local-port state machines.

Core structures: `struct fnic_iport_s` is the local-port root, holding MACs, FCID, WWPN/WWNN, timers, fabric/FIP substate, OXID pools, target lists, service parameters, timeouts, completions, and iport stats. `struct fnic_tport_s` represents a discovered target, with FCID, WWPN/WWNN, retry timer, in-flight I/O counter, max payload/timeouts, rport pointer, and deletion/reset state. `struct rport_dd_data_s` is the FC transport private glue tying `fc_rport` back to fnic iport/tport. `struct fnic_oxid_pool_s` tracks fabric exchange IDs and deferred reclaim work.

Control flow and integration: function declarations expose FDLS initialization, frame receive, link-down, frame allocation, OXID allocation/free, timers, target logout/delete, FIP receive/timers, FCoE/FIP sends, port-ID registration, target lookup, and rport exchange reset. `fnic_fcs.c` uses these declarations to forward frames and rport events, while `fnic_scsi.c` consumes tport state and rport private data before issuing I/O.

State and persistence: all structures are in-memory runtime state attached under `struct fnic`; no on-disk persistence exists. Timers and delayed work implement protocol timeouts and deferred OXID reclaim. The header also defines `FNIC_FRAME_HT_ROOM` and `FNIC_FCOE_FRAME_MAXSZ`, which drive mempool buffer sizing in main/FCS paths.

Risks: this header centralizes concurrency-sensitive state accessed from IRQ, workqueue, timer, SCSI EH, and remove paths. The private `rport_dd_data_s` pointers can briefly lag FC transport rport creation, which `fnic_queuecommand()` compensates for by looking up tports by FCID. Test signals include state transitions through link up/down, FIP-capable and non-FIP login, OXID exhaustion/reclaim, target add/delete events, rport private data consistency, and timer cancellation during unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_fdls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_io.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_io.h

Purpose: this header defines the per-I/O data structures used by the SCSI fast path and error-recovery paths. It describes how Linux SCSI commands are backed by fnic-owned scatter/gather descriptors, DMA addresses, remote-port state, completion waiters, and queue tags.

Important types and constants: `FNIC_DFLT_SG_DESC_CNT` is 32, `FNIC_MAX_SG_DESC_CNT` is 256, and `FNIC_SG_DESC_ALIGN` is 16. `struct host_sg_desc` is the hardware-facing scatter/gather descriptor containing little-endian address and length fields. `struct fnic_dflt_sgl_list` and `struct fnic_sgl_list` are slab/mempool allocation shapes for default and maximum SGL sizes. `enum fnic_sgl_list_type` selects the SGL cache. `enum fnic_ioreq_state` tracks command lifecycle: not initialized, command pending, ABTS pending, ABTS complete, and command complete.

Core structure: `struct fnic_io_req` links a `scsi_cmnd` to driver and firmware state. It records iport/tport pointers, SGL pointer plus original allocation pointer, DMA addresses for SGL and sense buffer, SGL count/type, an `io_completed` bit, remote FC port ID, start time, optional completions for abort and device reset, the blk-mq/fnic tag, and the SCSI command pointer.

Control flow and integration: `fnic_queuecommand()` allocates `fnic_io_req` from a mempool, fills SGL metadata, maps DMA, stores the object in both `fnic_priv(sc)->io_req` and the software copy-WQ tag table, then posts a copy-WQ descriptor. Completion handlers read and clear this object, unmap buffers through `fnic_release_ioreq_buf()`, and free it. Abort and device-reset paths reuse the same object to wait for firmware ITMF completions.

State and persistence: all state is per-command and volatile. The `start_time` supports latency histograms and EH diagnostics. `abts_done` and `dr_done` are stack completion pointers owned by EH callers and must be set/cleared under the copy-WQ lock.

Dependencies: the header depends on SCSI FC FCP definitions and `fnic_fdls.h` for iport/tport types. It is included by resource descriptor helpers, main initialization, FCS, ISR, and SCSI files.

Risks and test signals: risks center on lifetime and locking: stale `io_req` pointers, double completion, DMA unmap after failed mapping, and stack completion pointers surviving timeout paths. Tests should stress high queue depth, large SGL commands above 32 segments, abort races with normal completion, LUN reset with pending commands, host reset/unload with active I/O, and blk-mq tag reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_isr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_isr.c

Purpose: this file selects, requests, frees, and services fnic interrupt modes. It bridges PCI INTx/MSI/MSI-X vectors to queue completion handlers, link notification, and queue error logging.

Important APIs and functions: ISR handlers are split by mode: `fnic_isr_legacy()` decodes the legacy pending-bit array and handles notify, error, dummy, and combined WQ/RQ/copy-WQ events; `fnic_isr_msi()` services all queues through a single vector; `fnic_isr_msix_rq()`, `fnic_isr_msix_wq()`, `fnic_isr_msix_wq_copy()`, and `fnic_isr_msix_err_notify()` handle dedicated MSI-X vectors. `fnic_request_intr()` registers the selected handlers. `fnic_free_intr()` frees requested IRQs. `fnic_set_intr_mode_msix()`, `fnic_set_intr_mode()`, and `fnic_clear_intr_mode()` negotiate PCI vectors and record the chosen vNIC interrupt mode.

Control flow: probe first reads firmware resource counts, then calls `fnic_set_intr_mode()`. The driver prefers MSI-X, falls back to MSI, then INTx. MSI-X attempts enough vectors for RQ, raw WQ, each copy WQ, and one error/notify vector, with a minimum that guarantees at least a copy-WQ vector. It adjusts `rq_count`, `raw_wq_count`, `copy_wq_base`, `wq_copy_count`, `wq_count`, `cq_count`, `intr_count`, and `err_intr_offset` to match allocated vectors. During interrupts, handlers update ISR stats, call the right CQ service routines, and return credits with unmask/timer-reset flags.

State and persistence: interrupt mode and vector metadata are runtime PCI/vNIC state. Per-vector data lives in `fnic->msix[]`; counters such as `last_isr_time`, `isr_count`, and `intx_dummy` live in `fnic_stats.misc_stats`. No persistent state exists.

Dependencies and integration: this file depends on Linux PCI IRQ vector APIs, vNIC interrupt helpers, SCSI/FCS CQ handlers from `fnic_scsi.c` and `fnic_fcs.c`, queue error logging from `fnic_main.c`, and link-event scheduling via `fnic_handle_link_event()`. Resource allocation in `fnic_res.c` uses the selected mode to initialize CQs and interrupt controls.

Risks: MSI-X copy-WQ ISR derives vector index from IRQ number and has a fallback scan; bad vector bookkeeping can service the wrong CQ. Interrupt fallback changes queue counts, so all later resource allocation and blk-mq mapping must follow the adjusted counts. Error/notify sharing in MSI-X means queue errors and link events arrive through one vector. Test signals include boot/probe under MSI-X, MSI-only, and INTx environments; vector allocation shortfall; interrupt affinity mapping; queue completion progress; link event delivery; queue error logging; and clean IRQ free after partial request failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_isr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_main.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_main.c

Purpose: this is the module and PCI lifecycle hub for the fnic driver. It declares module parameters, the SCSI host template, FC transport template, global workqueues/slab caches, probe/remove paths, FC host stats operations, and module init/exit.

Important APIs and functions: `fnic_probe()` performs device allocation, PCI enablement, DMA mask selection, BAR mapping, vNIC registration/open/init, MAC/config fetch, SCSI host allocation, interrupt-mode/resource setup, mempool creation, FIP/timer/work/list setup, queue enablement, IRQ request, FDLS init, SCSI host registration, debugfs stats registration, and global fnic list insertion. `fnic_remove()` reverses this by stopping link events, flushing work, unloading SCSI/FDLS, deleting timers, removing debugfs, cleaning queues, freeing rports/tx/rx queues, unregistering vNIC/PCI resources, and freeing the host/fnic object. `fnic_init_module()` creates debugfs/trace buffers, kmem caches, workqueues, FC transport, optional reset workqueue, and registers the PCI driver. `fnic_cleanup_module()` unregisters and destroys global resources.

Control flow: the probe path is staged with explicit `goto` unwind labels. After vNIC config is clamped by `fnic_get_vnic_config()`, only initiator mode is accepted. Interrupt mode is selected before vNIC resources are allocated because queue/vector counts may be reduced. The SCSI driver setup adjusts `host->can_queue`, `max_lun`, `max_id`, `max_cmd_len`, and `nr_hw_queues`, allocates per-copy-WQ `io_req_table`, calls `scsi_add_host()`, initializes FC host attributes, and creates the I/O request mempool. Module init order matters: debugfs root and trace buffers precede probe, caches and workqueues precede PCI registration.

State and persistence: runtime state includes global `fnic_list`, IDA-assigned `fnic_num`, module parameters (`fnic_log_level`, FDMI support, target binding, completion budget, trace pages, max qdepth, PC-RSCN feature), per-device queues, timers, locks, work items, mempools, FC host attributes, and stats. No disk persistence exists; device identity is derived from PCI and vNIC firmware config.

Dependencies and integration: the file integrates Linux PCI, DMA, SCSI midlayer, FC transport, vNIC device/resource APIs, debugfs/tracing, FDLS/FIP, ISR, SCSI, and resource helper files. It is the main caller of APIs researched in all other files in this subset.

Risks: the probe unwind path is long and order-sensitive. Some debugfs/trace initialization failures are logged but not fatal. `fnic_cleanup()` destroys mempools after queue cleanup and completion draining, so missed outstanding references would surface as use-after-free. Interrupt count changes from fallback must stay consistent with copy-WQ tables and blk-mq queue mapping. Test signals include probe/remove under each interrupt mode, injected failures at every probe stage, module load/unload with active I/O and discovery, SCSI host attributes in sysfs, FC stats reset, queue depth/module parameter behavior, and leak/KASAN/lockdep checks across error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_pci_subsys_devid.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_pci_subsys_devid.c

Purpose: this file maps Cisco PCI subsystem device IDs to human-readable adapter family and model strings. It is used during probe to log the adapter model and populate the FDMI model description stored in `fnic->subsys_desc`.

Important APIs and data: `fnic_pcie_device_table[]` is a static table of `{device, desc, subsystem_device, subsys_desc}` records covering Sereno, Cruz, Bodega, and Beverly generations and many VIC model names. `fnic_get_desc_by_devid(struct pci_dev *pdev, char **desc, char **subsys_desc)` is the only function; it validates the PCI device ID and searches by subsystem device.

Control flow: `fnic_probe()` calls `fnic_get_desc_by_devid()` before enabling the PCI device. The helper rejects non-`PCI_DEVICE_ID_CISCO_VIC_FC` device IDs, walks until the sentinel `{0,}`, compares `pdev->subsystem_device` against table entries, and returns model strings on success or `1` with null outputs on failure.

State and persistence: the mapping is compile-time static state. Probe copies the selected `subsys_desc` into `fnic->subsys_desc` with length clamping for later FDMI reporting. There is no runtime mutation or persistence.

Dependencies and integration: the file includes `fnic.h` for PCI ID constants and `struct fnic_pcie_device`. The output feeds logging and fabric device-management identity rather than queue operation.

Risks: the search ignores table `device` after checking the top-level PCI device, so if multiple Cisco FC device IDs ever share subsystem IDs this helper would need extension. It uses `memcmp()` on little-endian in-memory `unsigned short` subsystem IDs instead of direct comparison; this works for equal host values but is unnecessarily indirect. Unknown models fall back cleanly. Test signals include probing every supported subsystem ID, unknown subsystem ID logging, FDMI model string length clamping, and ensuring newly added IDs are reflected in the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_pci_subsys_devid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_res.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_res.c

Purpose: this file reads vNIC firmware configuration, clamps it to driver-supported ranges, counts firmware-provided resources, allocates/frees vNIC queue/CQ/interrupt objects, and initializes those resources for the selected interrupt mode.

Important APIs and functions: `fnic_get_vnic_config()` fetches `struct vnic_fc_config` fields through `vnic_dev_spec()` and clamps descriptor counts, payload size, FC timeouts, login retries, I/O throttle, link/port-down timeouts, LUNs per target, interrupt timer, and copy-WQ count. `fnic_set_nic_config()` wraps `CMD_NIC_CFG` for NIC features such as VLAN stripping. `fnic_get_res_counts()` reads WQ/RQ/CQ/INTR counts from firmware and seeds raw/copy WQ counts. `fnic_alloc_vnic_resources()` allocates WQ, copy-WQ, RQ, CQ, interrupt resources, initializes their control blocks, performs an initial stats dump, and clears LIF stats. `fnic_free_vnic_resources()` frees those resources.

Control flow: probe calls config fetch, resource count discovery, interrupt-mode selection, then allocation. Allocation creates one raw WQ for FCS frames, copy WQs for SCSI I/O, RQs for received FCS/FIP frames, CQs for each RQ/WQ/copy-WQ, and interrupt controllers. CQ indices are laid out as RQs first, raw WQs next, copy WQs last. Error interrupt setup differs by interrupt mode: INTx/MSI-X enable queue error interrupts, MSI disables them. CQ interrupt offsets are per-CQ for MSI-X and zero otherwise.

State and persistence: the primary state is `fnic->config`, queue count fields, `legacy_pba`, queue rings/control blocks, interrupt controls, and `fnic->stats` backing storage. All state is runtime hardware/driver state. Clamping firmware config is persistent only for this probe instance.

Dependencies and integration: this file uses vNIC core helpers (`vnic_dev`, `vnic_wq`, `vnic_wq_copy`, `vnic_rq`, `vnic_cq`, `vnic_intr`, `vnic_nic`) and descriptor definitions. `fnic_main.c` owns call order; `fnic_isr.c` provides interrupt mode; `fnic_fcs.c` and `fnic_scsi.c` consume the queues.

Risks: queue count and CQ index assumptions must match ISR and completion handlers. Copy-WQ CQs are allocated with three times the copy-WQ descriptor count to cover multiple firmware completion types. On allocation failure, cleanup frees all resource arrays based on current counts, so partially initialized resource helpers must tolerate freeing unallocated entries. Test signals include config clamp validation with boundary firmware values, resource count shortage, each interrupt mode, stats dump failure, queue error interrupt routing, and queue/CQ index consistency under multi-copy-WQ configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_res.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_res.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_res.h

Purpose: this header provides inline descriptor-construction helpers for fnic raw WQ, Ethernet WQ, copy-WQ FCPIO requests, and RQ posts. It is the lowest-level encoding layer between driver control flow and hardware/firmware queue descriptors.

Important APIs: `fnic_queue_wq_desc()` encodes an FCoE raw work-queue descriptor with DMA address, frame length, FC EOF, VLAN insertion, CQ entry, SOP/EOP, and FCoE encapsulation enabled. `fnic_queue_wq_eth_desc()` emits a non-FCoE Ethernet descriptor. `fnic_queue_wq_copy_desc_icmnd_16()` builds an FCP SCSI command request with SGL/sense DMA addresses, CDB, LUN, target D_ID, max burst, and FC timeouts. `fnic_queue_wq_copy_desc_itmf()` builds task management requests for abort, terminate, and LUN reset. `fnic_queue_wq_copy_desc_flogi_reg()` and `fnic_queue_wq_copy_desc_fip_reg()` register FC/FIP login identity with firmware. `fnic_queue_wq_copy_desc_fw_reset()` issues firmware reset. `fnic_queue_wq_copy_desc_lunmap()` describes LUN map buffer requests. `fnic_queue_rq_desc()` posts a receive buffer.

Control flow: higher-level code checks descriptor availability and locks queues before calling these helpers. Each helper obtains the next descriptor, fills protocol-specific fields, and posts the queue entry (`vnic_wq_post`, `vnic_wq_copy_post`, or `vnic_rq_post`). These helpers do not validate arguments, reserve descriptors, or handle DMA mapping; callers must do that first.

State and persistence: descriptor contents become hardware-visible queue state after post. There is no standalone persistent state. Address fields are ORed with `VNIC_PADDR_TARGET`, multi-byte FC IDs use `hton24`, and SCSI CDB/LUN arrays are copied into firmware request formats.

Dependencies and integration: this header depends on descriptor encoders from `wq_enet_desc.h`, `rq_enet_desc.h`, FCPIO definitions, and vNIC queue APIs. It is consumed by FCS transmit, RQ refill, SCSI command queueing, abort/reset paths, FLOGI registration, and firmware reset.

Risks: because helpers are inline and trust callers, errors in CDB length, SGL count, DMA address lifetime, tag composition, or queue locking propagate directly to firmware-visible requests. `fnic_queue_wq_copy_desc_icmnd_16()` copies `cdb_len` bytes into a 16-byte CDB field, relying on host template `max_cmd_len` and caller behavior. Test signals include descriptor field validation via firmware traces, DMA mapping error paths, CDB length boundaries, abort/reset tag encoding, VLAN/FCoE encapsulation on raw WQ frames, and RQ replenishment under pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_res.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_scsi.c

Purpose: this file implements fnic's SCSI command path and error recovery over firmware copy work queues. It maps SCSI commands to FCPIO firmware descriptors, handles firmware completions, tracks per-command state, and implements abort, LUN reset, rport exchange reset, firmware reset completion, and host reset behavior.

Important APIs and functions: exported entry points include `fnic_queuecommand()`, `fnic_wq_copy_cmpl_handler()`, `fnic_fw_reset_handler()`, `fnic_flogi_reg_handler()`, `fnic_abort_cmd()`, `fnic_device_reset()`, `fnic_eh_host_reset_handler()`, `fnic_host_reset()`, `fnic_reset()`, `fnic_issue_fc_host_lip()`, `fnic_terminate_rport_io()`, `fnic_rport_exch_reset()`, `fnic_scsi_unload()`, `fnic_scsi_unload_cleanup()`, `fnic_count_ioreqs()`, `fnic_count_lun_ioreqs()`, and `fnic_is_abts_pending()`. Internal completion handlers decode `FCPIO_ACK`, `FCPIO_ICMND_CMPL`, `FCPIO_ITMF_CMPL`, FLOGI registration completions, and firmware reset completions.

Control flow: `fnic_queuecommand()` validates rport and iport/tport readiness, handles late rport private-data setup, increments in-flight counters, allocates `fnic_io_req`, maps SCSI data and sense/SGL buffers, stores the request in the per-hardware-queue tag table, and posts an `FCPIO_ICMND_16` descriptor. Firmware completions are serviced from copy-WQ CQs by `fnic_wq_copy_cmpl_handler()`, which dispatches by descriptor type. Normal command completion validates tag/hwq, handles abort-pending races, maps FCPIO status to SCSI result, unmaps DMA, updates FC host and fnic stats, calls `scsi_done()`, and frees the request.

Error recovery: abort handling sets `FNIC_IOREQ_ABTS_PENDING`, queues either ABTS or local terminate depending on rport readiness, waits for a firmware ITMF completion, and frees/completes the command on success. LUN reset creates or reuses an I/O request, posts `FCPIO_ITMF_LUN_RESET`, waits up to `FNIC_LUN_RESET_TIMEOUT`, then terminates pending commands on the same LUN. Rport exchange reset iterates busy commands for a port and sends local terminate requests. Host reset simulates a FLOGO/link flap through `fnic_reset()` and waits for fabric readiness when link is up. Firmware reset blocks I/O, waits for in-flight operations, posts `FCPIO_RESET`, cleans outstanding I/O on completion, and transitions state back toward Ethernet/FC mode.

State and persistence: per-command state is stored in `fnic_priv(sc)` and `struct fnic_io_req`; per-queue request tables live in `fnic->sw_copy_wq[hwq].io_req_table`; firmware descriptor acknowledgment state is `fw_ack_recd/fw_ack_index`; broad driver state is `fnic->state`, `state_flags`, `in_flight`, reset counters, and iport/tport in-flight counters. Stats include active/completed I/O, latency buckets, FCP byte counters, abort/terminate/reset outcomes, firmware request counts, and ISR timing correlations. All state is volatile.

Dependencies and integration: this file depends on SCSI midlayer, blk-mq tags, FC transport rports, FDLS tport state, DMA mapping, vNIC copy-WQ/CQ helpers, FCPIO descriptor formats, mempools, completions, and workqueues from main/FCS. It is the main consumer of `fnic_io.h` and `fnic_res.h`.

Risks: this is the highest-risk concurrency surface. Races exist between normal completion, abort, device reset, rport removal, host reset, and unload; correctness relies on copy-WQ locks and careful clearing of `io_req` and tag-table entries. Timeout paths leave cleanup to higher EH levels in some cases. Stack completions (`abts_done`, `dr_done`, `fw_reset_done`) must be nulled after waits. Descriptor availability and firmware ACK handling affect forward progress. Test signals include queuecommand success/failure status mapping, high-depth multi-queue I/O, abort-vs-completion races, rport loss during I/O, LUN reset with pending aborts, host reset under link flap, firmware reset timeout, unload with active I/O, DMA mapping failure injection, and lockdep/KASAN under SCSI EH stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_stats.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_stats.h

Purpose: this header defines the statistics schema exported through debugfs and updated throughout the fnic driver. It groups I/O, abort, terminate, reset, firmware, VLAN, miscellaneous, FC-host, and iport/fabric-discovery counters.

Important types: `struct stats_timestamps` records last reset/read times. `struct io_path_stats` tracks active/max active I/O, completions, failures, null request/scsi cases, allocation failures, not-found events, total I/Os, latency buckets, current max I/O time, and per-hardware-queue I/O counters for up to `FNIC_MQ_MAX_QUEUES` 64 queues. `struct abort_stats`, `terminate_stats`, and `reset_stats` record SCSI EH outcomes and timeout classes. `struct fw_stats` tracks active/max firmware requests and firmware resource/errors. `struct vlan_stats` tracks FIP VLAN discovery outcomes. `struct misc_stats` holds ISR/ACK timing, CQ/ACK anomalies, protocol status counters, frame errors, readiness failures, dummy INTx interrupts, and port speed. `struct fnic_iport_stats` tracks link, RSCN, fabric login/name-server, FDMI, and target login counters. `struct fnic_stats` aggregates most runtime stats plus `fc_host_statistics`.

Control flow and integration: `fnic_main.c` initializes and resets FC-host statistics; `fnic_debugfs.c` formats `struct fnic_stats` through `fnic_get_stats_data()` and zeros most counters on reset; `fnic_isr.c` updates ISR counters; `fnic_fcs.c` updates frame errors and discovery-related stats; `fnic_scsi.c` updates I/O, abort, terminate, firmware, and reset counters. `fnic_iport_stats` is embedded in `struct fnic_iport_s`, not in the top-level `struct fnic_stats` aggregate.

State and persistence: counters are `atomic64_t` where frequently updated across IRQ/workqueue/EH contexts, while timestamps and FC host statistics are regular fields. The stats are volatile and resettable via debugfs; there is no persistence across driver reload.

Dependencies: the header includes SCSI FC transport definitions for `struct fc_host_statistics`. It declares `fnic_get_stats_data()` for debugfs formatting and `fnic_role_to_str()` for role reporting.

Risks: readers may observe non-transactional snapshots across multiple atomic counters. Resetting stats by `memset` can race with concurrent increments and should be treated as best-effort diagnostics rather than strict accounting. Adding new counters requires updating debug formatting and reset logic. Test signals include debugfs stats content under normal I/O, abort/reset workloads, link/fabric discovery, stats reset behavior with active I/O, per-queue counter coverage when copy-WQ count changes, and absence of overflow or formatting truncation in the 2-page debug buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_stats.h -->
