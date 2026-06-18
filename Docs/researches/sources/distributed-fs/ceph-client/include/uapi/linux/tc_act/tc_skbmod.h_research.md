# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_skbmod.h

## Purpose
Defines the TC skbmod action ABI for modifying Ethernet header fields and related packet metadata.

## Important APIs, Types, and Constants
Flags include `SKBMOD_F_DMAC`, `SKBMOD_F_SMAC`, `SKBMOD_F_ETYPE`, `SKBMOD_F_SWAPMAC`, and `SKBMOD_F_ECN`. `struct tc_skbmod` embeds `tc_gen` and `__u64 flags`. Attributes carry destination/source MAC, ethertype, timing, parameters, and padding.

## Control Flow, State, and Persistence
Userspace selects fields to modify. Runtime action edits packet headers and updates generic action stats.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with TC L2 rewrite pipelines and often with checksum or tunnel actions.

## Risks and Test Signals
Risks include malformed MAC/ethertype writes, ECN flag semantics, and offload mismatch. Test each flag, swapmac behavior, packet capture, and hardware-offload acceptance/rejection.
