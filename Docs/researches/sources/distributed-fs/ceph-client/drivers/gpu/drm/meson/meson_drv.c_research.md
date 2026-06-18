# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_drv.c

## Purpose
Implements the top-level Amlogic Meson DRM platform driver. It allocates and registers the DRM device, maps VPU/HHI registers, initializes canvas, VPU/VENC/VPP/VIU/AFBCD blocks, binds component HDMI devices, creates encoders/planes/CRTC, handles vblank IRQ dispatch, and manages suspend/resume/shutdown.

## Important APIs, types, and functions
- `meson_drv_bind_master()` is the main device bring-up routine.
- `meson_drv_probe()` decides between direct bind and component-master binding based on OF graph endpoints.
- `meson_irq()` clears VENC interrupt flags and delegates to `meson_crtc_irq()`.
- `meson_dumb_create()` enforces 64-byte pitch alignment and page-aligned dumb buffer size.
- `meson_vpu_init()` programs VPU read/write arbitration.

## Control flow
Probe scans endpoint remote ports. If endpoints exist and some match DesignWare HDMI component nodes, it registers as component master; if endpoints exist without components, it binds directly; no endpoints means no-op. Master bind verifies at least one connector endpoint, gets SoC match data, allocates DRM and private state, maps VPU and HHI registers, initializes HHI regmap, obtains Meson canvas and four canvas IDs, initializes vblank, applies SoC-specific HDMI PHY limits, removes conflicting firmware framebuffers, initializes mode config, initializes hardware blocks, optional AFBCD, CVBS encoder, external components, HDMI encoder, optional G12A DSI encoder, primary/overlay planes, CRTC, IRQ, mode config reset, polling, DRM registration, and client setup.

Unbind unregisters DRM, stops polling, performs atomic shutdown, frees IRQ, drops DRM reference, removes encoders, unbinds components, exits AFBCD, and frees canvases. Suspend uses DRM mode-config helper suspend; resume reinitializes VPU/VENC/VPP/VIU/AFBCD before helper resume. Shutdown stops polling and performs atomic shutdown.

## State and persistence
Persistent state is `struct meson_drm` in `drm->dev_private`, containing MMIO/regmap resources, canvas IDs, planes, CRTC, encoders, SoC compatibility, limits, and cached VIU/VENC/RDMA/AFBCD state. Hardware state is reset and reinitialized on bind/resume and shut down through DRM atomic helpers.

## Dependencies and integration points
Depends on DRM core, GEM DMA/fbdev helpers, component framework, OF graph, aperture conflict removal, Meson canvas, sys_soc matching, Meson encoder/plane/overlay/CRTC/VIU/VPP/VENC/VCLK/RDMA/AFBCD modules, and DesignWare HDMI/DSI component nodes.

## Risks
Error unwinding is long and includes calls to encoder remove/component unbind after partial initialization; changes must preserve ordering. `meson_drv_unbind()` frees canvas IDs before unregistering DRM, so consumers must be inactive by then. Connector endpoint discovery controls whether the driver binds at all. SoC-specific limits are applied by `soc_device_match()` and may silently be absent on unknown package IDs.

## Test signals
Signals include probe logs for queued outputs, DRM device registration, fbdev/client setup, vblank IRQ operation, dumb buffer pitch alignment, CVBS/HDMI/DSI output creation, component bind failures, suspend/resume display recovery, shutdown blanking, and builds across GXBB/GXL/GXM/G12A match data.
