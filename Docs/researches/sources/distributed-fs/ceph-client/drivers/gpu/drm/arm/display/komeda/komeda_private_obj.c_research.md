# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_private_obj.c

Purpose: registers DRM private objects for every Komeda pipeline component and implements create/duplicate/destroy functions for their atomic private states.

Important APIs/types/functions: exported `komeda_kms_add_private_objs()` and `komeda_kms_cleanup_private_objs()`. Private state funcs exist for layers, scalers, compiz, splitter, merger, improc, timing controller, and pipeline. `komeda_component_state_reset()` clears transient binding/input state during duplication.

Control flow: KMS attach adds a pipeline private object, then private objects for each component present in each pipeline. Atomic duplication copies old state but resets `binding_user`, active/changed inputs, and active component masks so each commit recomputes resource ownership. Cleanup walks DRM mode-config private object list and finalizes each object.

State and persistence: private object initial states persist in DRM mode config. Per-commit duplicates hold transient validation results that become current on atomic commit. Component state reset preserves affected inputs so disables/changed-input tracking can compare old and new state.

Dependencies/integration: DRM private object helpers, Komeda KMS/device/pipeline structures, and pipeline-state validation/update code.

Risks: repetitive state functions are easy to update inconsistently. Cleanup finalizes all private objects in mode config, so ordering with mode-config cleanup matters. Reset semantics are central to avoiding stale users and missed disables. Test signals: atomic state duplication/destruction under stress, commit rollback/failure paths, private object cleanup on attach failure, resource contention, and kmemleak checks.
