# sources/distributed-fs/ceph-client/net/tipc/udp_media.c

## Purpose
Implements the UDP bearer media for TIPC. It maps TIPC media addresses to IPv4/IPv6 UDP endpoints, creates UDP tunnel sockets, transmits and receives TIPC packets over UDP, supports multicast and replicast peer discovery, and exports UDP bearer details through netlink.

## Important APIs, Types, And Functions
`struct udp_media_addr` stores protocol, port, and IPv4/IPv6 address in network byte order. `struct udp_replicast` stores a remote peer with a dst cache and RCU list node. `struct udp_bearer` ties a TIPC bearer to a UDP socket, interface index, cleanup work, and replicast list. The exported `udp_media_info` supplies generic media callbacks: send, enable, disable, address string/message conversion, and defaults. Public netlink helpers dump/add remote IPs and bearer data.

## Control Flow And State
Enable parses local and remote sockaddr netlink attributes, validates protocol match, finds the local device, autoconfigures node identity if needed, creates a UDP socket, installs `tipc_udp_recv` as the tunnel receive callback, initializes dst caches, joins multicast or adds an initial replicast peer, and attaches `udp_bearer` via RCU. Send expands headroom, marks the inner protocol as TIPC, then either unicasts/multicasts through `tipc_udp_xmit` or copies packets across the replicast peer list. Receive strips the UDP header, forwards packets to `tipc_rcv` if the bearer is up, and learns replicast peers from discovery packets when appropriate. Disable marks the socket dead, clears the bearer pointer, schedules cleanup outside rtnl, destroys dst caches, releases the UDP socket, synchronizes networking readers, and frees memory.

## Dependencies And Integration Points
Uses Linux UDP tunnel APIs, IPv4/IPv6 routing, multicast joins, dst caches, rtnl/RCU, TIPC bearer/netlink/core/node identity, and TIPC receive path. Netlink policies from `netlink.h` define accepted UDP options.

## Risks And Test Signals
Risks include RCU lifetime between bearer disable and receive, route-cache correctness under address changes, multicast scope/device selection, headroom expansion failures, replicated skb copy failures, peer-list races under rtnl, and IPv6 scope-id validation. Test signals include IPv4 and IPv6 UDP bearers, multicast and replicast setups, remote IP add/dump, device down cleanup, packet receive after disable, low-MTU rejection via header helper, and route/cache invalidation scenarios.
