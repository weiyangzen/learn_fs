# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_mark.c

## Purpose
Implements the legacy ebtables `mark` target for setting, ORing, ANDing, or XORing `skb->mark`, returning a verdict encoded in the same target field.

## Important APIs, Types, And Functions
Important functions are `ebt_mark_tg`, `ebt_mark_tg_check`, compat conversion helpers, and `xt_target ebt_mark_tg_reg`, using `struct ebt_mark_t_info`.

## Control Flow
At runtime the high action bits select set/or/and/xor against `skb->mark`, and the low verdict bits are returned as the ebtables verdict. Validation checks base-chain return rules, target validity, and allowed mark actions. Compat helpers translate `unsigned long` mark layout for 32-bit userspace.

## State And Persistence Behavior
The target mutates only the current skb mark. Rule parameters are immutable and there is no persistent storage.

## Dependencies And Integration Points
Depends on ebtables mark-target UAPI, xtables target registration, and ebtables verdict encoding. Its output can be consumed by `ebt_mark_m.c`, tc, routing, or later netfilter logic.

## Risks And Test Signals
Risks include mixed action/verdict bit handling, compat width conversion, and invalid target acceptance. Tests should cover all four actions, verdict preservation, base-chain return rejection, and 32-bit compat rule round trips.
