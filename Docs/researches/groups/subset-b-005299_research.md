# subset-b-005299 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli.h

## Purpose
`lpfc_sli.h` is a central private contract for the Emulex/Broadcom LPFC Fibre Channel driver shared by SLI-3 and SLI-4 code. It defines the software wrappers around IOCBs, WQEs, mailbox commands, SLI rings, host-buffer queues, statistics, link counters, and per-I/O buffers that the rest of the LPFC stack uses to submit FC, FCP, NVMe/FC, NVMET, ELS, BSG, and management work to adapter firmware.

## Important APIs, Types, And Functions
Important types include `struct lpfc_iocbq`, `LPFC_MBOXQ_t`, `struct lpfc_sli_ring`, `struct lpfc_sli`, and `struct lpfc_io_buf`. `struct lpfc_iocbq` is the common command/completion envelope; it stores list linkage, I/O/XRI tags, SLI-4 `union lpfc_wqe128`, SLI-3 `IOCB_t`, completion status, timeout, vport, DMA buffers, node pointer, VMID tag, and completion callbacks. `LPFC_MBOXQ_t` wraps SLI-3 mailbox and SLI-4 MQE payloads with vport/node/context buffers, completion callback, extended SGE metadata, and flags such as `LPFC_MBX_WAKE`.

The ring model is represented by `struct lpfc_sli_ring`, `struct lpfc_sli3_ring`, and `struct lpfc_sli4_ring`. It tracks transmit, completion, posted-buffer, IOCB-continuation queues, ring masks for unsolicited receive dispatch, command-available callbacks, statistics, and SLI-version-specific backing state. `struct lpfc_sli` is the HBA-level SLI state: active rings, mailbox queues, active mailbox pointer, mailbox timeout timer, IOCB lookup table, last IOTAG, statistics start time, and link-stat reset offsets. `struct lpfc_io_buf` is the shared fast-path I/O buffer for SCSI and NVMe, containing SGL DMA state, current IOCB, hardware queue pointer, flags, completion status/result, segment counts, node pointer, and protocol-specific command/response fields.

## Control Flow
This header has no standalone executable flow. It shapes runtime flow in implementation files: allocation paths fill `lpfc_iocbq` or `lpfc_io_buf`, issue paths place them on ring or WQ queues, interrupt paths recover them by IOTAG/XRI and dispatch callbacks, and completion paths use the stored protocol context to call SCSI, NVMe, ELS, BSG, or mailbox completion logic. Mailbox flow is similarly dictated by `LPFC_MBOXQ_t`: callers prepare `u.mb` or `u.mqe`, attach buffers and a completion callback, queue the command, and either block on a wait context or complete asynchronously through `mbox_cmpl`.

SLI ring flags (`LPFC_DEFERRED_RING_EVENT`, `LPFC_CALL_RING_AVAILABLE`, `LPFC_STOP_IOCB_EVENT`) gate ring scheduling and completion processing. I/O command flags (`LPFC_IO_FCP`, `LPFC_IO_NVME`, `LPFC_IO_NVMET`, `LPFC_IO_VMID`, `LPFC_EXCHANGE_BUSY`, DIF flags, abort flags, and outstanding flags) are the compact state transitions carried through issue, abort, timeout, and completion paths.

## State And Persistence
All state described here is volatile kernel memory owned by `struct lpfc_hba`, vports, queues, or per-command allocations. Persistent storage is not modified by this header. The primary lifetime boundaries are HBA lifetime for `struct lpfc_sli`, ring lifetime for `struct lpfc_sli_ring`, mailbox-command lifetime for `LPFC_MBOXQ_t`, and command/pool lifetime for `struct lpfc_io_buf`.

Synchronization is implied by fields and comments: ring queues use `ring_lock`, mailbox state is protected by SLI/HBA locks in implementation files, and `lpfc_io_buf.buf_lock` protects simultaneous abort/completion races. The lookup table `iocbq_lookup` persists command identity between issue and completion and is especially sensitive to IOTAG allocation/release ordering.

## Dependencies And Integration Points
The header depends on LPFC hardware definitions from `lpfc_hw.h` and `lpfc_hw4.h`, Linux list, timer, spinlock, waitqueue, DMA, SCSI, NVMe/FC, and debugfs conditional definitions through surrounding includes. Integration points include LPFC SCSI (`lpfc_scsi.c`), ELS/discovery, mailbox, SLI interrupt, NVMe initiator/target, BSG, VMID, debugfs, and fabric scheduler paths.

## Risks And Edge Cases
The same wrapper structures carry multiple protocol interpretations, so stale flags or union members can cause incorrect completion dispatch. IOTAG/XRI lookup correctness is critical because completions arrive asynchronously and abort/timeout paths may race firmware completion. The header also exposes many flag bitmasks with overlapping lifecycle meanings; missing a clear/set operation can leak queue depth, keep an I/O on a completion queue, or lose a deferred free. Debugfs fields are conditionally compiled, so code using timing/error-injection fields must stay guarded.

## Test Signals
Useful signals are clean compile coverage across SLI-3, SLI-4, debugfs, SCSI-only, NVMe, and NVMET configurations; stress I/O with aborts and timeouts; mailbox wait and async completion tests; IOTAG/XRI leak checks; ring full and command-available callback paths; VMID-tagged I/O; DIF insert/strip/pass-through cases; and unload checks proving mailbox, IOCB, ring, and I/O-buffer lists drain to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli4.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli4.h

## Purpose
`lpfc_sli4.h` defines the SLI-4-specific in-memory model and function surface for LPFC adapters. It covers event/completion/work/receive/mailbox queues, FCoE FCF/FIP records, bootstrap mailbox memory, SLI-4 capability and resource limits, CPU/IRQ/hardware-queue mapping, XRI/RPI/VPI/VFI allocation state, per-hardware-queue buffer pools, and prototypes for SLI-4 setup, queue creation, doorbells, asynchronous events, XRI abort handling, and FCF discovery.

