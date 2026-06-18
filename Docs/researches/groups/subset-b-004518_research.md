# Research: subset-b-004518

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_common.h

## Purpose
`otx2_common.h` is the central contract for the OcteonTX2/CN10K/CN20K RVU NIC driver. It defines the PF/VF shared state model, hardware capability flags, mailbox wrapper, queue/resource accounting, MCAM flow bookkeeping, PTP state, MACsec/IPsec hooks, DCB/PFC fields, and the exported intra-driver APIs used by PF, VF, ethtool, devlink, flow, QoS, XDP, and timestamp code.

## Important APIs, Types, And Functions
Key state types are `struct otx2_nic`, `struct otx2_hw`, `struct mbox`, `struct otx2_flow_config`, `struct otx2_ptp`, `struct otx2_vf_config`, `struct otx2_tc_flow`, and `struct dev_hw_ops`. `struct otx2_nic` is the long-lived per-netdev anchor: it owns BAR mappings, mailbox instances, workqueues, NIX/NPA queue state, feature flags, PTP, devlink, SR-IOV VF configuration, QoS, representor, MACsec, IPsec, and AF_XDP state. `struct otx2_hw` tracks resource counts, scheduler queues, RSS, MSI-X offsets, stats, LMTST support, and silicon capability bits.

Inline helpers provide device classification (`is_dev_otx2`, `is_dev_cn10kb`, `is_cn20k` via included headers), capability setup (`otx2_setup_dev_hw_settings`), register routing (`otx2_get_regaddr`, `otx2_read64`, `otx2_write64`), mailbox sending (`otx2_sync_mbox_msg`, `otx2_sync_mbox_up_msg`, busy polling), DMA mapping wrappers, aura alloc/free paths, queue selection helpers (`otx2_get_smq_idx`, `otx2_get_total_tx_queues`), and rate conversion. The `MBOX_MESSAGES` macro expansion creates typed `otx2_mbox_alloc_msg_*` request allocators.

## Control Flow And Integration
Most driver files include this header and operate on `struct otx2_nic`. The control path generally allocates a typed mailbox request with the generated helpers, fills hardware-specific fields, calls one of the sync helpers under `mbox.lock`, then updates in-memory flags or arrays after AF/CGX/NPC confirmation. Register accesses go through `otx2_get_regaddr`, which translates logical NIX/NPA/CPT offsets into the device's actual block address before dereferencing `reg_base`.

## State And Persistence
State is kernel-resident and device-scoped, not persistent across module unload or reprobe. Important state includes `flags`, queue counts, RSS key/indirection table, scheduler lists, MCAM entry arrays, PFC scheduler maps, VF MAC/VLAN/trust settings, timestamp config, and stats. Some state mirrors hardware and must be restored on open or reset, for example timestamp enable flags, DMAC filters, RSS setup, PFC queues, and QoS scheduler configuration.

## Dependencies
The header depends on Linux networking, PCI, PTP, DIM, page-pool, devlink, MACsec, TC, and Marvell RVU headers such as `mbox.h`, `npc.h`, `rvu.h`, `rvu_trace.h`, `qos.h`, `rep.h`, `cn10k_ipsec.h`, and `cn20k.h`. Hardware register constants come from `otx2_reg.h`; queue structures come from `otx2_txrx.h`.

## Risks
The header centralizes many cross-module invariants. Incorrect queue counts can corrupt array indexing across RQ/SQ/CQ, QoS, XDP, and PFC code. Mailbox bounce-buffer copying must clamp message size correctly because it copies from shared hardware memory. `otx2_atomic64_add` is architecture-specific and returns `0` on non-ARM64 builds, so register operations using it are meaningful only for supported build targets. Feature flags are bitfields with many runtime interactions, so reset/open paths must restore hardware state whenever a flag says a feature remains enabled.

## Test Signals
Useful signals include successful PF/VF probe, AF mailbox ready response, stable interface open/close cycles, correct queue counts in ethtool, RSS table programming, ntuple rule add/delete, DCB/PFC scheduler allocation when enabled, PTP clock registration, XDP attach/detach, and absence of NIX/NPA queue interrupt errors during traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_dcbnl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_dcbnl.c

