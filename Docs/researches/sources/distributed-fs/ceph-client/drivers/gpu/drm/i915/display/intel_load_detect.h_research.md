# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_load_detect.h

Purpose: declares the load-detect temporary pipe API.

Important APIs/types/functions: `intel_load_detect_get_pipe()` returns restore state or an error/null result, and `intel_load_detect_release_pipe()` restores and releases that state.

Control flow: probe code gets a temporary pipe, performs load detection, then releases the pipe with the same acquire context.

State and persistence behavior: implementation temporarily changes atomic display state and restores it through the returned duplicated state.

Dependencies and integration points: used by connector detect code that needs a lit pipe, with DRM atomic state and modeset locking.

Risks: callers must always release a non-null/non-error state and must handle `-EDEADLK` retries.

Test signals: compile coverage and connector probe paths using load detection.
