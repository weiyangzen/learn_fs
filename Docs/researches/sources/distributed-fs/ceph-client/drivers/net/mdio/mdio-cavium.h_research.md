<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.h -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.h

Purpose: shared register layout, data structures, accessors, and function declarations for Cavium MDIO implementations.

Important APIs/types/functions: defines `enum cavium_mdiobus_mode`, SMI register offsets (`SMI_CMD`, `SMI_WR_DAT`, `SMI_RD_DAT`, `SMI_CLK`, `SMI_EN`), endian-aware bitfield macro `OCT_MDIO_BITFIELD_FIELD`, unions for hardware register layouts, `struct cavium_mdiobus`, `oct_mdio_readq/writeq`, and common callback prototypes.

Control flow: no active control flow, but the type layouts are consumed by common and frontend drivers to program SMI command, clock/mode, enable, read-data, and write-data registers. Accessor selection uses OCTEON CSR functions on OCTEON SoCs and generic `readq/writeq` elsewhere.

State and persistence: `struct cavium_mdiobus` carries runtime state for one hardware bus: the mii_bus pointer, MMIO base, and cached mode. Unions model hardware register state.

Dependencies/integration: integrates `mdio-cavium.c`, `mdio-octeon.c`, and Thunder frontend code. Depends on architecture bitfield endianness and optional `CONFIG_CAVIUM_OCTEON_SOC`.

Risks and test signals: risks include bitfield packing mismatch, 64-bit MMIO ordering, and stale prototypes when common callbacks change. Build coverage across big/little-endian and OCTEON/non-OCTEON configs is critical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.h -->
