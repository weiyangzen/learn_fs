# Research: subset-b-004467

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_controlq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_controlq.c

## Purpose
`ice_controlq.c` implements the Intel ice driver control queue runtime: AdminQ, PF-VF mailbox queue, and the optional sideband queue. These queues are DMA descriptor rings used to exchange synchronous commands and asynchronous receive events with device firmware. The file owns queue register selection, DMA allocation, initialization/shutdown, locking, command submission, receive event cleanup, descriptor debug logging, sideband fallback, and firmware AdminQ API compatibility checks.

## Important APIs, Types, And Functions
The exported entry points are `ice_create_all_ctrlq()`, `ice_init_all_ctrlq()`, `ice_shutdown_all_ctrlq()`, `ice_destroy_all_ctrlq()`, `ice_sq_send_cmd()`, `ice_clean_rq_elem()`, `ice_fill_dflt_direct_cmd_desc()`, `ice_check_sq_alive()`, `ice_is_sbq_supported()`, and `ice_get_sbq()`. They operate on `struct ice_hw` queue members declared through `struct ice_ctl_q_info` and `struct ice_ctl_q_ring` in `ice_controlq.h`.

Internal helpers map queue types to register blocks with `ICE_CQ_INIT_REGS()`, allocate descriptor rings via `dmam_alloc_coherent()`, allocate per-entry DMA buffers for indirect commands/events, program head/tail/length/base registers, and free queue memory through `ICE_FREE_CQ_BUFS()` plus `ice_free_cq_ring()`. `ice_aq_ver_check()` compares firmware AdminQ API versions against `EXP_FW_API_VER_*_BY_MAC()` and blocks newer incompatible major versions. `ice_debug_cq()` provides descriptor and optional payload dumps under dynamic debug or `hw->debug_mask`.

## Control Flow
Driver load calls `ice_create_all_ctrlq()`, which initializes mutexes and then calls `ice_init_all_ctrlq()`. AdminQ is initialized first and validated by `ice_init_check_adminq()`, which sends `ice_aq_get_fw_ver()` and performs the API version check. A critical firmware error causes AdminQ init to be retried up to `ICE_CTL_Q_ADMIN_INIT_TIMEOUT` with `ICE_CTL_Q_ADMIN_INIT_MSEC` sleeps. The sideband queue is initialized only on generic MAC devices; otherwise sideband users fall back to AdminQ via `ice_get_sbq()`. Mailbox queue initialization follows.

Send command flow is centralized in `ice_sq_send_cmd()`: it rejects reset-in-progress, locks `sq_lock`, validates direct/indirect buffer arguments, checks the hardware head, cleans completed descriptors, copies the command onto the next ring descriptor, copies indirect payload into the per-entry DMA buffer, advances `next_to_use`, rings the tail, flushes MMIO writes, polls queue head with `ice_sq_done()`, copies writeback descriptor and optional data back to caller, updates `sq_last_status`, saves an optional writeback descriptor, and returns Linux errno-style status. Receive event flow in `ice_clean_rq_elem()` locks `rq_lock`, compares hardware head against `next_to_clean`, copies descriptor and bounded payload to caller, restores the receive buffer descriptor for reuse, updates tail and ring cursors, and optionally reports pending event count.

## State And Persistence
State is in `hw->adminq`, `hw->mailboxq`, and `hw->sbq`: ring register offsets, DMA addresses, queue depths, buffer sizes, cursors, counts, mutexes, and the last send status. No disk persistence exists. Hardware-visible persistence is limited to queue register programming and firmware-side command effects. Shutdown zeros control queue registers, frees coherent DMA buffers, and marks queue counts as zero. `hw->reset_ongoing` is treated as a soft blocker for new commands.

## Dependencies And Integration Points
The file depends on `ice_common.h`, `ice_adminq_cmd.h`, MMIO helpers (`rd32`, `wr32`, `ice_flush`, `rd32_poll_timeout`), kernel DMA APIs, mutexes, endian helpers, firmware AdminQ opcodes, and libie AQ descriptor definitions. Higher-level modules call `ice_aq_send_cmd()` wrappers, which route through `ice_sq_send_cmd()`; event processing paths consume `ice_clean_rq_elem()` for AdminQ/mailbox events. DCB, DDP, scheduler, resource-lock, mailbox, and reset code all depend on a working AdminQ.

## Risks
The main risks are DMA allocation unwind correctness, command timeouts during firmware critical errors, stale ring cursors after resets, incorrect indirect buffer lengths, and missed receive event recycling. `ice_sq_send_cmd()` returns `-EIO` for many firmware descriptor errors after recording `sq_last_status`, so callers must inspect queue status when they need detailed firmware reason codes. Sideband fallback to AdminQ is intentional but means callers must tolerate different queue routing by MAC type.

