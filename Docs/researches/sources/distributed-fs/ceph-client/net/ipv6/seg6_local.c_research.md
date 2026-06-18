# sources/distributed-fs/ceph-client/net/ipv6/seg6_local.c

## Purpose
`seg6_local.c` implements the IPv6 Segment Routing local SID lightweight-tunnel endpoint. It is the receive-side action engine for `LWTUNNEL_ENCAP_SEG6_LOCAL`, handling SRv6 End, End.X, End.T, End.DX2, End.DX4, End.DX6, End.DT4, End.DT6, End.DT46, End.B6, End.B6.Encaps, and End.BPF behaviors. It also owns netlink parsing, dumping, comparison, optional counters, flavor support, and lwtunnel registration for local SRv6 behaviors.

## Important APIs, types, and functions
Core state is carried by `struct seg6_local_lwt`, which stores the selected action, parsed attributes, nexthops, table or VRF table IDs, SRH template, BPF program reference, optional per-CPU counters, flavor configuration, and the selected `seg6_action_desc`. `struct seg6_action_desc` maps each UAPI action to required attributes, optional attributes, input callback, headroom, and optional build/destroy hooks. `seg6_action_table[]` is the main behavior registry.

Packet helpers include `get_and_validate_srh()`, `decap_and_validate()`, `advance_nextseg()`, `seg6_lookup_any_nexthop()`, `seg6_lookup_nexthop()`, `seg6_pop_srh()`, and `end_dt_vrf_core()`. Input callbacks implement the actions: `input_action_end()`, `input_action_end_x()`, `input_action_end_t()`, `input_action_end_dx2()`, `input_action_end_dx6()`, `input_action_end_dx4()`, `input_action_end_dt4()`, `input_action_end_dt6()`, `input_action_end_dt46()`, `input_action_end_b6()`, `input_action_end_b6_encap()`, and `input_action_end_bpf()`.

Control-plane helpers include per-attribute parsers/dumpers/comparators such as `parse_nla_srh()`, `parse_nla_table()`, `parse_nla_vrftable()`, `parse_nla_bpf()`, `parse_nla_counters()`, and `parse_nla_flavors()`. `seg6_local_build_state()`, `seg6_local_destroy_state()`, `seg6_local_fill_encap()`, `seg6_local_get_encap_size()`, and `seg6_local_cmp_encap()` implement the `lwtunnel_encap_ops` contract.

## Control flow
For packets, `seg6_local_input()` first rejects non-IPv6 packets, optionally runs the lwtunnel netfilter local-in hook, and then calls `seg6_local_input_core()`. The core retrieves the original route's lwtunnel state, dispatches to the action descriptor's input function, and updates optional per-CPU counters after the action returns.

Standard End and End.X validate the SRH and HMAC, decrement `segments_left`, update the IPv6 destination address, resolve the next route, and call `dst_input()`. End.X uses a configured IPv6 nexthop and optional output interface. End.T resolves within a configured table. NEXT-C-SID flavor paths shift the compressed SID argument in the destination address until the argument becomes zero, then fall back to normal End or End.X processing. RFC8986 PSP flavor support uses a packet-info/action lookup table and `seg6_pop_srh()` to remove the SRH at the penultimate segment.

Decapsulation actions call `decap_and_validate()` to reject packets with nonzero `segments_left`, validate HMAC, find the inner protocol, pull the outer headers, reset checksum state, and clear tunnel offload metadata. End.DX2 forwards an inner Ethernet frame through a configured Ethernet device after MTU, carrier, LRO, and protocol checks. End.DX6 and End.DX4 decapsulate IPv6 or IPv4, reset conntrack, optionally run prerouting hooks, route to an explicit or inner destination nexthop, and re-enter the stack with `dst_input()`.

End.DT4/DT6/DT46 route decapsulated traffic through a VRF table when `CONFIG_NET_L3_MASTER_DEV` is available. Build-time hooks map the configured VRF table to a VRF ifindex and enforce strict-mode requirements. Runtime processing presents the decapsulated packet as received by the VRF master and then routes it. Legacy DT6 table mode remains supported when a plain table attribute is configured.

End.B6 inserts an SRH inline after validating the current SRH. End.B6.Encaps advances the current SRH, marks inner headers, encapsulates with a new outer IPv6/SRH stack, and routes. End.BPF advances the current SRH, exposes a per-CPU mutable SRH state to `BPF_PROG_TYPE_LWT_SEG6LOCAL`, validates any BPF-edited SRH, and either routes normally or honors BPF redirect.

Netlink build flow parses a nested `SEG6_LOCAL_ACTION`, finds the descriptor, parses required attributes first, optional attributes second, then runs a behavior-specific constructor such as the End.DT VRF builder. Failures unwind any resources acquired by parsed attributes.

## State and persistence
All state is in kernel memory attached to a route's lwtunnel state. SRH templates and BPF names are dynamically allocated; BPF programs hold references; counters are per-CPU `pcpu_seg6_local_counters`; VRF mode records a net pointer, ifindex, table, family, and mode. No state persists beyond route/lwtunnel lifetime or module lifetime. Counter aggregation for netlink dumps uses `u64_stats_sync` to read per-CPU packet, byte, and error counters safely.

## Dependencies and integration points
This file integrates with the IPv6 route/FIB stack, lwtunnel core, SRv6 UAPI, HMAC validation, BPF lwt seg6local helpers, VRF/l3mdev, netfilter lwtunnel hooks, dst cache/routing, IP tunnel decapsulation helpers, Ethernet device transmit, conntrack reset, and netlink attribute policy code. `seg6_local_init()` registers `seg6_local_ops`; `seg6_local_exit()` unregisters it.

## Risks and edge cases
SRH mutation is sensitive to skb writability, header offsets, checksum updates, and extension-header ordering. `seg6_pop_srh()` must correctly preserve transport header position and reject fragment/auth ordering that cannot be safely updated. Flavor masks must stay disjoint from unsupported operations, and NEXT-C-SID block/function lengths must remain byte-aligned and within 128 bits. End.DT VRF mode depends on strict VRF table mapping and netns consistency. Decapsulation paths must avoid accepting packets with residual SRH segments or stale offload/conntrack state. Optional attribute cleanup must not double-free resources when required and optional masks change. Netlink size accounting must match emitted attributes, especially counters, BPF nests, SRHs, and flavor nests.

## Test signals
Useful tests create routes with every `SEG6_LOCAL_ACTION`, validate missing/extra attributes, dump and compare lwtunnel state, and exercise counter increments on success and drop. Packet tests should cover End, End.X, End.T, PSP, NEXT-C-SID, DX2 MTU/device failures, DX4/DX6 prerouting hooks, DT4/DT6 VRF strict-mode failures, DT46 protocol selection, B6/B6.Encaps SRH insertion, invalid HMAC, SRH with nonzero `segments_left` on decap, malformed extension header chains, and BPF programs returning OK, DROP, REDIRECT, invalid return values, and invalid SRH edits.
