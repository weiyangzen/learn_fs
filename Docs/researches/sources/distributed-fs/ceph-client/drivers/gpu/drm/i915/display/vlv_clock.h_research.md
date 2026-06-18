# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_clock.h

Purpose: declares VLV clock read helpers when building the i915 driver and provides zero-returning inline stubs when the header is included outside `I915` builds.

Important APIs/types/functions: the public functions are `vlv_clock_get_hpll_vco()`, `vlv_clock_get_hrawclk()`, `vlv_clock_get_czclk()`, `vlv_clock_get_cdclk()`, and `vlv_clock_get_gpll()`, all taking `struct drm_device *` and returning integer kHz values in the real implementation. The non-`I915` stubs return `0`.

Control flow: build-time `#ifdef I915` selects between external declarations and static inline fallback implementations. This lets shared code include the header without pulling in VLV sideband implementation dependencies when i915 is not present.

State and persistence behavior: the header owns no state. In i915 builds, the implementation caches selected values in `intel_display`; in stub builds, calls have no side effects.

Dependencies and integration points: forward-declares `struct drm_device` and is included by VLV/CHV display clock code or shared display code that needs clock helpers conditionally.

Risks: the zero stubs are safe for compilation but not meaningful clock values; callers must not treat stub builds as real hardware readout. The API does not encode units in the type, so callers must preserve the kHz convention from the implementation.

Test signals: compile coverage with and without `I915`, VLV/CHV runtime clock readout, and call sites verifying that zero-return stubs are only used in non-hardware or unsupported configurations.