## Important APIs, Types, And Functions
Key enums are `enum lpfc_sli4_queue_type`, `enum lpfc_sli4_queue_subtype`, and `enum lpfc_poll_mode`. `struct lpfc_queue` is the queue primitive for EQ, CQ, MQ, WQ, HRQ, and DRQ instances. It stores list linkage, queue IDs, entry geometry, page arrays, host/HBA indexes, notification and processing limits, doorbell registers, polling state, work items, associated queues, RQ buffers, and per-queue counters.

`struct lpfc_sli4_hba` is the main SLI-4 HBA extension. It stores mapped PCI/SLI registers, interface-type-specific status/error registers, doorbell registers, bootstrap mailbox, queue arrays, fast-path hardware queues, slow-path mailbox/ELS/NVMe-LS queues, receive queues, FCF state, link state, resource bitmaps and ID arrays for XRI/RPI/VFI, RPI headers, SGL lists, aborted lists, async work queues, CPU vector maps, IRQ handles, idle stats, trunk/optic state, and feature capability data. `struct lpfc_sli4_hdw_queue` groups a fast-path EQ/CQ/WQ tuple with I/O buffer lists, aborted I/O lists, multi-XRI pools, FC-4 stats, and per-HWQ SGL/command-response pools.

Other important structures include `struct lpfc_fcf`, `struct lpfc_fcf_rec`, `struct lpfc_fcf_conn_rec`, `struct lpfc_bmbx`, `struct lpfc_max_cfg_param`, `struct lpfc_pc_sli4_params`, `struct lpfc_sglq`, `struct lpfc_rpi_hdr`, `struct lpfc_rsrc_blks`, `struct lpfc_rdp_context`, and `struct lpfc_lcb_context`. Important inline helpers are `lpfc_sli4_qe()` for locating a queue entry by index and `lpfc_sli4_unrecoverable_port()` for ERR/RN status interpretation.

## Control Flow
The header describes, but does not execute, the SLI-4 control plane. Probe/setup code calls `lpfc_sli4_hba_setup()`, maps SLI registers, discovers capabilities into `lpfc_pc_sli4_params`, creates queues with `lpfc_eq_create()`, `lpfc_cq_create()`, `lpfc_wq_create()`, `lpfc_rq_create()`, and `lpfc_mq_create()`, then posts SGLs/RPI headers and arms queues. Runtime interrupts consume EQ/CQ entries through `struct lpfc_queue`, write EQ/CQ doorbells through function pointers, and dispatch completions or async events into the HBA work queues. Teardown reverses this with destroy/unset functions and resource-list cleanup.

Resource flow is mostly bitmap/list driven. XRI, RPI, VPI, VFI, FCFI, queue, and SGL resources are described by max/base/used counts, bitmaps, block lists, active lists, and per-HWQ pools. Multi-XRI pools split public and private XRI lists and use heartbeat counters to tune pool balance.

## State And Persistence
The state is volatile driver/HBA state initialized during PCI probe and firmware setup. It mirrors firmware-assigned queue IDs, resource extents, FCF records, link state, and adapter capabilities but does not itself persist data. FCF state persists across runtime rediscovery attempts in memory with flags such as `FCF_AVAILABLE`, `FCF_REGISTERED`, `FCF_IN_USE`, and rediscovery bits. Timers (`redisc_wait`) and delayed work fields persist pending rediscovery or poll work until canceled.

## Dependencies And Integration Points
The header depends on Linux IRQ polling, CPU frequency/affinity, workqueues, timers, per-CPU storage, DMA, PCI MMIO, and LPFC hardware bitfield macros. It is consumed by LPFC SLI-4 setup, interrupt, mailbox, FCoE, discovery, NVMe/FC, NVMET, SCSI fast path, debugfs, and vport code. Doorbell helpers and queue prototypes form the bridge between high-level LPFC operations and firmware queue commands.

## Risks And Edge Cases
Queue geometry must match firmware capabilities; bad entry size/count/page assumptions can corrupt queue memory or doorbell accounting. Hardware queue and CPU vector mapping is sensitive to CPU hotplug, IRQ affinity, and polling mode transitions. Resource counters (`xri_used`, `rpi_used`, `vpi_used`, pool counts) must match bitmap/list state or the driver can leak firmware resources or double-free IDs. FCF rediscovery flags have overlapping pending/event/failover meanings, so failover races can select stale FCF data. The inline `lpfc_sli4_qe()` trusts `q_pgs` and index bounds supplied by callers.

## Test Signals
Validation signals include SLI-4 probe on all supported interface types, queue creation/destruction under varied page sizes and queue counts, MSI-X/IRQ affinity mapping, interrupt and poll-mode completion paths, FCF scan/failover/rediscovery, XRI/RPI/VPI/VFI allocation exhaustion and recovery, SGL repost after reset, async link/FIP/DCBX/FC events, NVMET and NVMe-LS queue setup, and unload with all queue/list/bitmap resources reclaimed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_version.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_version.h

## Purpose
`lpfc_version.h` centralizes LPFC driver identity strings. It defines the public driver version, module/handler names, module description, and copyright string used by the LPFC module, logs, sysfs-style reporting, and other driver metadata.

## Important APIs, Types, And Functions
The file contains only macros. `LPFC_DRIVER_VERSION` is `"15.0.0.0"`, `LPFC_DRIVER_NAME` is `"lpfc"`, and `LPFC_MODULE_DESC` builds the module description with the version. `LPFC_SP_DRIVER_HANDLER_NAME` and `LPFC_FP_DRIVER_HANDLER_NAME` identify SLI-2/3 slow-path and fast-path handler names, while `LPFC_DRIVER_HANDLER_NAME` is the SLI-4 prefix. `LPFC_COPYRIGHT` is a Broadcom copyright string.

