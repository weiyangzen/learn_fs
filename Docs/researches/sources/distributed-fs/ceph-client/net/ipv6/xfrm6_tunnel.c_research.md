# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_tunnel.c

## Purpose
Implements IPv6 XFRM tunnel SPI dispatch for tunnel-mode security protocols. It maintains per-net hash tables mapping SPI and remote address to tunnel handlers, supports wildcard fallback, exposes register/deregister APIs for tunnel protocol handlers, and registers ESP/AH/IPCOMP tunnel receive adapters.

## Important APIs, types, and functions
Exports `xfrm6_tunnel_register` and `xfrm6_tunnel_deregister`. Important routines include `xfrm6_tunnel_spi_lookup`, `xfrm6_tunnel_input`, `xfrm6_tunnel_rcv`, `xfrm6_tunnel_err`, `xfrm6_tunnel_init`, and `xfrm6_tunnel_fini`. Static protocol descriptors are `xfrm6_tunnel_esp`, `xfrm6_tunnel_ah`, and `xfrm6_tunnel_ipcomp`.

## Control flow
Handlers are stored per net namespace in two hash tables: one for exact remote address/SPI and one for priority-ordered wildcard handlers. Lookup first hashes the source address and SPI, then falls back to wildcard entries. Receive entry `xfrm6_tunnel_input` extracts SPI from the protocol header, finds a handler, calls it, or discards the skb and increments no-state stats. Protocol-specific wrappers pass ESP/AH/IPCOMP IDs to the common receive path and route errors to matching handler error callbacks when available.

Registration allocates an `xfrm6_tunnel_net`, inserts exact or wildcard handlers under lock, and uses priority ordering for wildcard entries. Deregistration removes the matching handler and frees the node after RCU grace protection.

## State and persistence behavior
State is per-net handler registration data, protected by locks and RCU. No persistent disk state exists. Lifetime is tied to network namespaces and protocol module registration.

## Dependencies and integration points
Depends on XFRM protocol registration from `xfrm6_protocol.c`, pernet operations, IPv6 address hashing/comparison, XFRM stats, RCU, and tunnel modules that provide `struct xfrm6_tunnel` callbacks. It integrates with inbound IPsec tunnel packets after protocol dispatch.

## Risks and test signals
Risks include handler ordering mistakes for wildcard tunnels, stale RCU nodes after deregistration, SPI/address hash collisions, and error callback routing to the wrong tunnel. Test exact and wildcard tunnel handlers, multiple priorities, handler unregister under traffic, ESP/AH/IPCOMP tunnel receive, ICMPv6 error callbacks, and per-net namespace isolation.
