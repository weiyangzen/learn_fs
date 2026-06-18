# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_accel.c

## Purpose

`nv_accel.c` implements 2D acceleration for `nvidiafb` by writing DMA command buffers in framebuffer memory and kicking the NVIDIA FIFO. It accelerates fbdev sync, copyarea, fillrect, and monochrome imageblit, with software fallbacks when the card locks up or an operation is unsupported. The source was read as a complete 418-line file.

## Important APIs, Types, and Functions

Exported entry points are `NVResetGraphics()`, `nvidiafb_sync()`, `nvidiafb_copyarea()`, `nvidiafb_fillrect()`, and `nvidiafb_imageblit()`. Internal helpers include `nvidiafb_safe_mode()` for lockup fallback, `NVFlush()` and `NVSync()` polling FIFO/PGRAPH idle state, `NVDmaKickoff()`, `NVDmaWait()`, `NVSetPattern()`, `NVSetRopSolid()`, `NVSetClippingRectangle()`, and `nvidiafb_mono_color_expand()`. It depends on DMA register tags from `nv_dma.h` and DMA macros from `nv_local.h`, especially `NVDmaStart`, `NVDmaNext`, `WRITE_PUT`, and `READ_GET`.

## Control Flow

`NVResetGraphics()` places the DMA command buffer after `FbUsableSize`, writes object/context setup entries with a `SKIPS` guard area, initializes FIFO pointers, chooses surface/pattern/rect/line formats from current bpp, sets pitch/offsets, installs default ROP and clipping, and kicks the FIFO. Runtime accelerated operations first ensure the fb is running and the driver is not in lockup mode. Copy writes source point, destination point, and size. Fill resolves the fbdev color to a packed color, optionally switches ROP, emits a solid rectangle command, and restores copy ROP. Mono imageblit emits color expansion setup and streams image data in chunks, reversing bit order on little-endian hosts. Sync waits for FIFO and PGRAPH idle.

## State and Persistence Behavior

The acceleration state is held in `struct nvidia_par`: DMA put/current/free/max counters, `dmaBase`, `currentRop`, `lockup`, and fbdev pixmap alignment. Hardware state persists in PRAMIN/PFIFO/PGRAPH objects initialized by `NVLoadStateExt()` and the command buffer region reserved at the end of framebuffer memory. If a timeout occurs, `lockup` is set, scan alignment is reduced, and later operations use `cfb_*` software paths.

## Dependencies and Integration Points

This file is called from `nvidiafb_set_par()` when acceleration is enabled and installed into `nvidia_fb_ops` for fbdev operations. It integrates with the NVIDIA register layout initialized by `nv_hw.c`, the framebuffer layout computed by `nvidia.c`, software fb helpers (`cfb_copyarea`, `cfb_fillrect`, `cfb_imageblit`), and the kernel softlockup watchdog.

## Risks and Edge Cases

The DMA wait/flush/sync loops use very large polling counts and only fall back after long busy waits. Correctness depends on reserving enough framebuffer tail memory for command buffers and cursor/scratch areas. DMA wraparound has a hardware race workaround using `SKIPS`; mistakes in put/get handling can wedge the engine. Mono imageblit assumes enough padded data and bit order conversion; non-1bpp imageblits fall back to software. Lockup fallback changes behavior dynamically and should be visible to tests.

## Test Signals

Useful tests compare accelerated and software output for copy, fill, invert ROP, and 1-bpp glyph/image paths at 8/16/24/32 bpp; force a simulated or hardware FIFO timeout and verify software fallback; run pan/mode-set followed by acceleration to validate pitch and clipping; and build with `CONFIG_FB_NVIDIA` across endian-sensitive architectures.
