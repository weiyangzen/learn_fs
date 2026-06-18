# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_huc.h

Purpose: Declares the PXP-assisted HuC load/authentication helper.

Important APIs/types: `intel_pxp_huc_load_and_auth(struct intel_pxp *pxp)`.

Control flow: None.

State/persistence: None.

Dependencies/integration: Used by HuC/GSC loading paths through the TEE backend bind flow.

Risks: Header has no config stub, so callers must be in appropriate PXP-enabled build context.

Test signals: Build linkage and HuC authentication path results.
