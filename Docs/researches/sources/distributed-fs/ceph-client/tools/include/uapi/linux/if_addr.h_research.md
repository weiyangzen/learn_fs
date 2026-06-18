# sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_addr.h

Purpose: defines rtnetlink address message structures and attributes for adding, deleting, and dumping interface addresses.

Important APIs/types: `struct ifaddrmsg` carries family, prefix length, flags, scope, and interface index. Attributes include `IFA_ADDRESS`, `IFA_LOCAL`, label, broadcast/anycast/multicast, `IFA_CACHEINFO`, extended `IFA_FLAGS`, route priority, target netns ID, and address protocol. Address flags include secondary/temporary, DAD state, optimistic, deprecated, tentative, permanent, no-prefix-route, multicast auto-join, and stable privacy. `struct ifa_cacheinfo` carries preferred/valid lifetimes and timestamps. Compatibility macros `IFA_RTA` and `IFA_PAYLOAD` locate attributes.

Control flow, state, and persistence: userspace sends `RTM_NEWADDR`, `RTM_DELADDR`, or dump requests with `ifaddrmsg` plus attributes. Kernel updates per-interface address state and returns notifications. Persistent state is network namespace address configuration until removed or namespace/device teardown.

Dependencies and integration points: depends on `types.h` and `netlink.h`; integrates iproute2, NetworkManager/systemd-networkd, IPv4/IPv6 address management, DAD, router advertisements, and netns operations.

Risks and test signals: risks include confusing point-to-point `IFA_ADDRESS` with `IFA_LOCAL`, relying on the 8-bit `ifa_flags` when `IFA_FLAGS` is present, and lifetime/protocol mismatches. Tests should add/dump/delete IPv4 and IPv6 addresses, point-to-point addresses, temporary/deprecated addresses, and route-priority/protocol attributes.