## Purpose
`otx2_dcbnl.c` implements IEEE DCBNL Priority Flow Control support for PF devices when `CONFIG_DCB` is enabled. It exposes DCB operations to the networking stack, configures CGX/RPM PFC pause behavior through AF mailbox messages, allocates per-priority transmit scheduler queues, remaps SQ contexts to PFC scheduler queues, and maps receive queues to per-priority backpressure IDs.

## Important APIs And Functions
Public driver entry points are `otx2_dcbnl_set_ops`, `otx2_config_priority_flow_ctrl`, `otx2_update_bpid_in_rqctx`, `otx2_pfc_txschq_alloc`, `otx2_pfc_txschq_config`, `otx2_pfc_txschq_update`, and `otx2_pfc_txschq_stop`. The DCBNL callbacks are `otx2_dcbnl_ieee_getpfc`, `otx2_dcbnl_ieee_setpfc`, `otx2_dcbnl_getdcbx`, and `otx2_dcbnl_setdcbx`.

`otx2_check_pfc_config` prevents enabling a priority that has no corresponding TX queue. `otx2_pfc_txschq_alloc_one` requests one scheduler queue per level up to `txschq_link_cfg_lvl`, records those queue IDs in `pfc_schq_list`, and marks `pfc_alloc_status[prio]`. `otx2_pfc_update_sq_smq_mapping` updates SQ admin-queue context so the priority queue maps to the correct SMQ, using the CN10K AQ message shape when `CN10K_LMTST` is set.

## Control Flow
An administrator writes PFC config through DCBNL. `otx2_dcbnl_ieee_setpfc` stores the old bitmap, validates queue coverage, asks CGX/RPM to set PFC pause state, disables NIX-CPT backpressure by default, enables NIX backpressure when any PFC bit is set, and calls `otx2_pfc_txschq_update`. The update path walks all eight priorities, freeing scheduler queues for disabled priorities after flushing their SMQ, allocating missing queues for newly enabled priorities, updating SQ-to-SMQ mappings, and finally configuring schedulers.

## State And Persistence
State lives in `pfvf->pfc_en`, `queue_to_pfc_map`, `pfc_schq_list`, `pfc_alloc_status`, and `bpid[]`. It is runtime state and is restored during hardware resource initialization if `pfc_en` remains set. No on-disk persistence exists.

## Dependencies And Integration
This file depends on `otx2_common.h`, mailbox message definitions for CGX PFC, NIX/NPA AQ context writes, scheduler allocation/free helpers, `net/dcbnl` callbacks, and netdev queue stop/start APIs. It integrates with `otx2_get_smq_idx` in the shared header, `otx2_open` resource setup, ethtool channel changes, and ntuple VLAN rules that may invoke `otx2_update_bpid_in_rqctx`.

## Risks
PFC is sensitive to queue topology. Enabling a priority without a TX queue is rejected, but queue count changes after PFC configuration remain a risk area. Some mailbox return values in SQ/NPA update helpers are not deeply inspected after `otx2_sync_mbox_msg`. The path temporarily stops queues and carrier, so failures must leave queues restarted. `queue_to_pfc_map[qidx]` uses zero as both default and possible priority zero, making priority-zero mapping semantics worth testing.

## Test Signals
Exercise `dcb pfc set/get`, enabling priorities 0 through 7 with varying TX queue counts. Confirm AF mailbox success, scheduler IDs allocated and freed, SQ contexts remapped, no queue stalls during traffic, and expected pause behavior under congestion. Test rollback by forcing mailbox failures and by disabling PFC while traffic runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_dcbnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_devlink.c

## Purpose
`otx2_devlink.c` registers devlink support for OcteonTX2 PF/VF netdevs. It exposes runtime parameters for MCAM ntuple entry count and unicast filter count, and optionally exposes eswitch mode switching when representor/eswitch support is compiled in.

## Important APIs And Functions
The exported lifecycle functions are `otx2_register_dl` and `otx2_unregister_dl`. Devlink parameters are defined in `otx2_dl_params`: `mcam_count` (`u16`) and `unicast_filter_count` (`u8`). Validators and accessors are `otx2_dl_mcam_count_validate`, `otx2_dl_mcam_count_set`, `otx2_dl_mcam_count_get`, `otx2_dl_ucast_flt_cnt_validate`, `otx2_dl_ucast_flt_cnt_set`, and `otx2_dl_ucast_flt_cnt_get`. Optional eswitch operations are `otx2_devlink_eswitch_mode_get` and `otx2_devlink_eswitch_mode_set`.

