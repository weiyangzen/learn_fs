# sources/distributed-fs/ceph-client/net/bluetooth/bnep/Makefile

## Purpose
This Makefile builds the BNEP protocol module from its core, socket, and netdevice components.

## Important APIs, Types, And Functions
`obj-$(CONFIG_BT_BNEP) += bnep.o` creates the module or built-in object. `bnep-objs := core.o sock.o netdev.o` groups the implementation.

## Control Flow
There is no runtime control flow. Build inclusion is controlled entirely by `CONFIG_BT_BNEP`.

## State, Persistence, And Dependencies
The file has build-system state only. It depends on symbols declared by `bnep/Kconfig`.

## Integration Points
The parent Bluetooth Makefile descends into `bnep/`, and the resulting object registers the BNEP socket protocol and PAN netdev support.

## Risks
If any of the three component objects are omitted, exported BNEP control or netdev functions will be unresolved or the module will lack its expected data path.

## Test Signals
Kernel build output should include `core.o`, `sock.o`, and `netdev.o` in `bnep.o` whenever `CONFIG_BT_BNEP` is enabled.
