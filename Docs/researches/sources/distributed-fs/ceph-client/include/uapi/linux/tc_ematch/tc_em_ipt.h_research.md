# sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_ipt.h

## Purpose
Defines the TC ematch ABI for using iptables/netfilter match modules inside traffic-control classifiers.

## Important APIs, Types, and Constants
Attributes include hook, match name, match revision, netfilter protocol, and match data under `TCA_EM_IPT_*`.

## Control Flow, State, and Persistence
Userspace passes module identity and opaque match data. Runtime classifier invokes the corresponding netfilter match logic for packets.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates TC ematch with netfilter/xtables match modules.

## Risks and Test Signals
Risks include opaque match-data ABI mismatches, module revision mismatch, and netfilter hook/protocol confusion. Test known xt matches, wrong revision rejection, dump round trips, and protocol-specific packets.
