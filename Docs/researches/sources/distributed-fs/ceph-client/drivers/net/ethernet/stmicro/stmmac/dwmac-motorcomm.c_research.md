<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-motorcomm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-motorcomm.c

## Purpose
`dwmac-motorcomm.c` is a PCI glue driver for Motorcomm YT6801-style DWMAC controllers. It initializes vendor management registers, resets the internal PHY/MDIO block, reads the MAC address from eFuse patch rows, configures MSI/MSI-X interrupts, and presents a GMAC4 stmmac platform device.

## Important APIs, Types, and Functions
- `struct dwmac_motorcomm_priv` stores the BAR0 base used for vendor and GMAC registers.
- eFuse helpers read byte rows, scan patch entries, and extract `MACA0LR/MACA0HR` into `res.mac`.
- `motorcomm_reset()` toggles `SYS_RESET_RESET` and deasserts internal MDIO/PHY reset.
- `motorcomm_init()` disables management interrupt routing, programs RX/TX interrupt moderation, and disables out-of-band WOL during normal operation.
- `motorcomm_default_plat_data()` creates stmmac defaults for DMA, AXI, checksumming, TSO, EEE/LPI, GMAC4, and PCI PM callbacks.
- `motorcomm_setup_irq()` prefers six MSI-X vectors and falls back to one MSI vector.

## Control Flow
PCI probe allocates private and platform data, enables and maps BAR0, disables PCIe L1 ASPM for interrupt reliability, resets the vendor block, waits for eFuse load, reads or randomizes the MAC address, sets up interrupts, initializes vendor registers, offsets stmmac MMIO by `GMAC_OFFSET`, and calls `stmmac_dvr_probe()`. Resume first runs generic PCI stmmac resume, then deasserts PHY reset and reinitializes vendor registers.

## State and Persistence
Runtime state is private BAR mapping plus stmmac platform data. Hardware state includes reset state, eFuse controller operation, interrupt moderation, OOB WOL disablement, PCI IRQ vectors, and MAC address resource data. eFuse is persistent hardware storage but the driver only reads it.

## Dependencies and Integration Points
The file depends on PCI, MSI/MSI-X APIs, iopoll, stmmac PCI helpers, GMAC4/DMA constants, and Ethernet address helpers. PCI IDs are vendor `0x1f0a`, device `0x6801`.

## Risks and Edge Cases
- eFuse reads need a post-reset delay; without it reads can return zeros.
- `motorcomm_efuse_read_byte()` writes `*byte` even if polling times out, so callers must respect the return code.
- No valid eFuse MAC falls back to a random MAC address.
- ASPM L1 is disabled unconditionally due to card-specific MSI delivery failures.
- MSI-X vector positions are assumed by the hardware mapping.

## Test Signals
PCI probe should be tested with valid eFuse MAC, empty eFuse, and eFuse timeout/error. Interrupt tests should exercise MSI-X and forced MSI fallback. Suspend/resume should verify DMA interrupts still arrive after D3hot. Traffic tests should check checksum/TSO, EEE/LPI behavior, and MAC address stability across reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-motorcomm.c -->
