# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am654.c

## Purpose
This file provides the AM654 PSI-L endpoint map. It covers SA2UL, PRU_ICSSG Ethernet, PDMA McASP/SPI/USART/ADC, CPSW0, and MCU PDMA endpoints for early K3 AM65x devices.

## Important APIs, Types, and Functions
The exported object is `struct psil_ep_map am654_ep_map`. Endpoint macros are `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_ETHERNET()`, and `PSIL_SA2UL()`. Compared with newer AM62/AM64 maps, Ethernet and SA2UL entries do not encode mapped channel/flow IDs here; they primarily set endpoint type, packet mode, EPIB, PSD size, and `notdpkt` for TX SA2UL.

## Control Flow
The file contributes data only. `k3-psil.c` selects `am654_ep_map` for family `AM65X`; lookups then search source or destination arrays. Source entries correspond to RX threads such as `0x4000`, `0x4100`, `0x4400`, and MCU ranges; destination entries include `0xc000`, ICSSG TX ranges, and CPSW0 `0xf000`-style IDs.

## State and Persistence
The endpoint arrays persist as static module/kernel data and may be overwritten by the generic `psil_set_new_ep_config()` API when a caller supplies replacement config for a named DMA.

## Dependencies and Integration Points
The map is linked through the TI DMA Makefile and depends on `k3-psil-priv.h`. It integrates with K3 UDMA and the AM65x SoC-family match table.

## Risks
Because older entries omit explicit flow/channel mapping, consumers must rely on defaults or other UDMA resource management paths. Thread IDs span main and MCU domains, so accidental removal of MCU ranges breaks low-power/peripheral DMA. SA2UL TX uses `notdpkt`, and incorrect direction flags would affect packet formatting.

## Test Signals
Test AM65x UDMA endpoint lookup for SA2UL RX/TX, PRU_ICSSG, CPSW0, PDMA McASP/SPI/USART, MCU SPI/USART, and ADC TR endpoints. Negative tests should verify unknown thread IDs return `-ENOENT`.
