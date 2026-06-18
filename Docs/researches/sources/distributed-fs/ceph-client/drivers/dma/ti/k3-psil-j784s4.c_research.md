# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j784s4.c

## Purpose
This file defines the J784S4 PSI-L endpoint map. It covers main-domain McASP, SPI, CPSW2G, UART, extensive CSI2RX, CPSW9G, main SA2UL, MCU CPSW0, MCU PDMA, MCU ADC, and MCU SA2UL endpoints.

## Important APIs, Types, and Functions
The exported symbol is `struct psil_ep_map j784s4_ep_map`. Macros include `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_PDMA_MCASP()`, `PSIL_ETHERNET()`, `PSIL_SA2UL()`, and `PSIL_CSI2RX()`. They encode native packet endpoints with EPIB/PSD metadata, PDMA packet/TR modes, McASP PDMA burst/access flags, and SA2UL direction flags.

## Control Flow
Generic lookup in `k3-psil.c` selects this map for the `J784S4` family. Source lookups cover RX endpoints; destination lookups cover explicit TX entries for Ethernet, SA2UL, PDMA SPI, and MCU endpoints. The map itself has no executable control path.

## State and Persistence
The source/destination arrays are persistent static data. They are mutable indirectly through the generic replacement API, which copies new endpoint configuration into the matching map entry.

## Dependencies and Integration Points
The map depends on K3 PSI-L endpoint types and is linked into `k3-psil-lib.o`. K3 UDMA uses the selected endpoint config to determine packet mode, EPIB, PSD, PDMA behavior, and endpoint type.

## Risks
J784S4 has very large CSI2RX source ranges, including `0x4900`-style and `0x4940`-`0x499f` IDs, making duplicate/omitted entries hard to spot manually. Destination groups are ordered differently than source groups. Main and MCU domain IDs must not be confused. Ethernet entries are native packet mode without explicit flow data in this map style.

## Test Signals
Use table validation for all expected J784S4 DT thread IDs, plus hardware tests for CSI capture, CPSW2G/CPSW9G, SA2UL, SPI, McASP, UART, MCU CPSW0, and MCU PDMA/ADC paths. Include invalid ID lookup checks.
