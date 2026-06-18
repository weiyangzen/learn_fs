# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_snat.c

## Purpose
Implements the legacy ebtables `snat` target for source MAC rewriting in bridge nat postrouting, with optional ARP sender hardware address rewriting.

## Important APIs, Types, And Functions
Core functions are `ebt_snat_tg`, `ebt_snat_tg_check`, and `xt_target ebt_snat_tg_reg`, using `struct ebt_nat_info` and the `NAT_ARP_BIT` verdict flag.

## Control Flow
Runtime ensures the Ethernet header is writable, copies the configured MAC into `h_source`, optionally updates the ARP sender hardware address for ARP frames, and returns the encoded verdict. Validation checks base-chain `RETURN`, ebtables target validity, and that only expected NAT_ARP bits accompany the verdict.

## State And Persistence Behavior
The target mutates the current skb Ethernet source and optionally ARP payload. No module-level or durable state exists.

## Dependencies And Integration Points
Depends on ARP helpers, ebtables nat UAPI, bridge postrouting hook registration via the nat table, and xtables target registration.

## Risks And Test Signals
Risks include inconsistent Ethernet/ARP source rewriting, failure on non-writable skbs, and target-bit encoding mistakes. Tests should cover ARP and non-ARP frames, NAT_ARP_BIT behavior, invalid verdicts, base-chain return rejection, and postrouting hook constraints.
