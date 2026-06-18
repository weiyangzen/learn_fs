# sources/distributed-fs/ceph-client/net/ipv4/netfilter/arpt_mangle.c

## Purpose
`arpt_mangle.c` implements the legacy ARP `mangle` target that rewrites ARP sender/target hardware and protocol addresses.

## Important APIs, Types, And Functions
The registered `xt_target` is named `mangle` for `NFPROTO_ARP`. `target()` performs payload rewriting based on `struct arpt_mangle` flags, and `checkentry()` validates flag and verdict combinations.

## Control Flow
At runtime the target ensures the skb is writable, walks the ARP payload using `ar_hln` and `ar_pln`, bounds-checks each requested field against fixed maximums and the skb tail, writes requested source/target fields, and returns the configured verdict (`DROP`, `ACCEPT`, or `XT_CONTINUE`).

## State And Persistence
No per-net state is owned. Persistent state is only the module registration and rule-provided `arpt_mangle` target data.

## Dependencies And Integration Points
It is invoked by `arp_tables.c` after ARP rule matching and is built for `IP_NF_ARP_MANGLE`. It depends on ARP header layout, skb writability helpers, and FireWire ARP special handling.

## Risks
Risks include malformed ARP length fields, non-linear skb write failures, target address rewriting on FireWire ARP, and invalid target verdicts.

## Test Signals
Test all four rewrite flags, mixed rewrites with `XT_CONTINUE`, invalid flags, invalid verdicts, short/truncated ARP packets, non-linear skbs, and FireWire target-hardware/protocol rewrite rejection.
