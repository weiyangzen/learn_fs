# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutlib.c


Purpose: Implements helper routines for OMAP V4L2 output crop/window negotiation, default format-dependent layout, contiguous buffer allocation, and DSS generation detection.

Important APIs/functions: `omap_vout_default_crop()` centers the largest even crop that fits both source image and framebuffer. `omap_vout_try_window()` clips a requested overlay window to display bounds, enforces even dimensions, clears clips/bitmap, and rejects empty rectangles. `omap_vout_new_window()` applies a validated window and adjusts crop size for OMAP24xx/34xx scaling limits. `omap_vout_new_crop()` clips crop to source bounds, preserves resize ratios by adjusting `win`, enforces OMAP24xx 768-pixel vertical-resize line-buffer constraints and 2x/4x scaling limits, then updates crop. `omap_vout_new_format()` resets crop/window defaults after a format change. `omap_vout_alloc_buffer()` and `omap_vout_free_buffer()` allocate/free physically contiguous pages while marking pages reserved. `omap_vout_dss_omap24xx()` and `omap_vout_dss_omap34xx()` classify DSS versions.

Control flow: The main driver calls these helpers from format, overlay-window, and crop ioctls and from VRFB allocation paths. They are exported with `EXPORT_SYMBOL_GPL` for the geometric helpers, indicating reuse outside this source file.

State and persistence: Functions mutate caller-provided V4L2 rectangles, windows, pix formats, and framebuffer structs. Buffer allocation returns virtual and physical addresses to the caller; no module-global state is persisted.

Dependencies/integration: Depends on V4L2 structs, Linux page allocation and DMA mapping headers, and `omapdss_get_version()` from OMAP DSS. It encodes DSS-generation hardware limits used by `omap_vout.c`.

Risks and test signals: Integer division in scaling checks can hide near-threshold resize ratios, and crop/window clamping must avoid zero dimensions. Reserved-page allocation is legacy and should be stress-tested for allocation failure and cleanup. Test crop/window ioctls across negative origins, overlarge rectangles, OMAP24xx/34xx limits, RGB/YUV formats, and repeated VRFB static allocation/free.