## Control Flow
There is no executable control flow. Compilation units include this header and embed these constants into module metadata, log strings, interrupt handler names, or identity output.

## State And Persistence
The macros are compile-time constants. They do not create runtime state or persistent storage. Their values become part of the built kernel module and any strings exposed by that module.

## Dependencies And Integration Points
The file has no includes and no external dependencies. It integrates with `lpfc_vport.c` and other LPFC compilation units that need driver identity. Module build and runtime reporting paths depend on these strings staying consistent with release packaging.

## Risks And Edge Cases
Version skew is the main risk. If this header is updated without matching the broader LPFC source, package metadata, or documentation, diagnostics can report a misleading driver version. Handler-name changes can also affect log filtering or IRQ handler naming expectations.

## Test Signals
Useful signals are compile checks, `modinfo` or built-in module metadata showing the expected description/version, runtime LPFC logs using the expected handler prefix, and packaging/release checks that the source version matches the delivered driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vmid.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vmid.c

## Purpose
`lpfc_vmid.c` manages LPFC VMID lookup, allocation, registration, tagging, accounting, and reinitialization. VMID lets the driver tag I/O with an application ID or priority/CS_CTL value derived from a host VM UUID, then register that mapping with fabric/firmware through VMID commands.

## Important APIs, Types, And Functions
The exported helpers are `lpfc_get_vmid_from_hashtable()`, `lpfc_vmid_hash_fn()`, `lpfc_vmid_get_appid()`, and `lpfc_reinit_vmid()`. `lpfc_get_vmid_from_hashtable()` searches a vport hash bucket for a matching 16-byte `host_vmid`. `lpfc_vmid_hash_fn()` lowercases ASCII letters and computes a bounded hash with `LPFC_VMID_HASH_SHIFT` and `LPFC_VMID_HASH_MASK`. `lpfc_vmid_get_appid()` is the main fast-path call used when an I/O has a UUID; it returns a VMID tag in `union lpfc_vmid_io_tag` or an error indicating retry/busy/resource failure. `lpfc_reinit_vmid()` resets all VMID slots and hash links after events such as FLOGI completion.

Internal helpers include `lpfc_put_vmid_in_hashtable()`, `lpfc_vmid_update_entry()`, and `lpfc_vmid_assign_cs_ctl()`. Update logic fills either `tag->cs_ctl_vmid` for priority-tag mode or `tag->app_id` for application-header mode, increments per-VM read/write counters, and updates a per-CPU last-I/O timestamp.

## Control Flow
On I/O, `lpfc_vmid_get_appid()` first blocks priority-tag I/O if QFPA is required but not complete, setting `WORKER_CHECK_VMID_ISSUE_QFPA` and returning `-EAGAIN`. It hashes the UUID, takes `vmid_lock` for read, and searches the hash table. A registered hit immediately updates the tag and counters. A hit already registering or deregistering returns `-EBUSY` so the I/O is sent without a VMID tag.

On miss, the function upgrades to the write lock, rechecks for races, locates a free slot if `cur_vmid_cnt < max_vmid`, initializes the slot, inserts it into the hash table, optionally assigns a CS_CTL value, allocates per-CPU timestamp storage, and drops the lock before issuing fabric/firmware registration. Priority-tag mode calls `lpfc_vmid_uvem()`, while app-header mode calls `lpfc_vmid_cmd(..., SLI_CTAS_RAPP_IDENT, ...)`. Successful command submission increments `cur_vmid_cnt` and marks `LPFC_VMID_REQ_REGISTER`; failure removes the hash entry, frees per-CPU storage, and marks the slot free. The inactive VMID timer is enabled once globally through the physical port flag.

## State And Persistence
VMID state is volatile per-vport memory. The `vport->vmid` array stores slots, `vport->hash_table` indexes active slots, `cur_vmid_cnt` tracks allocated entries, and each entry carries flags, the host UUID, VMID length, read/write counters, union tag value, deletion policy, and per-CPU last-I/O timestamps. There is no on-disk persistence; registration state is recreated after link/login reinitialization.

## Dependencies And Integration Points
This file depends on Linux hash tables, percpu allocation, jiffies, rwlocks, DMA direction enums, and LPFC vport/HBA state. It integrates with LPFC SCSI/NVMe I/O build paths through the returned tag, with fabric registration helpers `lpfc_vmid_uvem()` and `lpfc_vmid_cmd()`, with CS_CTL allocation via `lpfc_vmid_get_cs_ctl()`, and with the HBA inactive VMID timer.

## Risks And Edge Cases
The function uses `strlen(uuid)` but compares 16 bytes in the hash lookup and copies `vmid_len` into `host_vmid`; callers must provide a bounded, NUL-terminated UUID representation consistent with the 16-byte storage. Failed registration frees `last_io_time` but does not clear the pointer in the visible code, creating risk if later paths assume NULL before reuse. Hash insertion happens before registration, so all paths must respect `LPFC_VMID_REQ_REGISTER` and `LPFC_VMID_DE_REGISTER`. Per-CPU timestamp updates use `raw_smp_processor_id()`, so preemption assumptions matter.

## Test Signals
Test signals include repeated UUID hits returning tags without extra registration, simultaneous miss races creating only one entry, max-VMID exhaustion returning `-ENOMEM`, QFPA delay returning `-EAGAIN` and setting worker events, registration failure cleanup, inactivity timer start once, app-header and priority-tag modes, vport reinit clearing hash/counters/timestamps, and read/write counter updates by DMA direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vmid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vport.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vport.c

