# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ct.h

## Purpose
Defines the TC conntrack action ABI for committing, clearing, forcing, and NATing connection-tracked packet state.

## Important APIs, Types, and Constants
`struct tc_ct` embeds `tc_gen`. Attributes include action flags, zone, mark/mask, labels/mask, NAT IPv4/IPv6 address ranges, NAT port ranges, helper name/family/proto, and padding. Action bits include `TCA_CT_ACT_COMMIT`, `TCA_CT_ACT_FORCE`, `TCA_CT_ACT_CLEAR`, `TCA_CT_ACT_NAT`, `TCA_CT_ACT_NAT_SRC`, and `TCA_CT_ACT_NAT_DST`.

## Control Flow, State, and Persistence
Userspace configures attributes through rtnetlink. Runtime action lookup or creates conntrack entries, applies metadata and NAT, or clears state. Conntrack table entries persist according to netfilter lifetimes.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with netfilter conntrack, NAT, helpers, OVS/TC offload paths, and `tc`.

## Risks and Test Signals
Risks include invalid NAT ranges, helper misuse, label width mismatch, offload incompatibility, and conntrack state leaks. Test commit/clear/NAT paths, zone isolation, mark/label masks, helper attributes, action dumps, and hardware-offload rejection paths.
