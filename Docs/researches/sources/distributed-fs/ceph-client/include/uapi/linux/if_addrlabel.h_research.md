<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_addrlabel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_addrlabel.h

## Purpose
`if_addrlabel.h` defines rtnetlink attributes for IPv6 address label policy management used by source/destination address selection.

## Important APIs, types, and functions
`struct ifaddrlblmsg` carries address family, reserved byte, prefix length, flags, interface index, and sequence number. The attribute enum defines `IFAL_ADDRESS` and `IFAL_LABEL`, bounded by `IFAL_MAX`. Message command transport is handled by rtnetlink address-label operations.

## Control flow
User space sends address-label add/delete/list requests with prefix address and numeric label. The kernel updates or dumps the per-network-namespace address label table used by IPv6 address selection.

## State and persistence behavior
Address label rules are live namespace configuration. They persist until deleted or namespace teardown; policy managers may reload them from configuration.

## Dependencies and integration points
It integrates with IPv6 RFC 6724 source address selection, rtnetlink, and tools such as `ip addrlabel`.

## Risks and test signals
Risks include overlapping prefix ambiguity, wrong label values changing source selection, missing namespace isolation, and netlink attribute-policy drift. Test signals include `ip addrlabel` add/delete/list, source-address selection tests, namespace isolation tests, duplicate prefix handling, and invalid attribute rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_addrlabel.h -->
