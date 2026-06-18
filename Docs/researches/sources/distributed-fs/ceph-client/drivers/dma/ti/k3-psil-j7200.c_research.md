# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j7200.c

## Purpose
This file defines the J7200 PSI-L endpoint map for K3 UDMA. It covers McASP, SPI, UART, CPSW5, CPSW0, MCU PDMA, ADC, and SA2UL endpoints.

## Important APIs, Types, and Functions
The main symbol is `struct psil_ep_map j7200_ep_map`. Endpoint macros are `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_PDMA_MCASP()`, `PSIL_ETHERNET()`, and `PSIL_SA2UL()`. McASP endpoints set PDMA 32-bit access and burst flags; packet-mode PDMA covers SPI/UART; Ethernet entries set native packet mode with EPIB and 16-byte PSD; SA2UL entries set 64-byte PSD and TX `notdpkt`.

## Control Flow
The map is selected by `k3-psil.c` for SoC family `J7200`. Source entries are searched for RX threads; destination entries are searched first for destination IDs and can otherwise fall back to symmetric source lookup if an explicit destination is absent.

## State and Persistence
The source and destination arrays are static configuration state. Generic PSI-L APIs return pointers into these arrays, so runtime replacement through `psil_set_new_ep_config()` changes later lookups.

## Dependencies and Integration Points
This file depends on the private PSI-L map header and links into `k3-psil-lib.o`. It integrates J7200 peripheral thread IDs with K3 UDMA endpoint setup.

## Risks
The map contains multiple peripheral groups with similar contiguous IDs, making range omissions easy. CPSW5 and CPSW0 use different RX/TX ranges; incorrect thread IDs would route Ethernet traffic to the wrong endpoint. MCU-domain entries are separate from main-domain entries and need board-level validation. SA2UL appears near `0x7500`/`0xf500`, matching other K3 families but still SoC-specific.

## Test Signals
Validate J7200 lookup and DMA operation for McASP, SPI groups, UART groups, CPSW5, CPSW0, MCU SPI/UART, ADC, and SA2UL. Static table tests should check that each destination group expected by DT has a matching entry.
