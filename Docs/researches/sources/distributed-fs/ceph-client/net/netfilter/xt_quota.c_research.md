<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_quota.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_quota.c

## Purpose
`xt_quota.c` implements a countdown quota match. A rule matches until a configured byte quota is exhausted, optionally in inverted mode.

## Important APIs, Types, and Functions
`struct xt_quota_priv` stores a spinlock and remaining quota. `quota_mt()` decrements quota by `skb->len`. `quota_mt_check()` allocates private state from `struct xt_quota_info`, and `quota_mt_destroy()` frees it.

## Control Flow, State, and Persistence
On insertion, the configured quota is copied to per-rule private memory. Each packet locks the quota, checks whether enough bytes remain, subtracts packet length when it does, and returns match or inverted match. The remaining quota persists for the life of the rule and is not reset by time.

## Dependencies and Integration Points
The module integrates with x_tables rule lifecycle and skb length accounting. It is protocol-unspecified and can apply to IPv4 and IPv6.

## Risks and Test Signals
Risks include shared mutable state across CPUs, expectations around rule replacement resetting quota, skb length including headers, and large packet/quota boundary behavior. Tests should cover exact exhaustion, over-quota packet behavior, inversion, SMP contention, rule reload reset, destroy cleanup, and zero quota.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_quota.c -->
