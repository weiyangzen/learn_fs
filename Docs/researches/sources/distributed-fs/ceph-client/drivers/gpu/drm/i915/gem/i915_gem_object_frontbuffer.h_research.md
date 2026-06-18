# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_frontbuffer.h

## Purpose
Defines the GEM-side frontbuffer wrapper and inline helpers for fast frontbuffer flush/invalidate and safe RCU lookup.

## Important APIs and Types
`struct i915_frontbuffer` embeds `intel_frontbuffer`, points to the GEM object, tracks writes with `i915_active`, and uses RCU plus kref. Inline `i915_gem_object_frontbuffer_flush()` and `_invalidate()` call out-of-line helpers only when an object frontbuffer exists. `i915_gem_object_frontbuffer_lookup()` performs RCU-safe lookup with `kref_get_unless_zero()`. The header also declares get/ref/put, tracking adapter, and `i915_display_frontbuffer_interface`.

## Control Flow
Lookup exits quickly when no pointer is present; otherwise it enters RCU, dereferences, tries to take a kref, verifies the pointer still matches, and retries on races. Inline flush/invalidate avoid full lookup on the common non-framebuffer path.

## State and Persistence Behavior
Defines the RCU-protected relation between `drm_i915_gem_object` and `i915_frontbuffer`; no global state is stored.

## Dependencies and Integration Points
Includes display frontbuffer definitions and GEM object types. It bridges GEM domain/object code and display frontbuffer code.

## Risks and Test Signals
Main risks are RCU misuse and kref imbalance. Rapid framebuffer create/destroy with CPU/GPU writes should expose race bugs. Build coverage catches interface drift.
