<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_statistic.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_statistic.c

## Purpose
`xt_statistic.c` implements probabilistic and nth-packet matching. It supports random sampling and deterministic every-N packet selection.

## Important APIs, Types, and Functions
`struct xt_statistic_priv` stores nth-mode counter state with a spinlock. `statistic_mt()` handles `XT_STATISTIC_MODE_RANDOM` and `XT_STATISTIC_MODE_NTH`. `statistic_mt_check()` validates mode and allocates private state for nth mode; `statistic_mt_destroy()` frees it.

## Control Flow, State, and Persistence
Random mode compares a random 31-bit value against configured probability. Nth mode decrements or resets a shared counter under lock and matches when the configured packet interval is reached. Nth counter state persists for the life of the rule.

## Dependencies and Integration Points
The module depends on x_tables, kernel random number generation, and per-rule private memory. It is protocol-unspecified.

## Risks and Test Signals
Risks include probability scaling, shared nth state across CPUs, off-by-one packet intervals, and rule replacement resetting counters. Tests should cover random probability extremes, statistical distribution, nth every/packet offsets, inversion, SMP traffic, invalid modes, allocation failure, and destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_statistic.c -->
