<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_u32.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_u32.c

## Purpose
`xt_u32.c` implements arbitrary 32-bit packet content matching using a compact expression language from iptables `u32`.

## Important APIs, Types, and Functions
`u32_match_it()` interprets `struct xt_u32` tests, reading packet words with `skb_copy_bits()`. `u32_mt()` applies global inversion. `u32_mt_checkentry()` validates counts against fixed arrays in `struct xt_u32_test`.

## Control Flow, State, and Persistence
For each ANDed test, the interpreter reads an initial packet offset, applies a sequence of AND/left-shift/right-shift/AT operations, then checks whether the resulting value falls in any configured min/max range. Bounds and overflow checks prevent out-of-skb reads. The module stores no state.

## Dependencies and Integration Points
It depends on x_tables and skb byte-copy helpers. Because offsets are packet-relative, userspace expressions must account for IP header sizes and encapsulation.

## Risks and Test Signals
Risks include expression validation gaps, offset arithmetic overflow, nonlinear skb reads, endian assumptions, and user confusion over dynamic `@` offsets. Tests should cover simple fixed offsets, chained arithmetic, `@` indirection, multiple tests and ranges, inversion, boundary offsets at `skb->len - 4`, overflow attempts, invalid ntests/nnums/nvalues, and IPv4/IPv6 packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_u32.c -->
