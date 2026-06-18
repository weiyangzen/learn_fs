# sources/distributed-fs/ceph-client/net/netfilter/ipset/pfxlen.c

## Purpose

`pfxlen.c` provides shared prefix-length helper data for ipset code. It exports precomputed IPv4/IPv6 netmask and hostmask maps and a helper that converts an IPv4 address range into the largest CIDR block starting at the range's left edge.

## Important APIs, types, and functions

`PREFIXES_MAP` is a macro-generated table of 129 four-word masks. `ip_set_netmask_map[]` exports network-order masks using `htonl()` for each word. `ip_set_hostmask_map[]` exports the same bit patterns as forced big-endian words for hostmask helper use. Both arrays are `union nf_inet_addr` and are exported with `EXPORT_SYMBOL_GPL`. `ip_set_range_to_cidr(u32 from, u32 to, u8 *cidr)` scans prefix lengths from 1 to 31, finds the largest aligned block whose last address does not exceed `to`, writes the CIDR, and returns the block's last address; if no broader block fits, it returns the single address with CIDR 32.

## Control flow

Consumers index the maps by prefix length for IPv4 or IPv6 masking. Range conversion is host-order IPv4 only: the loop checks alignment using `ip_set_hostmask(i)`, computes `last = from | ~ip_set_hostmask(i)`, and uses `after(last, to)` to avoid selecting a block beyond the requested range. The exported function is repeatedly called by hash set userspace add paths to decompose ranges into CIDR entries.

## State and persistence behavior

The file contains immutable exported tables and no runtime mutable state. The arrays persist for the lifetime of the module/kernel and are shared by ipset modules.

## Dependencies and integration points

Dependencies are limited to `linux/export.h` and `linux/netfilter/ipset/pfxlen.h`. Integration points include all ipset hash types that need `ip_set_netmask()`, `ip_set_hostmask()`, `ip6_netmask()`, or `ip_set_range_to_cidr()` for prefix normalization and range expansion.

## Risks

The maps must remain exactly aligned to prefix length indexes 0 through 128; any missing or reordered entry would corrupt every prefix match. `ip_set_range_to_cidr()` does not special-case the full IPv4 range as `/0`; callers that allow `/0` need their own wrapper, as `hash:net,port,net` does. The function assumes host-order IPv4 inputs.

## Test signals

Tests should validate masks at representative prefix lengths 0, 1, 31, 32, 33, 64, 96, 127, and 128; verify range-to-CIDR decomposition for aligned and unaligned ranges; confirm single-address `/32`; and include a caller-level test for full-range behavior where `/0` is expected.
