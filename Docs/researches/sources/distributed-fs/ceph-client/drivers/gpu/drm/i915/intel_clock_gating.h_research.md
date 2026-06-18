# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_clock_gating.h

Purpose: declares the clock-gating setup entry points used by i915 device initialization.

Important APIs/functions: `intel_clock_gating_hooks_init(struct drm_device *drm)` selects the platform hook table; `intel_clock_gating_init(struct drm_device *drm)` applies the selected clock-gating/workaround programming.

Control flow: this header is included by initialization code and by the implementation. It keeps the concrete platform dispatch private to `intel_clock_gating.c`.

State and persistence: no state in the header; state lives in `drm_i915_private->clock_gating_funcs` and hardware registers.

Dependencies and integration: only forward-declares `struct drm_device`, minimizing include coupling.

Risks: callers must run hook selection before applying clock gating. Missing this ordering would dereference an uninitialized function table.

Test signals: compile/link coverage from driver init, plus boot-time hardware init paths.
