<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_hl.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_hl.c

## Purpose
`xt_hl.c` implements IPv4 TTL and IPv6 Hop Limit matching. It supports equality, less-than, and greater-than comparisons against the packet header hop-count field.

## Important APIs, Types, and Functions
`ttl_mt()` handles IPv4 and `hl_mt6()` handles IPv6, both consuming `struct xt_hl_info`. `ttl_mt_check()` and `hl_mt6_check()` validate comparison mode. `hl_mt_reg[]` registers `ttl` for IPv4 and `hl` for IPv6.

## Control Flow, State, and Persistence
Each packet path reads the TTL or hop-limit byte from the network header and applies `XT_HL_EQ`, `XT_HL_NE`, `XT_HL_LT`, or `XT_HL_GT` style mode semantics as encoded by the UAPI. There is no persistent state.

## Dependencies and Integration Points
The module integrates with x_tables and IP header helpers. It is often paired with TTL/HL mangling targets elsewhere, but this file only matches.

## Risks and Test Signals
Risks are simple boundary and mode errors: TTL zero, 255, unsupported modes, and IPv4/IPv6 name differences. Tests should cover equality, not-equal/inverted mode, less-than, greater-than, invalid mode rejection, and both families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_hl.c -->
