# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp.h

Purpose: Public PXP subsystem interface for i915 callers.

Important APIs/types: Declares capability predicates, init/fini, hardware init/fini, termination marking, readiness/status helpers, start/end, backend timeout, protected-object `intel_pxp_key_check()`, and `intel_pxp_invalidate()`.

Control flow: Header only declares calls; consumers use predicates to guard optional PXP behavior before protected-content operations.

State/persistence: No state, but functions operate on `struct intel_pxp` allocated in `i915->pxp`.

Dependencies/integration: Forward declares DRM GEM object, i915 private, and PXP types. Used by GEM object/context paths, PM paths, IRQ handling, debugfs, session code, and backends.

Risks: `intel_pxp_tee_end_arb_fw_session()` is declared here but implemented by the TEE backend, exposing a backend-specific finalization call at the top-level interface. Callers must distinguish supported, enabled, and active.

Test signals: Build coverage across PXP-enabled and disabled configurations, plus runtime protected-content tests.
