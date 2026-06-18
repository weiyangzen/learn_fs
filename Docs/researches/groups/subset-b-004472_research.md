# subset-b-004472 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lib.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lib.c

### Purpose
`ice_lib.c` is the main VSI support library for the Intel ICE Ethernet driver. It allocates and tears down VSI software objects, programs VSI contexts into firmware, maps PF queue resources into VSIs, configures RSS/Flow Director/traffic classes/interrupt moderation, handles reset rebuilds, and exposes smaller policy helpers for default VSI forwarding, bandwidth limits, link control, VLAN-zero filters, feature flags, antispoofing, local loopback, and Rx descriptor VLAN extraction.

### Important APIs, Types, And Functions
The file operates on `struct ice_vsi`, `struct ice_pf`, `struct ice_vsi_ctx`, `struct ice_q_vector`, `struct ice_tx_ring`, `struct ice_rx_ring`, `struct ice_port_info`, `struct ice_channel`, and AQ/FW context structures from the ICE shared-code layer. Public entry points include `ice_vsi_alloc()`, `ice_vsi_cfg()`, `ice_vsi_setup()`, `ice_vsi_decfg()`, `ice_vsi_release()`, `ice_vsi_rebuild()`, `ice_ena_vsi()`, `ice_dis_vsi()`, `ice_vsi_close()`, `ice_vsi_cfg_tc()`, `ice_vsi_cfg_netdev_tc()`, `ice_vsi_cfg_msix()`, `ice_vsi_start_all_rx_rings()`, `ice_vsi_stop_all_rx_rings()`, `ice_vsi_stop_lan_tx_rings()`, `ice_vsi_stop_xdp_tx_rings()`, `ice_vsi_cfg_rss_lut_key()`, `ice_vsi_manage_rss_lut()`, `ice_update_eth_stats()`, `ice_update_{tx,rx}_ring_stats()`, `ice_fetch_{tx,rx}_ring_stats()`, `ice_set_{min,max}_bw_limit()`, `ice_set_link()`, `ice_set_dflt_vsi()`, `ice_clear_dflt_vsi()`, `ice_vsi_add_vlan_zero()`, `ice_vsi_del_vlan_zero()`, `ice_init_feature_support()`, `ice_vsi_update_security()`, `ice_vsi_update_local_lb()`, and `ice_vsi_update_l2tsel()`.

Important internal helpers divide the lifecycle into clear phases: `ice_vsi_set_num_qs()` derives queue/vector counts by VSI type; `ice_vsi_alloc_arrays()`, `ice_vsi_alloc_stat_arrays()`, `ice_vsi_alloc_rings()`, and `ice_vsi_alloc_ring_stats()` build software storage; `ice_vsi_get_qs()` reserves PF queue indices; `ice_vsi_init()` builds and submits add/update VSI contexts; `ice_vsi_cfg_tc_lan()` programs LAN scheduler resources; and unwind helpers return queues, rings, vectors, stats, and firmware VSIs in reverse order.

### Control Flow
The normal creation path is `ice_vsi_setup()` -> `ice_vsi_alloc()` -> `ice_vsi_cfg()` -> `ice_vsi_cfg_def()` -> `ice_vsi_cfg_tc_lan()`. Allocation reserves a `pf->vsi[]` slot under `pf->sw_mutex`, initializes `ICE_VSI_DOWN`, and records `pf->next_vsi`. Configuration then assigns type-specific queue counts and interrupt handlers, allocates arrays and stats, reserves PF Tx/Rx queues, derives RSS and TC settings, sends `ice_add_vsi()` or `ice_update_vsi()`, initializes VLAN ops, allocates q_vectors/rings/ring stats for real queue-owning VSI types, maps rings to vectors, optionally configures RSS and aRFS, and finally configures scheduler LAN nodes. Failure paths unwind from the most recent successfully completed phase.

`ice_vsi_init()` is the central firmware-context builder. It sets AQ VSI type flags for PF/SF/VF/CTRL/CHNL/LB, copies VF numbering when needed, applies default VLAN and UP tables, optionally sets Flow Director resource limits, enables loopback in VEB bridge mode, sets RSS LUT/hash context, builds queue mappings either from the generic TC splitter or channel-specific base queue, allows destination override for PF control frames, and then submits add or update AQ commands. The returned context is cached in `vsi->info` and `vsi->vsi_num`.

Runtime control flows are similarly staged. `ice_vsi_close()` brings a VSI down, clears NAPI queue associations, releases MSI-X mappings/IRQs, and frees ring descriptor resources. `ice_dis_vsi()` marks `ICE_VSI_NEEDS_RESTART` and closes active PF/SF/CTRL VSIs, while `ice_ena_vsi()` reopens them if a restart was needed. `ice_vsi_release()` cleans RSS replay/configuration, closes, removes LLDP software rules when applicable, decfgs scheduler and queue resources, and deletes the firmware/software VSI only when reset is not already in progress.

