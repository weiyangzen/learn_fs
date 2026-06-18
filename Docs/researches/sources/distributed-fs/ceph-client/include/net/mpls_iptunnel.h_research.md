<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mpls_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/net/mpls_iptunnel.h

## Purpose
`mpls_iptunnel.h` defines the lightweight-tunnel encapsulation payload used for MPLS IP tunnels.

## Important APIs, types, and functions
It defines `struct mpls_iptunnel_encap` with label count, TTL propagation/default TTL, and a flexible label array, plus `mpls_lwtunnel_encap` to cast `lwtunnel_state->data`.

## Control flow
MPLS tunnel code stores labels and TTL policy in lwtunnel state. Callers retrieve the typed encap data and push labels during output.

## State and persistence
State is embedded in `struct lwtunnel_state` and persists as long as the route/lwtunnel object exists. The header itself stores no global data.

## Dependencies and integration points
It depends on Linux types and lwtunnel infrastructure. It integrates MPLS route encapsulation with generic lightweight tunnels.

## Risks and test signals
Risks include flexible-array sizing, label count mismatch with allocated lwtunnel state, TTL propagation semantics, and unchecked casts. Tests should cover route creation with multiple labels, default TTL, propagation on/off, and malformed netlink attributes.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mpls_iptunnel.h` completely for this pass (25 lines, 481 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mpls_iptunnel.h -->
