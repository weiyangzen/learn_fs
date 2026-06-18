# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_ip.c

## Purpose

`ip_set_bitmap_ip.c` implements the `bitmap:ip` IP set type for IPv4 addresses or IPv4 network addresses inside a bounded range. It is efficient for dense, known ranges because membership is a bit indexed by address or subnet offset.

## Important APIs And Types

The module registers `bitmap_ip_type` with name `bitmap:ip`, feature `IPSET_TYPE_IP`, dimension one, family `NFPROTO_IPV4`, and revisions 0 through 3. `struct bitmap_ip` stores the member bitset, first and last IP in host byte order, number of elements, hosts per stored subnet, memory size, netmask, GC timer, set backpointer, and extension storage. `struct bitmap_ip_adt_elem` carries the computed element ID.

Type-specific callbacks include `bitmap_ip_do_test`, `bitmap_ip_do_add`, `bitmap_ip_do_del`, `bitmap_ip_do_list`, `bitmap_ip_do_head`, `bitmap_ip_kadt`, `bitmap_ip_uadt`, and `bitmap_ip_same_set`. Including `ip_set_bitmap_gen.h` generates the variant used by the core.

## Control Flow

Creation requires `IPSET_ATTR_IP` and either `IPSET_ATTR_IP_TO` or `IPSET_ATTR_CIDR`. It normalizes range order, applies optional `IPSET_ATTR_NETMASK`, computes `hosts` and `elements`, rejects ranges larger than `IPSET_BITMAP_MAX_RANGE + 1`, computes extension size with `ip_set_elem_len`, allocates the map plus extension storage, allocates the member bitmap, and starts GC if a timeout was requested.

Kernel ADT extracts the IPv4 source or destination address from the skb, rejects values outside the configured range, converts the IP to an ID with `ip_to_id`, and dispatches to add/delete/test. Userspace ADT parses a single IP, optional `IP_TO` or CIDR range for add/delete, extensions, and then loops by `map->hosts` across the requested range. Test operates on only one address.

## State And Persistence

State is in the bitmap and optional per-entry extension storage. `set->timeout` and the generated GC timer expire elements. `set->family` is fixed to IPv4. There is no persistent storage in the module; userspace must restore sets after reboot.

## Dependencies And Integration

The module depends on ipset prefix helpers, netlink attribute parsing, skb IPv4 address helpers, the bitmap template, and core extension helpers. It integrates with `ipset(8)` through nfnetlink and with xtables/nftables set matching through `kadt`.

## Risks

Range arithmetic is the critical area. Netmask and CIDR normalization must avoid overflow and must reject impossible ranges. Large ranges can consume significant memory, so the `IPSET_BITMAP_MAX_RANGE` check is important. Address zero handling is not globally forbidden here, unlike hash types; tests should confirm intended behavior for ranges including zero. Extension layout must remain aligned with empty `struct bitmap_ip_elem`.

## Test Signals

Create sets from explicit ranges and CIDR ranges, with and without netmask and timeout. Add, delete, test, and list single IPs and ranges; test boundary addresses, reversed ranges, invalid CIDR/netmask, range-size errors, timeout expiry, counters/comments/skbinfo, and packet-path source versus destination matching.
