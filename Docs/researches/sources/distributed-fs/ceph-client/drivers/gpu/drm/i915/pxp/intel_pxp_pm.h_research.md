# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_pm.h

Purpose: Declares optional PM hook entry points for PXP.

Important APIs/types: Suspend prepare, suspend, resume complete, runtime suspend, and runtime resume declarations with disabled-config stubs.

Control flow: Header-only conditional compilation.

State/persistence: None.

Dependencies/integration: Called from i915 PM flows.

Risks: Stubbed no-op behavior means callers rely on config gating for protected-content support.

Test signals: Build coverage and system/runtime PM tests.
