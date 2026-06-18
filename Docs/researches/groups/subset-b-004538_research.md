# Research: subset-b-004538

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_main.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_main.c

### Purpose

`en_main.c` is the central mlx5 Ethernet netdev implementation for Mellanox/NVIDIA ConnectX-class devices in this source tree. It owns the normal NIC auxiliary driver (`MLX5_ADEV_NAME ".eth"`), registers the representor auxiliary driver during module init, builds the NIC netdev feature surface, allocates and tears down the mlx5e private state, and drives the main lifecycle of receive queues, send queues, completion queues, channels, flow-steering resources, acceleration hooks, and netdev operations.

The file is the bridge between Linux networking core callbacks and mlx5 hardware objects. It translates `ndo_open`, `ndo_stop`, MTU changes, feature toggles, XDP, AF_XDP, hardware timestamping, traffic-control offload, queue management, SR-IOV VF configuration, suspend/resume, and auxiliary-device probe/remove into mlx5 command-interface operations and shared helper APIs from `en/`, `lib/`, `eswitch`, acceleration, and flow-steering modules.

### Important APIs, Types, And Functions

The primary exported/externally used objects are `mlx5e_netdev_ops`, `mlx5e_queue_mgmt_ops`, `mlx5e_nic_profile`, and the auxiliary driver `mlx5e_driver`. `mlx5e_init()` builds ethtool port mappings, registers the Ethernet auxiliary driver, and then registers the representor driver through `mlx5e_rep_init()`. `mlx5e_cleanup()` unregisters them in reverse order.

Queue construction is split by hardware object type. RX queue setup is handled by `mlx5e_init_rxq_rq()`, `mlx5e_alloc_rq()`, `mlx5e_create_rq()`, `mlx5e_open_rq()`, `mlx5e_modify_rq_state()`, `mlx5e_flush_rq()`, `mlx5e_close_rq()`, and `mlx5e_free_rx_descs()`. The RQ path supports cyclic WQs and linked-list striding RQs, UMR-backed multi-packet WQEs, SHAMPO/HW-GRO header buffers, page-pool backed RX memory, XSK memory, XDP program references, checksum state flags, CQE compression variants, and a special drop RQ for steering misses.

TX and internal control queues are built by `mlx5e_alloc_txqsq()`, `mlx5e_open_txqsq()`, `mlx5e_create_sq_rdy()`, `mlx5e_modify_sq()`, `mlx5e_activate_txqsq()`, `mlx5e_deactivate_txqsq()`, `mlx5e_close_txqsq()`, `mlx5e_open_icosq()`, `mlx5e_open_xdpsq()`, and `mlx5e_open_xdpredirect_sq()`. These routines allocate WQ buffers, per-WQE bookkeeping, DMA/skb/XDP FIFOs, configure TIS selection, CQ binding, inline mode, QoS queue groups, packet pacing rate-limit indexes, and TX timestamp translators.

Completion queues are managed by `mlx5e_alloc_cq_common()`, `mlx5e_open_cq()`, `mlx5e_create_cq()`, `mlx5e_modify_cq_period_mode()`, `mlx5e_modify_cq_moderation()`, and `mlx5e_close_cq()`. Channel-level orchestration is in `mlx5e_open_channel()`, `mlx5e_open_channels()`, `mlx5e_activate_priv_channels()`, `mlx5e_deactivate_priv_channels()`, `mlx5e_close_channels()`, `mlx5e_safe_switch_params()`, and `mlx5e_switch_priv_channels()`.

Netdev lifecycle APIs include `mlx5e_create_netdev()`, `mlx5e_priv_init()`, `mlx5e_attach_netdev()`, `mlx5e_detach_netdev()`, `mlx5e_netdev_change_profile()`, `mlx5e_netdev_attach_nic_profile()`, and `mlx5e_destroy_netdev()`. NIC profile callbacks are implemented by `mlx5e_nic_init()`, `mlx5e_init_nic_rx()`, `mlx5e_init_nic_tx()`, `mlx5e_nic_enable()`, `mlx5e_nic_disable()`, `mlx5e_cleanup_nic_rx()`, `mlx5e_cleanup_nic_tx()`, and `mlx5e_nic_cleanup()`.

