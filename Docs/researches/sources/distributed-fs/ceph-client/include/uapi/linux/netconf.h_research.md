# sources/distributed-fs/ceph-client/include/uapi/linux/netconf.h

## Purpose
Defines rtnetlink network-configuration message and attributes for per-family/per-interface forwarding and related kernel networking settings.

## Important APIs, Types, And Functions
Exports `netconfmsg`, `NETCONFA_*`, `NETCONFA_MAX`, `NETCONFA_ALL`, `NETCONFA_IFINDEX_ALL`, and `NETCONFA_IFINDEX_DEFAULT`.

## Control Flow
Userspace sends netconf rtnetlink queries or updates with an address family and ifindex/default/all selectors, and receives attributes such as forwarding, rp_filter, multicast forwarding, proxy neighbour, and link-down route behavior.

## State, Persistence, And Dependencies
State persists in per-network-namespace and per-interface sysctl-like network configuration. Depends on `linux/types.h` and `linux/netlink.h`.

## Integration Points
Used by iproute2 and network managers to observe IPv4/IPv6 forwarding-related configuration.

## Risks
Special negative ifindex constants are selectors, not normal interface indices. Attribute availability is family-specific.

## Test Signals
Validate all/default/interface queries, family-specific attrs, forwarding/rp_filter values, multicast forwarding reporting, and selector handling.
