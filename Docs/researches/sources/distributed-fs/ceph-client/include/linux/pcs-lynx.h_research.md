<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs-lynx.h -->
# sources/distributed-fs/ceph-client/include/linux/pcs-lynx.h

## Purpose
`include/linux/pcs-lynx.h` declares factory and teardown helpers for NXP Lynx PCS integration with the kernel phylink subsystem. It lets Ethernet MAC/controller drivers create a `struct phylink_pcs` either from an MDIO bus/address pair or from firmware node data, then destroy it when no longer needed.

## Important APIs, Types, and Functions
`lynx_pcs_create_mdiodev(struct mii_bus *bus, int addr)` creates a Lynx PCS backed by an MDIO device at a specific address. `lynx_pcs_create_fwnode(struct fwnode_handle *node)` creates one from firmware node description. `lynx_pcs_destroy(struct phylink_pcs *pcs)` releases the object returned by the create helpers.

The header exposes `struct phylink_pcs` from phylink as the consumer-facing object and depends on `struct mii_bus` plus `struct fwnode_handle` through included headers.

## Control Flow
A MAC driver obtains MDIO or firmware information during probe, calls one of the create helpers, passes the returned PCS to phylink setup, and calls `lynx_pcs_destroy()` during remove or probe-error unwinding. The PCS implementation behind these prototypes handles link-mode configuration and PCS operations through phylink callbacks.

## State and Persistence Behavior
The header itself stores no state. The created PCS object persists across the network device lifetime or until explicit destroy. Lifetime is caller-managed; a driver must not destroy the PCS while phylink can still call its PCS operations.

## Dependencies and Integration Points
The header includes `linux/mdio.h` and `linux/phylink.h`. It integrates with NXP/Freescale Ethernet controllers and any driver that uses a Lynx PCS with phylink, MDIO, and firmware description.

## Risks
The main risks are lifetime mismatch, passing an invalid MDIO address or firmware node, failing to unwind after partial probe, and creating duplicate PCS objects for the same hardware block. Since only prototypes are visible here, users must follow the implementation's error-pointer or NULL return convention as documented by the implementation.

## Test Signals
Probe/remove tests on Lynx PCS users, MDIO enumeration with valid and invalid addresses, firmware-node lookup, phylink mode changes, autonegotiation and fixed-link operation, suspend/resume if supported by users, and leak/error-path tests around create/destroy are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs-lynx.h -->
