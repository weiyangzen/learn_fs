# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_drv.c

## Purpose
`vc4_drv.c` is the top-level Broadcom VC4/VC5/VC6 DRM platform driver. It defines DRM driver objects and ioctls, handles component master binding, configures DMA masks and firmware handoff, initializes GEM for GEN_4, binds display/GPU subcomponents, loads KMS, registers the DRM device, and registers/unregisters all VC4 component platform drivers at module load/unload.

## Important APIs, Types, And Functions
- `vc4_ioremap_regs()` is a shared helper around `devm_platform_ioremap_resource()`.
- `vc4_dumb_fixup_args()` enforces minimum pitch and size for dumb buffers; `vc5_dumb_create()` applies it before DMA dumb allocation.
- `vc4_get_param_ioctl()` exposes V3D hardware IDs and feature booleans for GEN_4 userspace.
- `vc4_open()` and `vc4_close()` allocate/free `struct vc4_file`, initialize/close perfmon state, and release any per-file binner BO use.
- `vc4_drm_ioctls[]` maps VC4 render ioctls including submit, waits, BO creation/mapping/tiling/labels, hang state, madvise, and perfmon APIs.
- `vc4_drm_driver` includes modeset, atomic, GEM, render, and syncobj features with VC4 ioctl support. `vc5_drm_driver` is display/GEM-only and omits render ioctls.
- `vc4_match_add_drivers()` builds a component match list by discovering devices bound to each VC4 component platform driver.
- `vc4_drm_bind()` performs the primary bind sequence for the DRM device.
- `vc4_drm_unbind()` unplug/shutdowns the DRM device on component unbind.
- `vc4_drm_register()` and `vc4_drm_unregister()` register the subcomponent drivers and platform master driver.

## Control Flow
At module init, `vc4_drm_register()` refuses to load when firmware-only DRM drivers are requested, registers all component drivers, then registers the `vc4-drm` platform driver. Its probe builds a component match over HVS, HDMI, VEC, DPI, DSI, TXP, CRTC, and V3D devices and adds a component master.

When the component master binds, `vc4_drm_bind()` selects `vc4_drm_driver` for GEN_4 and `vc5_drm_driver` for newer generations. It sets a 32-bit or 36-bit coherent DMA mask, applies DMA-range configuration from matching HVS/V3D nodes, allocates `struct vc4_dev`, initializes BO cache and GEM only for GEN_4, initializes DRM mode config, obtains Raspberry Pi firmware if present, removes conflicting framebuffer devices, asks firmware to stop its display driver, binds all components, registers automatic unbind cleanup, creates additional planes, loads KMS, disables firmware-left PixelValves, registers the DRM device, and sets up the fbdev/client output with RGB565.

Unbind calls `drm_dev_unplug()`, `drm_atomic_helper_shutdown()`, and clears driver data. Platform shutdown also calls atomic shutdown to quiesce scanout.

## State And Persistence Behavior
The master allocates `struct vc4_dev` as the DRM device private object and sets `vc4->gen` and `vc4->dev`. For GEN_4 it initializes BO cache, GEM job state, purgeable BO state, power locks, and per-file perfmon context via open/close. Component binding populates shared pointers such as `vc4->hvs` and `vc4->v3d` in other files. Driver registration persists until module unload; DRM device registration persists until unbind/remove.

Firmware handoff is one-shot per bind: conflicting aperture devices are removed and `RPI_FIRMWARE_NOTIFY_DISPLAY_DONE` is sent when firmware support is available. DMA mask and DMA-range configuration are process-wide device settings.

## Dependencies And Integration Points
This file depends on Linux platform/component frameworks, OF matching, DMA configuration, aperture conflict removal, runtime PM, Raspberry Pi firmware API, DRM core/atomic/fbdev/GEM helpers, and all VC4 subdrivers. It is the central integration point for `vc4_hvs_driver`, `vc4_hdmi_driver`, `vc4_vec_driver`, `vc4_dpi_driver`, `vc4_dsi_driver`, `vc4_txp_driver`, `vc4_crtc_driver`, and `vc4_v3d_driver`.

The component driver order is intentional: HVS before HDMI and TXP/CRTC so HDMI can inspect HVS limits and TXP possible-CRTC masks are correct. GEN_4 userspace ABI is exposed through `uapi/drm/vc4_drm.h`; newer generations share display infrastructure but not VC4 render ioctl support.

## Risks And Edge Cases
- Component discovery depends on platform devices already associated with the registered component drivers; missing OF nodes or deferred probes can delay master bind.
- GEN gating is critical: invoking GEN_4 render ioctls or GEM scheduler on VC5/VC6 returns `-ENODEV`.
- Firmware handoff failures are only warnings for display-done notification, but aperture removal failure aborts bind.
- DMA mask differences matter for BCM2712/GEN_6_C 36-bit addressing.
- Open/close paths assume `struct vc4_file` only for GEN_4 render-capable devices.
- Driver unregister order unregisters component drivers before the platform master driver in `vc4_drm_unregister()`, matching current code but worth watching for teardown ordering interactions.

## Test Signals
- Probe tests should cover GEN_4, GEN_5, and GEN_6_C compatible strings, with and without firmware node, and with absent V3D.
- Userspace ABI tests should verify `GET_PARAM`, `SUBMIT_CL`, wait, BO, madvise, and perfmon ioctls on GEN_4, and absence/failure on VC5/VC6.
- KMS boot tests should confirm firmware framebuffer removal, firmware display handoff, CRTC boot disable, plane creation, and client setup.
- Component-order regressions show up as missing encoders/CRTC masks, HDMI mode-limit misdetection, or failed component bind.
