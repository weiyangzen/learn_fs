# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am64.c

## Purpose
This file declares the AM64 PSI-L endpoint map for K3 UDMA. It covers SAUL, ICSSG Ethernet, PDMA SPI/USART/ADC, and CPSW2 endpoints with AM64-specific mapped channel and flow assignments.

## Important APIs, Types, and Functions
The exported data object is `struct psil_ep_map am64_ep_map`. Macros include `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_ETHERNET()`, and `PSIL_SAUL()`. Unlike older maps, AM64 Ethernet and SAUL macros encode mapped channel IDs and flow ranges directly, including single-flow ICSSG TX entries and wider RX ranges.

## Control Flow
There are no local functions. Generic PSI-L lookup selects this map for the `AM64X` family and linearly searches source or destination arrays based on the requested thread ID. The destination-thread bit distinguishes TX IDs such as `0xc100`/`0xc500` from RX IDs such as `0x4100`/`0x4500`.

## State and Persistence
The arrays are static endpoint configuration tables. They are persistent for the lifetime of the driver and can be modified indirectly through `psil_set_new_ep_config()`.

## Dependencies and Integration Points
This map is linked into `k3-psil-lib.o` and supplies endpoint metadata to TI K3 UDMA. It depends on public K3 PSI-L endpoint config definitions and the generic SoC-family selector.

## Risks
AM64 has explicit channel/flow data for ICSSG, CPSW2, and SAUL; errors here lead to wrong UDMA channel or flow allocation. ADC endpoints use TR mode while SPI/USART use packet mode, so endpoint-type mismatches can break PDMA setup. Destination ICSSG Ethernet entries use one flow each, while CPSW2 uses eight-flow windows.

## Test Signals
Validate AM64 UDMA clients for ICSSG RX/TX, CPSW2 RX/TX, SAUL crypto, SPI/USART PDMA packet mode, and ADC TR mode. Lookup tests should include representative source/destination pairs and verify flow ranges/default flow IDs.
