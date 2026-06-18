# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mdio.c

## Purpose
`fbnic_mdio.c` creates a software Clause 45 MDIO bus that lets Linux phylink/XPCS code interact with FBNIC PMA/PMD and PCS state even though the underlying data comes from FBNIC CSRs and driver-maintained PMD training state.

## Important APIs, Types, And Functions
The public API is `fbnic_mdiobus_create()`. Bus callbacks are `fbnic_mdio_read_c45()` and `fbnic_mdio_write_c45()`, which dispatch to PMD helpers (`fbnic_mdio_read_pmd()`, `fbnic_mdio_write_pmd()`) or PCS helpers (`fbnic_mdio_read_pcs()`, `fbnic_mdio_write_pcs()`). Constants translate Synopsys XPCS vendor-page bit usage into FBNIC PCS page layout.

## Control Flow
Probe calls `fbnic_mdiobus_create()`, which allocates a devm-managed `mii_bus`, installs C45 callbacks, masks all PHY addresses to prevent autoprobing, registers it, and stores it in `fbd->mdio_bus`. PMD reads synthesize device IDs, device presence, reset-ready status, and lane detection, returning lane detect only when `fbd->pmd_state == FBNIC_PMD_SEND_DATA`. PCS reads either synthesize XPCS IDs/capability registers or read mapped FBNIC PCS CSRs. PCS writes are translated and forwarded to CSR space; PMD writes are logged only.

## State And Persistence
The created bus is devm-managed and stored on `fbnic_dev`. PCS writes persist in hardware registers. PMD results are mostly synthetic and depend on driver state (`netdev`, `fbn->aui`, `fbd->pmd_state`) rather than a real MDIO-attached PHY.

## Dependencies And Integration Points
This file depends on Linux MDIO, `pcs-xpcs`, `fbnic_mac.h` state values, and FBNIC CSR register access. `fbnic_phylink_create()` uses the bus with `xpcs_create_pcs_mdiodev()`, making this file a bridge between phylink/XPCS generic code and FBNIC-specific hardware.

## Risks
The synthetic MDIO layer must match what XPCS expects. Returning zero for unsupported registers is simple but can hide missing emulation if XPCS starts depending on more PMD/PCS registers. Vendor-page bit remapping and address bounds determine whether writes hit the intended PCS half, especially for 50G R2 mode. The PMD lane-detect read is gated by driver training state, so stale PMD state can alter phylink behavior.

## Test Signals
Probe should create the MDIO bus and XPCS PCS successfully. Phylink should read expected PMA/PCS device IDs, supported devices, and lane-detect bits after training. Register tracing or dynamic debug can confirm PCS vendor-page read/write translation and absence of PHY autoprobe.
