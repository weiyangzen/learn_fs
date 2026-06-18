# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_huc.c

Purpose: Sends HuC load/authentication requests through the PXP TEE streaming path for platforms where HuC is loaded by GSC via PXP.

Important APIs/functions: `intel_pxp_huc_load_and_auth()`.

Control flow: Verifies PXP and component availability, obtains HuC firmware object DMA address, builds a PXP 4.3 `START_HUC_AUTH` message, sends it through `intel_pxp_tee_stream_message()`, and accepts success or `PXP_STATUS_OP_NOT_PERMITTED` as benign when HuC may already survive resume.

State/persistence: Does not own state. Reads HuC firmware object and PXP component; firmware authentication state is updated externally by GSC/HuC logic.

Dependencies/integration: Depends on GEM DMA address helper, GT/HuC state, PXP TEE streaming, and PXP 4.3 command ABI.

Risks: Requires `pxp->pxp_component`, so it is tied to the MEI component backend. Incorrect DMA address or component absence fails HuC auth. Accepting OP_NOT_PERMITTED relies on later authentication-bit checks to catch real failures.

Test signals: HuC load/auth logs, GSC error status, and subsequent HuC authenticated state.
