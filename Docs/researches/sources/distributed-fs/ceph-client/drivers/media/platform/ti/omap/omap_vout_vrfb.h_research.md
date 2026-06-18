# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_vout_vrfb.h


Purpose: Declares the VRFB support interface consumed by `omap_vout.c` and supplies no-op stubs when VRFB support is not built. This keeps the main video-output driver source mostly independent of the optional rotation backend.

Important APIs/types: With `CONFIG_VIDEO_OMAP2_VOUT_VRFB`, the header declares `omap_vout_free_vrfb_buffers()`, `omap_vout_setup_vrfb_bufs()`, `omap_vout_release_vrfb()`, `omap_vout_vrfb_buffer_setup()`, `omap_vout_prepare_vrfb()`, and `omap_vout_calculate_vrfb_offset()`. Without the option, static inline stubs return success or do nothing.

Control flow: The main driver calls these hooks during device setup, vb2 queue setup, buffer prepare, crop-offset calculation, and cleanup. The stub path makes those call sites compile and execute as simple non-rotation behavior.

State and persistence: The header owns no state. It operates on `struct omap_vout_device` fields defined in `omap_voutdef.h` and only controls whether external functions or stubs are linked.

Dependencies/integration: Depends on prior visibility of `struct omap_vout_device`, `struct platform_device`, and `struct vb2_buffer`. It is tightly paired with `omap_vout_vrfb.c` and the Kconfig symbol used by the OMAP2/OMAP3 video-output build.

Risks and test signals: Stub success means call sites must independently gate rotation support via `rotation_type`; otherwise unsupported rotation paths can appear to succeed. Build-test both `CONFIG_VIDEO_OMAP2_VOUT_VRFB=y/m` and disabled configurations, including compilation units that include this header before full type definitions.
