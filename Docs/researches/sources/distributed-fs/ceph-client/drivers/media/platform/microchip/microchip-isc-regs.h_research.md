# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-regs.h

## Purpose
`microchip-isc-regs.h` defines the register offsets, bit masks, field helpers, product-specific offset deltas, and packing constants used by the Microchip ISC and XISC drivers.

## Important APIs, Types, and Functions
The header covers control/status (`ISC_CTRLEN`, `ISC_CTRLDIS`, `ISC_CTRLSR`), PFE configuration, clock registers, interrupt registers, DPC, white balance, CFA, color correction, gamma, XISC scaler/VHXS, CSC, contrast/brightness, subsampling, RLP, histogram, DMA, version, and histogram-entry registers. Product deltas such as `ISC_SAMA5D2_*_OFFSET` and `ISC_SAMA7G5_*_OFFSET` let shared code address variant layouts.

## Control Flow
Runtime code includes this header and uses the constants to program blocks in the pipeline: PFE samples sensor data, optional DPC/WB/CFA/CC/GAM/CSC/CBC/subsampling/RLP stages transform it, DMA writes planes, and histogram/AWB logic consumes histogram entries.

## State and Persistence
The file defines no state. The constants describe volatile MMIO state owned by the hardware and programmed through regmap in other files.

## Dependencies and Integration Points
It depends on `linux/bitops.h` for `BIT()` and `GENMASK()`. It is integrated by the shared base, clock, scaler, and product-specific ISC/XISC files.

## Risks and Edge Cases
Many fields are shared across SAMA5D2 and SAMA7G5 but shifted by per-block offsets; using the wrong offset will program the wrong block. Some names retain historical typos such as `ISC_PFG_CFG0_BPS_*`, so renames can be risky for downstream code. YUV packing constants and DMA plane address offsets must remain aligned with vb2 size calculations.

## Test Signals
Compile coverage is the first signal. Runtime validation should include frame capture for all supported RLP/DMA modes, interrupt delivery for DMA and histogram, clock enable/disable status, AWB histogram reads, and product-specific SAMA5D2/SAMA7G5 register offset correctness.
