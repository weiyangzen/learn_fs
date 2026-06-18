# subset-b-004540 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_tc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_tc.c

Purpose: implements mlx5e traffic-control flower and matchall hardware offload for both NIC RX steering and switchdev eswitch FDB steering. It translates tc matches/actions into mlx5 flow specs, flow attributes, modify-header programs, counters, post-action tables, tunnel restore mappings, conntrack metadata, sampling, meters, internal-port forwarding, hairpin forwarding, and peer duplicated FDB rules for LAG/multiport setups.

Important APIs and types: `struct mlx5e_tc_table` is the per-netdev TC owner for NIC mode, holding root/miss flow tables, `mlx5_fs_chains`, post-action state, rhashtable of flows, mod-header table, hairpin table, notifier, CT state, mapping context, debugfs, and action stats. `mlx5_flow_attr` and its flexible `mlx5_esw_flow_attr` or `mlx5_nic_flow_attr` tail carry parsed rule actions, destinations, counters, modify headers, chain/prio, match levels, tunnel ids, branches, post-action handles, meter/sample/CT attributes, and restore rules. Exported entry points include `mlx5e_configure_flower`, `mlx5e_delete_flower`, `mlx5e_stats_flower`, `mlx5e_tc_configure_matchall`, `mlx5e_tc_nic_init/cleanup`, `mlx5e_tc_esw_init/cleanup`, `mlx5e_setup_tc_block_cb`, `mlx5e_tc_update_skb`, and register mapping helpers such as `mlx5e_tc_match_to_reg_set`.

Control flow: flower replace starts in `mlx5e_configure_flower`, holds the eswitch, blocks conflicting IPsec offload when needed, rejects duplicate cookies, then calls `mlx5e_tc_add_flow`. The add path selects FDB offload in switchdev mode and NIC offload otherwise. NIC flows allocate a flow/parse attribute pair, parse flower keys, add CT match metadata, parse NIC actions through the action plugin table, prepare pedit modify-header actions, verify final actions, create counters/mod headers/hairpin state, and insert a rule through `mlx5e_add_offloaded_nic_rule`. FDB flows follow the same parsing base but parse eswitch actions, handle tunnel receive and tunnel-id mapping, route/decap attachment, internal OVS ports, encap destinations, split destinations, post-action tables, action stats, and finally offload through `mlx5e_tc_offload_fdb_rules` or a slow-path rule when neighbor or route state is not ready. Delete removes the cookie from the rhashtable, tears down peer flows when present, unoffloads rules, frees counters, mod headers, CT state, tunnel mappings, encap, decap, post actions, action stats, and flow memory.

Matching and actions: `__parse_cls_flower` translates supported dissector keys into mlx5 match buffers for L2, VLAN/CVLAN, IPv4/IPv6, IP TOS/TTL, TCP/UDP ports, TCP flags, ICMP/ICMPv6 flex-parser fields, MPLS-over-BareUDP, CT keys, and tunnel encapsulation keys. `parse_tunnel_attr` controls decap and register-C tunnel identity restore for chained tunnel rules. `parse_tc_actions` delegates individual tc actions to `en/tc/act` implementations, splits multi-table actions into post-action attributes, tracks missable action cookies, handles branch true/false attributes, and programs jumps through post-action flow tables. Pedit conversion validates supported fields, rejects fragmented rewrite masks, skips no-op rewrites, and emits mlx5 modify-header set/add actions.

State and persistence: state is kernel-resident only. Flow identity is the tc cookie in a rhashtable; refcounts and RCU free protect concurrent stats/delete. mlx5 objects persist until flow deletion or TC cleanup: flow rules, counters, mod-header handles, chain table references, post-action handles, meter objects, encap/decap attachments, int-port references, tunnel mapping ids, and hairpin pairs. Slow/unready flow lists allow FDB rules to survive transient route/neigh failures and be reoffloaded by `mlx5e_tc_reoffload_flows_work`. Chain/tunnel/action-miss restore values are stored in device metadata registers and decoded on RX completion.

Dependencies and integration points: this file sits at the boundary between Linux tc (`flow_cls_offload`, `flow_rule`, `flow_action`, matchall) and mlx5 steering (`mlx5_add_flow_rules`, eswitch offloads, chains, flow tables, counters). It integrates with `en/tc_tun*` for tunnel encap/decap, `en/tc_ct` for conntrack, `en/tc/post_act` and `post_meter` for multi-stage actions and meters, `en/tc/sample`, `en/tc/int_port`, `en/mod_hdr`, devcom/LAG peer eswitches, representors, netdevice notifiers, debugfs, and RX metadata restore.