## Purpose
`lpfc_vport.c` implements LPFC NPIV virtual-port lifecycle management. It creates, enables, disables, deletes, and enumerates LPFC virtual ports requested through the Fibre Channel transport, coordinating VPI allocation, service-parameter reads, WWN validation, fabric FDISC/LOGO/DA_ID sequences, SCSI host registration/removal, sysfs/debugfs attributes, discovery quiesce waits, and reference management.

## Important APIs, Types, And Functions
Public entry points are `lpfc_vport_set_state()`, `lpfc_alloc_vpi()`, `lpfc_vport_create()`, `lpfc_vport_disable()`, `lpfc_vport_delete()`, `lpfc_create_vport_work_array()`, and `lpfc_destroy_vport_work_array()`. Internal helpers include `lpfc_free_vpi()`, `lpfc_vport_sparm()`, `lpfc_valid_wwn_format()`, `lpfc_unique_wwpn()`, `lpfc_discovery_wait()`, `lpfc_send_npiv_logo()`, `disable_vport()`, and `enable_vport()`.

`lpfc_vport_set_state()` mirrors FC transport state into `fc_vport->vport_state` and maps failure-like states to `LPFC_VPORT_FAILED`. `lpfc_alloc_vpi()` and `lpfc_free_vpi()` manage the HBA VPI bitmap, reserving VPI 0 for the physical port and updating SLI-4 `vpi_used`. `lpfc_vport_sparm()` issues a blocking READ_SPARM mailbox and copies service parameters into the vport identities.

## Control Flow
Create flow validates NPIV support (`sli_rev >= 3`, `cfg_enable_npiv`) and rejects creation when NVMe target support is enabled. It allocates a VPI, obtains a driver instance number, creates the port, initializes debugfs, reads service parameters, overlays transport-supplied WWNN/WWPN, validates WWN format and uniqueness, allocates sysfs attributes, configures FCP-only FC4 support, attaches the vport to `fc_vport->dd_data`, sets FDMI flags, and handles SLI-4 VPI initialization. If link/fabric state is not ready or the request is initially disabled, it sets transport state and returns success without FDISC. Otherwise it finds the physical fabric node and issues initial FDISC when fabric NPIV support is advertised.

Disable flow optionally sends NPIV LOGO, stops host I/O, cleans RPI/default-RPI state, stops timers, unregisters VPI, marks SLI-4 vport as needing INIT_VPI, and sets `FC_VPORT_DISABLED`. Enable flow checks link/topology, marks loading, performs deferred INIT_VPI or sets `FC_VPORT_NEEDS_REG_VPI`, then issues FDISC if fabric state permits.

Delete flow rejects physical-port deletion and static-vport deletion except during driver unload. It marks unloading, waits for creation/discovery to settle when not unloading the physical port, takes an early SCSI host reference, removes sysfs/debugfs, optionally issues DA_ID and fabric LOGO, waits for discovery quiesce, removes FC/SCSI hosts, runs LPFC cleanup/host-down/timer stop, unregisters RPIs/VPI or releases the host reference directly, frees the VPI, removes the vport from `port_list`, and drops references.

## State And Persistence
State is volatile per-HBA and per-vport memory. The VPI bitmap persists for the HBA lifetime. Vport state spans FC transport state, `port_state`, `fc_flag`, `load_flag`, `vpi_state`, FDMI masks, sysfs/debugfs attributes, timers, node lists, and discovery counters. There is no disk persistence; static vport policy is represented by runtime flags and transport configuration.

## Dependencies And Integration Points
The file integrates with the SCSI host and FC transport (`fc_vport`, `fc_remove_host()`, `scsi_remove_host()`), LPFC mailbox and SLI helpers, discovery (`lpfc_initial_fdisc()`, `lpfc_set_disctmo()`), name server (`lpfc_ns_cmd()`), ELS LOGO, RPI/VPI unregister paths, sysfs/debugfs, and HBA port-list locking. It uses Linux spinlocks, waitqueues, signals, timers, kthreads/scheduler headers, and PCI/SCSI transport declarations.

## Risks And Edge Cases
Create and delete have many partial-resource paths. VPI allocation, instance allocation, port creation, service-parameter mailbox, sysfs allocation, SLI-4 INIT_VPI, and fabric discovery must unwind consistently. Delete has delicate SCSI host reference ordering: the early `scsi_host_get()` must happen before `scsi_remove_host()`, and unreg_vpi completion may drop a reference. DA_ID and LOGO are best-effort, so fabric may retain stale entries. Discovery waits use bounded sleeps and can return after timeout with teardown continuing. Duplicate WWPN checks rely on `port_list_lock` and must not race list insertion/removal.

## Test Signals
Useful tests include NPIV disabled rejection, NVMe-target rejection, max-VPI exhaustion, service-parameter mailbox timeout and signal paths, invalid and duplicate WWN rejection, create during link down, create before VFI registration, disabled-create then enable, fabric without NPIV support, disable/enable with LOGO and deferred INIT_VPI, delete during active discovery, static-vport delete rejection, driver unload delete path, refcount leak checks, and repeated create/delete stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vport.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vport.h

## Purpose
`lpfc_vport.h` declares the LPFC virtual-port management interface and legacy vport information structures. It defines API version bits, vport information and creation payloads, vport return codes, command tags, and the exported functions implemented by `lpfc_vport.c`.

## Important APIs, Types, And Functions
`struct vport_info` is a reporting structure with API version bits, physical/virtual link type, active/offline/failed state, failure reason and previous reason, WWNN/WWPN, SCSI host pointer, and physical-link capacity counters for vports and RPIs. `struct vport_data` describes creation input: API version, options such as `VPORT_OPT_AUTORETRY`, WWNN/WWPN, and the resulting `vport_shost`.

