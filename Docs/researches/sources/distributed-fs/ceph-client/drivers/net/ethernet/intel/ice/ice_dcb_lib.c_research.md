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