Reset rebuild uses `ice_vsi_rebuild()`: lock `xdp_state_lock`, resize stat arrays, decfg the old software/hardware resources, rerun the default configuration path, snapshot and restore coalesce/ITR settings around LAN TC scheduler configuration, and clear `ICE_VSI_REBUILD_PENDING`. If TC scheduler configuration fails during a no-init rebuild, it schedules a PF reset instead of silently leaving a partial VSI.

### State, Persistence, And Dependencies
Persistent driver state is in the PF and VSI objects: `pf->vsi[]`, `pf->next_vsi`, queue availability bitmaps, `pf->vsi_stats[]`, VSI queue maps, ring arrays, q_vectors, TC/RSS fields, `vsi->info`, `vsi->vsi_num`, VLAN counts, feature bitmaps, and aggregator-node child counts. Hardware/FW state is programmed through AQ helpers (`ice_add_vsi()`, `ice_update_vsi()`, `ice_free_vsi()`), queue/scheduler helpers, filter helpers, and direct register writes for queue control, interrupt moderation, stats, QRX context, and L2 tag extraction.

Memory ownership is mixed. VSI structs and pointer arrays use device-managed allocation, while rings and per-ring stats are `kzalloc()` objects freed via `kfree_rcu()` because datapath/stat readers can race teardown. `u64_stats_sync` protects ring packet/byte counters. `pf->sw_mutex` protects VSI slot allocation/free, `pf->avail_q_mutex` protects PF queue bitmap allocation, `vsi->xdp_state_lock` serializes rebuild with XDP state, RTNL is asserted for netdev NAPI queue association, and reset waiters sleep on `pf->reset_wait_queue`.

Dependencies include the ICE base queue helpers, flow/RSS package APIs, switch/filter APIs, DCB and mqprio configuration, VLAN operation dispatch, Flow Director capabilities, SR-IOV/VF state, LAG/switchdev checks, devlink RDMA parameter state, PTP timestamp caches, XDP ring setup, NAPI/netdev queue APIs, PCI MSI-X dynamic allocation, and shared-code scheduler/bandwidth/default-VSI routines.

### Integration Points
`ice_main.c` uses these helpers to create PF/SF/CTRL/LB VSIs, rebuild VSIs after resets, apply DCB/mqprio changes, set netdev min/max Tx rates, and release all VSIs on remove. SR-IOV and VF code use VSI setup/rebuild/release plus bandwidth/default-VSI helpers. `ice_dcb_lib.c` drives TC changes through `ice_vsi_cfg_tc()`. `ice_eswitch.c`, `ice_lag.c`, and virtchnl paths use security, default forwarding, and L2 tag extraction helpers. Devlink code waits for reset completion through `ice_wait_for_reset()`. Datapath and ethtool statistics consume the ring-stat update/fetch helpers.

### Risks
The lifecycle has many partially initialized states, so unwind order is critical: queues must be returned after scheduler/FW failures, stats must not outlive the arrays they index, and firmware VSIs must be removed only after filters are removed. `ice_vsi_rebuild()` appears to snapshot coalesce values after `ice_vsi_cfg_def()` has already recreated q_vectors, so preserving user coalesce settings across a rebuild depends on surrounding reset code and deserves regression attention. Queue mapping code assumes enough allocated queues per enabled TC and rounds Rx queue counts to powers of two for AQ encoding; mqprio/channel offsets can make off-by-one errors visible as lost queues or invalid AQ contexts.

Concurrency-sensitive areas include RCU ring/stat replacement, interrupt release versus NAPI/ring teardown, RTNL requirements for `netif_queue_set_napi()`, reset-state checks that suppress VSI deletion, and aggregator `num_vsis` accounting that is incremented in setup and decremented only for VF decfg. Feature and VLAN helper bounds are defensive, but callers must still avoid subtracting zero-VLAN counts from a smaller `vsi->num_vlan`. Bandwidth limit validation uses current link speed; unknown or stale link speed can reject or accept policy unexpectedly. `ice_set_link()` intentionally treats manageability ownership as non-fatal for a specific AQ status.

### Test Signals
Useful signals include PF/SF/VF/CTRL/CHNL/LB VSI setup and teardown under fault injection at each allocation/AQ/scheduler step, queue-count changes through ethtool channels, DCB and mqprio TC reconfiguration, ADQ channel creation/removal, reset rebuild preserving RSS/coalesce/XDP state, SR-IOV VF rebuild and bandwidth limits, LLDP filter add/remove with and without FW LLDP agent, VLAN pruning in SVM and DVM including VLAN 0 priority traffic, switchdev/LAG default-VSI handling, NAPI queue association under RTNL, interrupt moderation register programming, ring-stat readers during teardown, and devlink operations blocked on reset wait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lib.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lib.h

