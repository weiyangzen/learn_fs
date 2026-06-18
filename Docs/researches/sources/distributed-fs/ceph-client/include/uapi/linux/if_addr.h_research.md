<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_addr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_addr.h

## Purpose
`if_addr.h` defines rtnetlink address message and attribute constants for IPv4/IPv6 interface address configuration and dumps.

## Important APIs, types, and functions
`struct ifaddrmsg` contains address family, prefix length, flags, scope, and interface index. Address flags include `IFA_F_SECONDARY`, `IFA_F_TEMPORARY`, `IFA_F_NODAD`, `IFA_F_OPTIMISTIC`, `IFA_F_DADFAILED`, `IFA_F_HOMEADDRESS`, `IFA_F_DEPRECATED`, `IFA_F_TENTATIVE`, `IFA_F_PERMANENT`, `IFA_F_MANAGETEMPADDR`, `IFA_F_NOPREFIXROUTE`, `IFA_F_MCAUTOJOIN`, and `IFA_F_STABLE_PRIVACY`. Attribute enums include `IFA_ADDRESS`, `IFA_LOCAL`, `IFA_LABEL`, `IFA_BROADCAST`, `IFA_ANYCAST`, `IFA_CACHEINFO`, `IFA_MULTICAST`, `IFA_FLAGS`, `IFA_RT_PRIORITY`, `IFA_TARGET_NETNSID`, and `IFA_PROTO`. `struct ifa_cacheinfo` carries preferred/valid lifetimes, creation time, and update time. Compatibility macros `IFA_RTA()` and `IFA_PAYLOAD()` are exposed outside the kernel, and `IFAPROT_*` values identify kernel-originated address protocols.

## Control flow
Address add/delete/get rtnetlink messages carry `ifaddrmsg` plus attributes. The kernel validates family/prefix/interface and updates address lists; dumps return current addresses and lifetimes.

## State and persistence behavior
Address entries, labels, flags, lifetimes, route priorities, and namespace target references are live network-namespace state. Cacheinfo lifetimes age with time and can drive deprecation/removal.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with rtnetlink, IPv4/IPv6 address management, DAD, privacy addressing, prefix route creation, and iproute2.

## Risks and test signals
Risks include incorrect flag width when `IFA_FLAGS` is absent, lifetime overflow, missing DAD state transitions, label truncation, and namespace-ID confusion. Test signals include `ip addr` add/delete/dump, temporary/deprecated/tentative address tests, lifetime expiry, prefix-route behavior, and strict netlink policy validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_addr.h -->
