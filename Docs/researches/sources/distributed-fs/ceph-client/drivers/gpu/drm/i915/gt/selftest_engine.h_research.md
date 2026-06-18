# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine.h

Purpose: declares the GT-scoped engine PM selftest entry point used by the engine selftest dispatcher.

Important APIs/types: forward-declares `struct intel_gt` and declares `int live_engine_pm_selftests(struct intel_gt *gt)`.

Control flow: none in the header.

State and persistence behavior: none directly; the declared function runs tests that manipulate engine PM state.

Dependencies and integration points: included by `selftest_engine.c` and `selftest_engine_pm.c` to keep the selftest interface small.

Risks: prototype mismatch would break compilation. The header deliberately avoids pulling heavy GT internals into the dispatcher.

Test signals: compile coverage only; runtime signals come from `selftest_engine_pm.c`.