## Test Signals
Useful signals include successful probe and AdminQ firmware version reads, no leaked DMA buffers across probe/remove and reset cycles, AQ dynamic debug traces for descriptors and payloads, forced reset paths that shut down and reinitialize queues cleanly, mailbox traffic with VFs, sideband-capable and non-sideband hardware coverage, and negative tests for oversized buffers, invalid direct/indirect argument pairs, full send queues, receive queues with no pending events, and firmware/NVM API mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_controlq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_controlq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_controlq.h

## Purpose
`ice_controlq.h` defines the control queue ABI used by `ice_controlq.c` and all AQ callers. It supplies maximum command buffer sizes, descriptor ring access macros, expected firmware API versions, queue type identifiers, timeout constants, and the per-ring/per-queue state structures used for AdminQ, mailbox, and sideband queues.

## Important APIs, Types, And Functions
The key macros are `ICE_CTL_Q_DESC(R, i)` for descriptor lookup and `ICE_CTL_Q_DESC_UNUSED(R)` for ring space accounting. Expected firmware AdminQ API version macros distinguish E810-compatible and E830-compatible devices through `EXP_FW_API_VER_MAJOR_BY_MAC()` and `EXP_FW_API_VER_MINOR_BY_MAC()`.

`enum ice_ctl_q` names software queue roles: unknown, AdminQ, mailbox, and sideband. `struct ice_ctl_q_ring` holds descriptor DMA memory, per-entry DMA buffer arrays, ring cursor values, queue count, and MMIO register offsets/masks. `struct ice_sq_cd` carries optional send command details, currently only a writeback descriptor pointer. `struct ice_rq_event_info` is the receive-event handoff container. `struct ice_ctl_q_info` aggregates the send and receive rings, configured queue depths and buffer sizes, last send status, and mutexes.

## Control Flow
The header does not implement control flow but shapes it. Initialization code fills `num_*_entries` and `*_buf_size`, then `ice_controlq.c` populates register offsets and DMA fields. Send paths use `ICE_CTL_Q_DESC_UNUSED()` after cleaning to determine space, then index descriptors with `ICE_CTL_Q_DESC()`. Receive paths fill `ice_rq_event_info` before handing events to upper layers.

## State And Persistence
All structures are in-memory driver state mirrored partly into hardware queue registers. The descriptor buffers and per-entry indirect buffers are DMA-coherent memory. The header itself defines no persistent storage, but its queue state must survive runtime command submission until explicit queue shutdown or driver removal.

## Dependencies And Integration Points
It includes `ice_adminq_cmd.h` for `struct libie_aq_desc` and firmware status enums. It is included by queue code and indirectly by most firmware-command modules. The buffer size constants (`ICE_AQ_MAX_BUF_LEN`, `ICE_MBXQ_MAX_BUF_LEN`, `ICE_SBQ_MAX_BUF_LEN`) define limits that callers and queue setup must respect.

## Risks
The descriptor-unused macro assumes consistent ring cursor management and one unused descriptor slot. Incorrect queue depth or buffer size initialization leads to `-EIO` during queue init. Firmware API constants gate device load behavior, so updates to supported NVM/firmware combinations must keep these macros synchronized with firmware compatibility policy.

## Test Signals
Compile coverage across `CONFIG_*` variants, successful AdminQ version validation on E810/E830 families, queue depth boundary tests, indirect buffer-size rejection, and reset/reinit cycles are the best signals that these definitions still match the implementation and firmware contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_controlq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb.c

## Purpose
`ice_dcb.c` is the firmware-facing DCB/DCBX and LLDP MIB implementation. It reads LLDP/DCBX state from firmware, parses IEEE 802.1Qaz, CEE, and DSCP-oriented organizational TLVs into `struct ice_dcbx_cfg`, builds LLDP TLVs from local configuration, starts/stops LLDP and DCBX firmware agents, configures MIB change events, sets PFC mode, and queries port ETS scheduling topology.

## Important APIs, Types, And Functions
Public functions include `ice_aq_get_dcb_cfg()`, `ice_get_dcb_cfg()`, `ice_set_dcb_cfg()`, `ice_get_dcb_cfg_from_mib_change()`, `ice_init_dcb()`, `ice_cfg_lldp_mib_change()`, `ice_aq_stop_lldp()`, `ice_aq_start_lldp()`, `ice_aq_start_stop_dcbx()`, `ice_aq_set_pfc_mode()`, and `ice_query_port_ets()`.

Parser helpers include `ice_lldp_to_dcb_cfg()`, `ice_parse_org_tlv()`, IEEE ETS/PFC/APP parsers, and CEE PG/PFC/APP parsers. Serializer helpers include `ice_dcb_cfg_to_lldp()`, `ice_add_dcb_tlv()`, IEEE TLV builders, and DSCP TLV builders. `ice_cee_to_dcb_cfg()` converts firmware CEE operational responses into the common DCBX model. Port scheduler helpers query ETS through AdminQ and update the software scheduler tree.

## Control Flow
Initialization through `ice_init_dcb()` first checks DCB capability, reads firmware DCBX status from `PRTDCB_GENS`, and either fetches current DCB config when the firmware agent is active/progressing or returns `-EBUSY` when DCBX is disabled. If requested, it enables LLDP MIB change ARQ events; failure switches the QoS state toward software LLDP handling.