## Control Flow
Probe calls `otx2_register_dl`, which allocates a `devlink` with private `struct otx2_devlink`, links it back to `pfvf`, registers the parameter table, and then registers the devlink instance. Parameter writes validate that `flow_cfg` exists and that no active flow rules are installed. `mcam_count` stores the requested ntuple count and calls `otx2_alloc_mcam_entries`. `unicast_filter_count` updates `ucast_flt_cnt`, deletes current MCAM flows, and reinitializes MCAM default entries with `otx2_mcam_entry_init`.

## State And Persistence
Devlink state is runtime-only. `struct otx2_devlink` stores the devlink pointer and `otx2_nic` pointer. Parameter values are reflected into `pfvf->flow_cfg->ntuple_cnt`, `max_flows`, and `ucast_flt_cnt`; hardware MCAM state is rebuilt immediately for unicast filter count changes.

## Dependencies And Integration
The file depends on Linux devlink APIs, the shared NIC state, flow management (`otx2_alloc_mcam_entries`, `otx2_mcam_flow_del`, `otx2_mcam_entry_init`), and representor helpers (`rvu_rep_create`, `rvu_rep_destroy`, `otx2_rep_dev`) under `CONFIG_RVU_ESWITCH`.

## Risks
The setters assume `flow_cfg` is initialized except where explicitly checked. Reinitializing MCAM entries for unicast count changes can disrupt existing hardware filters, so validation blocks changes while active rules exist. `mcam_count_set` does not directly propagate allocation failure to devlink because `otx2_alloc_mcam_entries` returns an allocated count; a short allocation may still appear successful to the caller while reducing requested capacity.

## Test Signals
Use `devlink dev param show/set` for both parameters before and after ntuple rules exist. Verify active-rule validation, MCAM entry counts reported by ethtool, unicast filter rebuild, and cleanup on driver remove. With eswitch enabled, test legacy/switchdev transitions and invalid mode rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_devlink.h

## Purpose
`otx2_devlink.h` is the minimal header for the driver's devlink integration. It declares the private devlink wrapper and the registration lifecycle used by PF/VF setup and teardown.

## Important APIs And Types
`struct otx2_devlink` contains `struct devlink *dl` and `struct otx2_nic *pfvf`, tying the generic devlink object to the NIC private state. The exported prototypes are `otx2_register_dl(struct otx2_nic *pfvf)` and `otx2_unregister_dl(struct otx2_nic *pfvf)`.

## Control Flow And Integration
`otx2_common.h` includes this header so `struct otx2_nic` can hold `struct otx2_devlink *dl`. The PF probe path calls `otx2_register_dl` after TC initialization and calls `otx2_unregister_dl` during error unwinding and device removal.

## State And Persistence
The header defines only in-memory state. The `dl` pointer is valid between successful registration and unregister. There is no persistence outside the devlink runtime and the `otx2_nic` lifetime.

## Dependencies
It relies on forward availability of `struct devlink` and `struct otx2_nic` through include ordering. Actual implementation dependencies live in `otx2_devlink.c`.

## Risks
The type is small, but lifetime correctness matters: callers must not dereference `pfvf->dl` after unregister. Because `otx2_unregister_dl` assumes `pfvf->dl` is valid, error paths must call it only after successful registration.

## Test Signals
Build coverage is the main signal for this header. Runtime signals are successful probe, visible devlink instance/params, and no use-after-free reports during probe failure unwinding or module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_dmac_flt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_dmac_flt.c

## Purpose
`otx2_dmac_flt.c` manages CGX/RPM destination-MAC hardware filters used as a whitelist-style complement to NPC MCAM ntuple filtering. It adds, removes, updates, and sizes DMAC filter entries through AF mailbox messages, while maintaining the mapping from driver bitmap positions to hardware filter indexes.