User-facing netdev operations include `mlx5e_open()`, `mlx5e_close()`, `mlx5e_setup_tc()`, `mlx5e_get_stats()`, `mlx5e_set_mac()`, `mlx5e_set_features()`, `mlx5e_fix_features()`, `mlx5e_change_mtu()`, `mlx5e_xdp()`, `mlx5e_hwtstamp_set()`, `mlx5e_hwtstamp_get()`, `mlx5e_features_check()`, `mlx5e_tx_timeout()`, VXLAN port callbacks, bridge VEPA/VEB callbacks, SR-IOV VF NDOs, and per-queue memory-management operations for queue replacement.

### Control Flow

Module initialization registers the normal Ethernet auxiliary driver and then the Ethernet representor driver. Probe for `.eth` initializes scalable-device state, chooses the actual auxiliary device for multi-device setups, creates devlink state, registers a devlink port, allocates a multi-queue Ethernet netdev, builds the NIC netdev feature set, initializes the NIC profile, resumes/attaches mlx5 resources, registers the netdev, refreshes features, initializes DCB application state, records the uplink netdev in the core device, and logs the initial channel parameters.

Attach flow validates SQ WQEBB capability, recalculates the maximum channel count against firmware limits and netdev queue capacity, adjusts real RX/TX queue counts and XPS mappings, initializes profile TX resources, initializes profile RX resources, then calls the profile enable hook. For the NIC profile, TX init wires acceleration and DCB, RX init allocates q-counters, opens a drop RQ, creates RX resources and flow steering, initializes NIC TC and RX acceleration, and enable configures L2 address state, IPsec/PSP/MACsec, MTU, LAG, async/blocking event notifiers, monitor counters, PCIe congestion events, Hyper-V VHCA stats, DCB app state, RX mode work, and optional reopening of a running registered netdev.

Opening a netdev takes `state_lock`, prepares selected queue parameters, sets `MLX5E_STATE_OPENED`, opens all channels, lets the profile refresh RX steering, applies selected queue state, activates channels, applies traps, updates carrier, and queues stats work. Channel opening allocates channel stats, creates NAPI, opens ICOSQ/TX/RX/XDP CQs, opens ICOSQ/TX SQs/RQ/XDP SQs, optionally opens AF_XDP resources, and binds IRQ affinity and doorbells. Activation enables NAPI, starts TX queues, enables ICOSQs and RX/XSK RQs, associates NAPI with netdev RX/TX queues, activates QoS/PTP pieces, triggers ICOSQ NAPI for initial UMR work, publishes `txq2sq` through a write barrier, enables XDP TX, starts all netdev queues, and activates RX resources.

Close and detach flow reverse the above. `mlx5e_close_locked()` clears open state, drops carrier, deactivates channels, and closes channels. `mlx5e_detach_netdev()` marks the device destroying, disables the active profile, flushes the workqueue, cleans RX/TX resources, resets netdev traffic classes, and cancels stats work. Suspend detaches the netdev and destroys mlx5e mdev resources for every scalable-device component. Resume recreates those resources and reattaches the netdev.

Configuration changes use the safe-switch pattern. `mlx5e_safe_switch_params()` updates parameters in place when the device is closed, or opens a complete replacement `mlx5e_channels` set when opened, swaps it into `priv->channels`, runs an optional preactivate hook, updates XDP features, refreshes RX steering, applies selected-queue state, activates the new channels, restores carrier, and closes old channels after the handoff. This path is shared by MTU changes, LRO/HW-GRO changes, RX-FCS/scatter-FCS toggles, VLAN strip changes, XDP program changes that require reset, PTP RX timestamp mode, MQPRIO, HTB, and channel reopen.

### State And Persistence Behavior

The persistent runtime state is kernel and device state, not disk state. `struct mlx5e_priv` holds the active `mlx5_core_dev`, netdev, profile, profile-private data, maximum channel count, active channel parameters, selected queue state, TX queue to SQ mappings, channel stats allocations, rate-limit state, workqueue, flow steering pointer, RX resources, q-counters, drop RQ, timestamp configuration, acceleration state, debugfs root, and state bits such as opened, destroying, and channels-active.

