# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_session.h

Purpose: Declares optional PXP session-management functions.

Important APIs/types: `intel_pxp_session_management_init()` and `intel_pxp_terminate()`, with stubs when PXP is disabled.

Control flow: Header-only conditional compilation.

State/persistence: None directly; implementation operates on `struct intel_pxp`.

Dependencies/integration: Used by PXP init, IRQ worker, PM/end paths, and command backends.

Risks: Disabled-config stubs remove all session behavior, so callers must only expect real behavior when PXP is configured and enabled.

Test signals: Build in both configs and session recovery behavior.
