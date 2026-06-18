# sources/distributed-fs/ceph-client/include/uapi/linux/netdevice.h

## Purpose
Defines basic network device UAPI constants for hardware address length, default device group, name assignment type, media port selection, and hardware address assignment type.

## Important APIs, Types, And Functions
Exports `MAX_ADDR_LEN`, `INIT_NETDEV_GROUP`, `NET_NAME_*`, media port enum values `IF_PORT_*`, and `NET_ADDR_*`.

## Control Flow
Drivers and netlink/ioctl paths report naming origin, port type, and address origin to userspace. No executable logic is defined in the header.

## State, Persistence, And Dependencies
State persists as netdevice metadata. Depends on `linux/if.h`, `linux/if_ether.h`, `linux/if_packet.h`, and `linux/if_link.h`.

## Integration Points
Used by sysfs `name_assign_type`, iproute2, udev naming logic, network drivers, and hardware address reporting.

## Risks
Values are long-standing ABI and must not be renumbered. `MAX_ADDR_LEN` bounds hardware address arrays across many link types.

## Test Signals
Validate sysfs/netlink exposure of name assignment, MAC address assignment type, media port values, and max address length assumptions.
