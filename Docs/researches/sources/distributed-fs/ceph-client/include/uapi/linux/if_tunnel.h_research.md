
# sources/distributed-fs/ceph-client/include/uapi/linux/if_tunnel.h

## Purpose

`if_tunnel.h` defines ioctl, flag, structure, and netlink attribute UAPI for IP tunnels, GRE, SIT/6rd, VTI, tunnel encapsulation, and modern tunnel option bits. The complete 221-line file was read.

## Important APIs, Types, and Functions

Important ioctls include `SIOCGETTUNNEL`, `SIOCADDTUNNEL`, `SIOCDELTUNNEL`, `SIOCCHGTUNNEL`, PRL and 6rd variants. It defines GRE flags and helpers, `ip_tunnel_parm`, `ip_tunnel_prl`, `ip_tunnel_6rd`, tunnel encapsulation types/flags, `IFLA_IPTUN_*`, `IFLA_GRE_*`, `IFLA_VTI_*`, legacy `TUNNEL_*` flags for user space, and `IP_TUNNEL_*_BIT` values for expanded flag space.

## Control Flow

There is no local executable flow. User space configures tunnels through legacy private ioctls or rtnetlink attributes. Kernel tunnel drivers parse endpoints, keys, flags, encapsulation, 6rd/PRL settings, and route packets through the configured tunnel device.

## State and Persistence Behavior

Tunnel state is stored on netdevices and includes names, underlying link, input/output flags, keys, outer IP header template, 6rd parameters, PRL entries, encapsulation ports, fwmark, and GRE/ERSPAN options.

## Dependencies and Integration Points

The header includes `linux/types.h`, `linux/if.h`, `linux/ip.h`, `linux/in6.h`, and byteorder definitions. It integrates with IPIP/SIT/GRE/VTI tunnel drivers, rtnetlink, and legacy private ioctls.

## Risks and Edge Cases

The file explicitly warns that old `__be16` tunnel flags have no free bits; new code should use `*_BIT` definitions. Endian conversions, option-present masks, SIT/VTI bit aliasing, and ioctl/netlink parity are common compatibility traps.

## Test Signals

Tests should cover legacy ioctl and rtnetlink creation/change/delete, GRE key/seq/csum flags, 6rd and PRL operations, FOU/GUE/MPLS encapsulation, VTI flag behavior, and endian compatibility for old and new flag forms.
