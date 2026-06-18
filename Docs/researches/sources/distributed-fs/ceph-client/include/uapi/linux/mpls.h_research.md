# sources/distributed-fs/ceph-client/include/uapi/linux/mpls.h

## Purpose
Defines MPLS label stack entry layout, reserved label constants, netlink statistics attributes, and link statistics struct.

## Important APIs, Types, And Functions
Exports `mpls_label`, masks/shifts for label, TC, bottom-of-stack, and TTL fields, reserved label constants, `MPLS_STATS_*`, and `mpls_link_stats`.

## Control Flow
Networking code encodes/decodes a 32-bit big-endian MPLS label stack entry using masks and shifts. Netlink stats embed `mpls_link_stats` under AF_MPLS attributes.

## State, Persistence, And Dependencies
State lives in packets, routes, and per-link counters. Depends on `linux/types.h` and byteorder definitions.

## Integration Points
Used by MPLS route configuration, packet parsing, rtnetlink stats, and diagnostic tools.

## Risks
Endianness is critical: `entry` is `__be32`. Reserved labels have protocol-specific semantics and should not be treated as ordinary forwarding labels.

## Test Signals
Test label encode/decode, reserved label handling, TTL/TC/S bit extraction, link stats dump layout, and AF_MPLS netlink nesting.
