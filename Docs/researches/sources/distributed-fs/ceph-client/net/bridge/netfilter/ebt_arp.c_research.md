# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_arp.c

## Purpose
Implements the legacy ebtables `arp` match for ARP/RARP header fields, IPv4 sender/target protocol addresses, Ethernet sender/target hardware addresses, and gratuitous ARP detection.

## Important APIs, Types, And Functions
The module centers on `ebt_arp_mt`, `ebt_arp_mt_check`, and `xt_match ebt_arp_mt_reg`, using `struct ebt_arp_info` from UAPI.

## Control Flow
The matcher safely reads the ARP header and requested payload fields with `skb_header_pointer`, validates protocol/hardware lengths before address matching, applies masks to IP and MAC fields, and honors ebtables inversion flags. Checkentry requires ARP or RARP ethproto without inverted protocol match and rejects unknown bitmask or inversion bits.

## State And Persistence Behavior
No mutable state is stored. Per-rule match criteria live in ebtables rule memory.

## Dependencies And Integration Points
Depends on ARP/Ethernet headers, ebtables core validation, masked Ethernet comparison helpers, and xtables registration. It is typically used with rules whose base ethproto is ARP/RARP.

## Risks And Test Signals
Risks include offset mistakes for variable ARP hardware/protocol lengths and matching incomplete packets. Useful tests cover each field, masks, inversion, gratuitous ARP, RARP, invalid ethproto rejection, and truncated ARP frames.
