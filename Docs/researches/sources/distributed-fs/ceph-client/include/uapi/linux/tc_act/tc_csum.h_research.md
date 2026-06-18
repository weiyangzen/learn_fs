# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_csum.h

## Purpose
Defines the TC checksum update action ABI for recalculating protocol checksums after packet edits.

## Important APIs, Types, and Constants
`struct tc_csum` embeds `tc_gen` and `update_flags`. Flags include IPv4 header, ICMP, IGMP, TCP, UDP, UDPLite, and SCTP checksum updates. Attributes are `TCA_CSUM_PARMS`, `TCA_CSUM_TM`, and padding.

## Control Flow, State, and Persistence
Userspace configures which checksums to update. Kernel action execution examines packets and recalculates selected checksum fields. Persistent state is only the action's configured flags and generic counters.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Typically follows pedit, NAT, MPLS, VLAN, or other packet mutation actions in `tc` pipelines.

## Risks and Test Signals
Risks include stale checksums after edits, incompatible protocol flags, and fragmented/nonlinear skb handling. Test per-protocol checksum correction, bad flag combinations, action dump, and packet capture validation.
