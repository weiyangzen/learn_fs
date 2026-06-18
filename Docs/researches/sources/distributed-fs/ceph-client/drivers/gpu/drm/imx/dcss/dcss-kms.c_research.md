# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-kms.c

## Purpose
Creates and tears down the DRM/KMS device for the i.MX8MQ DCSS display subsystem. It wires the DCSS CRTC, encoder, bridge connector, vblank support, GEM DMA framebuffer support, fbdev/client setup, and atomic mode configuration into a single DRM device.

## Important APIs, types, and functions
- `dcss_kms_attach()` is the main attach path, using `devm_drm_dev_alloc()` with `struct dcss_kms_dev`.
- `dcss_kms_detach()` unregisters the DRM device, shuts down atomic state, disables CRTC vblank, cleans mode config, and deinitializes the CRTC.
- `dcss_kms_shutdown()` performs atomic shutdown for platform shutdown.
- Static objects include `dcss_kms_driver`, `dcss_drm_mode_config_funcs`, `dcss_mode_config_helpers`, and the simple encoder funcs.
- `dcss_kms_bridge_connector_init()` discovers the downstream panel/bridge from device tree, initializes the encoder, attaches the bridge without a connector, then creates a bridge connector.

## Control flow
Attach allocates a DRM device embedded in `dcss_kms_dev`, stores the DCSS hardware pointer in `drm->dev_private`, initializes mode limits and atomic helpers, initializes one vblank source, finds and attaches the downstream bridge, initializes the DCSS CRTC and its planes, resets mode objects, starts helper polling, registers the DRM device, and finally starts generic DRM client setup.

Error paths unwind in reverse: CRTC cleanup when registration fails and mode-config cleanup for earlier failures. Detach follows the runtime teardown path: unregister first to stop userspace entry, stop polling, run atomic shutdown, force vblank off, clean the mode config, deinitialize CRTC resources, and clear `dev_private`.

## State and persistence
The file owns the `struct drm_device` embedded in `struct dcss_kms_dev`, the associated encoder and connector pointer, and the link from DRM back to `struct dcss_dev` through `dev_private`. No persistent hardware state is stored here; it orchestrates lifecycle state in DRM core objects.

## Dependencies and integration points
Depends on DRM GEM DMA helpers, fbdev DMA helpers, atomic helpers, bridge connector helpers, vblank initialization, and device-tree bridge discovery. It integrates with the DCSS CRTC and plane code through `dcss_crtc_init()`/`dcss_crtc_deinit()` and is called by the broader DCSS platform driver after the hardware blocks have been initialized.

## Risks
Bridge discovery requires a valid downstream bridge; a panel returned without a bridge is treated as `-ENODEV`. The encoder is initialized before `dcss_crtc_init()`, so parse/attach failures must not leak encoder state. `drm->dev_private` is critical for plane and CRTC callbacks and must be cleared on failed attach/detach. Atomic shutdown is used in both detach and shutdown, so duplicate calls must remain harmless.

## Test signals
Build and probe should show one registered `imx-dcss` DRM device, one CRTC, one encoder, and one bridge connector. Runtime validation should cover bridge probe deferral, registration failure unwind, vblank initialization, fbdev/client setup, shutdown with an active mode, and hot-unplug or module removal without dangling polling or mode objects.
