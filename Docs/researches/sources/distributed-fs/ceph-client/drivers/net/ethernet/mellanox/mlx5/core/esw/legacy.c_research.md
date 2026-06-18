# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/legacy.c

Purpose: Implements legacy-mode eswitch FDB setup, VEPA mode, vport ACL orchestration, drop-stat queries, and legacy sriov vport configuration controls.

Important APIs/types/functions: Public entry points include `esw_legacy_enable()`, disable, `mlx5_eswitch_set_vepa()`, get, `esw_legacy_vport_acl_setup()`, cleanup, `mlx5_esw_query_vport_drop_stats()`, `mlx5_eswitch_set_vport_vlan()`, spoofchk/trust setters, and `mlx5_eswitch_set_vport_rate()`. Internal helpers create/destroy legacy FDB and VEPA tables and rules.

Control flow: Legacy enable creates the FDB table with address, allmulti, and promisc groups, initializes VF link state to auto, then enables PF/VF vports for UC/MC/promisc events. VEPA set creates a small higher-priority VEPA table with an uplink-to-FDB rule and a default star rule to uplink, or removes those rules and table when disabled. Vport ACL setup skips manager vports, installs ingress legacy ACL, then egress legacy ACL, unwinding ingress on egress failure. Configuration setters lock `esw->state_lock`, validate mode/permissions, update vport info, and recreate ACLs or notify vport change handlers when needed.

State and persistence: State lives in `esw->fdb_table.legacy` flow tables/groups/rules, `esw->user_count`, `esw->mc_promisc`, vport info fields such as VLAN/QoS/spoofchk/trusted/link state, and ACL counters used for drop stats.

Dependencies and integration: Uses flow steering, flow table pools, common eswitch vport lifecycle, legacy ACL headers, QoS rate setter, vport down stats firmware query, and permission/mode helpers. It bridges older SR-IOV netlink controls with mlx5 hardware steering.

Risks and test signals: Risks include FDB group size/index errors, VEPA partial rule leaks, legacy/offloads mode compatibility semantics for VLAN 0, spoof-check rollback on ACL failure, and drop stats double-counting. Test signals include enabling/disabling legacy SR-IOV, VEPA on/off, UC/MC/promisc updates, VLAN/spoofchk/trust/rate settings, vport down stats, and manager-vport ACL skip behavior.
