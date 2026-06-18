# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-scaler.h

## Purpose
This header defines the Samsung scaler register map and bitfield helpers for `exynos_drm_scaler.c`. It covers global status/config, interrupts, source/destination format and DMA, spans, luma/chroma positions, sizes, ratios, rotation/reflection, filter coefficients, color-space conversion, dithering, version, cycle/timeout counters, blending, fill, address queues, CRC, and shadow register offset.

## Important APIs, Types, and Functions
Important groups include `SCALER_STATUS`, `SCALER_CFG`, `SCALER_INT_EN`, `SCALER_INT_STATUS`, `SCALER_SRC_*`, `SCALER_DST_*`, `SCALER_H_RATIO`, `SCALER_V_RATIO`, `SCALER_ROT_CFG`, coefficient macros `SCALER_YHCOEF()`, `SCALER_YVCOEF()`, `SCALER_CHCOEF()`, `SCALER_CVCOEF()`, `SCALER_CSC_COEF()`, timeout and blend/fill registers, queue status registers, and CRC registers. Generic helpers `SCALER_MASK`, `SCALER_GET`, and `SCALER_SET` encode most fields. Color constants map YUV/RGB DRM formats to hardware values.

## Control Flow
The header has no runtime flow. The scaler driver uses it to reset hardware, enable a broad set of error and frame-end interrupts, write source/destination format/addresses/spans/rectangles, set scaling ratios, encode rotation/reflection, configure CSC, set a timeout, start a command, and decode/ack interrupt status.

## State and Persistence Behavior
Scaler MMIO state persists for the active IPP command. Non-shadow status/interrupt/version/counter registers reflect live hardware state, while other registers may be shadowed depending on the block. The driver rewrites the state after every reset for each task.

## Dependencies and Integration Points
The direct consumer is `exynos_drm_scaler.c`. The macros are connected to Exynos IPP format tables, DRM rotation bits, Samsung tile modifiers, timeout handling, CSC conversion, and IRQ completion.

## Risks
`SCALER_MASK` uses `1 << width`, so fields with width equal to or exceeding the native int bit width would be unsafe; current fields stay below that but should be reviewed when adding fields. Many setters mask values to field width, which can silently truncate invalid input if validation is missing. Source and destination chroma position math depends on the format table's tile dimensions. Address queue and blending macros are defined even though the current driver does not fully exercise them, so unused definitions may drift from hardware documentation.

## Test Signals
Test scaler task programming for all supported formats, luma/chroma span fields, source/destination positions and sizes, scaling ratio encoding, rotation/reflection bits, CSC coefficients, timeout interrupt, illegal-parameter interrupts, frame-end interrupt, CRC/debug paths if enabled, and register readback on Exynos5420/5433.
