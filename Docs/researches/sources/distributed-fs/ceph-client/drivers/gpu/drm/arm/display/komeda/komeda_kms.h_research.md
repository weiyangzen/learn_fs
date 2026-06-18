# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_kms.h

Purpose: defines Komeda DRM/KMS wrapper objects and declares KMS-facing helper APIs.

Important APIs/types/functions: structs `komeda_plane`, `komeda_plane_state`, `komeda_wb_connector`, `komeda_crtc`, `komeda_crtc_state`, and `komeda_kms_dev`; conversion macros; inline helpers `is_writeback_only()`, `is_only_changed_connector()`, and `has_flip_h()`. Declares CRTC/plane/private/writeback/KMS lifecycle and event functions.

Control flow: object wrappers are used by DRM init and atomic state hooks. Inline helpers support writeback-only commits, connector-change detection, and split-flow orientation under rotation/reflection.

State and persistence: KMS objects persist for DRM device lifetime; plane/CRTC private states persist per atomic state. `komeda_crtc` records master/slave pipelines, slave plane mask, writeback connector, pending disable completion, and encoder.

Dependencies/integration: DRM atomic, blend, device, writeback, print APIs and Komeda pipeline types.

Risks: wrappers assume specific embedding layout for `container_of`. `has_flip_h()` depends on DRM rotation simplification and affects split crop direction. Test signals: CRTC/plane state duplication/destruction, writeback connector paths, split with rotations/reflections, and multi-pipeline CRTC masks.
