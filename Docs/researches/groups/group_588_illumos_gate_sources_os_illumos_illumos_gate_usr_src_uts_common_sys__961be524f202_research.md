# Group Research: group_588_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__961be524f202

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and all fifteen requested source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_rsrc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_rsrc.h

## Role

`hermon_rsrc.h` defines the resource-management contract for the illumos Hermon InfiniBand HCA driver. It names Hermon resource pools, classifies hardware and software resource types, describes initialization/cleanup state, and declares the allocation/free/reservation entry points used across the driver.

## Major Definitions

The header defines sleep-context constants and `HERMON_SLEEPFLAG_FOR_CONTEXT()`, which maps interrupt or panic context to non-sleeping allocation behavior. It also defines resource cache and vmem arena names for ICM, mailboxes, CMPT/QPC/SRQC/CQC/EQC/DMPT/MTT/MCG tables, UAR pages, BlueFlame pages, and software handle caches.

The main enums are:
- `hermon_mpt_rsrc_type_t`, classifying CMPT-backed MPT/control resource variants.
- `hermon_rsrc_type_t`, enumerating all ICM-backed and non-ICM resources, including FCoIB-related QPC reservations.
- `hermon_rsrc_cleanup_level_t`, a staged attach/detach cleanup ladder.

The initialization helper structures describe mailbox pools, hardware entry pools, and software handle pools. `hermon_rsrc_pool_info_s` records each resource pool’s type, location, size, alignment, quantum, vmem arena, driver state, and private metadata. `hermon_rsrc_priv_mbox_t` carries DMA/access attributes for mailbox resources. `hermon_rsrc_s` is the allocation handle returned to consumers, with address, length, index, DMA handle, and access handle fields.

## Interfaces

The exported functions are `hermon_rsrc_alloc`, `hermon_rsrc_free`, two-phase resource initialization, resource finalization by cleanup level, and `hermon_rsrc_reserve` for FCoIB reservation use.

## Integration Notes

This header is central to Hermon attach, detach, firmware table setup, mailbox setup, and fast-path object allocation. Resource enum order is significant because resource arrays are indexed by type and comments explicitly constrain where new ICM resources can be inserted.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_rsrc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_srq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_srq.h

## Role

`hermon_srq.h` defines the Shared Receive Queue layer for the Hermon driver. It exposes the SRQ software handle layout, allocation/query/modify/post state carriers, SRQ constants, and the SRQ routines used by IBTF-facing CI code and internal queue management.

## Major Definitions

The file defines the default SRQ count shift, minimum SRQ size, maximum SGL count per SRQ WQE, and Hermon SRQ ownership/error states.

`hermon_sw_srq_s` is the core SRQ handle. It stores:
- Locking and state fields.
- SRQ number, protection domain, memory-region handle, user-mapping fields, UAR page, and devmap cookie.
- Real queue sizes, SRQC/WQ resources, callback argument, and reference count.
- Work-queue metadata, WQE buffer pointer, buffer size, WQE size shift, SGL count, and WQE counter.
- Doorbell record access handle, virtual/physical doorbell pointers, user map offset, zero-based descriptor offset, and queue allocation info.

The `_NOTE` annotations document read-only fields, lock-protected fields, and fields intentionally readable without holding `srq_lock`.

`hermon_srq_info_t` carries allocation inputs/outputs such as PD, IBT SRQ handle, requested and real sizes, result handle, and flags. `hermon_srq_options_t` exists for extended allocation options, currently queue-location selection.

## Interfaces

The exported routines allocate, free, modify, post receive WRs to, reference-count, and look up SRQs by SRQ number.

## Integration Notes

SRQs combine hardware context resources, WQE memory, memory registration, doorbell records, user mappings, and IBTF-visible handles. The file’s maximum SGL choice is a driver policy derived from firmware WQE-size limits.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_srq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_typedef.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_typedef.h

## Role

`hermon_typedef.h` is the forward-declaration hub for the Hermon driver. It lets `hermon.h` include common opaque types before pulling in the rest of the driver headers.

## Major Definitions

The file declares aliases for the Hermon soft state, agent list, queue allocation info, resource pool and resource handles, WRID/work-queue support structures, ICM structures, DMA info, and many hardware mailbox/context structures.

Hardware typedefs cover firmware/query structures, port setup structures, MPT/CMPT/MTT/EQC/EQE/CQC/SRQC/UAR/CQE layouts, address paths, UD address vectors, QP contexts, multicast group entries, performance counters, and WQE segment layouts.

