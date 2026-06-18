# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_rep.c

### Purpose

`en_rep.c` implements mlx5 Ethernet representor netdevs for eswitch switchdev mode. It provides both ordinary vport representors for VF/SF-like eswitch vports and the uplink representor profile that reuses the existing uplink netdev while enabling switchdev offload behavior. Representors expose switch vports as Linux netdevs, connect those netdevs to mlx5e channel/profile infrastructure from `en_main.c`, and integrate TC offload, tunnel encapsulation, neighbor tracking, bridge offload, devlink health reporting, and send-to-vport forwarding rules.

The file is loaded through an auxiliary driver named `eth-rep`. Its probe registers `REP_ETH` operations with the mlx5 eswitch. The eswitch calls those operations when representors are loaded, unloaded, paired with peer eswitches, unpaired, or queried for their protocol device.

### Important APIs, Types, And Functions

The primary externally visible entry points are `mlx5e_rep_init()`, `mlx5e_rep_cleanup()`, `mlx5e_rep_activate_channels()`, `mlx5e_rep_deactivate_channels()`, `mlx5e_is_uplink_rep()`, `mlx5e_eswitch_uplink_rep()`, `mlx5e_eswitch_vf_rep()`, `mlx5e_rep_has_offload_stats()`, `mlx5e_rep_get_offload_stats()`, and `mlx5e_rep_bond_update()`.

Representor netdev operations are collected in `mlx5e_netdev_ops_rep`. They open and close through `mlx5e_rep_open()` and `mlx5e_rep_close()`, transmit through the common `mlx5e_xmit()`, dispatch TC setup through `mlx5e_rep_setup_tc()`, change MTU through `mlx5e_rep_change_mtu()`, expose software/offload stats, and drive vport admin carrier through `mlx5e_rep_change_carrier()`.

Profile objects are `mlx5e_rep_profile` for non-uplink vport representors and `mlx5e_uplink_rep_profile` for the uplink representor. The ordinary profile uses representor stats groups, one TC, representor RX/TX setup, and a representor RX handler table. The uplink profile uses the full NIC-style stats groups, `MLX5_MAX_NUM_TC`, TC/IPsec/bridge/LAG/DCB enable hooks, carrier updates, and uplink-specific RX/TX initialization.

Stats helpers define software representor counters and vport hardware counters. `mlx5e_rep_stats_update_ndo_stats()` folds common NDO stats and updates aggregate q-counter data. `vport_rep` stats query eswitch vport counters via `mlx5_core_query_vport_counter()` and intentionally flip TX/RX because the counters are for the switch vport perspective. `mlx5e_rep_query_aggr_q_counter()` reads aggregate q-counter out-of-buffer data when firmware supports other-vport aggregate q-counters.

Forwarding-rule helpers include `mlx5e_sqs2vport_start()`, `mlx5e_sqs2vport_stop()`, `mlx5e_sqs2vport_add_peers_rules()`, `mlx5e_add_sqs_fwd_rules()`, `mlx5e_remove_sqs_fwd_rules()`, `mlx5e_rep_add_meta_tunnel_rule()`, and `mlx5e_rep_del_meta_tunnel_rule()`. These install send-to-vport rules for each active SQ, plus peer-eswitch rules when devcom reports paired devices.

Load/unload operations are `mlx5e_vport_rep_load()`, `mlx5e_vport_rep_unload()`, `mlx5e_vport_uplink_rep_load()`, `mlx5e_vport_uplink_rep_unload()`, `mlx5e_vport_vf_rep_load()`, and `mlx5e_vport_rep_get_proto_dev()`. Pair/unpair handling is implemented by `mlx5e_vport_rep_event_pair()`, `mlx5e_vport_rep_event_unpair()`, and `mlx5e_vport_rep_event()`.

### Control Flow

Auxiliary probe obtains the mlx5 eswitch from the core device and registers `rep_ops` for Ethernet representors. When the eswitch loads a representor, `mlx5e_vport_rep_load()` allocates `struct mlx5e_rep_priv`, stores the eswitch representor pointer, attaches it to `rep->rep_data[REP_ETH].priv`, initializes the vport SQ list, and dispatches based on vport number.

For the uplink representor, load obtains the already-created uplink netdev from the core and changes its mlx5e profile from the NIC profile to `mlx5e_uplink_rep_profile`. Unload either unregisters the netdev before the profile switch when not returning to legacy mode, or preserves the netdev identity for switchdev-to-legacy transitions, then attaches the NIC profile again.

For non-uplink vport representors, load creates a fresh netdev, builds representor netdev operations and features, stores `rpriv` in `priv->ppriv`, initializes the profile, attaches common mlx5e resources, associates the devlink port and representor vNIC health reporter when available, and registers the netdev. Unload unregisters the netdev, destroys the reporter, detaches mlx5e resources, cleans the profile, and frees the netdev and private representor state.

Opening a representor takes `state_lock`, calls the generic `mlx5e_open_locked()` channel path, then raises the represented eswitch vport admin state. Closing first lowers the vport admin state and then closes generic mlx5e channels. Channel activation adds send-to-vport rules for all active SQs and adds a metadata tunnel rule when the eswitch has a metadata group. Deactivation removes the metadata rule and tears down all SQ forwarding rules and peer rules.

RX setup initializes L2 flow-steering state, opens a drop RQ, creates RX resources, builds the representor TTC table, creates either a direct root table for non-uplink reps or an offloads namespace root table for uplink reps, and installs the vport RX rule pointing at that root table. Uplink RX additionally allocates q-counters, initializes internal-port RX support, and creates `mpesw_work`, which refreshes the vport RX rule after multiport eswitch events.

