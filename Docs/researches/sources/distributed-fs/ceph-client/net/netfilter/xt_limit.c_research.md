<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_limit.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_limit.c

## Purpose
`xt_limit.c` implements the classic global token-bucket `limit` match. It rate-limits matches for a rule, not per source or destination.

## Important APIs, Types, and Functions
`struct xt_limit_priv` stores spinlock-protected `prev` and `credit`. `limit_mt()` performs token accounting using `struct xt_rateinfo`. `user2credits()` converts userspace rates into internal credit units. `limit_mt_check()` allocates and initializes private state; `limit_mt_destroy()` frees it. Compat handlers translate 32-bit userspace layouts.

## Control Flow, State, and Persistence
On rule insertion, checkentry validates burst and overflow conditions, allocates `xt_limit_priv`, and initializes credit to the burst cap. Packet evaluation locks the private state, refills credit from elapsed jiffies up to `credit_cap`, and if enough credit is available subtracts `cost` and matches. The state persists for the life of the rule.

## Dependencies and Integration Points
The module integrates with x_tables match lifecycle and compat translation for mixed 32/64-bit userspace. It uses kernel jiffies and a per-rule spinlock.

## Risks and Test Signals
Risks include arithmetic overflow in rate conversion, compat pointer layout errors, rule sharing expectations, and jiffies wrap behavior. Tests should cover low and high rates, burst exhaustion and refill, SMP contention, compat from/to user conversion, destroy cleanup, invalid overflow inputs, and IPv4/IPv6 aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_limit.c -->
