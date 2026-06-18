# Group Research: group_587_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__260be2c63f68

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cfg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cfg.h

## Purpose
Defines the Hermon driver configuration profile, including resource sizing, port capabilities, mailbox counts, management-agent choices, command polling timing, interrupt preference, IOMMU bypass policy, relaxed ordering flags, and optional GUID overrides.

## Main Interfaces
- `hermon_cfg_profile_t`: central in-memory configuration record used by the driver after attach-time profile initialization.
- Constants:
  - `HERMON_RO_DISABLED`, `HERMON_RO_ENABLED` for PCIe relaxed ordering.
  - `HERMON_CFG_MEMFREE` profile selector.
  - `HERMON_MAX_PORTS` fixed at 2.
  - `HERMON_LOG_CMPT_PER_TYPE` default control MPT allocation size.
- Lifecycle prototypes:
  - `hermon_cfg_profile_init_phase1()`
  - `hermon_cfg_profile_init_phase2()`
  - `hermon_cfg_profile_fini()`

## Dependencies And Relationships
This header relies on `hermon_state_t` being declared before use by includers. The profile fields are consumed across QP, CQ, SRQ, MR, event queue, multicast, mailbox, and port initialization code.

## Research Notes
This is a driver policy header rather than hardware layout. It captures tunables that gate nearly every resource table size used later by command and resource initialization.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cfg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cmd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cmd.h

## Purpose
Defines the firmware command interface for the Hermon HCA: opcodes, status values, mailbox management structures, outstanding command tracking, command-post arguments, MAD helper constants, endian-swap helpers, and command posting prototypes.

## Main Interfaces
- Firmware command opcodes cover init/close/query, TPT/MPT/MTT, EQ, CQ, QP transitions, special QPs, SRQ, multicast, diagnostics, ICM mapping, FCoIB, health check, and interrupt moderation.
- Command status constants include PRM statuses plus driver-local timeout/resource/invalid-status values.
- `hermon_mbox_t`, `hermon_mboxlist_t`, `hermon_mbox_info_t`: mailbox pool and allocation descriptors.
- `hermon_cmd_t`, `hermon_cmdlist_t`: outstanding command slots and completion synchronization.
- `hermon_cmd_post_t`: generic firmware command post payload matching HCR fields.
- MAD helper macros and endian conversion macros for PortInfo, NodeInfo, GUIDInfo, and PKeyTable responses.

## Dependencies And Relationships
Includes `sys/ib/mgt/sm_attr.h` for SM MAD structures. Depends heavily on hardware structures from `hermon_hw.h` and resource/handle typedefs from the wider Hermon driver. The public prototypes are used throughout initialization, QP/CQ/MR/EQ transitions, multicast management, FCoIB setup, and diagnostics.

## Research Notes
The command path supports both polling and event-completion models through `HERMON_CMD_SLEEP_NOSPIN` and `HERMON_CMD_NOSLEEP_SPIN`. Lock annotations describe mailbox and command-list ownership and lock ordering.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cmd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cq.h

## Purpose
Defines Completion Queue constants, CQE status/opcode values, CQ interrupt scheduling state, CQ software handle state, and CQ lifecycle/polling/event prototypes.

## Main Interfaces
- Defaults:
  - `HERMON_NUM_CQ_SHIFT`
  - `HERMON_CQ_MIN_SIZE`
- CQE status constants map completion syndromes such as local length, protection, flushed WQE, remote access, retry, and RNR timeout errors.
- CQE send and receive opcode constants cover RDMA, send, atomic, LSO, FRWR, local invalidate, bind MW, and resize/error markers.
- `hermon_cq_sched_t`: assigns CQ handler IDs over interrupt/MSI EQ ranges.
- `struct hermon_sw_cq_s`: software CQ handle containing lock, consumer index, CQ number, buffer/MR/resource pointers, EQ numbers, user mapping state, doorbell record fields, interrupt moderation settings, handler argument, WRID tree, and queue allocation metadata.
- Prototypes cover allocation/free, resize, modify, notify, poll, scheduling, interrupt handlers, refcounts, lookup by CQ number, flush, and scheduler init/fini.

## Dependencies And Relationships
Includes `hermon_misc.h` for queue allocation and shared driver definitions. CQ handlers consume EQEs from `hermon_event.h`/`hermon_hw.h`; QP and WRID code depend on CQ state for completion processing.

## Research Notes
The header documents separate EQ assignment for normal completions and CQ errors. Lock annotations split immutable CQ fields, lock-protected fields, and deliberately shared moderation/resize state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_event.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_event.h