Configuration read flow starts with `ice_get_dcb_cfg()`. It attempts the CEE operational AQ command; if present, it fetches desired/local and remote LLDP MIBs and translates CEE operational fields. If CEE is absent (`LIBIE_AQ_RC_ENOENT`), it switches to IEEE mode and parses local/remote LLDP MIBs. LLDP parsing skips the Ethernet header, iterates TLVs until END or `ICE_LLDPDU_SIZE`, dispatches organizational TLVs by OUI, and fills ETS, PFC, app, DSCP map, and mode fields.

Configuration write flow uses `ice_set_dcb_cfg()`: allocate an LLDPDU buffer, choose local MIB flags, serialize the local DCB config into IEEE or DSCP TLVs depending on `pfc_mode`, and call `ice_aq_set_lldp_mib()`. ETS queries go through `ice_query_port_ets()`, which locks `pi->sched_lock`, issues the query, then reconciles root TC nodes with returned TEIDs.

## State And Persistence
Persistent driver state is stored in `pi->qos_cfg`: local, remote, and desired DCBX configs; DCBX status; and `is_sw_lldp`. Firmware persistence is controlled by LLDP start/stop `persist` flags and by setting the local LLDP MIB. PFC mode changes affect firmware hardware behavior. Scheduler tree updates mutate the in-memory port scheduling tree after querying firmware.

## Dependencies And Integration Points
The file depends on AdminQ command descriptors, `ice_common.h`, `ice_sched.h`, LLDP/DCBX constants from `ice_dcb.h`, endian and bitfield helpers, device-managed allocation, and scheduler-tree helpers. It integrates with the ARQ event path via `ice_get_dcb_cfg_from_mib_change()`, with DCB runtime policy in `ice_dcb_lib.c`, and with DCBNL userspace control through `ice_set_dcb_cfg()`/`ice_get_dcb_cfg()`.

## Risks
Risks concentrate around TLV bounds and format assumptions: APP TLV count truncation, CEE sub-TLV traversal, LLDPDU offset accounting, and DSCP TLV fixed lengths. CEE conversion has special handling for strict priority, FCoE/iSCSI/FIP, and iSCSI port variants; regressions can silently mis-advertise application priorities. `ice_aq_set_pfc_mode()` must verify firmware wrote back the requested mode because disabled DCB can cause firmware to echo zero.

## Test Signals
Test with firmware LLDP enabled and disabled, IEEE and CEE peer configurations, absent remote MIBs, DSCP mode, VLAN mode, pending MIB events, PFC mode changes, and reset/rebuild paths. Packet-level LLDP fixtures for ETS/PFC/APP/DSCP TLVs, scheduler TEID reconciliation checks, and AQ fault injection for `ENOENT`, `EIO`, invalid buffer sizes, and unsupported DCB capability are strong coverage points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb.h

## Purpose
`ice_dcb.h` defines the wire-format constants, packed TLV structures, DCBX status values, and public firmware-facing DCB APIs used by the ice DCB implementation. It is the shared contract for parsing/building IEEE 802.1Qaz, CEE DCBX, and Intel DSCP organizational TLVs.

## Important APIs, Types, And Functions
The header defines DCBX status constants (`ICE_DCBX_STATUS_*`), LLDP TLV type/length masks, IEEE OUI/subtype constants for ETS/PFC/APP, CEE OUI/subtypes, DSCP OUI/subtypes, TLV IDs and fixed lengths, and bit masks for ETS/PFC/app fields. Packed wire structures include `struct ice_lldp_org_tlv`, `struct ice_cee_tlv_hdr`, `struct ice_cee_ctrl_tlv`, `struct ice_cee_feat_tlv`, and `struct ice_cee_app_prio`.

Function declarations expose firmware control and configuration entry points: `ice_aq_set_pfc_mode()`, `ice_aq_get_dcb_cfg()`, `ice_get_dcb_cfg()`, `ice_set_dcb_cfg()`, `ice_get_dcb_cfg_from_mib_change()`, `ice_init_dcb()`, `ice_query_port_ets()`, LLDP start/stop, DCBX start/stop, and MIB change configuration. When `CONFIG_DCB` is disabled, LLDP/DCBX control functions are stubbed to no-op success or inactive status.

## Control Flow
The constants in this header drive parser switch statements and serializer TLV selection in `ice_dcb.c`. The `CONFIG_DCB` split also changes call behavior: core driver paths can call LLDP/DCBX helpers unconditionally while builds without DCB avoid firmware side effects for those optional controls.

## State And Persistence
This file defines no state itself. Its packed structures describe data as it appears in LLDP MIBs and CEE AQ responses. Persistent behavior is indirect: `persist` flags in declared LLDP functions and MIB serialization constants influence firmware state across reboot when callers request it.

