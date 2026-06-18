# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isphist.c

## Purpose
`isphist.c` implements the OMAP3 ISP histogram statistics subdevice. It validates histogram region/bin/white-balance configuration, programs histogram registers, clears and reads hardware histogram memory, uses DMA when possible with PIO fallback, and exposes stats configuration/request/enable ioctls through `ispstat`.

## Important APIs, Types, And Functions
- `hist_validate_params()` checks CFA mode, region count, region bounds/order, legal bin counts per region count, and buffer size.
- `hist_setup_regs()` computes control, white-balance gain, and region registers, clears histogram memory, writes all hardware registers, and updates stat framework config counters.
- `hist_reset_mem()` clears internal histogram memory and resets frame accumulation wait count.
- `hist_buf_process()` gates capture on error/enabled state and accumulated-frame count, then chooses DMA or PIO readout.
- `hist_buf_dma()` configures a DMA slave transfer from histogram data register to the active stats buffer; `hist_buf_pio()` reads the same data by repeated register reads.
- Public lifecycle: `omap3isp_hist_init()` requests an optional DMA channel and initializes the stat subdevice; `omap3isp_hist_cleanup()` releases DMA and cleans up stats.

## Control Flow
Initialization allocates config storage, attempts to obtain any slave-capable DMA channel, falls back to PIO on non-deferral failure, assigns stat ops/event type, and initializes the stat subdevice. Config ioctls validate and stage settings through generic stat callbacks. When setup is requested, memory is cleared before registers are programmed. At interrupt/stat processing time, the module waits for `num_acc_frames`, reads stats through DMA or PIO, resets the wait counter, and returns stat-buffer status to the framework. DMA completion clears the hardware clear bit, notifies the stat framework, and signals histogram DMA completion to the ISP core.

## State And Persistence
State persists in `struct ispstat` and private `struct omap3isp_hist_config`, including current region/bin/CFA/gain settings, wait-accumulation count, active buffer, DMA channel, and update/config counters. Hardware histogram memory is explicitly cleared during setup and error handling to avoid stale accumulation.

## Dependencies And Integration Points
This file depends on Linux DMAEngine, ISP register helpers, histogram register definitions, `ispstat`, V4L2 subdev ioctls/events, and ISP helpers such as `omap3isp_flush()` and `omap3isp_hist_dma_done()`. It uses `isp->mmio_hist_base_phys` as the DMA source base.

## Risks And Edge Cases
- DMAEngine cannot report transfer errors in the callback, so failed hardware reads may only surface indirectly.
- `cfg.src_maxburst = hist->buf_size / 4` depends on valid, bounded buffer sizing.
- `hist_set_params()` copies `user_cfg` before normalizing `num_acc_frames == 0` on `user_cfg`, leaving a possible inconsistency where `cur_cfg->num_acc_frames` remains zero while later logic expects reset behavior.
- Histogram memory must be cleared after invalid buffers/errors to avoid stale stats.

## Test Signals
Test histogram bin limits by region count, invalid region coordinates, DMA request deferral versus fallback, PIO readout with valid/invalid buffers, accumulation count behavior, clear-bit handling, ioctl dispatch, and config-to-register values for CFA, gains, and regions.
