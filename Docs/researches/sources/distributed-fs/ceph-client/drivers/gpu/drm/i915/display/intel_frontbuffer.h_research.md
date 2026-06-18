# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_frontbuffer.h

Purpose: defines frontbuffer tracking types, operation origins, bit layout, inline invalidate/flush wrappers, and public tracking lifecycle functions.

Important APIs/types/functions: `enum fb_op_origin` identifies CPU, command streamer, flip, dirtyfb, and cursor update origins. `struct intel_frontbuffer` stores display, atomic bitmask, and flush work. Macros define per-pipe frontbuffer slots: `INTEL_FRONTBUFFER_BITS_PER_PIPE`, `INTEL_FRONTBUFFER()`, `INTEL_FRONTBUFFER_OVERLAY()`, and `INTEL_FRONTBUFFER_ALL_MASK()`. Public functions include flip, invalidate/flush internals and wrappers, queue_flush, track, init, and fini.

Control flow: inline wrappers read the atomic bitmask, skip work when no slots are tracked, and dispatch to the non-inline implementations.

State and persistence: bitmask state persists while a GEM object is considered a frontbuffer. Work item state persists until queued flush completes.

Dependencies and integration: depends on Linux atomics/workqueue and is used by GEM/framebuffer/plane code and display power-saving subsystems.

Risks: macro bit allocation must remain large enough for all i915 planes/pipes. Callers must pass correct origin so CS busy filtering and flip/cursor exceptions work as intended.

Test signals: compile-time build bugs for bit capacity, runtime warnings on mismatched track/untrack, and rendering/flip tests that validate power-saving invalidation behavior.