## Dependencies And Integration Points
It includes `ice_type.h` for core device/DCB structures and `<scsi/iscsi_proto.h>` for iSCSI protocol constants used by CEE app translation. It is consumed by `ice_dcb.c`, `ice_dcb_lib.c`, `ice_dcb_nl.c`, and any code handling LLDP MIB-change events.

## Risks
The masks and fixed lengths must match firmware and standards exactly. Because structures are packed and parsed from firmware/network buffers, incorrect field sizes or endian handling can corrupt parsed DCB config. `CONFIG_DCB` stubs returning success can hide missing feature support if callers assume an action actually reached firmware.

## Test Signals
Build tests with and without `CONFIG_DCB`, parser fixture coverage for each OUI/subtype, static assertions or review against firmware specs for TLV lengths, and runtime DCB init on devices advertising different DCBX statuses are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_lib.c

## Purpose
`ice_dcb_lib.c` applies DCB configuration to the Linux-facing driver runtime. It converts DCBX config into enabled traffic classes, configures VSIs and rings, validates bandwidth, handles DCB reset/rebuild, updates DCB statistics, diagnoses PFC-induced Tx hangs, prepares VLAN priority tags, exports QoS info to auxiliary RDMA drivers, and processes LLDP MIB-change events from firmware.

## Important APIs, Types, And Functions
Important public functions are `ice_init_pf_dcb()`, `ice_pf_dcb_cfg()`, `ice_pf_dcb_recfg()`, `ice_dcb_rebuild()`, `ice_dcb_sw_dflt_cfg()`, `ice_dcb_get_num_tc()`, `ice_vsi_set_dcb_tc_cfg()`, `ice_vsi_cfg_dcb_rings()`, `ice_dcb_bwchk()`, `ice_update_dcb_stats()`, `ice_tx_prepare_vlan_flags_dcb()`, `ice_setup_dcb_qos_info()`, `ice_is_pfc_causing_hung_q()`, and `ice_dcb_process_lldp_set_mib_change()`.

Key internal helpers compute enabled TC maps, host/managed DCBX mode, first drop TC, TC contiguity, ETS recommended defaults, whether reconfiguration is needed, and temporary VSI disable/enable across TC changes.

## Control Flow
`ice_init_pf_dcb()` calls `ice_init_dcb()`. If firmware LLDP is disabled, it switches to software DCBX/LLDP mode, sets VLAN PFC mode, installs a default software DCB config, enables software LLDP packet handling, and advertises HOST DCBX capability. If firmware LLDP is active, it marks FW LLDP, advertises managed DCBX mode, and applies the initial firmware config through `ice_dcb_init_cfg()`.

`ice_pf_dcb_cfg()` is the main apply path. It toggles `ICE_FLAG_DCB_ENA` based on TC count, blocks DCB if custom Tx scheduler is active, tears down devlink rate tree when needed, compares configs, validates bandwidth, stores old config for rollback, notifies auxiliary RDMA before TC changes, takes RTNL if needed, disables affected VSIs, copies the new config into local state, writes firmware MIB in software LLDP mode, queries port ETS, reconfigures PF/CHNL VSIs, re-enables VSIs, and frees rollback state.

`ice_dcb_process_lldp_set_mib_change()` handles ARQ MIB-change events. It ignores non-DCB-capable or HOST-mode events, filters for nearest bridge, distinguishes pending versus already-applied changes, updates remote-only MIBs cheaply, locks `tc_mutex` for local changes, refreshes local config from event or firmware, flushes removed DCBNL apps, executes pending MIB changes, disables/reconfigures/enables VSIs under RTNL, and ensures pending events are executed even when no full reconfig is needed.

## State And Persistence
The file mutates PF flags (`ICE_FLAG_DCB_ENA`, `ICE_FLAG_FW_LLDP_AGENT`), `pf->dcbx_cap`, `port_info->qos_cfg`, `vsi->tc_cfg`, ring `dcb_tc`, PF DCB statistics, RDMA QoS exports, and scheduler-derived TC state. Persistence beyond memory is through `ice_set_dcb_cfg()` when software LLDP mode commits local MIBs to firmware.

## Dependencies And Integration Points
It depends on `ice_dcb.c` firmware APIs, DCBNL helpers, devlink rate-tree teardown, VSI enable/disable/configuration, RDMA auxiliary event interfaces, scheduler query/update, Tx/Rx ring structures, VLAN tag flags, and hardware stats registers. It is central to interactions among firmware DCB, Linux DCBNL, netdev reset, ADQ/channel VSIs, and RDMA QoS.

## Risks
DCB changes are disruptive: VSIs are brought down/up and auxiliary drivers must be notified in order. Rollback only restores local config if firmware set fails; later failures can still leave partially updated software state. Non-contiguous TC mappings trigger fallback software defaults. DSCP and VLAN QoS modes have different invariants. Lock ordering among `tc_mutex`, RTNL, scheduler lock, and auxiliary notifications is important. PFC hang detection depends on counters changing between two reads and can produce false negatives if sampling misses increments.

