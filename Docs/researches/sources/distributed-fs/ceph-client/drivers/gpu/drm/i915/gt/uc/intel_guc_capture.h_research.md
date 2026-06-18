## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_capture.h

Purpose: declares the public GuC capture interface used by ADS setup, GuC notification handling, and i915 GPU coredump code.

Important APIs, types, and functions:
- Forward declares `intel_guc`, `intel_gt`, `intel_context`, `intel_engine_cs`, and `intel_engine_coredump` to avoid pulling heavy headers into users.
- Declares lifecycle APIs `intel_guc_capture_init()` and `intel_guc_capture_destroy()`.
- Declares ADS-facing list APIs `intel_guc_capture_getlistsize()`, `intel_guc_capture_getlist()`, and `intel_guc_capture_getnullheader()`.
- Declares runtime/coredump APIs `intel_guc_capture_process()`, `intel_guc_capture_is_matching_engine()`, `intel_guc_capture_get_matching_node()`, `intel_guc_capture_print_engine_node()`, and `intel_guc_capture_free_node()`.

Control flow:
- Callers initialize capture state during GuC setup, request input register-list blobs during ADS construction, invoke processing when firmware reports capture data, attach matching nodes during error-state construction, and free attached nodes when the coredump is released.

State and persistence:
- The header owns no storage; all persistent state is embedded in `struct intel_guc` and the implementation-private capture structures allocated by `intel_guc_capture_init()`.

Dependencies and integration points:
- Bridges `intel_guc_capture.c` to ADS, CT/G2H error handling, and i915 GPU error reporting without exposing private parsed-node internals.

Risks:
- API users must respect ownership: `intel_guc_capture_getlist()` returns cached memory owned by capture state, while `intel_guc_capture_free_node()` returns an attached parsed node to the reuse cache.
- The print API depends on `CONFIG_DRM_I915_CAPTURE_ERROR`; callers must handle disabled or missing capture state.

Test signals:
- Compile coverage for all users of this header.
- Runtime capture tests should verify init/destroy pairing, ADS list retrieval, matching, print, and free paths.
