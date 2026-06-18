# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_tee.h

Purpose: Declares the MEI TEE backend API for PXP.

Important APIs/types: Component init/fini, arb-session create, and streaming message send helper.

Control flow: Header only.

State/persistence: None; implementation operates on `pxp->pxp_component` and `pxp->stream_cmd`.

Dependencies/integration: Includes top-level PXP header and is used by PXP init/session/HuC paths.

Risks: No disabled-config stubs here, so inclusion assumes PXP build context. Streaming message API exposes raw lengths and caller-owned buffers; size validation occurs in implementation.

Test signals: Build linkage and firmware-command behavior through TEE backend.
