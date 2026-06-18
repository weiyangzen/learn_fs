<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio-mux.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio-mux.h

## Purpose
This header exposes the MDIO mux framework used to present multiple child MDIO buses behind a selectable parent bus.

## Important APIs, types, and functions
`mdio_mux_init()` initializes a mux for a device node, switch callback, optional parent `mii_bus`, private data, and output handle. `mdio_mux_uninit()` tears the mux down. The switch callback receives current and desired child bus identifiers.

## Control flow
The mux driver calls `mdio_mux_init()`, which creates child buses from firmware data and routes transactions by invoking the switch callback before accessing the selected child. On removal, `mdio_mux_uninit()` unregisters and frees the mux-owned buses.

## State and persistence
Mux state is hidden behind `mux_handle`; the header stores none. Hardware selection state persists in the mux device until changed.

## Dependencies and integration points
It depends on Linux device, OF, phylib, and parent MDIO bus support. It integrates MDIO switches/multiplexers with PHY discovery and DSA-style nested MDIO topologies.

## Risks and test signals
Risks include incorrect child selection, nested bus locking deadlocks, parent-bus discovery failures, and uninit while child PHYs are active. Test each child bus, rapid switching, nested mux paths, failed switch callbacks, and remove after registered PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio-mux.h -->
