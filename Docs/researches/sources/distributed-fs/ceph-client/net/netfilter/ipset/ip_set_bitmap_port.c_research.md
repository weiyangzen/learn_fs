# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_port.c

## Purpose

`ip_set_bitmap_port.c` implements the `bitmap:port` set type for a dense range of transport-layer ports. It supports packet-path matching for TCP and UDP over IPv4 or IPv6, while userspace can add, delete, test, and list numeric port ranges.

## Important APIs And Types

The module registers `bitmap_port_type` with name `bitmap:port`, feature `IPSET_TYPE_PORT`, dimension one, family `NFPROTO_UNSPEC`, and revisions 0 through 3. `struct bitmap_port` stores the member bitmap, first/last ports, number of elements, memory size, GC timer, set backpointer, and extension storage. `struct bitmap_port_adt_elem` stores the computed ID.

The local helper `ip_set_get_ip_port` calls `ip_set_get_ip4_port` or `ip_set_get_ip6_port`, then accepts only `IPPROTO_TCP` and `IPPROTO_UDP` for this bitmap type. Common bitmap callbacks handle bit testing, adding, deleting, listing, and header output.

## Control Flow

Creation requires network-order `IPSET_ATTR_PORT` and `IPSET_ATTR_PORT_TO`, optional timeout and create flags, normalizes reversed ranges, computes `elements = last - first + 1`, calculates extension size, allocates map and bitmap, and starts timeout GC if needed.

Kernel ADT extracts the requested source or destination port from the skb based on family and dimension flags. If the protocol is unsupported, the L4 header is unavailable, or the port is outside the configured range, it returns an error. Userspace ADT parses a single port and optional `PORT_TO`, validates the range, parses extensions, and loops over every port for add/delete. Test checks a single port.

## State And Persistence

Membership is a dense bitset indexed by `port - first_port`. Extension state and timeout state are stored in the generic bitmap extension area. `set->family` is unspecified so the same set can serve IPv4 and IPv6 packet paths. There is no persistent kernel storage.

## Dependencies And Integration

The module depends on `ip_set_getport.c` for safe L4 extraction from non-linear skbs, on the bitmap template for ADT implementation, and on ipset core extension helpers. It integrates with packet rules that match source or destination TCP/UDP ports through ipset.

## Risks

The helper accepts only TCP and UDP even though `ip_set_getport.c` can parse SCTP, UDPLITE, and ICMP pseudo-ports. That is intentional for this set type but should be preserved in tests. Range loops use `u32 port` to avoid wraparound but still need boundary coverage around 0 and 65535. Non-linear skb parsing and fragments must fail safely.

## Test Signals

Create sets for small and full port ranges. Add/delete/test individual ports and ranges, including reversed inputs and endpoints 0 and 65535. Exercise TCP and UDP source/destination packet matching for IPv4 and IPv6, unsupported protocols, fragmented packets, timeout expiry, counters, comments, skbinfo, and list output.
