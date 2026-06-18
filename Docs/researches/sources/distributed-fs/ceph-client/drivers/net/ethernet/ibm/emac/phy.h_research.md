
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/phy.h

## Purpose
`phy.h` declares the legacy PHY abstraction used by the IBM EMAC driver when not fully delegated to phylib. It defines PHY operation callbacks, static PHY definitions, live PHY state, and public probe/reset APIs.

## Important APIs, Types, and Functions
`struct mii_phy_ops` contains optional `init`/`suspend` callbacks and required-style link methods for autonegotiation, forced setup, polling, and link reading. `struct mii_phy_def` describes a PHY ID/mask, feature set, name, and ops. `struct mii_phy` stores selected definition, advertising/features, MDIO address, interface mode, GPCS address, autoneg/speed/duplex/pause state, owning netdev, and MDIO callbacks. Public declarations are `emac_mii_phy_probe()`, `emac_mii_reset_phy()`, and `emac_mii_reset_gpcs()`.

## Control Flow
`core.c` allocates/fills a `struct mii_phy`, calls probe/reset helpers, then invokes `def->ops` during initial setup, ethtool changes, and link polling.

## State and Persistence
`struct mii_phy` is volatile per-EMAC state, mirroring current PHY configuration and negotiated status. Hardware persistence is limited to PHY register programming performed by operations in `phy.c`.

## Dependencies and Integration Points
The struct uses `struct net_device` and ethtool legacy `SUPPORTED_*`/`ADVERTISED_*` bit conventions. It integrates with EMAC’s MDIO functions via callback pointers rather than owning an MDIO bus itself.

## Risks
The abstraction predates modern phylib conventions and mixes policy, cache, and hardware state. The unused `magic_aneg` and `suspend` fields indicate incomplete or legacy surface. Consumers must ensure MDIO callbacks are valid before invoking operations.

## Test Signals
Compile coverage with legacy PHY discovery, ethtool link-setting operations, and MDIO ioctl paths validates this header. Runtime checks should ensure cached `mii_phy` state tracks actual PHY status after link changes.
