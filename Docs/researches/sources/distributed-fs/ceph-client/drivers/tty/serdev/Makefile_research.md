# sources/distributed-fs/ceph-client/drivers/tty/serdev/Makefile

## Purpose
Builds the serdev core object and the optional tty-port controller object based on Kconfig selections.

## Important APIs, types, and functions
- `serdev-objs := core.o` defines the composite serdev core module/built-in object.
- `obj-$(CONFIG_SERIAL_DEV_BUS) += serdev.o` includes core serdev support.
- `obj-$(CONFIG_SERIAL_DEV_CTRL_TTYPORT) += serdev-ttyport.o` includes the tty-port bridge.

## Control flow
Kbuild compiles `core.o` into `serdev.o` when the bus is selected, and separately compiles `serdev-ttyport.o` when the tty-port controller is enabled.

## State and persistence behavior
No runtime state. This is build metadata only.

## Dependencies and integration points
Directly mirrors `Kconfig` and drives inclusion of `core.c` and `serdev-ttyport.c` in the tty driver subtree.

## Risks and edge cases
The Makefile is simple; the main risk is config skew where serdev bus code is enabled without the bridge expected by serial drivers or board descriptions.

## Test signals
Kernel build matrix should verify `CONFIG_SERIAL_DEV_BUS=y/m` creates `serdev.o`, and `CONFIG_SERIAL_DEV_CTRL_TTYPORT=y` creates `serdev-ttyport.o`.
