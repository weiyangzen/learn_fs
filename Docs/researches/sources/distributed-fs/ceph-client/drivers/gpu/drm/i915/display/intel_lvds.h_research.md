# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds.h

Purpose: declares LVDS support APIs and provides non-i915 stubs.

Important APIs/types/functions: exposes `intel_lvds_port_enabled()`, `intel_lvds_init()`, `intel_get_lvds_encoder()`, and `intel_is_dual_link_lvds()` when `I915` is defined, with false/null/no-op stubs otherwise.

Control flow: display initialization calls LVDS init; hardware readout and platform code query LVDS encoder and dual-link state.

State and persistence behavior: implementation state lives in the LVDS encoder and hardware registers.

Dependencies and integration points: integrates LVDS code with display initialization, encoder queries, and register readout while allowing stubs in non-i915 build contexts.

Risks: callers must handle absent LVDS and stub return values.

Test signals: build coverage with and without `I915`, LVDS init on supported platforms, and dual-link query users.
