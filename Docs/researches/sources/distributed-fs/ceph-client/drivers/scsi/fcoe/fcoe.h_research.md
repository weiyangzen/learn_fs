# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe.h

## Purpose

`fcoe.h` is the private software-FCoE header. It defines driver constants, debug logging macros, the per-netdevice `struct fcoe_interface`, conversion helpers between an embedded `struct fcoe_ctlr` and interface object, and `fcoe_netdev()` for resolving a libfc lport back to its netdevice.

## Important APIs, types, and functions

Constants define queue depths, version/name/vendor strings, target/LUN/command limits, and the software exchange ID range. `FCOE_DBG()` and `FCOE_NETDEV_DBG()` are gated by `fcoe_debug_logging`. `struct fcoe_interface` stores list linkage, logical/real netdevices, packet handlers for FCoE/FIP/FIP VLAN discovery, shared offload exchange manager, removal flag, and traffic priority. `fcoe_to_ctlr()` and `fcoe_from_ctlr()` assume the allocation layout used in `fcoe.c`.

## Control flow

The header has no standalone flow. Its helpers are used by allocation, data path, and teardown code. `fcoe_netdev()` walks from lport private data to the interface and returns the associated logical netdevice.

## State and persistence behavior

The only declared global is `fcoe_debug_logging`. `struct fcoe_interface` is the persistent runtime object for an FCoE instance while the associated controller/lport exists.

## Dependencies and integration points

The header includes skb/thread headers and relies on libfc/libfcoe types visible to includers. It is local to the software FCoE driver, not UAPI.

## Risks and edge cases

The pointer conversion macros are layout-sensitive and unchecked. Any allocation-order change breaks all conversions. `fcoe_netdev()` assumes valid `struct fcoe_port` private data and a non-NULL `priv` interface pointer.

## Test signals

Compile coverage catches type drift; create/destroy and data-path runtime tests validate the allocation layout indirectly.
