# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_frontbuffer.c

## Purpose
Bridges GEM objects to display frontbuffer tracking. It creates/refcounts `i915_frontbuffer` wrappers, attaches them to objects with RCU, tracks GPU writes with `i915_active`, forwards display invalidate/flush operations, and exports the display frontbuffer interface.

## Important APIs and Functions
`i915_gem_object_frontbuffer_get()`, `_ref()`, `_put()`, `__i915_gem_object_frontbuffer_flush()`, `__i915_gem_object_frontbuffer_invalidate()`, `frontbuffer_active()`, `frontbuffer_retire()`, `frontbuffer_release()`, and `i915_display_frontbuffer_interface` are the core pieces.

## Control Flow
Get first performs an RCU/kref lookup. If no frontbuffer exists, it allocates and initializes one, takes an object reference, initializes active tracking, and installs it under `i915->frontbuffer_lock`; racing allocations are discarded in favor of the installed object. Put uses `kref_put_lock()` so final release clears scanout and the RCU pointer under lock, then finalizes active/display state, drops the object ref, and frees via RCU. Flush/invalidate look up a temporary ref and forward to display code.

## State and Persistence Behavior
Persistent state is the RCU `obj->frontbuffer` pointer, frontbuffer kref, `i915_active write` tracker, and display frontbuffer base state. Creation pins the GEM object by reference until final release. Release clears scanout via `i915_ggtt_clear_scanout()`.

## Dependencies and Integration Points
Depends on display frontbuffer APIs, `i915_active`, object refs, RCU, kref, global `frontbuffer_lock`, and display/domain flush helpers. Domain transitions and display code call into this bridge.

## Risks
RCU/kref lookup must not return a dying object. Release ordering must clear the object pointer before RCU free. Missing invalidate/flush on writes can break scanout, FBC, or PSR coherency. Active-ref imbalance leaks or prematurely frees frontbuffers.

## Test Signals
Display frontbuffer, PSR/FBC, pageflip, and scanout coherency tests exercise behavior. Concurrency stress can expose RCU/refcount bugs.