## Purpose
Defines interrupt/event queue support: UAR doorbell write macros, doorbell record writes, EQ defaults, event IDs and masks, catastrophic error codes, EQ arm/register offsets, EQ software handle state, and event processing prototypes.

## Main Interfaces
- `HERMON_UAR_DOORBELL()` handles 64-bit doorbell writes, using `hs_uar_lock` only on 32-bit kernels to protect non-atomic 64-bit access.
- `HERMON_UAR_DB_RECORD_WRITE()` writes host-memory doorbell records in network byte order.
- EQ defaults:
  - `HERMON_NUM_EQ_SHIFT`, `HERMON_NUM_EQ`
  - `HERMON_NUM_EQ_USED`
  - `HERMON_DEFAULT_EQ_SZ_SHIFT`
  - `HERMON_EQ_CI_MASK`
- Event IDs and masks include completions, QP async events, CQ errors, SRQ events, port state, command completion, catastrophic/local errors, GPIO, spoof failure, and FEXCH errors.
- `struct hermon_sw_eq_s`: software EQ handle with consumer index, EQ number, EQ buffer/doorbell, MR/resource pointers, event mask, handler callback, and queue allocation metadata.
- Prototypes cover EQ init/fini/arm, ISR, doorbell posting, overflow handling, and UAR base reset.

## Dependencies And Relationships
Used by command completion, CQ completion/error processing, async IB event processing, and catastrophic error handling. Hardware EQE formats are defined in `hermon_hw.h`.

## Research Notes
The owner-bit logic for EQEs lives in `hermon_hw.h`; this file defines higher-level event categories and the software EQ state that event handlers consume.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_fcoib.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_fcoib.h

## Purpose
Defines Fibre Channel over InfiniBand support state and helper prototypes for FEXCH/RFCI QP and MPT/MTT resource management.

## Main Interfaces
- `hermon_fcoib_qp_t`: FCoIB QP resource plus vmem arena pointer.
- `hermon_fcoib_t`: global FCoIB state including queried limits, lock, shared FEXCH MPT/MTT/QP resources, per-port enable flags, per-port counts, per-port vmem arenas, N_Port IDs, and base indexes for MPT, MTT, FEXCH QPs, and RFCI QPs.
- Prototypes cover source ID mapping, FEXCH base/offset validation, QP number and mkey translation, per-FEXCH MKEY init/fini, relative QPN lookup, and FCoIB init/fini.

## Dependencies And Relationships
Depends on `HERMON_MAX_PORTS`, resource handles, `ibt_fc_attr_t`, and PD handles from the wider driver. Ties into FCoIB command structures and QP/MR functions in `hermon_cmd.h`, `hermon_qp.h`, `hermon_mr.h`, and `hermon_hw.h`.

## Research Notes
This header is small but important for reserved-resource partitioning: FCoIB owns ranges of MPTs, MTTs, FEXCH QPs, and RFCI QPs per port.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_fcoib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_fm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_fm.h

## Purpose
Defines Hermon fault-management support: FMA structures, ereport classifications, device-error message strings, PIO retry/checking macros, test hooks, and FMA-related prototypes.

## Main Interfaces
- `struct i_hca_fm`: shared HCA FM state with refcount, lock, access-handle list, and cache.
- `struct i_hca_acc_handle`: wraps `ddi_acc_handle_t` with a linked-list node, lock, and active PIO thread count.
- `struct i_hca_fm_test`: optional `FMA_TEST` injection metadata.
- Type aliases:
  - `hermon_hca_fm_t`
  - `hermon_acc_handle_t`
  - `hermon_test_t`
- `HERMON_FMANOTE()` emits driver warning messages for likely hardware errors.
- Error strings cover CQE syndromes, EQE errors, HCR failures, firmware version, PCI ID, maintenance mode, and bad NVMEM.
- State flags distinguish PIO, DMA, ereport, callback, attach, and runtime FMA support.
- `hermon_pio_init()`, `hermon_pio_start()`, `hermon_pio_end()` wrap PIO operations with transient/persistent retry logic.

## Dependencies And Relationships
Includes Solaris FMA headers. Used by register mapping, PCI config access, command retry decisions, interrupt error polling, and attach/runtime hardware health paths.

## Research Notes
The PIO macros deliberately expand to a retrying `do { ... } while` pattern and require caller-supplied labels/status variables. This makes call-site control flow part of the interface contract.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_fm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_hw.h