## Test Signals
Exercise FW LLDP and SW LLDP initialization, DCB config changes with multiple TCs, rollback on firmware MIB failure, reset rebuild, MIB pending event handling, remote-only MIB updates, VSI reconfiguration for PF and channel VSIs, RDMA before/after notifications, DCB stats reads, Tx VLAN priority insertion, PFC storm diagnosis, non-contiguous TC fallback, and custom Tx scheduler conflict rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_lib.h

## Purpose
`ice_dcb_lib.h` exposes the runtime DCB helper API to the rest of the ice driver and provides no-op or conservative fallbacks when `CONFIG_DCB` is disabled. It bridges core PF/VSI/ring code with the DCB library implementation.

## Important APIs, Types, And Functions
With `CONFIG_DCB`, it defines DCB return/status constants (`ICE_DCB_HW_CHG_RST`, `ICE_DCB_NO_HW_CHG`, `ICE_DCB_HW_CHG`) and declares the DCB runtime functions for initialization, config apply, rebuild, VSI/ring TC setup, stats update, PFC hang diagnosis, VLAN priority preparation, RDMA QoS export, and LLDP MIB-change processing. Inline helpers include `ice_find_q_in_range()`, `ice_set_cgd_num()`, `ice_is_dcb_active()`, and `ice_get_pfc_mode()`.

Without `CONFIG_DCB`, it returns one traffic class, marks DCB inactive, rejects PF DCB initialization/configuration with `-EOPNOTSUPP`, sets default RDMA QoS to one TC at 100 percent bandwidth, and makes stats/reconfig/MIB handlers no-ops.

## Control Flow
The header lets core paths call DCB helpers regardless of build option. The compile-time branch determines whether those calls perform real DCB work or collapse to default single-TC behavior. `ice_is_dcb_active()` abstracts whether firmware LLDP or DCB tagging currently makes DCB operational.

## State And Persistence
No persistent state is stored in the header. Inline helpers read or set fields in caller-owned structures: `tlan_ctx->cgd_num`, PF flags, and `local_dcbx_cfg.pfc_mode`. Fallbacks set transient VSI/RDMA QoS defaults.

## Dependencies And Integration Points
It includes `ice.h`, `ice_base.h`, and `ice_lib.h`, so it is tightly coupled to PF, VSI, Tx context, ring, and IIDC RDMA types. It is consumed by transmit setup, VSI configuration, reset, DCBNL, and event-processing code.

## Risks
The non-DCB stubs must preserve core driver behavior without silently advertising unavailable DCB features. One signature inconsistency is worth watching: the non-DCB `ice_tx_prepare_vlan_flags_dcb()` stub is declared `int` while the real function returns `void`; build coverage likely catches this depending on call sites and compiler diagnostics. Inline state readers assume `pf->hw.port_info` exists.

## Test Signals
Build both `CONFIG_DCB=y` and disabled variants, run sparse/compile checks for prototype consistency, validate single-TC fallback behavior, and verify callers do not rely on side effects from stubbed functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_nl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_nl.c

## Purpose
`ice_dcb_nl.c` implements Linux DCBNL operations for the ice driver. It maps userspace DCB requests and notifications to the driver's DCBX config model, supporting IEEE ETS/PFC, CEE state/PG/PFC/app interfaces, DCBX mode changes, DSCP APP mapping, and synchronization of firmware-learned APP TLVs to netdev DCB state.

## Important APIs, Types, And Functions
The main public entry points are `ice_dcbnl_setup()`, `ice_dcbnl_set_all()`, and `ice_dcbnl_flush_apps()`. Static DCBNL callbacks populate `struct dcbnl_rtnl_ops`: IEEE `getets/setets`, `getpfc/setpfc`, `setapp/delapp`; CEE state, PG, PFC, capability, app, and set-all operations; and DCBX get/set mode operations.

Key helpers include `ice_dcbnl_devreset()` for down/up resync after hardware-changing DCB updates, `ice_dcbnl_find_app()` to compare APP tables, and `ice_dcbnl_vsi_del_app()` to remove stale apps. DSCP app handling in `ice_dcbnl_setapp()` and `ice_dcbnl_delapp()` is the most stateful userspace path.

## Control Flow
`ice_dcbnl_setup()` attaches DCBNL ops to the VSI netdev only when the PF is DCB-capable, then seeds netdev app state via `ice_dcbnl_set_all()`. Getter callbacks copy local DCBX state and stats into kernel DCBNL structures. Setter callbacks generally reject changes when firmware LLDP/LLD-managed mode owns DCBX, when the requested standard is unsupported, or when the PF is bonded. Accepted changes update `desired_dcbx_cfg`, call `ice_pf_dcb_cfg()` under `tc_mutex`, and may reset the netdev if a hardware-changing update requires it.

