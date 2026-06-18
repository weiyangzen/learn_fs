# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_framebuffer.h

Purpose: declares the Komeda framebuffer extension and framebuffer helper APIs.

Important APIs/types/functions: `struct komeda_fb` embeds `drm_framebuffer` and stores `format_caps`, `is_va`, AFBC aligned width/height, `afbc_size`, and `offset_payload`. `to_kfb()` converts from DRM framebuffer. Functions cover creation, source-coordinate checking, pixel-address lookup, and layer support.

Control flow: header connects DRM mode-config `fb_create`, atomic validation, and D71 hardware update paths.

State and persistence: `komeda_fb` persists as long as the DRM framebuffer object exists. Its AFBC metadata is computed once at creation and reused by atomic state and register programming.

Dependencies/integration: includes DRM framebuffer and Komeda format caps headers. Used by KMS, plane, pipeline-state, and D71 component code.

Risks: callers assume every framebuffer passed to Komeda is a `komeda_fb`; mixing generic DRM framebuffers would break `to_kfb()`. Test signals: framebuffer lifecycle, writeback framebuffer handling, source crop validation, and AFBC metadata consistency.