## Purpose
Defines the Hermon hardware ABI: PCI IDs, page/register constants, firmware command register layout, command mailbox structures, endian-specific hardware bitfields, queue/context formats, event/completion entry extraction macros, WQE segment formats/builders, UAR/doorbell layouts, FCoIB/ethernet structures, performance counters, and flash register constants.

## Main Interfaces
- PCI and base hardware constants:
  - Mellanox vendor/device IDs for SDR, DDR, DDR Gen2, QDR Gen2, QDR Gen2V, and maintenance mode.
  - Native 4 KiB page constants.
  - Command BAR offsets for HCR, software reset, and semaphore.
- `struct hermon_hw_hcr_s`: HCA command register fields with masks/shifts for token, status, go, event, toggle, opmod, and opcode.
- Query/init command layouts:
  - `hermon_hw_querydevlim_s`
  - `hermon_hw_queryfw_s`
  - `hermon_hw_queryadapter_s`
  - `hermon_hw_vpm_s`
  - `hermon_hw_initqueryhca_s`
  - helper parameter structures for QP/CQ/EQ/RDB, multicast, TPT, UAR, and QP allocation.
- Port and ethernet configuration:
  - `hermon_hw_query_port_s`
  - `hermon_hw_set_port_s`
  - ethernet set-port variants for general parameters, receive QPN calculation, MAC table, VLAN table, priority table, and GID table.
  - `hermon_hw_conf_int_mod_s`
- Memory and translation:
  - `hermon_hw_dmpt_s`, `hermon_hw_cmpt_s`, `hermon_hw_mtt_s`
  - MPT/MTT ownership, region/window, physical-address, and present flags.
- Event and completion:
  - `hermon_hw_eqc_s`, EQ status/state constants.
  - EQE payload variants for CQ, QP, CQ error, port state, GPIO, command completion, operational error, page fault, and FCoIB error.
  - `hermon_hw_eqe_s` union and extraction macros.
  - `hermon_hw_cqc_s`, CQ status/state constants.
  - `hermon_hw_cqe_s` and extraction macros for QPN, immediate/PKey/credit, DQPN, GRH, path bits, DLID, SL, byte count, WQE counter, error syndrome, opcode, send/receive, checksum/IPoIB status, and FEXCH fields.
- Queue contexts:
  - `hermon_hw_srqc_s`
  - `hermon_hw_mod_stat_cfg_s`
  - `hermon_hw_msg_in_mod_s`
  - `hermon_hw_udav_s`, `hermon_hw_udav_enet_s`
  - `hermon_hw_addr_path_s`
  - `hermon_hw_rss_s`
  - `hermon_hw_qpc_s`
  - QP state/service constants for RC, UC, UD, FCMND, FEXCH, XRC, MLX, and RFCI.
- Multicast/FCoIB/counters:
  - `hermon_hw_mcg_s`, `hermon_hw_mcg_en_s`, `hermon_hw_mcg_qp_list_s`
  - `hermon_hw_set_mcast_fltr_s`
  - `hermon_hw_config_fc_basic_s`
  - `hermon_hw_query_fc_s`
  - `hermon_hw_arm_req_s`
  - `hermon_hw_sm_perfcntr_s`, `hermon_hw_sm_extperfcntr_s`
- UAR, doorbells, and WQEs:
  - `hermon_hw_send_db_reg_t`, `hermon_hw_cq_db_reg_t`, `hermon_hw_guest_eq_ci_t`, `struct hermon_hw_uar_s`
  - `hermon_hw_qp_db_t`, `hermon_hw_cq_db_t`
  - Send, SRQ, FCP3, UD, bind, LSO, remote address, atomic, local invalidate, FRWR, MLX, and SGL segment structures.
  - WQE builder macros for UD, LSO, RDMA remote address, RC atomic, atomic, bind, FRWR, local invalidate, FCP3 init, receive/send data segments, inline segments, control segments, MLX LRH/GRH/BTH/DETH.
- Flash:
  - PCI config offsets, CR-space flash offsets, GPIO/semaphore constants, SPI opcodes/registers, masks, and timeouts.

## Dependencies And Relationships
This is the central hardware contract used by command posting, resource allocation, QP/CQ/EQ/SRQ/MR setup, multicast handling, FCoIB, ioctl flash access, and statistics. Other headers mostly define software handles and prototypes around these hardware structures.

## Research Notes
The file maintains separate little-endian and big-endian bitfield definitions for most hardware mailbox/context structures. Several hot-path macros avoid bitfield writes and instead build network-ordered 32/64-bit chunks with producer memory barriers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_ioctl.h

