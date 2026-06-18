# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_frontbuffer.c

Purpose: tracks which GEM frontbuffers are currently associated with scanout slots and dispatches invalidate/flush/flip notifications to display power-saving features such as PSR, FBC, DRRS, and TDF.

Important APIs/types/functions: implements `intel_frontbuffer_flip()`, `__intel_frontbuffer_invalidate()`, `__intel_frontbuffer_flush()`, `intel_frontbuffer_queue_flush()`, `intel_frontbuffer_init()`, `intel_frontbuffer_fini()`, and `intel_frontbuffer_track()`. Internal `frontbuffer_flush()` filters busy bits and calls subsystem flush hooks.

Control flow: rendering start invalidates frontbuffer bits, optionally marking them busy for command-stream origin. Rendering completion flushes only bits still busy for that render and clears them. Dirtyfb-origin flush also calls the parent display flush hook. Flip removes stale busy bits for the old buffer and immediately flushes with `ORIGIN_FLIP`. Queued flush takes a frontbuffer reference, schedules work, flushes dirtyfb, then drops the reference.

State and persistence: each `intel_frontbuffer` stores `display`, atomic `bits`, and a `flush_work`. Global `display->fb_tracking.busy_bits` tracks outstanding CS rendering under a spinlock. Bit ownership is guarded by plane mutexes but updated atomically for whole-object RMW.

Dependencies and integration: integrates with DRM GEM objects, i915 parent frontbuffer references, PSR, FBC, DRRS, TDF, tracepoints, and display tracking locks.

Risks: incorrect bit tracking can restart FBC/PSR while rendering is still in flight or fail to restart power-saving after rendering. Queued work must hold a reference. The bit layout assumes all pipe/plane bits fit in `atomic_t` and 32 bits.

Test signals: exercise CPU writes, GPU rendering, dirtyfb, cursor updates, flips, queued flush after fences, multi-plane/pipe tracking, frontbuffer finalization warnings, and PSR/FBC/DRRS reactions.
