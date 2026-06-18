# subset-b-004537 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_ethtool.c

## Purpose

`en_ethtool.c` is the mlx5e Ethernet driver's primary implementation of Linux `ethtool_ops`. It translates user-facing ethtool operations into mlx5 channel parameter updates, RSS/RXFH programming, port register queries, link-mode programming, stats collection, module EEPROM access, FEC control, Wake-on-LAN programming, private feature flags, and physical link diagnostics. The file is not a standalone subsystem; it is the netdev control surface for `struct mlx5e_priv`, `struct mlx5_core_dev`, `priv->channels.params`, `priv->rx_res`, and mlx5 port-management helpers.

## Important APIs, Types, And Functions

The file publishes `const struct ethtool_ops mlx5e_ethtool_ops`, whose callbacks are installed by the mlx5e netdev layer. Public helper entry points such as `mlx5e_ethtool_get_drvinfo`, `mlx5e_ethtool_get_sset_count`, `mlx5e_ethtool_get_strings`, `mlx5e_ethtool_get_ethtool_stats`, `mlx5e_ethtool_get_ringparam`, `mlx5e_ethtool_set_ringparam`, `mlx5e_ethtool_get_channels`, `mlx5e_ethtool_set_channels`, `mlx5e_ethtool_get_coalesce`, `mlx5e_ethtool_set_coalesce`, `mlx5e_ethtool_get_ts_info`, `mlx5e_ethtool_get_rxfh_key_size`, `mlx5e_ethtool_get_rxfh_indir_size`, and `mlx5e_ethtool_flash_device` are thin enough to be reused by profile-specific wrappers. Static netdev callbacks usually fetch `priv = netdev_priv(dev)` and delegate to those helpers.

Link-mode translation uses `struct ptys2ethtool_config`, `ptys2legacy_ethtool_table`, `ptys2ext_ethtool_table`, and `mlx5e_build_ptys2ethtool_map()`. This table maps mlx5 PTYS protocol bits to ethtool link mode bitmaps for both legacy and extended modes, including modern 100G/200G/400G/800G/1600G encodings. `mlx5e_ethtool_get_link_ksettings()` queries PTYS, pause, connector, FEC, and partner advertisement state; `mlx5e_ethtool_set_link_ksettings()` converts ethtool advertising or forced speed/lane settings back into PTYS admin bits and toggles the port link after programming.

RSS and classifier integration is split between RXFH callbacks and RXNFC callbacks. `mlx5e_get_rxfh()`, `mlx5e_set_rxfh()`, `mlx5e_create_rxfh_context()`, `mlx5e_modify_rxfh_context()`, and `mlx5e_remove_rxfh_context()` operate on `priv->rx_res`; `mlx5e_get_rxnfc()` and `mlx5e_set_rxnfc()` delegate rule handling to `en_fs_ethtool.c` through `mlx5e_ethtool_get_rxnfc()` and `mlx5e_ethtool_set_rxnfc()`. `mlx5e_get_rxfh_fields()` and `mlx5e_set_rxfh_fields()` similarly bridge to hash-field helpers implemented outside this file.

Private flags are described by `struct pflag_desc mlx5e_priv_flags[]`. The handlers include CQE-based moderation toggles, RX CQE compression, striding RQ, RX checksum-complete suppression, XDP/SKB MPWQE TX, and TX port timestamping. `mlx5e_set_priv_flags()` serializes changes under `priv->state_lock`, invokes each changed flag handler through `mlx5e_handle_pflag()`, updates `priv->channels.params.pflags`, and refreshes netdev features.

Other notable control functions include coalescing helpers that use DIM state and CQ moderation registers, PFC storm prevention tunables, pause parameters, WOL conversion between Linux and mlx5 bit definitions, FEC conversion between PPLM and ethtool values, module EEPROM readers, firmware flashing, LED physical ID, and extended link-state mapping from PDDR troubleshooting status opcodes to `struct ethtool_link_ext_state_info`.

## Control Flow

