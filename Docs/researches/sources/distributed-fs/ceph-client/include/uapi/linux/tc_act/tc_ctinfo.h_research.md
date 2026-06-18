# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ctinfo.h

## Purpose
Defines the TC ctinfo action ABI for copying conntrack metadata into packet DSCP or skb mark fields and reporting action statistics.

## Important APIs, Types, and Constants
`struct tc_ctinfo` embeds `tc_gen`. Attributes include action, zone, DSCP mask, DSCP state mask, cpmark mask, and statistics for DSCP set/error and cpmark set.

## Control Flow, State, and Persistence
Userspace configures masks and action mode. Kernel reads conntrack state during packet processing and conditionally updates packet DSCP or mark. Action counters persist with the action instance.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with conntrack, QoS classification, and `tc` filter/action chains.

## Risks and Test Signals
Risks include mask mistakes that corrupt DSCP bits, missing conntrack entries, and stats drift. Test DSCP/cpmark behavior with known conntrack marks, zone handling, and netlink dump of stats.