Hardware state programmed by this file includes RQs, SQs, CQs, MKEYs, UAR/doorbell selection, q-counters, RX resources/TIRs/TTCs, flow-steering tables, drop RQs, port/vport MTU, port admin state, NIC vport MTU, LAG netdev membership, vport admin state for uplink-follow cases, CQ moderation, SQ rate-limit/QoS IDs, FCS and RX timestamp-over-CRC port settings, and tunnel port offload entries. That state persists in the device until explicit teardown, function reset, suspend/remove, or profile switch.

Memory ownership is carefully layered. RQ allocation owns page pools or XSK pool references, UMR mkeys, SHAMPO header pages and mkeys, XDP program references, WQ controls, and RX descriptor bookkeeping. SQ allocation owns WQ controls, WQE info, DMA and skb FIFOs, XDP info FIFOs, rate-limit table entries, and recovery work. Channel stats are intentionally asymmetric: they are allocated on first channel open and freed only in `mlx5e_priv_cleanup()` so stats can survive channel resizing and report deactivated queues through base stats.

Concurrency is centered on `priv->state_lock`, RTNL/netdev locks for registered netdev changes, NAPI synchronization, `synchronize_net()` barriers before disabling queues or replacing programs, workqueue flushing/canceling for carrier/stats/RX-mode/timeout/recovery work, and memory barriers before publishing TX queue mappings. `MLX5E_STATE_DESTROYING` prevents late stats work and tells flow steering that destruction is underway.

### Dependencies And Integration Points

This file depends on Linux netdev, ethtool, DIM, XDP, AF_XDP, page-pool, rtnetlink, TC, bridge, timestamping, debugfs, notifier, workqueue, and auxiliary-driver APIs. It depends on mlx5 core command helpers for creating/modifying/destroying RQ/SQ/CQ/MKEY/q-counter objects, querying capabilities, managing vport/port MTU and admin state, LAG membership, scalable-device routing, devcom, devlink, EQ/IRQ vectors, VXLAN/Geneve state, and clock/PTP translators.

Internal integration is broad: `en.h` and `en/params.h` define core mlx5e data structures and parameters; `en/txrx.h`, `en/xdp.h`, `en/xsk/*`, and `en/ptp.h` supply fast-path and special queue handlers; `en/health.h` reports CQE, timeout, RQ, SQ, and ICOSQ failures; `en/fs_ethtool`, flow steering, TC, HTB/QoS, trap, DCB, monitor-stats, Hyper-V VHCA stats, PCIe congestion, IPsec, PSP, MACsec, kTLS, and devlink modules all plug into the profile hooks. `en_rep.c` uses the generic profile/channel infrastructure for representors and `en_main.c` calls `mlx5e_rep_init()`/`mlx5e_rep_cleanup()` as part of module lifecycle.

### Risks

The file has many multi-stage allocation paths with hardware side effects, so unwind order is critical. A missing close/destroy on an error path can leak mlx5 hardware objects, DMA mappings, page-pool state, XDP program references, rate-limit entries, or notifier registrations. The safe-switch path reduces downtime but is sensitive to preactivate failures, rollback failures, and ordering of old-channel closure versus new-channel activation.

Feature compatibility is dense. XDP conflicts with LRO/HW-GRO and some multi-buffer layouts; AF_XDP restricts MTU and page-size choices; RX CQE compression disables RX hash and conflicts with HW-GRO; header-data split depends on HW-GRO; uplink representors force-disable several NIC features in switchdev mode; PTP TX conflicts with MQPRIO channel mode; queue cloning rejects PTP, XDP, and HTB. Regressions often show up as invalid feature combinations rather than simple compile failures.

Concurrency risks include using queue mappings while netdev queue counts are changing, late work after destroy, NAPI running while queues are deactivated, XDP program replacement without correct reference accounting, and async event handlers racing profile switches. The code uses locks and synchronization heavily, but new call paths need to honor the same locking discipline.

Stats behavior can surprise callers because hardware stats are often refreshed asynchronously for the next read, channel stats outlive inactive channels, uplink representors report port/vport-derived counters differently from normal NIC netdevs, and q-counter allocation failures are tolerated by leaving IDs zero. Tests should check both immediate and delayed stats behavior.

