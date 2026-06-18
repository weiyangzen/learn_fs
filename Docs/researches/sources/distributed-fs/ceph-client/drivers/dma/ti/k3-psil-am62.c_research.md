# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62.c

## Purpose
This file declares the AM62 PSI-L endpoint map consumed by the K3 UDMA PSI-L library. It maps source and destination thread IDs to endpoint configuration for SAUL, PDMA SPI/UART/McASP, CPSW3G Ethernet, and CSI2RX.

## Important APIs, Types, and Functions
There are no executable functions. The exported data object is `struct psil_ep_map am62_ep_map`. Macros build `struct psil_ep` entries: `PSIL_PDMA_XY_PKT()`, `PSIL_ETHERNET()`, `PSIL_SAUL()`, `PSIL_PDMA_MCASP()`, and `PSIL_CSI2RX()`. These fill `struct psil_endpoint_config` fields such as endpoint type, packet mode, EPIB requirements, PSD size, mapped channel ID, flow range, default flow, and `notdpkt`.

## Control Flow
Runtime lookup happens in `k3-psil.c`, not here. When the detected SoC family is AM62X, `psil_get_ep_config()` searches `am62_src_ep_map` or `am62_dst_ep_map` for the requested thread ID. Source entries are used for RX (`DMA_DEV_TO_MEM`) and destination entries for TX (`DMA_MEM_TO_DEV`).

## State and Persistence
The arrays are static map data compiled into `k3-psil-lib.o`. `psil_set_new_ep_config()` can mutate returned endpoint configs at runtime for named device-tree DMA entries, so these static entries can become process-wide runtime configuration state.

## Dependencies and Integration Points
The file depends on `k3-psil-priv.h` and public `linux/dma/k3-psil.h` endpoint definitions. It is linked by the TI DMA Makefile and selected by `soc_device_match()` for family `AM62X`.

## Risks
Thread IDs, flow ranges, and channel IDs must match SoC integration data. Ethernet and SAUL entries carry explicit flow/channel assignments, so incorrect numbers can break packet DMA. CSI2RX entries are native endpoints with minimal config and rely on consumers/UDMA for the rest. Runtime mutation of static config should be treated carefully because all later lookups observe the changed data.

## Test Signals
Validate AM62 UDMA clients for SAUL RX/TX, SPI/UART PDMA packet mode, McASP 32-bit burst mode, CPSW3G packet DMA flows, and CSI2RX streams. Unit-style checks can call `psil_get_ep_config()` for representative source, destination, and invalid thread IDs.
