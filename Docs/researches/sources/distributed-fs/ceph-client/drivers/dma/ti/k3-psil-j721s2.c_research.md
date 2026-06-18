# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j721s2.c

## Purpose
This file declares the J721S2 PSI-L endpoint map. It covers main-domain McASP, SPI, CPSW2G, UART, CSI2RX, main SA2UL, MCU CPSW0, MCU PDMA, MCU ADC, and MCU SA2UL endpoints.

## Important APIs, Types, and Functions
The exported object is `struct psil_ep_map j721s2_ep_map`. Macros are `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_PDMA_MCASP()`, `PSIL_ETHERNET()`, `PSIL_SA2UL()`, and `PSIL_CSI2RX()`. These build endpoint configs for PDMA XY TR/packet, McASP burst/access, native packet Ethernet, SA2UL packet endpoints, and native CSI2RX.

## Control Flow
The file is selected by `psil_get_ep_config()` for SoC family `J721S2`. The generic lookup searches destination entries first when the destination bit is set and then source entries after masking the destination bit. Source entries include large CSI2RX ranges and both main and MCU domains.

## State and Persistence
The endpoint arrays are static global data. They can be changed by `psil_set_new_ep_config()` if a caller replaces a config associated with a device-tree DMA name.

## Dependencies and Integration Points
The file is compiled into the K3 PSI-L library and depends on the private map declarations. It integrates J721S2 peripheral endpoints with the K3 UDMA driver.

## Risks
J721S2 destination map is much smaller than its source map, so many TX-capable-looking peripherals may rely on symmetric fallback or may not be TX endpoints. CSI2RX ranges are numerous and easy to truncate. Main SA2UL uses `0x4a40`/`0xca40`, while MCU SA2UL uses `0x7500`/`0xf500`; confusing these would route to the wrong domain.

## Test Signals
Validate lookup and DMA operation for McASP, SPI groups, CPSW2G, UART, CSI2RX, main SA2UL, MCU CPSW0, MCU SPI/UART/ADC, and MCU SA2UL. Table tests should compare expected DT thread IDs against the map.
