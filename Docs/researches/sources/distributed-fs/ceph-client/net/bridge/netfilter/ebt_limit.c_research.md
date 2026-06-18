# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_limit.c

## Purpose
Implements the legacy ebtables `limit` match, a token-bucket rate limiter for controlling how often a rule can match.

## Important APIs, Types, And Functions
Important code includes `ebt_limit_mt`, `ebt_limit_mt_check`, `user2credits`, global `limit_lock`, and `xt_match ebt_limit_mt_reg`. It uses `struct ebt_limit_info` and compat sizing for 32-bit userspace.

## Control Flow
Rule validation converts userspace average and burst into internal credits, detects overflow, initializes `prev`, `credit`, `credit_cap`, and `cost`. Runtime matching locks globally, refills credits based on elapsed jiffies, caps them, consumes a cost if available, and returns match/no-match.

## State And Persistence Behavior
This match mutates per-rule rate-limit state embedded in the rule blob. The state is memory-only and resets when rules are loaded/replaced. The global spinlock serializes all limit matches.

## Dependencies And Integration Points
Depends on jiffies, spinlocks, ebtables UAPI, xtables registration, and compat layout support. It follows the classic iptables limit-match model.

## Risks And Test Signals
Risks include arithmetic overflow, global lock contention, HZ-dependent conversion, and per-rule state reset on table replacement. Tests should validate burst/average behavior, overflow rejection, compat load, replacement reset, and concurrent packet paths.
