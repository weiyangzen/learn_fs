# sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/Kconfig

## Purpose
This Kconfig file exposes the 3Com Ethernet vendor menu and driver selections for Vortex/Boomerang-family and Typhoon-family devices.

## Important APIs, Types, and Functions
- `NET_VENDOR_3COM` gates the 3Com menu and defaults to `y` when ISA, EISA, PCI, or PCMCIA is available.
- `VORTEX` is a tristate for 3c590/3c900-series support, depends on `(PCI || EISA) && HAS_IOPORT_MAP`, and selects `MII`.
- `TYPHOON` is a tristate for 3CR990-series support, depends on PCI, and selects `CRC32`.

## Control Flow
Kconfig first evaluates the vendor menu. If enabled, users can select individual drivers as built-in or modules. The selected symbols flow into the directory Makefile.

## State and Persistence
Persistent state is the kernel configuration symbols `CONFIG_NET_VENDOR_3COM`, `CONFIG_VORTEX`, and `CONFIG_TYPHOON`.

## Dependencies and Integration Points
The file integrates with `drivers/net/ethernet/3com/Makefile`, where `CONFIG_VORTEX` builds `3c59x.o` and `CONFIG_TYPHOON` builds `typhoon.o`.

## Risks and Edge Cases
Disabling the vendor menu hides the child drivers. `VORTEX` depends on I/O-port mapping support, which is important for legacy hardware paths. Help text relies on users mapping old product names correctly.

## Test Signals
Verify menu visibility, dependency enforcement, selected `MII`/`CRC32`, and object inclusion for built-in and module configurations.
