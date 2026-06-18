# sources/distributed-fs/ceph-client/net/openvswitch/flow_netlink.h

## Purpose
`flow_netlink.h` exports the flow key, mask, identifier, tunnel, and action netlink conversion APIs implemented in `flow_netlink.c`. It is the boundary used by datapath command handling, packet execution, flow table management, and packet key extraction from userspace.

## Important APIs
Size helpers `ovs_tun_key_attr_size()` and `ovs_key_attr_size()` estimate skb space for netlink replies. `ovs_match_init()` initializes a `struct sw_flow_match` around caller-owned key and optional mask storage.

Key parsing and metadata APIs include `parse_flow_nlattrs()`, `ovs_nla_get_flow_metadata()`, and `ovs_nla_get_match()`. Identifier helpers include `ovs_nla_get_ufid()`, `ovs_nla_get_identifier()`, and `ovs_nla_get_ufid_flags()`. Serialization functions include `ovs_nla_put_key()`, `ovs_nla_put_identifier()`, `ovs_nla_put_masked_key()`, `ovs_nla_put_mask()`, and `ovs_nla_put_tunnel_info()`.

Action APIs include `ovs_nla_copy_actions()`, `ovs_nla_add_action()`, `ovs_nla_put_actions()`, `ovs_nla_free_flow_actions()`, and `ovs_nla_free_flow_actions_rcu()`. `nsh_hdr_from_nlattr()` is shared with NSH action code to construct an NSH header from validated attributes.

## Control Flow and Integration
Datapath netlink handlers call parse helpers before creating or updating flows, action execution and reply paths call put helpers, and flow object teardown calls free helpers. The header hides the large internal validation machinery while exposing the small contract needed by the rest of the datapath.

## State and Persistence
The exported action-free APIs encode ownership rules: actions may contain nested allocations and must be freed through this layer, either directly or after RCU grace. Identifier parsing may allocate an unmasked key when no UFID is supplied.

## Dependencies
It depends on kernel netlink/Open vSwitch UAPI types, tunnel headers, RCU, and `flow.h`.

## Risks
Misusing direct `kfree()` on `struct sw_flow_actions` can leak tunnel metadata or conntrack nested resources. Callers must pass appropriately initialized matches, masks, and net namespaces because field support can be per-netns and conntrack dependent.

## Test Signals
Compile-time coverage of every caller, netlink flow add/set/get/dump tests, action memory leak tests, and UFID/non-UFID flow lifecycle tests validate the header contract.