Return codes are `VPORT_OK`, `VPORT_ERROR`, `VPORT_INVAL`, `VPORT_NOMEM`, and `VPORT_NORESOURCES`. Function declarations include `lpfc_vport_create()`, `lpfc_vport_delete()`, `lpfc_vport_getinfo()`, `lpfc_vport_tgt_remove()`, `lpfc_create_vport_work_array()`, `lpfc_destroy_vport_work_array()`, `lpfc_alloc_vpi()`, and `lpfc_vport_set_state()`. `DID_VPORT_ERROR` defines a host-byte result code for virtual-link failures. `struct vport_cmd_tag` packages a vport operation command and payload.

## Control Flow
The header has no executable control flow. It defines the call surface used by FC transport and LPFC internals. Create/delete/disable flows in `lpfc_vport.c` consume these prototypes and return codes. Work-array helpers let callers snapshot active vports with SCSI host references and later release them.

## State And Persistence
The structures describe runtime state only. `vport_info` is a snapshot-style payload; `vport_data` and `vport_cmd_tag` are command/control payloads. No persistent storage is defined.

## Dependencies And Integration Points
The header depends on declarations for `struct Scsi_Host`, `struct fc_vport`, `struct lpfc_hba`, `struct lpfc_vport`, and `enum fc_vport_state` from SCSI/FC transport and LPFC headers included by users. It integrates LPFC vport code with the FC transport, SCSI host layer, and any legacy management path still using `vport_cmd_tag`.

## Risks And Edge Cases
Several APIs are declared here but not implemented in the paired source file section, so users must include the broader LPFC tree when tracing them. The information structures expose raw `Scsi_Host *` pointers and fixed-size WWN arrays, which are kernel-internal contracts rather than stable UAPI. Return codes are negative integers that are distinct from standard Linux `-errno` values, so callers must not blindly mix them.

## Test Signals
Validation signals include compile checks for all declarations, FC transport create/delete/disable callbacks returning documented `VPORT_*` values, `DID_VPORT_ERROR` result propagation for failed virtual links, work-array reference balancing, and any management path using `vport_info` correctly reporting physical versus virtual capacity counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mac53c94.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mac53c94.c

## Purpose
`mac53c94.c` is a low-level SCSI driver for the 53C94 controller found on Power Macintosh systems, controlling the external SCSI chain through macio resources and a DBDMA engine. It binds an Open Firmware/macIO device, registers a single-queue SCSI host, maps controller and DBDMA registers, builds DBDMA command lists from SCSI scatterlists, drives a simple SCSI phase state machine, and completes commands through the SCSI mid-layer.

## Important APIs, Types, And Functions
The driver state is `struct fsc_state`, containing mapped 53C94 registers, DBDMA registers, IRQs, clock frequency, `Scsi_Host`, request queue, current command, phase, DBDMA command buffer, PCI/macio device pointers, and DMA metadata. `enum fsc_phase` models `idle`, `selecting`, `dataing`, `completing`, and `busfreeing`.

Important functions are `mac53c94_queue_lck()`/`mac53c94_queue`, `mac53c94_host_reset()`, `mac53c94_init()`, `mac53c94_start()`, `do_mac53c94_interrupt()`, `mac53c94_interrupt()`, `cmd_done()`, `set_dma_cmds()`, `mac53c94_probe()`, and `mac53c94_remove()`. The SCSI host template sets `can_queue = 1`, initiator ID 7, `SG_ALL`, a 65535-byte max segment size, and command-private storage for `struct mac53c94_cmd_priv`.

## Control Flow
Probe requires two address resources and two IRQs, requests macio resources, allocates the SCSI host plus `fsc_state`, maps controller and DMA registers, reads `clock-frequency` or defaults to 25 MHz, allocates an aligned DBDMA command array, initializes the chip, requests the controller IRQ, adds the host, and starts SCSI scanning.

Queueing appends commands to a simple singly-linked request queue using `host_scribble`. If the controller is idle, `mac53c94_start()` dequeues one command, flushes the FIFO, programs destination ID and async transfer settings, writes the CDB into FIFO, issues `CMD_SELECT`, sets phase `selecting`, and prepares the DBDMA command list. Interrupt handling reads sequence/status/interrupt registers in the hardware-required order, handles reset/illegal command/parity errors, and advances the phase state. Selection success starts DBDMA if a data phase is present; dataing either programs another 0xfff0-byte chunk or stops DMA and requests status; completing reads status/message and accepts the message; busfreeing completes the SCSI command and starts the next queued command.

## State And Persistence
All state is volatile. The command queue, active command, phase, residual count/status/message command-private fields, and DBDMA command buffer persist only while the host is registered. The driver does not persist configuration; hardware clock frequency comes from device tree at probe.

## Dependencies And Integration Points
The file depends on PowerPC macio, Open Firmware device nodes, DBDMA registers, MMIO accessors, Linux IRQ and SCSI mid-layer APIs, PCI device access through macio, DMA mapping through `scsi_dma_map()`/`scsi_dma_unmap()`, and register definitions from `mac53c94.h`.

## Risks And Edge Cases
`do_mac53c94_interrupt()` dereferences `current_req` before checking for NULL, so a spurious interrupt with no active request could fault before `mac53c94_interrupt()` handles it. `set_dma_cmds()` uses `BUG_ON(nseg < 0)` and panics if an SG element is at least 64 KiB. The DBDMA command memory is allocated with `kmalloc` and programmed via `virt_to_phys()`, with a comment noting it should use DMA-consistent routines. The driver handles only one command at a time and has minimal message/disconnect/reselection support. Error paths complete broadly with `DID_ERROR`, and DMA unmap occurs only on the expected data completion path.

