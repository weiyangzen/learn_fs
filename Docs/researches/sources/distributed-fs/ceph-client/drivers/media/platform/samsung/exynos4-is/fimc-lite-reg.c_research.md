# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite-reg.c

## Purpose
Provides the low-level MMIO programming helpers for the Exynos FIMC-LITE camera host interface.

## Important APIs, Types, and Functions
Exports reset, IRQ, capture, test-pattern, input format, crop/window, camera bus, DMA output, DMA buffer, buffer mask, and register-dump helpers such as `flite_hw_reset()`, `flite_hw_set_source_format()`, `flite_hw_set_camera_bus()`, `flite_hw_set_output_dma()`, and `flite_hw_set_dma_buffer()`.

## Control Flow
The main driver calls these helpers while holding `fimc_lite::slock` for register programming. Hardware init sets camera bus/mux, source format, crop offset, DMA mask, DMA output mode, interrupt masks, and optional test pattern. IRQ paths read and clear status, while queue paths program or mask DMA start-address slots.

## State and Persistence
All state is hardware-register state under `dev->regs`; the file keeps only static media-bus-to-register mapping tables. No save/restore cache exists, so callers must reprogram after reset or power transitions.

## Dependencies and Integration Points
Depends on `fimc-lite.h`, `fimc-lite-reg.h`, common Exynos FIMC format descriptors, media-bus codes, and MMIO accessors. It is tightly integrated with `fimc-lite.c` queue, stream, suspend, and register-dump paths.

## Risks and Edge Cases
The format-map lookup falls back to table entry zero on unsupported input codes, which can silently program YUYV ordering after logging. `flite_hw_set_out_order()` assumes a matching YUV code and can fall through to index zero for non-YUV formats. Reset waits for ready but proceeds even if timeout expires.

## Test Signals
Validate each supported YUV/raw/JPEG media-bus code, parallel versus MIPI bus polarity, one-buffer and 32-buffer variants, crop/compose offset programming, reset timeout behavior, and register dumps before/after stream start.
