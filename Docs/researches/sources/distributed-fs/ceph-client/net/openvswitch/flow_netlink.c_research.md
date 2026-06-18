# sources/distributed-fs/ceph-client/net/openvswitch/flow_netlink.c

## Purpose
`flow_netlink.c` is the Open vSwitch kernel datapath translator between generic-netlink attributes and internal flow keys, masks, identifiers, and actions. It validates userspace flow programming, converts packets and installed flows back to netlink form, allocates action blobs, and normalizes several user-facing action formats into execution-friendly internal formats.

## Important APIs, Types, and Functions
Length tables (`struct ovs_len_tbl`, `ovs_key_lens`, `ovs_tunnel_key_lens`, `ovs_nsh_key_attr_lens`, and `ovs_vxlan_ext_key_lens`) define accepted attribute sizes and nested grammars. `parse_flow_nlattrs()` and `parse_flow_mask_nlattrs()` reject duplicate, unsupported, oversized, or malformed key attributes. Mask parsing skips all-zero attributes so wildcard masks remain compact.

`ovs_nla_get_match()` is the main key/mask parser. It parses key attributes, unwraps nested VLAN `OVS_KEY_ATTR_ENCAP` layers, fills `struct sw_flow_match`, synthesizes exact masks when userspace omits a mask, parses explicit masks, forces exact TCI matching, and calls `match_validate()` to ensure protocol-dependent fields are present and only legal masks are supplied.

`metadata_from_nlattrs()` handles non-packet-derived metadata: datapath hash, recirc id, priority, in_port, skb mark, tunnel metadata, conntrack state/zone/mark/labels, and conntrack original tuples. `ip_tun_from_nlattr()` validates IPv4/IPv6 tunnel keys, TTL requirements, bridge-mode tunnel info, and mutually exclusive Geneve/VXLAN/ERSPAN option blocks. `genev_tun_opt_from_nlattr()`, `vxlan_tun_opt_from_nlattr()`, and `erspan_tun_opt_from_nlattr()` copy variable tunnel metadata into `sw_flow_key::tun_opts`. NSH support is handled by `nsh_hdr_from_nlattr()` and `nsh_key_put_from_nlattr()`.

Serialization APIs include `ovs_nla_put_key()`, `ovs_nla_put_identifier()`, `ovs_nla_put_masked_key()`, `ovs_nla_put_mask()`, `ovs_nla_put_tunnel_info()`, and `ovs_nla_put_actions()`. They emit nested VLANs, tunnel keys, conntrack keys, NSH, MPLS labels, transport fields, and normalized action forms.

Action handling is centered on `ovs_nla_copy_actions()`, which allocates `struct sw_flow_actions` and delegates to `__ovs_nla_copy_actions()`. Validation covers output ports, userspace upcalls, truncation, hash algorithms, VLAN push/pop, MPLS push/pop/add semantics, set and masked set writeability, tunnel set metadata allocation, sample/clone/check-packet-length/decrement-TTL nested actions, conntrack actions, Ethernet and NSH push/pop, meter ids, explicit drop placement, and psample support. Nesting is capped by `OVS_COPY_ACTIONS_MAX_DEPTH`. `actions_may_change_flow()` decides whether nested sample/clone/check branches can execute immediately or must be deferred. Free helpers recursively release nested action resources and tunnel metadata dsts.

## Control Flow
Flow installation or packet execute paths parse netlink key attributes through `ovs_nla_get_match()` or `ovs_nla_get_flow_metadata()`, then parse actions through `ovs_nla_copy_actions()`. The action parser walks attributes in order while maintaining a simulated current `mac_proto`, `eth_type`, VLAN TCI, and MPLS label count so later actions and set operations are validated against packet shape after prior actions. For flow dumps, upcalls, and replies, serialization functions convert internal keys/actions back to userspace-visible attributes and reverse internal normalized forms such as `SET_TO_MASKED` and tunnel-info set actions.

## State and Persistence
The file allocates and owns action blobs until they are installed into flows. `sw_flow_actions` is RCU-freed, and nested action resources must be walked recursively. Tunnel set actions allocate `metadata_dst`, initialize a dst cache, and store the pointer inside an internal `OVS_KEY_ATTR_TUNNEL_INFO` action; this requires explicit `dst_release()` on free. There is no disk persistence, but the netlink grammar is a kernel/userspace ABI.

## Dependencies and Integration Points
It depends on OVS UAPI constants, netlink helpers, tunnel protocols, Geneve, VXLAN, ERSPAN, NSH, MPLS, conntrack helpers, `drop.h`, `flow.h`, and `datapath.h`. Datapath command handlers call it to parse user commands and emit flow/packet replies. Action execution consumes the normalized action blob shape produced here.

## Risks
This is one of the highest-risk files in the set. Invalid length tables, missed duplicate checks, wrong mask synthesis, or protocol-inconsistent action validation can admit flows that corrupt packets or produce mismatched userspace/kernel views. Nested action handling must enforce depth and free every internal resource on all error paths. Tunnel options are variable length and require key/mask length agreement. VLAN and MPLS state simulation must stay synchronized with real action behavior. `BUILD_BUG_ON(OVS_KEY_ATTR_MAX != 32)` and `BUILD_BUG_ON(OVS_ACTION_ATTR_MAX != 25)` intentionally force review when UAPI expands.

## Test Signals
Strong signals include OVS datapath netlink selftests for key parse/reject cases, mask exact/wildcard behavior, VLAN/QinQ nesting, IPv4/IPv6 tunnel metadata, Geneve/VXLAN/ERSPAN options, NSH push/pop, conntrack action round-trips, nested sample/clone/check-packet-length/decrement-TTL depth rejection, psample feature gating, action dump round-trips, and memory leak testing on failed flow installs.