### Purpose
`ice_lib.h` declares the internal VSI library interface used across the ICE driver. It exposes creation, configuration, reset, queue, interrupt, RSS, TC, stats, bandwidth, default forwarding, VLAN, feature-bit, security, loopback, and L2 tag extraction helpers implemented in `ice_lib.c`.

### Important APIs, Types, And Functions
The header includes `ice.h` and `ice_vlan.h`, so its declarations are built around core driver objects such as `struct ice_pf`, `struct ice_vsi`, `struct ice_hw`, `struct ice_q_vector`, `struct ice_ring_container`, `struct ice_tx_ring`, `struct ice_rx_ring`, `struct ice_port_info`, `struct ice_vsi_cfg_params`, `struct ice_vsi_ctx`, `enum ice_vsi_type`, `enum ice_disq_rst_src`, and `enum ice_feature`.

It defines `ICE_VSI_FLAG_INIT` and `ICE_VSI_FLAG_NO_INIT` for create-versus-update/rebuild flows. It also defines the QRX context register index/bit offset used for `ice_vsi_update_l2tsel()` and declares `enum ice_l2tsel` with the two supported extraction modes: first VLAN tag into `L2TAG2_2ND` or first VLAN tag into `L2TAG1`.

The exported function groups are: VSI lifecycle (`ice_vsi_setup()`, `ice_vsi_alloc()`, `ice_vsi_cfg()`, `ice_vsi_rebuild()`, `ice_vsi_decfg()`, `ice_vsi_release()`, `ice_vsi_delete()`, `ice_vsi_free()`); open/close/pause/resume (`ice_vsi_close()`, `ice_ena_vsi()`, `ice_dis_vsi()`); queue and interrupt control (`ice_vsi_cfg_msix()`, ring start/stop helpers, IRQ/ring frees, ITR/INTRL writers, NAPI association); RSS/CRC/TC helpers; reset-state helpers; stats helpers; default-VSI/link/bandwidth helpers; VLAN-zero and VLAN-count helpers; feature support helpers; and security/local-loopback/L2TSEL update helpers.

### Control Flow
This header does not implement control flow, but it codifies the sequence expected by callers. New VSI callers prepare `struct ice_vsi_cfg_params`, set `ICE_VSI_FLAG_INIT`, and call `ice_vsi_setup()`. Reset callers reuse an existing VSI through `ice_vsi_rebuild()` with either init or no-init flags. Shutdown callers typically move through `ice_dis_vsi()` or `ice_vsi_close()` before `ice_vsi_release()`. TC/mqprio/DCB callers use `ice_vsi_cfg_tc()` while queues are quiesced, then refresh netdev TC state with `ice_vsi_cfg_netdev_tc()`.

### State, Persistence, And Dependencies
The header owns no storage beyond constants and the `enum ice_l2tsel` declaration. Its ABI is internal to the kernel driver build; persistence lives in the objects passed through the prototypes. Because it includes broad ICE core headers, any consumer sees the full core driver type graph and must obey locking/lifetime rules implemented in `ice_lib.c`, such as RTNL for NAPI queue association, reset-state checks around rebuild/release, and PF/VSI ownership of queue and stats arrays.

### Integration Points
The declarations are consumed by PF setup and reset code in `ice_main.c`, VF/SR-IOV support, DCB and mqprio paths, devlink reset wait paths, switchdev/eswitch security paths, LAG migration logic, virtchnl VLAN tag extraction paths, and ethtool/statistics code. The header acts as the stable local boundary between VSI lifecycle machinery and higher-level policy modules.

### Risks
Because this is a broad internal header, unrelated modules can depend directly on low-level lifecycle and hardware-update routines. Misordered calls are possible if a caller treats declarations as independent operations instead of phases in the VSI state machine. The `ice_vsi_update_l2tsel()` constants are hardware-layout details exposed in the public local header; future register-layout changes require coordinated updates. `ICE_VSI_FLAG_INIT` is a single bit with `NO_INIT` defined as zero, so default-zero parameter structs can accidentally request an update/rebuild flow if a setup wrapper forgets to set the init flag; `ice_vsi_setup()` defends against that with a warning.

### Test Signals
Compile coverage should include all modules that include `ice_lib.h`, especially after signature or enum changes. Runtime signals mirror `ice_lib.c`: PF/SF/VF/CTRL setup and release, reset rebuilds, DCB/mqprio TC updates, RSS programming, IRQ/NAPI association, default-VSI operations, bandwidth limit policy, VLAN-zero behavior, feature support gating by device ID/MAC type, security toggles, local loopback, and virtchnl-driven L2 tag extraction updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lib.h -->
