# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_fs.c

## Purpose

`en_fs.c` owns the mlx5e NIC receive flow-steering object and the default flow-table hierarchy used before traffic reaches transport traffic classifier tables. It maintains software mirrors of VLAN filters, L2 address filters, promisc/allmulti/broadcast state, trap rules, debugfs state, and pointers to optional steering subsystems such as TC, RXNFC ethtool steering, aRFS, TLS TCP acceleration, UDP, ANY, and PTP flow steering. Its main job is to create, update, and destroy hardware flow tables in a strict order while keeping netdev address and VLAN changes reflected in both mlx5 flow tables and NIC vport context lists.

## Important APIs, Types, And Functions

The central type is `struct mlx5e_flow_steering`. It contains namespace pointers, feature subsystem pointers, L2 and VLAN tables, TTC and inner TTC tables, promisc state, a destroy-state flag, VLAN strip state, device pointer, and debugfs root. `struct mlx5e_vlan_table` stores the VLAN flow table, active C-VLAN/S-VLAN bitmaps, per-VID rule handles, untagged/any-VID/trap rule handles, and a `cvlan_filter_disabled` flag. L2 address state is kept in hash buckets of `struct mlx5e_l2_hash_node`, which wrap `struct mlx5e_l2_rule`, pending add/delete action, and MPFS registration state.

Important external entry points include `mlx5e_fs_init()`, `mlx5e_fs_cleanup()`, `mlx5e_create_flow_steering()`, `mlx5e_destroy_flow_steering()`, `mlx5e_create_ttc_table()`, `mlx5e_destroy_ttc_table()`, `mlx5e_set_ttc_params()`, `mlx5e_fs_set_rx_mode_work()`, `mlx5e_fs_vlan_rx_add_vid()`, `mlx5e_fs_vlan_rx_kill_vid()`, VLAN/MAC trap add/remove helpers, CVLAN filter enable/disable helpers, and a collection of getters/setters for submodules.

Table construction helpers include `mlx5e_create_l2_table()`, `mlx5e_create_l2_table_groups()`, `mlx5e_fs_create_vlan_table()`, `mlx5e_create_vlan_table_groups()`, `mlx5e_create_inner_ttc_table()`, and `mlx5e_create_promisc_table()`. Rule helpers include `mlx5e_add_l2_flow_rule()`, `mlx5e_del_l2_flow_rule()`, `mlx5e_add_vlan_rule()`, `__mlx5e_add_vlan_rule()`, `mlx5e_fs_del_vlan_rule()`, and `mlx5e_add_trap_rule()`.

## Control Flow

Initialization is two-stage. `mlx5e_fs_init()` allocates the `mlx5e_flow_steering` object, records the core device and initial destroy-state behavior, conditionally allocates VLAN and TC structures based on profile capabilities, allocates RXNFC ethtool steering when configured, and creates a debugfs `fs` directory. Hardware flow tables are not created there. `mlx5e_create_flow_steering()` later resolves the kernel flow namespace, creates aRFS tables if possible, creates inner TTC, creates outer TTC, creates L2, creates VLAN, allocates PTP RX flow steering, and initializes ethtool steering. Each error path destroys only resources created earlier, in reverse order.

The default receive hierarchy is VLAN table to L2 table to TTC. VLAN rules forward matching traffic to the L2 flow table. L2 full-match, allmulti, and broadcast rules forward to the TTC table from `mlx5_get_ttc_flow_table(fs->ttc)`. Promiscuous mode creates a separate promisc flow table whose catch-all rule forwards directly to TTC. TTC parameters choose direct TIR for `MLX5_TT_ANY` and RSS TIRs for specific traffic types; tunnel traffic can be forwarded to `inner_ttc` when supported.

VLAN add and delete operations update software bitmaps and hardware rules. C-VLAN add sets the bit then adds a match rule and updates the NIC vport VLAN list; on failure it clears the bit. S-VLAN add sets the S-VLAN bit, adds a rule, and refreshes netdev features because S-tag handling affects feature exposure. Deletion clears the bit, deletes the rule, and for S-VLAN also refreshes netdev features. CVLAN filtering can be disabled by installing any-CVID and any-SVID rules, unless promisc mode already bypasses that filtering.

