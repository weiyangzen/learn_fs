# sources/distributed-fs/ceph-client/include/linux/mtd/lpc32xx_slc.h

## Purpose

Provides platform data for the LPC32xx SLC NAND controller.

## Important APIs, Types, and Functions

The single exported type is `struct lpc32xx_slc_platform_data` with a `dma_filter_fn dma_filter` field.

Source-visible symbols include structs: `struct lpc32xx_slc_platform_data`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_LPC32XX_SLC_H`.

## Control Flow

Platform code supplies DMA filtering during controller probe; the SLC controller consumes it when acquiring DMA channels.

## State and Persistence Behavior

The header contains only static platform configuration and no persistent state.

## Dependencies and Integration Points

It depends on the DMA engine API and the LPC32xx SLC controller implementation.

Direct includes observed in the source are: `#include <linux/dmaengine.h>`.

## Risks and Edge Cases

Incorrect DMA channel matching can break high-throughput or DMA-required NAND access.

## Test Signals

Board probe tests should confirm filter acceptance, channel acquisition, and fallback behavior.

Source read signal: 17 lines, 348 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