Most get operations read cached driver state or query firmware registers, then return ethtool-shaped values. Stats callbacks lock `priv->state_lock` only around `mlx5e_stats_update()` and then fill the supplied array. Ring, channel, coalesce, private-flag, RSS, and tunable setters validate user input, acquire `priv->state_lock`, clone `priv->channels.params`, mutate the clone, and call `mlx5e_safe_switch_params()` when the change requires reopening or reconfiguring channels.

Channel changes have explicit guards before switching: zero channels are rejected; XOR RSS cannot exceed the XOR8 channel limit; configured RXFH blocks changes that would resize the RSS table; HTB offload and MQPRIO channel mode block changes because queue numbering is externally visible. If aRFS is active, the setter disables aRFS before switching channels and attempts to re-enable it afterward.

Coalescing follows two paths. Global coalescing updates `new_params`, resets DIM/CQ moderation when period mode or adaptive state changes, applies moderation to existing channels, changes DIM state, then switches params without a full channel reset when possible. Per-queue coalescing directly modifies one channel's RX CQ and each TX CQ after toggling per-queue DIM state.

Link setting is register-driven: the setter chooses legacy versus extended PTYS mode from hardware support, requested advertisement, and autoneg state; converts ethtool bits to PTYS protocol bits or forced-speed info; intersects with hardware capability; checks special constraints such as 56G requiring autoneg; programs `mlx5_port_set_eth_ptys()`; then calls `mlx5_toggle_port_link()`.

RXFH context creation initializes an RSS object for the requested context, applies indir/key/hash function and symmetric transform settings, then reads the resulting values back into the ethtool context. Set/modify/remove operations are serialized by `state_lock` and update only `priv->rx_res`; RXNFC rules are delegated to the flow-steering ethtool module.

## State And Persistence

Persistent state here means driver memory and NIC firmware/hardware state, not filesystem persistence. The central software state is `priv->channels.params`, including queue sizes, channel count, moderation parameters, DIM enablement, private flags, packet merge settings, MPWQE flags, and timestamp-related fields. Hardware state is programmed through mlx5 port and CQ helpers: PTYS, pause, WOL, FEC, PFC stall watermark, module EEPROM reads, firmware flash, LED beacon, and CQ moderation. RSS state lives in `priv->rx_res` and can include multiple ethtool RXFH contexts.

`priv->state_lock` is the primary serialization mechanism for mutable channel/RSS state. Some port-management operations are not protected by this lock if they operate directly on firmware registers and do not mutate shared channel data. Netdev feature state is refreshed with `netdev_update_features()` after changes that affect advertised software features.

## Dependencies And Integration Points

This file depends on Linux ethtool/netdev APIs, `linux/dim.h`, mlx5 core port helpers, firmware flash helpers, stats helpers, RSS resource helpers, PTP support, channel parameter validation/switching, and `en_fs_ethtool.h` for RXNFC/RXFH field delegation. It is tightly coupled to `en_fs.c` and `en_fs_ethtool.c` through `priv->fs`, RX classifier callbacks, and timestamp/PTP flow-steering management. It also integrates with HTB, MQPRIO, XDP, HW-GRO/packet merge, WOL, FEC, and module EEPROM infrastructure.

## Risks And Edge Cases

The PTYS-to-ethtool map must be initialized before link-mode queries; stale or missing mapping entries can silently hide supported speeds. Link-mode conversion is subtle because extended and legacy PTYS admin fields are mutually exclusive, and forced mode uses a different conversion path than autoneg advertisement. Channel resizing is intentionally blocked in several externally visible configurations, but new queue-using features must add similar guards to avoid breaking qdisc or RSS assumptions.

Private flags have cross-feature constraints: RX CQE compression conflicts with HW-GRO/SHAMPO and can interact with hardware timestamping/PTP RX flow steering; TX port timestamping conflicts with HTB and MQPRIO channel mode; striding RQ cannot be disabled while HW-GRO/LRO packet merge is active. Some handlers update hardware state before `mlx5e_safe_switch_params()` returns, so rollback behavior depends on lower-layer switch semantics. FEC setting accepts only one ethtool FEC bit; unsupported combinations return `-EOPNOTSUPP`. EEPROM readers loop until the requested length is satisfied or hardware returns zero, so status/error handling is a useful failure signal.

