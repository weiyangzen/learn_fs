# sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-ti-mcbsp.h

Purpose: defines platform configuration for TI OMAP McBSP audio serial ports.

Important APIs and types: `struct omap_mcbsp_ops` provides optional `request()` and `free()` hooks per McBSP instance. `struct omap_mcbsp_platform_data` carries ops, buffer size, register size/step, wakeup capability, CCR support, and `force_ick_on()` clock callback. `omap3_mcbsp_init_pdata_callback()` initializes callback fields for OMAP3 platform data.

Control flow: platform code populates McBSP pdata; the driver calls request/free hooks for ownership, uses register sizing/stepping for IO access, configures wakeup/CCR features, and may force the interface clock through the callback.

State and persistence: platform data describes static controller capabilities. Runtime port ownership, clocks, buffers, DMA, and audio stream state live in the McBSP driver.

Dependencies and integration points: depends on spinlocks and clock framework declarations. Integrates OMAP platform setup, ASoC McBSP drivers, clock management, wakeup handling, and DMA/buffer sizing.

Risks and test signals: risks include wrong register stride/width, unbalanced request/free hooks, clock force leaks, and wakeup capability mismatch. Test probe on OMAP variants, playback/capture, suspend wakeup, force-clock paths, and request/free error handling.
