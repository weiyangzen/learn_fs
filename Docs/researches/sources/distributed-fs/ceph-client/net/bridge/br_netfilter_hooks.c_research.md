# sources/distributed-fs/ceph-client/net/bridge/br_netfilter_hooks.c

## Purpose

`br_netfilter_hooks.c` implements the bridge netfilter compatibility layer that lets bridged IPv4, IPv6, ARP, VLAN-tagged, and PPPoE-encapsulated traffic traverse iptables/ip6tables/arptables/nftables hooks. It temporarily presents bridged frames as L3 packets to IPv4/IPv6/ARP netfilter, remembers bridge metadata in `nf_bridge_info`, then restores L2 encapsulation and resumes bridge forwarding or delivery.

## Important APIs, Types, and Functions

Per-net namespace state is `struct brnf_net`, containing hook enablement and sysctl knobs: `call_iptables`, `call_ip6tables`, `call_arptables`, `filter_vlan_tagged`, `filter_pppoe_tagged`, and `pass_vlan_indev`.

Header classification helpers are `IS_IP()`, `IS_IPV6()`, `IS_ARP()`, `vlan_proto()`, `is_vlan_ip()`, `is_vlan_ipv6()`, `is_vlan_arp()`, `pppoe_proto()`, `is_pppoe_ip()`, and `is_pppoe_ipv6()`. Encapsulation helpers are `nf_bridge_encap_header_len()`, `nf_bridge_pull_encap_header()`, `nf_bridge_pull_encap_header_rcsum()`, `nf_bridge_update_protocol()`, and `setup_pre_routing()`.

Main hook callbacks are `br_nf_pre_routing()`, `br_nf_forward()`, `br_nf_post_routing()`, optional conntrack `br_nf_local_in()`, and `ip_sabotage_in()`. Finish callbacks include `br_nf_pre_routing_finish()`, `br_nf_pre_routing_finish_bridge()`, `br_nf_forward_finish()`, and `br_nf_dev_queue_xmit()`.

Registration objects are `br_nf_ops`, `br_ops`, `brnf_notifier`, and `brnf_net_ops`. `br_nf_hook_thresh()` is exported internally to resume bridge hooks after the bridge-netfilter priority point.

## Control Flow

Bridge `NF_BR_PRE_ROUTING` calls `br_nf_pre_routing()`. It pulls VLAN/PPPoE encapsulation if configured, checks the per-net and per-bridge call flags, validates IPv4 headers with `br_validate_ipv4()` or dispatches IPv6 to `br_nf_pre_routing_ipv6()`, allocates `nf_bridge_info`, records original destination, and calls the L3 PRE_ROUTING hook. The finish function detects DNAT by comparing the current destination with the saved one. If routing says the new destination is still reachable through the bridge, it restores bridge encapsulation and resumes bridge PRE_ROUTING via `br_nf_pre_routing_finish_bridge()`. Otherwise it converts the packet for local/routed handling by changing destination MAC and `PACKET_HOST` state.

Bridge `NF_BR_FORWARD` calls `br_nf_forward()`. IP and IPv6 packets are unshared, decapsulated, validated, given physical out-device metadata, and passed through L3 FORWARD. ARP packets optionally go through ARP FORWARD. `br_nf_forward_finish()` restores encapsulation, original protocol, `PACKET_OTHERHOST` state, and resumes bridge forwarding hooks before `br_forward_finish()`.

Bridge `NF_BR_POST_ROUTING` calls `br_nf_post_routing()`. Packets that still carry `nf_bridge_info->physoutdev` are decapsulated and sent through L3 POST_ROUTING. `br_nf_dev_queue_xmit()` restores protocol and encapsulation, handles packet type restoration, frees bridge netfilter skb extension on normal transmit, and fragments IPv4/IPv6 packets when defragmentation plus MTU constraints require it.

`ip_sabotage_in()` prevents locally destined bridge packets from being handed to IPv4/IPv6 PRE_ROUTING a second time. `br_nf_dev_xmit()` handles the slow bridged-DNAT path where neighbour output rewrote the MAC header and the original bridge source header must be restored before bridge forwarding continues.

## State and Persistence Behavior

Per-packet state lives in the skb extension `SKB_EXT_BRIDGE_NF` as `struct nf_bridge_info`. It records original encapsulation protocol, physical in/out devices, original IPv4/IPv6 destination, fragmentation limits, packet type, DNAT bridge path state, neighbour header bytes, and the `in_prerouting`/`sabotage_in_done` flags.

Per-CPU state `brnf_frag_data_storage` stores temporary MAC/encapsulation data while IPv4 or IPv6 fragmentation is rebuilding L2 headers. It is protected with `local_lock_nested_bh()`.

Per-net persistent state is registered through `brnf_net_ops`; sysctl state exists under `net/bridge` when `CONFIG_SYSCTL` is enabled. Bridge netfilter hooks are registered lazily on `NETDEV_REGISTER` for bridge master devices and unregistered on namespace exit.

## Dependencies and Integration Points

The file integrates bridge hooks (`NFPROTO_BRIDGE`) with IPv4, IPv6, ARP, conntrack, dst/neighbour routing, VLAN, PPPoE, sysctl, net namespace generic storage, and bridge forwarding (`br_handle_frame_finish()`, `br_forward_finish()`, `br_dev_queue_push_xmit()`). It calls IPv6-specific code in `br_netfilter_ipv6.c` for IPv6 validation and PRE_ROUTING handling. It also publishes `nf_br_ops.br_dev_xmit_hook` so bridge device transmit can delegate bridged-DNAT completion.

## Risks and Edge Cases

The main risk is preserving skb invariants while repeatedly pulling and pushing L2 encapsulation. Bugs can corrupt header offsets, checksums, protocol values, packet type, VLAN tags, or physical device metadata. DNAT routing decisions are subtle because packets may remain bridged or become routed after L3 netfilter changes destination addresses.

Fragmentation is explicitly imperfect: comments note that original fragment boundaries are not preserved when refragmenting. Conntrack handling for multicast/broadcast clone races is delicate and depends on confirmed/unconfirmed skb reference assumptions. Sysctl defaults enable bridge calls to iptables, ip6tables, and arptables, which can surprise deployments and affect forwarding performance.

## Test Signals

Tests should cover IPv4, IPv6, ARP, VLAN-tagged, and PPPoE bridge traffic with bridge-nf sysctls both enabled and disabled; DNAT to same bridge, DNAT to routed device, REDIRECT, local delivery, broadcast/multicast conntrack confirmation, MTU fragmentation, and IPv6-disabled handling. Observable signals include netfilter rule hits in bridge and L3 families, tcpdump header preservation across hooks, conntrack table behavior for multicast clones, sysctl values under `net/bridge`, and drop reasons for malformed packets.
