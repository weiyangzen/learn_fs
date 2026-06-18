# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_wait_util.h

Purpose: provides i915-specific polling macros for sleepable and atomic wait loops with timeout handling.

Important APIs/macros: `__wait_for`, `_wait_for`, `wait_for`, `_wait_for_atomic`, `wait_for_us`, `wait_for_atomic_us`, and `wait_for_atomic`. Debug builds define `_WAIT_FOR_ATOMIC_CHECK` to catch atomic-context misuse when preempt count is meaningful.

Control flow: sleepable waits calculate a raw-ktime deadline, repeatedly execute optional operation code, evaluate the condition before declaring timeout, sleep with bounded exponential backoff, and return `0` or `-ETIMEDOUT`. Atomic waits use `local_clock()`, optional preempt disable/enable to keep CPU-local time coherent, `cpu_relax()`, and timeout accounting across CPU migration.

State and persistence: stateless macros; all variables are block-local temporaries. The only side effects come from the caller-supplied condition and optional operation.

Dependencies and integration: used by pcode and register-poll paths. Depends on kernel delay, ktime, scheduler clock, SMP, preemption, and compiler barrier APIs.

Risks: conditions may be evaluated many times and must be side-effect safe. `wait_for_us` and atomic waits require compile-time constant timeouts, and `wait_for_atomic_us` rejects waits above 50 ms. Atomic mode can burn CPU and should be reserved for contexts that cannot sleep.

Test signals: compile-time `BUILD_BUG_ON` checks, debug atomic-context warnings, and runtime users such as `skl_pcode_request()` timeout/retry paths.
