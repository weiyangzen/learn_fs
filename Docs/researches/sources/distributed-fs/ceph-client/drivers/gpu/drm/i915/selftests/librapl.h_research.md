# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/librapl.h

Purpose: declares the RAPL selftest helper API.

Important APIs/types: forward declares `struct drm_i915_private` and exposes `librapl_supported(const struct drm_i915_private *i915)` plus `librapl_energy_uJ(void)`.

Control flow and state: no state is held by the header. Callers first check support, then sample energy values around a test workload.

Dependencies and integration: depends only on `linux/types.h`. The implementation integrates with MSR access and i915 platform detection.

Risks: header users must treat a zero energy value as unsupported or unavailable rather than as a precise power result.

Test signals: compile coverage and downstream energy-aware selftests that skip cleanly on unsupported platforms.
