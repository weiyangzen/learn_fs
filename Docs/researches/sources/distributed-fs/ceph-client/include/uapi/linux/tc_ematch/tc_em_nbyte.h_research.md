# sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_nbyte.h

## Purpose
Defines the TC nbyte ematch ABI for matching a byte sequence at a packet offset.

## Important APIs, Types, and Constants
`struct tcf_em_nbyte` carries offset, 12-bit length, and 4-bit layer. The pattern data is supplied by surrounding ematch netlink payload conventions.

## Control Flow, State, and Persistence
Runtime classifier computes layer-relative offset and compares the configured byte pattern of the configured length.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC ematch/classifier framework.

## Risks and Test Signals
Risks include length bitfield truncation, out-of-bounds offsets, and layer parsing failures on short packets. Test zero/maximum length, each supported layer, malformed packets, and dump round trips.
