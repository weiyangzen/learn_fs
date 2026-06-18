# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_mpls.h

## Purpose
Defines the TC MPLS action ABI for popping, pushing, modifying, decrementing TTL, or MAC-pushing MPLS headers.

## Important APIs, Types, and Constants
Actions include `TCA_MPLS_ACT_POP`, `TCA_MPLS_ACT_PUSH`, `TCA_MPLS_ACT_MODIFY`, `TCA_MPLS_ACT_DEC_TTL`, and `TCA_MPLS_ACT_MAC_PUSH`. `struct tc_mpls` embeds `tc_gen` and `m_action`. Attributes include protocol, label, traffic class, TTL, BOS, timing, parameters, and padding.

## Control Flow, State, and Persistence
Userspace configures MPLS operation and fields. Runtime packet handling mutates MPLS headers and updates action counters.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with TC, MPLS forwarding, and tunnel/encapsulation pipelines.

## Risks and Test Signals
Risks include invalid TTL zero, label width overflow, BOS misuse, and protocol mismatch after pop/push. Test each action, boundary label/TC/BOS values, checksum interactions, and packet capture validation.
