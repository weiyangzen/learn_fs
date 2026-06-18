# sources/distributed-fs/ceph-client/include/uapi/linux/mpls_iptunnel.h

## Purpose
Defines rtnetlink encapsulation attributes for MPLS IP tunnels.

## Important APIs, Types, And Functions
Exports `MPLS_IPTUNNEL_UNSPEC`, `MPLS_IPTUNNEL_DST`, `MPLS_IPTUNNEL_TTL`, and `MPLS_IPTUNNEL_MAX`.

## Control Flow
Userspace configures routes with `RTA_ENCAP` containing nested MPLS IP tunnel attributes: destination label stack and optional TTL. The kernel route code parses those attributes to build the encapsulation action.

## State, Persistence, And Dependencies
State persists in route entries. The header has no include dependencies.

## Integration Points
Used by iproute2 and rtnetlink consumers configuring MPLS encap routes.

## Risks
The header only defines numeric attributes; payload validation is external. Wrong nesting under `RTA_ENCAP` or missing destination attributes makes routes invalid.

## Test Signals
Validate netlink policy for `MPLS_IPTUNNEL_DST` and TTL, route add/dump round trips, and rejection of malformed nested attributes.
