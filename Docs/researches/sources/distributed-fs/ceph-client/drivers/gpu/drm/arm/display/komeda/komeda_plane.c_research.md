# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_plane.c

Purpose: creates DRM planes for Komeda layers and implements plane atomic validation/state lifecycle.

Important APIs/types/functions: `komeda_kms_add_planes()` is exported. Internal `komeda_plane_atomic_check()` builds layer data flow, `komeda_plane_init_data_flow()` maps DRM plane state to Komeda flow, and helpers create/destroy/reset/duplicate plane states. Plane funcs expose format-modifier checks and DRM atomic plane operations.

Control flow: KMS setup iterates each pipeline layer, creates a `komeda_plane`, builds a layer-specific format list, initializes a universal plane, attaches helper funcs, and creates rotation, alpha, blend, color, and zpos properties. Atomic check skips disabled/inactive cases, gets the target CRTC state, initializes data flow, and calls normal or split layer builder. Actual hardware updates are deferred to CRTC flush.

State and persistence: each `komeda_plane` points to a hardware layer. `komeda_plane_state` extends DRM plane state with z-order list linkage and `layer_split` flag. CRTC slave plane masks are updated at plane creation.

Dependencies/integration: DRM atomic/blend/color property APIs, Komeda framebuffer, format caps, KMS CRTC state, and pipeline-state builders.

Risks: zpos range is hard-coded 0..8 and duplicate zpos is rejected by KMS check. `layer_split` consumes two z-order slots. Format-modifier support checks rotation as 0 at plane level, with full rotation later in atomic check. Test signals: plane property enumeration, all layer formats/modifiers, rotation/reflection, alpha/blending, zpos conflicts, disabled CRTC updates, and split-layer cases.
