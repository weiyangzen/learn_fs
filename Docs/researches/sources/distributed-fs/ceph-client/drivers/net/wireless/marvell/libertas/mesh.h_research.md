# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/mesh.h

## Purpose
Declares the full-firmware mesh interface between `main.c`, `rx.c`, `tx.c`, ethtool, and `mesh.c`, and provides no-op stubs when `CONFIG_LIBERTAS_MESH` is disabled.

## Important APIs
When mesh is enabled, it declares lifecycle functions `lbs_init_mesh()`, `lbs_start_mesh()`, `lbs_deinit_mesh()`, `lbs_remove_mesh()`, status helper `lbs_mesh_activated()`, channel setter `lbs_mesh_set_channel()`, RX/TX descriptor helpers, and mesh ethtool callbacks. When disabled, macros preserve buildability while returning default behavior.

## Control Flow And State
No direct runtime state is stored here. Compile-time configuration selects either real functions or stubs, which determines whether `main.c` registers mesh support and whether RX/TX helpers alter device selection or descriptors.

## Dependencies And Integration
Includes `host.h` and `dev.h`, and forward-declares netdev, descriptor, command, and ethtool types. It is included by the core RX/TX/main paths.

## Risks And Test Signals
Risks include stub return types drifting from real functions and callers assuming mesh side effects when disabled. Test signals are successful builds with and without `CONFIG_LIBERTAS_MESH`, normal station RX/TX when disabled, and mesh device creation when enabled.