## Test Signals

Useful runtime tests are ethtool get/set coverage for `-g/-G`, `-l/-L`, `-c/-C`, per-queue coalesce, `-k/-K` feature interactions, `--show-priv-flags/--set-priv-flags`, `-x/-X` and RXFH contexts, `-n/-N` RXNFC rules, `--show-fec/--set-fec`, pause, WOL, module EEPROM, and forced/autoneg link settings on hardware with both legacy and extended PTYS support. Negative tests should assert extack or errno paths for unsupported capabilities, invalid queue counts, RXFH table resize attempts, HTB/MQPRIO blockers, FEC multi-bit requests, and CQE compression plus HW-GRO/PTP conflicts. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_fs.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_fs_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_fs_ethtool.c

## Purpose

`en_fs_ethtool.c` implements the mlx5e RXNFC/ethtool receive classification backend. It converts `struct ethtool_rx_flow_spec` rules into mlx5 flow specs, installs them in per-priority ethtool flow tables, keeps an ordered in-memory list of user rules, supports drop or queue/RSS destinations, and exposes RX hash-field get/set operations for RSS traffic types. It is compiled behind `CONFIG_MLX5_EN_RXNFC` through allocation hooks in `en_fs.c` and is reached from the `get_rxnfc`, `set_rxnfc`, `get_rxfh_fields`, and `set_rxfh_fields` ethtool callbacks in `en_ethtool.c`.

## Important APIs, Types, And Functions

`struct mlx5e_ethtool_steering` owns arrays of `struct mlx5e_ethtool_table` for L3/L4 and L2 priorities, a sorted `rules` list, and a total rule count. `struct mlx5e_ethtool_rule` stores the original ethtool flow spec, installed mlx5 rule handle, owning ethtool table, and optional referenced RSS object. Tables are reference-counted by `num_rules`; `put_flow_table()` destroys a table when its last rule is removed.

The public lifecycle functions are `mlx5e_ethtool_alloc()`, `mlx5e_ethtool_free()`, `mlx5e_ethtool_init_steering()`, and `mlx5e_ethtool_cleanup_steering()`. The public ethtool entry points are `mlx5e_ethtool_set_rxnfc()`, `mlx5e_ethtool_get_rxnfc()`, `mlx5e_ethtool_set_rxfh_fields()`, and `mlx5e_ethtool_get_rxfh_fields()`.

Rule construction flows through `validate_flow()`, `get_flow_table()`, `get_ethtool_rule()`, `add_ethtool_flow_rule()`, and `add_rule_to_list()`. Parsing helpers such as `parse_tcp4()`, `parse_udp4()`, `parse_ip4()`, `parse_tcp6()`, `parse_udp6()`, `parse_ip6()`, and `parse_ether()` fill mlx5 outer-header match criteria and values. Extension helpers handle VLAN VID and destination MAC extension matches.

## Control Flow

Rule insertion uses `mlx5e_ethtool_flow_replace()`. It validates the requested location, destination, masks, tuple count, and supported flow type. The tuple count determines which priority flow table array entry to use: more-specific L3/L4 rules are placed at higher priority within the ethtool namespace, and L2 `ETHER_FLOW` rules use a separate priority range after L3/L4 tables. `get_flow_table()` lazily creates an auto-grouped flow table in `MLX5_FLOW_NAMESPACE_ETHTOOL` when the first rule for a priority arrives.

If the requested location already exists, `get_ethtool_rule()` deletes the old rule first, then allocates a replacement and inserts it into the sorted list by location. `add_ethtool_flow_rule()` allocates an mlx5 flow spec, translates ethtool masks and values, chooses a drop action for `RX_CLS_FLOW_DISC`, or resolves a TIR destination. Non-RSS rules use `mlx5e_rx_res_get_tirn_direct()` based on `ring_cookie`; RSS rules look up the requested RSS context, map the flow type to an mlx5 traffic type, obtain a traffic-type-specific TIR with the current packet-merge parameters, store the RSS pointer, and increment its refcount. The mlx5 rule is added with `FLOW_ACT_NO_APPEND` and `MLX5_FS_DEFAULT_FLOW_TAG`.

