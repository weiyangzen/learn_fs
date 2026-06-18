# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_psp.c

Purpose: implements the HDCP and DTM PSP firmware boundary. It adds/removes displays from secure topology, creates/destroys HDCP sessions, asks firmware to generate transmitter messages, validates receiver messages, and enables link or stream encryption.

Important APIs: topology functions are `mod_hdcp_add_display_to_topology()` and `mod_hdcp_remove_display_from_topology()` with v2/v3 fallback. HDCP1 functions cover create/destroy session, validate receiver, enable encryption, validate KSV list/V', enable DP stream encryption, and link maintenance. HDCP2 functions cover create/destroy session, prepare AKE Init, validate AKE cert/H'/L'/receiver-id-list/stream-ready, prepare LC Init/EKS/stream management, enable encryption, and DP stream encryption.

Control flow: each PSP operation obtains `psp->dtm_context.mutex` or `psp->hdcp_context.mutex`, zeros the shared memory command, fills command-specific input, invokes `psp_dtm_invoke()` or `psp_hdcp_invoke()`, then translates firmware status and output fields into `enum mod_hdcp_status` and module state. DTM v3 falls back to v2 if unsupported at runtime.

State and persistence: persists `hdcp->auth.id`, generated HDCP1/2 messages under `hdcp->auth.msg`, connection flags (`is_repeater`, `is_km_stored`, revocation flags), trace events, and per-display state transitions between active and encryption-enabled.

Dependencies and integration: depends on AMDGPU PSP context, trusted-application command structures in `hdcp_psp.h`, display helper accessors, and DDC/execution layers that send or receive the prepared messages.

Risks: shared-memory layout must exactly match firmware ABI. Mutex coverage is mandatory because one shared buffer is reused. Some remove-display success paths set display state to `ACTIVE` rather than inactive, so callers must understand topology versus display lifecycle. Stream-encryption loops partially update display state if later displays fail.

Test signals: PSP mock tests for every command status, DTM v3 fallback, uninitialized TA contexts, no active display, revocation handling, forced content type negotiation, MST stream encryption with disabled displays, and state rollback after failed topology updates.
