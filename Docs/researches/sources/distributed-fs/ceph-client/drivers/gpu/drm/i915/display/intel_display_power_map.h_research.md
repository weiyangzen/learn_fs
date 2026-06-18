# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_map.h

Purpose: exposes the minimal interface for building and destroying the platform-specific power-domain to power-well mapping.

Important APIs, types, and functions: forward-declares `struct i915_power_domains` and declares `intel_display_power_map_init()` plus `intel_display_power_map_cleanup()`.

Control flow: callers initialize `struct i915_power_domains` enough to identify the containing display, then call `intel_display_power_map_init()` during power-domain setup and `intel_display_power_map_cleanup()` during teardown.

State and persistence: no state is stored in the header. The implementation allocates and later frees the dynamic power-well array inside `struct i915_power_domains`.

Dependencies and integration points: included by `intel_display_power.c`, with implementation dependencies hidden in `intel_display_power_map.c`. It keeps the topology table private while letting the power-domain core request a ready-to-use mapping.

Risks: failing init must abort display power-domain setup because no safe logical-domain mapping exists. Cleanup must match successful init to avoid leaking the power-well array.

Test signals: build linkage catches signature drift. Runtime init failures, missing power wells, or empty debug output on display-capable platforms indicate map init problems.
