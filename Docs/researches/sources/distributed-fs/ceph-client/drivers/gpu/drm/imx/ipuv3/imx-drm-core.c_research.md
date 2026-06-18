# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-drm-core.c

## Purpose
Implements the component-master DRM device for legacy i.MX IPUv3 display systems. It creates the DRM device, binds IPU CRTCs and output components, owns atomic commit policy, GEM DMA/fbdev support, dumb-buffer pitch alignment, suspend/resume, and platform-driver registration.

## Important APIs, types, and functions
- `imx_drm_atomic_check()` wraps `drm_atomic_helper_check()`, rechecks modesets after plane checks, and calls `ipu_planes_assign_pre()`.
- `imx_drm_atomic_commit_tail()` sequences modeset disables, active plane commits without disable-after-modeset, modeset enables, flip-done waits, deferred plane disables, and hardware-done notification.
- `imx_drm_encoder_parse_of()` sets encoder possible CRTCs from device tree and returns `-EPROBE_DEFER` when no CRTC is registered yet.
- `imx_drm_dumb_create()` aligns dumb-buffer pitch to hardware's 8-pixel scanout requirement.
- `imx_drm_bind()`/`imx_drm_unbind()` are component master callbacks.
- `imx_drm_platform_probe()` uses `drm_of_component_probe()` with `compare_of()` to collect subcomponents.

## Control flow
Probe creates the component master for `fsl,imx-display-subsystem`, then sets a 32-bit coherent DMA mask. Bind allocates a DRM device, sets mode limits/helpers, initializes managed mode config and vblank for up to four CRTCs, stores the DRM pointer on the device, binds all CRTC/output components, resets modes, validates `legacyfb_depth`, starts polling, registers the DRM device, and starts a color-mode client setup. Unbind unregisters, stops polling, runs atomic shutdown, unbinds components, drops the DRM device, and clears drvdata.

Atomic commit deliberately waits for flip completion before executing deferred plane disables because IPUv3 plane disable ordering can interact with IDMAC/DC clock state. The component match helper special-cases IPU DI platform devices whose OF node lives in platform data and LDB channel nodes whose component device is the parent LDB.

## State and persistence
The module parameter `legacyfb_depth` persists as the preferred fbdev color depth, constrained to 16 or 32. The DRM device stores mode-config state, vblank state, bound components, and plane/CRTC atomic state. No hardware registers are written directly here; those are delegated to CRTC, plane, and encoder components.

## Dependencies and integration points
Depends on Linux component framework, DRM GEM DMA/fbdev/atomic helpers, OF graph component probing, IPUv3 core support, and `ipu_planes_assign_pre()` from the plane code. It exports `imx_drm_encoder_parse_of()` to output drivers and registers both the master driver and `ipu_drm_driver`.

## Risks
The second modeset check is required because plane checks may set `crtc_state->mode_changed`; removing it can accept invalid commits. Deferred disable handling is sensitive to flip-done waits and plane `disabling` flags. Component matching for LDB and IPU DI is device-tree-shape-specific. Dumb pitch alignment must match the CRTC's hactive alignment behavior.

## Test signals
Test signals include successful component binding with IPU DI plus HDMI/LVDS/TVE/parallel components, probe deferral until CRTCs exist, atomic commits that resize or reformat planes, deferred plane disable completion, fbdev depth parameter handling, dumb-buffer pitch alignment, and suspend/resume via `drm_mode_config_helper_suspend/resume()`.
