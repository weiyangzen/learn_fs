# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_scaler.c

## Purpose
This file implements the Exynos scaler IPP backend for crop, scale, rotate, reflect, and color conversion operations. It programs source and destination DMA planes, spans, luma/chroma positions, size, scaling ratios, rotation, CSC coefficients, timeout, interrupts, and starts the scaler hardware for each IPP task.

## Important APIs, Types, and Functions
The main state is `struct scaler_context`, containing the IPP object, DRM device, DMA cookie, MMIO base, up to four clocks, active task, and SoC data. `struct scaler_data` selects clock names and supported format tables. `struct scaler_format` maps DRM fourcc formats to hardware color-format values and chroma tile geometry.

Key functions include `scaler_probe()`, `scaler_bind()`, `scaler_unbind()`, `scaler_commit()`, `scaler_irq_handler()`, `scaler_runtime_suspend()`, and `scaler_runtime_resume()`. Register-programming helpers cover reset, interrupt masks/status, source/destination format/base/span/position/size, ratios, rotation, CSC matrix, timeout, and hardware start. Format tables expose many YUV and RGB formats plus Samsung 16x16 tiled input/output entries with Exynos5420/5433 limits.

## Control Flow
Probe allocates context, selects SoC data, maps MMIO, requests a threaded IRQ, gets clocks, enables runtime PM autosuspend, and registers as a component. Bind registers DMA and calls `exynos_drm_ipp_register()` with crop, rotate, scale, and convert capabilities. `scaler_commit()` resolves source and destination DRM formats, resumes runtime PM, resets the scaler, stores the task, programs all source registers, programs all destination registers, computes horizontal and vertical fixed-point ratios with rotation awareness, writes rotation/reflection bits, selects a CSC matrix based on source format class, enables timeout and interrupts, and starts hardware. The IRQ handler acknowledges all status bits, disables interrupts, releases runtime PM, and completes the task with success only when `SCALER_INT_STATUS_FRAME_END` is present.

## State and Persistence Behavior
The active task is a single pointer cleared on interrupt completion. Runtime PM controls all clocks based on job activity and autosuspend. Hardware register state is rewritten per task after a soft reset. Supported formats, limits, and clock names persist as static SoC data. There is no software persistence across driver removal or system suspend beyond the component and runtime PM frameworks.

## Dependencies and Integration Points
The driver depends on the Exynos IPP core, DRM fourcc/modifier data, runtime PM, component binding, clock framework, register definitions in `regs-scaler.h`, and Samsung tiled format modifiers. It integrates with Exynos DRM DMA mapping helpers and device-tree compatibles `samsung,exynos5420-scaler` and `samsung,exynos5433-scaler`.

## Risks
`scaler_commit()` returns `-EIO` on reset failure after runtime PM resume without dropping the runtime PM reference, which can leak an active PM usage count on that path. `scaler_clk_ctrl()` ignores individual clock enable failures and always returns 0, making partial clock-enable failures hard to diagnose. The file contains a duplicated local declaration in `scaler_clk_ctrl()`, which would be a compile-time issue in a strict current build unless already patched elsewhere. Tile support is represented by `modifier != 0`, so any future nonzero modifier would be treated as tiled unless format validation prevents it. Ratio and position fields are masked by register macros; out-of-range values must be caught by IPP limits before commit.

## Test Signals
Exercise RGB and YUV conversions, NV12/NV21/YUV420/YUV422/YUV444 paths, tiled and linear buffers, up/down scaling within 1/4x to 16x limits, rotate 90/180/270, reflect X/Y, CSC direction changes, illegal size/ratio IRQs, timeout IRQs, reset failure injection, runtime PM autosuspend, and multi-clock Exynos5433 suspend/resume.
