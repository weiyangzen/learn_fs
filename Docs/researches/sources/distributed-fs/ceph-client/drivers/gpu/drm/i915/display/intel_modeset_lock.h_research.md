# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_lock.h

Purpose: declares the modeset lock retry helpers and defines the `intel_modeset_lock_ctx_retry()` loop macro.

Important APIs/types/functions: prototypes for `_intel_modeset_lock_begin()`, `_intel_modeset_lock_loop()`, `_intel_modeset_lock_end()`, and the macro that wraps them into a structured retry block.

Control flow: callers write a retry loop that initializes an acquire context, runs lock-taking work, and lets the end helper perform DRM backoff on `-EDEADLK`.

State and persistence behavior: no header state; implementation operates on acquire contexts, optional Intel atomic state, and caller `ret`.

Dependencies and integration points: used by modeset and atomic code needing DRM deadlock avoidance.

Risks: the macro contract requires `continue` for errors inside the block. Returning or breaking can skip cleanup.

Test signals: compile coverage and deadlock retry behavior under DRM modeset lock contention.
