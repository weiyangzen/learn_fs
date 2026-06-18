# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_uncore.c

Purpose: initializes an i915 uncore instance for mock devices with no-op MMIO read/write functions.

Important APIs/functions: macro-generated `nop_write8/16/32()` and `nop_read8/16/32/64()` implement raw MMIO accessors that ignore writes and return zero for reads. `mock_uncore_init()` calls `intel_uncore_init_early()` and assigns all raw read/write MMIO vfuncs to the no-op family.

Control flow and state: the uncore is initialized against `to_gt(i915)`, then its function pointers are replaced. No MMIO backing store is maintained, so register writes are not persistent.

Dependencies and integration: depends on `mock_uncore.h`, i915 uncore initialization, and `ASSIGN_RAW_*_MMIO_VFUNCS` macros. Used during mock GEM device creation before GT tests run.

Risks: tests that require register value persistence cannot use this uncore directly. Returning zero can hide missing setup unless tests explicitly assert behavior.

Test signals: mock-device tests should avoid real MMIO faults and should see deterministic zero reads from raw uncore access.