## Important APIs And Functions
Public functions are `otx2_dmacflt_add`, `otx2_dmacflt_remove`, `otx2_dmacflt_update`, and `otx2_dmacflt_get_max_cnt`. Internal helpers split PF interface MAC handling from ordinary MACs: `otx2_dmacflt_add_pfmac` uses `cgx_mac_addr_set`, `otx2_dmacflt_remove_pfmac` uses `cgx_mac_addr_reset`, while `otx2_dmacflt_do_add` and `otx2_dmacflt_do_remove` use add/delete mailbox messages. `otx2_dmacflt_update` sends `cgx_mac_addr_update` and stores the returned index.

## Control Flow
Flow code decides whether an ethtool rule qualifies as a DMAC filter. On add, it passes the destination MAC and bitmap bit position to `otx2_dmacflt_add`, which stores the CGX/RPM returned index in `flow_cfg->bmap_to_dmacindex[bit_pos]`. Removes and updates recover that index from the same array. `otx2_dmacflt_get_max_cnt` asks firmware for `max_dmac_filters` during MCAM flow initialization.

## State And Persistence
The hardware index mapping lives in `pf->flow_cfg->bmap_to_dmacindex`; active logical slots are tracked by `flow_cfg->dmacflt_bmap` in `otx2_flows.c`. Hardware state is not persistent; flow code reinstalls DMAC filters on interface reopen via `otx2_dmacflt_reinstall_flows`.

## Dependencies And Integration
The file depends on `otx2_common.h`, mailbox CGX/RPM MAC address messages, `ether_addr_copy/equal`, and `mbox.lock`. It is tightly integrated with `otx2_flows.c`, which owns rule classification, bitmap allocation, PF-MAC sentinel rule handling, and reinstall/update calls.

## Risks
All operations rely on a valid `flow_cfg` and correctly sized `bmap_to_dmacindex`; callers must validate DMAC support first. PF MAC uses set/reset semantics while other MACs use add/delete semantics, so mixing bit positions can remove or reset the wrong hardware slot. `otx2_dmacflt_do_remove` accepts `mac` but only uses the hardware index, so stale index mapping is the real failure hazard.

## Test Signals
Add/delete ethtool `ETHER_FLOW` rules with destination MAC actions, including PF MAC and non-PF MAC addresses. Verify hardware maximum discovery, bitmap-to-index updates after firmware returns a new index, interface down/up reinstall, and behavior when the DMAC filter table is full.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_dmac_flt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ethtool.c

## Purpose
`otx2_ethtool.c` implements ethtool operations for PF and VF netdevs: stats, channel/ring/coalesce tuning, RSS hash configuration and contexts, ntuple rule control, pause/FEC/link settings, timestamp capability reporting, and driver message level.

## Important APIs And Functions
PF ops are collected in `otx2_ethtool_ops` and installed by `otx2_set_ethtool_ops`; VF ops are in `otx2vf_ethtool_ops` and installed by `otx2vf_set_ethtool_ops`. Major callbacks include `otx2_get_ethtool_stats`, `otx2_get_sset_count`, `otx2_set_channels`, `otx2_set_ringparam`, `otx2_set_coalesce`, `otx2_get_rxnfc`, `otx2_set_rxnfc`, `otx2_set_rxfh`, RSS context create/modify/remove callbacks, `otx2_get_ts_info`, `otx2_get_fecparam`, `otx2_set_fecparam`, and link ksettings get/set helpers.

## Control Flow
Stats collection reads device counters, driver atomics, queue stats, CGX/RPM stats, reset count, and FEC counters. Channel and ring changes stop and reopen the interface if running, update queue/ring state, and rely on open to rebuild hardware. Coalesce updates clamp requested values, toggles adaptive interrupt moderation state, and reprograms CINTs when running. RSS callbacks validate TOP hash use, update the stored RSS key/table or context table, and call mailbox-backed RSS programming helpers. RXNFC callbacks bridge ethtool class-rule commands to `otx2_flows.c`.

Link, pause, and FEC operations use CGX mailbox messages. Timestamp info reports PHC support from `otx2_ptp` and includes one-step TX support only when the hardware capability bit is present.

## State And Persistence
Runtime settings live in `pfvf->hw` (`rss_info`, queue counts, ring sizes, coalesce thresholds, stats), `pfvf->flags` (pause/adaptive coalesce), `pfvf->flow_cfg` (ntuple state), `pfvf->linfo` (link/FEC), and `pfvf->msg_enable`. Settings are volatile but many survive interface down/up because they are stored in `otx2_nic` and reapplied on open.

