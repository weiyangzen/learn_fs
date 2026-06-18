# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_ECN.c

## Purpose
`ipt_ECN.c` implements the legacy IPv4 `ECN` target for the mangle table, modifying ECN bits in the IPv4 TOS field and optionally TCP ECE/CWR flags.

## Important APIs, Types, And Functions
The target is `ecn_tg_reg`. Important functions are `set_ect_ip()`, `set_ect_tcp()`, `ecn_tg()`, and `ecn_tg_check()`.

## Control Flow
The target applies configured IP ECN changes after making the IP header writable and updating the IPv4 checksum. If TCP flag operations are requested and the packet is TCP, it reads the TCP header, ensures it is writable, updates ECE/CWR bits, and adjusts the TCP checksum.

## State And Persistence
No mutable global state. Rule state is `struct ipt_ECN_info` stored in the installed xtables rule.

## Dependencies And Integration Points
It integrates with `ip_tables.c` target execution, mangle table restrictions, skb writable helpers, IPv4 and TCP checksum update helpers, and the target check path that verifies TCP-only operations.

## Risks
Risks include checksum update mistakes, truncated TCP headers, non-linear skb write failures, accepting TCP flag operations on non-TCP rules, and incorrect operation-mask validation.

## Test Signals
Test IP ECN-only rewrite, TCP ECE/CWR rewrite, no-op cases, truncated TCP packets, non-linear skbs, invalid operation bits, invalid ECN codepoints, and non-TCP rule rejection.