The file also defines the main software handle pointer typedefs:
- `hermon_mrhdl_t`, `hermon_mwhdl_t`, `hermon_pdhdl_t`
- `hermon_eqhdl_t`, `hermon_cqhdl_t`, `hermon_srqhdl_t`
- `hermon_fmrhdl_t`, `hermon_ahhdl_t`, `hermon_qphdl_t`
- `hermon_mcghdl_t`

## Interfaces

There are no function prototypes. The header only establishes names for structures defined elsewhere.

## Integration Notes

This file reduces include-order coupling across the Hermon driver. Many typedefs are opaque pointer handles used by IBTF-facing entry points, while hardware-layout typedefs make later headers readable without requiring full definitions up front.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_typedef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_wr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_wr.h

## Role

`hermon_wr.h` defines Hermon work-request and WRID tracking helpers. It provides macros for WQE address calculations, CQE WQE-token extraction, send-WQE ownership updates, special-QP directed-route MAD handling, and work-queue bookkeeping structures.

## Major Definitions

The WQE macros compute queue entries for QP send queues, QP receive queues, and SRQs from queue base plus tail index and WQE-size shift. SRQ helpers convert between WQE addresses and SRQ WQE indexes.

`HERMON_SET_SEND_WQE_OWNER()` writes the send WQE owner/opcode field. `HERMON_CQE_WQEADDRSZ_GET()` extracts the CQE WQE address/size token.

Directed-route MAD macros locate management class, hop pointer, and hop count fields across possibly fragmented buffers, then adjust the hop pointer for outbound/inbound directed-route MAD processing.

`hermon_workq_hdr_s` tracks WRID circular queue state: queue size, mask, WRID array, head, tail, and full flag. `hermon_workq_avl_s` links work queues into an AVL tree by QP number/type and carries SRQ metadata when completions must return SRQ WQEs to a free list. `HERMON_WR_RECV`, `HERMON_WR_SEND`, and `HERMON_WR_SRQ` classify work-queue types.

## Interfaces

The file declares post-send, post-receive, and post-SRQ routines; WRID reset handling; CQE-to-WRID lookup; work-queue header create/destroy helpers; an AVL comparator; and a debug QP check routine.

## Integration Notes

This header sits on the Hermon fast path. The work-queue and WRID structures bridge posted IBTF work requests to later CQ completions, including SRQ-specific completion recycling.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_wr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/mlnx_umap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/mlnx_umap.h

## Role

`mlnx_umap.h` defines the versioned kernel-to-user data ABI for direct userland access to Mellanox HCA resources. It is shared by kernel service drivers such as Tavor, Arbel, and Hermon and user libraries above them.

## Major Definitions

`MLNX_UMAP_IF_VERSION` is set to `2`; comments require consumers of `ibt_ci_data_out()` data to validate revision fields when reading these structures.

The resource type constants identify database entries for UAR pages, BlueFlame pages, process IDs, CQ memory, QP memory, MR user-memory cookies, SRQ memory, and doorbell-record memory. The file also defines a type mask and shift for resource type encoding.

The exported data structures are:
- `mlnx_umap_cq_data_out_t`, describing CQ number, CQ mapping offset/length, CQE count/size, and arm/poll doorbell record mappings and offsets.
- `mlnx_umap_qp_data_out_t`, describing QP number, queue memory mapping, RQ/SQ offsets, descriptor addresses, WQE counts/sizes, send/receive doorbell record mappings, and Hermon SQ headroom.
- `mlnx_umap_srq_data_out_t`, describing SRQ number, queue mapping, descriptor address, WQE count/size, receive doorbell record mapping, and offsets.
- `mlnx_umap_pd_data_out_t`, carrying PD revision and PD number.

## Interfaces

The header declares no functions. It defines data exchanged through other driver/library interfaces.

## Integration Notes

This is an ABI-sensitive header. Any structure change must be coordinated with user libraries such as `udapl_tavor.so.1` and corresponding version checks.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/mlnx_umap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor.h

## Role

`tavor.h` is the umbrella driver header for the Tavor InfiniBand HCA driver. It includes the shared IBTF and Mellanox user-mapping ABI headers, pulls in all Tavor-specific subsystem headers, and defines the driver soft-state structure plus attach/detach, callback, device-mode, devmap, and user-resource database infrastructure.

## Major Definitions

The file defines VPD header sizes, initial soft-state count, minor-number instance encoding, PCI BAR indexes for CMD/UAR/DDR spaces, software-reset constants, attach-message helpers, and `TAVOR_WARNING()`.

