# sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_meta.h

## Purpose
Defines the TC metadata ematch ABI for comparing packet, device, route, and socket metadata values.

## Important APIs, Types, and Constants
`struct tcf_meta_val` carries encoded `kind`, shift, and operator. `TCF_META_TYPE_MASK`, `TCF_META_ID_MASK`, `TCF_META_TYPE()`, and `TCF_META_ID()` decode kind. Types include variable and integer. Metadata IDs include constants for values, random, load averages, device, priority, protocol, packet type/length/data length/MAC length, netfilter mark, tcindex, route class/input interface, many socket fields, VLAN tag, and RX hash. `struct tcf_meta_hdr` stores left and right operands.

## Control Flow, State, and Persistence
Userspace describes a left/right metadata comparison. Runtime ematch fetches metadata from skb, netdevice, route, socket, or system source, applies shifts/operators, and returns match result.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC classifier ematch and socket/skb metadata.

## Risks and Test Signals
Risks include unimplemented IDs kept in ABI, changing socket metadata semantics, and type/operator mismatch. Test each supported metadata source, unsupported ID behavior, variable vs integer comparisons, and netlink dump compatibility.