Risks: the highest-risk areas are cleanup ordering across partially initialized flows, peer-flow duplication under LAG, route/neigh slow-path transitions, register bit layout collisions, tunnel option mapping lifetime, pedit mask validation, action splitting around branch/jump semantics, and lock/refcount ordering between rhashtable, RCU, eswitch peer mutexes, and hairpin resources. Hardware capability checks are spread across parse and post-process paths, so regressions can appear as silent software fallback, `-EOPNOTSUPP`, or rules installed with subtly different software semantics. Test signals include tc flower add/delete/stats for NIC and switchdev, tunnel decap with chains and Geneve options, CT restore, sample/meter/action-miss, pedit rewrite, mirror/redirect split destinations, OVS internal ports, LAG peer offload, matchall police, and teardown/reload while flows are live.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_tc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_tc.h

Purpose: public header for mlx5e TC offload. It exposes flow attribute layouts, TC flag bits, register mapping definitions, tunnel mapping structures, initialization APIs, flower/matchall callbacks, offload rule helpers, skb restore helpers, and no-op stubs when `CONFIG_MLX5_ESWITCH` or `CONFIG_MLX5_CLS_ACT` is unavailable.

Important APIs and types: `struct mlx5_flow_attr` is the core action/match/offload descriptor shared by NIC and FDB rules, with flexible tails for `struct mlx5_nic_flow_attr` and `struct mlx5_esw_flow_attr`. It carries action bits, tc action cookies, counter, modify-header handles, CT/sample/meter attributes, parse attributes, chain/prio/dest chain, flow tables, match levels, tunnel metadata, flags, ASO type, post-action and branch pointers, and action-miss restore rule. `struct mlx5e_tc_update_priv` carries RX skb restoration side effects (`fwd_dev`, `skb_done`, `forward_tx`). `struct tunnel_match_key` and `struct tunnel_match_enc_opts` define mapping keys for tunnel restore. The `mlx5e_tc_attr_to_reg` enum assigns logical metadata fields to hardware registers.

Control flow and integration: callers use `mlx5e_setup_tc_block_cb` as the tc block callback, which routes flower commands to configure/delete/stats. Driver init paths call `mlx5e_tc_nic_init/cleanup` for NIC mode and `mlx5e_tc_esw_init/cleanup` for uplink switchdev state. Rule insertion can be done with `mlx5_tc_rule_insert/delete` or NIC-specific add/delete helpers. RX paths call `mlx5e_tc_update_skb` or `mlx5e_tc_update_skb_nic` to restore tc chain, tunnel, CT, sample, internal-port, and action-miss metadata from completion metadata.

State and dependencies: the header depends on Linux packet classifier types, mlx5e core netdev structures, eswitch, CT, tunnel, internal port, meter, and representor headers. Register mapping macros derive bit offsets and masks from the exported `mlx5e_tc_attr_to_reg_mappings` array. `MLX5E_TC_TABLE_CHAIN_TAG_BITS`, tunnel-id bit partitioning, and `MLX5E_TC_FLOW_ID_MASK` encode the metadata ABI between flow insertion and RX restore.

Risks and test signals: because this header defines object layout and register IDs used across many modules, changes can break ABI-like assumptions inside action parsers, CT/tunnel restore, and hardware modify-header programming. Tests should cover builds for all relevant Kconfig combinations, NIC and switchdev flower offload, RX restore from `reg_b/reg_c`, action-miss restore, tunnel options, and compile coverage for consumers that include this header without full eswitch support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_tc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_tx.c

Purpose: implements the mlx5e transmit fast path and TX completion cleanup. It converts SKBs into mlx5 send WQEs, handles inline headers, checksum/LSO metadata, DMA mapping, MPWQE aggregation, accelerator hooks, hardware timestamp tracking, BQL accounting, CQ polling, queue wakeup, descriptor drain on teardown, and optional IPoIB datagram transmit.

Important APIs and functions: `mlx5e_xmit` is `ndo_start_xmit`. It selects a TX SQ from `txq2sq`, runs accelerator begin/finish hooks, computes `mlx5e_tx_attr` and `mlx5e_tx_wqe_attr`, optionally emits MPWQE packets, builds ethernet segments, maps payload/frags, completes the WQE, and rings the doorbell through `mlx5e_notify_hw` when BQL says to flush. `mlx5e_poll_tx_cq` consumes TX completions, unmaps DMA, consumes or frees SKBs, handles timestamp CQEs, detects request errors, and wakes stopped queues. `mlx5e_free_txqsq_descs` drains outstanding descriptors on teardown. `mlx5i_sq_xmit` is the IPoIB variant.

