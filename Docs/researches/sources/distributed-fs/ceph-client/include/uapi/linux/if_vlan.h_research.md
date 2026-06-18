
# sources/distributed-fs/ceph-client/include/uapi/linux/if_vlan.h

## Purpose

`if_vlan.h` defines the legacy 802.1Q VLAN ioctl argument ABI, VLAN operation commands, device flags, naming modes, and command payload union. The complete 66-line file was read.

## Important APIs, Types, and Functions

Enums define `vlan_ioctl_cmds`, `vlan_flags`, and `vlan_name_types`. `struct vlan_ioctl_args` carries a command, primary device name, union payload (`device2`, VID, skb priority, name type, bind type, flag), and `vlan_qos`.

## Control Flow

User space passes `vlan_ioctl_args` to VLAN ioctls defined in `sockios.h`. Kernel VLAN code branches on `cmd` to add/delete VLAN devices, set or get ingress/egress QoS mappings, set naming type/flags, and report real device or VID.

## State and Persistence Behavior

VLAN devices, flags, naming behavior, QoS mappings, and bindings persist as kernel netdevice/VLAN state until changed or the device is removed.

## Dependencies and Integration Points

The header intentionally relies on VLAN ioctl numbers from `sockios.h`. It integrates with legacy VLAN configuration tools and the VLAN netdevice subsystem; modern rtnetlink VLAN attributes in `if_link.h` are a parallel interface.

## Risks and Edge Cases

Device name arrays are fixed at 24 bytes, smaller than some modern interface-name expectations. Union interpretation depends entirely on `cmd`; callers must validate VID and QoS ranges and handle legacy naming modes.

## Test Signals

VLAN ioctl tests should cover add/delete, get realdev/VID, ingress/egress QoS mapping, flag changes, naming modes, invalid VID values, and compatibility with rtnetlink-created VLAN devices.
