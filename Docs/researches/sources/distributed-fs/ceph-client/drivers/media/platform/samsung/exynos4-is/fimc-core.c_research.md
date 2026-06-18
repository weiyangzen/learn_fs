# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-core.c

## Purpose
`fimc-core.c` provides common FIMC/CAMIF device infrastructure: supported pixel formats, scaler calculations, DMA address derivation, V4L2 controls, format helpers, clock/probe/remove handling, IRQ dispatch, runtime PM, and platform/OF variant data.

## Important APIs, Types, and Functions
Format helpers include `fimc_get_format()`, `fimc_find_format()`, `fimc_adjust_mplane_format()`, and `__fimc_get_format()`. Scaler and DMA helpers include `fimc_check_scaler_ratio()`, `fimc_set_scaler_info()`, `fimc_prepare_addr()`, `fimc_set_yuv_order()`, and `fimc_prepare_dma_offset()`. Control APIs are `fimc_ctrls_create()`, `fimc_ctrls_delete()`, `fimc_ctrls_activate()`, and `fimc_alpha_ctrl_update()`. Driver lifecycle is handled by `fimc_parse_dt()`, `fimc_probe()`, PM callbacks, `fimc_remove()`, `fimc_register_driver()`, and `fimc_unregister_driver()`. `fimc_irq_handler()` dispatches completion to either mem2mem or capture paths.

## Control Flow
Probe parses DT or platform data, validates the entity id, initializes locks and waitqueues, maps registers, acquires clocks, sets bus clock rate, enables the bus clock, requests the IRQ, initializes the capture subdev, enables runtime PM, and configures DMA segment limits. Runtime resume enables the gate clock, resets hardware, and resumes capture or mem2mem. Runtime suspend stops capture or m2m, then disables the gate clock. The IRQ handler clears hardware IRQ state, then either completes a pending m2m job, handles m2m suspend synchronization, or forwards capture frame handling.

## State and Persistence
Device state is kept in `struct fimc_dev`, especially `state` bits, `variant`, `drv_data`, clocks, mapped registers, `m2m`, and `vid_cap`. Per-operation state lives in `struct fimc_ctx`, frame descriptors, scaler values, effect settings, and controls. No persistent storage is used; hardware configuration is regenerated after reset/resume.

## Dependencies and Integration Points
The file depends on V4L2/vb2, media-controller headers, runtime PM, common clock framework, platform/OF APIs, syscon regmap for ISP writeback, FIMC register helpers, media-device pipeline code, and the FIMC mem2mem/capture modules. OF compatibles include S5PV210, Exynos4210, and Exynos4212 variants.

## Risks and Edge Cases
Scaler math rejects 64x or greater downscale ratios and swaps target dimensions for rotation. DMA address derivation assumes plane layout consistency for packed, planar, multi-planar, metadata, and tiled formats. Runtime PM chooses capture over m2m when capture is busy. `fimc_probe()` has early-return paths after clock enable where cleanup must remain correct. OF `samsung,lcd-wb` instances are rejected because they are not normal camera/video postprocessor nodes.

## Test Signals
Build and probe each compatible, validate DT pixel-limit parsing, clock rate/enable failure unwinding, IRQ routing for m2m and capture, scaler ratio and copy-mode calculations, DMA addresses for all supported formats, control activation/inactivation and alpha range updates, runtime suspend/resume during capture and m2m jobs, and remove cleanup of subdev, DMA limits, and clocks.