## Purpose
Defines the Hermon ioctl interface for firmware/flash operations, VTS diagnostics, register access in debug builds, port reporting, loopback testing, and adapter information.

## Main Interfaces
- `hermon_ioctl()` driver entry point prototype.
- Ioctl command base `HERMON_IOCTL` uses the Tavor-compatible `'t' << 8` value for VTS consistency.
- Commands include flash read/write/erase/init/fini, loopback, info, ports, DDR read, boot address write, and debug-only register read/write.
- Flash operation constants for sector/quadlet read, sector/byte write, sector/chip erase.
- Flash defaults and CFI sizing constants, including AMD, Intel, SPI, and unknown command-set identifiers.
- Public ioctl structs:
  - `hermon_fw_info_ioctl_t`
  - `hermon_flash_ioctl_t`
  - `hermon_flash_init_ioctl_t`
  - `hermon_reg_ioctl_t`
  - `hermon_stat_port_ioctl_t`
  - `hermon_ports_ioctl_t`
  - `hermon_loopback_ioctl_t`
  - `hermon_info_ioctl_t`
- `hermon_loopback_error_t`: detailed failure enum for VTS loopback setup, QP transitions, WQE post, CQ poll, and data comparison.

## Dependencies And Relationships
Includes `sys/cred.h`. 32-bit compatibility wrappers and loopback internal state are defined in `hermon_misc.h`. Flash register constants are in `hermon_hw.h`.

## Research Notes
The externally visible structures contain user pointers (`caddr_t`) and revision fields, so ioctl implementations must handle copyin/copyout, model conversion, and version validation carefully.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_misc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_misc.h

## Purpose
Defines miscellaneous Hermon driver support: address handles, multicast, protection domains, queue allocation, doorbell records, user doorbell pages, port limits, kstats, 32-bit ioctl compatibility, loopback test state, Fast Memory Registration pools, and associated prototypes.

## Main Interfaces
- Address handle and multicast defaults:
  - `HERMON_NUM_AH_SHIFT`, `HERMON_UDAV_SIZE_SHIFT`
  - UDAV sync decision macro.
  - address-path type flags for QP vs UDAV formats.
  - multicast group sizing, hash sizing, MGID validation constants, and QP-list pointer macro.
- Protection/domain/port defaults:
  - PD, PKey, GID, UAR, MTU, port width, VL, and counter constants.
- Doorbell support:
  - `hermon_dbr_t`
  - `hermon_dbr_info_t`
  - per-page DBR count and bitmap helpers.
  - user DBR page and management structs.
- Software handles:
  - `struct hermon_sw_ah_s`
  - `struct hermon_sw_mcg_list_s`
  - `struct hermon_sw_pd_s`
  - `struct hermon_qalloc_info_s`
- Kstats:
  - `hermon_ks_mask_t`
  - 64-bit perf counter index enum.
  - `hermon_perfcntr64_ks_info_t`
  - `hermon_ks_info_t`
- 32-bit ioctl compatibility:
  - `hermon_ports_ioctl32_t`
  - `hermon_loopback_ioctl32_t`
  - `hermon_flash_ioctl32_t`
- VTS loopback:
  - `hermon_loopback_comm_t`
  - `hermon_loopback_state_t`
- FMR:
  - `hermon_fmr_list_t`
  - `struct hermon_sw_fmr_s`
  - `HERMON_FMR_MAX_REMAPS`
- Prototypes cover DBR allocation/free, FMR pools, address handles, multicast attach/detach, PD allocation/refcounts, port query/modify, kstat init/fini, address-path translation, validation helpers, and queue allocation/free.

## Dependencies And Relationships
Includes `hermon_typedef.h`, `hermon_ioctl.h`, `hermon_rsrc.h`, and `hermon_hw.h`. This is a broad support header used by CQ, QP, MR, ioctl, statistics, multicast, and port code.

## Research Notes
The file bridges user-facing diagnostics and core IB verbs support. Lock annotations define which handle fields are immutable, lock-protected, or intentionally readable without locks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_mr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_mr.h

## Purpose
Defines Hermon memory region/window support: MPT/MTT sizing defaults, deregistration levels, DMA bind descriptors, memory-region software handles, registration options, allocated-memory handle state, and MR/MW/FMR prototypes.

## Main Interfaces
- Defaults:
  - `HERMON_NUM_DMPT_SHIFT`
  - `HERMON_NUM_MTT_SHIFT`
  - `HERMON_MTT_SIZE_SHIFT`
  - `HERMON_MAX_MEM_MPT_SHIFT`