IBTF callback macros enable, perform, and quiesce async/CQ callbacks using `ts_ibtfpriv` and `ts_in_evcallb`. Device-mode macros detect maintenance, compatibility, and HCA mode from PCI properties and distinguish operational modes.

`tavor_drv_cleanup_level_t` defines attach cleanup stages. `tavor_cmd_reg_t` records mapped HCR, ECR, clear-ECR, clear-interrupt, and software-reset register pointers plus the HCR lock.

`tavor_state_s` is the central per-instance state object. It stores device info, interrupt/MSI state, operational mode, GUIDs and HCA identity, IBTF registration data, BAR mappings and access handles, saved PCI config space, UAR resources, command registers, DDR/resource arenas, mailbox lists, outstanding command list, configuration profile, PD/EQ/CQ/QP/SRQ handle tables, QPN AVL tree, query-command snapshots, special-QP state, management-agent state, multicast shadow table, kstats, ioctl locks/flash state, PCI config handle, and fast-reboot quiesce state.

The user-mapping database structures define an AVL-protected database of mapped resources keyed by object/resource type/driver instance, plus optional on-close callbacks and devmap tracking reference counts.

## Interfaces

The file declares devmap handling, CI data input/output helpers, umap database initialization/finalization/allocation/free/add/find routines, user-memory unlock callback handling, and on-close callback registration/clearing/dispatch.

## Integration Notes

This header is the structural backbone of the Tavor driver. It ties attach/detach ordering, hardware register mapping, IBTF registration, resource management, ioctl flash access, and userland queue mapping into a single soft-state contract.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_agents.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_agents.h

## Role

`tavor_agents.h` defines the management-agent support layer for Tavor software-assisted InfiniBand agents, covering SMA/PMA/BMA-style MAD handling through IBMF.

## Major Definitions

The header defines default software-agent counts per port for QP0 and QP1. QP0 gets the SMA; QP1 currently registers one agent because firmware does not support BMA. It also defines the agent task queue thread count, maximum queued tasks, and base task queue name.

Directed-route MAD macros identify DR MADs, read hop count and hop pointer, update hop pointer, and set the direction bit with endian-specific status-bit handling. Additional macros identify special trap MADs and TrapRepress MADs.

`TAVOR_DRMAD_RETURN_PATH_OFFSET` gives the byte offset of the directed-route return path inside MAD data.

`tavor_agent_list_s` records driver state, port, management class, and IBMF handle for each registered agent so attach-time registrations can be cleaned up later. `tavor_agent_handler_arg_t` carries IBMF handle, message pointer, and agent-list pointer through the task queue from callback context to handler execution.

## Interfaces

The exported routines are `tavor_agent_handlers_init()` and `tavor_agent_handlers_fini()`.

## Integration Notes

This file bridges Tavor special-QP MAD traffic, IBMF agent registration, and task-queue-based request processing. It is only part of the control/management path, not data-path WQE posting.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_agents.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cfg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cfg.h

## Role

`tavor_cfg.h` defines the Tavor configuration profile structure and initialization hooks. The profile captures hardware resource sizing, queue capabilities, memory-mapping policy, port limits, agent policy, and GUID overrides used during attach and HCA initialization.

## Major Definitions

The header defines the fixed hardware port count (`TAVOR_NUM_PORTS`) and supported DDR sizing constants for 256 MB, 128 MB, and a minimal profile.

`tavor_cfg_profile_t` is the main configuration object. It contains:
- QP, CQ, SRQ, EQ, RDB, MCG, MPT, MTT, mailbox, UAR, PD, AH, PKey, and GID sizing fields.
- WQE SGL limits and real maximum SGL values.
- SRQ/FMR enablement fields and FMR remap limits.
- Multicast hash and QP-per-group parameters.
- HCA RDMA responder/initiator limits, MTU, port width, VL capability, and port count.
- Firmware-vs-software QP0/QP1 management-agent policy.
- DMA mapping policy, consistent-sync override, IOMMU bypass, and streaming-disable-on-bypass behavior.
- Work-queue placement policy for QP/SRQ queues.
- Reset and command polling delays.
- ACK request, split transaction, and read burst defaults.
- MSI preference.
- optional system image, node, and port GUID overrides.

## Interfaces

The file declares two-phase configuration profile initialization and profile finalization.

## Integration Notes

The profile is consumed by resource initialization, HCA initialization mailbox construction, queue allocation, DMA synchronization decisions, and port setup. Many fields can be controlled by driver configuration variables but must remain within hardware-reported limits.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cfg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cmd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cmd.h