## Dependencies And Integration
The file depends on Linux ethtool APIs, `cgx_fw_if.h`, PTP helpers, mailbox CGX messages, RSS helpers, MCAM flow helpers, queue stat helpers, and netdev stop/open. It is a primary user-facing integration point for `otx2_pf.c`, `otx2_flows.c`, `otx2_ptp.c`, and firmware link management.

## Risks
Several setters restart the device; error paths must leave netdev queues and hardware resources consistent. `otx2_set_channels` returns immediately on `otx2_set_real_num_queues` failure after stopping the interface, so channel-change error handling deserves attention. RSS ESP/AH hashing has hardware key-size constraints and rejects VLAN combinations. RXNFC requires the interface to be running and ntuple enabled. FEC and link setting depend on firmware support and may return mailbox errors.

## Test Signals
Run ethtool stats under traffic, change channel/ring/coalesce settings while up and down, configure RSS keys/indir/context tables, add/list/delete ntuple rules, toggle pause/FEC/link advertised modes, and verify timestamp capability output before and after PTP initialization. VF tests should confirm reduced stats/link behavior and unsupported PF-only operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_flows.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_flows.c

## Purpose
`otx2_flows.c` owns NPC MCAM flow management for unicast filters, ntuple ethtool rules, VF VLAN flows, RX VLAN offload, TC flow shared state, RSS-context rule cleanup, and CGX/RPM DMAC filter integration. It translates ethtool flow specs into `npc_install_flow_req` mailbox requests and keeps driver-side rule lists synchronized with allocated hardware entries.

## Important APIs And Functions
Initialization and teardown APIs are `otx2_mcam_flow_init`, `otx2vf_mcam_flow_init`, `otx2_mcam_entry_init`, `otx2_alloc_mcam_entries`, `otx2_mcam_flow_del`, `otx2_destroy_ntuple_flows`, and `otx2_destroy_mcam_flows`. Rule APIs are `otx2_add_flow`, `otx2_remove_flow`, `otx2_get_flow`, `otx2_get_all_flows`, and `otx2_get_maxflows`. MAC/VLAN helpers include `otx2_add_macfilter`, `otx2_del_macfilter`, `otx2_enable_rxvlan`, `otx2_install_rxvlan_offload_flow`, `otx2_dmacflt_reinstall_flows`, and `otx2_dmacflt_update_pfmac_flow`.

Internal translation helpers include `otx2_prepare_ipv4_flow`, `otx2_prepare_ipv6_flow`, `otx2_prepare_flow_request`, `otx2_get_kw_type`, `otx2_is_flow_rule_dmacfilter`, and `otx2_add_flow_msg`.

## Control Flow
Probe allocates `flow_cfg`, initializes lists and bitmaps, allocates default MCAM entries for unicast/VLAN/VF VLAN flows, checks field support, then allocates ntuple entries. EtHTool add-rule requests enter `otx2_add_flow`: it validates queue/rule location, creates or updates an `otx2_flow`, classifies DMAC-filter-only rules, either programs CGX/RPM DMAC filters or sends an NPC install-flow request, and inserts the rule into a sorted list. Removal reverses the specific hardware path and deletes the list node.

Flow translation builds packet/mask fields and feature bits for Ethernet, IPv4, IPv6, TCP/UDP/SCTP, AH/ESP, VLAN extension, MAC extension, drop/default/RSS/queue actions, and optional VF forwarding. CN20K may query profile keyword requirements and request X2 or X4 MCAM key type.

## State And Persistence
`flow_cfg` stores allocated ntuple entries (`flow_ent`), default entries (`def_ent`), offsets, DMAC bitmaps, hardware DMAC index mapping, active flow list, TC flow list, max counts, and rule counters. `mac_table` tracks unicast MCAM entries. This state is runtime-only but survives interface open/stop while the PCI device remains bound; hardware entries may be reinstalled during open.

