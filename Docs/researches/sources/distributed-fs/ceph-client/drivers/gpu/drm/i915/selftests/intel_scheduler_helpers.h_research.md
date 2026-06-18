# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_scheduler_helpers.h

Purpose: declares scheduler selftest helper APIs for temporarily changing `intel_engine_cs` scheduling policy and waiting for test requests. It is a small contract header shared by i915 scheduler selftests, with no implementation or persistent state.

Important APIs/types: `struct intel_selftest_saved_policy` captures `flags`, `reset`, `timeslice`, and `preempt_timeout` so a test can restore engine policy after mutation. `enum selftest_scheduler_modify` names supported mutations: disabling hangcheck and enabling a fast reset path. Exported prototypes are `intel_selftest_find_any_engine()`, `intel_selftest_modify_policy()`, `intel_selftest_restore_policy()`, and `intel_selftest_wait_for_rq()`.

Control flow and state: callers find a usable GT engine, save/modify policy through the modify API, run a scheduler scenario, then restore from the saved-policy snapshot. The header does not own memory; its state is caller-owned stack or local test data.

Dependencies and integration: depends only on `linux/types.h` plus forward declarations for i915 request, engine, and GT types. It integrates with scheduler selftests that need to alter engine policy without duplicating save/restore logic.

Risks: tests using this API must restore policy on all error paths or they can poison subsequent selftests. The enum is intentionally narrow; adding new policy modes requires matching implementation changes.

Test signals: success is indirect through scheduler selftests that compile against this header and verify request completion and policy restoration.