## Test Signals
Signals include successful macio probe/remove, correct fallback/default clock programming, SCSI scan on external bus, single-command queue ordering, no-data and data commands, multi-segment DBDMA lists below 64 KiB per segment, selection timeout producing `DID_BAD_TARGET`, bus reset producing `DID_RESET`, host reset reinitializing hardware, parity/illegal-command handling, module unload cleanup, and spurious-interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mac53c94.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mac53c94.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mac53c94.h

## Purpose
`mac53c94.h` defines the register map, command bits, status/interrupt/sequence/configuration constants, and command-private storage for the Power Macintosh 53C94 SCSI driver. It is the hardware contract consumed by `mac53c94.c`.

## Important APIs, Types, And Functions
`struct mac53c94_regs` lays out the 53C94 register block with 16-byte-spaced byte registers for transfer counts, FIFO, command, status, interrupt, sequence step, flags, configuration registers, and high count. Register aliases (`dest_id`, `sel_timeout`, `sync_period`, `sync_offset`) document alternate write meanings for shared offsets.

The command macros cover DMA mode, initiator/target/disconnect modes, reset, FIFO flush, data transfer, initiator completion, accept message, pad transfer, ATN control, target-mode operations, reselect/select variants, and DMA abort. Status macros expose IRQ, error, parity, terminal count, done, and phase bits. Interrupt macros expose reset, illegal command, disconnect, bus service, done, reselection, and selection events. Sequence, sync period/offset, FIFO flag, and config macros encode hardware programming values. `struct mac53c94_cmd_priv` stores per-command residual, status, and message, and `mac53c94_priv()` retrieves it from SCSI command-private storage.

## Control Flow
The header has no independent control flow. Its constants drive `mac53c94_init()` register programming, `mac53c94_start()` command selection, `mac53c94_interrupt()` phase decoding, and `mac53c94_host_reset()` reset commands. The register layout determines every MMIO access in the C file.

## State And Persistence
The register structure maps hardware state rather than owned memory. `struct mac53c94_cmd_priv` is volatile per-SCSI-command state allocated by the SCSI mid-layer using the host template `cmd_size`. The header defines no persistent state.

## Dependencies And Integration Points
The inline accessor depends on `struct scsi_cmnd` and `scsi_cmd_priv()` being visible to the including C file. The rest of the header is plain C constants and a hardware register layout. It integrates only with the Mac 53C94 driver.

## Risks And Edge Cases
The structure assumes exact 16-byte register spacing and byte access ordering. Alias macros make read/write meaning context-dependent; writing a value intended for `dest_id` to the same offset later read as `status` is correct only in the right phase. `TIMO_VAL()` and `CLKF_VAL()` encode chip-specific timing assumptions, so wrong clock input changes selection timeout and sync timing. Command-private residual is an `int`, while transfer totals are accumulated from DMA lengths.

## Test Signals
Header-level checks include correct compile on the PowerPC/macIO target, register offsets matching hardware documentation, reset/init/status/interrupt bits exercised by the driver, SCSI command-private size wired into the host template, and transfer-count programming verified for small and near-64KiB chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mac53c94.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mac_esp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mac_esp.c

## Purpose
`mac_esp.c` is the Macintosh Quadra front-end for the generic ESP SCSI core. It maps fixed Macintosh ESP register addresses, implements byte register access and pseudo-DMA/PIO transfer callbacks, handles the shared edge-triggered Mac SCSI IRQ for up to two ESP chips, and registers/unregisters ESP instances as platform devices.

## Important APIs, Types, And Functions
`struct mac_esp_priv` stores the generic `struct esp *` plus PDMA status and data I/O addresses. Global `esp_chips[2]` and `esp_chips_lock` coordinate the shared interrupt handler. Hardware access callbacks are `mac_esp_write8()`, `mac_esp_read8()`, `mac_esp_reset_dma()`, `mac_esp_dma_drain()`, `mac_esp_dma_invalidate()`, `mac_esp_dma_error()`, `mac_esp_irq_pending()`, and `mac_esp_dma_length_limit()`. Transfer helpers are `mac_esp_wait_for_empty_fifo()`, `mac_esp_wait_for_dreq()`, the inline-assembly `MAC_ESP_PDMA_LOOP`, and `mac_esp_send_pdma_cmd()`.

The integration surface is `struct esp_driver_ops mac_esp_ops`, `esp_mac_probe()`, `esp_mac_remove()`, and `mac_scsi_esp_intr()`. Probe fills the generic ESP fields and calls `scsi_esp_register()`.

## Control Flow
Probe rejects non-Mac systems and device IDs above 1, allocates a SCSI host with generic ESP private data, allocates a 16-byte command block, creates `mac_esp_priv`, chooses register addresses and clock frequency from `macintosh_config->scsi_type`, sets the FIFO register and callbacks, and selects PDMA or PIO. Quadra and Quadra2 use PDMA; Quadra3 logs PIO and disables sync because its PSC DMA is not driven. The first ESP instance normally owns the shared IRQ, and the second shares the global handler through `esp_chips[]`. After registration with the generic ESP core, the SCSI scan is handled by that core.

On transfer, `mac_esp_send_pdma_cmd()` programs transfer counts, issues the ESP command, waits for DREQ, runs the 68k assembly loop in read or write direction, drains FIFO for reads, and repeats until the ESP count reaches zero or an interrupt/error stops the loop. The IRQ handler loops while either chip reports `ESP_STAT_INTR`, calling `scsi_esp_intr()` for each to avoid losing edge-triggered transitions.

## State And Persistence
Runtime state is volatile: `esp_chips[]`, per-device `mac_esp_priv`, generic ESP state, command block memory, send-command error flag, and platform driver data. There is no persistent configuration; machine type and fixed addresses are firmware/platform facts.