### Test Signals

Strong test signals include successful auxiliary probe/remove and suspend/resume on single-device and scalable-device configurations, netdev registration with expected feature flags, `ip link set up/down` cycling without leaks or warnings, channel count/ring size/coalescing changes, MTU changes with and without XDP/AF_XDP, LRO/HW-GRO/RX-FCS/RXALL/VLAN-strip feature toggles, XDP program attach/replace/detach, XSK pool setup, PTP hardware timestamp configuration, MQPRIO DCB and channel modes, HTB offload interactions, VXLAN/Geneve/GRE/IPIP feature checks, SR-IOV VF NDOs, bridge VEPA/VEB controls, TX timeout reporter recovery, RX timeout reporting, and devlink health reporters.

Useful runtime evidence is absence of mlx5 command leaks on error injection, balanced q-counter/mkey/RQ/SQ/CQ create/destroy counts, stable `ethtool -S` output across channel resize, no WARNs from queue-count rollback, correct `real_num_{rx,tx}_queues`, correct XDP feature flags after feature changes, no late work after detach, and no netdev watchdog false positives after channel activation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_rep.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_rep.c

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_rep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_rep.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_rep.h

### Purpose

`en_rep.h` is the private interface for mlx5 Ethernet representors. It declares the representor RX handler object, representor lifecycle APIs, representor predicates, bonding hooks, offload-stats hooks, and the data structures used by `en_rep.c` and related representor TC, neighbor, bridge, and tunnel modules. It is compiled differently depending on `CONFIG_MLX5_ESWITCH`, providing no-op or unsupported stubs when eswitch support is disabled.

The header is state-definition heavy. It describes the software objects that let representor code track neighbor updates, tunnel encapsulation and decapsulation, TC uplink offload services, per-vport send queues, peer-eswitch forwarding rules, and representor-private netdev/profile state.

### Important APIs, Types, And Functions

When `CONFIG_MLX5_ESWITCH` is enabled, the header exposes `extern const struct mlx5e_rx_handlers mlx5e_rx_handlers_rep` and prototypes for `mlx5e_rep_init()`, `mlx5e_rep_cleanup()`, representor bonding operations, `mlx5e_rep_bond_update()`, offload-stat query helpers, `mlx5e_is_uplink_rep()`, channel activation/deactivation hooks, neighbor stats work, and representor netdev predicates.

`struct mlx5e_neigh_update_table` owns the representor neighbor hash table and list, the encapsulation lock, a netevent notifier, delayed neighbor-stats work, and a minimum stats interval. `struct mlx5e_neigh_hash_entry` is the per-neighbor object containing IPv4/IPv6 destination, family, owning mlx5e private pointer, neighbor netdev, list/hash nodes, protected encap list, refcount, last-use reporting timestamp, and RCU cleanup.

`struct mlx5_rep_uplink_priv` stores uplink-only TC/offload state: indirect TC block callback list, tunnel entropy, unready flow list and reoffload work, mapping contexts for tunnel info and encap options, post-action state, connection tracking, psample, representor bonding, tunnel encapsulation private data, OVS internal-port support, flow meters, TC action stats, and multiport-eswitch work.

`struct mlx5e_rep_priv` is the main per-representor private object. It contains the eswitch representor pointer, neighbor update table, netdev, root flow table, vport RX rule, list of vport SQs, uplink-private state, previous VF vport stats, metadata send rule, TC hash table, and representor vNIC devlink health reporter.

Tunnel offload structures include `struct mlx5e_decap_key`, `struct mlx5e_decap_entry`, `struct mlx5e_mpls_info`, and `struct mlx5e_encap_entry`. They hold Ethernet decap keys, flow lists, hash/list nodes, completions, packet reformat handles, route/tunnel device data, MPLS fields, destination MAC, generated encapsulation header, validity/no-route/decap flags, refcounts, and RCU cleanup.

`struct mlx5e_rep_sq` and `struct mlx5e_rep_sq_peer` model send-to-vport forwarding state for active SQs. Each representor SQ records the local send-to-vport rule, an xarray of peer-eswitch rules, the SQ number, and a list node.

