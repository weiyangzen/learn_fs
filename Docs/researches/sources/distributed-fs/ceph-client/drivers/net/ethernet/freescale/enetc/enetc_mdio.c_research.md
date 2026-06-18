# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_mdio.c

## Purpose
Implements ENETC external/internal MDIO controller accesses for Clause 22 and Clause 45 PHY transactions, plus allocation of a minimal `struct enetc_hw` for standalone MDIO PCI devices and definition of the LS1028A MDIO erratum lock.

## Important APIs, Types, and Functions
Exports `enetc_mdio_write_c22`, `enetc_mdio_write_c45`, `enetc_mdio_read_c22`, `enetc_mdio_read_c45`, `enetc_hw_alloc`, and `enetc_mdio_lock`. Internal helpers are `enetc_mdio_rd`, `enetc_mdio_wr`, `enetc_mdio_is_busy`, and `enetc_mdio_wait_complete`.

## Control Flow
Each transaction programs `ENETC_MDIO_CFG` for external MDIO defaults and Clause 22/45 mode, waits for busy clear, writes the port/device control fields, optionally writes the Clause 45 register address, then writes data or triggers a read and waits again. Read errors return `0xffff` to match MDIO absent-device semantics. `enetc_hw_alloc` devm-allocates a hardware wrapper with only the port register base set.

## State and Persistence
Hardware state includes MDIO configuration, control, address, and data registers. The controller clock divide and hold/negative-edge settings are programmed on every transaction. Software state lives in `struct enetc_mdio_priv` via the selected `mdio_base` and ENETC hardware pointer. `enetc_mdio_lock` is global state used by accessor wrappers when ERR050089 is active.

## Dependencies and Integration Points
Used by PF common code for port/internal MDIO buses and by the PCI MDIO driver. It relies on `enetc_port_rd_mdio` and `enetc_port_wr_mdio`, which take the erratum write lock when active. Integrates with Linux `mii_bus`, OF MDIO registration, phylink/PCS creation, and standalone central EMDIO probing.

## Risks
Clock divider values are fixed; incorrect board clocks could violate MDIO timing. Busy polling timeout is 10 ms. Returning `0xffff` hides read errors by design but can mask wiring issues. Erratum locking requires all non-MDIO register accesses to use the matching accessors.

## Test Signals
Probe PHYs through port MDIO, internal PCS MDIO, and PCI central MDIO; test Clause 22 and 45 reads/writes, absent PHY reads, timeout/error injection, concurrent MDIO plus packet traffic on LS1028A erratum hardware, and phylink link mode negotiation.
