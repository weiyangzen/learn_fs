# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_skbedit.h

## Purpose
Defines the TC skbedit action ABI for editing skb metadata such as priority, queue mapping, mark, packet type, and flags.

## Important APIs, Types, and Constants
Feature flags include `SKBEDIT_F_PRIORITY`, `SKBEDIT_F_QUEUE_MAPPING`, `SKBEDIT_F_MARK`, `SKBEDIT_F_PTYPE`, `SKBEDIT_F_MASK`, `SKBEDIT_F_INHERITDSFIELD`, and `SKBEDIT_F_TXQ_SKBHASH`. `struct tc_skbedit` embeds `tc_gen`. Attributes carry priority, queue mapping, mark, packet type, mask, flags, and max queue mapping.

## Control Flow, State, and Persistence
Runtime action changes skb metadata, not packet bytes. Configured fields and counters persist in TC action state.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with qdisc selection, mark-based policy, and TC pipelines.

## Risks and Test Signals
Risks include invalid queue mapping, mask misuse, and confusion between packet bytes and skb metadata. Test queue steering, mark/mask behavior, priority inheritance, packet type changes, and dump/counter output.
