# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-sama7g5-isc.c

## Purpose
`microchip-sama7g5-isc.c` is the SAMA7G5 XISC product driver. It adapts the shared ISC base to the extended SAMA7G5 pipeline, including MIPI input flagging, wider format support, XISC register offsets, DPC/gamma behavior, and AXI DMA settings.

## Important APIs, Types, and Functions
The file defines SAMA7G5 output/input format tables, a bipartite gamma table, product callbacks `isc_sama7g5_config_csc()`, `isc_sama7g5_config_cbc()`, `isc_sama7g5_config_cc()`, `isc_sama7g5_config_ctrls()`, `isc_sama7g5_config_dpc()`, `isc_sama7g5_config_gam()`, `isc_sama7g5_config_rlp()`, and `isc_sama7g5_adapt_pipeline()`. DT/probe functions are `xisc_parse_dt()` and `microchip_xisc_probe()`, with runtime PM in `xisc_runtime_suspend()` and `xisc_runtime_resume()`.

## Control Flow
Probe maps MMIO, initializes regmap, requests the shared ISR, installs SAMA7G5 callbacks and offsets, configures 3264x2464 limits, uses 32-beat AXI DMA bursts, disables ISPCK because XISC is clocked by MCK, initializes pipeline regmap fields, enables `hclock`, registers generated clocks, registers V4L2, parses endpoints, registers async notifiers, reads the version at the SAMA7G5 offset, initializes the media graph/scaler, and enables runtime PM. DT parsing adds normal parallel/BT.656 polarity bits and optionally sets `ISC_PFE_CFG0_MIPI` when `microchip,mipi-mode` is present.

## State and Persistence
State lives in `isc_device` and static SAMA7G5 tables/callbacks. Hardware state is volatile and rebuilt during streaming or runtime resume. There is no persisted state.

## Dependencies and Integration Points
The driver binds `microchip,sama7g5-isc`, depends on shared ISC common code, regmap, V4L2 async/fwnode, hclock and generated MCK clocks, and can be connected behind `microchip-csi2dc` through MIPI mode.

## Risks and Edge Cases
The SAMA7G5 input table includes UYVY and output table includes UYVY/VYUY/Y16 not present in SAMA5D2, so format regression tests must be product-specific. DPC and bipartite gamma are configured only through callbacks. `microchip,mipi-mode` is a global device property, so mixed endpoint topologies would apply MIPI PFE mode to all parsed endpoints.

## Test Signals
Validate MIPI and parallel DT endpoints, capture through CSI2DC, supported UYVY/VYUY/Y16 formats, DPC bay selection, gamma bipartite bit, 32-beat DMA configuration, runtime PM hclock balance, and max-size capture at 3264x2464.