## Dependencies And Integration Points
The driver depends on m68k Macintosh platform data (`macintosh_config`), NuBus accessors, VIA DRQ checks, Mac IRQ constants, generic ESP SCSI core (`esp_scsi.h`), Linux platform driver and SCSI host APIs, and low-level inline assembly exception-table fixups for PDMA.

## Risks And Edge Cases
The PDMA wait loops can spin for up to 500000 iterations with microsecond delays, so hung hardware causes long stalls. `mac_esp_ops.send_dma_cmd` is a global ops field mutated to PIO when one device lacks PDMA; mixed-device configurations could be sensitive to that shared mutation. Fixed physical MMIO addresses and machine-type branches limit portability. Transfer loops rely on m68k exception-table recovery and manual count reconstruction. Shared IRQ handling must update `esp_chips[]` atomically enough to avoid calling into a removed chip.

## Test Signals
Signals include probe on Quadra, Quadra2, and Quadra3 paths; PDMA and PIO transfer success; IRQ sharing with one and two ESP devices; FIFO-empty and DREQ timeout logging; transfer length clamping at 0xffff; generic ESP scan and command completion; unregister/free IRQ behavior when removing one of two chips; and error propagation through `esp->send_cmd_error`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mac_esp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mac_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mac_scsi.c

## Purpose
`mac_scsi.c` is the generic Macintosh NCR5380 SCSI platform driver. It binds Macintosh NCR5380-compatible hardware to the shared `NCR5380.c` core by defining register access macros, pseudo-DMA setup/residual callbacks, interrupt/queue/reset aliases, module/boot parameters, and Macintosh-specific PDMA transfer routines with m68k bus-error recovery.

## Important APIs, Types, And Functions
The file configures the core with macros such as `NCR5380_read`, `NCR5380_write`, `NCR5380_dma_xfer_len`, `NCR5380_dma_recv_setup`, `NCR5380_dma_send_setup`, `NCR5380_dma_residual`, and aliases for interrupt, queue, abort, reset, and info functions. Module parameters include queue depth, commands per LUN, SG table size, PDMA threshold, host ID, and Toshiba delay. Boot-time `mac5380=` parsing sets the same values for built-in kernels.

Transfer primitives are `mac_pdma_recv()`, `mac_pdma_send()`, `write_ctrl_reg()`, `macscsi_wait_for_drq()`, `macscsi_pread()`, `macscsi_pwrite()`, `macscsi_dma_xfer_len()`, and `macscsi_dma_residual()`. The platform integration is `mac_scsi_probe()`, `mac_scsi_remove()`, `mac_scsi_template`, and `module_platform_driver_probe()`.

## Control Flow
Probe obtains PIO, optional PDMA, and optional IRQ resources, checks hardware presence, applies module parameter overrides, forces IIfx SG table size to 1, allocates a SCSI host plus `NCR5380_hostdata`, fills register bases and PDMA flags, calls `NCR5380_init()` with late DMA setup, requests a shared IRQ when present, possibly resets the bus, adds the host, stores platform driver data, and scans. Remove unregisters the host, frees IRQ, exits the NCR5380 core, and drops the SCSI host reference.

Pseudo-DMA receive/write waits for DRQ while phase matches and no IRQ is pending, optionally toggles IIfx handshake mode, transfers up to 512 bytes per chunk with bus-error-aware assembly loops, updates `pdma_residual`, logs bus errors, and marks the connected command `DID_ERROR` if the target stops delivering data in a way that cannot be retried. `macscsi_dma_xfer_len()` enables PDMA only when pseudo-DMA is available and the residual exceeds the configured threshold.

## State And Persistence
State is volatile in `NCR5380_hostdata`, including register base, PDMA I/O address, flags, connected command, and `pdma_residual`. Module parameters persist only as module/kernel command-line configuration for the current boot. No device data is persisted.

## Dependencies And Integration Points
The file depends on m68k Macintosh platform data, `hwreg_present()`, Mac IRQs, I/O accessors, the generic NCR5380 core/header, Linux platform driver APIs, and SCSI mid-layer APIs. It includes `NCR5380.c` directly after defining implementation macros, making it a compile-time specialization of the generic core.

## Risks And Edge Cases
Inline assembly and exception-table recovery are architecture-specific and must preserve residual accounting exactly. Send-side bus errors may leave target-visible ACK uncertainty, so commands are retried as errors. Busy waits in `macscsi_wait_for_drq()` rely on polite polling and can still delay progress. Parameter overrides can set queue/SG sizes beyond what old hardware handles unless bounded by core behavior. The driver uses physical platform resource addresses directly as I/O pointers, reflecting legacy m68k address mapping assumptions.

## Test Signals
Signals include boot parameter parsing, probe with and without IRQ/PDMA resources, IIfx single-SG and handshake behavior, PDMA threshold fallback to PIO, receive/send bus-error injection, DRQ timeout handling, NCR5380 queue/abort/reset behavior, SCSI scan on supported Macs, module unload cleanup, and stress transfers across odd/even buffer alignment and residual lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mac_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid.c

## Purpose
`megaraid.c` is the legacy LSI Logic MegaRAID SCSI driver for older PCI RAID controllers. It registers a PCI driver and SCSI host template, translates SCSI logical-drive and physical-device commands into MegaRAID mailbox or passthrough commands, manages SCB pools and scatter-gather DMA, handles I/O- or MMIO-mapped interrupts, exposes `/proc/megaraid` diagnostics, and provides a privileged legacy management character-device ioctl interface.

