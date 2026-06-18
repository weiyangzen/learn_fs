# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_mark_m.c

## Purpose
Implements the legacy ebtables `mark_m` match for comparing `skb->mark` against a value/mask or checking whether any masked bits are set.

## Important APIs, Types, And Functions
Core items are `ebt_mark_mt`, `ebt_mark_mt_check`, compat conversion helpers, and `xt_match ebt_mark_mt_reg`, using `struct ebt_mark_m_info`.

## Control Flow
Runtime matching either tests any masked bit with `EBT_MARK_OR` or checks exact `(mark & mask) == mark`, then applies the invert flag. Checkentry rejects unknown mode bits, simultaneous OR/AND modes, and empty mode masks.

## State And Persistence Behavior
The match reads `skb->mark` only. Per-rule match data is immutable and no state is persisted.

## Dependencies And Integration Points
Depends on ebtables mark-match UAPI and xtables registration. It commonly consumes marks written by `ebt_mark.c` or other netfilter/classifier paths.

## Risks And Test Signals
Risks include confusing OR/AND semantics, invert handling, and compat width conversion for marks/masks. Tests should cover exact, OR, invert, invalid bitmasks, empty mode, simultaneous modes, and 32-bit compat.
