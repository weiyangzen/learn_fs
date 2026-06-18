# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_lock.c

Purpose: implements a compact retry helper around DRM modeset acquire contexts and `-EDEADLK` backoff for i915 modeset locking blocks.

Important APIs/types/functions: `_intel_modeset_lock_begin()` initializes a `drm_modeset_acquire_ctx`, optionally attaches it to an Intel atomic state, and seeds the loop return value with `-EDEADLK`. `_intel_modeset_lock_loop()` turns an `-EDEADLK` marker into another loop iteration. `_intel_modeset_lock_end()` handles real `-EDEADLK` backoff, clears atomic state when needed, drops locks, and finalizes the acquire context.

Control flow: the macro in the header creates a `for` loop. Begin initializes context and sets the first iteration. User code attempts lock-taking work inside the loop and must use `continue` on error. End either backs off and repeats on deadlock or drops/finalizes locks when complete.

State and persistence behavior: state is transient in `drm_modeset_acquire_ctx`, the optional atomic state's acquire context pointer, and the caller's return code. No persistent storage exists.

Dependencies and integration points: wraps DRM modeset locking and optional DRM atomic state clearing for i915 call sites that need deadlock-retry loops.

Risks: the header warning is important: `break` or `return` inside the loop can bypass `_intel_modeset_lock_end()` and leak locks/context. Clearing atomic state on deadlock is required to retry with a clean state. Mismanaging `ret` can suppress needed backoff.

Test signals: lockdep and deadlock-injection tests, atomic paths using retry loops, early error handling using `continue`, and absence of leaked acquire contexts.