Control flow: non-GSO packets use the configured inline mode and VLAN state to decide inline header size. GSO packets compute inner or outer TCP/UDP header size and use LSO opcode/MSS. `mlx5e_txwqe_build_eseg_csum` programs checksum offload, including PSP, IPsec, and TLS special cases. Data segments are DMA mapped for linear head and fragments; mapping failure unwinds already-pushed DMA entries and posts a NOP flush. MPWQE is used only for simple linear packets without VLAN tag, inline header, accelerator insertion, or MACsec; sessions are completed when full, when eseg changes, or when the stack requests a doorbell.

State and persistence: SQ producer/consumer counters (`pc`, `cc`), DMA FIFO cursors, skb FIFO, WQE info ring, MPWQE session state, PTP metadata freelist/map, queue stopped state, and stats are mutated. DMA mappings persist until CQ completion or teardown drain. Hardware timestamp SKBs may be held with an extra ref until timestamp completion processing.

Dependencies and integration points: depends on the mlx5 work queue/CQ helpers, Linux SKB and DMA APIs, BQL (`netdev_tx_sent_queue/completed_queue`), XPS queue mapping, accel modules for TLS/IPsec/PSP/MACsec, PTP helpers, VLAN helpers, and IPoIB datagram support. It is polled by `en_txrx.c` NAPI and interacts with queue lifecycle code through SQ state bits.

Risks and test signals: this is latency-sensitive and memory-order-sensitive code. Key risks are DMA leak/double unmap on error paths, incorrect WQE size calculation versus `MLX5E_MAX_TX_WQEBBS`, stale MPWQE sessions, timestamp metadata exhaustion, queue stop/wake races, checksum flags with encapsulation or accelerators, and CQ error recovery. Test with linear, fragmented, VLAN, GSO inner/outer, UDP GSO, XDP coexistence, TLS/IPsec/PSP/MACsec, hardware timestamping, MPWQE enabled/disabled, CQ error injection, and interface teardown under TX load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_txrx.c

Purpose: NAPI and CQ event glue for mlx5e channels. It polls TX, RX, XDP, AF_XDP, internal control SQs, kTLS resync work, adaptive interrupt moderation, CQ arming, and completion/error event callbacks.

Important APIs and functions: `mlx5e_napi_poll` is the channel NAPI poll function. `mlx5e_trigger_irq` posts a NOP on an ICOSQ to force an interrupt/NAPI cycle. `mlx5e_completion_event` schedules NAPI for a CQ and increments event counters. `mlx5e_cq_error_event` logs CQ errors. Internal helpers update DIM samples for TX/RX and handle AF_XDP need-wakeup semantics.

Control flow: NAPI first polls regular TX CQs for each traffic class, then optional QoS SQ CQs under RCU. With nonzero budget it polls XDP CQs, AF_XDP RX, normal RX, ICOSQ/AICOSQ completions, kTLS resync, refills RX WQs, handles AF_XDP TX/RX posting, and decides whether the poll remains busy. If busy on a CPU outside the channel affinity mask, it forces a follow-up IRQ. On completion it arms all relevant CQs and updates DIM for TX and RX queues.

State and dependencies: state includes NAPI budget/work_done, channel stats, CQ event counters, DIM state bits, QoS SQ RCU array, XSK need-wakeup flags, ICOSQ pending bits, and RX WQ fill levels. It depends on `en/txrx.h`, RX/TX polling implementations, XDP/XSK helpers, IRQ/NAPI core, RCU, and kTLS acceleration.

Risks and test signals: risks are budget accounting mistakes, missed CQ rearm, AF_XDP need-wakeup races, QoS SQ RCU misuse, affinity-change live lock, and XDP/RX starvation. Test signals include mixed TX/RX load, budget zero polling, QoS queue creation/removal under traffic, AF_XDP zero-copy wakeups, XDP redirect/TX, kTLS RX resync, DIM transitions, and CPU affinity changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eq.c

Purpose: manages mlx5 event queues. It creates/destroys async, command, page-request, generic, and completion EQs; maps EQ buffers into device memory; attaches interrupt notifiers; dispatches completion events to CQs; dispatches async events through notifier chains; and allocates completion IRQ vectors for PCI and SF devices.

Important APIs and types: `struct mlx5_eq_table` owns xarrays for completion EQs and IRQs, async/page/cmd EQs, event notifier heads, CQ error notifier, IRQ table, control IRQ, optional RFS CPU rmap, and CPU allocation masks. Exported APIs include `mlx5_eq_table_init/cleanup/create/destroy`, `mlx5_eq_enable/disable`, `mlx5_comp_eqn_get`, `mlx5_comp_irqn_get`, `mlx5_comp_vectors_max`, `mlx5_comp_vector_get_cpu`, `mlx5_eq_create_generic/destroy_generic`, `mlx5_eq_get_eqe`, `mlx5_eq_update_ci`, `mlx5_eq_notifier_register/unregister`, and `mlx5_cmd_eq_recover`.