TX setup initializes neighbor tracking for all representors. Uplink representors additionally initialize TC offload, tunnel entropy, representor bonding, and TC netdevice event handling. A per-representor TC hash table is initialized after those pieces. Cleanup destroys the TC hash table, uplink-only TC/bond/netdevice-event state, and neighbor tracking in reverse order.

### State And Persistence Behavior

Representor state is rooted in `struct mlx5e_rep_priv`, defined in `en_rep.h`. This file mutates the representor netdev pointer, root flow table, vport RX rule, vport SQ forwarding list, previous VF vport stats, metadata tunnel rule, TC hash table, uplink-private state, and devlink health reporter pointer. That state is private to the in-kernel representor lifetime and is freed on unload.

Hardware state includes eswitch send-to-vport flow rules, optional peer-eswitch send-to-vport rules, metadata tunnel send rules, representor TTC/root flow tables, vport RX steering rules, drop RQ and RX resources inherited from generic mlx5e code, vport admin state, aggregate q-counters, TC offload rules created through representor TC modules, and uplink offload state such as bridge, LAG, and tunnel offloads. It persists only until the relevant cleanup path, profile switch, eswitch mode change, or device teardown.

Stats state combines software channel counters with queried hardware vport counters. `prev_vf_vport_stats` is declared in the private structure for tracking previous VF vport statistics across updates. Hardware vport stats are copied into `priv->stats.rep_stats`, and ordinary NDO stats are refreshed asynchronously through the common stats workqueue.

Concurrency is governed by `priv->state_lock`, RTNL/netdev locks during uplink enable/disable and profile switches, workqueue serialization for carrier and multiport-eswitch updates, devcom peer iteration locks when installing peer rules, xarray storage for peer rules per SQ, and safe list iteration when removing SQ forwarding rules.

### Dependencies And Integration Points

`en_rep.c` depends on the mlx5 eswitch API, flow steering, TC offload code, representor TC helpers, neighbor helpers, bridge helpers, devcom, VXLAN/tunnel helpers, devlink health reporter APIs, internal-port TC support, IPsec, PTP, common mlx5e channel/profile code, and Linux switchdev/netdev/TC/ethtool APIs.

The most important integration point is the `struct mlx5_eswitch_rep_ops rep_ops` table. Eswitch code calls `.load`, `.unload`, `.get_proto_dev`, and `.event`, while this file maps those operations to mlx5e netdev creation/profile switching and peer-eswitch forwarding-rule maintenance. The second major integration point is generic mlx5e profile code: representors use `mlx5e_open_locked()`, `mlx5e_close_locked()`, channel activation, queue creation, stats work, MTU changes, and RX resource infrastructure from `en_main.c`.

The uplink representor is especially coupled to modules outside this file. It enables `mlx5e_rep_tc_enable()`, IPsec, bridge offload, DCB app state, LAG membership, and async events for port changes, port affinity, and multiport eswitch changes. It also uses the existing uplink netdev, so profile transitions between NIC and uplink-representor mode are designed to preserve ifindex in switchdev-to-legacy cases.

### Risks

The uplink profile switch is a sensitive lifecycle path. In some unload cases the netdev is unregistered before changing back to NIC profile to avoid leaking offloaded rules; in legacy-mode transitions the netdev is intentionally preserved. Regressions here can leak TC/IPsec/bridge state, break ifindex stability, or leave the core uplink netdev pointer stale.

SQ forwarding rules are installed per active SQ and, when devcom peers are ready, per peer eswitch. Partial failures trigger `mlx5e_sqs2vport_stop()` or event unpair cleanup, but changes to peer insertion or list/xarray ownership could leak flow handles or leave stale peer pointers. The xarray key uses peer `vhca_id`, so uniqueness and lifetime of peer devices matter.

Stats are easy to misinterpret. Vport RX/TX counters are flipped to match representor semantics, loopback counters are conditional on capability, aggregate q-counter reads are optional, and `mlx5e_rep_get_stats()` queues hardware refresh for the next read. Tests should avoid assuming every stat updates synchronously.

Feature support differs sharply between ordinary reps and the uplink rep. Ordinary reps have compact parameters, one TC, VLAN strip disabled for non-uplink vports, and representor netdev ops. The uplink rep presents as `mlx5e_netdev_ops` plus `mlx5e_is_uplink_rep()`, and `en_main.c` then fixes unsupported NIC features in switchdev mode. Bugs often arise when code tests only netdev ops or only vport number instead of using the helper predicates consistently.

### Test Signals

Useful test signals include eswitch switchdev enable/disable cycles, representor netdev creation and deletion for PF/VF/SF vports, uplink profile transitions preserving or unregistering the netdev in the expected cases, `ip link set <rep> up/down` changing the represented vport admin state, successful traffic through send-to-vport rules, metadata tunnel rule creation when the offloads metadata group exists, peer-eswitch pair/unpair events adding and removing peer send rules, and no stale rules after channel close.

Stats tests should check `ethtool -S` software and vport stats, aggregate q-counter out-of-buffer stats on capable firmware, loopback counters on capable firmware, and CPU-hit offload stats. Offload tests should cover TC flower rules, tunnel encap/decap neighbor updates, bridge offload, representor bonding, LAG interactions, uplink port-change carrier updates, port-affinity events, multiport eswitch vport RX rule refresh, devlink vNIC reporter diagnostics, and cleanup under driver unload or devlink reload.
