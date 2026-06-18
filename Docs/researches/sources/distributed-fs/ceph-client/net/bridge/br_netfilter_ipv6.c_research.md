# sources/distributed-fs/ceph-client/net/bridge/br_netfilter_ipv6.c

## Purpose

`br_netfilter_ipv6.c` contains the IPv6-specific bridge netfilter PRE_ROUTING path. It validates IPv6 packets received by the bridge, sends them through IPv6 PRE_ROUTING, detects DNAT, restores bridge encapsulation, and decides whether the packet should continue bridged or be converted for routed/local handling.

## Important APIs, Types, and Functions

The exported functions are `br_validate_ipv6()` and `br_nf_pre_routing_ipv6()`, declared for the main hook file through `include/net/netfilter/br_netfilter.h` when IPv6 support is enabled.

`br_validate_ipv6()` checks pullability, IPv6 version, hop-by-hop extension length through `nf_ip6_check_hbh_len()`, payload length versus skb length, checksum-safe trimming, and clears `IP6CB(skb)`.

`br_nf_pre_routing_finish_ipv6()` mirrors the IPv4 finish path in `br_netfilter_hooks.c`. It compares destination addresses with `br_nf_ipv6_daddr_was_changed()`, reroutes on DNAT with `ip6_route_input()`, handles bridge-parent routes, restores original bridge protocol, pushes encapsulation, and resumes bridge hooks.

`br_nf_pre_routing_ipv6()` validates the skb, allocates `nf_bridge_info`, calls `setup_pre_routing()`, stores the original IPv6 destination, sets protocol and transport-header offsets, invokes `NF_HOOK(NFPROTO_IPV6, NF_INET_PRE_ROUTING, ...)`, and returns `NF_STOLEN`.

## Control Flow

The main bridge pre-routing hook dispatches IPv6 frames here after optional VLAN/PPPoE decapsulation and call-ip6tables checks. `br_nf_pre_routing_ipv6()` first validates the skb. If validation or metadata allocation fails, it returns a bridge netfilter drop verdict with a reason. Otherwise, `setup_pre_routing()` records the physical ingress device and changes `skb->dev` to the logical bridge or bridge VLAN device. IPv6 PRE_ROUTING then runs.

When the IPv6 PRE_ROUTING hook finishes, `br_nf_pre_routing_finish_ipv6()` stores fragment size state, restores `PACKET_OTHERHOST` if needed, clears `in_prerouting`, and checks for DNAT. If the destination changed, it drops the old dst, runs `ip6_route_input()`, and either continues bridged when the route output device is still the bridge device, or rewrites the Ethernet destination to the bridge device address and marks the skb as `PACKET_HOST` for routed/local processing. If the destination did not change, it uses the bridge parent rtable. Both non-drop paths restore the physical bridge input device, update the original protocol, push encapsulation, and resume bridge PRE_ROUTING.

## State and Persistence Behavior

This file owns no persistent global state. Per-packet state is stored in `nf_bridge_info`, especially `ipv6_daddr`, `frag_max_size`, `pkt_otherhost`, and `in_prerouting`. IPv6 control block state is cleared during validation and `IP6CB(skb)->frag_max_size` is copied back into bridge netfilter metadata after IPv6 hooks run.

## Dependencies and Integration Points

The implementation depends on IPv6 core helpers (`ipv6_hdr()`, `ipv6_payload_len()`, `ip6_route_input()`), IPv6 stats, netfilter bridge metadata helpers (`nf_bridge_alloc()`, `nf_bridge_info_get()`, `nf_bridge_update_protocol()`, `nf_bridge_push_encap_header()`), `setup_pre_routing()` and `br_nf_hook_thresh()` from `br_netfilter_hooks.c`, and bridge forwarding completion through `br_handle_frame_finish()` or `br_nf_pre_routing_finish_bridge()`.

## Risks and Edge Cases

IPv6 validation must keep skb length, extension header length, checksum state, and `IP6CB` state consistent before the packet enters IPv6 netfilter. DNAT handling depends on route output device comparison; wrong device restoration can turn a bridged packet into a routed one or vice versa. The file shares header offset and encapsulation assumptions with the main hook file, so VLAN/PPPoE changes there directly affect this path.

## Test Signals

Useful tests include IPv6 bridge forwarding with `bridge-nf-call-ip6tables` enabled and disabled, IPv6 DNAT to another host on the same bridge, DNAT to routed/local destinations, VLAN and PPPoE IPv6 frames, malformed payload length and hop-by-hop headers, IPv6-disabled behavior in the caller, and packet captures verifying that Ethernet headers and skb devices are restored correctly after IPv6 PRE_ROUTING.