Control flow: EQ creation allocates a fragmented buffer, initializes owner bits, fills create EQ command PAS entries, programs event masks and IRQ vector index, executes firmware create, records EQ number/doorbell, and registers debugfs. Async setup requests one control IRQ, registers CQ error handling, creates command EQ first so commands can use events, then general async EQ and optional pages EQ. Completion EQs are created lazily per vector under `comp_lock`; each requests a vector, creates an EQ, attaches the completion interrupt handler, stores it in `comp_eqs`, and returns the EQN. Destruction reverses these steps and restores command polling while tearing down command EQs.

Event handling: completion interrupts poll EQEs up to `MLX5_EQ_POLLING_BUDGET`, use the CQN to find and hold CQs in a radix tree, call the CQ completion callback, update consumer index, and ring the EQ doorbell. Async interrupts call per-event and notify-any atomic notifier chains. CQ error events look up the CQ and invoke its event callback. Recovery can poll command EQ entries with IRQ-save locking.

State and dependencies: persistent state includes EQ buffer ownership bits, consumer index, CQ radix tree per EQ, xarray mappings, current/max comp EQ counts, IRQ references, CPU masks, and notifier registrations. Dependencies include mlx5 command interface, IRQ and PCI IRQ layers, devlink EQ size params, eswitch capability queries, FPGA/clock/fw tracer/IPsec/MACsec event capability checks, RFS rmap, and debugfs helpers.

Risks and test signals: critical risks include missing memory barriers around EQE ownership, CQ lookup lifetime races, leaking IRQ vectors on partial create failure, incorrect async event masks, SF IRQ sharing/rmap behavior, command event recovery, and destroy ordering with live CQs. Test signals include probe/remove, devlink EQ-size parameter changes, many completion vectors, SF devices, RFS enabled/disabled builds, command timeout recovery, CQ error injection, page-request events, and async notifier consumers for port/module/vhca/object changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/Makefile

Purpose: minimal Kbuild fragment for the mlx5 eswitch subdirectory. It applies `subdir-ccflags-y += -I$(src)/..`, making parent `core` headers available to sources below `core/esw`.

Important behavior: there are no object lists or conditional targets in this file; compilation units are selected by parent Kbuild files. Its only API-like effect is the include-path contract for files such as `esw/acl/*.c`, which include headers like `mlx5_core.h`, `eswitch.h`, and local ACL headers.

State and dependencies: no runtime state. The dependency is build-system state: `$(src)` must resolve to `drivers/net/ethernet/mellanox/mlx5/core/esw`, and the parent directory must contain the headers consumed by eswitch submodules.

Risks and test signals: changes here can break all eswitch subdirectory compilation by removing parent include visibility or adding overbroad flags. Test signals are allmodconfig or mlx5 eswitch builds, especially ACL files that rely on `-I$(src)/..`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/egress_lgcy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/egress_lgcy.c

Purpose: configures legacy eswitch egress ACL behavior for vports in VST VLAN/QoS mode. It creates an egress ACL table with an allowed VLAN rule and a drop-all rule, optionally counting drops, then tears it down when VLAN/QoS state no longer requires steering.

Important APIs and functions: `esw_acl_egress_lgcy_setup` is the main setup/update entry. `esw_acl_egress_lgcy_cleanup` destroys rules, groups, table, and drop counter. Static helpers create/destroy the drop rule group and remove existing legacy rules. It uses shared helpers `esw_acl_table_create`, `esw_acl_egress_vlan_grp_create/destroy`, `esw_egress_acl_vlan_create`, and `esw_acl_egress_table_destroy`.

Control flow: setup first reuses or creates a drop counter if egress ACL counters are supported, destroys old rules, and if both VLAN and QoS are zero it cleans up and exits. Otherwise it lazily creates the egress ACL table sized for two rules, creates the VLAN group at index 0 and drop group at index 1, adds an allow rule matching `vport->info.vlan`, optionally with VLAN pop in steering VST mode, then adds the drop rule with optional counter destination. Any failure calls full cleanup.

State and dependencies: state is stored under `vport->egress.acl`, `vport->egress.vlan_grp`, `vport->egress.allowed_vlan`, `vport->egress.legacy.drop_grp`, `drop_rule`, and `drop_counter`. It depends on eswitch capability macros, mlx5 flow table/group/rule APIs, vport VLAN/QoS info, and helper functions in `helper.c`.