- Deregistration levels:
  - full deregistration
  - skip HW2SW MPT
  - skip HW2SW MPT and unbind
- `HERMON_MR_REUSE_DMAHDL()` determines when an existing DMA handle may be reused during reregistration.
- `hermon_sw_refcnt_t`: MTT sharing reference counter with helper macros.
- `hermon_bind_info_t`: DMA bind inputs and outputs for vaddr, buf, user buffer, LKey, flags, bypass mode, cookie count, and DMA-handle ownership.
- `struct hermon_sw_mr_s`: software MR/MW handle with lock, MPT/MTT/refcount resources, PD, bind info, access flags, keys, page sizing, MPT type, FMR/user-memory metadata, and unpin callback.
- `hermon_mr_options_t`: optional bind DMA handle, bind type, and virtual-address override policy.
- `struct ibc_mem_alloc_s`: DMA/access handles for CI memory allocation entry points.
- Prototypes cover DMA MR registration, normal/buffer/shared/reregister paths, MTT bind/unbind, deregister/query/sync, MW alloc/free, key calculation, FMR allocation/deallocation/registration, LKey allocation, and FCoIB FEXCH MPT init/fini.

## Dependencies And Relationships
Used by QP/CQ/EQ/SRQ queue memory registration, user memory pinning, FMR, FCoIB, and TPT command posting. Hardware MPT/MTT formats are in `hermon_hw.h`; command submission is declared in `hermon_cmd.h`.

## Research Notes
The header separates dMPT/cMPT ownership policy through `hermon_mpt_rsrc_type_t` and `HERMON_NO_MPT_OWNERSHIP`/`HERMON_PASS_MPT_OWNERSHIP`, reflecting Hermon’s mixed use of hardware-owned and driver-tracked MPT-like contexts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_mr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_qp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_qp.h

## Purpose
Defines Queue Pair defaults, QP number masks, scheduling helpers, service-type validation, WQ sizing types, QP range/QPN tracking, software QP handle state, and QP allocation/modification prototypes.

## Main Interfaces
- Defaults:
  - `HERMON_NUM_QP_SHIFT`
  - `HERMON_NUM_QPS`
  - `HERMON_QP_MIN_SIZE`
  - `HERMON_LOG_NUM_RDB_PER_QP`
  - `HERMON_NUM_SGL_PER_WQE`
  - `HERMON_QP_ACKREQ_FREQ`
  - `HERMON_QP_LOG_MAX_MSGSZ`
- QP masks:
  - `HERMON_QP_MAXNUMBER_MSK`
  - `HERMON_QP_XRC_MSK`
- Special QP and scheduling:
  - `HERMON_QP_SMI`, `HERMON_QP_GSI`
  - default scheduling policy/selection constants.
  - `HERMON_QP_SCHEDQ_GET()`
- `HERMON_QP_TYPE_VALID()` maps IBT transport types to Hermon service types, including FCoIB-related UD services.
- `hermon_qp_wq_type_t`: send/receive/MLX WQ type classification for WQE sizing.
- `hermon_qp_range_t`: resource range with refcount for RSS/FEXCH QPs.
- `hermon_qp_info_t`: allocation input/output carrier.
- `hermon_qpn_entry_t`: AVL-tracked QPN reservation/refcount entry.
- `struct hermon_sw_qp_s`: complete software QP handle with locks, state/type/QPN, PD/MR/CQ handles, special-QP info, UAR/user mapping state, send and receive work queue metadata, doorbell record, resources, handler argument, SQD event flags, SRQ, multicast refcount, saved MTU, QPN handle, queue allocation info, FCoIB attributes, QP range, and cached hardware QPC.
- `HERMON_SET_QP_POST_SEND_STATE()` updates the cached post-send state under the SQ lock.
- Prototypes cover normal/special/range QP allocation, free, query, lookup, QPN release/AVL init/fini, modify, and reset.

## Dependencies And Relationships
Software QP state embeds `struct hermon_hw_qpc_s` from `hermon_hw.h`, uses CQ/MR/PD/SRQ handles, and drives command opmasks from `hermon_cmd.h`. Work request posting code uses the send/receive queue metadata and state cache.

## Research Notes
The QP handle is the densest software handle in this group. Its annotations distinguish immutable setup data, QP-lock state, SQ-lock post-send state, and fields protected by broader sharing schemes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_qp.h -->