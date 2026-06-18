# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power.h

Purpose: declares the logical display power-domain model and public power-management API for i915 display code. It is the contract clients use to keep pipes, transcoders, ports, AUX channels, audio, VGA, GT IRQ, DC-off, TC-cold, and initialization resources powered while accessing hardware.

Important APIs, types, and functions: `enum intel_display_power_domain` lists all logical domains and relies on consecutive pipe/transcoder/port ranges for helper macros. `struct intel_power_domain_mask` wraps a bitmap. `struct i915_power_domains` stores global power-domain state, per-domain use counts, async put state, and the power-well array. `struct intel_display_power_domain_set` groups acquired refs for batch release. Public APIs cover init/cleanup, HW init/remove, enable/disable, suspend/resume, domain get/put, async put, set-based acquisition/release, debug output, DDI/AUX domain translation, and DBUF slice updates. RAII-style macros `with_intel_display_power()` and `with_intel_display_power_if_enabled()` acquire a domain for a loop scope and release asynchronously.

Control flow: display clients include this header, choose the innermost logical domain needed, call `intel_display_power_get()` or conditional/set variants before MMIO access, and release with `intel_display_power_put()` or async helpers. Debug runtime PM builds preserve and verify `struct ref_tracker *` wakerefs; non-debug builds collapse wakeref tracking to unchecked put paths.

State and persistence: the header defines in-memory refcount and async-work state but does not implement persistence. Domain use counts are per display instance. The masks and wakeref arrays track acquired domains until explicit release. `INTEL_WAKEREF_DEF` marks non-debug or untracked wakeref slots.

Dependencies and integration points: depends on Linux mutex/workqueue and i915 display type forward declarations. It is consumed across modeset, connector, AUX, audio, VGA, watermarks, and suspend/resume paths. The domain enum must remain synchronized with mapping tables in `intel_display_power_map.c` and platform operation implementations in `intel_display_power_well.c`.

Risks: enum reordering breaks arithmetic macros such as `POWER_DOMAIN_PIPE()` and port/transcoder domain derivation. Missing get/put symmetry leaks power wells or causes MMIO while unpowered. Conditional compilation changes wakeref checking behavior, so bugs may only become visible with `CONFIG_DRM_I915_DEBUG_RUNTIME_PM`.

Test signals: compile coverage catches enum/API drift, while debug runtime PM warns on refcount mismatch. Runtime inspection through debugfs/power debug output, power-domain set release paths, and scoped macro use around MMIO accesses are key validation signals.
