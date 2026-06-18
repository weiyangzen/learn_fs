# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.h

## Purpose
`dwmac-intel.h` centralizes Intel DWMAC PCI glue constants for SerDes MDIO registers, power/rate fields, MDIO addresses, cross timestamping, PTP clock selection, and PMC ModPHY register programming values.

## Important APIs, Types, And Functions
- SerDes register indices: `SERDES_GCR`, `SERDES_GSR0`, and `SERDES_GCR0`.
- SerDes bitfields cover PLL clock request/ack, PHY RX clock, reset, power state, link mode, PCIe rate, and PCLK rate.
- `INTEL_MGBE_ADHOC_ADDR` and `INTEL_MGBE_XPCS_ADDR` identify non-PHY MDIO addresses used by Intel glue and XPCS.
- Cross timestamp constants include ART CPUID leaf and EHL PSE ART base frequency.
- PTP clock frequency masks define PSE and PCH GMAC GPIO encodings for 19.2, 200, and 256 MHz cases.
- ModPHY register indices and 1G/2.5G values are consumed by PMC IPC programming in `dwmac-intel.c`.

## Control Flow
No executable flow; definitions are consumed by the Intel PCI glue driver during SerDes power sequencing, interface detection, PTP clock setup, cross timestamp adjustment, and PMC ModPHY programming.

## State And Persistence
Constants define hardware register values that persist when written by `dwmac-intel.c`.

## Dependencies And Integration Points
The header assumes GMAC GPIO bit definitions from included STMMAC/DWMAC headers are visible to consumers. It is private to Intel DWMAC glue.

## Risks
- Typo `SERSED_LINK_MODE_1G` is unused or easy to misuse.
- ModPHY magic values are hardware/firmware-specific and should not be changed without Intel platform validation.
- MDIO addresses are masked out from normal PHY scanning in the driver; changing them affects discovery.

## Test Signals
Successful Intel PCI driver compile, correct SerDes power transitions, SGMII/2.5G mode detection, PTP frequency selection, and PMC ModPHY programming for 1G and 2.5G cases.
