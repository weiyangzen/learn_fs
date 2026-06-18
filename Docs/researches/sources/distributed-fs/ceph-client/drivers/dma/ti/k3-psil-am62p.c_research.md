# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62p.c

## Purpose
This file defines the AM62P PSI-L endpoint map, also reused for the J722S SoC family by the generic selector. It covers SAUL, PDMA SPI/UART/McASP, CPSW3G, and a large CSI2RX source-thread set including J722S-only additional receivers.

## Important APIs, Types, and Functions
The exported data object is `struct psil_ep_map am62p_ep_map`. Macros include `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_ETHERNET()`, `PSIL_SAUL()`, `PSIL_PDMA_MCASP()`, and `PSIL_CSI2RX()`. Entries populate packet mode, EPIB/PSD metadata, mapped channel IDs, flow windows, default flow IDs, and PDMA burst/access flags.

## Control Flow
The file is declarative. `psil_get_ep_config()` in `k3-psil.c` selects it for `AM62PX` and `J722S`, then searches source and destination arrays. Source entries cover RX endpoints, while destination entries cover TX endpoints.

## State and Persistence
Endpoint arrays are static global data. They are logically read-only configuration, but the generic `psil_set_new_ep_config()` API can overwrite an entry for a device-tree named DMA.

## Dependencies and Integration Points
The map depends on `k3-psil-priv.h` and is part of the `k3-psil-lib.o` object group. It feeds K3 UDMA channel and flow setup for AM62P/J722S peripherals.

## Risks
The source array includes repeated `0x5000`-`0x501f` CSI2RX entries followed by J722S-only `0x5100`-`0x531f` ranges. Duplicate thread IDs mean lookup returns the first matching config; that is harmless only if duplicate configs are intentionally identical. Reusing AM62P for J722S can hide SoC-specific differences if future peripherals diverge. Flow assignments for SAUL and CPSW must match board firmware/resource allocation.

## Test Signals
Verify `psil_get_ep_config()` for AM62P and J722S families, including duplicate CSI2RX IDs, J722S-only CSI IDs, CPSW3G TX/RX channels, SAUL flows, and PDMA endpoints. A static duplicate-ID checker would be useful for this map.
