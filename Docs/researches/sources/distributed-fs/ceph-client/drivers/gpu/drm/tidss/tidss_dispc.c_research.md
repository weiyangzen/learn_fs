# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc.c

## Purpose

`tidss_dispc.c` is the hardware abstraction for the TI DSS display controller used by the `tidss` DRM driver. It describes SoC-specific DISPC feature tables, maps named platform resources, programs video ports, overlays, planes, scaling filters, color conversion, gamma/CTM state, interrupt masks, OLDI control bits, and runtime power transitions.

## Important APIs, Types, and Functions

- SoC feature descriptors: `dispc_k2g_feats`, `dispc_am625_feats`, `dispc_am62a7_feats`, `dispc_am62l_feats`, `dispc_am65x_feats`, and `dispc_j721e_feats` define register maps, VP/OVR/resource names, bus types, plane order, scaling limits, gamma support, and hardware plane IDs.
- `struct dispc_device`: private runtime state for mapped common/VID/OVR/VP register bases, VP clocks, OLDI syscon, feature pointer, format list, bandwidth limit, and errata flags.
- IRQ API: `dispc_read_and_clear_irqstatus()` and `dispc_set_irqenable()` dispatch to K2G or K3 register layouts and translate raw VP/VID bits into the packed `dispc_irq_t` layout from `tidss_irq.h`.
- VP API: `dispc_vp_prepare()`, `dispc_vp_enable()`, `dispc_vp_disable()`, `dispc_vp_unprepare()`, `dispc_vp_go()`, `dispc_vp_mode_valid()`, and clock helpers program timing, polarity, bus width, clock rate, and GO/enable bits.
- Plane API: `dispc_plane_check()`, `dispc_plane_setup()`, `dispc_plane_enable()`, and `dispc_plane_formats()` validate scaling/CSC support and program DMA base addresses, increments, picture/output sizes, FIR coefficients, CSC, alpha, and premultiplied-alpha state.
- Color/scaler helpers: `dispc_vid_calc_scaling()`, `tidss_get_scale_coefs()` integration, `dispc_find_csc()`, gamma table writers, and CTM-to-CSC conversion routines implement the display processing math.
- Lifecycle API: `dispc_init()`, `dispc_remove()`, `dispc_runtime_suspend()`, and `dispc_runtime_resume()` allocate resources, initialize hardware, and restore register state after PM.

## Control Flow

Probe enters through `dispc_init()`. It selects the already matched feature table, configures DMA masks, allocates `struct dispc_device`, applies errata filtering to the FourCC list, installs the feature-specific common register map, ioremaps common/VID/OVR/VP resources by the names in the feature table, acquires VP and functional clocks, optionally finds AM65x OLDI syscon control, reads `max-memory-bandwidth`, soft-resets the controller, and finally stores `tidss->dispc`.

Atomic modeset code calls into the VP and plane APIs. A CRTC new modeset programs the VP with bus format, OLDI data width if needed, horizontal/vertical timing, polarity, screen size, default color, gamma table, and CTM. Plane update code calls `dispc_plane_setup()`, which recalculates scaling, maps DRM FourCCs to DISPC format codes, writes DMA addresses for one- or two-plane buffers, computes row/pixel increments with decimation, sets scaler registers and coefficients, configures YUV-to-RGB CSC where required, and updates alpha/blending fields.

Interrupt handling is split by hardware generation. K2G has per-VP/per-VID IRQ registers under VP/VID bases plus a top-level status; K3-style devices use common-space per-VP/per-VID status and enable registers. Both paths clear statuses around enable-mask transitions to avoid stale IRQ delivery.

## State and Persistence Behavior

The feature table is immutable per device and controls all register layout decisions. `struct dispc_device` persists for the platform device lifetime and owns devm-managed mappings, clocks, gamma tables, and the generated FourCC list. Hardware state is volatile across runtime suspend; `dispc_runtime_resume()` re-enables `fclk`, logs reset/idle status, calls `dispc_initial_config()`, marks `is_enabled`, and restores IRQ enables through `tidss_irq_resume()`. Gamma tables are kept in memory per VP and rewritten when color management changes or after resume setup paths.

## Dependencies and Integration Points

The file depends on Linux clock, DMA, regmap/syscon, runtime PM, OF, SoC matching, and MMIO helpers. It integrates upward with `tidss_crtc.c`, `tidss_plane.c`, `tidss_irq.c`, `tidss_oldi.c`, and `tidss_kms.c`; downward it consumes `tidss_dispc_regs.h`, `tidss_irq.h`, and scale coefficients. DRM integration uses format metadata, DMA framebuffer helpers, color encoding/range/CTM/gamma objects, and mode validation enums.

## Risks and Edge Cases

- `dispc_common_regmap` is file-global, so it assumes one active register map at a time. Multiple TIDSS devices with different subrevisions would share this pointer.
- Several hardware waits use tight count loops for OLDI reset without `cpu_relax()` or timeout based on time; behavior depends on CPU speed.
- `dispc_plane_setup()` calls `dispc_vid_calc_scaling()` but does not check its return, relying on atomic check to have rejected invalid states.
- CTM conversion clamps coefficient formats differently for K2G and K3; color changes need hardware comparison on each SoC family.
- The bandwidth check assumes 4 bytes per pixel and may be conservative or inaccurate for 16/24-bit and YUV formats.
- OLDI support is split between legacy AM65x handling in this file and the newer `tidss_oldi.c` bridge; bus-type and external-clock flags must remain consistent.
- Erratum i2000 disables all YUV formats for matched AM65x SR1.0 devices; tests need coverage that filtered formats reach plane creation.

## Test Signals

Useful signals include probe success on each compatible string, ioremap/clock/syscon failure handling, mode validation for porch/clock/bandwidth limits, plane validation for scaling and YUV CSC combinations, gamma/CTM programming with both 8-bit and 10-bit LUT hardware, IRQ enable/clear behavior under lock, runtime suspend/resume preserving display state, and real scanout tests for RGB, YUYV/UYVY/NV12, overlay z-order, alpha, and scaler ratios near hardware limits.
