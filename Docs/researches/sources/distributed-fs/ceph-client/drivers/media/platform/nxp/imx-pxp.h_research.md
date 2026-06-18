# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-pxp.h

## Purpose
`imx-pxp.h` is the register and bitfield definition header for the Freescale/NXP i.MX Pixel Pipeline block. It provides the symbolic offsets, masks, shifts, field-construction macros, and enumerated field values used by `imx-pxp.c` to program the PXP hardware.

## Important APIs, Types, and Functions
The file exports preprocessor macros only. Register offset groups include `HW_PXP_CTRL`, `HW_PXP_STAT`, `HW_PXP_OUT_*`, `HW_PXP_PS_*`, `HW_PXP_AS_*`, `HW_PXP_CSC1_*`, `HW_PXP_CSC2_*`, `HW_PXP_LUT_*`, `HW_PXP_ALPHA_*`, `HW_PXP_DATA_PATH_CTRL*`, `HW_PXP_IRQ_MASK`, `HW_PXP_IRQ`, `HW_PXP_NEXT`, `HW_PXP_DEBUG*`, and `HW_PXP_VERSION`.

For most fields the header defines `BP_*` bit positions, `BM_*` masks, `BF_*()` value packing macros, and `BV_*__*` enumerants. Important groups include global control bits for reset, clock gate, enable, interrupts, rotation, flipping, CSC2, LUT, dither, and PS/AS output; status bits for completion and AXI errors; output and processed-surface buffer addressing, pitch, dimensions, decimation, scale, and format fields; alpha-surface blending and ROP fields; CSC coefficient packing for both CSC engines; data path mux fields; and 36-bit-free 32-bit DMA address fields.

## Control Flow
There is no runtime control flow in this header. It participates at compile time by expanding constants and bitfield constructors in the PXP driver. The driver writes the register offsets through regmap and builds values with these macros when configuring per-job geometry, formats, CSC coefficients, interrupts, and data-path muxing.

## State and Persistence
The header stores no state. It encodes the hardware's volatile register layout. Correctness depends on these macros matching the SoC register specification used by the runtime driver.

## Dependencies and Integration Points
The primary integration point is `imx-pxp.c`, which includes the header and uses its offsets as the regmap address space. The `HW_PXP_VERSION` offset also defines the maximum register exposed in the driver's regmap config. The macro style is compatible with plain C constant expressions and includes a special `BF_PXP_CSC1_COEF0_UV_OFFSET()` multiplication form to work around an old GCC constant-expression issue with negative values.

## Risks and Edge Cases
Generated-style headers are prone to silent hardware misprogramming if masks, offsets, or enumerants drift from the reference manual. Some fields describe unused driver capabilities such as LUT, alpha surfaces, WFE, memory init, and debug paths, so changes could affect future users even if current code does not exercise them. Several signed CSC offset fields are packed through unsigned masks, so coefficient tests should verify negative offset encoding.

## Test Signals
Build coverage is the main static signal: all macros must compile in `imx-pxp.c`. Runtime signals are correct PXP reset, version read at `HW_PXP_VERSION`, successful format programming, correct IRQ masking and clearing, accurate CSC output, and no AXI or status error bits when exercising supported buffer layouts.