Netdev address synchronization uses a mark-and-apply model. Existing unicast and multicast hash nodes are first marked `MLX5E_ACTION_DEL`; current netdev addresses are added back with `MLX5E_ACTION_ADD` or reset to `NONE`; then `mlx5e_apply_netdev_addr()` executes pending changes. Adds install L2 flow rules and, for unicast addresses, attempt MPFS registration. Deletes remove MPFS entries when previously registered, delete hardware rules, and free hash nodes. `mlx5e_fs_set_rx_mode_work()` also manages promisc/allmulti/broadcast transitions and updates vport UC/MC/promisc context at the end.

Destroy paths reverse creation order. `mlx5e_destroy_flow_steering()` frees PTP RX steering, VLAN table, L2 table, TTC, inner TTC, aRFS, and ethtool steering. `mlx5e_destroy_vlan_table()` first deletes all VLAN rules and trap rules, then destroys flow groups and the flow table. `mlx5e_destroy_flow_table()` destroys groups before destroying the table handle.

## State And Persistence

All persistent state is in memory and NIC hardware/firmware flow-table state. The active VLAN bitmaps and L2 hash tables are the software source for reinstalling rules when tables are recreated. Hardware state includes mlx5 flow table handles, flow group handles, flow rule handles, NIC vport MAC/VLAN lists, NIC vport promisc/allmulti flags, and MPFS MAC registrations. `state_destroy` gates whether RX mode state is treated as active and is used during teardown-style synchronization; it must be set coherently with work flushing by callers. `vlan_strip_disable` is advisory state used to warn about S-tagged traffic under promisc with C-tag stripping.

The file does not implement its own explicit lock; callers are expected to serialize netdev RX mode, VLAN, and flow-steering lifecycle operations through the wider mlx5e state model. Several allocations use GFP_ATOMIC in address-hash update paths, reflecting use from constrained contexts.

## Dependencies And Integration Points

The file depends on Linux netdev address lists, VLAN protocol handling, debugfs, mlx5 flow steering APIs, mlx5 MPFS, TTC helpers, RX resource TIR selection, profile feature capability checks, PTP RX flow steering, TC table allocation, aRFS, RXNFC ethtool steering, TLS acceleration hooks, and mlx5 tunnel capabilities. It is directly integrated with `en_ethtool.c` through RXNFC steering allocation/access and with `en_fs_ethtool.c` through `mlx5e_fs_get_ethtool()`. Netdev VLAN callbacks and set-rx-mode work call into this file.

## Risks And Edge Cases

Creation order is critical because later tables point to earlier destination tables; error unwinding must stay in exact reverse order. `mlx5e_fs_create_vlan_table()` creates rules immediately from active bitmaps, so bitmap state must be valid before table creation. Vport context update list sizes are capped by device capabilities; excess VLAN or MAC entries are dropped from the vport list with warnings even though software bitmaps/hash nodes still contain them. Partial MPFS failures do not fail L2 rule installation and are only warned, so cleanup must check the `mpfs` flag.

The address handling logic is sensitive to `state_destroy`: the code currently calls `mlx5e_sync_netdev_addr()` only when `fs->state_destroy` is true, while the mode booleans use `rx_mode_enable = fs->state_destroy`. Callers must set this flag according to the intended active/destroy phase or address rules can be removed instead of synchronized. Promisc mode bypasses VLAN filter changes in the CVLAN enable/disable helpers, so tests must cover transitions with and without promisc. Trap rules occupy the last groups in L2/VLAN tables and should remain consistent with table size/group ordering.

## Test Signals

Useful signals include interface open/close with flow table creation and teardown, VLAN add/delete for both 802.1Q and 802.1AD, promisc/allmulti/broadcast transitions, MAC address list churn, vport UC/MC/VLAN list overflow warnings, tunnel inner TTC support on capable and incapable devices, PTP RX flow-steering allocation failure unwinds, and RXNFC/aRFS enabled/disabled profiles. Fault injection around flow-table, flow-group, rule, and allocation failures should verify reverse-order cleanup and absence of leaked rule handles. No local executable tests were run for this research item.