### Control Flow

The header itself has no runtime control flow, but it defines the object graph used by representor load, channel activation, TC offload, tunnel resolution, and cleanup. Eswitch load allocates `struct mlx5e_rep_priv`, stores it in `rep->rep_data[REP_ETH].priv`, and later `mlx5e_rep_to_rep_priv()` retrieves it inline.

During representor TX/offload initialization, modules initialize the neighbor table, TC hash table, tunnel mappings, uplink-private TC services, and bonding/bridge helpers described here. During channel activation, `en_rep.c` allocates `struct mlx5e_rep_sq` records and peer rule entries from these definitions. During unload, those lists, xarrays, hash tables, refcounted objects, completions, notifiers, delayed work, and RCU objects must be drained by implementation files.

When eswitch support is disabled, the header still allows common mlx5e code to compile by providing inline stubs. `mlx5e_is_uplink_rep()` returns false, representor activation/deactivation do nothing, representor driver init returns success, cleanup does nothing, and offload-stat helpers return false or `-EOPNOTSUPP`.

### State And Persistence Behavior

All state defined here is in-memory kernel state. Neighbor, encap, decap, TC, SQ forwarding, and reporter objects exist for the lifetime of a representor or individual offloaded flow and are not persisted to disk. Some structures mirror persistent hardware state: packet reformat handles, send-to-vport flow rules, root flow tables, vport RX rules, tunnel mapping IDs, flow-meter objects, and TC action stats refer to resources programmed elsewhere into mlx5 hardware.

Lifetime management uses a mix of mutexes, spinlocks, refcounts, completions, RCU heads, delayed/work items, hash-table nodes, list nodes, hlist nodes, and xarrays. `mlx5e_neigh_hash_entry` is explicitly protected against removal while notifications or TC users reference it. Encapsulation and decapsulation entries include completions so asynchronous route/reformat resolution can signal waiting flows.

### Dependencies And Integration Points

The header depends on Linux tunnel, rhashtable, mutex, list, refcount, completion, xarray, RCU, and netdev primitives, plus mlx5 internal headers `eswitch.h`, `en.h`, and `lib/port_tun.h`. It forward-declares TC and uplink helper types so related modules can share representor private state without forcing all definitions into this header.

Integration points include `en_rep.c` for lifecycle and profile logic, `en/rep/tc.c` for representor TC offload, `en/rep/neigh.c` for neighbor tracking and stats work, `en/rep/bridge.c` for bridge offload, tunnel encapsulation code for `mlx5e_encap_entry`, decap code for `mlx5e_decap_entry`, and common mlx5e code in `en_main.c`, which calls representor predicates and activation hooks even when built without eswitch support.

### Risks

Because this header defines shared private structures, layout and lifetime changes have broad blast radius. Adding fields to `struct mlx5_rep_uplink_priv` or `struct mlx5e_rep_priv` often requires coordinated initialization and cleanup in several modules. Missing cleanup for a list, hash table, xarray, notifier, work item, or RCU callback can leak objects across representor unload or switchdev mode changes.

Concurrency requirements are implicit in the fields. Neighbor hash operations require `encap_lock`; individual encap lists require `encap_list_lock`; unready flows require `unready_flows_lock`; refcounts protect objects used by notifications and TC; completions communicate asynchronous setup results; RCU heads imply delayed freeing. New code must use the right lock/refcount for the specific subobject rather than assuming representor-wide serialization.

The `CONFIG_MLX5_ESWITCH` stubs hide representor behavior from common code when eswitch support is absent. Callers must be prepared for false or unsupported results and avoid dereferencing representor private state unless the predicate and build configuration make that valid.

### Test Signals

Compile-time signals include successful builds with and without `CONFIG_MLX5_ESWITCH`, no incomplete type misuse from forward declarations, and no missing prototype or stub mismatches. Runtime signals include representor load/unload without leaked neighbor, encap, decap, SQ, peer, or health reporter objects; TC tunnel offload flows resolving and cleaning asynchronously; neighbor notifications safely racing flow removal; peer send-to-vport rules being added and removed; representor bonding hooks updating RX rules; and common NIC code behaving identically when eswitch support is compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_rep.h -->
