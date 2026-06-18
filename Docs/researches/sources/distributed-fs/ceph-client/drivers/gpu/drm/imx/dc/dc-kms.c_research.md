<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-kms.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-kms.c

Purpose: Initializes the i.MX8 DC DRM KMS mode configuration, CRTCs, bridge-backed encoders/connectors, vblank support, and polling.

Important APIs/types/functions: Public functions are `dc_kms_init()` and `dc_kms_uninit()`. Internal helper `dc_kms_init_encoder_per_crtc()` creates a simple encoder, attaches the output bridge, creates a bridge connector, and attaches it.

Control flow: KMS init initializes mode config, sets size limits and mode config callbacks, configures vblank limits, initializes each CRTC and optional bridge/encoder/connector pair, completes CRTC post-init IRQ setup, initializes vblank support, resets mode config, and starts KMS polling. Uninit stops polling.

State and persistence behavior: Populates `drm->mode_config`, `dc_drm->encoder[]`, CRTC/plane objects, connectors, and vblank state.

Dependencies: DRM atomic helpers, bridge and bridge-connector helpers, OF graph bridge lookup, CRTC/plane init APIs, and display-engine tcon device-tree nodes.

Integration points: Called by top-level DC bind after component bind/post-bind and before DRM device registration.

Risks: Bridge lookup returns `-ENODEV` as a valid no-output case but other errors abort KMS init. Connector/encoder setup is per CRTC and depends on tcon OF nodes. CRTC post-init occurs after all CRTCs are created to request IRQs.

Test signals: DRM device registration with two CRTCs, bridge connector creation, hotplug/polling behavior, vblank init, and modeset through attached bridge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-kms.c -->
