# sources/distributed-fs/ceph-client/include/drm/drm_encoder.h

Purpose: Defines DRM encoder objects and callbacks, representing the routing stage between CRTCs and connectors/bridges in a KMS display pipeline.

Important APIs, types, and functions: Defines `struct drm_encoder_funcs` and `struct drm_encoder`. Encoder state includes parent device, list node, mode object base, name, user-visible encoder type, stable index, `possible_crtcs`, `possible_clones`, legacy current CRTC pointer, bridge chain, function/helper tables, and debugfs entry. Exported helpers include `drm_encoder_init()`, `drmm_encoder_init()`, `drmm_encoder_alloc()`, `drmm_plain_encoder_alloc()`, `drm_encoder_index()`, `drm_encoder_mask()`, `drm_encoder_crtc_ok()`, `drm_encoder_find()`, `drm_encoder_cleanup()`, and encoder iteration macros.

Control flow: Drivers initialize encoders during mode-config setup, set possible CRTC and clone masks before registration, attach bridges/connectors, and optionally supply reset/destroy/late-register/early-unregister/debugfs callbacks. KMS routing checks masks to decide whether a CRTC can drive an encoder and whether clone configurations are legal. Managed allocation variants register cleanup with DRM managed resources.

State and persistence: Encoder objects are runtime KMS mode objects with stable indices and userspace IDs for the device lifetime. They are not hotplugged in DRM core assumptions, though connectors and bridges may be dynamic around them. No disk persistence exists.

Dependencies and integration points: Depends on CRTC masks, mode objects, connector routing, bridges, debugfs, and helper private callbacks. Integrates with atomic connector state, legacy encoder `crtc` state, bridge chains, and object lookup under lease checks.

Risks and test signals: Risks include incorrect `possible_crtcs` or `possible_clones` masks, forgetting self-clone bits where required, stale legacy `crtc` use in atomic drivers, cleanup lifetime mismatches with managed allocation, and debugfs hooks surviving unregister. Test encoder registration warnings, multi-CRTC routing, clone modes, leased-object lookup, bridge attach order, debugfs init/removal, and driver unload cleanup.
