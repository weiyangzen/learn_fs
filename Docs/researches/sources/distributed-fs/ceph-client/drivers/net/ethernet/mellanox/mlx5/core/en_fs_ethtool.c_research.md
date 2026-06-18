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
