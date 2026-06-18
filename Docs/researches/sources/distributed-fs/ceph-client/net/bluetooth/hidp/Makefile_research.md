# sources/distributed-fs/ceph-client/net/bluetooth/hidp/Makefile

## Purpose
Builds the Bluetooth HIDP module or built-in object from the HIDP core and socket implementation.

## APIs, Types, and Functions
`obj-$(CONFIG_BT_HIDP) += hidp.o` selects the composite object when the Kconfig symbol is enabled. `hidp-objs := core.o sock.o` links session/device logic from `core.o` with PF_BLUETOOTH socket/ioctl registration from `sock.o`.

## Control Flow, State, and Persistence
There is no runtime behavior in the Makefile. Build-time control flow follows the value of `CONFIG_BT_HIDP`; the resulting `hidp.o` contains both module lifecycle code and the socket family operations.

## Dependencies and Integration
Depends on the surrounding kernel kbuild system and the `BT_HIDP` Kconfig symbol. It integrates the two implementation files into one loadable module named `hidp` when built as `m`.

## Risks and Test Signals
Risks include missing either object from `hidp-objs`, which would break module init or ioctl/session symbols at link time. Test signals are successful built-in and module builds, `modinfo hidp` metadata from `core.c`, and link errors if either object dependency is accidentally removed.
