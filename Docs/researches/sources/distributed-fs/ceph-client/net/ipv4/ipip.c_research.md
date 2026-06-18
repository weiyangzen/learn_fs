# sources/distributed-fs/ceph-client/net/ipv4/ipip.c

## Purpose
Implements the concrete IPIP tunnel driver for IPv4-over-IPv4 and, when enabled, MPLS-over-IPv4. It registers the `ipip` rtnetlink kind and fallback `tunl0`, handles IPIP/MPLS receive and ICMP errors, validates tunnel protocols, drives generic tunnel transmit/receive helpers, supports collect-metadata and optional tunnel encapsulation attributes, and exposes forward-path information.

## APIs, Types, and Functions
The module initializes with `ipip_init()` and exits with `ipip_fini()`. Key functions are `ipip_err()`, `ipip_tunnel_rcv()`, `ipip_rcv()`, optional `mplsip_rcv()`, `ipip_tunnel_xmit()`, `ipip_tunnel_ctl()`, `ipip_fill_forward_path()`, `ipip_tunnel_setup()`, `ipip_tunnel_init()`, `ipip_tunnel_validate()`, `ipip_netlink_parms()`, `ipip_newlink()`, `ipip_changelink()`, `ipip_get_size()`, `ipip_fill_info()`, and pernet `ipip_init_net()`/`ipip_exit_rtnl()`. Static objects include `ipip_link_ops`, `ipip_handler`, optional `mplsip_handler`, `ipip_policy`, and module parameter `log_ecn_error`.

## Control Flow
Inbound packets arrive through XFRM tunnel handlers. `ipip_tunnel_rcv()` looks up a keyless tunnel by outer source/destination/link, validates configured protocol, checks XFRM inbound policy, pulls the outer header, optionally creates metadata dst for collect-md, resets the MAC header, and calls `ip_tunnel_rcv()` with IP or MPLS packet info. ICMP errors locate the reverse tunnel and update PMTU, process redirects, or record soft errors for connected tunnels.

Transmit validates the inner protocol, ensures it matches configured `tiph->protocol`, prepares offloads with `SKB_GSO_IPXIP4`, records inner IP protocol, and dispatches either metadata transmit or configured `ip_tunnel_xmit()`. Rtnetlink newlink parses generic tunnel params, encap params, collect metadata, and fwmark; changelink forbids switching to collect-md and enforces point-to-point flag consistency.

## State and Persistence
Per-net state is generic `ip_tunnel_net` under `ipip_net_id`, including fallback `tunl0`. Each tunnel stores configured IPv4 header params, encap settings, fwmark, collect-md flag, dst cache, error count/time, and device stats. The module persists XFRM tunnel registrations for AF_INET and optional AF_MPLS, rtnl link ops, pernet operations, and the `log_ecn_error` module parameter.

## Dependencies and Integration
Depends on the generic tunnel library, XFRM tunnel registration, rtnetlink, netdevice ops, IPv4 route/ICMP helpers, metadata dst, optional MPLS, tunnel offload/GSO helpers, netlink policies for `IFLA_IPTUN_*`, and legacy private ioctls through the generic tunnel control path.

## Risks
Risks include accepting malformed or mismatched protocol tunnel parameters, collect-md singleton conflicts handled in the generic layer, ECN error logging noise, short ICMP payloads limiting precise error relay, PMTU/redirect propagation to wrong link/protocol, offload handling for MPLS payloads, and changelink constraints around point-to-point versus wildcard tunnels.

## Test Signals
Tests should cover creating `ipip` and `tunl0` devices, configured and wildcard remote endpoints, IPv4 and MPLS payloads, collect-md mode, netlink dump/change validation, legacy SIOC add/change/delete, PMTU and redirect ICMP handling, ECN decapsulation logging, forward-path reporting, offloaded/GSO packets, namespace teardown, and module load/unload registration cleanup.
