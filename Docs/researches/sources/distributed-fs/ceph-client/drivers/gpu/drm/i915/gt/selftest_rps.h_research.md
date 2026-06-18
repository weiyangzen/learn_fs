# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rps.h Research

Purpose: this header exposes the RPS live selftest functions to the i915 selftest registration code.

Important APIs/types/functions: it declares `live_rps_control()`, `live_rps_clock_interval()`, `live_rps_frequency_cs()`, `live_rps_frequency_srm()`, `live_rps_power()`, `live_rps_interrupt()`, and `live_rps_dynamic()`. All take the selftest runner's `void *arg` convention, implemented as an `intel_gt *`.

Control flow: no executable logic is present; it is a declaration boundary.

State and persistence: the header owns no state. The implementations mutate live RPS/PM state and restore it internally.

Dependencies/integration: this header lets other GT selftest modules include RPS subtests without pulling in implementation internals. It has a single include guard, `SELFTEST_RPS_H`.

Risks and test signals: interface drift is caught by build errors. Because the declarations are direct and narrow, accidental dependency expansion is low.
