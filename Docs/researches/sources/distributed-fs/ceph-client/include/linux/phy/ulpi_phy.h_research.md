# sources/distributed-fs/ceph-client/include/linux/phy/ulpi_phy.h

## Purpose
Helper for registering a generic PHY for a ULPI device and binding it to the parent USB controller through a lookup.

## Important APIs, Types, and Functions
Defines `ulpi_phy_create()` and `ulpi_phy_destroy()`. Creation calls `phy_create()` on `ulpi->dev`, creates a lookup named `"usb2-phy"` for the parent device, and destroys the PHY on lookup failure. Destruction removes the lookup and destroys the PHY.

## Control Flow
The helper wraps a two-step create/bind sequence with error unwinding. Consumers call destroy for symmetric cleanup.

## State and Persistence
Persistent state is the created `struct phy` and lookup entry linking the ULPI PHY to its controller. The header owns no global state.

## Dependencies and Integration Points
Depends on generic PHY APIs, ULPI device structures, device names, and USB controller parent-child topology.

## Risks
The lookup assumes the controller is always `ulpi->dev.parent` and the connection id is `"usb2-phy"`. If topology or naming differs, consumers may fail to find the PHY.

## Test Signals
ULPI PHY probe/remove tests, lookup resolution from parent USB controller, and error-path tests for lookup creation failure.
