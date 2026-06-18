# sources/distributed-fs/ceph-client/net/ipv4/netfilter.c

## Purpose
`netfilter.c` provides IPv4-specific routing helpers used by netfilter modules after packet mangling or for route lookups from generic netfilter code.

## Important APIs, Types, And Functions
Exports are `ip_route_me_harder()` and `nf_ip_route()`. `ip_route_me_harder()` reroutes an skb after source/destination/TOS/mark changes and optionally performs XFRM lookup. `nf_ip_route()` wraps `ip_route_output_key()` for generic netfilter routing.

## Control Flow
`ip_route_me_harder()` derives a `flowi4` from the current IP header, socket, mark, L3 master, source address type, and early flow dissection, then installs a new dst. If XFRM is enabled and the packet has not already been transformed, it decodes and applies an XFRM route. Finally it expands headroom if the output device hard-header length increased.

## State And Persistence
No persistent state is owned. The function mutates the skb destination, may steal/drop dst references, and may expand skb headroom.

## Dependencies And Integration Points
Callers include mangle/NAT/queue/reject paths that need a packet rerouted after header or mark changes. It depends on FIB routing, L3 master devices, XFRM, flow dissector integration, and skb dst/headroom APIs.

## Risks
Risks include using a foreign source address incorrectly, missing XFRM policy application, returning with insufficient headroom, dst reference mistakes, and subtle behavior changes for locally generated packets using non-standard sources.

## Test Signals
Test mangle `LOCAL_OUT` reroute after mark, TOS, source, and destination changes; XFRM policy interaction; bound socket output interfaces; VRF/L3 master behavior; and failure paths for route lookup, XFRM lookup, and head expansion.