## Role

`tavor_cmd.h` defines the Tavor firmware command interface. It names firmware opcodes and completion statuses, describes mailbox and outstanding-command pools, defines command-post payloads, handles MAD endianness conversion helpers, and declares the command wrappers used by the rest of the driver.

## Major Definitions

The header defines command polling defaults, mailbox counts/sizes/alignment, and `TAVOR_MBOX_IS_SYNC_REQ()` for deciding whether mailbox DMA sync is required.

Firmware opcodes cover system enable/disable, device/firmware/DDR/adapter/HCA queries, HCA and IB port init/close/set operations, MPT/MTT/TPT operations, EQ/CQ/QP/SRQ ownership and state transitions, MAD interface, multicast table operations, debug, diagnostics, static config modification, and MPT modification. Status constants include hardware statuses plus driver-defined insufficient-resource, timeout, and invalid-status values.

QP command flags cover special QP type, QP transition opmasks, SQD event requests, direct-to-reset behavior, output-mailbox modifiers, SYS_EN modes, MAP_EQ mapping/unmapping, and MAD_IFC modes/sizes/attributes. Endian-aware macros convert common SM MAD responses for PortInfo, NodeInfo, GUIDInfo, and PKeyTable.

`tavor_mbox_t`, `tavor_mboxlist_t`, and `tavor_mbox_info_t` implement fast mailbox allocation/free pools. `tavor_cmd_t` and `tavor_cmdlist_t` similarly manage outstanding firmware command slots. `tavor_cmd_post_t` mirrors HCR command fields plus command flags.

## Interfaces

The file declares generic command posting, mailbox allocation/free, command completion handling, mailbox list initialization/finalization, outstanding-command list management, and wrappers for SYS_EN/DIS, INIT/CLOSE HCA, INIT/CLOSE/SET IB, QP transitions, queries, ownership transitions, MAD_IFC helpers, WRITE_MTT, SYNC_TPT, MAP_EQ, RESIZE_CQ, special-QP configuration, multicast commands, MOD_STAT_CFG, and MODIFY_MPT.

## Integration Notes

This is the Tavor control-plane API to firmware. It coordinates with event handling when commands complete through EQs and with resource code when mailbox allocation must obey sleep/non-sleep context rules.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cmd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cq.h

## Role

`tavor_cq.h` defines Tavor Completion Queue constants, software CQ state, CQE status/opcode values, and CQ operations exposed to IBTF and internal event processing.

## Major Definitions

The header defines default and minimal CQ counts/sizes for supported DDR profiles, CQ minimum size, `TAVOR_CQ_IS_SYNC_REQ()` for CQE DMA synchronization, and CQC entry size.

It enumerates CQE completion statuses for successful completions and local/remote errors, including length, operation, protection, flushed, bind, access, request, timeout, RNR NAK timeout, and unsupported RD-related errors. CQE type constants distinguish send RDMA write/read, send, atomic, bind, receive, and receive-with-immediate variants.

Macros map CQ numbers to completion EQs and CQ-error EQs. Error-CQE helpers define status, doorbell count, send/receive error opcodes, and recycling behavior. Special-QP tracking distinguishes normal and special CQs.

`tavor_sw_cq_s` stores CQ lock, consumer index, CQ number, CQE buffer, MR handle, size, sync flag, reference count, EQ numbers, special/user mapping flags, UAR page, devmap cookie, CQC and handle resources, callback argument, WRID AVL/tree state, reap list, and queue allocation info. `_NOTE` annotations document concurrency rules.

## Interfaces

The exported routines allocate, free, resize, arm/notify, poll, handle completion and error events, manage CQ reference counts, look up CQ handles by CQ number, and flush SRQ entries associated with a QP.

## Integration Notes

CQ state links hardware completion memory, event queues, IBTF callbacks, user mapping, and WRID lookup. CQE ownership and DMA sync behavior are performance-sensitive and depend on queue placement and mapping mode.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_event.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_event.h

## Role

`tavor_event.h` defines interrupt and event-queue support for the Tavor driver. It covers UAR doorbell writes, EQ sizing, event masks, catastrophic error identifiers, EQ software state, and event/interrupt processing entry points.

## Major Definitions

`TAVOR_UAR_DOORBELL()` performs 64-bit UAR writes. On 32-bit kernels it takes `ts_uar_lock` around `ddi_put64()` to preserve the hardware-required atomic write.

