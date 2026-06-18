# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/librapl.c

Purpose: supplies RAPL energy helpers for i915 selftests that want approximate package/graphics energy readings on integrated GPUs.

Important APIs/functions: `librapl_supported()` rejects discrete GPUs and returns true only when `librapl_energy_uJ()` can read nonzero energy. `librapl_energy_uJ()` reads `MSR_RAPL_POWER_UNIT` to get the energy unit exponent, then reads `MSR_PP1_ENERGY_STATUS` and converts the raw value to microjoules.

Control flow and state: both functions are stateless. MSR reads use `rdmsrq_safe()` and return `0` on read failure, making unsupported hardware a soft no-op rather than a crash.

Dependencies and integration: depends on x86 MSR access and i915 platform predicates. It is used by performance/energy selftests that should skip where RAPL PP1 is unavailable or where discrete GPUs require hwmon integration instead.

Risks: RAPL counters can wrap and are platform-specific. Returning zero conflates unsupported hardware, read failure, and a true zero reading, which is acceptable for skip detection but not detailed diagnostics.

Test signals: selftests can call `librapl_supported()` before measuring and should observe increasing `librapl_energy_uJ()` values during workloads on supported integrated platforms.
