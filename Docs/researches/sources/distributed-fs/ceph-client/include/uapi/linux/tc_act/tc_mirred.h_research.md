# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_mirred.h

## Purpose
Defines the TC mirror/redirect action ABI for cloning or redirecting packets to ingress or egress of another interface or block.

## Important APIs, Types, and Constants
Action constants are `TCA_EGRESS_REDIR`, `TCA_EGRESS_MIRROR`, `TCA_INGRESS_REDIR`, and `TCA_INGRESS_MIRROR`. `struct tc_mirred` embeds `tc_gen`, `eaction`, and target `ifindex`. Attributes include timing, parameters, padding, and `TCA_MIRRED_BLOCKID`.

## Control Flow, State, and Persistence
Runtime action either redirects the packet or mirrors a clone. Target ifindex/block and generic counters are stored in action state.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC ingress/egress hooks, netdevice ifindex lookup, and shared TC blocks.

## Risks and Test Signals
Risks include redirect loops, invalid ifindex, block target ambiguity, and clone allocation failures. Test mirror vs redirect semantics, ingress/egress direction, loop prevention, interface removal, and action stats.