The file defines 64 total EQs, 47 used EQs, default EQ size, and `TAVOR_EQ_IS_SYNC_REQ()` for deciding whether EQE DMA sync is required. It also defines EQC entry size.

Event type constants and masks cover completions, path migration, communication established, send queue drained, CQ errors, local WQ/category errors, path migration failure, port state change, command completion, page faults, ECC detection, EQ overflow, invalid request/access violation WQ errors, and SRQ catastrophic/last-WQE events. `TAVOR_EVT_CATCHALL_MASK` catches selected error classes.

Additional constants control forced EQE sync, catastrophic error classification, and MSI programming.

`tavor_sw_eq_s` stores EQ consumer index, EQ number, EQE buffer, MR handle, size, sync flag, event mask, EQC and handle resources, handler function pointer, and queue allocation info.

## Interfaces

The file declares EQ initialization/finalization, EQ arming, the main ISR, EQ doorbell posting, and EQ overflow handling.

## Integration Notes

This header connects hardware interrupts, EQ memory, command completion events, CQ events, and asynchronous IBTF events. Its doorbell macro is architecture-sensitive because Tavor requires atomic 64-bit MMIO writes.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_hw.h

## Role

`tavor_hw.h` is the hardware ABI definition header for the Tavor HCA. It maps command BAR offsets, firmware mailbox layouts, resource-context entries, event/completion entries, queue-pair contexts, doorbells, WQE segments, undocumented register offsets, and flash-interface constants.

## Major Definitions

The header defines CMD BAR offsets for HCR, ECR, clear-ECR, clear-interrupt, and software reset registers; hardware/software ownership constants; and address-translation enablement constants.

Firmware command layouts include:
- `tavor_hw_hcr_s` and masks/shifts for command status, go bit, event bit, opmod, opcode, and token.
- `QUERY_DEV_LIM`, `QUERY_FW`, `QUERY_DDR`, and `QUERY_ADAPTER` result structures and revision/version constants.
- `INIT_HCA`/`QUERY_HCA` component structures for QP/EQ/CQ/RDB context bases, UDAV memory, multicast, TPT, UAR, and full HCA setup.
- `INIT_IB` port setup fields.

Memory and queue resource layouts include MPT, MTT, EQC/EQE, CQC/CQE, SRQC, MOD_STAT_CFG, UDAV, QP address paths, QPC entries, MCG entries, and performance counters. Most major firmware structures have separate little-endian and big-endian bitfield definitions.

Doorbell and work-queue definitions cover UAR send/receive/CQ/EQ doorbells, send WQE segments, MLX special-QP WQEs, receive WQE segments, SGL entries, and many macros for building WQEs with explicit DDI 32/64-bit writes.

The final sections define undocumented port/stat/GID/PKey register offsets and macros, plus flash PCI/config/register offsets, masks, timeouts, and Intel flash command-set constants.

## Interfaces

There are no C function prototypes. The file exports structures and macros consumed by command, CQ, EQ, QP, MR, multicast, ioctl, flash, and work-request code.

## Integration Notes

This is highly layout-sensitive firmware/hardware contract code. Field order, bit positions, endian variants, owner bits, and DDI accessor usage must match Tavor hardware expectations. Several fast-path WQE builders intentionally avoid C bitfield stores to reduce read-modify-write behavior.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_ioctl.h

## Role

`tavor_ioctl.h` defines the ioctl interface for Tavor driver control, diagnostics, firmware flashing, flash access, VTS status, loopback testing, and DDR reads.

## Major Definitions

The header declares `tavor_ioctl()` and defines the ioctl command base. In debug builds it includes register read/write ioctl commands; non-debug builds expose flash read/write/erase/init/fini, loopback, info, ports, and DDR read commands.

Flash constants define read/write/erase operation types, default sector/device sizes, CFI init command, legacy and expanded CFI data sizes, and supported flash command-set IDs for Intel, AMD, and unknown command sets.

The ioctl data structures include:
- `tavor_fw_info_ioctl_t` for firmware version.
- `tavor_flash_ioctl_t` for sector, quadlet, byte, and erase operations.
- `tavor_flash_init_ioctl_t` for hardware revision, firmware revision, CFI info, and part number.
- `tavor_reg_ioctl_t` for debug register access.
- `tavor_stat_port_ioctl_t` and `tavor_ports_ioctl_t` for VTS port state.
- `tavor_ddr_read_ioctl_t` for aligned 32-bit DDR reads.
- `tavor_loopback_error_t` for loopback failure classification.
- `tavor_loopback_ioctl_t` for loopback buffers, iteration/retry/timeout settings, pass count, failure buffer, and error type.
- `tavor_info_ioctl_t` for firmware/hardware version, flash size, and accessible DDR range.

