# sources/distributed-fs/ceph-client/include/uapi/linux/sockios.h

## Purpose
Defines Linux socket ioctl command numbers shared by userspace network tools and kernel socket/netdevice handlers. It is a stable UAPI registry for routing, interface, ARP/RARP, ethtool, MII, bonding, bridge, VLAN, timestamp, hardware timestamp, device-private, and protocol-private ioctl ranges.

## Important APIs, Types, and Constants
There are no functions or structs in this header. Important exported constants include `SIOCINQ`, `SIOCOUTQ`, `SIOCGSTAMP`, `SIOCGSTAMPNS`, `SIOCADDRT`, `SIOCDELRT`, `SIOCGIF*`, `SIOCSIF*`, `SIOCETHTOOL`, `SIOCGMIIPHY`, `SIOCGMIIREG`, `SIOCSMIIREG`, `SIOCSHWTSTAMP`, `SIOCGHWTSTAMP`, `SIOCDEVPRIVATE`, and `SIOCPROTOPRIVATE`. Timestamp ioctl selection depends on word size and libc `timeval`/`timespec` layout.

## Control Flow, State, and Persistence
The header has compile-time selection only. Runtime state is in socket and netdevice subsystems, not in this file. Ioctl numbers are persistent ABI; reusing obsolete holes or renumbering existing commands would break old tools.

## Dependencies and Integration Points
Depends on `<asm/bitsperlong.h>` and `<asm/sockios.h>`. Integrates with `ioctl(fd, request, arg)`, netdevice `ndo_do_ioctl`, bridge/bonding/VLAN handlers, hardware timestamp configuration in `linux/net_tstamp.h`, and TIPC's protocol-private additions.

## Risks and Test Signals
Risks are ABI collisions, wrong timestamp command on 32-bit/time64 builds, and userspace issuing private ioctls to the wrong device. Test by compiling representative 32-bit and 64-bit userspace, checking numeric ioctl stability, and exercising interface query/set operations through tools such as `ip`, `ethtool`, and timestamp socket tests.
