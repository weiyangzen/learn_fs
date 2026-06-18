<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.c

## Purpose
Implements Keem Bay DRM plane support for LCD video layers. It validates framebuffer formats and sizes, programs DMA addresses and layer format registers, configures alpha/blending and CSC, defers disables to EOF, and creates the primary and overlay planes.

## Important APIs, types, and functions
Plane callbacks are `kmb_plane_atomic_check()`, `kmb_plane_atomic_update()`, `kmb_plane_atomic_disable()`, and `kmb_plane_destroy()`. Helpers include `check_pixel_format()`, `get_pixel_format()`, `get_bits_per_pixel()`, `config_csc()`, and `kmb_plane_set_alpha()`. `kmb_plane_init()` creates up to `KMB_MAX_PLANES` planes and records the primary.

## Control flow
Atomic check rejects unsupported formats, changes in format after first use, changes in framebuffer width/height after first configuration, out-of-range plane dimensions, and scaling. Atomic update exits during underflow recovery, then programs DMA length, stride, line width, Y/Cb/Cr addresses, source rectangle, destination position, pixel format, planar CSC, alpha register and flags, LCD control layer enable/blend bits, pipeline DMA, output RGB888/MIPI mode, DMA configuration, initial display config cache, and EOF/DMA-error interrupts. Atomic disable records a per-plane disable flag and control bit; the IRQ EOF path performs the actual hardware disable.

## State and persistence
Persistent software state is held in `kmb->init_disp_cfg[plane_id]` and `kmb->plane_status[plane_id]`. Hardware state includes layer DMA addresses, widths, strides, format config, CSC coefficients, alpha, LCD control enables, output format, and interrupt enables.

## Dependencies and integration points
Depends on DRM atomic plane helpers, GEM DMA framebuffer address helpers, blend properties, `kmb_drv.h` MMIO helpers, and `kmb_regs.h` register constants. The IRQ logic in `kmb_drv.c` consumes plane disable and underflow state.

## Risks
`KMB_MAX_PLANES` is defined as 2 even though enum and register constants describe four layers, so only two video layers are created. Static DMA address storage is shared across updates. Format and size immutability after first configuration is a hardware limitation that userspace must handle. Underflow recovery can cause updates to be skipped. Planar stride calculations use width and `cpp[0]`, which needs careful validation for subsampled formats.

## Test signals
Test primary and overlay updates, all advertised packed and planar formats, alpha blend modes, immutable format/size rejection, no-scaling enforcement, EOF-delayed disable, DMA underflow recovery, and vblank/page-flip behavior. LCD layer register dumps and underflow logs are useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.c -->