## Dependencies And Integration
The file depends on AF/NPC mailbox messages, `otx2_dmac_flt.c`, ethtool RXNFC structures, IPv6 helpers, sort, DCB backpressure updates, RSS context handling, and PF/VF resource state. It integrates with devlink parameter changes, ethtool ntuple operations, netdev unicast sync, VLAN feature toggles, SR-IOV VF VLAN setup, and TC flower support.

## Risks
MCAM allocation can return fewer entries than requested; callers must respect `max_flows`. DMAC filter rules share the ethtool rule namespace by offsetting locations after `max_flows`, which is easy to misuse. Flow list mutation is not protected by an explicit lock in every public path; callers generally arrive through serialized rtnl/ethtool paths. PFC VLAN rules update RQ BPIDs and must be reversed correctly. VLAN and AH/ESP support depends on the active NPC extraction profile, so unsupported masks should be tested.

## Test Signals
Test unicast filter sync, ntuple add/list/delete for Ethernet, IPv4, IPv6, TCP/UDP/SCTP, drop, queue, VF queue, RSS context, VLAN extension, and unsupported AH/ESP SPI masks. Verify devlink MCAM count changes, DMAC filter table full handling, RX VLAN offload enable/disable, interface reopen reinstall, and destroy paths on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_flows.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_pf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_pf.c

## Purpose
`otx2_pf.c` is the Physical Function driver entry point. It registers the PCI driver, probes and removes PF netdevs, manages AF and VF mailboxes, initializes NPA/NIX resources, opens/stops packet I/O, handles interrupts and resets, exposes netdev operations, manages SR-IOV, applies VF MAC/VLAN/trust settings, handles PTP hardware timestamp configuration, and integrates QoS, XDP, AF_XDP, TC, devlink, DCB, MACsec, and IPsec subsystems.

## Important APIs And Functions
Lifecycle functions include `otx2_probe`, `otx2_remove`, `otx2_init_rsrc`, `otx2_open`, `otx2_stop`, `otx2_init_hw_resources`, and `otx2_free_hw_resources`. Mailbox paths include `otx2_pfaf_mbox_init/destroy`, `otx2_register_mbox_intr`, `otx2_pfaf_mbox_intr_handler`, PF-AF work handlers, PF-VF mailbox init/destroy/interrupt forwarding, and `otx2_queue_vf_work`. Netdev callbacks are collected in `otx2_netdev_ops`, covering open/stop/xmit/select_queue/features/MTU/VF config/XDP/TC/hwtstamp.

Other important paths are FLR/ME interrupt handling, queue error interrupt handling, CQ interrupt/NAPI scheduling, reset work, RX mode programming, SR-IOV enable/disable/configure, VF link-event forwarding, and NDC sync on removal.

## Control Flow
Probe enables PCI, requests BARs, configures DMA, allocates a multi-queue netdev, initializes PF resources and AF mailbox, attaches NPA/NIX LFs, configures LMTST, obtains MAC/PTP/IOMMU, initializes MCAM flows, capabilities, MACsec/IPsec, netdev features, TC, devlink, SR-IOV VF config, link events, AF_XDP bitmap, DCB ops, and QoS. Open allocates queue memory, initializes hardware resources, registers NAPI and IRQs, configures MTU/RSS/segmentation/coalescing/VLAN/timestamps/QoS/DMAC/TC, enables RXT, and sets RX mode. Stop disables traffic, IRQs, NAPI, refill work, and all hardware resources while preserving ring-size settings.

Mailbox interrupts copy or synchronize bounce buffers, queue work, validate message signatures, dispatch responses/notifications, and forward VF messages between VF and AF. SR-IOV enable sets up PF-VF mailbox regions, mailbox IRQs, FLR work, and PCI SR-IOV; disable tears these down in reverse.

## State And Persistence
All state is in `struct otx2_nic`, netdev, PCI device data, workqueues, mailbox regions, queue memory, and hardware. Flags such as `INTF_DOWN`, timestamp enables, pause enables, port-up, and shutdown guide restoration and cleanup. VF state is held in `vf_configs` for MAC, VLAN, trust, and interface-down tracking. Open/stop cycles rebuild hardware resources while keeping driver settings in memory.

## Dependencies And Integration
This file depends on almost every local module: common/register/txrx structures, PTP, CN10K/CN20K helpers, QoS, IPsec, XSK, TC, flows, devlink, DCB, MACsec, representors, and mailbox APIs. External dependencies include PCI, netdev, NAPI, IRQ/MSI-X, IOMMU, BPF/XDP, VLAN, page-pool, and Marvell RVU firmware/AF.

