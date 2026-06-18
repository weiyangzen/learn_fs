# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/phy.h

Purpose: declares private mv88e6xxx PHY access helpers and defines the Marvell PHY page register constants used by internal PHY access code.

Important APIs/types/functions: constants are `MV88E6XXX_PHY_PAGE` and `MV88E6XXX_PHY_PAGE_COPPER`. Prototypes cover direct 6165 access, 6185 PPU-mediated access, generic C22 and C45 read/write, paged read/write, and PHY lifecycle/setup helpers.

Control flow: no executable flow. The header lets chip ops tables select direct, PPU-mediated, or Global2 SMI PHY access implementations while keeping callers on generic wrappers.

State and persistence: no state is stored here. Declared functions manipulate PHY hardware registers and runtime PPU coordination state in `struct mv88e6xxx_chip`.

Dependencies/integration: consumed by `phy.c`, `pcs-639x.c`, chip ops tables, and MDIO setup. It relies on visible declarations for `struct mv88e6xxx_chip` and `struct mii_bus`.

Risks: page register constant must not be used as a normal paged target register; implementation rejects that. Header guard comment has a minor formatting typo but no functional effect.

Test signals: compile/link coverage for all selected chip ops, MDIO bus callbacks using C22/C45 prototypes, and page helpers returning `-EINVAL` for register 22.