## Important APIs, Types, And Functions
The module entry points are `megaraid_init()` and `megaraid_exit()`. PCI lifecycle is `megaraid_probe_one()`, `megaraid_remove_one()`, and `megaraid_shutdown()`. SCSI integration is `megaraid_template` with `megaraid_queue`, `megaraid_info`, `megaraid_biosparam`, `megaraid_abort`, and `megaraid_reset`. Character-device integration is `megadev_fops`, `megadev_open()`, `megadev_unlocked_ioctl()`, and `megadev_ioctl()`.

Core command functions include `mega_setup_mailbox()`, `mega_query_adapter()`, `mega_build_cmd()`, `mega_allocate_scb()`, `mega_prepare_passthru()`, `mega_prepare_extpassthru()`, `mega_build_sglist()`, `issue_scb()`, `issue_scb_block()`, `mega_cmd_done()`, `mega_free_scb()`, `mega_internal_command()`, and `mega_init_scb()`. Firmware capability/configuration helpers include `mega_is_bios_enabled()`, `mega_enum_raid_scsi()`, `mega_get_boot_drv()`, `mega_support_random_del()`, `mega_support_ext_cdb()`, `mega_get_max_sgl()`, `mega_support_cluster()`, `mega_del_logdrv()`, and `mega_do_del_logdrv()`.

## Control Flow
Probe enables PCI, filters false Intel/Compaq matches, detects 64-bit support, reserves and maps BAR resources as I/O or memory, allocates `Scsi_Host` plus `adapter_t`, initializes lists and locks, allocates the internal command buffer and SCB array, requests the IRQ, sets up an aligned coherent mailbox, queries firmware for product, channel, logical-drive, max-command, and SG information, applies firmware quirks, discovers BIOS boot drive and RAID/SCSI channel layout, checks random-delete support, allocates per-SCB SG/passthrough buffers, initializes counters and internal-command serialization, creates proc entries, adds the SCSI host, and scans.

Queue flow starts in `megaraid_queue_lck()`. Under `adapter->lock`, it builds an SCB or completes simple emulated commands immediately. Logical-drive TEST_UNIT_READY and MODE_SENSE may complete in software; INQUIRY/READ_CAPACITY use passthrough; READ/WRITE commands become mailbox LREAD/LWRITE commands with LBA/sector fields and SG lists. Physical-device commands use passthrough or extended passthrough. Built SCBs are appended to `pending_list`, and `mega_runpendq()` posts them while the adapter is not quiescent.

Interrupt flow differs by mapping type but both handlers collect completed command IDs and firmware status, acknowledge the controller, decrement pending counts, call `mega_cmd_done()`, run `scsi_done()` for completed commands, and then drain newly pending SCBs. Completion maps firmware status to `DID_OK`, check condition with sense copy, bus busy, reservation conflict, abort/reset, or bad target, unmaps DMA, frees SCBs, and queues SCSI commands for callback.

Management ioctl flow accepts only admin callers, converts old MIMD user requests to internal NIT-like structures, reports driver/controller/stats data, or issues mailbox/passthrough commands with temporary coherent low-DMA buffers. Logical-drive deletion quiesces the adapter, waits for issued and pending commands to drain, sends the delete command, updates logical-drive addressing mode, unquiesces, and restarts pending work.

## State And Persistence
Persistent hardware configuration lives in controller firmware/BIOS and is queried through mailbox commands; this driver does not write host-side persistent storage. Runtime state is in `adapter_t`: mailbox memory, MMIO/I/O base, free/pending/completed SCB lists, SCB array, internal command SCB/completion/mutex, product info, firmware/BIOS versions, logical-drive/channel mapping, boot drive selection, capability flags, quiescent and pending-command counters, SG length, proc-visible stats, and HBA global arrays. The global `hba_soft_state`, `mcontroller`, `mega_hbas`, `hba_count`, proc root, char-device major, and module parameters persist for module lifetime.

## Dependencies And Integration Points
The driver depends on PCI, DMA mapping/coherent allocation, interrupt handling, SCSI mid-layer/error handling, scatterlists, procfs/seq_file, uaccess, capabilities, mutex/completion/list APIs, and private firmware structures/macros from `megaraid.h`. User-space integration is through `/dev/megadev_legacy` ioctls and `/proc/megaraid/hba*/...` diagnostics. Firmware integration is the MegaRAID mailbox protocol, including 64-bit mailbox segment fields, passthrough, inquiry, config, cache flush, and logical-drive delete commands.

## Risks And Edge Cases
The code is legacy and contains several sharp edges. DMA map failure in `mega_build_sglist()` is handled with `BUG_ON(sgcnt < 0)`, so mapping failure can crash the kernel. Several busy waits spin until mailbox/interrupt fields change, including blocking commands used during probe and shutdown. The ioctl path handles user-controlled lengths for coherent allocations and passthrough shapes; it checks access through copy helpers and admin capability but remains high-risk. The NIT signature path is intentionally disabled while older MIMD translation remains active. Logical-drive deletion waits in one-second sleeps for all pending work and depends on user space coordinating OS device removal. `hba_count` and global arrays are simple legacy global state, so hot-unplug/reordering behavior is delicate. Shutdown frees IRQ before issuing blocking flush commands and then waits up to about 11 seconds.

## Test Signals
Signals include PCI probe/remove for I/O- and MMIO-mapped controllers, false Intel ID rejection, 32/64-bit DMA mask paths and HP firmware quirk, successful adapter inquiry on 8LD and 40LD firmware, SCSI scan of logical and physical channels with boot-drive remapping, read/write SG mapping and completion, passthrough INQUIRY/READ_CAPACITY, abort/reset behavior for driver-owned versus firmware-owned SCBs, interrupt handling under command queue pressure, proc config/stat/mailbox/rebuild/battery/disk outputs, admin-only ioctl behavior, passthrough data copy in both directions, logical-drive delete quiesce/unquiesce, cache flush on shutdown, and unload with SCB/mailbox/proc/char-device resources freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid.c -->