## Risks
The main risks are teardown ordering, mailbox forwarding correctness, reset races, partial probe unwind, and state restoration after open failures. Some hardware errors schedule full reset work from IRQ context. PF-VF forwarding temporarily repoints mailbox base pointers to VF memory, so restoration and locking are critical. Queue counts interact with QoS, XDP, PFC, and AF_XDP. Timestamp, pause, PFC, VLAN, and DMAC states must be disabled on remove and restored on reopen. SR-IOV paths must handle >64 VFs with split interrupt registers.

## Test Signals
Probe/remove and repeated module reloads should be clean under KASAN/lockdep. Run interface up/down loops, MTU changes, queue/ring changes, traffic, XDP attach/detach, AF_XDP setup, TC offload, QoS, ntuple, VLAN, timestamp enable/disable, link events, SR-IOV enable/disable, VF mailbox traffic, VF FLR, and forced AF mailbox failure/defer scenarios. Watch reset count, IRQ errors, queue stalls, and resource leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ptp.c

## Purpose
`otx2_ptp.c` implements Precision Time Protocol PHC support for the RVU NIC. It registers a `ptp_clock`, provides time adjustment/get/set callbacks, supports external timestamp polling and periodic output, selects hardware-atomic or software timecounter conversion mode based on firmware capabilities, and exposes timestamp conversion helpers to netdev timestamp code.

## Important APIs And Functions
Exported functions are `otx2_ptp_init`, `otx2_ptp_destroy`, `otx2_ptp_clock_index`, and `otx2_ptp_tstamp2time`. PTP clock callbacks include `otx2_ptp_adjfine`, `otx2_ptp_enable`, `otx2_ptp_verify_pin`, hardware-mode `otx2_ptp_hw_adjtime/gettime/settime`, and timecounter-mode `otx2_ptp_tc_adjtime/gettime/settime`. Mailbox helpers include `otx2_ptp_get_clock`, `ptp_tstmp_read`, `ptp_set_thresh`, and `ptp_pps_on`.

## Control Flow
Initialization skips loopback VFs, probes PTP availability with `PTP_OP_GET_CLOCK`, allocates `struct otx2_ptp`, populates `ptp_clock_info`, queries `PTP_CAP_HW_ATOMIC_UPDATE`, and either wires callbacks directly to hardware mailbox operations or initializes a `cyclecounter/timecounter` pair. It registers the PHC and selects timestamp format converters based on silicon generation. External timestamp support schedules a delayed polling work item; one-step sync support schedules another delayed work item from PF timestamp config.

## State And Persistence
PTP state lives in `pfvf->ptp`: clock info, registered PHC pointer, cycle/time counters, delayed works, last external timestamp, threshold, pin config, converter callbacks, synchronized timestamp cache, and base nanoseconds. It is runtime-only and destroyed on driver remove. Timestamp enable flags and requested hwtstamp config are stored in `otx2_nic` by `otx2_pf.c`.

## Dependencies And Integration
The file depends on Linux PTP/timecounter APIs, module infrastructure, `otx2_common.h`, `otx2_ptp.h`, and AF PTP mailbox operations. It integrates with ethtool timestamp info, netdev hwtstamp get/set in `otx2_pf.c`, RX/TX timestamp conversion in packet paths, and CN10K one-step support.

## Risks
Some PTP mailbox helpers rely on callers to hold `mbox.lock`, while others lock internally; lock discipline must remain consistent. `otx2_ptp_destroy` cancels `synctstamp_work` but not `extts_work`, so external timestamp polling lifetime should be reviewed. Hardware read failures return zero timestamps, which can look like a valid epoch time. Delayed work reads `ptp->nic`, so teardown ordering must prevent use-after-free.

## Test Signals
Verify `ptp4l/phc2sys` clock registration, `ethtool -T`, gettime/settime/adjfine/adjtime behavior, external timestamp enable/disable, periodic output enable/disable, one-step TX timestamp mode on capable hardware, timestamp conversion for OTX2 and CN10K formats, and clean module removal while EXTS is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ptp.h