Rule removal validates the location, finds the list entry, deletes the hardware rule, decrements any RSS refcount, unlinks and frees the rule, decrements the total rule count, and drops the table reference. Listing rules is location-driven: `mlx5e_ethtool_get_all_flows()` scans from location 0 up to the maximum and calls `mlx5e_ethtool_get_flow()` until it fills the requested rule count. Individual gets copy back the original `flow_spec` and, if the rule used RSS, convert the stored RSS pointer back to an RSS context index.

RX hash-field operations are separate from RX classifier rules. They map ethtool flow types to mlx5 traffic types, allow only TCP/UDP IPv4/IPv6 for setting fields, translate `RXH_IP_SRC`, `RXH_IP_DST`, `RXH_L4_B_0_1`, and `RXH_L4_B_2_3` to mlx5 hash-field selector bits, and call `mlx5e_rx_res_rss_set_hash_fields()` under `priv->state_lock`. The get path reads selectors and translates them back to ethtool bits.

## State And Persistence

State is held in the `mlx5e_ethtool_steering` allocation reached via `mlx5e_fs_get_ethtool(priv->fs)`. It tracks live hardware rules, flow tables, sorted user locations, total rule count, and RSS references. Hardware persistence consists of mlx5 flow tables in the ethtool namespace and flow rule handles inside those tables. RSS rule destinations keep `struct mlx5e_rss` alive with an explicit refcount increment until the rule is deleted. There is no disk persistence; rules are destroyed during flow-steering cleanup and must be recreated after driver lifecycle reset by the netdev/ethtool layer if desired.

## Dependencies And Integration Points

The file depends on mlx5 flow steering, ethtool RX classification definitions, mlx5 RX resources, RSS objects, packet-merge parameters, XSK/channel parameters, and the flow-steering object from `en_fs.c`. It integrates upward through `en_ethtool.c` RXNFC and RXFH field callbacks and downward through `mlx5_create_auto_grouped_flow_table()`, `mlx5_add_flow_rules()`, `mlx5_del_flow_rules()`, direct TIR lookup, and RSS TIR lookup.

## Risks And Edge Cases

`get_flow_table()` increments `num_rules` before namespace lookup and table creation; callers compensate with `put_flow_table()` when later allocation fails, but a direct error return from `get_flow_table()` after increment without table creation is a fragile path to audit when changing this code. Replacement deletes the old rule before proving the new one can be installed, so failed replacement can lose the previous rule. Validation is intentionally restrictive: unsupported masks such as IPv4 TOS, IPv6 traffic class, VLAN ethertype, partial VLAN masks, invalid IPv4 version, too many locations, and out-of-range queue destinations are rejected.

The `FLOW_RSS` path depends on the requested RSS context existing and on a valid mapping from flow type to traffic type. RSS refcounts must be balanced on all deletion and failure paths. The parser applies masks to Ethernet and extension DMAC values in place on the supplied ethtool spec, so callers should not assume those fields remain unmodified after insertion. A rule with no outer-header criteria is rejected earlier by zero tuple count; if future flow types allow metadata-only matches, `outer_header_zero()` and tuple validation would need revisiting.

## Test Signals

Useful tests include inserting, replacing, deleting, getting, and listing RXNFC rules for TCP/UDP IPv4, TCP/UDP IPv6, IPv4/IPv6 user flows, Ethernet flows, VLAN extension matches, destination MAC extension matches, drop rules, direct-queue rules, and RSS-context rules. Negative tests should cover invalid masks, invalid queue cookies, missing RSS contexts, duplicate location replacement failure behavior, max-location limits, and cleanup destroying the last rule in each priority table. RXFH field tests should verify allowed TCP/UDP hash fields, rejection of unsupported flow types or unsupported data bits, and correct behavior for nondefault RSS contexts. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_fs_ethtool.c -->