Risks and test signals: risks are stale rule handles after setup retries, counter lifetime when ACL creation fails, table-size/group-index mismatches, and behavioral differences between VST steering and non-steering modes. Test with VF vport VLAN add/remove, QoS-only configuration, counter-supported and unsupported firmware, repeated setup updates, and cleanup after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/egress_lgcy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/egress_ofld.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/egress_ofld.c

Purpose: configures eswitch egress ACLs for switchdev/offloads mode. It handles priority-tag pop rules, default or bond-driven forward-to-vport rules, bounce rule cleanup, and vport bond/unbond rewrites for passive representors.

Important APIs and functions: `esw_acl_egress_ofld_setup` creates the offload egress ACL table when fwd-to-vport or prio-tag support requires it. `esw_acl_egress_ofld_cleanup` removes all rules/groups/table. `mlx5_esw_acl_egress_vport_bond` redirects a passive vport to an active vport and removes forwarding from the active vport. `mlx5_esw_acl_egress_vport_unbond` restores default rules. `esw_acl_egress_ofld_bounce_rule_destroy` deletes one xarray-indexed bounce rule.

Control flow: setup exits if neither relevant capability is present or the vport is not VF/SF. It destroys stale rules, computes table size from supported features, creates the egress ACL table, creates a VLAN group for prio-tag rule and optional fwd group, then installs rules. In prio-tag mode it creates a VLAN rule for VLAN ID 0 that pops the tag and either allows or forwards. If a forward destination is supplied, it also creates a catch-all fwd-to-vport rule. Bonding recreates rules on active and passive vports with a destination of type vport plus VHCA ID.

State and dependencies: state lives under `vport->egress.offloads`: `fwd_rule`, `fwd_grp`, `bounce_grp`, and `bounce_rules` xarray, plus shared `vport->egress.acl`, `vlan_grp`, and `allowed_vlan`. Dependencies include firmware capability checks for prio tag and egress fwd-to-vport, eswitch vport lookup, mlx5 flow rules/groups, and shared ACL helpers.

Risks and test signals: risks include leaking xarray bounce rules, stale fwd rules after bond transitions, table size mismatch with conditional groups, ignoring errors when recreating active-vport rules, and using VHCA IDs incorrectly across devices. Test VF and SF vports, prio-tag-required firmware, fwd-to-vport-supported firmware, bond/unbond transitions, repeated cleanup, and error injection in group/rule creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/egress_ofld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/helper.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/helper.c

Purpose: shared ACL utility layer for mlx5 eswitch ingress/egress ACL code. It creates vport ACL flow tables, creates/destroys egress VLAN allow rules and VLAN flow groups, and destroys common ingress/egress ACL tables/rules.

Important APIs and functions: `esw_acl_table_create` checks ingress or egress ACL table support, resolves the vport flow namespace, sets table size and `MLX5_FLOW_TABLE_OTHER_VPORT` when needed, and creates a vport flow table. `esw_egress_acl_vlan_create` creates one allowed VLAN rule matching outer cvlan tag and first VID, with caller-supplied action and optional destination. `esw_acl_egress_vlan_grp_create/destroy` manages the matching group for VLAN rules. `esw_acl_egress_table_destroy`, `esw_acl_ingress_table_destroy`, and `esw_acl_ingress_allow_rule_destroy` are common cleanup helpers.

Control flow: helpers allocate firmware command/spec buffers with `kvzalloc`, fill match criteria using `MLX5_SET` macros, call mlx5 flow steering APIs, store handles on the vport, and clear pointers after destroy. Error paths free allocated buffers and leave handle fields NULL when rule creation fails.

State and dependencies: state is entirely in `struct mlx5_vport` ingress/egress fields: ACL table pointers, `allowed_vlan`, `vlan_grp`, and ingress allow rule. Dependencies include eswitch capability macros, `mlx5_get_flow_vport_namespace`, `mlx5_create_vport_flow_table`, `mlx5_create_flow_group`, `mlx5_add_flow_rules`, and destroy/delete counterparts.

Risks and test signals: risks are duplicate `allowed_vlan` attempts returning `-EEXIST`, wrong namespace/capability selection, missing `OTHER_VPORT` flag for non-uplink or ECPF cases, and match criteria mismatches for VLAN tag/VID. Test ingress and egress ACL table creation on supported/unsupported firmware, vport 0/ECPF/nonzero vports, VLAN allow rule lifecycle, group creation failure cleanup, and repeated destroy calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/helper.c -->