DSCP APP setup only accepts `IEEE_8021QAZ_APP_SEL_DSCP`, requires HOST IEEE mode and feature support, validates DSCP and TC ranges, records the app through DCB core helpers, switches firmware PFC mode from VLAN to DSCP if needed, initializes default DSCP maps, applies the requested mapping, appends it to `desired_dcbx_cfg.app`, and commits through `ice_pf_dcb_cfg()`. Deleting the last DSCP mapping switches back to VLAN mode and default software DCB config.

## State And Persistence
The file mutates `pf->dcbx_cap`, `desired_dcbx_cfg`, `local_dcbx_cfg` through apply paths, `dscp_mapped` bitmap, DSCP map arrays, PFC config, ETS tables, and netdev DCB app state maintained by the kernel DCB subsystem. Firmware persistence is indirect via `ice_pf_dcb_cfg()` and `ice_set_dcb_cfg()`.

## Dependencies And Integration Points
It depends on `<net/dcbnl.h>`, `ice_dcb.h`, `ice_dcb_lib.h`, netdev open/close/state change APIs, bonding state (`pf->lag->bonded`), DCB app helpers (`dcb_ieee_setapp`, `dcb_ieee_delapp`, `dcb_getapp`), feature flags, and DCBNL notifications. It integrates userspace tools such as lldpad/iproute2 with firmware DCB and driver runtime reconfiguration.

## Risks
Mode gating is critical: allowing userspace changes while firmware LLDP manages DCBX would fight firmware state. DSCP mode has non-negotiated behavior and must not be mixed with unsupported app selectors. APP deletion shifts entries using `old_cfg` data after clearing `new_cfg`, which should be reviewed carefully for consistency. Several CEE setters update desired state without immediately committing until `setall`; userspace ordering matters. Netdev reset waits for reset-in-progress loops, so long resets can delay DCBNL calls.

