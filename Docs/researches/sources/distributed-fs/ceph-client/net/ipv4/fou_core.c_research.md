# sources/distributed-fs/ceph-client/net/ipv4/fou_core.c

## Purpose
`fou_core.c` implements Foo-over-UDP and Generic UDP Encapsulation support for IPv4 and optionally IPv6 sockets. It creates UDP tunnel sockets, receives and decapsulates FOU/GUE traffic, provides GRO/GSO integration, exposes generic netlink control, exports tunnel header builders, and registers IP tunnel encapsulation operations.

## Important APIs, Types, And Functions
`struct fou` is the per-port object with socket, protocol, flags, port, address family, encap type, list node, and RCU head. `struct fou_cfg` contains parsed netlink/UDP socket configuration. Per-net state is `struct fou_net`, a list plus mutex.

Receive paths are `fou_udp_recv` and `gue_udp_recv`. GRO paths are `fou_gro_receive`, `fou_gro_complete`, `gue_gro_receive`, and `gue_gro_complete`. Configuration paths are `parse_nl_config`, `fou_nl_add_doit`, `fou_nl_del_doit`, `fou_nl_get_doit`, and `fou_nl_get_dumpit`. Tunnel export functions include `fou_encap_hlen`, `gue_encap_hlen`, `__fou_build_header`, and `__gue_build_header`. Optional IP tunnel operations are registered by `ip_tunnel_encap_add_fou_ops`.

## Control Flow
Netlink add parses address family, local/peer ports, local/peer addresses, interface binding, encap type, IP protocol, and remcsum flag into `fou_cfg`. `fou_create` opens a UDP socket, allocates `struct fou`, installs UDP tunnel callbacks, sets `sk_user_data`, marks allocation atomic, and inserts the object into the per-net list after duplicate detection. Delete parses the same identity and calls `fou_destroy`, which removes the list entry, releases the UDP tunnel socket, and frees the object with RCU.

FOU direct receive removes the UDP header, updates IPv4 total length or IPv6 payload length, pulls checksum state, resets transport header, calls `iptunnel_pull_offloads`, and returns negative protocol to the UDP tunnel core. GUE receive validates the base header, supports version 1 direct IPv4/IPv6 encapsulation, validates optional flags for version 0, handles private remote-checksum data, drops unsupported control messages, pulls GUE/UDP headers, and returns the encapsulated protocol.

GRO mirrors the decapsulation logic without fully linearizing the packet. It identifies the next protocol's `net_offload`, marks FOU state in `NAPI_GRO_CB`, validates GUE headers and optional fields, handles remote checksum offload, compares GUE headers across candidate packets, and delegates to the inner protocol GRO callbacks. Completion delegates to the inner offload and sets inner MAC headers.

Transmit header builders prepare tunnel offload state with `iptunnel_handle_offloads`, choose a UDP source port from flow hash if not configured, optionally build a GUE private remcsum option, push the GUE header, then optional IP tunnel ops push the UDP header and set checksum.

## State And Persistence
FOU state is per network namespace. Each `struct fou` persists until netlink deletion or namespace teardown. It owns a UDP socket and is discoverable by list under `fou_lock`. Socket `sk_user_data` points to the FOU object and is read under socket/RCU conventions. Module init registers pernet state, generic netlink family, BPF kfuncs, and tunnel encap ops; module exit reverses these and closes all sockets.

## Dependencies And Integration Points
The file depends on UDP tunnel socket infrastructure, generic netlink policy/ops from `fou_nl.c`, BPF registration from `fou_bpf.c`, GUE helpers, IP tunnel encap registration, inet and inet6 offload tables, ICMP error dispatch through `inet_protos`, and network namespace generic storage. User space configures it through the `fou` generic netlink family defined by UAPI `linux/fou.h`.

## Risks
Header length and checksum manipulation are the main risk. GUE option validation, remote checksum offsets, and GRO remcsum state must remain consistent with skb pulls. Duplicate detection must include family, local/peer ports, addresses, and bound interface. The netlink parser allows partial identities, so add/delete/get must reject ambiguous cases where required peer or bind information is missing. Error handlers must avoid recursion for UDP-in-GUE.

## Test Signals
Test netlink add/get/dump/delete for IPv4, IPv6, peer-bound, and device-bound sockets; duplicate add should return `-EALREADY`. Exercise FOU direct and GUE v0/v1 receive, malformed GUE option drops, remote checksum offload, GRO aggregation and flush decisions, tunnel transmit with checksum and remcsum flags, ICMP error propagation, namespace teardown cleanup, and module init failure unwind after each registration step.
