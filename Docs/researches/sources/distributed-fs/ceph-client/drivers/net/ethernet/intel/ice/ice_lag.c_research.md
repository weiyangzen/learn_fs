# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lag.c

## Purpose
Implements link aggregation support for `ice`, especially SR-IOV VF behavior in Linux bonding configurations. It watches netdevice bond events, validates whether a bond is compatible with SR-IOV LAG, programs switch recipes/filters, shares switch IDs, moves VF scheduling nodes/queues between ports for active-backup and active-active modes, and rebuilds LAG resources after resets.

## Important APIs, types, and functions
- Public entry points: `ice_init_lag()`, `ice_deinit_lag()`, `ice_lag_rebuild()`, `ice_lag_is_switchdev_running()`, `ice_lag_move_vf_nodes_cfg()`, `ice_lag_prepare_vf_reset()`, `ice_lag_complete_vf_reset()`, and `ice_lag_aa_failover()`.
- Netdevice event path: `ice_lag_event_handler()` snapshots events and bond member lists, queues work on `ice_lag_wq`; `ice_lag_process_event()` handles `NETDEV_CHANGEUPPER`, `NETDEV_BONDING_INFO`, and `NETDEV_UNREGISTER` under `pf->lag_mutex`.
- Role/state helpers: `ice_lag_set_primary()`, `ice_lag_set_bkup()`, `ice_lag_find_primary()`, `ice_lag_link()`, `ice_lag_link_unlink()`, `ice_lag_info_event()`.
- Compatibility: `ice_lag_chk_comp()` rejects unsupported bond modes/features, non-ice members, more than two members, different PCI slot/bus, DCB mismatches, missing switchdev, and firmware LLDP peer conflicts.
- Hardware programming: `ice_create_lag_recipe()`, `ice_lag_cfg_fltr()`, `ice_lag_cfg_dflt_fltr()`, `ice_lag_cfg_drop_fltr()`, `ice_lag_cfg_lp_fltr()`, `ice_lag_primary_swid()`, `ice_lag_set_swid()`, prune-list add/delete helpers.
- VF movement: `ice_lag_move_vf_node_tc()`, `ice_lag_move_vf_nodes()`, `ice_lag_reclaim_vf_tc()`, `ice_lag_aa_move_vf_qs()`, sync/rebuild variants, and reset prepare/complete helpers.

## Control flow
Initialization checks device/package capabilities, allocates `struct ice_lag`, registers a global netdevice notifier, creates three recipes, and maps them to default profiles. Netdevice notifier callbacks filter for ice bonding events, copy notifier data and bond-member lists into a work item, then defer processing. Work processing updates disabled-bond state, validates compatibility, links/unlinks bond state, configures RDMA capability, programs filters, moves VF queues/nodes on active-port changes, and unwinds state on unregister.

Active-backup mode tracks `active_port`; when the active slave changes, VF scheduler nodes and queues move from the previous lport to the new lport, and eswitch representors are retargeted. Active-active mode tracks `port_bitmap`, primary/secondary lports, queue home (`q_home`), and placeholder secondary VF VSIs (`sec_vf`) so queues can be split or failed over between ports. Reset helpers temporarily move nodes home, then restore them after reset under the LAG mutex.

## State and persistence behavior
Driver state lives in `pf->lag`, role flags, bond mode, upper netdev, notifier block, active lport, bond lports, `port_bitmap`, recipe IDs, rule IDs, `q_home`, secondary placeholder VSIs, and bond SWID. Hardware state includes switch recipes, SWID sharing, prune lists, default/drop/control filters, queue-to-port configuration, and scheduler-tree parentage. No host files are persisted.

## Dependencies and integration points
Depends on Linux bonding/netdevice notifier APIs, workqueues, RCU bond member iteration, switchdev/eswitch representors, DCB config, RDMA capability flags, SR-IOV VF/VSI structures, scheduler tree APIs, AdminQ switch-rule and queue-config commands, recipe allocation, and hardware resource sharing. It is invoked by PF init/remove, reset rebuild paths, VF reset flows, and switchdev/SR-IOV control paths.

## Risks
This file has high concurrency and hardware-state risk. Event data is intentionally copied into work items to leave notifier context, but bond topology can change before work runs. Correct locking with `lag_mutex`, RCU list capture, and rebuild/reset pairing is essential. Queue/scheduler movement updates both firmware and software scheduler structures; partial failures can leave mismatches. Active-active placeholder VSI lifetime and `q_home` tracking are fragile. Compatibility checks intentionally disable SR-IOV LAG for unsupported topologies to avoid corrupting VF traffic.

## Test signals
Important tests include two-port same-device bonds, non-ice member rejection, more-than-two member rejection, DCB mismatch rejection, active-backup failover and failback with VFs, active-active link up/down with queue split/failover, switchdev representor Tx after failover, PF reset while bonded, VF reset while bonded, unregister/unlink cleanup, RDMA capability clear/restore on bond join/leave, and recipe/filter cleanup on driver removal.
