# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd.h

Purpose: Declares the GPU command based PXP session termination API.

Important APIs/types: `intel_pxp_terminate_session(struct intel_pxp *pxp, u32 idx)`.

Control flow: None in header.

State/persistence: None.

Dependencies/integration: Forward declares `struct intel_pxp` and includes Linux types. Called by session teardown code.

Risks: API only terminates one indexed session; future multiple-session support would need broader command emission.

Test signals: Build linkage and PXP teardown behavior.