## Purpose
`otx2_ptp.h` declares the PTP lifecycle/query API and provides inline hardware timestamp format converters for OTX2 and CN10K-style timestamp layouts.

## Important APIs And Functions
Inline conversion helpers are `otx2_ptp_convert_rx_timestamp`, `otx2_ptp_convert_tx_timestamp`, and `cn10k_ptp_convert_timestamp`. OTX2 RX timestamps are converted from big-endian 64-bit values, OTX2 TX timestamps are already host-order, and CN10K timestamps pack seconds in the upper 32 bits and nanoseconds in the lower 32 bits. Declared APIs are `otx2_ptp_init`, `otx2_ptp_destroy`, `otx2_ptp_clock_index`, and `otx2_ptp_tstamp2time`.

## Control Flow And Integration
`otx2_ptp.c` assigns these converters into `struct otx2_ptp` based on device generation. Packet RX/TX paths can then call through the selected converter without rechecking silicon type. Netdev hwtstamp and ethtool timestamp code use the declared lifecycle/query functions.

## State And Persistence
The header holds no mutable state. It defines conversion semantics used by `pfvf->ptp` function pointers.

## Dependencies
It depends on endian helpers and `NSEC_PER_SEC` being available through the include chain, and on forward availability of `struct otx2_nic`.

## Risks
Timestamp format mistakes create silent time errors. CN10K conversion assumes lower 32 bits are nanoseconds and upper 32 bits seconds; any firmware format change would need a new converter. The big-endian RX cast in `otx2_ptp_convert_rx_timestamp` assumes the input contains exactly the hardware byte layout.

## Test Signals
Validate RX and TX hardware timestamps against PHC time on OTX2 and CN10K devices, including packet captures with known PTP event timing and one-step TX mode where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_reg.h

## Purpose
`otx2_reg.h` defines register offsets and register-address construction macros for the RVU PF/VF, mailbox, NPA LF, NIX LF, LMT LF, and CN20K discovery blocks used by the NIC driver.

## Important APIs And Constants
PF register macros cover PF-VF mailbox windows, VF BAR4 address discovery, block discovery, VF FLR/ME/mailbox interrupt status and enable registers, PF-AF mailbox registers, PF interrupt enables, MSI-X vector/PBA registers, VF mailbox address, and LMT line address. VF macros define VF-PF mailbox, VF interrupts, block discovery, MSI-X, PBA, and mailbox region offsets. CN20K mailbox constants include `RVU_MBOX_AF_PFX_ADDR`, `RVU_PFX_FUNC_PFAF_MBOX`, and `RVU_PFX_FUNCX_VFAF_MBOX`.

NPA macros define aura/pool allocation/free/count/limit/interrupt/stat registers and queue interrupt registers. NIX macros define global/error/RAS registers, SQ/CQ/RQ operation registers, TX/RX stats, debug registers, queue interrupt registers, and completion interrupt moderation registers. LMT macros define LMT line and cancel offsets.

## Control Flow And Integration
Callers pass these logical offsets into `otx2_read64`/`otx2_write64`. `otx2_get_regaddr` decodes the block type bits using `RVU_FUNC_BLKADDR_SHIFT` and `RVU_FUNC_BLKADDR_MASK`, replaces the logical block with the actual NIX/NPA/CPT/RVUM block address, and returns an MMIO address under `reg_base`.

## State And Persistence
The file contains no state. It is a hardware ABI map; the persistent aspect is the contract between driver and silicon/firmware.

## Dependencies
It includes `rvu_struct.h` for block type constants such as `BLKTYPE_NPA` and `BLKTYPE_NIX`. It is included by `otx2_common.h` and PF code that performs direct register access.

## Risks
Incorrect offsets or shifts can direct writes to wrong hardware blocks, causing interrupt loss, mailbox failure, or queue corruption. Multi-register areas for >64 VFs require callers to use the correct bank. CN20K mailbox aliasing differs from older parts, so code must branch on silicon generation.

## Test Signals
Probe-time AF readiness, mailbox interrupt delivery, PF-VF mailbox operation, NPA aura/pool operations, NIX queue interrupts, CQ moderation programming, stats reads, and SR-IOV with more than 64 VFs are the main validation signals for this register map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_reg.h -->