## Test Signals
Run DCBNL userspace tests for IEEE ETS/PFC set/get, CEE set-all, DCBX mode changes, DSCP add/delete including last mapping, bonded PF rejection, firmware-managed rejection, unsupported selector rejection, netdev reset after hardware-changing updates, app notification after firmware MIB changes, and DCB-disabled build stubs through `ice_dcb_nl.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_nl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_nl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_nl.h

## Purpose
`ice_dcb_nl.h` declares the DCBNL integration surface for the ice driver and supplies empty fallbacks for non-DCB builds. It lets VSI setup, DCB reconfiguration, and MIB-change handling synchronize netdev DCB state without conditional call sites everywhere.

## Important APIs, Types, And Functions
With `CONFIG_DCB`, it declares `ice_dcbnl_setup()`, `ice_dcbnl_set_all()`, and `ice_dcbnl_flush_apps()`. Without DCB, all three are static inline no-ops. The declarations operate on `struct ice_vsi`, `struct ice_pf`, and `struct ice_dcbx_cfg` types from the broader ice headers.

## Control Flow
`ice_dcbnl_setup()` is expected during netdev/VSI setup to attach DCBNL ops. `ice_dcbnl_set_all()` is called after TC reconfiguration to publish APP state. `ice_dcbnl_flush_apps()` is used when DCBX config changes remove APP TLVs. In non-DCB builds, all flows intentionally do nothing.

## State And Persistence
The header stores no state. Real implementations mutate netdev DCBNL ops and DCB app tables; stubs leave netdev state unchanged.

## Dependencies And Integration Points
It is included by `ice_dcb_lib.c` and other VSI/DCB setup code. It bridges the DCB runtime library with Linux DCBNL when enabled.

## Risks
The main risk is silent no-op behavior in non-DCB builds if a caller expects userspace DCB state to exist. The header also relies on included upstream headers providing forward declarations or full definitions of PF/VSI/DCBX structures.

## Test Signals
Build coverage with `CONFIG_DCB` enabled and disabled, netdev setup verification that `dcbnl_ops` is assigned only when capable, and MIB-change tests confirming app flush/set operations run only in DCB-capable builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_nl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ddp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ddp.c

## Purpose
`ice_ddp.c` implements Dynamic Device Personalization package handling. It validates package files, discovers the device-specific package segment and signing requirements, downloads package buffers to firmware under the global config lock, caches parser and tunnel metadata from package labels/sections, exposes package-buffer construction/update helpers, enumerates package sections and field vectors, derives switch profile metadata, and optionally applies Tx scheduler topology from runtime config segments.

## Important APIs, Types, And Functions
Public entry points include `ice_init_pkg()`, `ice_copy_and_init_pkg()`, `ice_free_seg()`, `ice_is_init_pkg_successful()`, `ice_pkg_enum_section()`, `ice_pkg_enum_entry()`, `ice_get_sw_fv_bitmap()`, `ice_get_sw_fv_list()`, `ice_init_prof_result_bm()`, `ice_pkg_buf_alloc()`, `ice_pkg_buf_free()`, `ice_pkg_buf_reserve_section()`, `ice_pkg_buf_alloc_section()`, `ice_pkg_buf_alloc_single_section()`, `ice_pkg_buf_get_active_sections()`, `ice_pkg_buf()`, `ice_update_pkg_no_lock()`, `ice_update_pkg()`, `ice_aq_upload_section()`, and `ice_cfg_tx_topo()`.

Major internal helpers validate package and buffer bounds, enumerate buffers/sections/entries, find segments, map AQ errors to DDP states, acquire/release global package locks, send signed/config package hunks, inspect active firmware package info, scan labels for tunnel and DVM/SVM hints, fill enabled PTYPE bitmaps, and classify switch field-vector profiles as tunnel/non-tunnel types.

## Control Flow
`ice_init_pkg()` verifies package format and segment bounds, extracts metadata through `ice_init_pkg_info()`, checks signing segment requirements for the MAC type, validates package version and NVM compatibility through `ice_chk_pkg_compat()`, scans hints, downloads the package, retrieves active package info, maps already-loaded cases to specific states, and on success sets `hw->seg`, initializes package-related registers, fills block tables, fills hardware PTYPE bitmap, and records the max used switch profile index.

Download flow differs by signed package support. Signed packages search signing segments matching `hw->pkg_seg_id` and `hw->pkg_sign_type`, download signature buffers, then the referenced config buffer range, and set the "last" bit according to signing segment flags. Unsigned packages download the config segment's buffer table directly. Both paths skip metadata buffers, use AdminQ download package commands, retry security/signature-related failures briefly, and call VLAN-mode post-download actions. Global config locking prevents multiple PFs from downloading conflicting packages; `-EALREADY` is treated as an already-loaded package condition.

Section enumeration is stateful: callers start with an `ice_seg`, then pass `NULL` to continue. Section and entry helpers validate section count, `data_end`, offsets, sizes, and handler-specific counts before returning package pointers. Tx topology flow validates firmware support and current flags, verifies runtime config package structure, extracts a 5-layer topology section when needed, acquires the global config lock, sends topology through AdminQ, triggers CORE reset, and reinitializes hardware.

## State And Persistence
The file mutates `struct ice_hw` package state: package versions/names, active package info, package copy pointer and size, `hw->seg`, signing identifiers, tunnel hint tables, DVM update tables, switch profile result bitmaps, hardware PTYPE bitmap, block tables, and scheduler topology. Firmware-visible persistence includes downloaded package state, package updates, VLAN mode configuration, and Tx topology changes that require CORE reset. `ice_copy_and_init_pkg()` owns a device-managed package copy until `ice_free_seg()`.

## Dependencies And Integration Points
It depends on AdminQ package opcodes, resource locks (`ICE_GLOBAL_CFG_LOCK_RES_ID`, change lock), `ice_common.h`, `ice_sched.h`, package structures from `ice_ddp.h`, parser/switch block table code (`ice_fill_blk_tbls()`), VLAN mode helpers, reset/deinit/init hardware paths, bitmap/list APIs, and device-managed allocation. Flow director, switch recipe, tunnel, VLAN, and scheduler code consume the package-derived field vectors, labels, PTYPEs, and result bitmaps.

## Risks
DDP package parsing is binary and bounds-sensitive; every segment, buffer, section, and handler count must remain validated before pointer arithmetic. Multi-PF races require correct global lock handling and already-loaded interpretation. Signed package behavior depends on matching segment ID and signing type by MAC family. Package load may succeed with a compatible but different package already active, which callers must distinguish. Tx topology update is disruptive because it issues CORE reset and reinitializes hardware. Metadata buffers intentionally terminate download sequences; mishandling this can send invalid data to firmware.

## Test Signals
Use package fixtures for invalid format versions, truncated segment arrays, bad section offsets/sizes, unsupported package versions, NVM mismatch, missing metadata, signed and unsigned packages, metadata-buffer termination, already-loaded package states, AQ security/signature failures, tunnel/DVM/SVM label scanning, switch field-vector lookup, package update/upload helpers, and Tx topology transitions including already-applied, lock contention, reset-in-progress, and hardware reinit failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ddp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ddp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ddp.h

## Purpose
`ice_ddp.h` defines the binary package layout, section IDs, package state enum, parser table structures, buffer-builder structures, and exported DDP helper prototypes for `ice_ddp.c` and package-consuming flow/switch code.

## Important APIs, Types, And Functions
Version constants define supported package major/minor (`1.3`) and package format (`1.0.0.0`). `enum ice_ddp_state` provides success, already-loaded variants, firmware mismatch, invalid file, unsupported version, signature/revision, load, and generic errors. Package structures describe headers (`ice_pkg_hdr`, `ice_generic_seg_hdr`), ICE device segments, NVM tables, 4 KiB package buffers, runtime config segments, signing segments, section entries, metadata, labels, field vectors, boost TCAM entries, marker PTYPE TCAM entries, XLT sections, and profile redirection sections.

The header declares package upload/update, buffer allocation/building, section/entry enumeration, and Tx topology configuration APIs. `struct ice_pkg_enum` captures enumeration state; `struct ice_buf_build` wraps a mutable package buffer plus reserved section-entry count.

## Control Flow
The structures support two principal flows. First, package initialization validates and enumerates immutable package content using segment, buffer table, section, label, field-vector, and TCAM structures. Second, runtime updates allocate a new `ice_buf_build`, reserve section entries, allocate section payload space, then send built buffers through update-package AdminQ commands.

## State And Persistence
The header defines in-memory views of firmware package content. Package contents are little-endian and frequently point directly into package memory retained by `hw->seg`/`hw->pkg_copy`. Persistent firmware effects occur when buffers matching these structures are downloaded or updated through AdminQ.

## Dependencies And Integration Points
It includes `ice_type.h` for package version/name and hardware-facing types. Section IDs are shared with switch, ACL, FD, RSS, parser, label, and Tx topology code. Field-vector structures and profile IDs are consumed by switch recipe/profile lookup code.

## Risks
This header encodes binary layout contracts; changing packing, constants, section IDs, or min/max bounds can break package compatibility. Flexible-array structures require strict size checks before access. All package contents must be interpreted little-endian. The broad section ID namespace makes accidental ID reuse risky.

## Test Signals
Compile-time structure layout review, package fixture parsing, endian-sensitive tests, section builder tests for alignment and capacity, enumeration tests across multiple buffers/sections, and compatibility tests against E810/E830/E825 package variants are appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ddp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_debugfs.c

## Purpose
`ice_debugfs.c` provides minimal debugfs directory lifecycle support for the ice driver. It creates a module-level debugfs root and per-PF subdirectories named by PCI device name, and removes them during PF teardown or module exit.

## Important APIs, Types, And Functions
The file has one static global, `ice_debugfs_root`. Public functions are `ice_debugfs_init()`, `ice_debugfs_exit()`, `ice_debugfs_pf_init()`, and `ice_debugfs_pf_deinit()`. Per-PF state is stored in `pf->ice_debugfs_pf`.

## Control Flow
Module/driver initialization calls `ice_debugfs_init()`, which creates `/sys/kernel/debug/<module-name>`. PF initialization calls `ice_debugfs_pf_init()`, which creates a child directory using `pci_name(pf->pdev)`. PF deinit removes the PF subtree recursively and nulls the pointer. Module exit removes the root recursively and clears the global pointer.

## State And Persistence
Debugfs entries are runtime-only kernel debug state. They are not persistent across module unload or reboot. The only retained state is the root dentry and per-PF dentry pointer.

## Dependencies And Integration Points
It depends on `<linux/debugfs.h>`, `ice.h`, PF PCI device state, `KBUILD_MODNAME`, and kernel debugfs APIs. Other ice debugfs files can add files below the per-PF directory after `ice_debugfs_pf_init()` succeeds.

## Risks
`debugfs_create_dir()` may return an error pointer, which this file handles for PF init and logs for root init. If root creation fails but PF init is still called, behavior depends on debugfs accepting an error/NULL parent; callers should order and gate setup carefully. Recursive removal must be paired with pointer nulling to avoid stale dentries.

## Test Signals
Probe/remove cycles with debugfs enabled, root creation failure injection if available, multiple PFs creating unique PCI-name directories, module unload cleanup, and checking that no debugfs dentries remain after PF removal are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_devids.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_devids.h

## Purpose
`ice_devids.h` centralizes PCI device and subdevice IDs for Intel Ethernet Controller/Connection families supported by the ice driver subset: E810, E822, E823, E825, E830, and E835 variants across backplane, QSFP, SFP, SFP-DD, 10GBASE-T, SGMII, and related subdevice identifiers.

## Important APIs, Types, And Functions
The file contains preprocessor constants only. Examples include `ICE_DEV_ID_E810C_BACKPLANE`, `ICE_DEV_ID_E810C_QSFP`, `ICE_DEV_ID_E823L_*`, `ICE_DEV_ID_E822C_*`, `ICE_DEV_ID_E830*`, `ICE_DEV_ID_E835*`, `ICE_DEV_ID_E825C_*`, and E810T subdevice IDs. There are no functions or structures.

## Control Flow
The header participates in control flow indirectly through PCI ID tables and device-family detection in other driver files. Matching a PCI ID selects the ice driver and can influence MAC type, feature capability setup, package signing requirements, firmware API expectations, and media-specific behavior elsewhere.

## State And Persistence
No runtime state or persistence is defined. These constants are compile-time identifiers used to match hardware.

## Dependencies And Integration Points
It is included by PCI registration and hardware identification code. It integrates with Linux PCI device tables and any switch statements or lookup tables mapping device IDs to capabilities.

## Risks
Incorrect IDs can cause unsupported devices to bind, supported devices to fail probe, or devices to be assigned wrong capabilities. Adding new hardware requires keeping this header synchronized with PCI ID tables, MAC type selection, DDP segment/signature expectations, and firmware compatibility logic.

## Test Signals
Compile checks for PCI tables, hardware probe on each listed family/media variant, lspci ID matching, negative testing for unsupported IDs, and review against Intel device ID documentation or upstream driver tables are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_devids.h -->
