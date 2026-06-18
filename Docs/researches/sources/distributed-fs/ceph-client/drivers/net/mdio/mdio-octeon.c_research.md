<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-octeon.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-octeon.c

Purpose: platform frontend for Cavium OCTEON MDIO buses using the common Cavium callbacks.

Important APIs/types/functions: probe/remove allocate and manage `struct cavium_mdiobus`; callbacks are imported from `mdio-cavium.c`. Hardware enable is controlled through `union cvmx_smix_en` and `SMI_EN`.

Control flow: probe allocates a devm mii_bus with Cavium private state, maps SMI registers, enables the SMI block, sets bus name/id/parent and C22/C45 callbacks, stores platform data, and registers with OF MDIO. On registration failure or remove it disables SMI and unregisters the bus.

State and persistence: runtime state is the enabled SMI hardware bit, register base, cached mode in common code, and registered bus. No persistent storage exists.

Dependencies/integration: depends on OF MDIO, HAS_IOMEM, `MDIO_CAVIUM`, OCTEON-compatible DT node `cavium,octeon-3860-mdio`, and phylib.

Risks and test signals: risks include enabling hardware before registration failure, pointer-form bus IDs, C22/C45 common-code behavior, and 64-bit accessor correctness. Tests should cover probe failure cleanup, remove disable, C22/C45 transactions, and OF PHY child discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-octeon.c -->