## Interfaces

Only `tavor_ioctl()` is declared here. Helpers and 32-bit compatibility forms live in other headers/source files.

## Integration Notes

This header is a user-kernel ABI surface. Structure layout and revision fields matter for tools such as VTS and firmware-update utilities. Some interfaces are gated by `DEBUG`.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_misc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_misc.h

## Role

`tavor_misc.h` collects Tavor support contracts for address handles, multicast groups, protection domains, queue allocation, port operations, kstats, VTS loopback support, and ioctl compatibility structures.

## Major Definitions

The header defines AH/UDAV counts and size, minimal AH profile, and `TAVOR_UDAV_IS_SYNC_REQ()`. Address-path type constants distinguish QP paths from UDAV paths.

Multicast definitions include MCG counts, QPs per group, MCG entry sizing and QP-list pointer macros, multicast hash sizing, and IBA-derived multicast GID validation fields for top bits, permanent/non-permanent flags, and scope. PD, PKey table, GID table, UAR page, MTU, port width, VL capability, and kstat counter constants follow.

Queue allocation location constants distinguish normal kernel memory, user-mappable memory, and HCA DDR. `TAVOR_VTS_LOOPBACK_MIN_WAIT_DUR` sets a minimum loopback polling delay.

Software structures include:
- `tavor_sw_ah_s` for AH/UDAV resources, PD/MR handles, saved GUID/rate, and sync state.
- `tavor_sw_mcg_list_s` for the shadow multicast table.
- `tavor_sw_pd_s` for PD number, reference count, and resource handle.
- `tavor_qalloc_info_s` for queue allocation size, alignment, buffer pointers, location, DMA/access handles, and user-memory cookie.
- kstat mask and 64-bit performance counter state.
- 32-bit ioctl compatibility structures for ports, loopback, and flash.
- VTS loopback communication and test-state structures.

## Interfaces

The file declares AH allocate/free/query/modify, multicast attach/detach, PD allocate/free/refcount, port query/modify, kstat init/fini, address-path set/get, port/PKey validation, queue allocate/free, and DMA attribute initialization.

## Integration Notes

This header is a broad support layer used by data-path setup, management operations, user ABI handling, diagnostics, and statistics. Its queue-location constants influence DMA sync and userland mapping behavior elsewhere.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_mr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_mr.h

## Role

`tavor_mr.h` defines Tavor memory-region and memory-window support. It provides MPT/MTT sizing constants, deregistration policy flags, DMA binding metadata, software MR handle state, registration options, and IBTF-facing MR/MW routines.

## Major Definitions

The file defines default and minimal MPT counts, MPT entry size, MTT entry size, MTT segment size, default/minimal MTT segment counts, and `TAVOR_NUMMTT_TO_MTTSEG()` for rounding MTT entries to segments. It also defines the MTT page-walk version and maximum memory-region/window size shifts for supported DDR profiles.

Deregistration levels specify whether to free all resources, skip HW2SW_MPT, or skip both HW2SW_MPT and unbind. `TAVOR_MR_REUSE_DMAHDL()` determines whether an existing DMA handle can be reused when bypass/noncoherent mapping constraints allow.

`tavor_sw_refcnt_t` tracks shared MTT reference counts for shared memory regions, with helpers to initialize and test sharing.

`tavor_bind_info_t` records the data needed for DMA binding: address, length, address space, buf pointer, DMA handle, current DMA cookie, cookie count, bind type, flags, bypass mode, and whether to free the DMA handle. Bind types cover none, virtual address, buf, and user buf.

`tavor_sw_mr_s` stores MR lock, MPT/MTT/refcount resources, PD handle, bind info, access flags, LKey/RKey, MTT page size, software resource, user-memory flag/cookie, and unpin callback data. `tavor_mr_options_t` provides optional DMA handle, bind type, and zero-based/override address behavior.

## Interfaces

The header declares DMA MR registration, virtual-address and buf registration, MTT bind/unbind, shared registration, deregistration, query, reregister variants, sync, memory-window allocate/free, and key calculation.

## Integration Notes

This header ties IBTF memory verbs to illumos DDI DMA binding and Tavor MPT/MTT firmware ownership. Reference counting is essential because shared MRs have distinct MPTs but may share MTT resources.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_mr.h -->