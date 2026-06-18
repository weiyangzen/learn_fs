# sources/distributed-fs/ceph-client/include/linux/mtd/lpc32xx_mlc.h

## Purpose

Provides platform data for the LPC32xx MLC NAND controller.

## Important APIs, Types, and Functions

The single exported type is `struct lpc32xx_mlc_platform_data` with a `dma_filter_fn dma_filter` field.

Source-visible symbols include structs: `struct lpc32xx_mlc_platform_data`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_LPC32XX_MLC_H`.

## Control Flow

Board or platform code passes a DMA channel filter to the LPC32xx MLC controller driver during probe so the driver can request appropriate DMA resources.

## State and Persistence Behavior

No runtime or persistent state is stored here; it is probe-time configuration.

## Dependencies and Integration Points

It depends on the DMA engine API and the LPC32xx MLC NAND controller driver.

Direct includes observed in the source are: `#include <linux/dmaengine.h>`.

## Risks and Edge Cases

A wrong or missing DMA filter can force probe failure or fall back to slower/unsupported transfer paths depending on the driver.

## Test Signals

Probe with valid and invalid DMA filter functions and verify DMA channel selection.

Source read signal: 17 lines, 348 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
