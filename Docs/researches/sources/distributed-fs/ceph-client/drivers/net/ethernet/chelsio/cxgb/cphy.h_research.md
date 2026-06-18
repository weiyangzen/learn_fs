# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cphy.h

## Purpose
`cphy.h` defines the PHY abstraction used by the Chelsio T1 driver. It wraps MDIO access, PHY operation callbacks, PHY instance state, convenience read/write helpers, and factory operations for supported PHY chips.

## Important APIs, Types, and Constants
`struct mdio_ops` supplies board-level MDIO init/read/write functions and mode support. PHY event/state constants cover link change, error, FIFO error, link up, autoneg ready, and autoneg enabled. `struct cphy_ops` declares lifecycle, interrupt, autoneg, advertise, loopback, speed/duplex, and link-status callbacks plus supported MMDs. `struct cphy` stores link state-machine data, adapter pointer, delayed work, BMSR/count fields, ELMER GPIO state, ops, `mdio_if_info`, and chip-specific instance data. `struct gphy` is a factory/reset interface, with extern factories for MY3126, Marvell, VSC8244, and MV88X201X.

## Control Flow and Integration
Driver code creates PHY instances through a `gphy` factory from `board_info`, initializes them with `cphy_init`, then invokes `cphy_ops` from link management and interrupt paths. `cphy_mdio_read`, `cphy_mdio_write`, `simple_mdio_read`, and `simple_mdio_write` adapt Linux MDIO callbacks to the T1 PHY abstraction. `cphy_init` binds the PHY to the netdev's adapter and populates MDIO addressing/capability fields when board MDIO ops exist.

## State and Persistence
PHY state is in-memory and per adapter port. Hardware link/autoneg state persists in the PHY registers until reset or reconfiguration, accessed through MDIO. The delayed work member supports asynchronous PHY updates, but this header only defines the container.

## Dependencies and Risks
The header depends on `common.h`, Linux MDIO definitions, netdev private data layout, and each PHY implementation honoring the callback contracts. Risks include null MDIO ops when a caller assumes them, stale `mmds`/mode support causing MDIO core misbehavior, factory/reset mismatches for multi-port PHY chips, and delayed-work lifetime issues if implementations do not cancel before freeing.

## Test Signals
Build with all supported PHY implementations, probe boards using each `gphy`, verify MDIO read/write error propagation, link status and autoneg transitions, PHY interrupt enable/clear/handler paths, loopback and speed/duplex changes, and remove/unload with pending PHY delayed work.
