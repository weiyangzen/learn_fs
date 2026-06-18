<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if.h

## Purpose
`if.h` defines core Linux network-interface UAPI constants, names, flags, maps, request structures, and interface setting containers used by sockets, ioctl paths, rtnetlink-adjacent code, and network tools.

## Important APIs, types, and functions
The header defines `IFNAMSIZ`, `IFALIASZ`, `ALTIFNAMSIZ`, interface flag values such as `IFF_UP`, `IFF_BROADCAST`, `IFF_DEBUG`, `IFF_LOOPBACK`, `IFF_POINTOPOINT`, `IFF_NOARP`, `IFF_PROMISC`, `IFF_ALLMULTI`, `IFF_MULTICAST`, `IFF_LOWER_UP`, `IFF_DORMANT`, and `IFF_ECHO`, plus `IFF_VOLATILE`. It defines HDLC interface/protocol selectors (`IF_IFACE_*`, `IF_PROTO_*`), RFC 2863 operational states, link modes, `struct ifmap`, `struct if_settings`, and `struct ifreq`/`ifconf` style ioctl carriers with unions for addresses, flags, MTU, metric, map, data, slave/newname, and settings.

## Control flow
User space passes `ifreq` objects to socket ioctls to query or set interface attributes. The kernel dispatches by ioctl number and interprets the matching union member. Operational state is exposed through netdevice/rtnetlink/sysfs flows.

## State and persistence behavior
Interface flags, MTU, addresses, hardware map, master/slave naming, queue state, and operational state are live netdevice state. Some values persist through configuration managers until device teardown.

## Dependencies and integration points
It depends on libc coordination macros and socket address types through included kernel headers. It is central to net-tools, iproute2 compatibility, drivers, rtnetlink, sysfs, and protocol-specific interface headers.

## Risks and test signals
Risks include union member misuse, interface-name truncation, flag mask drift, ioctl/rtnetlink disagreement, and 32/64-bit pointer compatibility for `ifr_data`. Test signals include SIOCGIF* ioctl tests, name-length boundary tests, flag toggling, MTU and address round trips, compat ioctl checks, and cross-validation with rtnetlink dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if.h -->
