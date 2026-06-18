# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop2.c

## Purpose

`rockchip_drm_vop2.c` implements the newer Rockchip VOP2 display controller. VOP2 has multiple video ports, shared overlay/layer routing, cluster and smart windows, regmap-backed fields, SoC-specific mux ops, gamma/debugfs support, runtime PM, clocks, IRQs, and component lifecycle.

## Important APIs, Types, and Functions

- `vop2_bind`/`vop2_unbind` create and destroy the component and its DRM objects.
- `vop2_win_init` creates per-window regmap fields from cluster or smart descriptors.
- Plane helpers validate sizes, scaling, AFBC, YUV alignment, rotation, alpha/background constraints, and modifiers.
- `vop2_plane_atomic_update` programs linear or AFBC scanout, stride, format, swaps, rotation, scale, CSC, color key, dither, VP selection, and cluster enablement.
- CRTC helpers manage VP timings, interface muxing, dither, post-scaler/background, gamma, cfg-done, events, and standby.
- `vop2_isr` and `rk3576_vp_isr` handle global and per-VP interrupts.

## Control Flow

Bind reads SoC match data, initializes MMIO regmap and mode-config bounds, allocates window regmap fields, maps optional LUT memory, gets GRF/PMU syscons, clocks, IRQs, creates planes/CRTCs for connected ports, registers per-VP IRQs on RK3576-class hardware, optionally creates RGB output, initializes DMA mapping, and enables runtime PM. Atomic enable prepares VP dclk, globally enables VOP2 on the first active port, asks SoC ops to program output muxing, writes timings and output control from `rockchip_crtc_state`, optionally switches HDMI PHY PLL parents, updates gamma, and enables vblank. Flush commits cfg-done and events; disable waits for DSP hold and disables global hardware on the last VP.

## State and Persistence Behavior

`struct vop2` persists global resources, regmap, syscons, clocks, IRQ, enable count, old shared layer/port selections, overlay lock, RGB helper, and windows. `vop2_video_port` persists CRTC, dclk source, win mask, primary plane, event pointer, layer count, and completion. Regmap uses `REGCACHE_MAPLE` with non-volatile ranges for delayed cfg-done registers.

## Dependencies and Integration Points

The driver integrates with Rockchip GEM DMA addresses, `rockchip_crtc_state`, `rockchip_encoder->crtc_endpoint_id`, optional `rockchip_rgb`, SoC data from `rockchip_vop2_reg.c`, syscon GRFs, DRM atomic/vblank/debugfs helpers, media bus formats, V4L2 colorspaces, runtime PM, clocks, and IOMMU attach/detach.

## Risks and Edge Cases

`vop2_enable` has early returns after resource changes that deserve error-path review. Shared overlay registers require correct locking and SoC ops. Modifier restrictions differ by SoC and window type. Gamma LUT on RK356x is limited to one CRTC. Event delivery waits for cfg-done to clear in IRQ context. VOP2 assumes a primary-capable non-mirror window per active VP.

## Test Signals

Test multi-CRTC modesets, overlay routing, zpos/layer limits, AFBC/linear modifiers, 10bpc restrictions, YUV/RGB CSC, interlaced modes, HDMI PHY PLL switching, gamma on RK356x and newer SoCs, debugfs dumps, bus-error IRQs, per-VP IRQs, suspend/resume, and missing graph ports.
