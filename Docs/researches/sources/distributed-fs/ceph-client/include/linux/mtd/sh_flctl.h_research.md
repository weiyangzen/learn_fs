# sources/distributed-fs/ceph-client/include/linux/mtd/sh_flctl.h

## Purpose

Defines registers, bit fields, platform data, and driver state for the Renesas SuperH FLCTL NAND controller.

## Important APIs, Types, and Functions

Important items are FLCTL register macros, command/control bit masks, `enum flctl_ecc_res_t`, `struct sh_flctl`, `struct sh_flctl_platform_data`, and `mtd_to_flctl()`.

Source-visible symbols include structs: `struct dma_chan;`, `struct sh_flctl`, `struct nand_chip	chip;`, `struct platform_device	*pdev;`, `struct dev_pm_qos_request pm_qos;`, `struct dma_chan		*chan_fifo0_rx;`, `struct dma_chan		*chan_fifo0_tx;`, `struct completion	dma_complete;`, `struct sh_flctl_platform_data`, `struct mtd_partition	*parts;`; enums: `enum flctl_ecc_res_t`; typedefs: none visible in this header; prototypes: `return container_of(mtd_to_nand(mtdinfo), struct sh_flctl, chip);`; representative macros: `__SH_FLCTL_H__`, `FLCMNCR`, `FLCMDCR`, `FLCMCDR`, `FLADR`, `FLADR2`, `FLDATAR`, `FLDTCNTR`, `FLINTDMACR`, `FLBSYTMR`, `FLBSYCNT`, `FLDTFIFO`, `FLECFIFO`, `FLTRCR`, `FLHOLDCR`, `_4ECCCNTEN`.

## Control Flow

The driver programs FLCMNCR/FLCMDCR/FLADR/FLDATAR/FIFO/ECC registers, tracks staged SEQIN/ERASE command parameters, uses DMA channels when available, and maps `mtd_info` back to the enclosing `sh_flctl` through the embedded `nand_chip`.

## State and Persistence Behavior

Runtime state includes the raw NAND chip, platform device, PM QoS request, MMIO base, FIFO address, data buffer, command staging fields, address-cycle settings, base register values, page-size/ECC/hold/QoS flags, DMA channels, and DMA completion.

## Dependencies and Integration Points

It depends on completions, MTD/raw NAND/partition APIs, PM QoS, platform devices, and DMA engine.

Direct includes observed in the source are: `#include <linux/completion.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/rawnand.h>`, `#include <linux/mtd/partitions.h>`, `#include <linux/pm_qos.h>`.

## Risks and Edge Cases

Clock divider bits, hold control, ECC result handling, and DMA FIFO synchronization are hardware-sensitive. The fixed `done_buff` size assumes maximum 2048+64 page/OOB data.

## Test Signals

Probe platform data variations, 512/2048 page modes, hardware ECC result classes, DMA read/write completion, timeout paths, and PM QoS hold behavior.

Source read signal: 180 lines, 5927 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
