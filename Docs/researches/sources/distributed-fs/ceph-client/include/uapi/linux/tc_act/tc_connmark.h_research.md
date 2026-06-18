# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_connmark.h

## Purpose
Defines the TC connmark action ABI, which restores or uses conntrack marks in packet classification/action pipelines.

## Important APIs, Types, and Constants
`struct tc_connmark` embeds `tc_gen` and a `__u16 zone`. Attributes are `TCA_CONNMARK_PARMS`, `TCA_CONNMARK_TM`, and padding.

## Control Flow, State, and Persistence
Userspace configures the action via rtnetlink. Runtime state is in TC action instances and conntrack zone/mark state; the header itself is declarative.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with netfilter conntrack and `tc` action configuration.

## Risks and Test Signals
Risks include zone mismatch with conntrack rules and missing conntrack state. Test add/dump/delete, zone-specific packets, and mark restoration with conntrack enabled and disabled.
