# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_ww.h

## Purpose
This header defines the i915 GEM wound/wait context structure and retry-loop helper used for deadlock-safe multi-object reservation locking.

## Important APIs, Types, and Functions
`struct i915_gem_ww_ctx` contains `ww_acquire_ctx ctx`, `obj_list`, `contended`, and `intr`. It declares init/fini/backoff/unlock-single functions and defines inline `__i915_gem_ww_fini()` plus the `for_i915_gem_ww()` retry macro.

## Control Flow
`for_i915_gem_ww()` initializes a ww context, runs the loop while the caller returns `-EDEADLK`, and lets `__i915_gem_ww_fini()` perform backoff or final cleanup. If backoff succeeds it deliberately returns `-EDEADLK` to rerun the caller's locking body with the contended object held.

## State and Persistence Behavior
The context is stack/local operation state. It stores locked object refs until final cleanup and a contended object between trylock failure and slow-lock backoff.

## Dependencies and Integration Points
It includes DRM driver types for the ww class and forward references GEM objects. It is used throughout i915 GEM/VMA code for multi-object lock ordering.

## Risks
The macro expects callers to assign `_err` correctly inside the loop. Returning success too early without cleanup would leak locks, while mishandling `-EDEADLK` can spin or deadlock.

## Test Signals
Compiler coverage of macro users, lockdep ww tests, and runtime paths that force contended object backoff.
