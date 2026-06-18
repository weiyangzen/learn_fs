# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lpe_audio.h

Purpose: declares or stubs the LPE audio bridge API depending on the i915 build context.

Important APIs/types/functions: when `I915` is defined, exposes init, teardown, IRQ forwarding, and ELD notification. Otherwise inline stubs return `-ENODEV` or no-op.

Control flow: display audio code can call these APIs without conditional compilation at each callsite.

State and persistence behavior: no header state; implementation stores platform device and IRQ state in `struct intel_display`.

Dependencies and integration points: bridges display audio logic, interrupt dispatch, and the standalone LPE audio platform driver.

Risks: stub behavior must match non-i915 build expectations; callers should tolerate `-ENODEV` from init.

Test signals: build coverage with and without `I915`, audio init skip behavior, and no-op stubs in non-i915 contexts.
