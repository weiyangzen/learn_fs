# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_pm.c

Purpose: Provides PXP hooks for system suspend/resume and runtime suspend/resume.

Important APIs/functions: `intel_pxp_suspend_prepare()`, `intel_pxp_suspend()`, `intel_pxp_resume_complete()`, `intel_pxp_runtime_suspend()`, and `intel_pxp_runtime_resume()`.

Control flow: Suspend prepare ends active PXP synchronously and invalidates protected contexts. Suspend disables PXP hardware under RPM and clears invalidated flag. Resume initializes hardware either with an explicit wakeref after system resume or without one in runtime-resume context. TEE backend resume defers hardware init until component bind if the MEI component is not bound; GSC-CS backend can initialize directly.

State/persistence: Mutates `arb_is_valid` and `hw_state_invalidated`, and toggles hardware/IRQ state via init/fini. Protected contexts are invalidated during suspend prepare.

Dependencies/integration: Runtime PM, top-level PXP end/invalidate/init_hw/fini_hw, IRQ hooks, and backend component availability.

Risks: Runtime suspend declares the arb session invalid without full context invalidation here; correctness depends on higher-level sequencing. Resume must not initialize TEE-backed hardware before component rebind. Missing wakeref on system resume would risk MMIO while suspended, so `_pxp_resume()` optionally takes one.

Test signals: Suspend/hibernate tests and protected-content behavior after resume; logs for PXP end timeout or reinit failures.
